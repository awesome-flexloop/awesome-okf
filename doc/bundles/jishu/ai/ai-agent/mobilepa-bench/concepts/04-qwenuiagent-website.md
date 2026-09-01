---
type: Concept
title: "Qwen-UI-Agent 网站技术栈简析"
description: "Qwen-UI-Agent 技术报告网站：网站源码仓非实现仓、Next.js 16 双构建轨道（vinext/wrangler 与 next build）、双语 LocalizedText 机制、无数据库架构与 Pages 部署自检。"
tags: [Qwen-UI-Agent, Next.js, 双构建轨道, 双语站点, 网站工程]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobilepa-facts
    resource: /references/facts.md
    title: MobilePA-Bench 与网站事实台账
  - id: mobilepa-sources
    resource: /references/source-registry.md
    title: 信源登记
---

# Qwen-UI-Agent 网站技术栈简析

> **事实基础**：本文所有数据与引文均标注 WEB-A 编号，对应本束 `references/facts.md` B 部分（每条已标注 facts-websites.md 原编号），信源根为 Qwen-UI-Agent 网站仓（`external/libs/tools/Tongyi-MAI/Qwen-UI-Agent`）。

本篇是与 MobilePA-Bench 基准本体**无依赖关系**的并入篇：对 Qwen-UI-Agent 技术报告网站（https://tongyi-mai.github.io/Qwen-UI-Agent/）的网站工程做一次技术栈简析，可与 [00-benchmark-overview.md](00-benchmark-overview.md) 的"纯静态项目页"并置，对照两种学术站点工程路线。**先声明性质：该仓库是网站源码仓，不是实现代码仓。**

## 1. 性质声明：网站源码仓，非实现代码仓

README 顶部 IMPORTANT 块原文（WEB-A-01）：

```text
Website source only — this is not the Qwen-UI-Agent implementation repository.
This repository contains only the source code and static assets for the
Qwen-UI-Agent project website ... It does not contain the model, training
code, or agent implementation.
```

中文段同义："**本仓库仅为网站源码，并非 Qwen-UI-Agent 的项目实现代码仓。** ... 不包含模型、训练代码或智能体实现代码"（WEB-A-01）。需要模型与 Agent 实现代码时，README 明确指向官方仓库 **Tongyi-MAI/MAI-UI**（WEB-A-02）。站点本身是**双语技术报告网站**，呈现真实场景能力、基准结果、更广泛的通用与智能体能力、可玩 demo 与发布材料，主流程为 "Capabilities → Performance (including Broader Capabilities) → Demos → Citation"（WEB-A-03）。

## 2. 技术栈：Next.js 16 + React 19

`package.json`：name `qwen-ui-agent-tech-report`，version 0.1.0，private，`"type": "module"`，engines `node >=22.13.0`（WEB-A-04）。依赖清单（WEB-A-05）：

| 类别 | 依赖（版本） |
|---|---|
| dependencies | next 16.2.6；react 19.2.6；react-dom 19.2.6；drizzle-orm 0.45.2 |
| devDependencies | vite 8.0.13；vinext 0.0.50；wrangler 4.92.0；@cloudflare/vite-plugin 1.37.1；@vitejs/plugin-rsc 0.5.26；tailwindcss 4.2.1（及 @tailwindcss/postcss）；typescript 5.9.3；drizzle-kit 0.31.10；eslint 9.39.4；react-server-dom-webpack 19.2.6 |

## 3. 双构建轨道：vinext/wrangler 与 next build

同一源码存在**两条构建路径**（WEB-A-06）：

- **Cloudflare 轨道**：`dev`/`build`/`start` 脚本均调用 `vinext`（带 `WRANGLER_LOG_PATH=.wrangler/wrangler.log`），面向 Cloudflare 运行时（WEB-A-04、WEB-A-06）；
- **GitHub Pages 轨道**：`build:pages` = `next build`，产出 GitHub Pages 静态站（WEB-A-04、WEB-A-06）。

`next.config.ts` 为静态导出配置（WEB-A-07）：

