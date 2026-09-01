---
type: Concept
title: 字体与单位
description: "KaTeX 字体加载策略（font-display: block/swap、katex-swap.css、Web Font Loader 预加载）、TeX 单位换算与绝对长度缩放、字体自托管与目录要求，面向集成 KaTeX 的开发者。"
tags: [katex, fonts, units, font-display, fout, foit, self-hosting, sass]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-font
    resource: /references/katex-website.md#web-font
    title: KaTeX 官网 Font 页面
  - id: web-browser
    resource: /references/katex-website.md#web-browser
    title: KaTeX 官网 Browser 页面
---

## 概述

KaTeX 使用自包含的 Web 字体渲染数学公式，不依赖系统字体。本文档面向集成 KaTeX 的开发者，说明字体加载策略、`katex-swap.css` 的取舍、TeX 单位换算、绝对长度缩放以及字体自托管要求。

字体内部架构（fontMetrics 度量数据、Unicode 支持、度量提取工具链）见 [字体与度量](12-font-metrics.md)；样式系统的 8 种 TeX Style 与字号倍数见 [样式系统](11-style-system.md)。

## 字体加载策略

### font-display: block（默认）

KaTeX 默认样式表 `katex.css`/`katex.min.css` 使用 `font-display: block` 声明字体[^web-browser]。这意味着：

- 字体加载期间，浏览器使用**不可见的占位字体**渲染文本（FOIT，Flash of Invisible Text）
- 字体加载完成后立即替换为正确字形
- 优点：避免公式先以回退字体显示再跳动（无布局抖动）
- 缺点：慢网络下公式区域短时间不可见

### font-display: swap（katex-swap.css）

KaTeX 提供替代样式表 `katex-swap.css`/`katex-swap.min.css`，使用 `font-display: swap`[^web-browser]：

- 字体加载期间，浏览器立即使用**回退字体**显示文本（FOUT，Flash of Unstyled Text）
- 字体加载完成后替换为 KaTeX 字体
- 优点：内容立即可见，不会出现空白
- 缺点：字体加载前后公式宽度可能变化，产生布局抖动

选择建议：

| 场景 | 推荐样式 |
|------|---------|
| 数学公式是核心内容、要求无跳动 | `katex.min.css`（block，默认） |
| 内容优先可见、可容忍短暂重排 | `katex-swap.min.css`（swap） |
| 慢网络或弱网环境 | `katex-swap.min.css`（避免白屏） |

### Web Font Loader 预加载

