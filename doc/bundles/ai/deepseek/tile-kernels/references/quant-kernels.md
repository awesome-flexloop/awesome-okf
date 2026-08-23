---
type: api-reference
scope: tile-kernels
name: TileKernels 量化核函数参考
version: "0.1.0"
source: tile_kernels/quant/
description: TileKernels 量化核函数详细参考（FP8/FP4/E5M6 cast、SwiGLU融合、反量化）
---

# TileKernels 量化核函数参考

本章节详细描述 TileKernels 的量化核函数实现，涵盖 FP8 E4M3、FP4 E2M1、E5M6 三种低精度格式的量化/反量化，以及 SwiGLU 融合量化算子。

---

## 一、量化配置体系

### 1.1 CastConfig 数据类

量化核函数使用三个 frozen dataclass 管理配置：

| 配置类 | 基类 | 新增字段 | 用途 |
|---|---|---|---|
| `BaseCastConfig` | — | `torch_dtype`, `sf_block`, `use_tma_aligned_col_major_sf`, `use_packed_ue8m0` | 基础量化参数 |
| `CastInputConfig` | BaseCastConfig | `with_sf: bool = True` | 输入侧配置（是否携带缩放因子） |
| `CastOutputConfig` | BaseCastConfig | `round_sf: bool = False`, `custom_clamp_min_value` | 输出侧配置（舍入、clamp） |

**torch_dtype 映射**：

| fmt 字符串 | torch dtype | TileLang dtype | 说明 |
|---|---|---|---|
| `'e4m3'` | `torch.float8_e4m3fn` | T.float8_e4m3fn | FP8 E4M3 |
| `'e2m1'` | `torch.int8` | T.float4_e2m1fn | FP4 E2M1（packed，两个值打包为一个 int8） |
| `'e5m6'` | `torch.uint32` → uint8 视图 | 自定义 | E5M6（8个值打包为3个uint32） |

**缩放因子格式**：
- 默认：float32，每个缩放因子占 4 字节
- `use_packed_ue8m0=True`：UE8M0 格式（8-bit 指数-only），4 个 scale 打包为 1 个 int32
- `use_tma_aligned_col_major_sf=True`：列主序 TMA 对齐布局

### 1.2 辅助函数

| 函数 | 说明 |
|---|---|
| `get_best_vectorize_size(dtype)` | 根据 GPU compute capability 返回向量化加载大小 |
| `get_cast_input_and_config(x, sf_block)` | 解析输入（普通 tensor 或 QuantTensor），返回 (data, sf, config) |
| `get_cast_output_config(fmt, sf_block, ...)` | 从 fmt 字符串构造 CastOutputConfig |
| `get_logical_hidden(hidden, dtype)` | int8(FP4) 时返回 hidden*2，否则返回 hidden |
| `get_physical_hidden(hidden, dtype)` | int8(FP4) 时返回 hidden//2，否则返回 hidden |
| `get_sf_shape(shape, config)` | 计算缩放因子的 shape |
| `alloc_scaling_factors(shape, out_config, device)` | 分配缩放因子张量 |
| `cast_epilogue(out_sf, num_tokens, hidden, config)` | kernel 启动后的 sf 后处理 |
| `unpack_from_e2m1fn_x2(x, out_dtype)` | packed FP4 解码为高精度 |

### 1.3 TileLang 宏复用

量化 kernel 间通过 `@T.macro` 复用四个核心宏：

- `get_sf_and_inv(amax, out_config)`：从 amax 计算 sf 和 sf_inv，支持 round_sf（2 的幂次舍入）
- `load_sf(tensor, m_idx, k_idx, config)`：从全局内存加载 sf（支持 packed_ue8m0 和 col-major）
- `transform_sf(sf, config) -> T.float32`：sf 转换为 float32 用于计算
- `store_sf(tensor, sf, m_idx, k_idx, config)`：存储 sf 到全局内存

---

## 二、Per-Token 量化

### 2.1 per_token_cast

逐 token 量化，每行独立计算缩放因子。适用于激活值（activation）量化。

**JIT kernel 工厂**：`get_per_token_cast_kernel(...)` 使用 `@tilelang.jit` 装饰。

**Python wrapper 签名**：

