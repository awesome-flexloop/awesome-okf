---
type: Concept
title: 快速开始
description: KaTeX 的安装方式、CDN 引入、基本 API 使用方法和常用配置选项。
tags: [katex, getting-started, installation, api]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 安装

### 使用 npm/pnpm/yarn

```bash
npm install katex
# 或
pnpm add katex
```

安装后需要同时引入 KaTeX 的 JS 和 CSS：

```javascript
import katex from 'katex';
import 'katex/dist/katex.min.css';
```

### 使用 CDN（浏览器直接引入）

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
```

### 自动渲染扩展

如果希望页面中的 `$...$` 或 `$$...$$` 自动被渲染为公式，需要额外引入 auto-render 扩展：

```html
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body);"></script>
```

## 核心 API

### katex.render(expression, element, options?)

将 LaTeX 表达式渲染到指定的 DOM 元素中。

```javascript
katex.render("c = \\pm\\sqrt{a^2 + b^2}", element, {
    displayMode: false  // true 为显示模式（居中、大符号），false 为行内模式
});
```

**参数**：
- `expression: string` — LaTeX 数学表达式字符串
- `element: HTMLElement` — 渲染结果将作为子节点添加到此元素
- `options?: SettingsOptions` — 可选配置对象

### katex.renderToString(expression, options?)

将 LaTeX 表达式渲染为 HTML 字符串，适用于服务端渲染（SSR）。

```javascript
const html = katex.renderToString("\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}", {
    displayMode: true,
    throwOnError: false
});
```

**返回值**：`string` — 可直接插入页面的 HTML 字符串

### katex.__parse(expression, options?)

返回 KaTeX 的内部解析树（不推荐在生产中使用，内部结构不稳定）。

```javascript
const tree = katex.__parse("\\frac{a}{b}");
// 返回 AnyParseNode[] 数组
```

### katex.__renderToDomTree(expression, options?)

返回虚拟 DOM 树（包含 HTML 和 MathML），适用于自定义输出场景。

### katex.__renderToHTMLTree(expression, options?)

返回仅包含 HTML 的虚拟 DOM 树（无 MathML）。

## 常用配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `displayMode` | `boolean` | `false` | 是否使用显示模式（块级居中，大号积分/求和符号） |
| `output` | `string` | `"htmlAndMathml"` | 输出格式：`"html"`、`"mathml"`、`"htmlAndMathml"` |
| `throwOnError` | `boolean` | `true` | 解析错误时是否抛出异常；设为 `false` 则用红色文本显示错误公式 |
| `errorColor` | `string` | `"#cc0000"` | throwOnError=false 时错误文本的颜色 |
| `macros` | `object` | `{}` | 自定义宏映射，如 `{"\\RR": "\\mathbb{R}"}` |
| `colorIsTextColor` | `boolean` | `false` | `\color` 行为是否类似 `\textcolor` |
| `strict` | `boolean\|string\|function` | `false` | LaTeX 严格模式：`"warn"` 输出警告、`"error"` 抛异常、`"ignore"` 忽略 |
| `trust` | `boolean\|function` | `false` | 是否信任输入（启用 `\href`、`\url`、`\includegraphics` 等潜在危险命令） |
| `maxSize` | `number` | `Infinity` | 用户指定尺寸的上限（em单位），防止超大元素 |
| `maxExpand` | `number` | `1000` | 宏展开次数上限，防止无限宏循环 |
| `leqno` | `boolean` | `false` | 显示模式下公式编号放在左侧 |
| `fleqn` | `boolean` | `false` | 显示模式下公式左对齐而非居中 |
| `minRuleThickness` | `number` | — | 线条最小粗细（em），适用于分数线、根号等 |
| `globalGroup` | `boolean` | `false` | 是否将全局命名空间作为表达式作用域（CLI用） |

## 第一个完整示例

**浏览器端**：

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
</head>
<body>
    <p>行内公式：<span id="inline-math"></span></p>
    <div id="display-math"></div>
    <script>
        katex.render("E = mc^2", document.getElementById("inline-math"));
        katex.render("\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}",
                     document.getElementById("display-math"), {displayMode: true});
    </script>
</body>
</html>
```

**Node.js 服务端渲染**：

```javascript
const katex = require('katex');
// 或 import katex from 'katex';

const html = katex.renderToString("a^2 + b^2 = c^2");
// <span class="katex">...</span>
```

## ParseError

KaTeX 解析失败时抛出 `katex.ParseError`。可以用 `instanceof` 判断是否为 KaTeX 解析错误：

```javascript
try {
    katex.render("\\invalidcommand", element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        console.error("LaTeX 解析错误:", e.message);
    } else {
        throw e;  // 其他错误重新抛出
    }
}
```

## 相关概念

- [KaTeX 简介](/concepts/00-introduction.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [配置系统](/concepts/10-settings-options.md)
- [基础渲染示例](/examples/basic-render.md)
- [错误处理示例](/examples/error-handling.md)
