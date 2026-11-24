---
okf_version: "0.2"
type: bundle
title: "pydata-sphinx-theme — PyData 科学文档主题"
description: "pydata-sphinx-theme 源码级中文教程：Bootstrap 布局、toctree 导航、页内目录、主题配置、品牌化与暗色模式、搜索/版本切换、可访问性与构建性能"
tags: [sphinx, theme, pydata, bootstrap, html, documentation, dark-mode]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:45:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-repo
    resource: https://github.com/pydata/pydata-sphinx-theme
    title: pydata-sphinx-theme GitHub Repository
    author: team:pydata
    last_modified: 2026-11-20
  - id: pst-docs
    resource: https://pydata-sphinx-theme.readthedocs.io/
    title: PyData Sphinx Theme Documentation
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# pydata-sphinx-theme — PyData 科学文档主题

pydata-sphinx-theme（PST）是 PyData 社区维护的 Sphinx HTML 主题，以 Bootstrap 5 为骨架，提供顶部导航、可折叠章节树、页内目录、light/dark 切换、版本切换器、搜索即输与科学计算内容适配。NumPy、pandas、SciPy、Matplotlib、Xarray 等项目的文档均使用它。

> **核心判断**：PST 不是一层 CSS 皮肤，而是一套在 Sphinx 构建生命周期中运行的导航与布局应用——11 个事件回调、23 个可插拔组件、约 50 个主题选项，共同决定最终页面。

## 知识地图

```text
pydata-sphinx-theme/
├── concepts/        概念文档（11 篇 + 索引）
│   ├── 入门：简介、快速开始
│   ├── 架构：总览、布局与区段
│   ├── 使用：导航、页内目录、配置、品牌化、搜索/版本
│   └── 深入：内部实现、可访问性/性能/FAQ
├── examples/        实战示例（5 篇 + 索引）
│   ├── 基础站点
│   ├── 导航与布局
│   ├── 品牌化与暗色模式
│   ├── 版本切换与即时搜索
│   └── 自定义组件与静态资源
├── references/      信源与速查（3 篇 + 进程登记 + 索引）
│   ├── 源码路径映射
│   ├── 官方文档入口
│   ├── 配置项速查
│   └── seven-concepts-v 进程
└── spec/            R/I/E/V 阶段产物
    ├── facts.md     事实清单（88 条）
    ├── insights.md  洞察四元组（6 条）
    ├── patterns.md  可复用模式（3 个）
    └── review.md    对抗审查记录
```

## 推荐学习路径

### 30 分钟跑起来

1. [简介](concepts/00-introduction.md) — 它解决什么问题，和 alabaster/Furo 的差异。
2. [快速开始](concepts/01-getting-started.md) — 安装、最小 `conf.py`、构建与验收。
3. [基础站点示例](examples/01-basic-site.md) — 复制完整配置，得到三栏文档站。

### 1–2 小时掌握布局

4. [架构总览](concepts/02-architecture-overview.md) — 事件管线与模板继承链。
5. [布局与模板区段](concepts/03-layout-and-sections.md) — 九个区段、空渲染移除、自定义模板。
6. [导航与 toctree](concepts/04-navigation-and-toctree.md) — 顶部导航、章节树、折叠与缓存。
7. [页内目录与次级侧栏](concepts/05-page-toc-and-secondary-sidebar.md) — 右侧 TOC、按页配置、编辑链接。
8. [导航与布局示例](examples/02-navigation-and-layout.md) — 9 个顶层章节的实战配置。

### 2–3 小时做品牌与发布

9. [主题配置项](concepts/06-theme-options.md) — 全部选项、默认值与联动行为。
10. [品牌、样式与暗色模式](concepts/07-branding-styling-and-dark-mode.md) — 双 logo、CSS 变量、Pygments、字体。
11. [搜索、版本切换与公告](concepts/08-search-versioning-and-announcements.md) — 搜索弹窗、`switcher.json`、警告横幅。
12. [品牌化示例](examples/03-branding-and-dark-mode.md) 与 [版本切换示例](examples/04-version-switcher-and-search.md)。

### 深入与二次开发

13. [内部实现与扩展点](concepts/09-internals-and-extension-points.md) — translator、transform、i18n、扩展接入。
14. [可访问性、性能与常见问题](concepts/10-accessibility-performance-faq.md) — a11y、构建优化、排错表。
15. [自定义组件示例](examples/05-custom-components.md) — 模板覆盖、按页注入资源。

