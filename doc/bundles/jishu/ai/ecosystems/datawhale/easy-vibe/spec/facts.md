---
type: spec
title: "Easy-Vibe 事实清单（R阶段）"
---

# Easy-Vibe 事实清单（R阶段）

> 信源：https://github.com/datawhalechina/easy-vibe
> 采集日期：2026-08-23
> 原则：只记录"代码/文件里有什么"，不写"用于/目的是"等推断。

## F-001 项目身份

- 仓库名：`datawhalechina/easy-vibe`
- `package.json` 中 `name` 为 `easy-vibe`，`version` 为 `1.0.0`，`description` 为 "Easy-Vibe 中文实战课 - 零基础学会用 AI 编程"。
- 许可证：CC-BY-NC-SA-4.0（`package.json` `license` 字段与 README 徽章一致）。
- `engines.node` 要求 `>=18.0.0`。
- README 标语："Learn AI coding from zero by shipping real products. / 从零开始学 AI 编程，把想法真正做成产品。"

## F-002 项目性质

- `AGENTS.md` 第 1 行声明："This repo is a VitePress (Vue 3) documentation project."
- 仓库根目录无应用业务源码；核心内容位于 `docs/` 下的 Markdown 文件。
- `docs/.vitepress/theme/index.js` 注册了大量 Vue 交互组件，供 Markdown 中以 `<ComponentName />` 形式引用。
- `examples/` 目录包含 4 个练习项目：`trae-3d-block-game`（Electron+Vite）、`trae-block-game`、`trae-linear-dashboard`、`trae-screenshot-demo`。

## F-003 核心理念关键词

- README "Why Easy-Vibe" 章节原文："In the AI era, programming starts by describing what you want."
- `docs/zh-cn/guide/introduction.md` 第 3 行将 2025 年称为"AI编程的元年"，并提出"Vibe Coding组织开发流程"。
- `llms.txt` 第 1328 行："核心理念是 Vibe Coding（用自然语言编程）"。
- README 列出 5 类目标读者：Complete beginners、Product managers/founders、Students、Junior developers、Mid-level and senior developers。

## F-004 学习路径结构（3+1 阶段）

`docs/zh-cn/guide/introduction.md` 与 `llms.txt` 定义三阶段实战路径：

| 阶段 | 目录 | 主题 |
|------|------|------|
| Stage 1 | `docs/{locale}/stage-1/`（含部分 `stage-0/`） | 新手入门与产品原型：AI IDE、找创意、原型开发、AI 能力集成、完整项目实战 |
| Stage 2 | `docs/{locale}/stage-2/` | 初中级全栈：frontend/、backend/、ai-capabilities/、assignments/ |
| Stage 3 | `docs/{locale}/stage-3/` | 高级开发：core-skills/（Claude Code、MCP、Skills、Agent Teams）、cross-platform/、ai-advanced/ |
| 附录 | `docs/{locale}/appendix/` | 9 大知识领域、80+ 交互式专题 |

- 附录 9 大领域目录名（`llms.txt` 第 74-82 行）：
  `1-computer-fundamentals`、`2-development-tools`、`3-browser-and-frontend`、`4-server-and-backend`、`5-data`、`6-architecture-and-system-design`、`7-infrastructure-and-operations`、`8-artificial-intelligence`、`9-engineering-excellence`。

## F-005 多语言支持

- `docs/.vitepress/config.mjs` 第 48-109 行 `localeMap` 定义 10 个 locale：
  `zh-cn`、`en`、`zh-tw`、`ja-jp`、`ko-kr`、`es-es`、`fr-fr`、`de-de`、`ar-sa`、`vi-vn`。