```typescript
output: "export"          // "Keep the site fully static so the same source can be exported for GitHub Pages."
trailingSlash: true
basePath: <NEXT_PUBLIC_SITE_BASE_PATH 环境变量>
images: { unoptimized: true }
```

`build/sites-vite-plugin.ts` 定义名为 "sites" 的 Vite 插件（`apply: "build"`），在 `closeBundle` 时把 `.openai/hosting.json` 与 `drizzle/` 迁移目录复制到 `dist/.openai/`（WEB-A-06）。

## 4. 双语机制：Language / LocalizedText / localize

双语由**内容层**处理，`<html lang>` 固定英文（WEB-A-09）。`app/siteContent.ts` 的类型与工具（WEB-A-11）：

```typescript
export type Language = "en" | "zh";
type LocalizedText = { en: string; zh: string };
function localize(text: LocalizedText, language: Language): string;
```

所有站点文案以 en/zh 双字段成对维护（WEB-A-11）。`SITE_COPY` 中的导航为 `["Capabilities", "Performance", "Demos", "Citation"]`（zh：「智能体能力/性能指标/演示/引用」），subtitle 为 "Towards Next-Generation Real-World Centric Foundation GUI Agent" / 「阿里巴巴集团的新一代真实场景 GUI 智能体」；性能表列名 `baseColumn: "Qwen3.5-27B"`、`oursColumn: "Qwen-UI-Agent"`；`sourceNote` 声明 "Content and metrics are distilled from the current LaTeX draft. Values may change before release."（WEB-A-12）。

## 5. 内容数据结构：SITE_COPY / APPLICATIONS / METHOD_STEPS / PERFORMANCE_BENCHMARKS

- **APPLICATIONS**（"what it can do" 轮播的六张视觉卡，WEB-A-13）：`kind` 枚举为 "mobile" | "computer" | "gui-cli" | "browser" | "research" | "proactive"；`visual` 类型含 `mobile-ui`（CSS 绘制手机场景）/ `video`（本地循环视频）/ `gui-cli` / `browser-capture`（三帧动画浏览器序列）/ `research-flow` / `proactive-flow` / `image`。
- **METHOD_STEPS** 四阶段方法流水线（WEB-A-14）：01 Environment infrastructure（stat "≈10K concurrent"）；02 Agent-driven data flywheel（stat "≈10K task-verifier pairs"）；03 SFT + ActionRL + Online RL（stat "100+ step trajectories"）；04 Proactive harness（stat "Mobile + Desktop + Search"）。
- **PERFORMANCE_BENCHMARKS** 代表分数（WEB-A-15）：MobileWorld 条目（metric "GUI-Only Success rate (%)"）——Qwen-UI-Agent 27B **82.1**（access "ours"）、Seed 2.1 Pro 73.2、GPT-5.6 Sol 70.1、Claude Opus 4.8 67.5、Qwen 3.7 Plus 62.3、Gemini 3.1 Pro 58.1；MobileWorld-Real 条目（真实手机）——Qwen-UI-Agent 27B **92.2**、Seed 2.1 Pro 88.7、Gemini 3.1 Pro 86.2。
- 辅助结构：`DEMO_CATEGORIES`/`DEMO_VIDEOS` 每个 demo 记录 `instructionSourceLanguage`（WEB-A-21）；`MODEL_ORGANIZATIONS` 把基准条目映射到发布方标签与 `public/brand-logos/` 本地 logo（多数 SVG 来自 Lobe Icons 1.94.0）（WEB-A-22）；`GENERAL_CAPABILITY_GROUPS` 渲染在 Performance 内的 "Broader Capabilities" 子节（WEB-A-23）；`SpecialistKey` 字面量为 `"guiOwl" | "uiVenus" | "openCUA"`（WEB-A-23）。

## 6. 无数据库：schema 故意留空

虽然技术栈引入了 drizzle-orm 与 drizzle-kit（WEB-A-05），但 `db/schema.ts` 全文仅 4 行（WEB-A-17）：

```typescript
// Intentionally empty by default.
// Add Drizzle tables here when the site actually needs a database.
// See examples/d1/db/schema.ts for an opt-in example.
export {}
```

