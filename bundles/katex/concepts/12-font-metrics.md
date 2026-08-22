---
type: Concept
title: 字体与度量
description: KaTeX 字体系统的组织结构，fontMetrics 度量数据，Unicode字符支持，以及字体度量提取工具链。
tags: [katex, font, metrics, unicode, glyph]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:35:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:35:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## KaTeX 字体体系

KaTeX 使用自包含的 Web 字体（.ttf/.woff/.woff2），不依赖系统字体。字体文件位于 [fonts/](https://github.com/KaTeX/KaTeX/tree/main/fonts) 目录。

### 字体族

| 字体名 | 用途 |
|--------|------|
| KaTeX_Main | 主字体（拉丁字母、数字、运算符、扩展符号） |
| KaTeX_Math | 数学斜体（变量默认字体） |
| KaTeX_AMS | AMS符号（额外数学符号） |
| KaTeX_Caligraphic | 花体（`\mathcal`） |
| KaTeX_Fraktur | 哥特体（`\mathfrak`） |
| KaTeX_SansSerif | 无衬线体（`\mathsf`） |
| KaTeX_Script | 手写体（`\mathscr`） |
| KaTeX_Typewriter | 打字机体（`\mathtt`） |
| KaTeX_Size1~4 | 大尺寸分隔符（`\Big`、`\bigg` 等可伸缩符号的各尺寸） |

字体在 [src/styles/fonts.scss](https://github.com/KaTeX/KaTeX/blob/main/src/styles/fonts.scss) 中通过 `@font-face` 声明。

## 字体度量数据（fontMetrics）

精确排版需要每个字符的度量信息（高度、深度、宽度、斜体修正等）。KaTeX 将这些数据预提取并内置于代码中。

### getGlobalMetrics()

[src/fontMetrics.ts](https://github.com/KaTeX/KaTeX/blob/main/src/fontMetrics.ts) 提供全局度量获取接口：

```typescript
function getGlobalMetrics(size: number): {
    cssEmPerMu: number;     // 数学单位mu到em的转换系数
    // 字体度量数据对象
};
```

度量数据按字号大小索引，不同字号下同一字符的度量（通过em单位归一化后）基本一致，但大算符在display模式下使用不同的字形变体。

### 度量字段

每个字符的度量信息包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `depth` | number | 基线以下的深度（em） |
| `height` | number | 基线以上的高度（em） |
| `italic` | number | 斜体修正（em），用于斜体字符后的间距校正 |
| `skew` | number | 倾斜修正（em），用于重音符号的居中定位 |
| `width` | number | 字符宽度（em） |

这些数据在 buildHTML 时用于：
- 计算行高（height + depth）
- 放置上标/下标位置
- 定位重音符号（hat、bar、vec等）
- 原子间间距计算

### 符号注册

符号在 [src/symbols.ts](https://github.com/KaTeX/KaTeX/blob/main/src/symbols.rs)（实际是.ts）中通过 `defineSymbol()` 注册到不同模式和字体中：

```typescript
defineSymbol(
    "math",      // 模式（math或text）
    "main",      // 字体族
    "mord",      // 数学类（mord/mop/mbin等）
    "a",         // Unicode字符
    "a"          // LaTeX命令（单字符通常与Unicode相同）
);
defineSymbol(
    "math",
    "main",
    "mop",
    "\u2211",    // ∑ (U+2211 N-ARY SUMMATION)
    "\\sum"
);
```

## 大算符与尺寸变体

### 尺寸映射

大符号（分隔符、根号、箭头等）需要多个尺寸变体。KaTeX 通过 KaTeX_Size1~KaTeX_Size4 字体提供4种尺寸：

| 大小命令 | CSS类 | 尺寸倍数 | 使用字体 |
|---------|-------|---------|---------|
| `\big`/`\bigl`/`\bigr` | `.size1` | 基础尺寸×1.2 | Size1 |
| `\Big`/`\Bigl`/`\Bigr` | `.size2` | 基础尺寸×1.6 | Size2 |
| `\bigg`/`\biggl`/`\biggr` | `.size3` | 基础尺寸×2.0 | Size3 |
| `\Bigg`/`\Biggl`/`\Biggr` | `.size4` | 基础尺寸×2.4 | Size4 |

`\left...\right` 对根据内容高度自动选择合适的尺寸（通过stretchy机制）。

### 可伸缩符号

[src/stretchy.ts](https://github.com/KaTeX/KaTeX/blob/main/src/stretchy.ts) 处理可伸缩分隔符：
- 对于需要的目标高度，选择合适的尺寸变体
- 对于超大尺寸，通过多段拼接（顶部+中间重复段+底部）实现
- 使用SVG或CSS实现线段扩展

## Unicode 支持

KaTeX 对 Unicode 的支持通过几层机制实现：

### 直接符号映射

许多 Unicode 数学字符直接映射到内置符号。例如：
- `α` (U+03B1) → `\alpha`
- `∑` (U+2211) → `\sum`
- `√` (U+221A) → `\sqrt`

### Unicode 重音组合

[src/unicodeAccents.js](https://github.com/KaTeX/KaTeX/blob/main/src/unicodeAccents.js) 映射 Unicode 组合变音符号到 KaTeX 重音命令：

- U+0300 (combining grave) → `\grave`
- U+0301 (combining acute) → `\acute`
- U+0302 (combining circumflex) → `\hat`
- U+0303 (combining tilde) → `\tilde`
- 等等...

### Unicode 规范化

[src/unicodeSymbols.js](https://github.com/KaTeX/KaTeX/blob/main/src/unicodeSymbols.js) 处理 Unicode 字符的变体和规范化，例如：
- 希腊字母的变体形式（φ vs ϕ：`\phi` vs `\varphi`）
- 连字和兼容字符

### Unicode 上下标

[src/unicodeSupOrSub.ts](https://github.com/KaTeX/KaTeX/blob/main/src/unicodeSupOrSub.ts) 处理 Unicode 原生上下标字符：
- ² (U+00B2) → `^{2}`
- ₃ (U+2083) → `_{3}`
- ⁿ (U+207F) → `^{n}`
- 等等...

### supportedCodepoint()

[src/unicodeScripts.ts](https://github.com/KaTeX/KaTeX/blob/main/src/unicodeScripts.ts) 中的 `supportedCodepoint()` 判断一个 Unicode 码点是否被支持：

- 支持的范围：基本拉丁字母、希腊字母、西里尔字母、希伯来字母、阿拉伯字母、CJK等
- 对于不支持的字符，渲染为红色错误或直接显示为原字符（取决于strict模式）

`scriptFromCodepoint()` 判断字符所属的文字系统（用于字体选择）。

## 字体度量提取工具链

[src/metrics/](https://github.com/KaTeX/KaTeX/blob/main/src/metrics/) 目录包含字体度量提取的工具脚本：

| 文件 | 语言 | 作用 |
|------|------|------|
| `extract_tfms.py` | Python | 从 TeX TFM（TeX Font Metric）文件中提取度量 |
| `extract_ttfs.py` | Python | 从 TrueType 字体中提取字形信息 |
| `format_json.py` | Python | 将提取的数据格式化为 JavaScript 可用的格式 |
| `parse_tfm.py` | Python | TFM二进制文件解析器 |
| `mapping.pl` | Perl | 字符映射处理 |

这些工具在 KaTeX 的**构建阶段**运行，生成嵌入到 dist 中的度量数据。运行时使用预生成的数据，不需要实时解析字体文件。

## 字号系统

LaTeX 有10个标准字号命令（从 `\tiny` 到 `\HUGE`），KaTeX 通过 `sizeMultipliers` 数组定义它们的相对倍数：

```typescript
// [src/Options.ts]
const sizeMultipliers = [
    0.5,    // 0: \tiny
    0.6,    // 1: \scriptsize
    0.7,    // 2: \footnotesize
    0.8,    // 3: \small
    0.9,    // 4: (smaller than \normalsize)
    1.0,    // 5: (unused / also normalsize-1)
    1.0,    // 6: \normalsize (BASESIZE)
    1.2,    // 7: \large
    1.44,   // 8: \Large
    1.728,  // 9: \LARGE
    2.074,  // 10: \huge
    2.488,  // 11: \HUGE (实际上在sizeStyleMap中10同时映射\huge和\HUGE到不同倍数)
];
```

注意：从 normalsize 开始，每级字号是前一个的 1.2 倍（1.2^0=1.0, 1.2^1=1.2, 1.2^2=1.44, 1.2^3=1.728, 1.2^4=2.074），这是经典的 LaTeX 几何缩放比例。

## minRuleThickness

`minRuleThickness` 设置（在 Options 和 Settings 中）控制分数线、根号等线条的最小粗细。默认情况下由字体度量决定，但用户可以覆盖：

```javascript
katex.render(expr, el, {
    minRuleThickness: 0.05  // 最小0.05em（约0.5px在10px基准下）
});
```

这在高DPI屏幕或小字号渲染时特别有用，可以防止线条过细不可见。

## 相关概念

- [样式系统](/concepts/11-style-system.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [虚拟DOM树](/concepts/07-dom-tree.md)