## 核心洞察

| # | 洞察 | 一句话总结 |
|---|---|---|
| 1 | 主题即应用 | 11 个事件回调横跨构建三阶段，能力边界由事件决定而非 CSS |
| 2 | 导航是构建期数据结构 | 侧栏层级与高亮在 Python 侧算好，前端只管交互 |
| 3 | 双主题是同一份 HTML 的状态 | `data-theme` + CSS 变量 + 双前缀 Pygments，无第二份页面 |
| 4 | 三套目录三套算法 | 顶部轻量遍历、侧栏祖先子树、页内 TOC 改写，各自优化 |
| 5 | 模板即组件，空渲染即移除 | 可插拔性来自渲染结果，不来自中心开关表 |
| 6 | 可访问性是构建期 + 运行期共同产物 | 语义、焦点、快捷键与 Axe 回归缺一不可 |

## 架构速查

| 要素 | 位置 | 作用 |
|---|---|---|
| Entry point | `pyproject.toml` → `sphinx.html_themes` | 让 Sphinx 发现主题 |
| 继承 | `theme.conf` → `inherit = basic` | 复用 Sphinx 页面骨架 |
| 页面骨架 | `theme/.../layout.html` | 三栏、区段 include、首屏主题脚本 |
| 导航计算 | `toctree.py` | 顶部导航、侧栏树、页内 TOC |
| 模板过滤 | `__init__.py` | 空渲染移除、CSS 去重、`DOCUMENTATION_OPTIONS` |
| 前端交互 | `assets/scripts/pydata-sphinx-theme.js` | 主题切换、搜索、版本、公告、TOC 同步、抽屉 |
| 构建产物改写 | `pygments.py`、`logo.py` | 双主题高亮 CSS、logo 复制 |

## 常见选择速查

| 需求 | 配置入口 |
|---|---|
| 顶部只显示 4 项 | `header_links_before_dropdown: 4` |
| 左侧展开到第 2 层 | `show_nav_level: 2` |
| 按 caption 折叠整段 | `show_nav_level: 0` |
| 某页去掉右侧栏 | 页面元数据 `html_theme.sidebar_secondary.remove: true` |
| 双 logo | `logo.image_light` / `logo.image_dark` |
| 品牌色 | `html[data-theme] { --pst-color-primary: light-dark(...) }` |
| 版本下拉 | `switcher.json_url` + `version-switcher` 模板 |
| 旧版警告 | `show_version_warning_banner: True` + 唯一 `preferred` |
| 搜索即输 | `search_as_you_type: True` |
| 禁用内置搜索 | `disable_search: True` |

## 与相邻知识包的关系

| 知识包 | 关系 |
|---|---|
| [Sphinx 文档工程生态](../index.md) | 父分组；PST 是 Sphinx 主题系统的生产级实现 |
| [sphinx](../sphinx/index.md) | 主题系统、事件系统、HTML builder 的底层框架 |
| [alabaster](../alabaster/index.md) | Sphinx 默认主题；极简范本，可与 PST 对照学习 |
| [sphinx-autobuild](../sphinx-autobuild/index.md) | 主题开发时的热重载工具 |
| [sphinx-docker-images](../sphinx-docker-images/index.md) | CI 中构建文档的镜像方案 |
| [Jupyter Book](../../jupyter-book/index.md) | 另一条文档工具链，主题与 MyST 生态相关 |
| [MyST](../../myst/index.md) | Markdown 解析与 Sphinx 集成 |
| [KaTeX](../../katex/index.md) | 数学排版 |

## 信任与生命周期

- **status**：`stable`。内容基于 `0.25.0dev0`（`73732a16`）源码与官方文档，关键声明见 `spec/facts.md`，审查记录见 `spec/review.md`。
- **verified**：`process:seven-concepts-v` 于 2026-11-24 完成 V 阶段审查，修正 9 处问题；进程定义见 [references/processes/seven-concepts-v.md](references/processes/seven-concepts-v.md)。
- **stale_after**：2027-11-24。上游默认值与模板结构可能随版本变化，到期后应重新核对 `theme.conf` 与 release notes。
- **未覆盖**：真实浏览器矩阵、读屏实测、全量示例构建；这些属于站点验收环节。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
spec/patterns
spec/review
log
```
