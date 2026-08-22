---
type: Example
title: 自动渲染使用示例
description: auto-render扩展的完整使用示例，包括分隔符配置、忽略元素、自定义预处理、动态内容处理。
tags: [katex, example, auto-render, delimiter, dynamic]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:40:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 基本使用

### 最简CDN方式

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/auto-render.min.js"
            onload="renderMathInElement(document.body);"></script>
</head>
<body>
    <h1>数学笔记</h1>
    <p>勾股定理：\(a^2 + b^2 = c^2\)。</p>
    <p>高斯积分：$$\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}$$</p>
</body>
</html>
```

- `\(...\)`：行内公式（LaTeX风格）
- `\[...\]` 或 `$$...$$`：行间显示公式
- `defer` 确保DOM加载完成后再执行脚本

### 启用$...$分隔符

默认不启用 `$...$`（容易误触发），需要显式配置：

```html
<script>
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false},
            {left: "\\(", right: "\\)", display: false},
            {left: "\\[", right: "\\]", display: true},
        ]
    });
});
</script>
```

HTML中使用：
```html
<p>已知 $x = 3$，求 $x^2$ 的值。</p>
<p>$$\sum_{i=1}^n i = \frac{n(n+1)}{2}$$</p>
```

## 配置选项

### 忽略特定标签

默认忽略的标签：`script, noscript, style, textarea, pre, code, option`

添加额外忽略标签：

```javascript
renderMathInElement(document.body, {
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option",
                  "my-custom-tag"]  // 添加自定义标签
});
```

### 忽略特定CSS类

```html
<div class="no-math">这里的$不会被渲染：$a+b$</div>
<div class="math-content">这里的$会被渲染：$a+b$</div>
```

```javascript
renderMathInElement(document.body, {
    ignoredClasses: ["no-math", "code-block", "raw-text"]
});
```

### 传递KaTeX选项

所有 KaTeX 渲染选项都可以传递给 auto-render：

```javascript
renderMathInElement(document.body, {
    delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
    ],
    throwOnError: false,        // 不抛异常
    errorColor: "#cc0000",      // 错误文本红色
    strict: "warn",             // 严格模式警告
    macros: {                   // 自定义宏
        "\\RR": "\\mathbb{R}",
        "\\diff": "\\mathop{}\\!\\mathrm{d}",
    },
    trust: true,                // 允许\href等
    maxExpand: 2000,            // 宏展开上限
});
```

### 自定义分隔符

可以使用任意分隔符，不仅限于LaTeX标准：

```javascript
renderMathInElement(document.body, {
    delimiters: [
        {left: "[m]", right: "[/m]", display: false},    // 行内
        {left: "[math]", right: "[/math]", display: true}, // 行间
    ]
});
```

HTML：
```html
<p>公式：[m]E=mc^2[/m]</p>
[math]E=mc^2[/math]
```

### LaTeX环境分隔符

auto-render默认支持多种LaTeX环境：

```javascript
delimiters: [
    {left: "\\begin{equation}", right: "\\end{equation}", display: true},
    {left: "\\begin{align}", right: "\\end{align}", display: true},
    {left: "\\begin{equation*}", right: "\\end{equation*}", display: true},
    {left: "\\begin{align*}", right: "\\end{align*}", display: true},
    {left: "\\begin{gather}", right: "\\end{gather}", display: true},
    {left: "\\begin{CD}", right: "\\end{CD}", display: true},
]
```

使用：
```latex
\begin{equation}
    E = mc^2
\end{equation}

\begin{align}
    a &= b + c \\
    d &= e + f
\end{align}
```

## 高级用法

### preProcess 预处理

在渲染前对公式文本进行替换/转换：

```javascript
renderMathInElement(document.body, {
    preProcess: function(math) {
        // 自定义简写替换
        return math
            // 替换 RR/NN/ZZ 为黑板粗体
            .replace(/\\RR\b/g, "\\mathbb{R}")
            .replace(/\\NN\b/g, "\\mathbb{N}")
            .replace(/\\ZZ\b/g, "\\mathbb{Z}")
            // 替换 -> => 为箭头
            .replace(/->/g, "\\to")
            .replace(/=>/g, "\\implies");
    }
});
```

HTML中使用：
```html
<p>映射 $f: \RR -> \RR$</p>
<!-- 预处理后变为：$f: \mathbb{R} \to \mathbb{R}$ -->
```

### errorCallback 错误处理

自定义渲染错误的处理：

```javascript
renderMathInElement(document.body, {
    throwOnError: false,  // 必须设为false才会调用errorCallback
    errorCallback: function(err, mathText, originalElement) {
        console.error("KaTeX公式渲染失败:", err.message);
        console.error("问题公式:", mathText);

        // 自定义错误显示
        originalElement.classList.add("katex-error");
        originalElement.title = err.message;
        originalElement.textContent = "[公式错误: " + mathText.substring(0, 50) + "]";
    }
});
```

### 限定渲染范围

对于大型页面，不要渲染整个document.body，限定到特定容器：

```html
<article id="post-content">
    <p>文章内容，包含数学公式...</p>
