---
type: concept
scope: deep-gemm
name: FP8/FP4 GEMM 精度方案
version: "2.6.1"
source: csrc/apis/gemm.hpp, deep_gemm/utils/math.py, csrc/utils/layout.hpp, csrc/apis/layout.hpp
description: DeepGEMM 的 FP8/FP4 低精度 GEMM 方案，包括 per-block 缩放因子、UE8M0 编码、缩放因子布局转换
---

# FP8/FP4 GEMM 精度方案

DeepGEMM 的核心优势在于对 FP8（8-bit 浮点）和 FP4（4-bit 浮点）低精度矩阵乘法的深度优化。通过 per-block 缩放因子（Scaling Factor, SF）方案，在显著减少内存带宽和计算量的同时保持训练/推理精度。

---

## 一、数据类型

### 1.1 FP8（Float8 E4M3）

- **编码**：1 位符号 + 4 位指数 + 3 位尾数，偏置 7
- **表示范围**：约 ±240，精度约 3 位有效十进制数
- **PyTorch dtype**：`torch.float8_e4m3fn`
- **元素大小**：1 byte
- **适用场景**：前向/反向传播中的激活和权重，SM90/SM100 均支持

### 1.2 FP4（Float4 E2M1）

- **编码**：1 位符号 + 2 位指数 + 1 位尾数，偏置 1
- **码点**：`{0, ±0.5, ±1, ±1.5, ±2, ±3, ±4, ±6}`，无 NaN/Inf
- **存储方式**：每 2 个 E2M1 码打包为 1 byte（nibble packing），即 `kPackedFP4 = torch::kInt8`
- **逻辑维度**：物理 Int8 张量的最后一维 ×2
- **元素大小**：0.5 byte（打包后 1 byte 存 2 个元素）
- **适用场景**：MegaMoE 路由专家权重（极致压缩），仅 SM100 支持

### 1.3 BF16 输出

- FP8/FP4 GEMM 的输出 D 张量支持 `torch.bfloat16` 或 `torch.float32`
- BF16 为默认输出精度
- FP32 输出用于需要更高精度的累加场景

---

## 二、缩放因子（Scaling Factor）方案

### 2.1 Per-block 量化

FP8/FP4 精度有限，直接使用全局 scale 会导致精度损失。DeepGEMM 采用 per-block 缩放因子方案：将矩阵划分为固定大小的 block，每个 block 使用独立的 scale 进行量化和反量化。

量化公式：
```
X_fp8[i,j] = quantize(X_fp32[i,j] / sf[block_i, block_j])
```

反量化公式：
```
Y_fp32[i,j] = Y_fp8[i,j] * sf_a[block_i, block_k] * sf_b[block_k, block_j]
```

### 2.2 Recipe（粒度配置）

Recipe 是三元组 `(gran_m, gran_n, gran_k)`，定义 M、N、K 三个维度上每个 scale 覆盖的元素数。

| 架构 | Kernel 类型 | A 的 Recipe | B 的 Recipe | SF dtype | 说明 |
|---|---|---|---|---|---|
| SM90 | 1D1D | (1, -, 128) | (1, -, 128) | Float | A per-1×128，B per-1×128（即 per-K 粒度） |
| SM90 | 1D2D | (1, -, 128) | (128, -, 128) | Float | A per-1×128，B per-128×128（二维 block） |
| SM100 | 1D1D | (1, -, K) | (1, -, K) | Int (UE8M0) | A/B 均 per-1×K，SF 使用 UE8M0 打包 |

**默认 recipe 选择**（`get_default_recipe`）：
- SM90：`(1, 128, 128)` → 1D2D 核函数
- SM100（B 的 SF 为 Float，旧格式）：`(1, 128, 128)`
- SM100（B 的 SF 为 Int，1D1D 新格式）：`(1, 1, 128)` 或 `(1, 1, 32)`（MegaMoE）

> **注意**：1D1D 表示 A 和 B 的 SF 在 MN 维度上粒度为 1（per-row/per-column），1D2D 表示 A 为 per-row 而 B 为二维 block。