- `docs/` 下存在对应 10 个语言目录（LS 结果确认）。
- `docs-readme/` 下存在 10 个本地化 README：`ar-SA/`、`de-DE/`、`en-US/`、`es-ES/`、`fr-FR/`、`ja-JP/`、`ko-KR/`、`vi-VN/`、`zh-CN/`、`zh-TW/`。
- `docs/index.md` 通过 `navigator.language` 映射表（第 15-37 行）将根路径重定向到对应语言目录；首次访问先跳 `/welcome`。
- `config.mjs` 为每个 locale 配置了独立的 label、lang、title、description、SEO head、nav、sidebar 与 docFooter 文案。

## F-006 文档站目录结构

```
docs/
├── .vitepress/
│   ├── config.mjs              # 站点主配置
│   ├── seo.mjs                 # SEO head 生成
│   ├── build-hooks.mjs         # 构建钩子
│   ├── sidebars/
│   │   ├── index.mjs           # 侧边栏聚合导出
│   │   └── data.mjs            # 侧边栏数据
│   └── theme/
│       ├── index.js            # 主题入口、组件注册
│       ├── Layout.vue          # 布局覆写
│       ├── style.css           # 全局样式
│       ├── components/         # 通用组件（NavCard、StepBar、Tabs、WelcomeScreen 等）
│       ├── composables/useI18n.js
│       ├── data/               # easyVibePaths.json、relatedArticles.js
│       └── locales/            # 附录组件的 i18n 文案（api-intro、cloud-iam、dns-https 等）
├── public/                     # favicon、logo、llms.txt、robots.txt、sitemap.xml、style.css
├── assets -> ../assets         # 符号链接
├── index.md                    # 首页（语言重定向逻辑）
├── welcome.md                  # 欢迎页（<WelcomeScreen />）
├── DEPLOYMENT.md               # 部署说明
├── zh-cn/  en/  zh-tw/  ja-jp/  ko-kr/  es-es/  fr-fr/  de-de/  ar-sa/  vi-vn/
│   ├── index.md                # 各语言首页（hero + HomeFeatures）
│   ├── guide/introduction.md
│   ├── stage-1/  stage-2/  stage-3/  appendix/
│   └── vibe-stories/           # zh-cn、en 含 story-1~4.md
└── （部分语言含 stage-0/、public/）
```

## F-007 技术栈（package.json 依赖）

运行时依赖：
- `vitepress: ^2.0.0-alpha.16`
- `vue: ^3.5.0`
- `element-plus: ^2.13.1`、`@element-plus/icons-vue: ^2.3.2`
- `viewerjs: ^1.11.7`（图片查看）
- `typeit: ^8.8.7`（打字机效果）
- `mermaid: ^11.13.0`（图表）
- `reveal.js: ^6.0.1`（演示）
- `claude: ^0.1.1`

开发依赖：
- `prettier: ^3.7.4`、`eslint: ^9.0.0`、`eslint-plugin-vue`、`vue-eslint-parser`
- `husky: ^9.1.7`（Git hooks）
- `gray-matter: ^4.0.3`（frontmatter 解析）
- `markdown-it`、`markdown-it-katex`、`markdown-it-container`、`markdown-it-footnote`
- `katex: ^0.18.1`
- `puppeteer-core: ^25.5.0`（PDF/EPUB 生成）
- `archiver: ^8.0.0`

## F-008 自定义主题能力（docs/.vitepress/theme/）

