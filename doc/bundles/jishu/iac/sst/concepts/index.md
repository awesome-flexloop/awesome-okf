# Concepts

本组概念文档按“产品模型 → 配置与生命周期 → 组件和执行架构 → 资源链接与开发体验”的顺序组织。

| 文档 | 内容 |
|---|---|
| [SST 应用模型与阅读边界](00-application-model.md) | SST 的应用模型、教程范围与来源边界 |
| [配置、stage 与 state](01-config-stage-state.md) | 配置发现、stage 和 state 的源码与官网说明 |
| [CLI 到项目执行生命周期](02-cli-project-lifecycle.md) | CLI、项目模型与 Pulumi 命令映射 |
| [组件与 provider 边界](03-components-and-providers.md) | 代表性组件、provider 与扩展面 |
| [运行时、RPC 与平台程序](04-runtime-server-architecture.md) | Go CLI、JSON-RPC、runtime 和平台入口 |
| [资源链接与 SDK 数据边界](05-resource-linking.md) | Linkable 数据到 JavaScript SDK Resource 的路径 |
| [Live 与 Mosaic 开发机制](06-live-mosaic-development.md) | 本地开发实现与官网 Live 说明的版本边界 |

```{toctree}
:hidden:
:maxdepth: 2

00-application-model
01-config-stage-state
02-cli-project-lifecycle
03-components-and-providers
04-runtime-server-architecture
05-resource-linking
06-live-mosaic-development
```
