# DeepGEMM 示例

本章节提供 DeepGEMM 各功能的使用示例。

## 示例列表

| 示例 | 说明 |
|---|---|
| [basic-gemm](/ai/deepseek/deep-gemm/examples/basic-gemm) | 基础 FP8/BF16 GEMM 用法，包括数据量化、核函数调用、性能测试 |
| [moe-forward](/ai/deepseek/deep-gemm/examples/moe-forward) | MoE 前向计算示例，包括 M-grouped GEMM 方案和 MegaMoE 融合核（SM100） |
| [tuning](/ai/deepseek/deep-gemm/examples/tuning) | 性能调优指南，包括 SM/TC 配置、JIT 预热、性能测量、问题排查 |

```{toctree}
:hidden:
:maxdepth: 7

basic-gemm
moe-forward
tuning
```
