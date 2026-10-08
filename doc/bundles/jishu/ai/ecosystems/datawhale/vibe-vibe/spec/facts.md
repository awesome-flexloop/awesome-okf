---
type: spec
title: "Vibe Vibe 事实清单（R阶段）"
---

# Vibe Vibe 事实清单（R阶段）

> 信源：https://github.com/datawhalechina/vibe-vibe
> 采集日期：2026-08-23
> 原则：只记录"代码/文件里有什么"，不写"用于/目的是"等推断。

## F-001 项目身份

- 仓库名：`datawhalechina/vibe-vibe`
- `package.json` 中 `name` 为 `vibe-vibe-tutorial`，`version` 为 `0.0.4`。
- README 声明许可证为 CC BY-NC-SA 4.0（含徽章与完整许可链接）；`package.json` `license` 字段为 `ISC`（两者不一致）。
- `packageManager` 为 `pnpm@10.21.0`。
- 在线站点：`https://www.vibevibe.cn`（config.mts 第 44 行 `SITE_URL_FALLBACK`）。
- README 标题："Vibe Vibe —— 人人都能学会的 AI 编程（Vibe Coding）指南"。
- README 副标题："面向零编程基础学习者的 AI 辅助编程系统化教程，从「我有一个想法」到「我做出了一个产品」，让人人都能成为 Builder。"

## F-002 项目性质

- 仓库是基于 VitePress 的静态文档站，核心内容位于 `docs/` 下的 Markdown 文件。
- `package.json` 无业务运行时依赖（无 dependencies 字段，全部为 devDependencies）。
- 文档站完全静态运行，部署指南明确"无需外部 API 调用""不需要数据库"。
- `docs/.vitepress/theme/components/` 下注册 100+ 个 Vue 交互组件，供 Markdown 中以标签形式引用。

## F-003 核心理念关键词

- README "核心理念"章节："践行 OpenAI 联合创始人 Andrej Karpathy 提出的 Vibe Coding 理念——从 Coder 到 Commander：通过自然语言与 AI 对话，让编程从'写代码'转变为'对话式创作'。"
- 引用 Karpathy 原文："完全沉浸于编程的'氛围'中，忘记代码的存在。"
- docs/index.md 第 182-184 行引用 Karpathy 英文原文及 2025 年份标注。
- docs/index.md 将 Vibe Coding 定位为"AI 创造"的子集："你负责方向、判断和审美，AI 帮你把作品做出来。"
- llms.txt 第 9 行："Vibe Vibe is the first systematic open-source tutorial for Vibe Coding in China"。
- llms.txt 第 11 行："Core philosophy: From Coder to Commander, replacing traditional coding with conversational creation."

## F-004 四大板块结构

README 与 docs/index.md 定义四大板块：

| 板块 | 目录 | 定位 | 技术栈 |
|------|------|------|--------|
| 基础篇 | `docs/Basic/` | AI 编程入门 + 心法 + 第一个项目 | HTML/CSS/JS · AI 工具 · Git · 静态部署 |
| 进阶篇 | `docs/Advanced/` | 16 章从 0 到上线的避坑指南 | Next.js 16 · React · TypeScript · Tailwind · shadcn/ui · Drizzle · PostgreSQL |
| 实践篇 | `docs/Practice/` | 分人群项目实战 + 进阶技能训练 | 多种 |
| 优质文章篇 | `docs/Articles/` | 精选学习资源 + 行业前沿追踪 | 无特定栈 |

- 进阶篇 16 章标题（README 目录与 config.mts nav 一致）：环境搭建、AI 调教、PRD 文档驱动、开发常识、UI/UX、数据持久化、后端 API、认证安全、测试自动化、公网访问、Git 协作、无服务器部署 CI/CD、域名 DNS、VPS 运维部署、SEO 分析、用户反馈迭代。
- 优质文章篇分 6 个子目录：`01-core-concepts/`、`02-technical-architecture/`、`03-toolchain-frameworks/`、`04-engineering-practices/`、`05-security-compliance/`、`06-business-trends/`。

## F-005 基础篇 v2 重构

