---
title: 多语言文档架构
type: concept
bundle: /datawhale/vibe-vibe
description: Vibe Vibe 以 VitePress 1.6.4 稳定版构建中英文双语文档站，采用内容层/配置层/重定向层三层架构，直接利用 VitePress 原生多语言能力，无需自定义构建脚本，并通过 100+ Vue 交互组件增强教学体验。
related:
  - /datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy
  - /datawhale/vibe-vibe/concepts/02-basic-getting-started
sources:
  - https://github.com/datawhalechina/vibe-vibe
---

## 架构总览

Vibe Vibe 是一个基于 VitePress 1.6.4（Vue 3.5.25）的静态文档站，支持简体中文与英语两种语言。与同组织的 easy-vibe（10 语言、自定义多语言构建脚本）不同，vibe-vibe 的多语言架构极为简洁，直接依赖 VitePress 稳定版的原生 `locales` 配置。

架构分为三层：

1. **内容层**：中文内容位于 `docs/` 根目录，英文内容镜像到 `docs/en/`
2. **配置层**：`docs/.vitepress/config.mts` 中的 `locales` 块为两种语言各自配置导航与文案
3. **重定向层**：`docs/index.md` 根据浏览器语言自动跳转到 `/zh/` 或 `/en/`

## 内容层：目录镜像

### 中文内容（root locale）

中文内容直接放在 `docs/` 根目录下，四大板块各占一个目录：

```
docs/
├── Basic/          # 基础篇（v2，7 章）
├── Basic-old/      # 旧版基础篇（保留）
├── Advanced/       # 进阶篇（16 章）
├── Articles/       # 优质文章篇（6 分类）
├── Practice/       # 实践篇
└── deployment/     # 私有化部署指南
```

此外，`docs/zh/index.md` 作为 `/zh/` 路径的中文首页入口存在，内容与根首页一致。

### 英文内容（en locale）

英文内容完整镜像到 `docs/en/` 目录：

```
docs/en/
├── Basic/          # 基础篇英文版（00-preface ~ 06-launch + appendix + epilogue + next-part）
├── Advanced/       # 进阶篇英文版（01-16 章，含完整小节文件）
├── Articles/       # 优质文章篇英文版（01-06 分类，含翻译文章）
└── Practice/       # 实践篇英文版
```

Glob 结果确认 `docs/en/` 下有 200+ 个 Markdown 文件，目录结构与中文版一一对应。英文内容不仅是界面文案翻译，文章内容也完整翻译（如 Articles 下的英文文章原文）。

### 静态资源

`docs/public/` 目录存放全站共享的静态资源：

- `logo.png`、`favicon.ico`：站点图标
- `llms.txt`：AI 助手导航文件
- `images/`：教程截图，按板块分目录（`Advanced/`、`Basic/` 等）
- `giscus/`：评论系统主题 CSS（深色/浅色）
- `components/`：静态 HTML 演示组件
- `gonganbeian.png`：备案图标
- `humans.txt`

## 配置层：locales 块

`docs/.vitepress/config.mts` 第 71-248 行定义 `locales` 配置，包含两个 locale：

### root（简体中文）

```typescript
root: {
  label: '简体中文',
  lang: 'zh-CN',
  title: 'VibeVibe',
  description: 'Vibe Coding 全栈实战教程 - ...',
  themeConfig: {
    nav: [ /* 首页、基础篇、进阶篇、优质文章篇、实践案例篇、LocaleSwitch */ ],
    docFooter: { prev: '上一篇', next: '下一篇' },
    outline: { label: '页面导航', level: [2, 3] },
    lastUpdated: { text: '最后更新于', formatOptions: { dateStyle: 'short', timeStyle: 'short' } },
    // ...
  }
}
```

### en（English）

```typescript
en: {
  label: 'English',
  lang: 'en-US',
  title: 'VibeVibe',
  description: 'Vibe Coding Full-Stack Tutorial - ...',
  link: '/en/',
  themeConfig: {
    nav: [ /* Home, Fundamentals, Advanced, Articles, Practice, LocaleSwitch */ ],
    docFooter: { prev: 'Previous', next: 'Next' },
    outline: { label: 'On this page', level: [2, 3] },
    // ...
  }
}
```

两个 locale 的关键差异：

