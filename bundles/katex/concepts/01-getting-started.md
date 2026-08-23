---
type: Concept
title: 快速开始
description: KaTeX 的安装方式、CDN 引入、核心 API 使用方法、String.raw 技巧、错误处理和持久宏说明。
tags: [katex, getting-started, installation, api]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T21:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T21:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-api
    resource: /references/katex-website.md#web-api
    title: KaTeX 官网 API 页面
  - id: web-browser
    resource: /references/katex-website.md#web-browser
    title: KaTeX 官网 Browser 页面
  - id: web-node
    resource: /references/katex-website.md#web-node
    title: KaTeX 官网 Node.js 页面
---

## 安装

### 使用包管理器（Node.js / 打包工具）

```bash
npm install katex
# 或
yarn add katex
# 或
pnpm add katex
```

安装后需要同时引入 KaTeX 的 JS 和 CSS：

```javascript
import katex from 'katex';
import 'katex/dist/katex.min.css';
```

CommonJS 环境使用 `require`：

```javascript
const katex = require('katex');
```

Deno 可直接从 CDN 导入 ESM：

```javascript
import katex from "https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.mjs";
```

> 完整安装说明（自托管、Browserslist 构建、字体目录配置、从源码构建等）见 [安装与运行时](/concepts/15-installation-and-runtime.md)。

### 使用 CDN（浏览器直接引入）

```html
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css"
      crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"
        crossorigin="anonymous"></script>
</head>
<body>
<p>行内公式：<span id="math"></span></p>
<script defer>
document.addEventListener("DOMContentLoaded", function () {
    katex.render("c = \\pm\\sqrt{a^2 + b^2}", document.getElementById("math"));
});
</script>
</body>
</html>
```

> 生产环境建议从 [jsDelivr](https://www.jsdelivr.com/package/npm/katex) 获取对应版本的 SRI integrity 哈希并添加到 `<link>`/`<script>` 标签中。

注意：

- 必须使用 `<!DOCTYPE html>`（HTML5 doctype），否则浏览器进入 quirks mode 会导致渲染异常
- 脚本默认使用 `defer` 延迟加载，`katex` 对象在 `DOMContentLoaded` 事件后可用
- `fonts/` 目录必须与 CSS 文件位于同级目录（CSS 通过相对 URL 引用字体），移动字体会导致渲染失败

### 自动渲染扩展

如果希望页面中的数学分隔符自动被渲染为公式，需要额外引入 auto-render 扩展：

```html
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body);"></script>
```

auto-render 的默认分隔符和配置见 [自动渲染扩展](/concepts/13-auto-render.md)。

## 核心 API

### katex.render(expression, element, options?)

将 LaTeX 表达式渲染到指定的 DOM 元素中。

```javascript
katex.render("c = \\pm\\sqrt{a^2 + b^2}", element, {
    displayMode: false
});
```

**参数**：
- `expression: string` — LaTeX 数学表达式字符串
- `element: HTMLElement` — 渲染结果将作为子节点添加到此元素
- `options?: SettingsOptions` — 可选配置对象，详见 [配置系统](/concepts/10-settings-options.md)

### katex.renderToString(expression, options?)

将 LaTeX 表达式渲染为 HTML 字符串，适用于服务端渲染（SSR）。

```javascript
const html = katex.renderToString("\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}", {
    displayMode: true,
    throwOnError: false
});
```

**返回值**：`string` — 可直接插入页面的 HTML 字符串。

> Node.js 中 `renderToString` 生成的 HTML 仍需链接 CSS 文件、提供字体文件并使用 HTML5 doctype；客户端不需要再包含 katex.js。

### 使用 String.raw 避免反斜杠转义

JavaScript 字符串中反斜杠需要双重转义（`\\frac`），使用 `String.raw` 模板标签可直接书写 LaTeX 源码：

```javascript
katex.render(String.raw`\frac{a}{b}`, element);
```

注意：`String.raw` 无法转义 `${` 和反引号本身，包含这些字符时仍需手动处理。

### 内部 API

以下 API 以下划线前缀标记为内部使用，不推荐在生产中依赖，结构可能在版本间变更：

- `katex.__parse(expression, options?)` — 返回内部解析树（`AnyParseNode[]`）
- `katex.__renderToDomTree(expression, options?)` — 返回含 HTML+MathML 的虚拟 DOM 树
- `katex.__renderToHTMLTree(expression, options?)` — 返回仅含 HTML 的虚拟 DOM 树
- `katex.__defineFunction` / `__defineMacro` / `__defineSymbol` — 扩展 API

## 第一个完整示例

**浏览器端**：

```html
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
</head>
<body>
<p>行内公式：<span id="inline-math"></span></p>
<div id="display-math"></div>
<script defer>
document.addEventListener("DOMContentLoaded", function () {
    katex.render("E = mc^2", document.getElementById("inline-math"));
    katex.render(String.raw`\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}`,
                 document.getElementById("display-math"), { displayMode: true });
});
</script>
</body>
</html>
```

