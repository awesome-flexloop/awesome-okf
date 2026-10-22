# DeepInfer 核心概念

本章节深入讲解 DeepInfer 推理框架的核心概念与设计原理。

## 概念文档列表

| 文档 | 说明 |
|---|---|
| overview | DeepInfer 整体定位、支持矩阵、目录结构、构建与快速开始 |
| architecture | LLMEngine 引擎架构、C++ 调度器、ZOS 零开销异步调度流水线 |
| parallelism | EP/DP/CP/EPLB 并行策略、deep_cluster 硬件探测层、Wide-EP 部署 |
| speculative-decoding | DSpark 推测解码：DFlash 草稿模型、ConfidenceHead、变长验证 |
| structured-output | 结构化输出：xgrammar 编译/匹配、token bitmask、编译推理解耦 |
| deployment-practice | 大规模部署实践：四层负载均衡、KVCache 存储、自动扩缩容 |

```{toctree}
:hidden:
:maxdepth: 7

architecture
deployment-practice
overview
parallelism
speculative-decoding
structured-output
```