- `docs/Basic/index.md` frontmatter description："VibeVibe 基础篇：围绕个人主页 + 数字分身案例，带零基础读者完成第一次从想法到上线的完整闭环。"
- 基础篇已按新版主线重写，围绕"个人主页 + 数字分身"一个连续案例。
- v2 章节结构（7 章，编号 0-6）：

| 章节 | 目录 | 解决问题 | 核心交付 |
|------|------|---------|---------|
| 第 0 章 | `00-preface/` | 开始前知道学什么、怎么学、卡住怎么办 | 学习地图 |
| 第 1 章 | `01-awakening/` | 做出第一个能预览、能聊天的版本 | v1 原型 |
| 第 2 章 | `02-mindset/` | 把项目带回本地，获得长期掌控力 | 本地可运行项目 |
| 第 3 章 | `03-technique/` | 让首页更像作品而非默认模板 | 视觉统一的首页 |
| 第 4 章 | `04-practice-0-to-1/` | 让内容更完整，代码更可回退 | 完整主页 + 最小 Git 闭环 |
| 第 5 章 | `05-advanced/` | 让数字分身更像你，学会基础排错 | 稳定的数字分身 |
| 第 6 章 | `06-launch/` | 正式上线并收集真实反馈 | 公网可访问链接 |

- 每章含 `index.md` 与若干编号小节文件（如 `1.1-coder-to-commander.md`、`3.1-prompt-basics.md`）。
- 另有 `99-appendix/`（附录）、`100-epilogue/`（结语）、`101-next-part/`（下部预告）。
- `docs/Basic-old/` 保留旧版基础篇内容（5 章 + 附录结构，每章含更多子目录与小节）。
- 基础篇明确默认读者是"独立 vibe coder"，不假设身边有前端、后端、测试同事。

## F-006 多语言架构

config.mts 第 71-248 行定义 `locales` 配置，含两个 locale：

| locale key | label | lang | link | 内容位置 |
|-----------|-------|------|------|---------|
| `root` | 简体中文 | `zh-CN` | 无（根路径） | `docs/` 根目录下的 Basic/、Advanced/、Articles/、Practice/ |
| `en` | English | `en-US` | `/en/` | `docs/en/` 下镜像相同结构 |

- `docs/zh/index.md` 存在，是中文首页（与根 locale 内容相同，作为 `/zh/` 路径入口）。
- `docs/en/index.md` 是英文首页，hero 文案翻译为英文，actions 链接指向 `/en/Basic/`、`/en/Advanced/` 等。
- `docs/en/Basic/`、`docs/en/Advanced/`、`docs/en/Articles/`、`docs/en/Practice/` 完整镜像中文目录结构（Glob 结果确认 200+ 英文文件）。
- `docs/index.md` 第 44-54 行 `<script setup>` 中 `resolveLocaleEntry()` 函数：读取 `navigator.languages`，若任一语言以 `zh` 开头则返回 `/zh/`，否则返回 `/en/`；`onMounted` 时若路径为 `/` 则 `window.location.replace()` 重定向。
- 顶部导航含 `{ component: 'LocaleSwitch' }`（config.mts 第 136、224 行），提供手动语言切换。
- 两个 locale 各自独立配置 nav、docFooter、outline、lastUpdated 等文案。

## F-007 文档站目录结构

