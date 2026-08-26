# KaTeX 概念文档

本目录包含 24 篇 KaTeX v0.18.4 概念文档，按"入门→架构→扩展→配置→运行时→安全→排障迁移"递进组织，融合源码架构分析与官网用户文档。

## 入门与概览

* [KaTeX 简介](/concepts/00-introduction.md) — KaTeX 是什么、核心特点、版本许可、能力边界；融合首页卖点与 Users/Versions 入口。
* [快速开始](/concepts/01-getting-started.md) — 安装、CDN、核心 API（render/renderToString）、String.raw、错误处理、持久宏说明。
* [架构总览](/concepts/02-architecture-overview.md) — 三层消化管模型（Lexer→MacroExpander→Parser）、注册表驱动设计、双输出无障碍。

## 核心架构（源码层）

* [词法分析器（Lexer）](/concepts/03-lexer.md) — 正则分词、Token 结构、catcodes、\verb 特殊处理。
* [宏展开器（MacroExpander）](/concepts/04-macro-expander.md) — Token 栈、展开循环、参数消费、Namespace 分组作用域。
* [解析器（Parser）](/concepts/05-parser.md) — 递归下降解析、atom/上下标处理、函数调度、模式切换。
* [渲染管线](/concepts/06-render-pipeline.md) — buildTree/buildHTML/buildMathML、HTML+MathML 双输出、displayWrap。
* [虚拟 DOM 树](/concepts/07-dom-tree.md) — Span/Anchor/SymbolNode/SvgNode、toNode/toMarkup 双输出。

## 扩展机制

* [函数注册表](/concepts/08-function-registry.md) — defineFunction 三要素（handler/htmlBuilder/mathmlBuilder）、FunctionSpec、参数类型。
* [宏系统](/concepts/09-macro-system.md) — 内置宏、自定义宏（settings.macros/__defineMacro）、\newcommand/\def、持久宏与 globalGroup。

## 配置与样式

* [配置系统](/concepts/10-settings-options.md) — Settings/Options 双层配置、strict/trust/globalGroup 默认值、trust context、不可变状态传递。
* [样式系统](/concepts/11-style-system.md) — 8 种 TeX 样式、sup/sub/fracNum/fracDen 转换、数学原子类、间距规则。
* [字体与度量](/concepts/12-font-metrics.md) — 字体族组织、fontMetrics、Unicode、字体格式、Browserslist、Sass 变量。

## 扩展模块

* [自动渲染扩展](/concepts/13-auto-render.md) — renderMathInElement()、默认 delimiters（8 条不含 $...$）、ignoredTags、preProcess、宏持久化。
* [贡献扩展模块](/concepts/14-contrib-extensions.md) — 官方 5 扩展（auto-render/copy-tex/mathtex-script-type/mhchem/render-a11y-string）。

## 安装运行时与 CLI

* [安装与运行时](/concepts/15-installation-and-runtime.md) — 浏览器 CDN/自托管、Node/npm/pnpm/yarn/Deno、ESM/CJS、CSS 与字体路径、Bundler、Browserslist/USE_FONT 构建。
* [命令行接口](/concepts/16-command-line.md) — CLI 输入输出、18 个选项（含 --version/--help）、与 Settings 映射、宏文件、常见用法。
* [字体与单位](/concepts/17-fonts-and-units.md) — 字体加载策略、katex-swap.css、FOUT/FOIT、TeX 单位换算、绝对长度缩放、字体自托管、1.21em 缩放。

## 安全与错误

* [安全与错误处理](/concepts/18-security-and-errors.md) — trust 控制命令、maxSize/maxExpand 三层防御、HTML 消毒白名单、ParseError、错误消息转义。

## 参考、排障与迁移

* [支持的函数](/concepts/19-supported-functions.md) — 按官网 14 个 H2 分类整理 TeX 函数（Accents/Delimiters/Environments/HTML/Layout 等）。
* [支持表](/concepts/20-support-table.md) — 字母序支持表用途、支持/不支持条目阅读方式、Detexify、源码/宏定义溯源。
* [常见问题](/concepts/21-common-issues.md) — DOCTYPE/quirks mode、智能引号、aligned/matrix 间距、align vs aligned、MathJax 命名映射、CSS 排障。
* [版本迁移](/concepts/22-migration.md) — v0.13-v0.18 迁移要点：CSS 类名前缀、__defineFunction、contrib 路径、\relax、宏参数行为。
* [生态与版本](/concepts/23-ecosystem-and-versions.md) — Users 列表、Versions 版本说明、官方扩展入口、第三方库索引（React/Vue/Angular/Android/iOS/Rust/Ruby/小程序等）。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-lexer
04-macro-expander
05-parser
06-render-pipeline
07-dom-tree
08-function-registry
09-macro-system
10-settings-options
11-style-system
12-font-metrics
13-auto-render
14-contrib-extensions
15-installation-and-runtime
16-command-line
17-fonts-and-units
18-security-and-errors
19-supported-functions
20-support-table
21-common-issues
22-migration
23-ecosystem-and-versions
```