```python
def per_token_cast(
    x: torch.Tensor,           # (num_tokens, hidden)，输入高精度张量
    fmt: str,                  # 'e4m3' 或 'e2m1'
    num_per_channels: int,     # 每个缩放因子覆盖的 channel 数
    x_block_size=None,         # 可选输入 block 大小
    use_tma_aligned_col_major_sf=False,
    round_sf=False,
    use_packed_ue8m0=False,
) -> QuantTensor              # (data, sf)
```

**工作流程**：
1. 每个 token 沿 channel 维度分块，每块大小为 `num_per_channels`
2. 对每块求 `amax = max(|x|)`
3. 计算 `sf = amax / max_quant_val`，可选舍入到 2 的幂次
4. 量化：`x_q = cast_to_low_precision(x / sf, RTNE)`
5. FP4 时两个 4-bit 值打包为一个 int8

**变体**：
- `per_token_cast_with_sf_only(...)`：仅计算 sf，不输出量化数据
- `per_token_cast_with_precomputed_sf(x, fmt, num_per_channels, sf, ...)`：使用预计算 sf 量化

### 2.2 per_token_cast_to_e5m6

逐 token 量化到 E5M6 格式。E5M6 是 DeepSeek 设计的 12-bit 浮点格式，精度接近 FP16 但位宽仅 12bit，主要用于 KV cache 等需要高压缩比但保留精度的场景。

**格式定义**：
- 位分配：1 位符号 + 5 位指数 + 6 位尾数（12bit）
- 指数 bias：15
- 打包方式：8 个 E5M6 值（96bit）打包为 3 个 uint32（12 字节）
- 输出数据类型：uint8，shape 为 `(num_tokens, hidden*3//2)`
- 数值范围：max_normal=65024.0, min_normal=2^-14, max_subnormal=2^-14*63/64, min_subnormal=2^-20

**约束**：
- `num_per_channels` 必须等于 `hidden`（即每 token 一个全局 sf）
- `hidden % 8 == 0`

**内部实现**：
- `float_to_e5m6(...)` 宏：float32 → E5M6 RTZ 截断（类 FP16 转换）
- `get_sf_and_inv_e5m6(amax, out_config)`：E5M6 专用 sf 计算

---

## 三、Per-Block 量化

### per_block_cast

逐 block 量化，每个矩形 block 独立计算缩放因子。适用于权重量化。

**JIT kernel 工厂**：`get_per_block_cast_kernel(...)`。

**Python wrapper 签名**：

```python
def per_block_cast(
    x: torch.Tensor,                    # (M, K)，输入权重
    fmt: str,                           # 'e4m3' 或 'e2m1'
    block_size: tuple[int, int],        # (block_m, block_k)，量化块大小
    use_tma_aligned_col_major_sf=False,
    round_sf=False,
    use_packed_ue8m0=False,
) -> QuantTensor
```

**变体**：
- `per_block_cast_with_sf_only(...)`：仅计算 sf
- `per_block_cast_with_precomputed_sf(...)`：使用预计算 sf

### per_block_cast_lossless

FP4 → FP8 无损重量化。将已量化的 FP4 数据无损上转为 FP8 格式（因为 FP8 精度高于 FP4，所以无精度损失）。

**约束**：
- fmt 必须为 `'e4m3'`（输出 FP8）
- 输入必须为 e2m1（FP4）格式的 QuantTensor

**使用场景**：MoE 训练中，权重以 FP4 存储以节省显存，计算时按需无损上转到 FP8 供 Tensor Core 使用。

---

## 四、Per-Channel 量化

### per_channel_cast

逐 channel 量化，缩放因子沿 token 维度分组（每 `num_per_tokens` 行共享一个 sf）。

```python
def per_channel_cast(
    x: torch.Tensor,
    fmt: str,            # 必须为 'e4m3'
    num_per_tokens: int, # 必须为 128
    round_sf: bool = False,
) -> QuantTensor
```

**约束**：
- fmt 必须为 `'e4m3'`（FP8）
- `num_tokens % 128 == 0`
- `hidden % 64 == 0`
- `num_per_tokens` 必须为 128

内部调用 `per_channel_cast_fused`。

