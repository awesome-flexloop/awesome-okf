---
type: concept
scope: tile-kernels
name: FP8/FP4 量化与反量化
version: "0.1.0"
source: tile-kernels-spec-facts
description: TileKernels 量化体系详解——FP8 E4M3、FP4 E2M1、E5M6 三种低精度格式，per-token/per-block/per-channel 量化粒度，SwiGLU 融合量化
---

# FP8/FP4 量化与反量化

量化是大语言模型训练和推理中的关键技术，通过将激活和权重量化到低精度格式（FP8/FP4/E5M6）来减少显存占用和内存带宽。TileKernels 提供了完整的量化核函数库，支持多种精度、多种量化粒度以及与 SwiGLU 激活的融合。

---

## 一、支持的量化格式

### 1.1 FP8 E4M3（torch.float8_e4m3fn）

FP8 是当前大模型训练的主流低精度格式，在 Hopper 及更新架构上由 Tensor Core 原生支持。

| 属性 | 值 |
|---|---|
| 总位宽 | 8 bit |
| 符号位 | 1 bit |
| 指数位 | 4 bit（bias=7） |
| 尾数位 | 3 bit |
| 可表示的最大值 | 448.0 |
| 可表示的最小正规数 | 2^-7 |
| Clamp 最小值 | 1e-4（避免下溢到0的精度保护） |
| 舍入模式 | RTNE（Round to Nearest, Ties to Even） |
| PyTorch dtype | `torch.float8_e4m3fn` |

FP8 E4M3 的动态范围与 BF16 相当（最大 448 vs BF16 的 ~3.39e38），但精度较低（3 位尾数 ≈ 10^-1 相对精度）。通过分块缩放因子（block-wise scaling）可以补偿精度损失。

### 1.2 FP4 E2M1（torch.int8，packed）

FP4 是 Blackwell 架构引入的极低精度格式，位宽仅 4 bit，适合 MoE 等对带宽极度敏感的场景。

| 属性 | 值 |
|---|---|
| 总位宽 | 4 bit |
| 符号位 | 1 bit |
| 指数位 | 2 bit（bias=1） |
| 尾数位 | 1 bit |
| 可表示值 | {0, ±0.5, ±1, ±1.5, ±2, ±3, ±4, ±6} |
| 最大值 | 6.0 |
| 打包方式 | 两个 4-bit 值打包为 1 个 int8（低 4 位 + 高 4 位） |
| PyTorch dtype | `torch.int8`（packed）/ TileLang `T.float4_e2m1fn` |
| 舍入模式 | RTNE |

FP4 的物理存储：一个 int8 包含两个 E2M1 值，低 4 位为第一个值，高 4 位为第二个值。因此 FP4 张量的物理 hidden 维度为逻辑 hidden 的一半。

**E2M1 码点表**（bias=1）：

| E2M1 bits | 值 |
|---|---|
| 0 000 | 0 |
| 0 001 | 0.5 |
| 0 010 | 1.0 |
| 0 011 | 1.5 |
| 0 100 | 2.0 |
| 0 101 | 3.0 |
| 0 110 | 4.0 |
| 0 111 | 6.0 |

### 1.3 E5M6（torch.uint8，packed）

E5M6 是 DeepSeek 自定义的 12-bit 浮点格式，精度接近 FP16 但位宽仅 12bit，主要用于 KV cache 压缩等需要高压缩比同时保持精度的场景。

| 属性 | 值 |
|---|---|
| 总位宽 | 12 bit |
| 符号位 | 1 bit |
| 指数位 | 5 bit（bias=15） |
| 尾数位 | 6 bit |
| 最大正规数 | 65024.0 |
| 最小正规数 | 2^-14 |
| 最大次正规数 | 2^-14 × 63/64 |
| 最小次正规数 | 2^-20 |
| 打包方式 | 8 个 12-bit 值（96 bit）打包为 3 个 uint32（12 字节） |
| 物理存储 | uint8 张量，shape 为 `(num_tokens, hidden*3//2)` |
| 转换路径 | float32 → fp16 RTZ（截断低 4 位尾数）→ E5M6 |

E5M6 实际上是 FP16 的截断版本（FP16 有 10 位尾数，E5M6 取高 6 位），因此 fp16→E5M6 是 RTZ 截断，反向是精确恢复。

### 1.4 BF16 与 FP32 的角色

