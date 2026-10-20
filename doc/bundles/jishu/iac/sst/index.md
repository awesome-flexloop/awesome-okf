---
type: bundle
okf_version: "0.2"
title: "SST 基础设施即代码框架源码与官方文档教程"
description: "以 SST v4.17.2 固定源码和 2026-10-20 官方文档为依据，学习应用模型、CLI 生命周期、组件/provider、runtime、资源链接与 Live/Mosaic 开发边界。"
bundle_name: "sst"
version: "1.0"
language: zh-CN
license: CC-BY-4.0
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T04:15:52Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T04:15:52Z" }
status: draft
stale_after: 2027-10-20
sources:
  - id: source
    resource: /references/source-v4.17.2.md
    title: SST v4.17.2 固定源码快照
  - id: docs
    resource: /references/official-docs-2026-10-20.md
    title: SST 官方文档（2026-10-20 采集）
---

# SST 基础设施即代码框架教程

本知识包通过固定提交源码和注明采集日期的官方文档，带读者从 SST 应用与配置模型逐步进入 CLI 生命周期、provider/组件、语言运行时、资源链接以及 Live/Mosaic 开发机制。源码实现结论限定于 SST `v4.17.2` / commit `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`；官网现行用法单独以 2026-10-20 采集的 W 编号标注。

## 学习路径

1. **建立产品模型**：[SST 应用模型与阅读边界](concepts/00-application-model.md) → [配置、stage 与 state](concepts/01-config-stage-state.md)。
2. **理解执行主线**：[CLI 到项目执行生命周期](concepts/02-cli-project-lifecycle.md) → [组件与 provider 边界](concepts/03-components-and-providers.md)。
3. **深入实现边界**：[运行时、RPC 与平台程序](concepts/04-runtime-server-architecture.md) → [资源链接与 SDK 数据边界](concepts/05-resource-linking.md) → [Live 与 Mosaic 开发机制](concepts/06-live-mosaic-development.md)。
4. **跟随示例**：先声明 [最小应用与组件](examples/01-minimal-component-app.md)，再看 [资源链接到 runtime](examples/02-link-resources-to-runtime.md)，最后梳理[本地开发到 stage 部署](examples/03-local-development-and-deployment.md)。

## 范围与验证边界

本教程覆盖代表性组件与主要架构机制，不穷举所有组件、provider 或 API。示例的配置/API 依据固定源码和注明日期的官网页面核验；本任务没有安装依赖、运行 `sst dev`/`sst deploy`，也没有创建或验证真实云资源。逐项来源、验证结果和未覆盖边界见[信源登记](references/index.md)、[变更日志](log.md)与[独立验证记录](verification.md)。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
examples/index
references/index
log
verification
```
