---
type: bundle
okf_version: "0.2"
scope: opencode
name: opencode
version: "0.2.0"
description: "OpenCode OKF Wiki 增量覆盖 1.18.21 历史快照与 2.0.32 固定源码快照，涵盖包图、会话执行、工具扩展、API 契约和产品交付"
source_versions:
  - "1.18.21：2026-08-23 历史快照"
  - "2.0.32：commit 6ec56821d63100fe5bda45b759364f561c56b359"
generated:
  by: "reference_agent/trae-cn"
  at: 2026-10-20T12:01:30+08:00
---

# OpenCode Wiki

本 bundle 按源码快照增量组织 OpenCode 知识：原有 `concepts/00`～`04`、`examples/01` 与旧事实记录保留为 1.18.21 历史内容；新增 `concepts/05`～`09`、`examples/02` 及对应事实、洞察和源码地图以 2.0.32 固定 commit 为边界。跨版本阅读时应以各篇标注的来源为准，不将旧章节默认为新版本实现说明。

## 快速导航

### 概念

历史快照（1.18.21）：

- [OpenCode 简介](concepts/00-introduction.md)
- [架构概览](concepts/01-architecture.md)
- [配置系统](concepts/02-config-system.md)
- [会话与工具](concepts/03-session-tools.md)
- [部署与基础设施](concepts/04-deployment-infra.md)

固定源码快照（2.0.32）：

- [Monorepo 包地图](concepts/05-monorepo-package-map.md)
- [会话执行生命周期](concepts/06-session-execution-lifecycle.md)
- [模型、工具与扩展机制](concepts/07-model-tool-extensibility.md)
- [Protocol、Server、Client 与 SDK 边界](concepts/08-protocol-server-client-sdk.md)
- [产品入口与工程交付](concepts/09-product-surfaces-and-delivery.md)

### 示例

- [基本使用](examples/01-basic-usage.md)
- [Session Prompt 源码追踪](examples/02-session-prompt-trace.md)（2.0.32 源码导读，非可运行示例）

### 参考

- [源文件参考](references/source.md)
- [2.0.32 固定源码地图](references/source-code-map-2.0.32.md)

### 规范

- [事实清单（1.18.21 历史快照）](spec/facts.md)
- [架构洞察（1.18.21 历史快照）](spec/insights.md)
- [事实清单（2.0.32，F-081～F-114）](spec/facts-2.0.32.md)
- [架构洞察与学习地图（2.0.32）](spec/insights-2.0.32.md)

### 其他

- [变更日志](log.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/index
log
```