- **BF16**（torch.bfloat16）：主计算精度，用于 forward/backward 中的矩阵乘输入输出
- **FP32**（torch.float32）：累加精度、权重存储、缩放因子、中间结果
- **FP16**（torch.float16）：仅作为 E5M6 反量化的中间格式
- **TF32**：通过 `round_to_tf32()` 将 float32 舍入到 TF32 精度（19 bit），用于 Tensor Core GEMM 输入

---

## 二、量化粒度

### 2.1 Per-Token 量化（per_token_cast）

每个 token（行）独立计算缩放因子，沿 hidden 维度可分块。

```
sf[m] = amax(x[m, :]) / max_quant_val
x_q[m, :] = quantize(x[m, :] / sf[m])
```

**参数**：`num_per_channels` 控制每个 sf 覆盖的 channel 数。例如 `num_per_channels=32` 时，每 32 个 channel 共享一个 sf。

**适用场景**：激活量化（activations），因为激活值的范围在 token 间差异很大。

### 2.2 Per-Block 量化（per_block_cast）

每个 M×K 矩形块独立计算缩放因子。

```
for i in range(0, M, block_m):
    for j in range(0, K, block_k):
        block = x[i:i+block_m, j:j+block_k]
        sf[i//block_m, j//block_k] = amax(block) / max_quant_val
        block_q = quantize(block / sf[i//block_m, j//block_k])
```

**参数**：`block_size=(block_m, block_k)` 指定块大小，常用 (128, 128)。

**适用场景**：权重量化，因为权重的统计特性在局部块内相对均匀。

### 2.3 Per-Channel 量化（per_channel_cast）

缩放因子沿 token 维度分组，每 `num_per_tokens` 行共享一个 sf。

**约束**：
- 仅支持 FP8 E4M3
- `num_per_tokens` 必须为 128
- token 数需 128 对齐，hidden 需 64 对齐

**适用场景**：MoE expert GEMM 输出的量化，配合 DeepGEMM 的 per-channel scaling。

### 2.4 Per-Channel 融合量化（per_channel_cast_fused）

在 per-channel 量化基础上增加了两个融合能力：

1. **FP8 输入重缩放**：当输入已经是 QuantTensor（FP8 数据+sf）时，先反量化再重新量化到新的 per-channel sf，避免显式 cast_back→cast 两步
2. **Token 扩展（gather）**：通过 `pos_to_token` 参数在量化同时执行 token 维度的 gather 操作，常用于 MoE dispatch

---

## 三、缩放因子（Scale Factor）

缩放因子是量化的核心，它将低精度值映射回高精度值域：

```
x_dequant = x_quant * sf
```

### 3.1 SF 布局

| 布局类型 | 说明 | 适用场景 |
|---|---|---|
| 标准 float32 | 每个 sf 为 float32，shape `(M/block_m, K/block_k)` | 默认 |
| TMA 对齐列主序 | sf 以列主序存储并 TMA 对齐 | Hopper TMA 异步加载 |
| UE8M0 打包 | 4 个 scale 打包为 1 个 int32（SM100） | Blackwell 架构，减少带宽 |

### 3.2 SF 舍入（round_sf）

当 `round_sf=True` 时，缩放因子被舍入到最近的 2 的幂次。这使得反量化中的乘法可以用位移操作替代，在某些硬件上更快，但会引入微小精度损失。

### 3.3 UE8M0 编码

UE8M0（Unsigned 8-bit Exponent-only, Mantissa 0）是 Blackwell 架构引入的缩放因子编码格式：

- 8 bit 无符号整数，纯指数编码
- 表示值：`2^(ue8m0_value - 127)`
- 范围：`2^-127` 到 `2^128`
- 4 个 UE8M0 值打包为 1 个 int32
- 设置 `use_packed_ue8m0=True` 启用

---

## 四、反量化

反量化将低精度 QuantTensor 恢复为高精度：

```python
# 通用反量化
x_bf16 = tile_kernels.quant.cast_back((x_fp8, x_sf), fmt='bf16', x_block_size=(128, 128))

# Per-token 反量化（便捷封装）
x_bf16 = tile_kernels.quant.per_token_cast_back((x_fp8, x_sf), fmt='bf16', num_per_channels=32)

# E5M6 反量化
x_fp32 = tile_kernels.quant.cast_back((x_e5m6, x_sf), fmt='fp32', x_block_size=(1, hidden), x_special_fmt='e5m6')
```

