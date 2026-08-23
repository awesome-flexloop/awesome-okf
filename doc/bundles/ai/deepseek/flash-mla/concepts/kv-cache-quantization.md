---
type: concept
scope: flash-mla
name: FP8 KV Cache 量化
version: "1.0.0"
source: README.md, csrc/sm90/decode/sparse_fp8/config.h, csrc/sm100/decode/head64/config.h, tests/quant.py
description: FlashMLA FP8 KV Cache 量化方案，V32 与 MODEL1 模式对比，反量化流程与精度设计
---

# FP8 KV Cache 量化

FlashMLA 在稀疏注意力（DSA）解码中使用 FP8 量化 KV cache 以减少内存占用和带宽消耗。量化方案采用分块缩放因子（per-tile scale）的 FP8 E4M3 格式，对 NoPE（非位置编码）部分进行量化，而 RoPE（旋转位置编码）部分保持 BF16 精度不量化。

---

## 一、为什么需要 FP8 KV Cache 量化

### 1.1 内存带宽瓶颈

在 LLM 推理中，KV cache 的内存访问是解码阶段的主要瓶颈：

- **内存受限场景**：当 batch size 小、序列短时，计算量小于 HBM 带宽所能提供的速度，性能由 KV 加载速度决定
- **计算受限场景**：当 batch size 大、序列长或使用稀疏注意力时，计算成为瓶颈，此时需要减少每次计算的数据量
- FP8 量化将每个 NoPE 值从 2 字节（BF16）压缩到 1 字节（FP8），直接翻倍有效带宽

### 1.2 量化精度考量

直接对整个 KV cache 进行低精度量化会导致显著精度损失。FlashMLA 采用分而治之的策略：

| KV 组成部分 | 精度敏感度 | 量化方式 | 原因 |
|---|---|---|---|
| NoPE（压缩潜在向量） | 相对不敏感 | FP8 E4M3 + per-tile scale | 主要承载语义信息，低秩结构对量化更鲁棒 |
| RoPE（位置编码部分） | 高度敏感 | BF16 不量化 | 位置信息精度直接影响注意力的位置区分能力 |

---

## 二、FP8 E4M3 数据格式

FlashMLA 使用 `float8_e4m3fn`（E4M3）格式存储量化的 NoPE 数据：

| 属性 | 值 |
|---|---|
| 位宽 | 8 bit |
| 指数位 | 4 bit |
| 尾数位 | 3 bit |
| 表示范围 | [-448, 448]（有限值） |
| 特殊值 | 无 inf，NaN 表示为 1.0000000b（仅负零） |
| 精度分布 | 大值处绝对精度低，小值处绝对精度高（浮点特性） |

选择 E4M3 而非 E5M2 的原因：E4M3 有更多尾数（3 bit vs 2 bit），在神经网络权重/激活的典型值范围内提供更好的精度，且 448 的表示范围足以覆盖注意力激活值。

---

## 三、V32 模式量化格式

V32 模式是 DeepSeek-V3/V3.1/V3.2/R1 使用的格式，每个 token 的 KV cache 占用 656 字节。

### 3.1 内存布局

```
字节偏移:  0                  511  512   515   519   523   527  528             655
           ├────────────────────┼────┬─────┬─────┬─────┬─────┼─────────────────┤
内容:      │  FP8 NoPE 数据     │scale0│scale1│scale2│scale3│   BF16 RoPE 数据   │
           │  (512 个值)        │(fp32)│(fp32)│(fp32)│(fp32)│   (64 个值)       │
           │  512 字节          │ 4 B │ 4 B │ 4 B │ 4 B │   128 字节         │
           └────────────────────┴────┴─────┴─────┴─────┴─────┴─────────────────┘
                                              总计: 656 字节/token
```

### 3.2 缩放因子策略

- **量化 tile 大小**：`QUANT_TILE_SIZE = 128`，即每 128 个连续的 FP8 值共享一个 float32 缩放因子
- **缩放因子数量**：`NUM_SCALES = d_noPE / QUANT_TILE_SIZE = 512 / 128 = 4`
- **缩放因子存储**：4 个 float32 值，紧跟在 FP8 数据之后，共 16 字节
- **缩放因子含义**：`scale[i]` 是第 i 个 tile（128 个 FP8 值）的反量化缩放因子

### 3.3 反量化公式

