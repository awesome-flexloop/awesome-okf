---
type: Example
title: Node.js 服务端渲染示例
description: 在 Node.js（CJS/ESM）和 Deno 中使用 renderToString 进行服务端渲染，包括 CSS/字体引入、HTML 页面组装、扩展加载（mhchem）和预渲染缓存策略。
tags: [katex, example, node, ssr, renderToString, esm, cjs, deno, server-side]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:40:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-node
    resource: /references/katex-website.md#web-node
    title: KaTeX 官网 Node.js 页面
  - id: web-api
    resource: /references/katex-website.md#web-api
    title: KaTeX 官网 API 页面
  - id: web-browser
    resource: /references/katex-website.md#web-browser
    title: KaTeX 官网 Browser 页面
---

## 安装

通过 npm、yarn 或 pnpm 安装 KaTeX[^web-node]：

```bash
npm install katex
# 或
yarn add katex
# 或
pnpm add katex
```

KaTeX v0.18.4 同时提供 CommonJS 和 ECMAScript Module 两种入口[^web-node]。

## CommonJS 用法

```javascript
const katex = require("katex");

const html = katex.renderToString("c = \\pm\\sqrt{a^2 + b^2}", {
    throwOnError: false,
    displayMode: true,
});

console.log(html);
```

`renderToString` 返回 HTML 字符串，可直接插入服务端模板。

## ECMAScript Module 用法

```javascript
import katex from "katex";

const html = katex.renderToString("e^{i\\pi} + 1 = 0", {
    displayMode: true,
    output: "htmlAndMathml",
});
```

在支持条件导出的环境中，`import katex from "katex"` 自动加载 ESM 版本；ESM 包含 ES6 语法，旧环境可能需要转译[^web-node]。

## Deno 用法

Deno 可直接从 CDN 导入 ESM 版本[^web-node]：

```javascript
import katex from "https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.mjs";

const html = katex.renderToString("\\int_0^\\infty e^{-x^2}\\,dx = \\frac{\\sqrt{\\pi}}{2}", {
    displayMode: true,
    throwOnError: false,
});
console.log(html);
```

也可通过 `deno install katex` 或 `deno install -g npm:katex` 安装[^web-node]。

## 组装完整 HTML 页面

`renderToString` 只生成数学公式的 HTML 片段。在浏览器中正确显示还需要：

1. **HTML5 doctype**（`<!DOCTYPE html>`），否则浏览器进入 quirks mode 导致渲染错误
2. **KaTeX CSS** 文件
3. **字体文件**，必须位于 CSS 同级的 `fonts/` 目录（CSS 通过相对 URL 引用字体）[^web-browser]

### 最小 HTML 模板

```javascript
const katex = require("katex");
const fs = require("fs");
const path = require("path");

function renderPage(expression, options = {}) {
    const mathHtml = katex.renderToString(expression, {
        throwOnError: false,
        ...options,
    });

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>KaTeX SSR 示例</title>
<link rel="stylesheet" href="/katex/katex.min.css">
</head>
<body>
<main>
    <div class="math-display">${mathHtml}</div>
</main>
</body>
</html>`;
}

const html = renderPage("\\frac{a}{b} + \\sqrt{c^2 + d^2}", {
    displayMode: true,
});