支持输出精度：BF16 和 FP32。

---

## 五、SwiGLU 融合量化

SwiGLU 是 LLM 中 FFN 层的标准激活函数：`SwiGLU(x) = silu(x_gate) * x_up`。在 MoE 场景中，expert FFN 的输出通常需要量化后送入下一个 GEMM，将 SwiGLU 激活和量化融合为单个 kernel 可以显著减少显存读写。

### 5.1 SwiGLU + Per-Token 量化

```
x (bf16, num_expanded_tokens, 2*hidden)
  → split into gate/up
  → silu(gate) * up                    # SwiGLU 激活
  → * topk_weights (可选)              # 路由权重缩放
  → clamp (可选)                       # 值域裁剪
  → FP8 per-token 量化                 # 量化输出
  → QuantTensor (fp8_data, sf)
```

融合点：激活计算和量化在一个 kernel 中完成，SwiGLU 输出直接写为 FP8，不需要写 BF16 中间结果再量化。

### 5.2 SwiGLU + Per-Channel 量化 + 转置

```
x (bf16) → SwiGLU → per-channel FP8 量化 → 转置
```

三重融合：激活+量化+转置在一个 kernel 中完成，输出直接为 `(hidden, num_tokens)` 布局，供后续权重 GEMM 使用。

### 5.3 SwiGLU 反向 + 量化

反向传播中，SwiGLU 的梯度计算和梯度量化同样融合：

```
(grad_out, weight, x_fp8, sf)
  → FP8 反量化
  → SwiGLU 反向梯度计算
  → 梯度 FP8 量化
  → (out_bf16, x_grad_fp8, x_grad_bf16, weight_grad)
```

---

## 六、FP4 → FP8 无损重量化

`per_block_cast_lossless` 实现 FP4 → FP8 的无损上转。由于 FP8 的精度（3 位尾数）高于 FP4（1 位尾数），FP4 量化的结果可以精确表示为 FP8 值，不需要额外的精度损失。

**应用场景**：MoE 训练中，expert 权重以 FP4 格式存储以节省显存，在需要计算时无损上转为 FP8 供 Tensor Core 使用。

**约束**：
- 输入必须为 E2M1（FP4）格式
- 输出为 E4M3（FP8）格式
- 支持 block size 转换（输入和输出的 block_size 可以不同）

---

## 七、量化配置数据类

```python
@dataclass(frozen=True)
class BaseCastConfig:
    torch_dtype: torch.dtype = torch.float8_e4m3fn
    sf_block: tuple[int, int] = (1, 1)
    use_tma_aligned_col_major_sf: bool = False
    use_packed_ue8m0: bool = False

    @property
    def dtype(self) -> T.dtype:       # TileLang dtype
    @property
    def sf_torch_dtype(self) -> torch.dtype:  # float32 或 uint8
    @property
    def sf_dtype(self) -> T.dtype:

@dataclass(frozen=True)
class CastInputConfig(BaseCastConfig):
    with_sf: bool = True              # 输入是否携带缩放因子

@dataclass(frozen=True)
class CastOutputConfig(BaseCastConfig):
    round_sf: bool = False            # SF 是否舍入到2的幂次
    custom_clamp_min_value: float | None = None

    @property
    def clamp_min_value(self) -> float:  # e4m3→1e-4, e2m1→T.max_value(dtype)*2^-126
```

使用 `get_cast_output_config(fmt, sf_block, ...)` 从 fmt 字符串构造配置：
- `'e4m3'` → torch.float8_e4m3fn
- `'e2m1'` → torch.int8
- `'e5m6'` → torch.uint32（E5M6 专用）

---

## 八、TileLang 宏复用

量化 kernel 之间通过四个 `@T.macro` 宏共享核心逻辑：

| 宏 | 功能 |
|---|---|
| `get_sf_and_inv(amax, out_config)` | 从 amax 计算 sf 和 1/sf，支持 round_sf |
| `load_sf(tensor, m_idx, k_idx, config)` | 从全局内存加载 sf，支持 packed_ue8m0 和 col-major |
| `transform_sf(sf, config)` | 将 sf 转换为 float32 用于计算 |
| `store_sf(tensor, sf, m_idx, k_idx, config)` | 将 sf 存储到全局内存 |

这种宏复用保证了所有量化 kernel 在 sf 计算、加载、存储上的一致性。
