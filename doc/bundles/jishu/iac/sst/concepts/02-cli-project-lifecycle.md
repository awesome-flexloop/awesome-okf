---
type: Concept
title: "CLI 到项目执行生命周期"
description: "沿 SST v4.17.2 的配置构建、StackInput 与 Pulumi 命令映射追踪 CLI 主线，并与官网命令用法分层阅读。"
tags: [SST, CLI, Pulumi, deployment, lifecycle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00Z" }
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

# CLI 到项目执行生命周期

SST CLI 命令与项目执行不是同一个层次：命令入口收集用户选项，项目层构建配置并准备 stack 输入，随后把命令映射到 Pulumi Automation 的执行选项。以下路径来自 v4.17.2 固定源码；官网 CLI 页的用户命令示例另以 W 编号标记。

## 执行主线

可将已核验路径概括为：

1. **发现项目**：`project.Discover()` 向上查找 `sst.config.ts` 并创建 `.sst` 工作目录（F-003，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L115-L130)）。
2. **构造项目**：`project.New()` 检查 stage、设置目录，并创建 runtime collection、构建配置入口（F-005–F-007，[目录与校验](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L160-L244)）。
3. **整理执行输入**：`StackInput` 含 `Command`、`Target`、`Exclude`、`ServerPort`、`Dev`、`Verbose`、`Continue`、`SkipHash` 与 `PolicyPath` 等字段（F-008，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/stack.go#L18-L30)）。
4. **进入项目执行**：`Project.Run()` 构建并运行 SST 平台程序；相关实现调用 `js.Build`（F-009，[源码入口](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/run.go#L35-L55)、[构建路径](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/run.go#L150-L190)）。
5. **映射执行命令**：在 `Project.Run()` 中，`diff` 映射为 Pulumi `preview`，`refresh` 映射为 `refresh --yes --run-program`，`deploy` 映射为 `up --yes -f`，`remove` 映射为 `destroy --yes -f`（F-010，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/run.go#L329-L337)）。

例如，deploy 命令入口将 `Command: "deploy"` 及 target、exclude、dev、server port、verbose、continue、policy 等选项装入 `StackInput`，再调用项目运行路径（F-011，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/deploy.go#L175-L199)）。

## 官网命令与源码映射

官网 CLI reference 列出 `sst deploy --stage <name>`、`sst diff`、`sst remove --stage <name>` 等用法，并说明 deploy 可选择 target 或排除 component（W-011，[CLI reference](https://sst.dev/docs/reference/cli/)）。这些命令帮助读者理解产品操作面；固定快照能进一步证明上述四种内部 command 到 Pulumi 参数的映射，但不能据此推断所有 CLI flags 的完整兼容性。

对于新读者，可先按官网文档运行 `sst dev` 理解产品流程，再回到源码检查 project 与 Pulumi 的边界。官网称 `sst dev` 默认启动 multiplexer，协调部署、本地函数与前端进程，并列出 `multi`（默认）、`basic`、`mono` 模式（W-010，[CLI dev 章节](https://sst.dev/docs/reference/cli/#dev)）；本教程不把这一描述扩展为源码中未核验的全部 dev 行为。

## 重要边界

- 源码中的 `Project.Run()` 命令映射是固定提交事实，不等价于本教程执行了 Pulumi 或创建了云资源。
- stack 输入中存在 `Dev` 等字段（F-008），只表示字段存在；字段具体影响需由对应调用点证明。
- 官网文档随时间更新；产品命令用法与 v4.17.2 的 CLI 实现应分别引用。

## 相关概念

- [配置、stage 与 state](/concepts/01-config-stage-state.md)
- [运行时、RPC 与平台程序](/concepts/04-runtime-server-architecture.md)
- [Live 与 Mosaic 开发机制](/concepts/06-live-mosaic-development.md)
- [本地开发到部署示例](/examples/03-local-development-and-deployment.md)