fs.writeFileSync("output.html", html);
```

### 静态文件服务

CSS 和字体需作为静态资源提供。以 Express 为例：

```javascript
const express = require("express");
const katex = require("katex");
const path = require("path");
const app = express();

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function renderPageHtml(mathHtml) {
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>KaTeX SSR 示例</title>
<link rel="stylesheet" href="/katex/katex.min.css">
</head>
<body>
<main>
    <div class="math-display">${mathHtml}</div>
</main>
</body>
</html>`;
}

app.use("/katex", express.static(
    path.join(__dirname, "node_modules", "katex", "dist")
));

app.get("/math", (req, res) => {
    const expr = req.query.expr || "x^2 + y^2 = z^2";
    try {
        const html = katex.renderToString(expr, {
            displayMode: true,
            throwOnError: true,
        });
        res.send(renderPageHtml(html));
    } catch (e) {
        if (e instanceof katex.ParseError) {
            res.status(400).send("公式语法错误: " + escapeHtml(e.message));
        } else {
            throw e;
        }
    }
});

app.listen(3000);
```

`node_modules/katex/dist/` 目录包含 `katex.min.css`、`katex.min.js`、`contrib/` 和 `fonts/`。

### 字体目录要求

CSS 通过相对路径引用字体，如 `url("fonts/KaTeX_AMS-Regular.woff2")`。因此 `fonts/` 必须与 `katex.min.css` 位于同级目录，移动或重命名字体会导致渲染失败[^web-browser]。

```
static/
└── katex/
    ├── katex.min.css
    ├── katex.min.js
    ├── contrib/
    │   ├── auto-render.min.js
    │   └── mhchem.min.js
    └── fonts/
        ├── KaTeX_AMS-Regular.woff2
        ├── KaTeX_Main-Regular.woff2
        └── ...
```

## 客户端无需加载 katex.js

SSR 的优势之一是客户端只需 CSS，不需要加载 KaTeX JavaScript[^web-node]：

```html
<head>
    <link rel="stylesheet" href="/katex/katex.min.css">
    <!-- 不需要 <script src="katex.min.js"></script> -->
</head>
```

预渲染的 HTML 已包含完整的数学标记，浏览器直接显示。若后续还需在客户端动态渲染公式，再引入 `katex.min.js`。

## 加载扩展（mhchem）

在 Node 中使用 mhchem 化学扩展，需在渲染前 `require` 扩展模块[^web-node]：

```javascript
const katex = require("katex");
require("katex/contrib/mhchem");

const html = katex.renderToString(
    "\\ce{2H2 + O2 -> 2H2O}",
    {throwOnError: false, displayMode: true}
);
```

mhchem 通过修改 katex 模块添加化学命令支持。其他 contrib 扩展（如 auto-render）主要面向浏览器，在 Node SSR 中通常不需要。

## 批量渲染与宏共享

同一页面的多个公式可共享 `macros` 对象实现 `\gdef` 持久化：

```javascript
const katex = require("katex");

function renderArticle(expressions) {
    const macros = {};
    return expressions.map(expr =>
        katex.renderToString(expr, {
            macros,
            throwOnError: false,
            displayMode: true,
        })
    );
}

const formulas = [
    "\\gdef\\RR{\\mathbb{R}}",
    "\\RR^n \\text{ 是实数空间}",
    "\\forall x \\in \\RR",
];

const htmlBlocks = renderArticle(formulas);
```

> **安全注意**：共享 `macros` 对象仅适用于可信内容。处理多用户输入时，必须为每条消息创建独立的 `macros` 对象。详见[安全信任示例](security-trust.md)。

## 预渲染缓存

对于静态文档或频繁访问的公式，可缓存渲染结果：

```javascript
const katex = require("katex");
const cache = new Map();

function renderCached(expression, options = {}) {
    const key = JSON.stringify({expression, options});
    if (cache.has(key)) {
        return cache.get(key);
    }
    const html = katex.renderToString(expression, {
        throwOnError: false,
        ...options,
    });
    cache.set(key, html);
    return html;
}
```

缓存键需包含影响输出的选项（`displayMode`、`output`、`macros` 等），避免不同配置命中同一缓存。

## 与静态站点生成器集成

### 通用模式

```javascript
const katex = require("katex");

function renderMarkdownWithKatex(markdown) {
    return markdown.replace(/\$\$([^$]+)\$\$/g, (_, expr) =>
        katex.renderToString(expr.trim(), {
            displayMode: true,
            throwOnError: false,
        })
    ).replace(/\$([^$]+)\$/g, (_, expr) =>
        katex.renderToString(expr.trim(), {
            throwOnError: false,
        })
    );
}
```

### String.raw 避免转义

使用 `String.raw` 模板标签可避免 JavaScript 字符串中反斜杠双重转义[^web-api]：

```javascript
const html = katex.renderToString(String.raw`\frac{a}{b} + \sqrt{c}`, {
    displayMode: true,
});
```

注意 `String.raw` 无法转义 `${` 和反引号。

## 常见问题

### CSS/字体 404

若公式显示为乱码或方框，检查：
- CSS 是否正确加载（浏览器开发者工具 Network 面板）
- `fonts/` 目录是否与 CSS 同级
- 静态文件中间件路径是否正确

### DOCTYPE 缺失

缺少 `<!DOCTYPE html>` 会导致浏览器进入 quirks mode，KaTeX 布局可能错乱。此问题在 `<iframe>` 中同样存在，iframe 不继承父文档 doctype[^web-browser]。

### ESM 导入错误

若 `import katex from "katex"` 报错，确认：
- Node.js 版本支持条件导出（Node 12+）
- `package.json` 中 `"type": "module"` 或使用 `.mjs` 扩展名
- 旧环境可回退到 `const katex = require("katex")`

## 相关内容

- [安装与运行时](../concepts/15-installation-and-runtime.md)
- [命令行接口](../concepts/16-command-line.md)
- [基础渲染示例](basic-render.md)
- [错误处理示例](error-handling.md)
- [安全信任示例](security-trust.md)

[^web-node]: 官网 Node.js 页面，https://katex.org/docs/node
[^web-api]: 官网 API 页面，https://katex.org/docs/api
[^web-browser]: 官网 Browser 页面，https://katex.org/docs/browser