```python
def dequant_v32(kv_bytes):
    """V32 模式反量化"""
    # 解析 FP8 NoPE
    nope_fp8 = kv_bytes[:512].view(torch.float8_e4m3fn)  # (512,)
    
    # 解析缩放因子
    scales = kv_bytes[512:528].view(torch.float32)       # (4,)
    
    # 解析 BF16 RoPE
    rope_bf16 = kv_bytes[528:656].view(torch.bfloat16)   # (64,)
    
    # 反量化 NoPE
    nope_tiles = nope_fp8.view(4, 128)
    nope_bf16 = (nope_tiles.float() * scales[:, None]).to(torch.bfloat16).view(512)
    
    # V 向量完全在 NoPE 部分（V_HAVE_ROPE = false）
    # v = nope_bf16[:512]
    # k_nope = nope_bf16
    # k_rope = rope_bf16
    
    return nope_bf16, rope_bf16
```

### 3.4 V32 模式关键特性

- **d_noPE = 512**：NoPE 维度等于 V 输出维度
- **V_HAVE_ROPE = false**：V 向量完全从 NoPE 部分计算，不涉及 RoPE
- **RoPE 维度 d_R = 64**：K 的位置编码部分
- **量化 tile = 128**：较大的 tile 大小，缩放因子开销仅 16 字节/token（2.4%）
- **K_ROPE_SW = 64 字节**：SM100 上 RoPE 部分通过 64 字节宽度的 shared memory load 加载

---

## 四、MODEL1 模式量化格式

MODEL1 模式是 DeepSeek 新配置模型使用的格式，每个 token 的 KV cache 占用 576 字节。

### 4.1 与 V32 的关键区别

| 属性 | V32 | MODEL1 |
|---|---|---|
| d_qk (head_dim_k) | 576 | 512 |
| d_noPE | 512 | 448 |
| d_RoPE | 64 | 64 |
| QUANT_TILE_SIZE | 128 | 64 |
| NUM_SCALES | 4 | 8（含 1 padding） |
| bytes_per_token | 656 | 576 |
| V_HAVE_ROPE | false | true |
| K_ROPE_SW | 64 字节 | 128 字节 |
| TMA_K_STRIDE | 656 | 576 |

### 4.2 MODEL1 模式特点

- **更细粒度的量化**：QUANT_TILE_SIZE=64（vs V32 的 128），每 64 个 FP8 值一个缩放因子
- **更多缩放因子**：448/64=7 个有效 scale + 1 padding = 8 个 float32（32 字节）
- **V 包含 RoPE**：V_HAVE_ROPE=true，V 的计算需要 RoPE 部分参与（上行投影后 RoPE 影响 V）
- **更紧凑的存储**：576 字节/token，比 V32 节省 12.2% 内存

---

## 五、量化与反量化流程

### 5.1 量化（写入 KV Cache 时）

```python
import torch

def quantize_kv_fp8(nope_bf16: torch.Tensor, rope_bf16: torch.Tensor, 
                    quant_tile_size: int = 128) -> torch.Tensor:
    """
    将 BF16 KV 数据量化为 FP8 紧凑格式
    
    Args:
        nope_bf16: (..., d_noPE) BF16 张量
        rope_bf16: (..., d_R) BF16 张量（d_R=64）
        quant_tile_size: 128 (V32) 或 64 (MODEL1)
    
    Returns:
        紧凑的字节缓冲区，每个 token 占 bytes_per_token 字节
    """
    d_noPE = nope_bf16.shape[-1]
    d_R = rope_bf16.shape[-1]
    num_scales = d_noPE // quant_tile_size
    bytes_per_token = d_noPE + num_scales * 4 + d_R * 2
    
    # Reshape 为 per-tile
    tiles = nope_bf16.float().view(*nope_bf16.shape[:-1], num_scales, quant_tile_size)
    
    # 计算 per-tile 缩放因子：amax / 448（FP8 E4M3 最大值）
    amax = tiles.abs().amax(dim=-1, keepdim=True)  # (..., num_scales, 1)
    scales = (amax / 448.0).to(torch.float32)      # (..., num_scales, 1)
    
    # 量化：除以 scale，截断到 FP8 范围，转换为 float8_e4m3fn
    nope_fp8 = (tiles / scales).clamp(-448, 448).to(torch.float8_e4m3fn)
    nope_fp8 = nope_fp8.view(*nope_bf16.shape[:-1], d_noPE)
    
    # 拼接为字节缓冲区
    # FP8 数据 (d_noPE B) + scales (num_scales*4 B) + RoPE BF16 (d_R*2 B)
    buf = torch.empty(*nope_bf16.shape[:-1], bytes_per_token, 
                      dtype=torch.uint8, device=nope_bf16.device)
    
    # 写入 FP8 NoPE 数据
    buf[..., :d_noPE] = nope_fp8.view(torch.uint8)
    
    # 写入缩放因子
    scale_offset = d_noPE
    buf[..., scale_offset:scale_offset + num_scales*4] = scales.view(torch.uint8)
    
    # MODEL1 模式需要在 scales 后添加 padding 到 8 个 float32
    if num_scales < 8:
        buf[..., scale_offset + num_scales*4:scale_offset + 32] = 0
    
    # 写入 RoPE BF16 数据
    rope_offset = d_noPE + (8 if num_scales > 4 else num_scales) * 4
    buf[..., rope_offset:rope_offset + d_R*2] = rope_bf16.view(torch.uint8)
    
    return buf
```

