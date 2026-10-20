---
type: Reference
title: "OpenCode 2.0.32 固定源码地图"
description: "登记本轮源码基线、workspace 包范围、重点调用路径和事实编号映射"
tags: [opencode, source-map, monorepo, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T11:57:39+08:00 }
verified: { by: "process:source-snapshot-preflight", at: 2026-10-20T11:57:39+08:00 }
status: stable
stale_after: 2027-04-20
sources:
  - id: opencode-source-2.0.32
    resource: https://github.com/anomalyco/opencode/tree/6ec56821d63100fe5bda45b759364f561c56b359
    title: "anomalyco/opencode 固定 commit 6ec56821"
---

# OpenCode 2.0.32 固定源码地图

## 信源坐标

| 项目 | 值 |
|---|---|
| 上游仓库 | [`anomalyco/opencode`](https://github.com/anomalyco/opencode) |
| 固定 commit | [`6ec56821d63100fe5bda45b759364f561c56b359`](https://github.com/anomalyco/opencode/tree/6ec56821d63100fe5bda45b759364f561c56b359) |
| 根 manifest 版本 | `2.0.32` |
| 工作区 manifest 统计 | 五个根 workspace glob，共 39 个匹配 manifest；按 glob 数为 29、1、4、2、3 |
| 本地 checkout | 仅作为本轮读取位置；本参考及教程不依赖本机绝对路径 |

固定 commit 是本轮所有源码结论的唯一版本坐标。版本号用于读者识别，若版本标签与 commit 有冲突，以 commit 内容为准。

## Workspace 范围

根 `package.json` 声明的 workspace glob 为 `packages/*`、`packages/plugins/*`、`services/*`、`packages/console/*`、`packages/stats/*`。本轮以固定 checkout 中符合 glob 的 manifest 作为 package 清点对象；39 个 manifest 的逐包角色线索、覆盖等级和限制见[版本化事实与覆盖矩阵](/spec/facts-2.0.32.md)。

| 覆盖等级 | 数量 | 使用方式 |
|---|---:|---|
| 深读 | 6 | 阅读关键实现并追踪接口或调用路径，不代表通读该包全部源码。 |
| 入口/接口读取 | 4 | 检查入口、导出或接线文件；不据此推导内部实现。 |
| 清单级 | 29 | 依据 manifest、依赖与脚本登记包图位置；实现行为需另行查源。 |

`github/package.json` 与 `sdks/vscode/package.json` 不匹配上述 workspace glob，因此不计入 39 个 workspace manifest。本轮只登记边界，不将其纳入深读范围。

## 重点源码路径

下表中的文件链接均固定到上述 commit；“事实”列指向 bundle 内与本轮版本一一对应的事实记录。

| 子系统 | 固定源码入口 | 可核验范围 | 事实 |
|---|---|---|---|
| Workspace 与构建 | [`package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/package.json)、[`turbo.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/turbo.json) | 版本、workspace glob、Turbo task 边界 | F-081～F-085 |
| Agent、Provider、权限和扩展 | [`agent.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/agent.ts)、[`provider.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/provider.ts)、[`permission.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/permission.ts)、[`host.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin/host.ts) | 服务接口、Provider 包加载、Permission 规则匹配、Plugin host 与存储 namespace | F-086～F-092 |
| 会话协调与执行 | [`run-coordinator.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/run-coordinator.ts)、[`execution.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/execution.ts)、[`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/session.ts)、[`llm.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/runner/llm.ts)、[`step.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/runner/step.ts) | session key 协调、execution 状态、prompt admission/wake、LLM step 与本地工具 fiber | F-093～F-097、F-114 |
| 持久化与事件 | [`sql.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/sql.ts)、[`projector.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/projector.ts)、[`migration.gen.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/database/migration.gen.ts) | Session 表、事件投影与迁移清单计数 | F-098～F-100 |
| API 契约与服务接线 | [`api.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/api.ts)、[`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/groups/session.ts)、[`routes.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/src/routes.ts)、[`session handler`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/src/handlers/session.ts) | API group/middleware、session endpoint、Server route 与 handler 到 Core prompt | F-101～F-103、F-114 |
| Client 与 SDK | [`client.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/client.ts)、[`build.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/client/script/build.ts)、[`sdk index`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/sdk/src/index.ts) | Protocol 导出、Client contract 生成、SDK namespace 与依赖 | F-104～F-105 |
| 用户入口与工程生命周期 | [`CLI entry`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/cli/src/index.ts)、[`TUI entry`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/index.tsx)、[`App entry`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/src/entry.tsx)、[`Desktop RPC`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/shared/ipc-rpc.ts)、[`test workflow`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/test.yml)、[`publish workflow`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml) | CLI/TUI/App/Desktop 的代表性入口、测试构建阶段及 CLI/Node/Desktop 发布流程 | F-106～F-109、F-112～F-113 |

## 阅读边界

- 以上清单是分层采样地图，不是对仓库每个文件的穷尽审计。
- 事实表中的数量按其各自定义的对象与统计口径解释；不同表达式得到的 API endpoint 匹配数不作为总量结论。
- 新增教程对实现的解释必须能回到本参考固定链接或 `spec/facts-2.0.32.md`；覆盖矩阵标为清单级的包不得被描述为已完成实现深读。