**Node.js 服务端渲染**：

```javascript
const katex = require('katex');

const html = katex.renderToString("a^2 + b^2 = c^2");
console.log(html);
```

## 错误处理

KaTeX 解析失败时抛出 `katex.ParseError`。可用 `instanceof` 判断是否为 KaTeX 解析错误：

```javascript
try {
    katex.render("\\invalidcommand", element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        console.error("LaTeX 解析错误:", e.message);
    } else {
        throw e;
    }
}
```

设置 `throwOnError: false` 可将无效输入以 LaTeX 源码形式渲染（hover 文本显示错误消息），颜色由 `errorColor` 指定：

```javascript
katex.render("\\invalid", element, {
    throwOnError: false,
    errorColor: "#cc0000"
});
```

> **安全提示**：KaTeX 抛出的错误消息可能包含未转义的 LaTeX 源码。将错误消息渲染到 HTML 前，必须将 `&`、`<`、`>` 替换为 `&amp;`、`&lt;`、`&gt;`，否则可能导致 `<script>` 注入攻击。详见 [安全与错误处理](/concepts/18-security-and-errors.md)。

## 持久宏（Persistent Macros）

KaTeX 的 `render`/`renderToString` 表面上是无状态函数，但通过传入共享的 `macros` 对象可实现宏持久化。当 LaTeX 代码使用 `\gdef`、`\global\let`（或 `globalGroup` 选项下的 `\def`/`\newcommand`/`\let`）时，KaTeX 会将宏定义插入该对象，使后续调用复用同一宏：

```javascript
const macros = {};

katex.render("\\gdef\\RR{\\mathbb{R}}", element1, { macros });
katex.render("\\RR^n", element2, { macros });
```

**安全警告**：持久宏可改变 KaTeX 行为（如重定义标准命令），应仅在共同信任的多个元素间使用。处理不可信输入时，必须为每条消息/每个用户创建独立的 `macros` 对象，不应跨多用户消息共享。详见 [宏系统](/concepts/09-macro-system.md) 和 [安全与错误处理](/concepts/18-security-and-errors.md)。

## 常用配置选项

完整选项说明见 [配置系统](/concepts/10-settings-options.md)。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `displayMode` | `boolean` | `false` | 显示模式（块级居中，大号积分/求和符号） |
| `output` | `string` | `"htmlAndMathml"` | 输出格式：`"html"`、`"mathml"`、`"htmlAndMathml"` |
| `throwOnError` | `boolean` | `true` | 解析错误时是否抛出异常 |
| `errorColor` | `string` | `"#cc0000"` | throwOnError=false 时错误文本颜色 |
| `macros` | `object` | `{}` | 自定义宏映射 |
| `strict` | `boolean\|string\|function` | `"warn"` | 严格模式：`"warn"` 输出警告、`"error"` 抛异常、`"ignore"`/`false` 忽略 |
| `trust` | `boolean\|function` | `false` | 是否信任输入（控制 `\url`、`\href` 等） |
| `maxSize` | `number` | `Infinity` | 用户指定尺寸上限（em），防止超大元素 |
| `maxExpand` | `number` | `1000` | 宏展开次数上限，防止无限宏循环 |
| `globalGroup` | `boolean` | `false` | 是否在全局组中运行（使顶层 `\def` 写入 macros 对象） |

## 相关概念

- [KaTeX 简介](/concepts/00-introduction.md)
- [安装与运行时](/concepts/15-installation-and-runtime.md)
- [配置系统](/concepts/10-settings-options.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [命令行接口](/concepts/16-command-line.md)
- [基础渲染示例](/examples/basic-render.md)
- [错误处理示例](/examples/error-handling.md)
