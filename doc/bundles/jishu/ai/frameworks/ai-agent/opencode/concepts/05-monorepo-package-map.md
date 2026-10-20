---
type: Concept
title: "OpenCode 2.0.32 Monorepo 包地图"
description: "从固定快照的 workspace manifest 建立 OpenCode 包边界，并区分清单覆盖与实现深读"
tags: [opencode, monorepo, workspace, architecture, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T12:01:30+08:00 }
verified: { by: "process:seven-concepts-e", at: 2026-10-20T12:01:30+08:00 }
status: draft
stale_after: 2027-04-20
sources:
  - id: opencode-source-map-2.0.32
    resource: /references/source-code-map-2.0.32.md
    title: OpenCode 2.0.32 固定源码地图
---

# OpenCode 2.0.32 Monorepo 包地图

本篇建立 OpenCode 2.0.32 的 workspace 包地图，帮助读者先辨认源码边界，再选择需要深入的执行路径。这里的“包”按根 `package.json` 声明的 workspace glob 匹配 `package.json` 文件统计；它不等同于用户界面数量、独立进程数量或已深读的实现数量。

事实和版本以固定 commit `6ec56821d63100fe5bda45b759364f561c56b359` 为准。本轮保留旧版 `1.18.21` 的 `concepts/00`～`04`，本篇只补充新快照中的包图，不把旧章节内容自动视为 2.0.32 的实现描述。（F-081～F-084、F-110）

## Workspace 的边界

根 manifest 声明五个 glob：`packages/*`、`packages/plugins/*`、`services/*`、`packages/console/*`、`packages/stats/*`。按这些 glob 枚举到 39 个 manifest，分组计数为 29、1、4、2、3。逐包路径、manifest 包名和覆盖范围见[事实清单中的 workspace 覆盖矩阵](/spec/facts-2.0.32.md)。（F-082、F-083、F-110）

地图可先按职责粗分：

| 边界 | 代表包 | 本轮可确认的角色 |
|---|---|---|
| Agent 核心与模型运行 | `@opencode/core`、`@opencode/ai` | 会话、Agent、Provider、工具等实现与 LLM 流抽象 |
| 契约与服务接口 | `@opencode/protocol`、`@opencode/server`、`@opencode/client`、`@opencode/sdk` | API 定义、Server 接线、生成客户端契约与 SDK 导出 |
| 用户交互入口 | `@opencode/cli`、`@opencode/tui`、`@opencode/app`、`@opencode/desktop` | CLI 命令分发、终端 UI、应用渲染及桌面 IPC 类型边界 |
| 周边产品与服务 | `@opencode/console-app`、`@opencode/stats-app`、`@opencode/www` 等 | 独立应用、统计与网站相关 workspace；本轮多为清单级覆盖 |

表中“代表包”不是穷尽清单。39 个 manifest 的精确名称与各包的角色线索以矩阵为准；manifest 中的描述、依赖和脚本只提供导航线索，不能替代实现证据。

## 阅读覆盖不是包清点

本轮矩阵把 6 个包标为深读、4 个标为入口/接口读取、29 个标为清单级。深读表示围绕关键路径检查了多个源码位置，不表示通读整个包；入口/接口读取仅支持对入口或导出边界的有限描述；清单级不支持据此推断实现行为。（F-110）

这个分层直接决定后续教程可以说到哪里：

- 对深读包，可沿已登记源码路径讲解本轮检查过的调用关系，但不可把抽样写成全量审计。
- 对入口/接口读取包，可说明实际可见的导出或接线，不延伸到未读的内部实现。
- 对清单级包，只将其放在包图中作为定位线索；若要说明其运行行为，需另行查阅并记录源码事实。

特别地，`github/package.json` 与 `sdks/vscode/package.json` 不匹配上述五个根 workspace glob。因此它们属于仓库里的其他边界，不计入 39 个匹配项。（F-084）

## 从包图进入执行路径

学习会话主链时，可从 `@opencode/server` 的 session handler 追到 `@opencode/core` 的 Session service，再观察 runner 如何调用 `@opencode/ai`。客户端契约则从 `@opencode/protocol` 的 `ClientApi` 出发，接到 `@opencode/client` 的生成构建，再看 `@opencode/sdk` 的导出。这些是本轮有多点源码证据的路径，不意味着包之间所有依赖方向均已穷尽。（F-093～F-105、F-114）

构建与测试也有自己的边界：根 `turbo.json` 声明 `typecheck`、`build`、`test` 任务，而根 `package.json` 的 `test` 脚本明确提示不要直接从根运行测试。具体验证范围应进一步对照测试 workflow，不能从包图或一个 job 推断整个产品已通过验证。（F-085、F-112）

## 适用范围

本篇是固定快照的导航图，不是所有包的实现手册，也不描述浮动分支的当前状态。需要复核时，先从[源码地图](/references/source-code-map-2.0.32.md)选择 commit 固定的入口，再回到[版本化事实](/spec/facts-2.0.32.md)查看该结论的证据与覆盖等级。

## 相关概念

- [会话执行生命周期](/concepts/06-session-execution-lifecycle.md)
- [Protocol、Server、Client 与 SDK 边界](/concepts/08-protocol-server-client-sdk.md)
- [产品入口与工程交付](/concepts/09-product-surfaces-and-delivery.md)