### per_channel_cast_fused

融合 per-channel 量化，支持 FP8 输入反量化重缩放和 token 扩展。

```python
def per_channel_cast_fused(
    x: torch.Tensor | QuantTensor,
    fmt: str,                    # 必须为 'e4m3'
    num_per_tokens: int,         # 必须为 128
    round_sf=False,
    num_per_channels=None,
    pos_to_token=None,           # 可选 token 索引映射，用于 gather/expand
) -> QuantTensor
```

**高级特性**：
- **FP8 输入重缩放**：当 x 为 QuantTensor（已有 FP8 数据+sf）时，先反量化再重新量化到新的 per-channel sf
- **Token 扩展**：`pos_to_token` 参数允许在量化同时执行 token 维度的 gather 操作（MoE dispatch 场景）
- **输出对齐**：使用 pos_to_token 时输出 token 数需 16 对齐，否则 128 对齐

**内部宏**：`transform_token_idx(with_expand, idx, token_idx, x)` 处理 token 索引转换。

### per_channel_cast_and_transpose

量化 + 转置融合 kernel。

```python
def per_channel_cast_and_transpose(
    x: torch.Tensor,
    fmt: str,
    num_per_tokens: int,
    round_sf: bool = False,
) -> QuantTensor
```

输出为转置布局 `(hidden, num_tokens)`，减少一次单独的转置操作。

---

## 五、反量化

### cast_back

通用反量化 kernel，将低精度 QuantTensor 转回高精度。

**JIT kernel 工厂**：`get_cast_back_kernel(...)`。

```python
def cast_back(
    x: QuantTensor,                       # (data, sf)
    fmt: str,                             # 'bf16' 或 'fp32'，输出精度
    x_block_size: tuple[int, int],        # 量化时的 block 大小
    x_special_fmt: str | None = None,     # 可选 'e5m6'
) -> torch.Tensor
```

### per_token_cast_back

逐 token 反量化，是 `cast_back` 的便捷封装：

```python
def per_token_cast_back(
    x: QuantTensor,
    fmt: str,
    num_per_channels: int,
    x_special_fmt=None,
) -> torch.Tensor
# 等价于 cast_back(x, fmt, (1, num_per_channels), x_special_fmt=x_special_fmt)
```

### cast_back_e5m6

E5M6 格式专用反量化 kernel。

**JIT kernel 工厂**：`get_cast_back_e5m6_kernel(...)`。

```python
def cast_back_e5m6(
    x: QuantTensor,
    fmt: str,                      # 输出精度
    x_block_size: tuple[int, int],
) -> torch.Tensor
```

- 输入 data 为 uint8（packed E5M6），shape 为 `(num_tokens, hidden*3//2)`
- 内部 `e5m6_to_float(...)` 函数执行 E5M6 → fp16 → float32 解包

---

## 六、SwiGLU 融合量化

### swiglu_forward_and_per_token_cast

SwiGLU 激活（`silu(x_left) * x_right`）+ 按 topk 权重缩放 + FP8 量化融合 kernel。这是 MoE 层 Expert GEMM 后的关键融合算子。

**JIT kernel 工厂**：`get_swiglu_forward_and_per_token_cast_kernel(...)`。

```python
def swiglu_forward_and_per_token_cast(
    x: torch.Tensor,                          # (num_expanded_tokens, hidden*2) bf16
    fmt: str,                                 # 必须为 'e4m3'
    num_per_channels: int,
    pos_to_token_topk=None,                   # 可选 topk 位置映射
    topk_weights=None,                        # 可选路由权重
    pos_to_expert=None,                       # 可选 expert 映射
    use_tma_aligned_col_major_sf=False,
    round_sf=False,
    use_packed_ue8m0=False,
    swiglu_clamp_value=None,                  # 可选激活 clamp 值
    clamped_count=None,                       # 可选 clamp 计数输出
    sf_clamp_min=None,                        # 可选 sf 最小值 clamp
) -> QuantTensor
```

**融合计算**：
1. 将 x 沿 hidden 维拆分为 gate(x_left) 和 up(x_right)
2. 计算 `silu(gate) * up`（SwiGLU 激活）
3. 如果提供 topk_weights，乘以路由权重
4. 如果设置 swiglu_clamp_value，对激活值进行 clamp
5. 对结果进行 per-token FP8 量化