- `index.js` 同步注册通用组件：`HomeFeatures`、`WelcomeScreen`、`NavGrid`、`NavCard`、`CategoryIndex`、`ArticleGrid`、`RelatedArticlesSection`、`StepBar`、`ChapterIntroduction`、`ReadingProgress`、`SummaryCard`、`Tabs`、`TabItem`、`LearningPathCompact`、`ProductJourney`、`AppendixFlowMap`、`CopyOrDownloadAsMarkdownButtons`。
- `index.js` 通过 `appendixComponentModules` 对象以动态 `import()` 注册了 200+ 附录交互组件，按主题分子目录：`terminal-intro/`、`api-intro/`、`llm-intro/`、`vlm-intro/`、`image-gen-intro/`、`audio-intro/`、`web-basics/`、`git-intro/`、`computer-fundamentals/`、`deployment/`、`auth-design/`、`cache-design/`、`queue-design/`、`prompt-engineering/`、`context-engineering/`、`frontend-engineering/`、`agent-intro/`、`database-intro/`、`ide-intro/`、`operations/`、`backend-languages/`、`concurrency-models/`、`component-state-management/`、`ai-protocols/`、`framework-nature/`、`backend-evolution/`、`frontend-performance/`、`canvas-intro/`、`transformer-attention/`、`browser-frontend/`、`data-encoding/`、`url-to-browser/`、`ai-history/`、`frontend-routing/`、`browser-devtools/` 等。
- `WelcomeScreen.vue` 实现 SVG 路径描边动画，含 ocean/rainbow/sunset 三套主题循环，点击后写入 `localStorage` 键 `easy-vibe-welcome-seen=1` 并跳转。
- `CLAUDE.md` 记载主题行为：Viewer.js 在 `.vp-doc` 容器按路由切换初始化；TypeIt 仅在首页 `frontmatter.hero.tagline` 为数组时激活；阅读设置面板用 Element Plus popover 调整字号(12-18px)与行高(1.25-1.8)，通过 CSS 变量 `--ev-doc-font-size`、`--ev-doc-line-height` 持久化到 localStorage。

## F-009 构建脚本（scripts/）

- `build-locales.mjs`：`npm run build` 入口。默认构建 10 个 locale，通过 `VITEPRESS_BUILD_LOCALES` 环境变量可指定子集。
  - 第 40 行 `groupSize` 默认 1（顺序构建每个 locale），注释说明 VitePress 2 alpha 共享 `.temp` 目录，并发构建会导致 `ERR_MODULE_NOT_FOUND`。
  - 第 44 行使用文件锁 `build-locales.lock`（`wx` 标志 + PID 存活检测），15 分钟超时。
  - 每个 locale 以 `--max-old-space-size=4096`（可通过 `BUILD_HEAP_MB` 调整）单独调用 vitepress build，输出到临时目录 `dist-locales/{group}`，再合并到最终 `dist/`。
  - 合并各 locale 的 `hashmap.json`，复制 `sitemap.xml`。
- `generate-sitemap.mjs`：生成 `sitemap.xml` 与 `robots.txt`。
- `build-latex-book.mjs`、`build-epub.mjs`、`build-books.mjs`、`book-shared.mjs`、`render-book-asset.mjs`、`epub-image-conversion.mjs`：多语言 PDF（XeLaTeX）与 EPUB 电子书构建。
- `optimize-stage1-images.mjs`：Stage 1 图片优化。
- `scan-appendix-component-i18n.mjs` + `.test.mjs`：扫描附录 Vue 组件 `<template>` 文案在两 locale 间的翻译缺失（`tools/translation/` 下有 fixture 与韩文术语表）。

## F-010 部署配置

- Base 路径自适应（`config.mjs` 第 21-29 行）：
  - `process.env.BASE` 优先；
  - `VERCEL=1` 或 `VERCEL_URL` 存在，或 `EDGEONE=1`/`EDGEONE_URL` 存在 → `/`；
  - 否则（GitHub Pages / 本地）→ `/easy-vibe/`。