```
docs/
├── .vitepress/
│   ├── config.mts                  # 站点主配置（locales、nav、SEO、head、markdown）
│   ├── modules/
│   │   ├── defaults.ts             # 自动描述、难度推断、相关页生成
│   │   ├── faq.ts                  # FAQ Schema 构建
│   │   ├── feed.ts                 # RSS/robots.txt 生成
│   │   ├── seo.ts                  # 面包屑 Schema
│   │   ├── sitemap.ts              # 图片 sitemap
│   │   └── utils.ts                # frontmatter 解析、阅读时间、JSON-LD 等
│   └── theme/
│       ├── components/             # 100+ 交互组件（按章节编号前缀）
│       ├── composables/useAnimation.ts
│       ├── styles/variables.css
│       ├── types/components.ts
│       ├── custom.css
│       └── index.ts
├── public/
│   ├── logo.png
│   ├── favicon.ico
│   ├── llms.txt                    # AI Agent 导航文件（公开发布）
│   ├── giscus/                     # 评论系统主题 CSS
│   ├── images/                     # 教程截图（按板块分目录）
│   ├── components/                 # 静态 HTML 演示组件
│   ├── humans.txt
│   └── gonganbeian.png             # 备案图标
├── index.md                        # 首页（含语言自动重定向脚本）
├── zh/index.md                     # 中文首页
├── en/index.md                     # 英文首页
├── Basic/                          # 基础篇（中文，v2）
│   ├── 00-preface/ ~ 06-launch/
│   ├── 99-appendix/
│   ├── 100-epilogue/
│   └── 101-next-part/
├── Basic-old/                      # 旧版基础篇（保留）
├── Advanced/                       # 进阶篇（中文，16 章）
├── Articles/                       # 优质文章篇（中文，6 分类）
├── Practice/                       # 实践篇（中文）
├── en/                             # 英文版镜像
│   ├── Basic/  Advanced/  Articles/  Practice/
└── deployment/index.md             # 私有化部署指南
```

## F-008 技术栈与依赖

`package.json` devDependencies：

- `vitepress: ^1.6.4`（稳定版，非 alpha）
- `vue: ^3.5.25`
- `vitepress-sidebar: ^1.33.0`（自动侧边栏生成）
- `vitepress-plugin-mermaid: ^2.0.17` + `mermaid: ^11.12.1`（图表）
- `vitepress-markdown-timeline: ^1.2.2`（时间线）
- `vite-plugin-pwa: ^0.21.2`（PWA 支持）
- `markdown-it-task-lists: ^2.1.1`、`markdown-it-mathjax3: ^4.3.2`
- `@giscus/vue: ^3.1.1`（评论系统）
- `medium-zoom: ^1.1.0`（图片缩放）
- `cytoscape: ^3.33.1` + `cytoscape-cose-bilkent: ^4.1.0`（关系图可视化）
- `dayjs: ^1.11.19`、`debug: ^4.4.3`、`glob: ^13.0.6`
- `@braintree/sanitize-url: ^7.1.1`（URL 消毒）
- `patch-package: ^8.0.1`（依赖补丁）
- `prettier: ^3.8.1`
- `@types/node: ^25.0.2`

## F-009 构建脚本

`package.json` scripts：

- `dev`: `vitepress dev docs`
- `build`: `vitepress build docs`
- `preview`: `vitepress preview docs`
- `postinstall`: `patch-package`

与 easy-vibe 不同，vibe-vibe 没有自定义多语言构建脚本——直接使用 VitePress 原生的多语言构建能力（稳定版 1.6.4 已支持），无需顺序构建或文件锁。

构建产物位于 `docs/.vitepress/dist`。

## F-010 自定义主题与交互组件

- `docs/.vitepress/theme/components/` 下有 100+ 个 Vue 组件，按章节编号前缀命名：
  - `01-0-*` ~ `01-1-*`：第 1 章相关（终端模拟器、AI 工具选择器、文件系统树、包管理器生态等）
  - `02-1-*` ~ `02-5-*`：第 2 章（Token 计算器、工作流步进器、MCP 决策树、提示词优化器）
  - `03-1-*` ~ `03-4-*`：第 3 章（面试模拟器、灵魂三问、PRD 对比、PRD 到代码流）
  - `04-0-*` ~ `04-7-*`：第 4 章（构建模式模拟器、编译 vs 解释、数据模型 ER、HTTP 请求流、API 集成流、代理架构）
  - `05-1-*` ~ `05-5-*`：第 5 章（设计工具工作流、组件库决策树、动效演示、视觉效果）
  - `06-1-*` ~ `06-3-*`：第 6 章（存储演进、数据库可视化、CRUD 可视化）
  - `07-0-*` ~ `07-3-*`：第 7 章（全栈流、API 演进、错误处理、实时对比）
  - `08-0-*` ~ `08-5-*`：第 8 章（认证流、安全边界、CORS、RBAC 矩阵、攻击可视化）
  - `09-1-*` ~ `09-3-*`：第 9 章（测试金字塔、API 测试场景、CI 工作流）
  - `10-1-*` ~ `10-2-*`：第 10 章（localhost vs 公网、网络层、隧道流）
  - `11-1-*` ~ `11-3-*`：第 11 章（Git 流程图、三区域模型、分支工作流、PR 工作流）
  - `12-3-*`：第 12 章（CI 工作流、部署流水线）
  - `13-1-*`：第 13 章（DNS 记录类型、DNS 解析、域名层级、SSL 证书流）
  - `14-2-*` ~ `14-3-*`：第 14 章（防火墙规则、安全加固、容器网络）
  - `15-1-*` ~ `15-2-*`：第 15 章（OG 卡片预览、SEO 清单、SEO 流程）
  - `16-2-*` ~ `16-3-*`：第 16 章（优先级矩阵、RICE 计算器、面试题）
  - 通用组件：`BasicEditionUpdateBox.vue`、`LocaleSwitch.vue`