### swiglu_backward_and_per_token_cast

SwiGLU 反向传播 + 梯度 FP8 量化融合。

**JIT kernel 工厂**：`get_swiglu_backward_and_per_token_cast_kernel(...)`。

```python
def swiglu_backward_and_per_token_cast(
    x: QuantTensor,                           # FP8 输入 (data, sf)
    grad_out: torch.Tensor,                   # 输出梯度
    weight: torch.Tensor,                     # 权重
    pos_to_token_topk: torch.Tensor,
    token_topk_to_pos: torch.Tensor,
    num_per_channels: int,                    # 必须为 32 或 128
    round_sf=False,
    swiglu_clamp_value=None,
) -> tuple[Tensor, QuantTensor, Tensor, Tensor]
# 返回: (out_bf16, (x_grad_fp8, x_grad_fp8_sf), x_grad_bf16, weight_grad)
```

### swiglu_forward_and_per_channel_cast_and_transpose

SwiGLU 前向 + per-channel 量化 + 转置三重融合。

```python
def swiglu_forward_and_per_channel_cast_and_transpose(
    x: torch.Tensor,                   # bf16
    fmt: str,                          # 必须为 'e4m3'
    num_per_tokens: int,               # 32 或 128
    round_sf=False,
    without_transpose=False,           # True 时不转置
    swiglu_clamp_value=None,
) -> QuantTensor
```

**约束**：
- x 必须为 bfloat16
- `num_tokens % 128 == 0`
- `hidden % 128 == 0`

---

## 七、量化数据格式规范

### FP8 E4M3（torch.float8_e4m3fn）

| 属性 | 值 |
|---|---|
| 位宽 | 8 bit |
| 符号位 | 1 bit |
| 指数位 | 4 bit（bias=7） |
| 尾数位 | 3 bit |
| 最大正值 | 448.0 |
| 最小正值 | 2^-10（subnormal） |
| Clamp min | 1e-4（避免下溢到0） |
| 舍入模式 | RTNE（round to nearest, ties to even） |

### FP4 E2M1（torch.int8，packed）

| 属性 | 值 |
|---|---|
| 位宽 | 4 bit |
| 符号位 | 1 bit |
| 指数位 | 2 bit（bias=1） |
| 尾数位 | 1 bit |
| 可表示值 | {0, ±0.5, ±1, ±1.5, ±2, ±3, ±4, ±6} |
| 最大正值 | 6.0 |
| 最小正值 | 2^-126（subnormal 通过 sf 表示） |
| 打包方式 | 两个 4-bit 值打包为一个 int8（低 4 位 + 高 4 位） |
| 舍入模式 | RTNE |

### E5M6（torch.uint8，packed）

| 属性 | 值 |
|---|---|
| 位宽 | 12 bit |
| 符号位 | 1 bit |
| 指数位 | 5 bit（bias=15） |
| 尾数位 | 6 bit |
| 最大正规数 | 65024.0 |
| 最小正规数 | 2^-14 |
| 最大次正规数 | 2^-14 × 63/64 |
| 最小次正规数 | 2^-20 |
| 打包方式 | 8 个 12-bit 值打包为 3 个 uint32（96 bit = 12 字节） |
| 转换方式 | float32 → fp16 RTZ → E5M6（截断低 4 位尾数） |
| 主要用途 | KV cache 压缩 |

---

## 八、缩放因子布局

### 标准布局（float32 sf）

缩放因子 shape 为 `(ceil(M/block_m), ceil(K/block_k))`，每个元素为 float32。

### TMA 对齐列主序布局

`use_tma_aligned_col_major_sf=True` 时，sf 以列主序存储并做 TMA 对齐，适用于 Hopper TMA 异步加载。

### UE8M0 打包布局

`use_packed_ue8m0=True`（SM100 Blackwell）时，缩放因子使用 UE8M0（无符号 8-bit exponent-only）格式编码，4 个 scale 打包为 1 个 int32，减少内存带宽。UE8M0 的值为 `2^(ue8m0 - 127)`，可表示范围 `2^-127` 到 `2^128`。
