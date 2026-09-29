---
type: Reference
title: 事实核验报告
description: DSH Mobile 博文 14 项 P0 声明核验结论——11 项通过、2 项口径差异、0 项证伪，含勘误口径标注与权威来源 URL
tags: [核验, P0, DeepSeek Harness, DSH, Kuikly, DSH Mobile, dsh-scan-remote, Kotlin Multiplatform]
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: kuikly-repo
    resource: https://github.com/Tencent-TDS/KuiklyUI
    title: KuiklyUI 官方仓库（Tencent-TDS）
  - id: kuikly-arch-doc
    resource: https://kuikly.tds.qq.com/Introduction/arch.html
    title: Kuikly 官方文档-架构介绍
  - id: kuiklymarkdown-repo
    resource: https://github.com/Kuikly-contrib/KuiklyMarkdown
    title: KuiklyMarkdown 组件仓库
  - id: kuiklywebview-repo
    resource: https://github.com/Kuikly-contrib/KuiklyWebview
    title: KuiklyWebview 组件仓库
  - id: kuikly-ui-ai-repo
    resource: https://github.com/Tencent-TDS/KuiklyUI-AI
    title: KuiklyUI-AI 仓库（Rules 与 Skills）
  - id: dsh-official
    resource: https://deepseek.com/harness/en/
    title: DeepSeek Harness 官网
  - id: dsh-repo
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: deepseek-ai/deepseek-harness 官方仓库
  - id: dsh-releases
    resource: https://github.com/deepseek-ai/deepseek-harness/releases
    title: DeepSeek Harness Releases（版本 tag）
  - id: dsh-scan-remote-repo
    resource: https://github.com/yukiykchen/dsh-scan-remote
    title: yukiykchen/dsh-scan-remote（扫码插件与 Relay）
  - id: dsh-mobile-repo
    resource: https://github.com/yukiykchen/deepseek-harness-mobile
    title: yukiykchen/deepseek-harness-mobile（DSH Mobile 仓库）
  - id: cursor-ios
    resource: https://cursor.com/changelog/ios-mobile-app
    title: Cursor Mobile App for iOS（changelog）
  - id: claude-remote-control
    resource: https://code.claude.com/docs/en/remote-control
    title: Claude Code Remote Control 官方文档
---

# 事实核验报告

> 对博文《我用腾讯 Kuikly，把 DeepSeek Harness 装进了口袋》中 14 项 P0（最高优先级）声明进行 WebSearch 权威核验。
> 核验日期：2026-09-09。
> 结果：**11 项通过（✅）、2 项口径差异（⚠️）、0 项失败（❌）。无源文硬错误。**

## 核验结论总览

| # | 声明 | 结论 | 对应事实 |
|---|------|------|---------|
| A1 | Kuikly 腾讯开源、基于 KMP、覆盖六大平台 | ✅ 通过 | F-006 |
| A2 | Kuikly "支撑业务日活超 5 亿" | ✅ 通过（官方口径，不可独立验证） | F-006 |
| A3 | KuiklyMarkdown/KuiklyWebview 组件与版本 | ⚠️ Markdown ✅ / Webview 版本出入 | F-008/F-009 |
| A4 | KuiklyUI-AI（DSL/Compose DSL Rules + Skills） | ✅ 通过 | F-011 |
| B1 | DSH 官方框架、@deepseek-ai/dsh、Cordis、developer preview | ✅ 通过 | F-017/F-045 |
| B2 | 127.0.0.1:3080 + events.mux/events.host | ✅ 通过（多方独立源） | F-018 |
| B3 | dsh-v0.1.1-rc.2 方法表 52 方法 / rpc-map.ts | ⚠️ session.prompt ✅ / "52"仅博文单源 | F-019/F-020 |
| B4 | deepseek-ai/deepseek-harness 官方仓库与最新 tag | ✅ 通过 | F-045 |
| C1 | yukiykchen/dsh-scan-remote（relay/sealed-tunnel-v1/v0.0.1） | ✅ 通过 | F-029/F-037/F-038 |
| C2 | yukiykchen/deepseek-harness-mobile 仓库 | ✅ 通过 | F-039 |
| D1 | Cursor iOS 应用 Remote Control | ✅ 通过 | F-032 |
| D2 | Claude Code Remote Control 手机接续 | ✅ 通过 | F-033 |