| 配置项 | root（中文） | en（英文） |
|-------|-------------|-----------|
| `link` | 无（根路径） | `/en/` |
| 导航文案 | 简体中文 | English |
| 章节链接 | `/Basic/`、`/Advanced/` 等 | `/en/Basic/`、`/en/Advanced/` 等 |
| docFooter | 上一篇/下一篇 | Previous/Next |
| outline 标签 | 页面导航 | On this page |

两个 locale 的导航结构完全对称，都包含首页、四大板块下拉菜单和 `LocaleSwitch` 组件。导航项不仅是链接，还包含完整的章节下拉列表（如基础篇下拉列出 0-6 章和附录）。

### LocaleSwitch 组件

顶部导航中的 `{ component: 'LocaleSwitch' }` 是一个自定义 Vue 组件（`docs/.vitepress/theme/components/LocaleSwitch.vue`），提供手动语言切换入口，补充自动重定向的不足。

## 重定向层：首页语言检测

`docs/index.md` 使用 `layout: home`，同时包含一段 `<script setup>` 在客户端执行语言检测：

```typescript
function resolveLocaleEntry() {
  if (typeof navigator === 'undefined') return '/zh/'
  const languages = Array.isArray(navigator.languages) && navigator.languages.length > 0
    ? navigator.languages
    : [navigator.language]
  return languages.some((language) => language?.toLowerCase().startsWith('zh'))
    ? '/zh/'
    : '/en/'
}

onMounted(() => {
  if (typeof window !== 'undefined' && window.location.pathname === '/') {
    window.location.replace(resolveLocaleEntry())
  }
})
```

逻辑简洁明了：

1. 读取 `navigator.languages`（浏览器偏好语言列表）
2. 若任一语言以 `zh` 开头 → 跳转 `/zh/`（中文）
3. 否则 → 跳转 `/en/`（英文）
4. 仅在根路径 `/` 时触发，不影响直接访问子页面

与 easy-vibe 的 21 条语言映射表相比，vibe-vibe 只需 zh/非 zh 二选一，因为只支持两种语言。

## 构建系统

### 为什么不需要自定义构建脚本

easy-vibe 使用 VitePress 2.0.0-alpha.16，该版本在并发构建多语言时共享 `.temp` 目录会导致 `ERR_MODULE_NOT_FOUND`，因此需要 `build-locales.mjs` 顺序构建 + 文件锁。

vibe-vibe 使用 VitePress **1.6.4 稳定版**，原生多语言构建没有并发问题。因此 `package.json` 的构建脚本极简：

```json
{
  "scripts": {
    "dev": "vitepress dev docs",
    "build": "vitepress build docs",
    "preview": "vitepress preview docs",
    "postinstall": "patch-package"
  }
}
```

`pnpm build` 一条命令直接完成中英文双语构建，产物输出到 `docs/.vitepress/dist`。无需顺序构建、文件锁、临时目录合并、hashmap 合并等额外编排。

### 包管理器

项目使用 pnpm 10.21.0（`packageManager` 字段锁定），提供 `pnpm-lock.yaml`。`postinstall` 执行 `patch-package` 对依赖打补丁。

## 交互组件体系

多语言站点的教学内容不仅是文字，还包含 100+ 个 Vue 交互组件，位于 `docs/.vitepress/theme/components/`。组件按章节编号前缀命名，在 Markdown 中以 `<ComponentName />` 标签直接引用。

### 组件分布

| 前缀 | 章节 | 组件示例 |
|------|------|---------|
| `01-0-*` ~ `01-1-*` | 第 1 章 | TerminalSimulator、AIToolSelector、FileSystemTree、PackageEcosystem |
| `02-1-*` ~ `02-5-*` | 第 2 章 | TokenCalculator、WorkflowStepper、MCPDecisionTree、PromptOptimizer |
| `03-1-*` ~ `03-4-*` | 第 3 章 | SoulThreeQuestions、GoodBadPRDCompare、PRDToCodeFlow |
| `04-0-*` ~ `04-7-*` | 第 4 章 | CompileVsInterpret、DataModelER、HttpRequestFlow、ProxyArchitecture |
| `05-1-*` ~ `05-5-*` | 第 5 章 | DesignToolWorkflow、ComponentLibraryDecisionTree、StyleShowcase |
| `06-1-*` ~ `06-3-*` | 第 6 章 | StorageEvolution、DatabaseVisualizer、CRUDVisualizer |
| `07-*` ~ `16-*` | 进阶篇各章 | AuthFlow、SecurityBoundary、TestPyramid、GitFlowDiagram、DNSResolution、FirewallRuleBuilder、SEOChecklist 等 |
| 通用 | — | BasicEditionUpdateBox、LocaleSwitch |