### 2.3 UE8M0 编码（SM100）

SM100 引入 UE8M0（Unsigned 8-bit Exponent-only, 0 mantissa bits）编码来压缩缩放因子：

- **格式**：8 位无符号整数，表示 2 的幂次指数
- **值**：`scale = 2^(ue8m0_value - bias)`
- **打包**：4 个 UE8M0 scale 打包为 1 个 int32（每个 8 bit）
- **优势**：
  - SF 内存占用减少 4×（Float32 → Int8 packed，即 4 byte/scale → 1 byte/scale）
  - 硬件直接支持 UE8M0 格式的 WGMMA 指令，无需反序列化开销
- **转换函数**（Python 层，[deep_gemm/utils/math.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/DeepGEMM/deep_gemm/utils/math.py)）：
  - `ceil_to_ue8m0(x)`：通过 bit 操作计算 UE8M0 指数
  - `pack_ue8m0_to_int(x)`：4 个 scale 打包为 int32
  - `unpack_ue8m0_from_int(packed_sf)`：解包为 float

---

## 三、缩放因子布局转换

不同架构的核函数对 SF 布局有不同要求（内存排列、TMA 对齐、major 方向）。DeepGEMM 在 API 层自动执行布局转换。

### 3.1 转换入口

```cpp
// csrc/apis/layout.hpp
layout::transform_sf_pair_into_required_layout(
    sfa, sfb, m, n, k, recipe, recipe_a, recipe_b,
    num_groups_a, num_groups_b, disable_ue8m0_cast, psum_layout
) -> tuple<Tensor, Tensor, int, int>
```

### 3.2 转换规则

| 条件 | 转换操作 |
|---|---|
| SM90, Float SF, gran_mn=1, gran_k=128 | `get_mn_major_tma_aligned_tensor(sf)` → MN-major + TMA 对齐 |
| SM90, Float SF, gran_mn=128, gran_k=128 | `check_sf_layout(..., sm90_sfb_check=true)` → contiguous 或 transpose 后 contiguous |
| SM100, Float SF, gran_k∈{32,128} | 广播后 `get_mn_major_tma_aligned_packed_ue8m0_tensor(..., psum_layout)` → UE8M0 打包 + TMA 对齐 |
| SM100, Int SF, gran_mn=1, gran_k∈{32,128} | `check_sf_layout(..., tma_stride_check=true, type_check=kInt)` → 验证 TMA 对齐和 MN-major |

### 3.3 TMA 对齐要求

TMA（Tensor Memory Accelerator）异步拷贝要求数据满足特定对齐约束：
- 行首地址 128 字节对齐
- MN-major（stride(-2)==1）排列
- 维度大小满足 TMA tile 要求

### 3.4 SF 形状校验

```cpp
check_sf_layout(sf, mn, k, gran_mn, gran_k, num_groups,
                tma_stride_check, sm90_sfb_check, type_check)
```

验证 SF 张量：
- dtype 匹配（Float 或 Int）
- 维度为 2D 或 3D（grouped 场景）
- 形状为 `(ceil_div(mn, gran_mn), ceil_div(k, gran_k / (Float ? 1 : 4)))`
  - Int/UE8M0 类型下 gran_k 除以 4（因为 4 个 scale 打包为 1 个 int32）
- TMA 对齐检查（可选）
- contiguous 检查（SM90 B 侧 SF）

---

## 四、Python 量化工具

[deep_gemm/utils/math.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/DeepGEMM/deep_gemm/utils/math.py) 提供完整的 FP8/FP4 量化工具链。

### 4.1 FP8 量化函数