即**当前站点无任何数据表定义**——数据库能力是预留而非使用（WEB-A-17）。`drizzle.config.ts` 配置为 `out: "./drizzle"`、`schema: "./db/schema.ts"`、`dialect: "sqlite"`（WEB-A-18）。

## 7. 路由与元数据

- `app/sitePath.ts`：`SITE_BASE_PATH` 读自 `NEXT_PUBLIC_SITE_BASE_PATH`（去尾斜杠，默认空串）；`PUBLIC_SITE_URL = "https://tongyi-mai.github.io/Qwen-UI-Agent/"` 硬编码；导出 `siteAsset()`（补 basePath 前缀）与 `absoluteSiteUrl()`（WEB-A-08）。
- `app/layout.tsx` metadata：title "Qwen-UI-Agent — Technical Report"；applicationName "Qwen-UI-Agent"；authors `[{ name: "MAI-UI Team" }]`；openGraph 图 og.png（1536x1024）；根节点 `<html lang="en">`（WEB-A-09）。
- 首页 `app/page.tsx` 全文 5 行，仅渲染 `<ReportPage />`（页面结构在 `app/components/ReportPage.tsx` 编辑）（WEB-A-10）。
- 第二路由页 `/mobileworld-real/`：渲染 `MobileWorldRealPage`，metadata 描述 "MobileWorld-Real is a real-device benchmark with human-written mobile tasks across live Android apps, accounts, content, and networks."，openGraph 提及 "everyday mobile GUI work across 409 tasks and 104 live Android apps"（WEB-A-16）。

## 8. 部署与质量自检

GitHub Pages 部署 workflow（WEB-A-19）：push main 或手动触发；Node 22 + `npm ci`；在构建环境变量 `NEXT_PUBLIC_SITE_BASE_PATH: /Qwen-UI-Agent` 下执行 `npm run build:pages`，随后 `npm run validate:pages` 校验部署路径，上传 `./out` 至 deploy-pages@v4。

测试与自检（WEB-A-20）：`npm test` = `npm run build && node --test tests/rendered-html.test.mjs`（先完整构建，再对**构建产物 HTML** 跑 Node 内置 test runner）；`validate:pages` 校验 Pages 前缀路径；`export:review`（`scripts/export-self-contained.mjs`）产出自包含审阅导出。

## 9. 站点当前状态

README 状态声明（WEB-A-24）：资源卡当前为 `Coming soon` 占位，正式技术报告、代码与 checkpoint URL 待发布时替换；外部引用嵌入被明确标注为临时样例；当前草稿中相互冲突的结果数字被**有意省略**，直至技术报告数值冻结；所有可见文案须提供英文与完全本地化中文，模型与基准专名保持不变。

## 10. 与既有评测束的互补视角

本篇是**网站工程视角**：拆的是构建轨道、双语机制与数据结构；既有 qwen-ui-agent 束是**网站内容评测视角**：评的是 Qwen-UI-Agent 的能力、基准成绩与实测体验。两者互为补充，可对照阅读：[../qwen-ui-agent/index.md](../../qwen-ui-agent/index.md)。本篇引用的 MobileWorld 82.1% / MobileWorld-Real 92.2% 等分数（WEB-A-15）为该站点登记的数据快照，与 MobilePA-Bench 榜单（[03-leaderboard-analysis.md](03-leaderboard-analysis.md)）分属不同基准，不可混用。

## 相关概念

- [00-benchmark-overview.md](00-benchmark-overview.md)——MobilePA-Bench 纯静态项目页工程（两种学术站点工程对照）
- [03-leaderboard-analysis.md](03-leaderboard-analysis.md)——不同基准的分数不可混用
- [../qwen-ui-agent/index.md](../../qwen-ui-agent/index.md)——Qwen-UI-Agent 技术评测束（网站内容视角）
- [../mai-ui/index.md](../../mai-ui/index.md)——网站 README 指向的官方实现代码仓（Tongyi-MAI/MAI-UI）对应的束