- `composables/useAnimation.ts` 提供动画复用逻辑。
- `styles/variables.css` 定义 CSS 变量。
- `COMPONENT_GUIDE.md` 存在于 theme 目录（组件开发指南）。

## F-011 SEO 与站点增强

config.mts 中实现的 SEO/增强功能：

- `transformHead`（第 315 行起）：为每页动态生成 title、description、OG 标签、面包屑 JSON-LD。
- 自动关键词生成（第 347 行 `generateKeywords`）：根据路径与标题生成 meta keywords。
- 自动文章分类：根据路径前缀（Basic/Advanced/Practice/Articles）生成 articleSection。
- `buildBreadcrumbList`（modules/seo.ts）：面包屑结构化数据。
- `buildFAQSchema` + `tutorialFAQs`（modules/faq.ts）：FAQ 结构化数据。
- `generateRobotsTxt` + `buildRssXml`（modules/feed.ts）：robots.txt 与 RSS 订阅。
- `buildImageSitemap`（modules/sitemap.ts）：图片 sitemap。
- `generateAutoDescription`、`inferDifficulty`、`generateRelatedPages`、`getLastUpdatedHint`（modules/defaults.ts）：自动描述、难度推断、相关页推荐、最后更新提示。
- `estimateReadingTime`（modules/utils.ts）：阅读时间估算。
- `safeJsonLd`、`escapeXml`、`safeCdata`：安全序列化工具。
- head 中配置：百度/Google/Bing 站长验证、Umami 统计（`u.vibevibe.cn/script.js`，website ID `a1b0c652-...`）、PWA manifest、hreflang  alternate 链接（zh-CN/en-US/x-default）、DNS 预解析与预连接。
- sitemap hostname 由 `resolveSiteUrl()` 动态确定，优先级：`SITE_URL` > `EDGEONE_PAGES_URL` > `DEPLOY_URL` > `URL` > `VERCEL_URL` > `https://www.vibevibe.cn`。

## F-012 部署配置

- `Dockerfile`：多阶段构建。`node:24-alpine` 安装 pnpm、`pnpm install --frozen-lockfile`、`pnpm build`；`nginx:alpine` 拷贝 `docs/.vitepress/dist` 到 `/usr/share/nginx/html`，`EXPOSE 80`。
- `docker-compose.yml`：服务名 `vibevibe`，镜像 `vibevibe-docs:latest`，端口映射 `1024:80`，时区 `Asia/Shanghai`，含 wget healthcheck（interval 30s、timeout 10s、retries 3、start_period 40s），JSON 日志限制 10m×3，bridge 网络。
- README 私有化部署命令：`docker compose up -d --build`，默认访问 `http://localhost:1024`。
- 部署指南列出四种方式：直接静态文件部署（推荐）、Docker（推荐）、EdgeOne Pages、本地预览。
- 离线能力：纯静态站，私有化部署后完全离线运行；需注意 Giscus 评论、GitHub raw 图片、外部 CDN 三类资源。
- 部署指南明确许可证在私有化场景的含义：企业内部培训/学校教学允许，收费课程禁止，须保留署名。

## F-013 AI Agent 友好设计