```python
# Per-token 量化：沿 K 维度按 gran_k 分块，每块独立 scale
per_token_cast_to_fp8(x, use_ue8m0, gran_k=128, use_packed_ue8m0=False) -> (x_fp8, sf)

# Per-channel 量化：沿 M 维度分块
per_channel_cast_to_fp8(x, use_ue8m0, gran_k=128) -> (x_fp8, sf)

# Per-block 量化：M 和 K 均按 gran_k 分块
per_block_cast_to_fp8(x, use_ue8m0, gran_k=128) -> (x_fp8, sf)

# 自定义维度量化
per_custom_dims_cast_to_fp8(x, dims, use_ue8m0) -> (x_fp8, sf)
```

### 4.2 FP4 量化函数

```python
# Per-token FP4 量化（nibble packing）
per_token_cast_to_fp4(x, use_ue8m0, gran_k=128, use_packed_ue8m0=False) -> (x_fp4, sf)

# FP4 E2M1 量化核心
_quantize_to_fp4_e2m1(x) -> Tensor  # 码点: {0, 0.5, 1, 1.5, 2, 3, 4, 6}

# Packed FP4 转置
transpose_packed_fp4(a) -> Tensor
```

### 4.3 反量化函数

```python
# FP4 → float
cast_back_from_fp4(packed, sf, gran_k=128, use_packed_ue8m0=False) -> Tensor

# FP8 → float
cast_back_from_fp8(x_fp8, sf, gran_k=128, use_packed_ue8m0=False) -> Tensor
```

### 4.4 辅助函数

```python
ceil_div(x, y) -> int       # 向上取整除法
align(x, y) -> int          # 向上对齐到 y 的倍数
```

---

## 五、核函数分发逻辑

`fp8_fp4_gemm_nt` 的架构分发路径：

```
fp8_fp4_gemm_nt(a, b, d, c, recipe, ...)
  │
  ├─ 检查 major 类型（SM90 要求 A/B 均为 K-major）
  ├─ 检查 C/D 为 N-major
  ├─ 获取逻辑形状（FP4 时最后一维 ×2）
  ├─ early_return 处理（m=0/n=0/k=0）
  ├─ transform_sf_pair_into_required_layout() → (sfa, sfb, gran_k_a, gran_k_b)
  │
  ├─ arch_major == 9 && sfa.dtype == Float:
  │   ├─ gran_n == 1 → sm90_fp8_gemm_1d1d()
  │   └─ gran_n != 1 → sm90_fp8_gemm_1d2d()
  │
  └─ arch_major == 10 && sfa.dtype == Int:
      └─ sm100_fp8_fp4_gemm_1d1d()
```

---

## 六、关键约束

1. **SM90 K-major 要求**：SM90 上 FP8 GEMM 的 A 和 B 必须为 K-major（`stride(-1) == 1`）；SM100 无此限制
2. **C/D N-major 要求**：输出张量 D 和累加张量 C 必须为 N-major（行优先，`stride(-1) == 1`）
3. **FP4 维度扩展**：kPackedFP4（Int8）张量的逻辑 K/MN 维度为物理维度的 2 倍
4. **K 对齐**：FP8 要求 K 对齐到 128（或 recipe 中的 gran_k）；FP4 MegaMoE 要求 K 对齐到 32
5. **SF 类型一致性**：SM90 使用 Float32 SF，SM100 新格式使用 Int32（UE8M0 packed）SF
6. **recipe 互斥**：`recipe`（统一指定）与 `recipe_a`/`recipe_b`（分别指定）互斥，必须同时提供或同时不提供

---

## 七、相关链接

- [/deepseek/deep-gemm/concepts/grouped-gemm](/ai/deepseek/deep-gemm/concepts/grouped-gemm) — 分组 GEMM 中的 FP8 方案
- [/deepseek/deep-gemm/concepts/performance-optimization](/ai/deepseek/deep-gemm/concepts/performance-optimization) — WGMMA 和 TMA 硬件加速
- [/deepseek/deep-gemm/references/api](/ai/deepseek/deep-gemm/references/api) — FP8/FP4 GEMM API 参考
- [/deepseek/deep-gemm/examples/basic-gemm](/ai/deepseek/deep-gemm/examples/basic-gemm) — FP8 GEMM 使用示例
