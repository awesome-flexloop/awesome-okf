---
title: 多语言文档站架构
type: concept
bundle: /datawhale/easy-vibe
description: Easy-Vibe 以 VitePress 构建支持 10 种语言的文档站，采用 locale 隔离目录、侧边栏工厂函数、顺序构建加文件锁、SEO 元数据生成与组件 i18n 扫描，保障大规模多语言内容的构建确定性。
related:
  - /datawhale/easy-vibe/concepts/vibe-coding-philosophy
  - /datawhale/easy-vibe/concepts/deployment-toolchain
sources:
  - https://github.com/datawhalechina/easy-vibe
---

## 架构总览

Easy-Vibe 是一个基于 VitePress（Vue 3）的文档站，支持 10 种语言。其多语言架构分为三层：

1. **内容层**：每种语言一个独立目录 `docs/{locale}/`，镜像相同的阶段结构。
2. **配置层**：`docs/.vitepress/config.mjs` 中的 `localeMap` 与侧边栏工厂函数，为每语言生成导航、SEO、文案。
3. **构建层**：`scripts/build-locales.mjs` 顺序构建每个 locale，合并产物，规避 VitePress alpha 的并发缺陷。

## 内容层：locale 目录镜像

`docs/` 下存在 10 个语言目录，目录名即 locale 标识：

| 目录 | 语言 |
|------|------|
| `zh-cn/` | 简体中文（主语言，内容最完整） |
| `en/` | 英语 |
| `zh-tw/` | 繁体中文 |
| `ja-jp/` | 日语 |
| `ko-kr/` | 韩语 |
| `es-es/` | 西班牙语 |
| `fr-fr/` | 法语 |
| `de-de/` | 德语 |
| `ar-sa/` | 阿拉伯语 |
| `vi-vn/` | 越南语 |

每个 locale 目录下保持一致的结构：`stage-1/`、`stage-2/`、`stage-3/`、`appendix/`、`guide/`、`vibe-stories/`（仅 zh-cn/en 完整含 4 个故事），以及各自的 `index.md` 首页和 `public/` 资源。这意味着新增一篇中文文章后，其他语言是否同步取决于社区翻译进度，构建系统不强制要求所有语言内容一致。

此外，`docs-readme/` 下有 10 份本地化 README（使用不同命名风格如 `en-US/`、`zh-CN/`），供 GitHub 仓库主页切换语言。

## 配置层：localeMap 与侧边栏工厂

### localeMap 元数据

`config.mjs` 第 48-109 行定义 `localeMap`，为每个 locale 声明四项元数据：

- `ogLocale`：Open Graph locale（如 `zh_CN`、`en_US`）
- `twitterSite`：Twitter 卡片站点句柄（均为 `@datawhale`）
- `lang`：HTML lang 属性（如 `zh-CN`、`en-US`）
- `hreflang`：SEO hreflang 值（如 `zh-CN`、`en`）

这些元数据由 `seo.mjs` 的 `createSeo` 工厂消费，生成每语言的 `<meta>` 标签、canonical 与 hreflang 链接。

### locales 配置块

`config.mjs` 的 `locales` 字段为每个 locale 单独配置：`label`（语言切换器显示名）、`lang`、`link`、`title`、`description`、`head`（SEO）、`themeConfig`（含 404 文案、outline 标签、docFooter 上一页/下一页、nav 顶部导航、sidebar 侧边栏）。

顶部导航按语言本地化，例如中文显示"零基础入门/初中级开发/高级开发/附录知识库/Vibe 故事"，英文显示"Getting Started/Full-Stack Development/Advanced Development/Appendix"。

### 侧边栏工厂函数

侧边栏不在 config 中为每语言硬编码，而是由 `docs/.vitepress/sidebars/index.mjs` 导出的工厂函数生成：

- `getStage1Sidebar(locale)` / `getStage2Sidebar(locale)` / `getStage3Sidebar(locale)`
- `getVibeStoriesSidebar(locale)` / `getVibeStoriesNavText(locale)`
- `localizeAppendixSidebar(appendixSidebarEn, locale)`

英文与韩文的 Stage 1 有专用侧边栏（`productManagerSidebarEn`、`productManagerSidebarKo`），其他语言通过工厂函数生成。这种模式让侧边栏结构复用、文案按 locale 注入，避免 10 份拷贝维护。

## 构建层：顺序构建与文件锁

### 为什么不能并发构建

`scripts/build-locales.mjs` 第 36-40 行的注释解释了关键约束：

> "VitePress 2 alpha uses one shared `.temp` directory per build. Building more than one locale at a time can remove SSR chunks before page rendering has finished, producing intermittent ERR_MODULE_NOT_FOUND failures."

即 VitePress 2 alpha 版本在并发构建时共享 `.temp` 目录，一个 locale 的构建可能在另一个 locale 页面渲染完成前删除 SSR chunk，导致间歇性 `ERR_MODULE_NOT_FOUND`。因此脚本默认 `groupSize = 1`，即一次只构建一个 locale。

### 构建流程

`npm run build` 调用 `build-locales.mjs`，流程如下：