### 组件基础设施

- `composables/useAnimation.ts`：动画复用逻辑
- `styles/variables.css`：CSS 变量定义
- `types/components.ts`：组件类型定义
- `COMPONENT_GUIDE.md`：组件开发指南
- `index.ts`：主题入口，注册组件

这些组件把抽象概念（DNS 解析过程、Git 分支工作流、CORS 机制、测试金字塔）做成可点击的可视化演示，且中英文版本共享同一套组件——组件内文案通过 Markdown 内容传递，无需额外 i18n 系统。

## SEO 与站点增强

config.mts 实现了一套自动化的 SEO 增强系统，位于 `docs/.vitepress/modules/`：

| 模块 | 功能 |
|------|------|
| `utils.ts` | frontmatter 解析、阅读时间估算、URL 路径生成、JSON-LD 安全序列化 |
| `seo.ts` | 面包屑结构化数据（`buildBreadcrumbList`） |
| `faq.ts` | FAQ Schema 构建（`buildFAQSchema` + `tutorialFAQs`） |
| `feed.ts` | robots.txt 生成、RSS XML 构建 |
| `sitemap.ts` | 图片 sitemap 生成 |
| `defaults.ts` | 自动描述生成、难度推断、相关页推荐、最后更新提示 |

`transformHead` 钩子为每页动态生成：title、description、OG 标签、面包屑 JSON-LD、自动关键词、文章分类（基础篇/进阶篇/实践篇/优质文章）。

站点还配置了：PWA 支持（vite-plugin-pwa）、Mermaid 图表、时间线插件、任务列表、Giscus 评论、Umami 统计、数学公式（MathJax）、图片缩放（medium-zoom）、关系图可视化（Cytoscape）。

## 部署

多语言静态站点的部署非常简单，因为产物是纯静态文件：

- **Docker**：多阶段构建（node:24-alpine 构建 + nginx:alpine 服务），端口 80
- **docker-compose**：端口映射 `1024:80`，含健康检查，`docker compose up -d --build` 一键启动
- **EdgeOne Pages**：腾讯云边缘平台，GitHub 仓库自动同步构建
- **静态文件**：`dist/` 目录可部署到 Nginx/Apache/IIS/OSS/S3 任意静态托管
- **离线运行**：完全静态，无需数据库或外部 API（Giscus 评论除外）

站点 URL 由 `resolveSiteUrl()` 按环境变量优先级自动确定：`SITE_URL` > `EDGEONE_PAGES_URL` > `DEPLOY_URL` > `URL` > `VERCEL_URL` > `https://www.vibevibe.cn`。

## 与 easy-vibe 多语言架构的对比

| 维度 | Vibe Vibe | Easy-Vibe |
|------|-----------|-----------|
| 语言数 | 2（中英） | 10 |
| VitePress 版本 | 1.6.4 稳定版 | 2.0.0-alpha.16 |
| 构建脚本 | 原生 `vitepress build` | 自定义 `build-locales.mjs`（顺序构建+文件锁） |
| 首页重定向 | 10 行脚本（zh/非 zh） | 21 条语言映射 + 欢迎页 |
| 侧边栏 | 手动配置 nav | 工厂函数 `getStageXSidebar(locale)` |
| 组件 i18n | 不需要（文案在 Markdown） | `theme/locales/` + 翻译缺失扫描工具 |
| 电子书 | 无 | PDF（XeLaTeX）+ EPUB 多语言发布 |
| Base 路径 | 根路径部署 | 自适应（Vercel/EdgeOne `/`，GitHub Pages `/easy-vibe/`） |

两者的差异反映了不同的定位选择：vibe-vibe 聚焦中文社区的内容深度与教学体验，用稳定版框架降低维护成本；easy-vibe 追求全球多语言覆盖，承担 alpha 框架的工程复杂度。

## 相关概念

- [Vibe 开发理念](/datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy.md)：多语言站点承载的教学内容与 AI 助教路由设计。
- [Basic 入门教学设计](/datawhale/vibe-vibe/concepts/02-basic-getting-started.md)：基础篇的单一连续案例与 7 里程碑结构。
