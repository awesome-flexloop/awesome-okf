# TileKernels 示例

本章节提供 TileKernels 各功能模块的使用示例。

## 示例列表

| 示例 | 说明 |
|---|---|
| [basic-quant](/ai/deepseek/tile-kernels/examples/basic-quant) | FP8/FP4/E5M6 量化基础用法，per-token/per-block/per-channel 量化、反量化、SwiGLU融合量化、精度对比 |
| [moe-forward](/ai/deepseek/tile-kernels/examples/moe-forward) | MoE 前向计算流水线，top2-sum gate、fused mapping、expand/reduce、辅助算子 |
| [mhc-usage](/ai/deepseek/tile-kernels/examples/mhc-usage) | MHC Multi-Head Compute 使用，mhc_pre/mhc_post 训练/推理流程、LM Head、原子Op、多层重计算 |

```{toctree}
:hidden:
:maxdepth: 7

basic-quant
mhc-usage
moe-forward
```