1. **获取锁**：在 `docs/.vitepress/build-locales.lock` 以 `wx`（排他创建）模式加文件锁，写入当前 PID。若锁已存在，检查持有者 PID 是否存活；崩溃的锁会被清除，存活则等待 2 秒重试，15 分钟超时。这防止多个构建进程并发执行。
2. **清理与准备**：删除 `dist-locales/` 临时目录与最终 `dist/`，重新创建。
3. **生成 sitemap**：先调用 `generate-sitemap.mjs` 生成 `sitemap.xml` 与 `robots.txt`。
4. **逐 locale 构建**：按 `chunkLocales(locales, groupSize)` 分组（默认每组 1 个），对每组以 `--max-old-space-size=4096`（可由 `BUILD_HEAP_MB` 调整）调用 `vitepress build docs --outDir dist-locales/{group}`，并通过环境变量 `VITEPRESS_BUILD_LOCALES_ACTIVE` 告知 config.mjs 当前激活的 locale，后者据此设置 `srcExclude` 排除其他语言目录。
5. **合并产物**：每组构建完成后，把 `hashmap.json` 合并到全局 `mergedHashmap`，并把临时目录递归拷贝到最终 `dist/`。
6. **收尾**：写入合并后的 `hashmap.json`，复制 sitemap，删除临时目录，释放锁。

环境变量 `VITEPRESS_BUILD_LOCALES` 可指定只构建部分语言（如 `zh-cn,en`），用于加速预览。`--force` 参数透传给 VitePress 强制重建。

## Base 路径自适应

多语言站点需同时部署到不同平台，各平台 base 路径不同。`config.mjs` 第 21-29 行实现自适应：

```js
const isVercel = process.env.VERCEL === '1' || !!process.env.VERCEL_URL
const isEdgeOne = !!process.env.EDGEONE || process.env.EDGEONE === '1'
const base = process.env.BASE || (isVercel || isEdgeOne ? '/' : '/easy-vibe/')
```

| 环境 | base | 示例 URL |
|------|------|---------|
| Vercel | `/` | `https://xxx.vercel.app/en/stage-1/...` |
| EdgeOne | `/` | 根路径部署 |
| GitHub Pages | `/easy-vibe/` | `https://datawhalechina.github.io/easy-vibe/en/...` |
| 本地 dev | `/easy-vibe/` | `http://localhost:5173/easy-vibe/en/...` |

站点 URL 也由 `getSiteUrl()` 根据 `VERCEL_URL`/`EDGEONE_URL`/`SITE_URL` 动态确定，默认回退到 GitHub Pages 地址。首页与欢迎页所有跳转都用 `withBase()` 包裹路径，避免硬编码 base。

## 首页语言重定向

`docs/index.md` 不直接渲染内容，而是在 `<script setup>` 中：

1. 定义 21 条浏览器语言到 locale 路径的映射（含短码回退，如 `zh`→`/zh-cn/`、`en-us`→`/en/`、`zh-hk`→`/zh-tw/`）。
2. 读取 `navigator.language`，先精确匹配再按短码匹配，无匹配回退 `/zh-cn/`。
3. 检查 `localStorage` 键 `easy-vibe-welcome-seen`：首次访问跳 `/welcome?next={目标路径}`，已看过则直接替换到目标语言首页。

`docs/welcome.md` 使用 `layout: false` 渲染 `<WelcomeScreen />`——一个 SVG 路径描边动画组件，含 ocean/rainbow/sunset 三套主题循环，点击任意位置写入 `localStorage` 并跳转。

## 附录组件的 i18n

附录有 200+ 交互式 Vue 组件，组件内的文案也需要国际化。项目采用两种机制：

1. **`docs/.vitepress/theme/locales/`**：按主题分目录存放组件文案，目前有 `api-intro/`、`cloud-iam/`、`dns-https/`、`git-intro/`、`ide-intro/`、`llm-intro/`、`vlm-intro/` 等子目录，每个含 `en.js`。组件通过 composables/useI18n.js 读取当前 locale 文案。
2. **`tools/translation/check-localization.mjs`**：扫描两个 locale 下同名 Vue 组件的 `<template>` 文案，对比发现翻译缺失。`tools/translation/ko-kr/` 下有韩文术语表（glossary.md）与风格指南（style-guide.md）。

## SEO 与站点地图

- `sitemap.xml` 由 `generate-sitemap.mjs` 生成，`changefreq: weekly`，优先级：首页 1.0、语言首页 0.9、各 stage 0.8、appendix 0.7。
- Sitemap 过滤掉 `/extra/`、`/examples/`、`/project/` 等遗留路径。
- `seo.mjs` 为每语言生成 Open Graph、Twitter Card、hreflang  alternate 链接。
- `vercel.json` 配置静态资源缓存（`/assets/*` immutable 1 年）与安全头。

## 相关概念

- [Vibe Coding 理念](01-vibe-coding-philosophy.md)：多语言站点承载的教学内容与三阶段路径。
- [部署与工具链](03-deployment-toolchain.md)：多语言产物如何部署到 Vercel、GitHub Pages、魔搭 Docker，以及电子书发布流水线。
