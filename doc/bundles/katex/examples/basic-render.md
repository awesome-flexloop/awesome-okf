---
type: Example
title: 基础渲染示例
description: KaTeX render() 和 renderToString() 的基本用法，String.raw 避免转义，行内/显示模式，常见公式渲染示例，持久宏共享。
tags: [katex, example, render, displayMode, basic, string-raw]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:30:00+08:00 }
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
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
---

## 浏览器端渲染

### 最小示例：行内公式

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
</head>
<body>
    <p>勾股定理：<span id="formula1"></span></p>
    <script>
        katex.render("c^2 = a^2 + b^2", document.getElementById("formula1"));
    </script>
</body>
</html>
```

渲染结果（行内模式默认）：`c² = a² + b²`

### 使用 String.raw 避免转义

JavaScript 字符串中反斜杠需要双重转义（`\\frac`），可读性较差。可使用 `String.raw` 模板标签直接书写 LaTeX 源码[^web-api]：

```javascript
katex.render(
    String.raw`\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}`,
    document.getElementById("display-formula"),
    { displayMode: true }
);
```

注意：`String.raw` 无法转义 `${` 和反引号本身，包含这些字符的公式仍需普通字符串。

### 显示模式（displayMode）

```javascript
katex.render(
    String.raw`\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}`,
    document.getElementById("display-formula"),
    { displayMode: true }
);
```

`displayMode: true` 使公式[^web-options]：
- 块级显示（独占一行、居中）
- 积分/求和等大算符使用大号字形
- 上下标位置在正上方/正下方（行内模式在角上）
- 禁用最外层关系符或二元运算符后的自动换行

### 服务端渲染（Node.js）

```javascript
const katex = require('katex');
// 或 ESM: import katex from 'katex';

// 行内公式
const inlineHtml = katex.renderToString("E = mc^2");
// <span class="katex">...</span>

// 显示模式
const displayHtml = katex.renderToString(
    "\\sum_{n=1}^{\\infty}\\frac{1}{n^2}=\\frac{\\pi^2}{6}",
    { displayMode: true }
);
// <span class="katex-display"><span class="katex">...</span></span>
```

注意：服务端渲染仍需在HTML页面中引入 `katex.min.css`，否则样式缺失。

## 常见公式示例

### 上下标与分数

```javascript
// 上标
katex.render("x^{n+1}", el);

// 下标
katex.render("a_{ij}", el);

// 同时上下标
katex.render("\\sum_{i=0}^{n}", el2, {displayMode: true});

// 分数
katex.render("\\frac{a+b}{c+d}", el);

// 嵌套分数（连分数）
katex.render("a_0+\\cfrac{1}{a_1+\\cfrac{1}{a_2+\\cfrac{1}{a_3}}}", el2, {displayMode: true});
```

### 根号

```javascript
// 平方根
katex.render("\\sqrt{x^2+y^2}", el);

// n次方根
katex.render("\\sqrt[3]{8}=2", el);
```

### 希腊字母

```javascript
katex.render("\\alpha+\\beta=\\gamma", el);
katex.render("\\Delta\\theta=\\theta_2-\\theta_1", el);
katex.render("\\varepsilon\\neq\\epsilon", el);
```

常用希腊字母：`\alpha, \beta, \gamma, \delta, \epsilon, \varepsilon, \zeta, \eta, \theta, \iota, \kappa, \lambda, \mu, \nu, \xi, \pi, \rho, \sigma, \tau, \upsilon, \phi, \varphi, \chi, \psi, \omega`（大写首字母：`\Gamma, \Delta, \Theta, \Lambda, \Xi, \Pi, \Sigma, \Phi, \Psi, \Omega`）

### 运算符

```javascript
// 二元运算符
katex.render("a\\pm b", el);
katex.render("a\\times b\\div c", el);
katex.render("a\\cdot b = a\\ast b", el);

// 关系运算符
katex.render("x\\leq y\\geq z\\neq w", el);
katex.render("A\\approx B\\sim C\\equiv D", el);
katex.render("p\\Rightarrow q\\Leftrightarrow r", el);

// 大算符
katex.render("\\sum_{i=1}^{n}i=\\frac{n(n+1)}{2}", el2, {displayMode: true});
katex.render("\\int_a^b f(x)\\,dx", el2, {displayMode: true});
katex.render("\\prod_{k=1}^{n}k=n!", el2, {displayMode: true});
katex.render("\\lim_{x\\to\\infty}f(x)=L", el2, {displayMode: true});
```

### 括号与分隔符

```javascript
// 自动大小括号（\left...\right）
katex.render("\\left(\\frac{a}{b}\\right)", el);
katex.render("\\left[\\sum_{i=1}^n x_i\\right]", el);
katex.render("\\left\\{0,1,2\\right\\}", el);
katex.render("\\left|\\frac{x}{y}\\right|", el);

// 手动大小括号
katex.render("\\Big(\\frac{a}{b}\\Big)", el);  // \big, \Big, \bigg, \Bigg
```

### 矩阵

```javascript
// pmatrix: 圆括号矩阵
katex.render(
    "\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}",
    el, {displayMode: true}
);

// bmatrix: 方括号矩阵
katex.render(
    "A=\\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}",
    el, {displayMode: true}
);

// vmatrix: 行列式
katex.render(
    "\\det(A)=\\begin{vmatrix}a&b\\\\c&d\\end{vmatrix}=ad-bc",
    el, {displayMode: true}
);
```

### 文本嵌入

```javascript
// 数学模式中的文本
katex.render("\\text{如果 }x>0\\text{，则 }f(x)>0", el);

// 文本中混合数学
katex.render("\\{x\\in\\mathbb{R}\\mid x>0\\}", el);
```

### 字体样式

```javascript
// 粗体
katex.render("\\mathbf{x}=\\mathbf{A}\\mathbf{b}", el);

// 黑板粗体（数集）
katex.render("\\mathbb{R}, \\mathbb{N}, \\mathbb{Z}, \\mathbb{Q}, \\mathbb{C}", el);

// 花体
katex.render("\\mathcal{L}\\{f\\}(s)=\\int_0^\\infty e^{-st}f(t)\\,dt", el);

// 罗马体（函数名）
katex.render("\\sin^2\\theta+\\cos^2\\theta=1", el);
katex.render("\\log_2 n=\\frac{\\ln n}{\\ln 2}", el);
```

## 多公式批量渲染

如果页面有多个公式需要渲染，逐个调用 `katex.render` 效率较低。可以循环处理：

```javascript
document.querySelectorAll(".math-inline").forEach(function(el) {
    katex.render(el.textContent, el, {throwOnError: false});
});

document.querySelectorAll(".math-display").forEach(function(el) {
    katex.render(el.textContent, el, {displayMode: true, throwOnError: false});
});
```

HTML：
```html
<span class="math-inline">a^2 + b^2</span>
<div class="math-display">\int_0^1 f(x)\,dx</div>
```

或者使用 [auto-render扩展](/examples/auto-render-usage.md) 自动处理 `$...$` 分隔符。

## 持久宏（Persistent Macros）

KaTeX 的 `render` 和 `renderToString` 表面上是无状态的，但通过传入**共享的 `macros` 对象**可实现宏定义在多次调用间持久化[^web-api]：

```javascript
const macros = {};

katex.render(String.raw`\gdef\RR{\mathbb{R}}`, el1, { macros });
katex.render(String.raw`\RR^n`, el2, { macros });
```

当作者使用 `\gdef` 时，KaTeX 将宏定义插入传入的 `macros` 对象，由于该对象在多次调用间持续存在，后续渲染可以使用前面定义的宏。

**安全注意**：持久宏可改变 KaTeX 行为（如重定义标准命令），应仅在共同信任的多个元素间使用；不应跨多用户消息启用。多用户场景应为每条消息创建独立的 `macros` 对象。详见 [宏系统](/concepts/09-macro-system.md) 和 [安全与错误处理](/concepts/18-security-and-errors.md)。

## 输出格式选择

```javascript
// 仅HTML（无MathML，体积更小但无障碍支持弱）
katex.render(expr, el, {output: "html"});

// 仅MathML（仅Firefox/Safari原生支持，不推荐单独使用）
katex.render(expr, el, {output: "mathml"});

// HTML+MathML（默认，最佳无障碍支持）
katex.render(expr, el, {output: "htmlAndMathml"});
```

## 相关内容

- [快速开始](/concepts/01-getting-started.md)
- [安装与运行时](/concepts/15-installation-and-runtime.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [配置系统](/concepts/10-settings-options.md)
- [支持的函数](/concepts/19-supported-functions.md)
- [自定义宏示例](/examples/custom-macros.md)
- [错误处理示例](/examples/error-handling.md)

[^web-api]: 官网 API 页面，https://katex.org/docs/api
[^web-browser]: 官网 Browser 页面，https://katex.org/docs/browser
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
