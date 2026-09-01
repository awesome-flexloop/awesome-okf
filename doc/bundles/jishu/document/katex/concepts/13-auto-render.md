---
type: Concept
title: 自动渲染扩展
description: KaTeX auto-render 扩展（contrib/auto-render）的使用方法，包括 renderMathInElement() API、默认 8 条分隔符（不含 $...$）、ignoredTags 默认值、preProcess/errorCallback 钩子、displayMode 由分隔符决定，以及宏持久化与 ESM 版本。
tags: [katex, auto-render, contrib, delimiter, dom, esm]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-autorender
    resource: /references/katex-website.md#web-autorender
    title: KaTeX 官网 Auto-render Extension 页面
---

## auto-render 扩展简介

auto-render 是 KaTeX 的官方扩展模块，位于 [contrib/auto-render/](https://github.com/KaTeX/KaTeX/tree/main/contrib/auto-render)，提供了一个便捷功能：**自动扫描页面中指定DOM元素内的数学公式分隔符，并将其渲染为 KaTeX 公式**。

这使得无需手动调用 `katex.render()` 就可以让包含 `$...$` 或 `$$...$$` 的静态页面自动渲染数学公式。

## 安装与引入

### CDN 方式

```html
<!-- 先引入 katex 本体 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
<!-- 再引入 auto-render 扩展 -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body);"></script>
```

`defer` 属性确保脚本在DOM解析完成后执行。`onload` 回调在脚本加载完成后调用渲染函数。

> **版本注意**：官网 Auto-render 页面的 CDN 示例引用 `katex@0.18.1`（扩展版本），而核心 katex.js 引用 `0.18.4`。本 bundle 以源码 v0.18.4 为基准，实际使用时建议两者保持一致版本，详见 [事实清单修正-8](../spec/facts.md#修正-8官网版本号标注不一致)。

### npm 方式

```bash
npm install katex
```

```javascript
import katex from 'katex';
import renderMathInElement from 'katex/contrib/auto-render';
// 或
import renderMathInElement from 'katex/dist/contrib/auto-render';

// 在DOM就绪后调用
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        // 选项
    });
});
```

注意：需要确保katex本体在auto-render之前加载，auto-render依赖全局的 `katex` 对象。

auto-render 也提供 ESM 版本 `contrib/auto-render.mjs`，支持 `nomodule` 回退[^web-autorender]。

[^web-autorender]: 官网 Auto-render Extension 页面，https://katex.org/docs/autorender

## renderMathInElement() API

```typescript
function renderMathInElement(
    elem: HTMLElement,       // 要扫描的DOM元素
    options?: AutoRenderOptions  // 配置选项
): void;
```

这是auto-render的唯一公开函数。它扫描 `elem` 及其所有后代节点（排除被忽略的标签/类），找到数学分隔符包围的文本，替换为渲染结果。

### 选项（AutoRenderOptions）

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `delimiters` | Array | 见下方 | 数学分隔符配置 |
| `ignoredTags` | string[] | `["script", "noscript", "style", "textarea", "pre", "code", "option"]` | 忽略的HTML标签 |
| `ignoredClasses` | string[] | `[]` | 忽略的CSS类名 |
| `preProcess` | function | — | 数学内容预处理函数 |
| `errorCallback` | function | console.error | 渲染错误回调 |
| `throwOnError` | boolean | — | 传递给 katex.render 的选项 |
| `errorColor` | string | — | 传递给 katex.render 的选项 |
| `macros` | object | — | 传递给 katex.render 的选项 |
| `displayMode` | boolean | — | **被忽略**：显示模式由每条分隔符的 `display` 键决定，而非此选项[^web-autorender] |
| 其他 KaTeX 选项 | — | — | 所有其他 SettingsOptions 都可以传递 |

### 默认分隔符

如果不指定 `delimiters`，auto-render 使用以下配置：

```javascript
[
    {left: "$$", right: "$$", display: true},    // 行间公式
    {left: "\\(", right: "\\)", display: false},  // 行内公式（LaTeX风格）
    {left: "\\begin{equation}", right: "\\end{equation}", display: true},
    {left: "\\begin{align}", right: "\\end{align}", display: true},
    {left: "\\begin{alignat}", right: "\\end{alignat}", display: true},
    {left: "\\begin{gather}", right: "\\end{gather}", display: true},
    {left: "\\begin{CD}", right: "\\end{CD}", display: true},
    {left: "\\[", right: "\\]", display: true},   // 行间公式（LaTeX风格）
    // 注意：$...$ 默认不启用，因为$符号在普通文本中太常见
]
```

要启用 `$...$` 行内公式，需要显式配置：

```javascript
renderMathInElement(document.body, {
    delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},    // 启用$...$
        {left: "\\(", right: "\\)", display: false},
        {left: "\\[", right: "\\]", display: true},
    ]
});
```

### 分隔符配置格式

```typescript
{
    left: string;       // 左分隔符
    right: string;      // 右分隔符
    display: boolean;   // 是否为displayMode
}
```

分隔符可以是任意字符串，不限于LaTeX标准：

```javascript
// 自定义分隔符
{left: "[math]", right: "[/math]", display: false}
```

## 工作原理

auto-render的核心处理流程由两部分组成：

### 1. 文本分割：splitAtDelimiters()

[splitAtDelimiters.ts](https://github.com/KaTeX/KaTeX/blob/main/contrib/auto-render/splitAtDelimiters.ts) 将文本按分隔符分割为片段数组：

```
输入: "已知 $a^2 + b^2 = c^2$，求 $c$。"
分割结果:
  [
    {type: "text", data: "已知 "},
    {type: "math", data: "a^2 + b^2 = c^2", display: false},
    {type: "text", data: "，求 "},
    {type: "math", data: "c", display: false},
    {type: "text", data: "。"}
  ]
```

算法采用**最长匹配优先**，避免 `$$` 被误匹配为两个 `$`。分割器还正确处理转义：
- `\$` 不被视为分隔符（转义的美元符）
- `\\$` 中 `\\` 是转义反斜杠，`$` 仍作为分隔符

### 2. DOM遍历与替换

renderMathInElement 的主循环：
1. 遍历 elem 的所有文本节点
2. 跳过 `ignoredTags` 中的标签（script、pre、code等）
3. 跳过 `ignoredClasses` 中指定类名的元素
4. 对每个文本节点，用 splitAtDelimiters 分割
5. 对 math 类型片段，调用 `katex.render()` 渲染到新创建的 span 元素
6. 用渲染后的 span 替换原文文本节点；text 类型片段保留为文本节点

### 3. preProcess 钩子

preProcess 函数在数学内容传递给 katex.render 之前被调用，可以对公式文本做预处理：

```javascript
renderMathInElement(document.body, {
    preProcess: function(math) {
        // 例如：替换自定义简写
        return math
            .replace(/\\RR/g, "\\mathbb{R}")
            .replace(/\\NN/g, "\\mathbb{N}");
    }
});
```

### 4. errorCallback

当某个公式渲染失败时调用（不影响其他公式渲染）：

```javascript
renderMathInElement(document.body, {
    errorCallback: function(err, mathText, element) {
        console.error("KaTeX渲染错误:", err.message, "公式:", mathText);
        // 自定义错误显示
        element.textContent = "公式错误: " + mathText;
    }
});
```

### 5. 宏持久化

`options.macros` 对象默认为空对象 `{}`，在多次内部 `katex.render` 调用间传递[^web-autorender]。这意味着同一页面中连续的方程可以通过 `\gdef` 建立共享宏：

```javascript
renderMathInElement(document.body, {
    macros: {}  // 同一对象在所有匹配的公式间共享
});
```

```latex
$$ \gdef\RR{\mathbb{R}} $$
$$ f: \RR \to \RR $$
```

第二个公式中的 `\RR` 由第一个公式的 `\gdef` 定义。持久宏的安全注意事项见 [宏系统](09-macro-system.md) 和 [安全与错误处理](18-security-and-errors.md)：不应跨多用户消息共享 macros 对象。

## 使用注意事项

### $...$ 的风险

`$` 作为行内公式分隔符在普通英文文本中容易误触发（如 "价格是 $50 到 $100"）。建议：
- 仅在内容可控（如自己编写的博客文章）时使用 `$...$`
- 对于用户生成内容，使用 `\(...\)` 或 `\[...\]` 更安全
- 可通过 ignoredClasses 排除特定区域

### 动态内容

renderMathInElement 只处理调用时已经存在于DOM中的内容。对于动态加载的内容（AJAX、SPA路由切换），需要在内容加载完成后再次调用 renderMathInElement：

```javascript
// 动态加载内容后重新渲染
async function loadContent() {
    const response = await fetch("/api/content");
    const html = await response.text();
    document.getElementById("content").innerHTML = html;
    // 重新渲染新内容中的公式
    renderMathInElement(document.getElementById("content"));
}
```

为避免重复渲染已处理的元素，可以给已渲染的元素添加标记类，在ignoredClasses中排除。

### 性能考虑

- 对于大型文档，扫描整个 document.body 可能有性能开销
- 建议限定扫描范围到包含数学内容的容器元素
- 避免频繁调用（如在scroll事件中调用）
- SSR环境中应使用 renderToString 而非auto-render

### 与MathJax共存

如果页面同时使用MathJax和KaTeX，需要小心处理：
- 使用不同的分隔符配置，避免冲突
- 或者通过ignoredClasses让两者互不干扰

## 相关概念

- [快速开始](01-getting-started.md)
- [配置系统](10-settings-options.md)
- [自动渲染示例](../examples/auto-render-usage.md)
- [贡献扩展](14-contrib-extensions.md)
