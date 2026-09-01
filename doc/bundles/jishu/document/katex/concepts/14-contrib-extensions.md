---
type: Concept
title: 贡献扩展模块
description: KaTeX contrib/ 目录下的官方扩展模块：auto-render（自动渲染）、copy-tex（复制 LaTeX 源码）、mhchem（化学方程式）、render-a11y-string（无障碍字符串）、mathtex-script-type（script 标签自动渲染）。第三方生态库索引见生态文档。
tags: [katex, contrib, extension, copy-tex, mhchem, a11y, mathtex]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-libs
    resource: /references/katex-website.md#web-libs
    title: KaTeX 官网 Extensions & Libraries 页面
---

## contrib/ 扩展目录

[contrib/](https://github.com/KaTeX/KaTeX/tree/main/contrib) 目录包含 KaTeX 的官方扩展模块，这些扩展不是核心功能，但提供了实用的附加能力。每个扩展是独立的，可以按需引入。

| 扩展 | 功能 |
|------|------|
| auto-render | 自动扫描DOM中的数学分隔符并渲染（详见[自动渲染扩展](13-auto-render.md)） |
| copy-tex | 复制KaTeX渲染结果时输出LaTeX源码而非Unicode字符 |
| mhchem | 化学方程式和化学式排版（`\ce{...}`命令） |
| render-a11y-string | 生成公式的可读文本字符串（无障碍辅助） |
| mathtex-script-type | 自动渲染 `<script type="math/tex">` 标签中的公式 |

> **范围说明**：`contrib/` 目录共 5 个扩展（见上表）。官网 Extensions & Libraries 页面列出 4 个官方扩展（auto-render、copy-tex、mathtex-script-type、mhchem），render-a11y-string 同样存在于 `contrib/` 目录[^web-libs]。第三方库（React/Vue/Angular/Android/iOS/Rust/Ruby/微信小程序等）的索引见 [生态与版本](23-ecosystem-and-versions.md)，不在本文档范围内。

[^web-libs]: 官网 Extensions & Libraries 页面，https://katex.org/docs/libs

## copy-tex 扩展

### 功能

当用户选择并复制KaTeX渲染的公式时，默认情况下会复制渲染后的Unicode字符（如"α²+β²"）。copy-tex 扩展修改了复制行为，使其复制原始LaTeX源码（如 `\alpha^2 + \beta^2`），方便粘贴到LaTeX编辑器中。

### 使用方法

```html
<!-- 在katex.js之后引入 -->
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/copy-tex.min.js"></script>
```

或 npm：

```javascript
import 'katex/contrib/copy-tex';
```

### 工作原理

copy-tex 在脚本加载时自动注册一个 `copy` 事件监听器，无需手动初始化：

1. 用户复制时，检查选区是否包含 KaTeX 渲染的 MathML 元素
2. 若包含，从 MathML 的 `<annotation>` 节点中提取原始 LaTeX 源码
3. 行内公式用 `$...$` 包裹，行间公式用 `$$...$$` 包裹
4. 将 LaTeX 源码作为纯文本写入剪贴板，同时保留 HTML 格式

当选区不包含 KaTeX 内容或浏览器不支持相关 API 时，扩展直接返回，不影响默认复制行为。

### 浏览器兼容性

copy-tex 依赖浏览器的 Selection API 和 ClipboardEvent API。当 API 不可用时，扩展直接返回，浏览器保持默认复制行为（优雅降级）。KaTeX 支持的主流浏览器（Chrome、Safari、Firefox、Opera、Edge）均提供这些 API。

## mhchem 扩展

### 功能

[mhchem](https://mhchem.github.io/MathJax-mhchem/) 是一个用于排版化学方程式的LaTeX包。KaTeX的mhchem扩展提供了对 `\ce{...}` 命令的支持，可以排版：

- 化学式：`\ce{H2O}`、`\ce{SO4^2-}`
- 化学反应方程式：`\ce{2H2 + O2 -> 2H2O}`
- 化学计量：`\ce{C6H12O6 ->[yeast] 2C2H5OH + 2CO2}`
- 氧化态、键合箭头、平衡箭头等
- 物理量单位：`\pu{123 kJ/mol}`

### 使用方法

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/mhchem.min.js"></script>
```

```javascript
katex.render("\\ce{CO2 + C -> 2CO}", element);
katex.render("\\ce{[Co(NH3)6]Cl3}", element2);
katex.render("\\pu{1.5e-6 mol}", element3);
```

### 工作原理

mhchem 扩展通过 `__defineMacro` 注册 `\ce` 和 `\pu` 两个宏命令（以及内部辅助命令 `\tripledash`）：
- `\ce{...}`：排版化学表达式
- `\pu{...}`：排版物理量单位（Physical Unit）

mhchem 是 [MathJax-mhchem](https://mhchem.github.io/MathJax-mhchem/) 的 KaTeX 移植版本（基于 mhchem 3.3.0），源码位于 [contrib/mhchem/mhchem.js](https://github.com/KaTeX/KaTeX/blob/main/contrib/mhchem/mhchem.js)。它通过宏展开将化学语法转换为 KaTeX 原生命令，再由 KaTeX 的标准解析和渲染管线处理。

### 注意事项

- mhchem 是独立的 JavaScript 文件，引入后自动注册宏命令，无需额外配置
- 它是 MathJax-mhchem 的移植版本，对原 LaTeX mhchem 包的部分功能做了适配和简化
- 具体支持的化学语法详见 [mhchem 文档](https://mhchem.github.io/MathJax-mhchem/)

## render-a11y-string 扩展

### 功能

为数学公式生成人类可读的文本字符串，用于：
- 屏幕阅读器替代（ARIA标签）
- 语音朗读
- 公式的纯文本摘要

例如 `\frac{1}{2}` 会生成 "start fraction, 1, divided by, 2, end fraction"。

### 使用方法

该扩展导出独立的 `renderA11yString` 函数，接收 LaTeX 字符串和可选的配置选项，返回人类可读的文本字符串：

```javascript
import renderA11yString from 'katex/contrib/render-a11y-string';

const a11yString = renderA11yString("\\frac{1}{2}");
// "start fraction, 1, divided by, 2, end fraction"
```

该函数调用 KaTeX 的内部解析接口获取解析树，再遍历解析树生成文本描述。它不修改 `katex.render` 或 `katex.renderToString` 的行为，也不会自动向渲染结果添加 `aria-label`。如需无障碍标注，需由调用方自行将返回的字符串设置到相应元素的属性上。

### 字符串生成规则

该扩展遍历 KaTeX 解析树，为不同类型的节点生成对应的英文短语：

- 分数 → "start fraction, ..., divided by, ..., end fraction"
- 上标 → "start superscript, ..., end superscript"，幂次为 2 或 3 时读作 "squared"/"cubed"
- 下标 → "start subscript, ..., end subscript"（对数下标读作 "base"）
- 根号 → "square root of, ..., end square root"
- 常用运算符和函数 → 英文名称（"plus"、"equals"、"sine"、"sum" 等）
- 括号和分隔符 → "left parenthesis"、"right parenthesis" 等

生成的字符串以逗号分隔，旨在提升屏幕阅读器的可读性。

## mathtex-script-type 扩展

### 功能

自动查找页面中的 `<script type="math/tex">` 标签，渲染其中的LaTeX内容。这是一种较早的数学公式标记方式，曾被MathJax推广。

### 使用方法

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/mathtex-script-type.min.js"></script>

<!-- 公式内容写在script标签中 -->
<script type="math/tex">a^2 + b^2 = c^2</script>
<script type="math/tex; mode=display">\sum_{n=1}^\infty \frac{1}{n^2}</script>
```

- `type="math/tex"`：行内公式
- `type="math/tex; mode=display"`：行间显示公式

### 工作原理

脚本加载时自动执行一次：

1. 遍历页面中的 `<script>` 标签，筛选 `type` 属性匹配 `math/tex` 的标签
2. 根据 `type` 中是否包含 `mode=display` 判断行内或行间模式
3. 行间公式创建 `<div class="equation">`，行内公式创建 `<span class="inline-equation">`
4. 调用 `katex.render()` 渲染 LaTeX 内容；渲染失败时在控制台输出错误并显示原始文本
5. 用渲染后的元素替换原 `<script>` 标签

### 注意事项

- 此扩展在脚本加载时自动执行一次，不会处理后续动态添加的 `<script>` 标签
- 必须在 KaTeX 核心脚本之后加载
- 现代项目通常使用 auto-render 扩展（`$...$`/`$$...$$` 分隔符）或手动调用 `katex.render()`

## 扩展的加载机制

contrib 扩展的共同特点：

1. 依赖 KaTeX 核心（必须先加载 katex.js）
2. 以独立脚本或模块形式提供，可按需引入
3. 各扩展的注册方式不同：mhchem 通过 `__defineMacro` 注册宏命令；auto-render 暴露 `renderMathInElement` 函数；copy-tex 和 mathtex-script-type 在加载时自动注册事件监听器或执行 DOM 扫描；render-a11y-string 导出独立的字符串生成函数
4. 当前版本的 contrib 扩展均不附带独立的 CSS 文件（copy-tex 自 v0.16.0 起不再需要 CSS）

## 第三方生态库

除官方 `contrib/` 扩展外，KaTeX 社区还提供了按平台/语言分类的第三方库[^web-libs]：

| 平台/语言 | 代表库 |
|-----------|--------|
| React | react-katex、react-latex |
| Vue | vue-katex |
| Angular 2+ | ng-katex |
| Android | KaTeXView |
| iOS | KaTeX-iOS、KatexUtils |
| Rust | katex-rs（服务端渲染绑定） |
| Ruby | katex-ruby（Rails/Hanami 集成） |
| Web Components | katex-element、katex-expression |
| 微信小程序 | @rojer/katex-mini |
| AsciiMath | asciimath2tex（先转 LaTeX 再渲染） |

完整的第三方库索引和版本生态说明见 [生态与版本](23-ecosystem-and-versions.md)。

## 相关概念

- [自动渲染扩展](13-auto-render.md)
- [函数注册表](08-function-registry.md)
- [快速开始](01-getting-started.md)
- [生态与版本](23-ecosystem-and-versions.md)