可通过 [Web Font Loader](https://github.com/typekit/webfontloader) 预加载 KaTeX 字体族，在字体就绪前隐藏公式或显示加载状态[^web-browser]。KaTeX 使用的自定义字体族包括：

| 字体族 | 字重/样式 |
|--------|----------|
| `KaTeX_AMS` | n4 |
| `KaTeX_Caligraphic` | n4, n7 |
| `KaTeX_Fraktur` | n4, n7 |
| `KaTeX_Main` | n4, n7, i4, i7 |
| `KaTeX_Math` | i4, i7 |
| `KaTeX_SansSerif` | n4, n7, i4 |
| `KaTeX_Script` | n4 |
| `KaTeX_Size1`~`KaTeX_Size4` | n4 |
| `KaTeX_Typewriter` | n4 |

## 渲染缩放

KaTeX 默认以周围上下文字体大小的 **1.21 倍** 渲染数学公式，使上下标更易读[^web-font]。可通过 CSS 覆盖：

```css
.katex { font-size: 1.1em; }
```

这一缩放作用于 `.katex` 根元素，内部 Style 的 script/scriptscript 倍数（0.7/0.5）在此基础上二次缩放。

## TeX 单位与绝对长度

### 支持的单位

KaTeX 支持所有 TeX 单位，包括相对单位和绝对单位[^web-font]：

| 类别 | 单位 | 说明 |
|------|------|------|
| 相对 | `em` | 相对于当前字号 |
| 相对 | `ex` | 相对于当前字体的 x-height |
| 相对 | `mu` | 数学单位，1mu = 1/18 em |
| 绝对 | `pt` | 点，1pt = 1/72.27in（TeX 基准） |
| 绝对 | `pc` | 派卡，1pc = 12pt |
| 绝对 | `in` | 英寸 |
| 绝对 | `cm` | 厘米，1in = 2.54cm |
| 绝对 | `mm` | 毫米 |
| 绝对 | `bp` | 大点，1bp = 1/72in |
| 绝对 | `dd` | Didot 点 |
| 绝对 | `cc` | Cicero，1cc = 12dd |
| 绝对 | `sp` | 缩定点，65536sp = 1pt |

### 绝对长度的缩放基准

所有绝对单位（cm、in、pt 等）相对于 **默认 TeX 字号 10pt** 统一缩放，而非浏览器的物理单位[^web-font]。例如：

```
\kern1cm  ≡  \kern2.845275em
```

这意味着 KaTeX 中的 `1cm` 是相对于 10pt TeX 字号的逻辑厘米，而非屏幕物理厘米。由于浏览器默认字号通常为 16px（大于 10pt），KaTeX 中的 `1cm` 视觉上会比浏览器原生 CSS 的 `1cm` 更大。相对单位和绝对单位均遵循这一统一缩放规则。

### 常用换算

| TeX 表达式 | 等效 em（10pt 基准） |
|-----------|---------------------|
| `1mu` | 0.05556em（1/18em） |
| `1pt` | 0.1em |
| `1cm` | 2.845275em |
| `1in` | 7.227em |
| `\thinspace`（`\,`） | 0.16667em（3mu） |
| `\medspace`（`\:`） | 0.22222em（4mu） |
| `\thickspace`（`\;`） | 0.27778em（5mu） |

> **注**：`1cm = 2.845275em` 为官网 Font 页面给出的唯一显式换算值[^web-font]；`1pt = 0.1em`、`1in = 7.227em` 由 TeX 标准换算（1em = 10pt、1in = 72.27pt）推导。mu 与间距命令的换算为 TeX 标准定义。

## 字体自托管

### 目录结构要求

自托管时，`fonts/` 目录必须与 CSS 文件位于**同级目录**[^web-browser]。CSS 通过相对 URL 引用字体：

```css
/* katex.min.css 中的 @font-face 声明 */
src: url("fonts/KaTeX_AMS-Regular.woff2") format("woff2");
```

正确的目录结构：

```
your-site/
├── katex.min.css
└── fonts/
    ├── KaTeX_AMS-Regular.woff2
    ├── KaTeX_Main-Regular.woff2
    ├── KaTeX_Math-Italic.woff2
    └── ...
```

移动或重命名 `fonts/` 目录会导致字体加载失败、公式回退到系统字体。

### 获取预构建文件

有两种方式获取自托管文件[^web-browser]：

1. **GitHub Releases**：下载 `katex.tar.gz` 或 `katex.zip`（注意不是 auto-generated "Source code"），解压后包含：
   - `katex.js`/`katex.min.js`/`katex.mjs`
   - `katex.css`/`katex.min.css`/`katex-swap.css`/`katex-swap.min.css`
   - `contrib/`（5 个扩展各含 `.js`/`.min.js`/`.mjs`）
   - `fonts/`（WOFF2/WOFF/TTF）

2. **npm 包**：通过 `npm install katex` 安装，文件位于 `node_modules/katex/dist/`。npm 包同时包含未构建的 TypeScript 源码（`src/`、`contrib/`、`katex.ts`），但这些不应直接在 HTML 中引用。

### 从源码构建

从源码构建需要 Git、Node.js 22.13+、启用 corepack[^web-font]：

```bash
corepack enable
pnpm install
pnpm build
```

构建时根据 Browserslist config 自动转译代码并只包含目标环境所需字体。可通过环境变量控制：

```bash
# 指定目标浏览器环境
BROWSERSLIST="Chrome 68" pnpm build

# 强制包含/排除字体格式
USE_WOFF2=true USE_TTF=false pnpm build
```

字体格式、字体目录的 Sass 变量配置详见 [字体与度量](12-font-metrics.md#字体格式与构建配置用户视角)。

## 相关概念

- [字体与度量](12-font-metrics.md) — 字体族、fontMetrics 内部架构、Unicode 支持、Sass/Browserslist 构建配置
- [样式系统](11-style-system.md) — 8 种 TeX Style、字号倍数、数学原子类
- [安装与运行时](15-installation-and-runtime.md) — CDN、Node、打包工具集成
- [配置系统](10-settings-options.md) — minRuleThickness 等影响渲染的选项

[^web-font]: 官网 Font 页面，https://katex.org/docs/font
[^web-browser]: 官网 Browser 页面，https://katex.org/docs/browser