### 5.2 反量化（Kernel 内执行）

FlashMLA kernel 在 shared memory 中执行反量化，基本步骤：

1. **全局内存加载**：使用 PTX `ld.global.nc` 指令带 L1/L2 缓存提示从 HBM 加载 FP8 数据和 scale
2. **寄存器反量化**：`cvt_fp8x8_bf16x8` 一次转换 8 个 FP8 值为 BF16，并乘以对应 scale
3. **写入 shared memory**：反量化后的 BF16 数据写入 smem 供 WGMMA/UTCMMA 使用

SM90 上的关键反量化 PTX 指令特性：
- `ld.global.nc.L1::EVICT_LAST.L2::B256`：非一致加载（read-only texture path），L1 evict-last 策略，L2 256 字节预取
- 向量化加载：128-bit（16 字节）或 64-bit（8 字节）对齐加载
- 转换：FP8→BF16 硬件转换（CUDA >= 12.8 支持原生指令，否则使用软件转换）

---

## 六、量化精度设计考量

### 6.1 为什么 NoPE 可以 FP8 量化

1. **低秩结构**：MLA 的 NoPE 部分是低秩压缩后的潜在向量（512/448 维），信息冗余度高，对量化噪声更鲁棒
2. **Per-tile scale**：128/64 粒度的缩放因子能有效适应不同 tile 的值分布差异
3. **BF16 计算**：反量化后在 BF16 精度下进行注意力计算（WGMMA 使用 BF16 输入），不累积 FP8 截断误差

### 6.2 为什么 RoPE 保持 BF16

1. **位置编码敏感性**：RoPE 携带位置信息，量化误差会直接影响位置区分能力
2. **维度小**：RoPE 仅 64 维（128 字节），仅占 V32 总 656 字节的 19.5%，不量化的代价可接受
3. **高频分量**：位置编码包含高频分量（表示近位置和精确位置），需要更高精度保持

### 6.3 Per-tile vs Per-token vs Per-tensor

FlashMLA 选择 per-tile（per-block-of-128/64-elements）缩放因子，权衡如下：

| 策略 | 精度 | 存储开销 | 实现复杂度 |
|---|---|---|---|
| Per-tensor（全局一个 scale） | 最差 | 4 字节/token | 最简单 |
| **Per-tile（128/64 个值一组）** | **好** | **16/32 字节/token** | **中等** |
| Per-token（每行一个 scale） | 好 | 4 字节/token | 需要额外加载 |
| Per-channel（每维一个 scale） | 最好 | 4*d_noPE 字节 | 开销大 |

Per-tile 是一个良好的平衡点：128 个值一组能捕捉局部值范围变化，开销仅 16/32 字节/token。

---

## 七、KV Cache 内存节省计算

以 DeepSeek-V3（61 层，h_kv=1，d=576）为例，不同精度下的 KV cache 内存占用（单 token）：

| 格式 | 每 token 字节数 | 32K 上下文 | 128K 上下文 | 相对 BF16 MQA 压缩比 |
|---|---|---|---|---|
| BF16 MHA (128 heads) | 2×128×576×2 = 294,912 B | ~9.0 GB | ~36.0 GB | 0.06×（基准） |
| BF16 MQA (1 head) | 2×1×576×2 = 2,304 B | ~72 MB | ~288 MB | 1×（基准） |
| FP8 V32 (656 B/token) | 656 B | ~20 MB | ~82 MB | **3.5×** |
| FP8 MODEL1 (576 B/token) | 576 B | ~18 MB | ~72 MB | **4.0×** |

注：以上为单层大小，61 层模型需乘以 61。

---

## 八、相关链接

- [/deepseek/flash-mla/concepts/mla-decoding](/ai/deepseek/flash-mla/concepts/mla-decoding) — MLA 解码算法原理
- [/deepseek/flash-mla/concepts/hopper-blackwell-kernels](/ai/deepseek/flash-mla/concepts/hopper-blackwell-kernels) — Hopper/Blackwell 内核设计
- [/deepseek/flash-mla/references/kv-cache-layout](/ai/deepseek/flash-mla/references/kv-cache-layout) — KV cache 内存布局详解
- [/deepseek/flash-mla/references/kernel-architecture](/ai/deepseek/flash-mla/references/kernel-architecture) — 内核架构详解（反量化实现）
- [/deepseek/deep-gemm/concepts/fp8-gemm](/ai/deepseek/deep-gemm/concepts/fp8-gemm) — DeepGEMM FP8 GEMM 量化方案
