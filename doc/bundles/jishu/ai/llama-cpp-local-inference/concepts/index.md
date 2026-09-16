# concepts/ 概念文档

本知识包的概念层按“事实 → 机制 → 决策”三层组织（源自微信博文经 R→I→E→V 转化，操作可复现性两问未全中，故无 examples/）。

| 层次 | 文档 | 说明 |
|------|------|------|
| 事实层 | [00 项目身份与信源边界](00-project-and-source-boundaries.md) | 仓库身份、热度时点、四种安装形态、“零依赖”口径、观点/事实分层 |
| 机制层 | [01 量化、硬件与本地服务](01-quantization-hardware-server.md) | GGUF/Q4 内存量级、4GB/7B 勘误、后端矩阵、llama-server、树莓派边界 |
| 决策层 | [02 本地 API 采用与云端取舍](02-local-api-adoption.md) | OpenAI 兼容迁移六项核对、三维取舍、采用步骤与六条反模式 |

```{toctree}
:hidden:
:maxdepth: 2

00-project-and-source-boundaries
01-quantization-hardware-server
02-local-api-adoption
```
