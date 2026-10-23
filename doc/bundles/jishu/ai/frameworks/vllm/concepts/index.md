# concepts/ 概念文档

本知识包的概念层按「入门 → 核心模块 → 场景与选型 → 进阶」四段组织（源自 vLLM v0.32 源码 + 官网/文档站，R→I→E→V 转化，操作可复现性两问均中，故设 examples/）。

| 层次 | 文档 | 说明 |
|------|------|------|
| 入门 | [00 整体架构与项目身份](00-overview.md) | 身份卡片、两大入口、版本谱系、生态位与适用边界 |
| 入门 | [01 快速开始](01-quickstart.md) | 安装 → 离线推理 → `vllm serve` 最小闭环与首token验证 |
| 入门 | [02 安装与硬件平台](02-installation.md) | 平台矩阵、四种安装方式、硬件插件生态 |
| 核心 | [03 架构总览](03-architecture.md) | V1 进程架构、类层次设计、请求生命周期 |
| 核心 | [04 调度与批处理](04-scheduling.md) | continuous batching、chunked prefill、调度策略与令牌预算 |
| 核心 | [05 KV 缓存与 PagedAttention](05-kv-cache.md) | block 池、前缀缓存、KV 量化与卸载 |
| 核心 | [06 执行层：Executor 与模型运行](06-execution.md) | Worker、ModelRunner、CUDA Graph、torch.compile |
| 核心 | [07 配置体系](07-configuration.md) | EngineArgs → VllmConfig、常用参数分组速查 |
| 场景 | [08 在线服务与 API](08-online-serving.md) | OpenAI 兼容 API 全谱、chat 模板、鉴权、多模态与工具调用 |
| 场景 | [09 模型支持](09-model-support.md) | 架构注册表、Transformers backend、任务类型与自定义模型 |
| 场景 | [10 量化](10-quantization.md) | 量化方法矩阵、硬件兼容、外挂量化插件 |
| 场景 | [11 投机解码](11-speculative-decoding.md) | 方法谱系、`--speculative-config` 与选型表 |
| 进阶 | [12 分布式推理与扩展](12-distributed.md) | TP/PP/DP/EP/CP、执行器选型与多节点部署 |
| 进阶 | [13 进阶主题](13-advanced.md) | PD 分离、结构化输出、LoRA、RL 接口、插件系统、可观测性 |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-quickstart
02-installation
03-architecture
04-scheduling
05-kv-cache
06-execution
07-configuration
08-online-serving
09-model-support
10-quantization
11-speculative-decoding
12-distributed
13-advanced
```