- `docs/public/llms.txt`：173 行的 AI 助手导航文件，标题为"Vibe Vibe - AI Programming for Everyone"，标注"GOLDEN START FOR AI ASSISTANTS"。
- llms.txt 结构：
  1. Project Essence（一句话定位）
  2. Project Structure（四大板块 ASCII 图）
  3. AI Assistant Collaboration Guide（三问识别需求、推荐学习路径表、技术栈速查、常见任务链接表、代码引用规范）
  4. Key Links（核心入口、重要文档、社区支持，按优先级排序）
  5. Project Metadata（版本 Alpha v0.0.4、许可证、主语言、技术栈、部署平台、维护组织、核心贡献者）
  6. Special Notes for AI（独特价值、用户提问响应方法、常见问题快答表）
  7. Conclusion（愿景：to enable everyone to become a Builder）
- llms.txt 最后更新日期标注为 2026-02-03。
- 与 easy-vibe 不同，根目录无独立的 `llms.txt`、`CLAUDE.md`、`AGENTS.md` 文件；AI 导航资产仅 `docs/public/llms.txt` 一份。
- llms.txt 中常见任务表直接给出章节路径（如"Write PRD → /Advanced/03-prd-doc-driven/"）。

## F-014 进阶篇技术栈

- README 与 llms.txt 一致声明进阶篇技术栈：Next.js 16 · React · TypeScript · Tailwind CSS · shadcn/ui · Drizzle ORM · PostgreSQL。
- 部署平台推荐：Vercel / EdgeOne Pages（llms.txt 第 72 行）。
- AI 工具推荐：Cursor / Windsurf / Claude / GitHub Copilot（llms.txt 第 73 行）。
- 进阶篇状态（docs/index.md 第 146 行）："已完成 2/16，其余章节可阅读序言"。
- 进阶篇含额外页面：`happy-coder.md`、`web-ide.md`、`99-next-level/index.md`。

## F-015 目标读者分层

README 与 docs/index.md 明确面向多类人群：

| 人群 | 推荐起点 |
|------|---------|
| 完全零基础 | 基础篇 → 第 1 章 觉醒 |
| 用过 ChatGPT 但没做过项目 | 基础篇 → 第 2 章 心法 |
| 有编程基础想学 Vibe Coding | 基础篇快速浏览 → 进阶篇 |
| 想直接动手做项目 | 基础篇 → 第 4 章 实战 |
| 想找项目练手 | 实践篇 |
| 设计师/产品经理 | 基础篇 |
| 前端开发者 | 进阶篇 |
| 后端开发者 | 进阶篇 |
| 创业者/独立开发者 | 基础篇 + 进阶篇 |

## F-016 项目状态与时间线

- docs/index.md 与 docs/zh/index.md 标注"内部预览版本"，"章节内容正在持续优化完善中"。
- docs/en/index.md 第 135 行："VibeVibe tutorial officially resumed development on January 25, 2026, with continuous updates."
- llms.txt 标注版本为 Alpha v0.0.4。
- README "进阶版预告"：即将推出在线开发环境（云端 IDE 内置 Node.js 24/Python/Docker、50+ AI Skills、开箱即用）。
- README 提到关联站点 `cclog.vibevibe.cn`（Claude Code 全特性速览，220+ 版本、1000+ 项更新）。

## F-017 贡献者

README 贡献者名单：

| 姓名 | 职责 |
|------|------|
| 符航康 | 项目负责人 & 核心贡献者 |
| 齐国皓 | 项目负责人 & 核心贡献者 |
| 刘磊 | 实践篇贡献者、图像贡献者 |
| 陈俊希 | 优质文章篇板块贡献者 |
| 金龙 | 实践篇板块贡献者 |
| 舒璐璐 | 实践篇板块贡献者 |

- 维护组织：Datawhale。
- 贡献入口：GitHub Issues / Pull Requests，无人回复可联系 Datawhale 保姆团队（`datawhalechina/DOPMC`）。

## F-018 备案与合规

- docs/zh/index.md 与 docs/en/index.md 底部含备案信息：
  - 蜀ICP备2024097797号-3
  - 川公网安备51170202000484号（含 `gonganbeian.png` 图标）
- `docs/public/gonganbeian.png` 存在。
- 部署指南含"许可证在私有化部署场景的含义"表，明确商业用途禁止。
