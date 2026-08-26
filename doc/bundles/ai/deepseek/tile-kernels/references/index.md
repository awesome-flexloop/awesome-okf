# TileKernels API 参考

本章节提供 TileKernels 的完整 API 参考文档。

## 参考文档列表

| 文档 | 说明 |
|---|---|
| [api](/ai/deepseek/tile-kernels/references/api) | 公共 API 完整参考，包括配置管理、量化、MoE、MHC、Engram、转置、数据类 |
| [quant-kernels](/ai/deepseek/tile-kernels/references/quant-kernels) | 量化核函数详细参考，FP8/FP4/E5M6 cast、SwiGLU融合、反量化、缩放因子布局 |
| [moe-kernels](/ai/deepseek/tile-kernels/references/moe-kernels) | MoE 核函数详细参考，topk gate、fused mapping、expand/reduce、辅助算子 |
| [mhc-kernels](/ai/deepseek/tile-kernels/references/mhc-kernels) | MHC 与 Engram 核函数详细参考，Multi-Head Compute、Engram门控、转置、配置工具 |

```{toctree}
:maxdepth: 7

api
mhc-kernels
moe-kernels
quant-kernels
```
