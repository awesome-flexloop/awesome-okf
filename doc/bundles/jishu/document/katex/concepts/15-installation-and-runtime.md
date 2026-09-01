---
type: Concept
title: 安装与运行时
description: KaTeX 的浏览器 CDN/自托管、Node.js 包管理器安装、Deno、ESM/CJS 模块格式、CSS 与字体路径、打包工具集成，以及从源码构建的 Browserslist 和字体配置。
tags: [katex, installation, runtime, cdn, node, esm, cjs, fonts, build]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T21:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T21:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-node
    resource: /references/katex-website.md#web-node
    title: KaTeX 官网 Node.js 页面
  - id: web-browser
    resource: /references/katex-website.md#web-browser
    title: KaTeX 官网 Browser 页面
  - id: web-font
    resource: /references/katex-website.md#web-font
    title: KaTeX 官网 Font 页面
---

## 概述

KaTeX 支持多种运行环境和安装方式。本文档系统说明浏览器端（CDN/自托管/打包工具）和 Node.js 端（npm/yarn/pnpm/Deno）的安装与模块格式，以及 CSS、字体路径和从源码构建的配置。

快速上手的最简安装见 [快速开始](01-getting-started.md#安装)。

## 浏览器安装

### CDN（jsDelivr）

通过 jsDelivr CDN 直接引入，推荐使用 `defer`：

```html
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css"
      crossorigin="anonymous">
<script defer
        src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"
        crossorigin="anonymous"></script>
</head>
<body>
<script defer>
document.addEventListener("DOMContentLoaded", function () {
    katex.render("E = mc^2", document.body);
});
</script>
</body>
</html>
```

关键点：

- 必须使用 `<!DOCTYPE html>`（HTML5 doctype），否则浏览器进入 quirks mode 导致渲染异常；该要求在 `<iframe>` 中同样适用（iframe 不继承父文档 doctype）
- `defer` 脚本在 `DOMContentLoaded` 事件后可用，`katex` 对象作为全局变量挂载
- CDN 链接中的版本号应与本 bundle 基准 v0.18.4 保持一致

### ESM 模块方式

支持通过 `<script type="module">` 导入 ESM 版本，并用 `nomodule` 为旧浏览器提供回退：

```html
<script type="module">
import katex from "https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.mjs";
katex.render("a^2", document.getElementById("math"));
</script>
<script nomodule defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
```

ESM 版本包含 ES6 语法，在旧环境中可能需要转译。

### AMD 模块加载器

KaTeX 也支持 AMD 模块加载器：

```javascript
require(["https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"], function (katex) {
    katex.render("a^2", document.getElementById("math"));
});
```

### 自托管

**方式一：从 GitHub Releases 下载**

从 [GitHub Releases](https://github.com/KaTeX/KaTeX/releases) 下载预构建的 `katex.tar.gz` 或 `katex.zip`（注意不是 auto-generated "Source code"），解压后包含：

- `katex.js` / `katex.min.js` / `katex.mjs`
- `katex.css` / `katex.min.css` / `katex-swap.css` / `katex-swap.min.css`
- `contrib/`（5 个扩展各含 `.js`/`.min.js`/`.mjs`）
- `fonts/`（WOFF2/WOFF/TTF 字体文件）

**方式二：通过 npm 安装**

```bash
npm install katex
```

文件位于 `node_modules/katex/dist/`。npm 包同时包含未构建的 TypeScript 源码（`src/`、`contrib/`、`katex.ts`），但这些不应直接在 HTML 中引用。

### 字体目录要求

无论 CDN 还是自托管，`fonts/` 目录必须与 CSS 文件位于**同级目录**。CSS 通过相对 URL 引用字体（如 `url("fonts/KaTeX_AMS-Regular.woff2")`），移动或重命名字体会导致渲染失败。

默认字体使用 `font-display: block` 防止 FOUT（Flash of Unstyled Text）；若需防止 FOIT（Flash of Invisible Text），可改用 `katex-swap.css` 或 `katex-swap.min.css`（使用 `font-display: swap`）。也可通过 Web Font Loader 预加载字体。

## Node.js 安装

### 包管理器安装

```bash
npm install katex
yarn add katex
pnpm add katex
```

### Deno

Deno 可直接从 CDN 导入 ESM，无需安装：

```javascript
import katex from "https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.mjs";
```

也可使用 `deno install katex` 或 `deno install -g npm:katex`。

### 模块导入

KaTeX 作为 CommonJS 模块导出，可通过 `require` 导入；同时条件性导出 ESM，可通过 `import` 导入：

```javascript
// CommonJS
const katex = require('katex');

// ESM
import katex from 'katex';
```

### CSS 与字体要求

在 Node.js 中通过 `renderToString` 生成的 HTML **仍需**在最终页面中链接 CSS 文件、提供字体文件并使用 HTML5 doctype。客户端不需要再包含 katex.js，只需 CSS 和字体即可正确显示。

### 扩展加载

以 mhchem 为例，扩展通过修改 katex 模块添加功能，Node 中需在渲染前 require：

```javascript
require('katex');
require('katex/contrib/mhchem');
```

## 打包工具集成

使用 webpack、rollup.js 等打包工具时，通过 npm 安装并导入，**必须**同时打包样式表或手动引入 CSS：

```javascript
import katex from 'katex';
import 'katex/dist/katex.min.css';
```

打包工具不会自动处理 `fonts/` 目录的部署，需确保构建输出中字体文件位于 CSS 同级路径，或通过打包工具的 file-loader/asset 模块配置正确解析字体 URL。

## 从源码构建

### 环境要求

从源码构建需要：

- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) 22.13 或更高版本
- 启用 [corepack](https://nodejs.org/api/corepack.html)（`corepack enable`）
- pnpm（项目使用 pnpm@11.4.0，corepack 会自动切换）

### 构建步骤

```bash
git clone https://github.com/KaTeX/KaTeX.git
cd KaTeX
corepack enable
pnpm install
pnpm build
```

### Browserslist 目标环境

构建时根据 [Browserslist config](https://github.com/browserslist/browserslist) 自动转译代码，并只包含目标环境所需的字体格式。可通过 `BROWSERSLIST` 环境变量指定目标环境：

```bash
BROWSERSLIST="Chrome 68" pnpm build
```

### 字体格式控制

KaTeX 提供三种字体格式：

| 格式 | 用途 |
|------|------|
| WOFF2 | 现代浏览器，体积最小 |
| WOFF | 现代浏览器广泛支持 |
| TTF | 非常旧的浏览器和本地安装 |

可通过 `USE_(FONT NAME)` 环境变量设为 `"true"` 或 `"false"` 强制包含或排除某种字体格式：

```bash
USE_TTF=false USE_WOFF=false USE_WOFF2=true pnpm build
```

自定义字体族包括 `KaTeX_AMS`、`KaTeX_Caligraphic`、`KaTeX_Fraktur`、`KaTeX_Main`、`KaTeX_Math`、`KaTeX_SansSerif`、`KaTeX_Script`、`KaTeX_Size1-4`、`KaTeX_Typewriter`。

### Sass 变量覆盖

使用 Sass 时可通过 `@use ... with (...)` 覆盖字体格式和字体目录变量：

```scss
@use 'node_modules/katex/src/styles/katex' with (
    $use-ttf: false,
    $use-woff: false,
    $use-woff2: true,
    $font-folder: "path/to/fonts"
);
```

默认构建期望字体位于 `katex.min.css` 同级的 `fonts` 目录。也可修改 `src/styles/fonts.scss` 中的字体文件夹值，或通过 webpack 配置中的 `sassVariables` 注入 `$font-folder`。修改字体相关配置后需重新运行 `pnpm build`。

## 模块格式总结

| 环境 | 引入方式 | 说明 |
|------|---------|------|
| 浏览器（最简） | `<script src="katex.min.js">` | 全局 `katex` 变量 |
| 浏览器（CDN） | `<script defer src="...katex.min.js">` | 推荐，DOMContentLoaded 后可用 |
| 浏览器（ESM） | `<script type="module"> import katex from '...katex.mjs'` | 现代浏览器 |
| 浏览器（AMD） | `require([...], katex => {})` | RequireJS 等 |
| Node.js（CJS） | `const katex = require('katex')` | 传统 Node |
| Node.js（ESM） | `import katex from 'katex'` | 现代 Node/打包工具 |
| Deno | `import katex from 'https://.../katex.mjs'` | 直接 CDN 导入 |

## 相关概念

- [快速开始](01-getting-started.md)
- [KaTeX 简介](00-introduction.md)
- [命令行接口](16-command-line.md)
- [字体与单位](17-fonts-and-units.md)
- [自动渲染扩展](13-auto-render.md)
