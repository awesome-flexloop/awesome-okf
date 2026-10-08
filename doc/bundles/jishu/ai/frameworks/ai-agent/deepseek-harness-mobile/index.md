---
okf_version: "0.2"
type: bundle
title: DSH Mobile — 用 Kuikly 把 DeepSeek Harness 装进口袋
description: 腾讯程序员 yuki 一手实测——用 Kotlin Multiplatform/Kuikly 开发 DeepSeek Harness 手机客户端（Android/iOS/鸿蒙一码三端），直连 Host 协议（RPC+双 WebSocket）、SSH/扫码 Relay 双通道、断线重连状态机；含本地扫码连接与扩展开发上手
tags: [DeepSeek Harness, DSH, DSH Mobile, Kuikly, Kotlin Multiplatform, 跨端开发, 移动Agent, Remote Control, 断线重连]
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-09-09T00:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
    title: 博文信源事实清单（F-001~F-045）
  - id: tencent-tech-article
    resource: https://mp.weixin.qq.com/s/THtcdws01AV_Q3fe2pYRlQ
    title: 腾讯技术工程：我用腾讯 Kuikly，把 DeepSeek Harness 装进了口袋（2026-09-08）
  - id: dsh-official
    resource: https://deepseek.com/harness/en/
    title: DeepSeek Harness 官网
  - id: dsh-mobile-repo
    resource: https://github.com/yukiykchen/deepseek-harness-mobile
    title: yukiykchen/deepseek-harness-mobile（作者开源仓库）
  - id: kuikly-repo
    resource: https://github.com/Tencent-TDS/KuiklyUI
    title: KuiklyUI 官方仓库
related:
  - "[[deepseek-harness]]"
---

# DSH Mobile — 用 Kuikly 把 DeepSeek Harness 装进口袋

> **技术实测/资讯型教程（非源码逐行教程）**：本 bundle 源自腾讯程序员 yuki 在「腾讯技术工程」公众号的一手实测博文（2026-09-08），介绍如何用腾讯开源跨端框架 **Kuikly** 开发 **DSH Mobile**——一个覆盖 Android/iOS/鸿蒙、直连电脑上 **DeepSeek Harness（DSH）** 的手机客户端。全部命令/仓库/组件版本均经作者实测与权威源核验。

> ⚠️ **版本敏感提示**：DSH 处于 developer preview，协议与包结构可能破坏性变化。文中 RPC 方法数（52）、端点与组件版本对应 **dsh-v0.1.1-rc.2**（博文时点），核验时官方最新已至 `dsh-v0.1.3-alpha.1`；实际开发请锁定已验证 tag。KuiklyWebview 版本博文为 `1.0.1-2.0.21`，核验时仓库 README 为 `1.0.2-2.0.21`（verification A3 勘误）。

## 核心看点

- **设计动机**：DSH 任务长、运行中需人审批/提问；手机用来接住"短而频繁的交互"，而非把 IDE 搬上手机（[00](concepts/00-dsh-mobile-overview.md)）
- **跨端方案**：一套 Kotlin（commonMain 约 1.3 万行）三端共享；KuiklyMarkdown/KuiklyWebview 组件复用 + 原生差异下沉（[01](concepts/01-kuikly-cross-platform.md)）
- **协议直连**：不加中间层，直接复用 DSH 官方 Host 协议——HTTP RPC（`POST /api/session.prompt`）+ 两条只下行 WebSocket（events.mux/events.host）（[02](concepts/02-dsh-host-protocol.md)）
- **连接与可靠**：SSH 隧道或扫码 Relay（sealed-tunnel-v1），DSH 始终只听本机 3080；断线先补事件再对历史，世代号防旧连接污染（[03](concepts/03-connection-and-reconnect.md)）
- **行业趋势**：Cursor/Claude Code Remote Control 同向演进，手机正在成为 Agent 决策节点入口（[04](concepts/04-mobile-agent-control-patterns.md)）

## 主题关联

- [deepseek-harness](../deepseek-harness/index.md) — DeepSeek Harness 源码级教程（Cordis 插件架构/ACP/MCP/ReactLoopAgent），本 bundle 是其移动端接入视角的姊妹篇，可对照学习

## 知识导航

- **概念**：[concepts/index](concepts/index.md)（5 篇：定位/跨端/协议/连接重连/行业趋势）
- **示例**：[examples/index](examples/index.md)（2 篇：扫码连接上手 + 扩展开发入口）
- **信源与核验**：[references/index](references/index.md)（F-001~F-045 事实清单 + 11✅/2⚠️/0❌ P0 核验报告）

## 已知边界

- **单源声明**：RPC "52 个方法"与 rpc-map.ts 路径仅博文单源（verification B3）；引用以官方仓库为准
- **厂商宣传口径**：Kuikly "日活超 5 亿"为腾讯官方口径，无法独立验证（verification A2）
- **时点信息**：博文 2026-09-08 发布；组件/版本/端点信息以 stale_after（2026-12-31）为复核时限
- **未覆盖**：DeepSeek Harness 源码级实现细节请见同簇 [deepseek-harness](../deepseek-harness/index.md)

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