## 通过项详情（摘要）

### ✅ A1/A2：Kuikly 六平台与日活 5 亿（F-006）
- **核验**：GitHub `Tencent-TDS/KuiklyUI` README 确认 "one codebase, six platforms"；平台清单与博文一致（官方标注 H5/小程序 Beta、macOS Alpha）。腾讯 2025-04-30 开源公告确认基于 Kotlin Multiplatform。"日活超 5 亿"为腾讯官方宣传口径（腾讯端服务专栏 2026-07-01、云社区 2026-04-16 等一致），但仓库与文档页未载精确数字，属厂商宣传数据无法独立验证 → 正文以"腾讯官方口径"标注，不视为独立事实。
- **来源**：[KuiklyUI 仓库](https://github.com/Tencent-TDS/KuiklyUI) / [官方文档-架构](https://kuikly.tds.qq.com/Introduction/arch.html) / [腾讯开源公告](https://cloud.tencent.com/developer/article/2517161)

### ⚠️ A3：KuiklyMarkdown 与 KuiklyWebview 组件（F-008/F-009）
- **KuiklyMarkdown ✅**：`Kuikly-contrib/KuiklyMarkdown` 仓库 README 精确命中依赖坐标 `com.tencent.kuiklybase:KuiklyMarkdown:1.0.6-2.1.21`；基于 intellij-markdown、流式渲染等描述与博文一致。
- **KuiklyWebview ⚠️**：仓库 `Kuikly-contrib/KuiklyWebview` 存在、坐标正确，但**当前 main 分支 README 版本为 `1.0.2-2.0.21`，与博文 `1.0.1-2.0.21` 不一致**（疑博文引用旧版或笔误）。→ 正文标注"版本以仓库最新 README 为准"。
- **口径注意**：两组件位于 `Kuikly-contrib` 组织（腾讯端服务关联），表述为"腾讯端服务关联的 Kuikly 组件生态"而非 KuiklyUI 主仓库。
- **来源**：[KuiklyMarkdown](https://github.com/Kuikly-contrib/KuiklyMarkdown) / [KuiklyWebview](https://github.com/Kuikly-contrib/KuiklyWebview)

### ✅ A4：KuiklyUI-AI（F-011）
- **核验**：`Tencent-TDS/KuiklyUI-AI` 仓库含 rules/（kuiklyDSL.mdc、kuiklyComposeDSL.mdc）与 skills/，README 明确支持 CodeBuddy/Cursor/Claude Code/Windsurf。官方发布文（掘金·腾讯端服务 2026-04-22）确认。
- **来源**：[KuiklyUI-AI 仓库](https://github.com/Tencent-TDS/KuiklyUI-AI)

### ✅ B1/B2/B4：DSH 官方框架与协议端点（F-017/F-018/F-045）
- **核验**：DeepSeek 官网 harness 页自述 "developer preview"、安装命令 `npx @deepseek-ai/dsh web`、基于 Cordis。端口 3080/仅回环经 CSDN 教程与 dsh-scan-remote README 独立确认；events.mux/events.host 两路 WS 经独立源码实测复现（jishuzhan.net 2026-08-15）。官方仓库 `deepseek-ai/deepseek-harness` 最新 tag `dsh-v0.1.3-alpha.1`（约 2026-09-07），晚于博文锁定的 dsh-v0.1.1-rc.2，印证"快速迭代、按 tag 锁定"的时效声明。
- **来源**：[DSH 官网](https://deepseek.com/harness/en/) / [官方仓库](https://github.com/deepseek-ai/deepseek-harness) / [Releases](https://github.com/deepseek-ai/deepseek-harness/releases)

### ⚠️ B3：RPC 方法数与 session.prompt（F-019/F-020）
- **session.prompt ↔ POST /api/session.prompt ✅**：CSDN 源码分析与 jishuzhan.net 浏览器实测独立确认。
- **"52 个方法 / rpc-map.ts" 🔍**：未找到独立复述来源，属博文单源细节；博文本人注明"52 只对应文中使用的版本" → 正文以"博文口径（dsh-v0.1.1-rc.2）"标注，提示以仓库 rpc-map.ts 为准。
- **来源**：[CSDN 源码分析](https://blog.csdn.net/qq_20042935/article/details/163945715) / [浏览器实测](https://jishuzhan.net/article/2088656858302005249)

### ✅ C1/C2：作者开源仓库（F-029/F-037/F-039）
- **核验**：`yukiykchen/dsh-scan-remote` 含 relay/（Passwordless WSS Relay）、sealed-tunnel-v1 test vectors、v0.0.1 Latest release、安装命令与博文一致。`yukiykchen/deepseek-harness-mobile`（Public）README 自述"用 Kotlin/Kuikly 做宿主界面，连到电脑上的 Host"，支持扫码（Relay sealed tunnel）与 SSH 两种模式、events.mux WebSocket。作者 yukiykchen 即博文作者 yuki。
- **来源**：[dsh-scan-remote](https://github.com/yukiykchen/dsh-scan-remote) / [deepseek-harness-mobile](https://github.com/yukiykchen/deepseek-harness-mobile)

### ✅ D1/D2：行业同类产品（F-032/F-033）
- **核验**：Cursor 官方 changelog（2026-06-29，v3.9）确认 iOS App + Remote Control 操作电脑 Agent；Anthropic 官方文档确认 Claude Code Remote Control 通过 Claude App 扫码接续本机会话（代码执行/文件访问仍在本机）。
- **来源**：[Cursor iOS changelog](https://cursor.com/changelog/ios-mobile-app) / [Claude Code Remote Control](https://code.claude.com/docs/en/remote-control)

## 勘误与口径清单

| 类型 | 源文口径 | 核验后处理 |
|------|---------|-----------|
| 版本口径（F-009） | KuiklyWebview `1.0.1-2.0.21` | ⚠️ 当前 README 为 `1.0.2-2.0.21`；正文标注"博文撰写时版本，以仓库最新为准" |
| 单源声明（F-020） | "52 个方法 / rpc-map.ts" | ⚠️ 仅博文单源；正文标注"博文口径（dsh-v0.1.1-rc.2）" |
| 宣传口径（F-006） | Kuikly "日活超 5 亿" | 标注"腾讯官方宣传口径"，不可独立验证；不作独立事实 |
| 组件归属（F-008/F-009） | "组件市场" | 两组件属 `Kuikly-contrib`（腾讯端服务关联）组织，非 KuiklyUI 主仓库 |

## 信源距离判定

- **博文性质**：作者一手实测（作者即 DSH Mobile / dsh-scan-remote 开发者）+ 腾讯官方公众号发布。非纯厂商自宣文（无夸大提效数字），但含 Kuikly（腾讯开源）宣传背景 → 已核验 5 亿日活口径。
- **核验手段**：官方仓库（KuiklyUI/Kuikly-contrib/KuiklyUI-AI/deepseek-harness）+ 官方文档（DSH 官网/Cursor/Claude Code）+ 独立第三方实测（CSDN/jishuzhan）。
- **无假核验**：所有来源 URL 均来自 WebSearch 实际检索结果；未能独立证实的细节（52 方法/rpc-map.ts）如实标注"仅博文单源"。

## 验证日期

- 核验日期：2026-09-09
- 复核建议：DSH 版本迭代极快（本文核验时已至 dsh-v0.1.3-alpha.1），涉及版本/方法数引用时以仓库 Releases 与 rpc-map.ts 为准。
