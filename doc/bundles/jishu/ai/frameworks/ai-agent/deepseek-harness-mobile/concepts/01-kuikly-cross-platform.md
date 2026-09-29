---
type: Concept
title: Kuikly 跨端框架与原生桥接
description: 为什么选 Kuikly——基于 Kotlin Multiplatform 的六平台框架、组件市场复用（KuiklyMarkdown/KuiklyWebview）、差异下沉到原生层、KuiklyUI-AI 开发配套
tags: [Kuikly, Kotlin Multiplatform, 跨端开发, 组件市场, 原生桥接, KuiklyMarkdown, KuiklyWebview, KuiklyUI-AI]
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
    title: 博文信源事实清单（F-001~F-045）
---

# Kuikly 跨端框架与原生桥接

> **事实基础**：本文所有具体声明带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，P0 核验报告见 [references/verification.md](../references/verification.md)。

## 1. Kuikly 是什么

Kuikly 是腾讯开源的高性能跨端框架，基于 **Kotlin Multiplatform（KMP）**，覆盖 Android、iOS、HarmonyOS、H5、微信小程序、Mac 六大平台（F-006）。腾讯官方口径称其"支撑业务日活用户超 5 亿"——该数字为**腾讯官方宣传口径**，无法独立验证（见 [verification.md](../references/verification.md) A2 项）。

> 平台口径注意：官方对 H5/小程序标注 Beta、macOS 标注 Alpha，本次核验的仓库 `Tencent-TDS/KuiklyUI` 确认 "one codebase, six platforms"。

## 2. 为什么选 Kuikly

对跨端框架的要求并不抽象（F-007）：

- 聊天正文是**持续变化的 Markdown**，模型每吐一个 chunk 页面都要刷新
- 工具调用、审批卡、提问卡、后台任务**同时更新**
- 底层有 HTTP RPC、两条 WebSocket 事件流、扫码配对、SSH 隧道与本地存储
- 三端不仅长得接近，**连接与恢复行为也要一致**

选 Kuikly 最直接的原因是**开发快**：组件市场已有常用能力，找到合适组件、加上依赖就能在共享代码中使用，不需要先给 Android、iOS、鸿蒙分别写一套（F-007）。

## 3. 组件复用：KuiklyMarkdown 与 KuiklyWebview

DSH Mobile 直接使用两个现成组件（F-008/F-009）：

```
implementation("com.tencent.kuiklybase:KuiklyMarkdown:1.0.6-2.1.21")
implementation("com.tencent.kuiklybase:KuiklyWebview:1.0.1-2.0.21")
```

### KuiklyMarkdown：省掉最多工作

AI 对话里的 Markdown 不是解析一次就结束——**模型输出一直在变**，代码块、列表、引用和链接都要跟着刷新。若从零开始，需要先找三端可用的解析器，再写 AST→UI 映射、代码高亮、主题、列表缩进与流式更新（F-008）。

KuiklyMarkdown 已做好这套骨架：基于 **intellij-markdown** 解析文本、输出 Block 列表，并提供**流式渲染状态**（F-008）。接入后主要处理 DSH 自己的产品逻辑：

- 已结束的 Block 保持不动，尾部内容继续更新
- 代码块暂时未闭合时，在解析副本里补上闭合标记
- 页面更新按 **16ms 合帧**，避免每个小 chunk 都刷新一次

> 核验口径：KuiklyMarkdown 仓库位于 `Kuikly-contrib` 组织，README 精确命中版本 `1.0.6-2.1.21`，描述与博文一致（verification A3 项）。

### KuiklyWebview：App 内打开链接与外部页面

用于 Markdown 链接和外部页面的 App 内打开：共享页面直接放一个 WebView、设置 URL、监听开始加载/进度/完成/失败事件即可，刷新与返回逻辑也写在同一份 Kotlin 中（F-009）。

> ⚠️ 版本勘误：博文写 `1.0.1-2.0.21`，核验时仓库当前 README 为 `1.0.2-2.0.21`——以仓库最新版本为准（verification A3 项）。

### 组件市场整体

组件市场里还有 SQLite、相机、图片选择、录音、定位、蓝牙、MMKV 等常用能力。项目没有全部接入，但开发新功能时可先找现成组件——**省下的不是一个控件，而是同一项基础能力在三个平台上的接入、对齐与后续维护**（F-010）。

## 4. 原生桥接：差异下沉，共享层保持业务统一

跨端项目真正费时间的地方通常不是页面，而是 WebSocket、扫码、SSH 与数据库这类系统能力（F-013）。

DSH Mobile 在 **commonMain 定义统一 Module 接口**（连接、发消息、收消息、断开等业务语义），Android/iOS/鸿蒙分别接自己的系统实现（F-013）。以 WebSocket 为例：

| 平台 | 底层实现 | 共享层接口 |
|------|---------|-----------|
| Android | OkHttp | DshWebSocketModule |
| iOS | NSURLSession | DshWebSocketModule |
| HarmonyOS | NetworkKit | DshWebSocketModule |

平台差异被收敛在最底层，聊天页、事件处理、业务状态**不需要知道自己在哪个系统上**（F-013）。SSH 隧道、扫码配对也是同一套拆法（F-014）。

### 规模数据

项目约 **1.3 万行 commonMain 共享 Kotlin**；Android、iOS、鸿蒙宿主各有三四千行，主要用于接入系统能力与平台工程配置（F-015）。

### 收益会随协议变化放大

DSH 协议尚未完全稳定，往后每多一个 RPC、改一个事件，只需改共享层、三端一起生效——比将来维护三个壳便宜得多（F-014）。

## 5. KuiklyUI-AI：AI 开发配套

Kuikly 的 AI 开发配套（F-011）提供：

- **Kuikly DSL** 与 **Kuikly Compose DSL** 的开发规则
- 组件使用、Module 扩展、网络请求、响应式状态、协程、多端资源等 **Skills**

这些规则可交给 CodeBuddy、Cursor、Claude Code 等 AI 编程工具使用（F-011）。Agent 写页面、接组件或补原生桥接时，不用临时猜 Kuikly 的 API 与工程约定，生成的代码更容易直接落进项目。

> 核验确认：`Tencent-TDS/KuiklyUI-AI` 仓库含 rules/ 与 skills/，README 明确支持 CodeBuddy/Cursor/Claude Code/Windsurf（verification A4 项）。

作者的实际开发分工（F-012）：协议模型、状态机和重复页面先交给 Agent 完成，自己主要检查交互、平台差异与真机表现。
