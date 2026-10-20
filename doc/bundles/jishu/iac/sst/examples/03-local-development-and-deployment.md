---
type: Example
title: "从本地开发到 stage 部署"
description: "串起 SST 的本地开发、差异查看与指定 stage 部署命令，并明确其云端依赖和本教程的执行边界。"
tags: [SST, example, CLI, dev, deployment, stage]
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

# 从本地开发到 stage 部署

本例以 [最小应用与组件](/examples/01-minimal-component-app.md) 中的 `sst.config.ts` 为起点，串起本地开发、差异查看和指定 stage 部署。命令来自 2026-10-20 查阅的 SST 官方 CLI 文档（W-010、W-011）；固定源码则能证明 v4.17.2 中 `dev` 命令入口存在，以及 `Project.Run()` 对 `diff`、`deploy` 等命令的内部映射（F-002、F-010、F-011）。

这些命令可能与云 provider 交互。所谓“本地开发”描述的是开发工作流入口，不等于完全离线、不会触及云端资源的模拟器。

## 准备项目

在项目根目录准备 SST 配置，并按项目方式安装对应版本：

```bash
npm install sst@4.17.2
```

还需要配置目标 provider 的凭证和访问权限。安装命令是本教程给读者的版本固定建议；本任务没有执行安装，也没有验证任何账号或凭证。

## 启动本地开发

在项目根目录运行：

```bash
npx sst dev
```

官网 CLI 文档称 `sst dev` 默认启动 multiplexer，协调应用部署、本地函数和前端进程，并加载 linked resources、监视配置变化（W-010）。固定版本 CLI 源码也将 `dev` 声明为 CLI 命令，其描述涉及 multiplexer、frontend/process、linked resources 与 watcher（F-002）。

开发期间可按项目需要修改配置或应用代码，并观察 SST 提供的开发反馈。若配置声明云组件，首次启动或后续变更可能要求访问 provider、部署或更新云端资源；请先核对账号、stage、权限、费用和清理策略。

## 查看差异并部署

在决定部署目标前，可以先查看变更，再将配置发布到指定 stage：

```bash
npx sst diff
npx sst deploy --stage production
```

官方 CLI reference 列出 `sst diff` 和 `sst deploy --stage <name>` 用法（W-011）。固定提交中，CLI deploy 入口将 `Command: "deploy"` 和若干选项放入 `StackInput`（F-011）；项目执行路径将 `deploy` 映射为 Pulumi `up --yes -f`，将 `diff` 映射为 `preview`（F-010）。这是源码中的命令映射，不代表本教程已经运行 Pulumi。

部署前应确认 `production` 是预期目标，并审阅配置中的资源保留/移除策略。不要把 `diff` 的预览结果当成部署成功，也不要在未确认环境与费用前执行 deploy。

## 本教程的验证边界

- 示例命令与配置写法以已登记的官方页面和固定源码位置为依据；命令没有在本任务环境执行。
- 本任务未运行 `npm install`、`sst dev`、`sst diff` 或 `sst deploy`，未配置云凭证、创建/更新云资源，也未核验部署结果。
- 真实执行需由读者在自己的项目、账号和预算边界内完成。SST 官网说明可能随时间变化，本文所引 W 编号仅代表 2026-10-20 的页面内容。

## 相关概念

- [配置、stage 与 state](/concepts/01-config-stage-state.md)
- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
- [Live 与 Mosaic 开发机制](/concepts/06-live-mosaic-development.md)
- [最小应用与组件](/examples/01-minimal-component-app.md)