- `vercel.json`：`buildCommand: npm run build`，`outputDirectory: docs/.vitepress/dist`，framework 为 vitepress；配置了静态资源缓存头（`/assets/*` immutable 1年）、安全头（`X-Content-Type-Options`、`X-Frame-Options: DENY`、`X-XSS-Protection`、`Referrer-Policy`、`Permissions-Policy`）。
- `Dockerfile`：多阶段构建。`node:20-alpine` 执行 `npm ci && npm run build`，`nginx:alpine` 拷贝 `nginx.conf` 与 `docs/.vitepress/dist`，`EXPOSE 7860`（魔搭 ModelScope 创空间要求端口）。
- `nginx.conf`：配套 Nginx 配置（未展开读取，由 Dockerfile 引用）。
- `.github/workflows/deploy.yml`：推送到 `main` 时构建并部署到 GitHub Pages。Node 20，`NODE_OPTIONS=--max-old-space-size=8192`，仅 `github.repository_owner == 'datawhalechina'` 执行，使用 `actions/configure-pages`、`upload-pages-artifact`、`deploy-pages`。
- `.github/workflows/release-books.yml`：推送 `v*` tag 时，安装 texlive（含 CJK/阿拉伯/韩/日字体）、imagemagick、ffmpeg、ghostscript、librsvg，执行 `npm run book:all`，将 PDF/EPUB 上传到 GitHub Release。
- `docs/DEPLOYMENT.md` 记录 Vercel/GitHub Pages/Local 三种环境的 base 差异与故障排查（`VERCEL` 缺失导致 404、GitHub Pages 缺 `/easy-vibe/` base 导致 404）。
- `ms_deploy.json`：存在于仓库根（内容未读取，文件名暗示魔搭部署配置）。

## F-011 开发命令（package.json scripts）

- `dev`: `vitepress dev docs`
- `build`: `node scripts/build-locales.mjs`
- `build:single`: `npm run sitemap && node --max-old-space-size=8192 node_modules/vitepress/bin/vitepress.js build docs`
- `preview`: `vitepress preview docs`
- `test`: `node --test $(find docs scripts -name '*.test.js' -print)`
- `format`: `prettier --write .`
- `lint`: `eslint docs/.vitepress/theme`
- `sitemap`: `node scripts/generate-sitemap.mjs`
- `book:pdf` / `book:epub` / `book:all` / `book:zh` / `book:en`
- `prepare`: `husky`（安装 git hooks）

## F-012 代码风格与质量

- `.prettierrc`：`semi: false`、`singleQuote: true`、`trailingComma: "none"`。
- `.husky/pre-commit`、`.husky/pre-push`：存在（内容未展开）。
- `eslint.config.js`：ESLint 9 扁平配置。
- 无独立测试框架；`AGENTS.md` 明确"use `npm run build` as the primary correctness check"，测试仅 `tools/translation/check-localization.test.mjs` 等少量 Node 原生 test。

## F-013 AI Agent 友好设计

- 根目录 `llms.txt`：1380 行的 AI 导航地图，含高层架构 ASCII 图、快速决策树、目录结构速查、每篇文章的文件路径/关键词/内容概要、回答规则 8 条。
- `docs/public/llms.txt`：公开发布版本（站点可访问）。
- `CLAUDE.md`：针对 Claude Code 的详细指南（项目概述、命令、架构、内容规范、多语言、权限）。
- `AGENTS.md`：通用 AI Agent 仓库指南（项目结构、构建命令、编码风格、测试、PR 规范、部署）。
- `config/mcporter.json`：存在（MCP 相关配置，内容未读取）。
- README 新闻条目（2026-03-02）："Added `llms.txt` so OpenClaw, Claude, Cursor, Trae, and other AI agents can quickly understand the repository structure."

## F-014 首页与欢迎页机制

- `docs/index.md` frontmatter `layout: home`，`<script setup>` 中：
  - 定义 21 条浏览器语言→locale 路径映射（含短码回退，如 `zh`→`/zh-cn/`、`en-us`→`/en/`）。
  - 读取 `localStorage` 键 `easy-vibe-welcome-seen`；未看过则 `window.location.replace('/welcome?next=...')`；已看过则直接替换到目标语言路径。
  - 使用 `withBase()` 包裹路径以兼容 base 差异。