</article>
<aside id="sidebar">
    <p>侧边栏不需要渲染数学...</p>
</aside>
```

```javascript
// 只渲染文章内容区域
renderMathInElement(document.getElementById("post-content"), {
    delimiters: [{left: "$", right: "$", display: false},
                 {left: "$$", right: "$$", display: true}]
});
```

## 动态内容处理

### AJAX加载内容后重新渲染

```javascript
async function loadArticle(articleId) {
    const response = await fetch(`/api/articles/${articleId}`);
    const html = await response.text();

    const container = document.getElementById("article-container");
    container.innerHTML = html;

    // 只渲染新加载的内容
    renderMathInElement(container, {
        delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "\\(", right: "\\)", display: false},
        ]
    });
}
```

### SPA路由切换后渲染

```javascript
// Vue/React/Angular等框架中，在路由组件挂载后渲染
function onRouteChanged() {
    // 等待DOM更新
    setTimeout(() => {
        const mathContainer = document.querySelector(".math-container");
        if (mathContainer) {
            // 清除之前的渲染标记（如果需要重新渲染）
            renderMathInElement(mathContainer, {
                delimiters: [{left: "$", right: "$", display: false},
                             {left: "$$", right: "$$", display: true}],
                throwOnError: false,
            });
        }
    }, 0);
}
```

### 避免重复渲染

多次调用renderMathInElement会重复处理已渲染的元素。避免方式：

```javascript
// 给已渲染元素添加标记
document.querySelectorAll(".katex").forEach(function(el) {
    el.setAttribute("data-katex-rendered", "true");
});

// 渲染时排除已渲染元素
function renderMath(container) {
    const ignored = ["katex-rendered-marker"];
    container.classList.add(ignored[0]);  // 临时标记避免递归
    renderMathInElement(container, {
        ignoredClasses: ignored,
        // ...
    });
    container.classList.remove(ignored[0]);
    container.setAttribute("data-katex-rendered", "true");
}
```

## 与Markdown结合

### Markdown + KaTeX 典型配置

在Markdown渲染管线中使用auto-render：

```javascript
// 假设使用marked.js渲染Markdown
function renderMarkdownToElement(markdownText, element) {
    // 1. 先渲染Markdown为HTML
    element.innerHTML = marked.parse(markdownText);

    // 2. 再让auto-render处理数学
    renderMathInElement(element, {
        delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "\\(", right: "\\)", display: false},
        ],
        throwOnError: false,
    });
}
```

注意：Markdown解析器可能会转义反斜杠或处理`$`，需要配置Markdown解析器保留数学分隔符。例如marked.js中：

```javascript
marked.setOptions({
    // 不要转义LaTeX中的反斜杠
    // 或在marked之前先提取数学块作为代码块保护
});
```

### 保护数学块免受Markdown处理

更稳健的方法是在Markdown解析前提取数学公式，解析后还原：

```javascript
function processMarkdownWithMath(markdown) {
    const mathBlocks = [];
    // 提取 $$...$$ 块
    let processed = markdown.replace(/\$\$([^$]+)\$\$/g, function(match, math) {
        const id = "MATH_PLACEHOLDER_" + mathBlocks.length;
        mathBlocks.push({id, math, display: true});
        return id;
    });
    // 提取 \(...\) 块
    processed = processed.replace(/\\\(([^)]+)\\\)/g, function(match, math) {
        const id = "MATH_PLACEHOLDER_" + mathBlocks.length;
        mathBlocks.push({id, math, display: false});
        return id;
    });

    // 渲染Markdown
    let html = marked.parse(processed);

    // 还原数学块为原始LaTeX（让auto-render处理）
    mathBlocks.forEach(block => {
        const delimiter = block.display ? "$$" : "\\(";
        const endDelimiter = block.display ? "$$" : "\\)";
        html = html.replace(block.id, delimiter + block.math + endDelimiter);
    });

    return html;
}
```

## 相关内容

- [自动渲染扩展](/concepts/13-auto-render.md)
- [快速开始](/concepts/01-getting-started.md)
- [基础渲染示例](/examples/basic-render.md)
- [配置系统](/concepts/10-settings-options.md)
