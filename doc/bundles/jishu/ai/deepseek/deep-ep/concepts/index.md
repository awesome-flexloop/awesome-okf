# DeepEP 核心概念

本目录包含 DeepEP 的核心概念文档，解释通信模型、架构设计和使用模式。

## 概念文档

| 概念 | 说明 |
|------|------|
| [架构概述](overview.md) | DeepEP 定位、两代缓冲区设计、通信拓扑抽象、在 DeepSeek 训练栈中的位置 |
| [Dispatch/Combine 流程](dispatch-combine.md) | Token 分发和聚合的数据流动模型、EPHandle 路由元数据、缓存/展开/确定性模式 |
| [MoE 专家并行](moe-parallelism.md) | EP 并行策略基础、top-k 路由、EP 与 TP/PP/DP 的组合、负载均衡 |
| [Elastic vs Legacy](elastic-vs-legacy.md) | V2 ElasticBuffer 与 V1 Buffer 的架构差异、API 对比、迁移指南 |
| [低延迟模式](low-latency-mode.md) | V1 IBGDA 低延迟推理路径、零拷贝优化、rank 屏蔽机制 |
| [JIT 编译系统](jit-compilation.md) | 运行时 CUDA 内核编译原理、CRTP 启动器框架、内核缓存机制 |

```{toctree}
:hidden:
:maxdepth: 7

dispatch-combine
elastic-vs-legacy
jit-compilation
low-latency-mode
moe-parallelism
overview
```
