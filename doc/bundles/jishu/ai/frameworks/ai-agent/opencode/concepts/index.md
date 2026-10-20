# 概念

## 历史快照（1.18.21）

- [00 - OpenCode 简介](00-introduction.md) — 项目定位与旧版技术栈概览
- [01 - 架构概览](01-architecture.md) — 包依赖方向、infra 模块、Effect 架构与 V2 API
- [02 - 配置系统](02-config-system.md) — V2 配置规范、.opencode 目录与配置审查组
- [03 - 会话与工具](03-session-tools.md) — SessionV2、Context Epoch、自动压缩、工具注册表与权限
- [04 - 部署与基础设施](04-deployment-infra.md) — SST 部署、Cloudflare/AWS 与数据湖

## 固定源码快照（2.0.32）

- [05 - Monorepo 包地图](05-monorepo-package-map.md) — workspace manifest 范围与源码覆盖等级
- [06 - 会话执行生命周期](06-session-execution-lifecycle.md) — prompt admission、wake、coordinator、runner 与事件投影
- [07 - 模型、工具与扩展机制](07-model-tool-extensibility.md) — Provider、工具 runtime、MCP、Permission 与 Plugin host
- [08 - Protocol、Server、Client 与 SDK 边界](08-protocol-server-client-sdk.md) — API 契约、handler 接线、客户端生成与 SDK 导出
- [09 - 产品入口与工程交付](09-product-surfaces-and-delivery.md) — CLI/TUI/App/Desktop 与测试、构建、发布边界

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-architecture
02-config-system
03-session-tools
04-deployment-infra
05-monorepo-package-map
06-session-execution-lifecycle
07-model-tool-extensibility
08-protocol-server-client-sdk
09-product-surfaces-and-delivery
```
