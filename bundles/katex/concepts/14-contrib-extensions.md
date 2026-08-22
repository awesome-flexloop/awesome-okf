---
type: Concept
title: 贡献扩展模块
description: KaTeX contrib/ 目录下的官方扩展模块：copy-tex（复制LaTeX源码）、mhchem（化学方程式）、render-a11y-string（无障碍字符串）、mathtex-script-type（script标签自动渲染）。
tags: [katex, contrib, extension, copy-tex, mhchem, a11y]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:35:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:35:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## contrib/ 扩展目录

[contrib/](https://github.com/KaTeX/KaTeX/tree/main/contrib) 目录包含 KaTeX 的官方扩展模块，这些扩展不是核心功能，但提供了实用的附加能力。每个扩展是独立的，可以按需引入。

| 扩展 | 功能 |
|------|------|
| auto-render | 自动扫描DOM中的数学分隔符并渲染（详见[自动渲染扩展](/concepts/13-auto-render.md)） |
| copy-tex | 复制KaTeX渲染结果时输出LaTeX源码而非Unicode字符 |
| mhchem | 化学方程式和化学式排版（`\ce{...}`命令） |
| render-a11y-string | 生成公式的可读文本字符串（无障碍辅助） |
| mathtex-script-type | 自动渲染 `<script type="math/tex">` 标签中的公式 |

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

copy-tex 使用浏览器的 Selection API 和 Clipboard API：
1. 监听 `copy` 事件
2. 检查选中内容是否包含KaTeX渲染元素
3. 查找KaTeX MathML注解中的 `<annotation encoding="application/x-tex">` 节点（buildMathML生成的原始LaTeX源码）
4. 将annotation中的LaTeX源码写入剪贴板

copy-tex 不需要调用任何初始化函数，引入脚本后自动生效。

### 浏览器兼容性

- Chrome/Edge/Firefox/Safari 现代版本均支持
- 依赖 Selection API 和 ClipboardEvent API
- 在不支持的浏览器上优雅降级（仍使用默认复制行为）

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

mhchem 扩展通过 `__defineFunction` 注册 `\ce` 和 `\pu` 两个命令：
- `\ce{...}`：解析化学表达式
- `\pu{...}`：解析物理量单位（Physical Unit）

mhchem 内部有自己的解析器（在 [contrib/mhchem/mhchem.js](https://github.com/KaTeX/KaTeX/blob/main/contrib/mhchem/mhchem.js) 中），它是MathJax-mhchem的KaTeX移植版本，将化学语法转换为KaTeX的ParseNode树，再使用KaTeX的buildHTML/buildMathML渲染。

### 注意事项

- mhchem 是独立的JavaScript文件，引入后自动注册命令，无需额外配置
- mhchem 的解析器相对较大（~100KB压缩后），按需引入
- 化学渲染效果依赖mhchem内置的样式规则，KaTeX的核心样式不足以渲染所有化学结构
- 不支持完整的LaTeX mhchem包的所有功能（如复杂的有机化学结构）

## render-a11y-string 扩展

### 功能

为数学公式生成人类可读的文本字符串，用于：
- 屏幕阅读器替代（ARIA标签）
- 语音朗读
- 公式的纯文本摘要

例如 `\frac{a}{b}` 可能生成 "StartFraction a Over b EndFraction"。

### 使用方法

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/contrib/render-a11y-string.min.js"></script>
```

```javascript
// 引入后，katex对象上添加了renderToString方法的附加选项
// 或使用独立API：
const a11yString = katex.renderToString("\\frac{a}{b}", {
    // render-a11y-string自动添加aria-label
});
```

render-a11y-string 通过向 KaTeX 的构建流程中注入字符串生成逻辑，在渲染过程中同时生成公式的文本描述，作为 `aria-label` 属性添加到KaTeX根元素上。

### 内部结构

该扩展定义了一套从ParseNode到字符串的规则：
- 分数 → "StartFraction ... Over ... EndFraction"
- 上标 → "Superscript ... Baseline" 或 "... squared"/"... cubed"
- 下标 → "Subscript ... Baseline"
- 根号 → "StartRoot ... EndRoot"
- 求和/积分 → "Sum from ... to ... of ..."
- 希腊字母 → 英文名称（"alpha"、"beta"等）

这些字符串遵循 Nemeth Braille（盲文）和MathML规范的惯例。

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

脚本加载时自动执行：
1. 查找 `document.querySelectorAll('script[type^="math/tex"]')`
2. 提取script标签的textContent
3. 判断是否为display mode（检查type中是否包含 `mode=display`）
4. 创建span元素，调用katex.render()渲染
5. 用渲染后的span替换原script标签

### 注意事项

- 此扩展在脚本加载时自动执行一次，不会处理后续动态添加的script标签
- 与auto-render相比，这种方式的优点是搜索引擎可能看到原始LaTeX内容
- 但由于使用 `<script>` 标签，内容不会被搜索引擎索引为可见文本
- 现代KaTeX推荐使用auto-render（`$...$`/`$$...$$`）或手动调用render

## 扩展的加载机制

所有contrib扩展遵循相同的加载模式：
1. 依赖全局 `katex` 对象（必须先加载katex.js）
2. 自执行脚本，引入后立即生效（无需手动初始化）
3. 通过 `__defineFunction` 等内部API注册新命令或行为
4. 使用独立的CSS文件（如果需要额外样式）

## 相关概念

- [自动渲染扩展](/concepts/13-auto-render.md)
- [函数注册表](/concepts/08-function-registry.md)
- [快速开始](/concepts/01-getting-started.md)
