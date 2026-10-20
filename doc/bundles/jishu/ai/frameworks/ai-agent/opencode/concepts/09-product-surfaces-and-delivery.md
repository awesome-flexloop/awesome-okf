---
type: Concept
title: "OpenCode 2.0.32 产品入口与工程交付"
description: "辨认 CLI、TUI、App、Desktop 入口，并按固定 workflow 区分测试、构建与发布证据"
tags: [opencode, cli, tui, desktop, ci, release, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T12:01:30+08:00 }
verified: { by: "process:seven-concepts-e", at: 2026-10-20T12:01:30+08:00 }
status: draft
stale_after: 2027-04-20
sources:
  - id: opencode-source-map-2.0.32
    resource: /references/source-code-map-2.0.32.md
    title: OpenCode 2.0.32 固定源码地图
---

# OpenCode 2.0.32 产品入口与工程交付

OpenCode 并非单一 UI 入口。固定快照中可以分别定位 CLI 命令分发、TUI 导出、Web App 渲染入口和 Desktop renderer/IPC 类型；工程验证与发布又由不同 workflow 管理。理解这些边界有助于把“用户从哪里进入”“改动在哪些 job 验证”“哪些产物参与发布”拆开回答。（F-085、F-106～F-109、F-112～F-113）

本篇只描述源码中已检查的入口和 workflow 片段，不代表所有平台打包配置、部署环境或 CI 实际运行结果都已审计。

## 四类交互入口

| 入口 | 固定快照中可见的边界 |
|---|---|
| CLI | 入口将 `Commands` 与 `Runtime.handlers` 组合；默认命令处理器和 upgrade 等处理器通过动态 `import()` 加载。（F-106） |
| TUI | `packages/tui/src/index.tsx` 从 `./app` 导出 `run` 与 `TuiInput` 类型。（F-107） |
| App | `packages/app/src/entry.tsx` 通过 Solid `render` 渲染 `AppInterface`。（F-108） |
| Desktop | renderer 入口渲染 `DesktopApp`；共享 IPC 文件把 App、Storage、File、Window、Menu、Event 与 Extension RPC 类型合并为 `DesktopRpcs`。（F-108、F-109） |

这些是不同的入口或接线点，不能仅从 `packages/*` 的数量推导出用户可见产品数量，也不能因为共享某些类型就断言各运行形态具有完全相同的交互行为。

## 测试与构建证据

根 `turbo.json` 声明 `typecheck`、`build` 与 `test` 任务；根 `package.json` 的 `test` 脚本明确退出失败并提示不要从根运行测试。因此“根目录执行 test 成功”不是本快照支持的结论，实际验证应按项目 workflow 与目标包选择。（F-085）

`.github/workflows/test.yml` 可见的阶段包括 affected-package 检查、Linux/Windows unit job、build job，以及受 affected app 输出控制的浏览器测试 job。Linux unit 步骤还检查生成的 client 与 www 文档。（F-112）

这些阶段各自提供不同类型的证据。某个 unit job 通过，不等于浏览器测试、生成文件检查和 build job 都通过；workflow 定义存在，也不等于某次 CI 执行已经成功。

## 发布链路

`.github/workflows/publish.yml` 中，`version` job 产出版号、release 和 tag 输出；后续 job 构建 CLI、Node CLI 与 Electron 桌面包；`publish` job 汇集相关 job 结果并运行 `script/publish.ts`。（F-113）

这说明发布是由多个构建和协调阶段组成的工程链，而不是单个根包构建命令。要判断具体版本是否已发布，仍需查对应 workflow run 与发布结果；本篇只登记该固定 commit 中的 workflow 结构。

## 读者如何使用这张边界图

排查一个用户入口问题时，先定位对应运行形态，再沿其入口追到 Core 或 API；验证构建问题时，对照 affected-package 与目标 job，而不是仅凭包名判断；核对发布问题时，区分版本生成、各产物构建和汇总发布阶段。这是一套基于已登记边界的定位顺序，并不替代项目针对具体变更的测试策略。

本轮对 UI、Desktop 主进程、平台适配和 workflow 的覆盖是代表性读取，不是完整发布审计。包覆盖等级及遗漏范围见[事实清单矩阵](/spec/facts-2.0.32.md)，固定文件入口见[源码地图](/references/source-code-map-2.0.32.md)。

## 相关概念

- [OpenCode Monorepo 包地图](/concepts/05-monorepo-package-map.md)
- [Protocol、Server、Client 与 SDK 边界](/concepts/08-protocol-server-client-sdk.md)
- [OpenCode 2.0.32 会话执行生命周期](/concepts/06-session-execution-lifecycle.md)