- `docs/welcome.md` frontmatter `layout: false`，仅渲染 `<WelcomeScreen />`。
- `docs/zh-cn/index.md` 使用 VitePress home hero，`typingTagline` 为 8 句循环文案数组，主按钮跳转 `/zh-cn/stage-1/learning-map/`，渲染 `<HomeFeatures />`。

## F-015 Vite Stories（用户故事）

- `docs/zh-cn/vibe-stories/` 与 `docs/en/vibe-stories/` 各含 `story-1.md`~`story-4.md`。
- README 新闻（2026-03-29）说明四个真实故事主角：乡村小学教师、大学生、高中 IT 教师、用 AI 做出真实产品的卡车司机。
- `config.mjs` 中 `getVibeStoriesSidebar(locale)` 与 `getVibeStoriesNavText(locale)` 为各语言生成故事侧边栏与导航文案。

## F-016 Markdown 扩展与构建钩子

- `config.mjs` 第 208-233 行：markdown 配置启用 `markdownItKatex`；自定义 image 渲染规则——对 `stage-1` 路径下的图片自动添加 `decoding="async"` 与 `loading="lazy"`（注释说明 Stage 1 长教程截图多，原生懒加载避免首屏竞争）。
- `build-hooks.mjs`：提供 `transformHtml`/`transformHead`/`buildEnd` 钩子（通过 `createBuildHooks` 工厂创建，接收 base、siteUrl、supportedLocaleDirs 等）。
- `seo.mjs`：`createSeo` 工厂生成 Open Graph/Twitter card 等 head 标签，并提供 `rewriteMissingLocaleMenuLinks`。
- Sitemap（`config.mjs` 第 250-274 行）：`changefreq: weekly`，优先级首页 1.0、语言首页 0.9、各 stage 0.8、appendix 0.7；过滤掉 `/extra/`、`/examples/`、`/project/` 遗留路径。
- `ignoreDeadLinks: true`（第 235 行）。

## F-017 示例项目（examples/）

| 目录 | 关键文件 |
|------|---------|
| `trae-3d-block-game/` | `electron/main.js`、`src/index.html`、`src/main.js`、`src/styles.css`、`package.json`、`vite.config.js`、`prompt.txt`、`reference.png` |
| `trae-block-game/` | `index.html`、`prompt.txt`、`reference.png` |
| `trae-linear-dashboard/` | `index.html`、`prompt.txt` |
| `trae-screenshot-demo/` | `index.html`、`script.js`、`styles.css`、`prompt.txt` |

- 每个示例均含 `prompt.txt`，记录用于生成该示例的 AI 提示词。

## F-018 版本与时间线（README 新闻）

- 2026-08-12：Stage 1 重构改版（从真实问题出发，找机会、选方向、用户需求、访谈、收敛方案、原型、AI 集成）。
- 2026-06-17：全部教程内容（Stage 1-3）完成 10 语言覆盖。
- 2026-03-29：Vibe Stories 上线，4 个真实用户故事。
- 2026-03-26：Stage 2 SaaS 大作业（文案生成网站）与 Stripe 支付扩充。
- 2026-03-25：新增用户研究与需求验证附录（创意来源、双钻模型、JTBD、The Mom Test）；英文文档 Stage 2/3 完整。
- 2026-03-02：新增 `llms.txt`；Stage 3 升级 Claude Code 深度指南（MCP、Skills、Agent Teams）+ 8 个跨平台项目。
- 2026-01-13：重构文档架构，全面启用多语言。
- 2026-01-01：发布核心学习地图。

## F-019 维护团队

- README 贡献者名单：Sanbu（项目负责人，Datawhale 成员）、方可（导师，清华大学）、Yerim Kang、Zhilin Zhao、Yixuan Li（视觉设计）、Siyi Liu、Lixin Liu 等清华大学参与者。
- 特别感谢 OpenAI 提供算力支持、@Sm1les 协助。
- Datawhale 支持团队联系入口指向 `datawhalechina/DOPMC`。
