---
type: Concept
title: 样式系统
description: KaTeX 的 TeX 样式模型（8种Style），样式转换方法（sup/sub/fracNum/fracDen/cramp），数学原子类（mord/mop/mbin等）、tight spacing规则，以及官网 Font 页说明的 1.21em 默认缩放与 TeX 单位换算。
tags: [katex, style, tex-style, cramped, math-class, spacing, units]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-font
    resource: /references/katex-website.md#web-font
    title: KaTeX 官网 Font 页面
---

## TeX 样式模型

TeX 有四种基本数学样式，每种又有 cramp（压缩，上标位置更低）变体，共8种样式。KaTeX 的 [Style 类](https://github.com/KaTeX/KaTeX/blob/main/src/Style.ts) 精确实现了这个模型。

## 8种样式

| 样式名 | ID | 说明 |
|--------|-----|------|
| D（display） | 0 | 行间显示模式，非压缩 |
| D'（display cramped） | 1 | 行间显示模式，压缩（如根号内） |
| T（text） | 2 | 行内文本模式，非压缩 |
| T'（text cramped） | 3 | 行内文本模式，压缩 |
| S（script） | 4 | 上标/下标样式，非压缩 |
| S'（script cramped） | 5 | 上标/下标样式，压缩 |
| SS（scriptscript） | 6 | 上上标/下标的下标，非压缩 |
| SS'（scriptscript cramped） | 7 | 上上标/下标的下标，压缩 |

样式通过 `styles` 数组预创建为单例，避免重复实例化。

## 样式转换规则

TeX 定义了在不同上下文中子表达式使用什么样式：

| 当前样式 | 上标 sup() | 下标 sub() | 分子 fracNum() | 分母 fracDen() | 压缩 cramp() | 文本 text() |
|---------|-----------|-----------|---------------|---------------|-------------|------------|
| D | S | S' | T | T' | D' | T |
| D' | S' | S' | T' | T' | D' | T' |
| T | S | S' | S | S' | T' | T |
| T' | S' | S' | S' | S' | T' | T' |
| S | SS | SS' | SS | SS' | S' | — |
| S' | SS' | SS' | SS' | SS' | S' | — |
| SS | SS | SS' | SS | SS' | SS' | — |
| SS' | SS' | SS' | SS' | SS' | SS' | — |

这些规则的含义：

### sup()：上标样式
- 在D/T样式下，上标使用S（script）样式
- 在S/SS样式下，上标使用SS（scriptscript）样式（不会无限缩小）
- 如果当前是cramped，上标也是cramped

### sub()：下标样式
- 下标始终是cramped（TeX排版惯例：下标位置更低）
- 其他规则同sup

### fracNum()：分子样式
- 在D样式下，分子使用T（text）样式（行间分数的分子是T样式，与行内公式同大）
- 在T样式下，分子使用S（script）样式（行内分数的分子是上标大小）
- 分母总是比分子多一层cramp

### fracDen()：分母样式
- 分母始终是cramped（分数线下方的内容）
- 其他规则同fracNum

### cramp()：压缩样式
- 非cramped→对应cramped变体
- 已cramped→不变（cramp是幂等的）
- 触发cramp的场景：根号内、下划线/下划线、分母、下标

### text()：文本模式样式
- D→T（显示模式降级到文本模式）
- D'→T'
- T/T'保持不变
- S/SS不转换（文本命令在script样式下的行为）

## Style 类 API

```typescript
class Style {
    id: number;            // 0-7
    size: number;          // 对应的字号级别（0=SS, 1=S, 2=T, 3=D）
    cramped: boolean;      // 是否压缩
    isTight(): boolean;    // 是否为tight样式（S/SS）

    sup(): Style;          // 上标样式
    sub(): Style;          // 下标样式
    fracNum(): Style;      // 分子样式
    fracDen(): Style;      // 分母样式
    cramp(): Style;        // 压缩样式
    text(): Style;         // 文本样式

    // 预创建实例
    static DISPLAY: Style;         // D (id=0)
    static TEXT: Style;            // T (id=2)
    static SCRIPT: Style;          // S (id=4)
    static SCRIPTSCRIPT: Style;    // SS (id=6)
}
```

## 样式与字号关系

Style 不直接控制字号大小，但通过 `size` 属性和 Options 的 `sizeMultiplier` 共同决定最终渲染大小：

- D 和 T → sizeMultiplier = 当前字号倍数（如normalsize=1.0）
- S → sizeMultiplier × 0.7（上标缩小30%）
- SS → sizeMultiplier × 0.5（上上标缩小50%）

这是通过 `Options.havingStyle()` 中的 `sizeMultiplier` 调整实现的。

## 渲染缩放与 TeX 单位（用户视角）

> 本节内容来自官网 Font 页面，面向集成 KaTeX 的开发者；内部 Style 转换规则见上文。

### 1.21em 默认缩放

KaTeX 默认以周围上下文字体大小的 **1.21 倍** 渲染数学公式，使上下标更易读[^web-font]。这一缩放通过 CSS 实现，可用自定义 CSS 覆盖：

```css
.katex { font-size: 1.1em; }
```

`Style` 内部的 `sizeMultiplier`（S→0.7、SS→0.5）是在这个 1.21em 基准之上的二次缩放，二者共同决定最终像素大小。

### TeX 单位与绝对长度

KaTeX 支持所有 TeX 单位（包括 cm、in 等绝对单位）。绝对单位相对于 **默认 TeX 字号 10pt** 统一缩放，而非浏览器的 1cm 物理长度[^web-font]：

| TeX 单位 | 换算基准 | 示例 |
|----------|---------|------|
| em | 相对于当前字号 | `1em` = 当前字号宽度 |
| mu | 1/18 em（数学单位） | `18mu` = `1em` |
| cm | 相对 10pt 缩放 | `\kern1cm` ≡ `\kern2.845275em` |
| in | 相对 10pt 缩放 | `1in` = 2.54cm（TeX 基准） |

因此，由于浏览器默认字号通常大于 10pt，KaTeX 中的 `1cm` kern 视觉上会比浏览器原生的 `1cm` 更大。相对单位与绝对单位均相对于 10pt 字体的 LaTeX 统一缩放[^web-font]。

[^web-font]: 官网 Font 页面，https://katex.org/docs/font

## 数学原子类（MathClass）

TeX 将每个数学原子分为8个数学类（math class），决定了原子之间的间距：

| 类名 | CSS类 | 说明 | 示例 |
|------|-------|------|------|
| mord | `.mord` | 普通（ordinary） | 字母、数字、`\alpha` |
| mop | `.mop` | 大算符（operator） | `\sum`、`\int`、`\sin` |
| mbin | `.mbin` | 二元运算符（binary） | `+`、`-`、`\times` |
| mrel | `.mrel` | 关系运算符（relation） | `=`、`<`、`\to`、`\approx` |
| mopen | `.mopen` | 左分隔符（opening） | `(`、`[`、`\left\{` |
| mclose | `.mclose` | 右分隔符（closing） | `)`、`]`、`\right\}` |
| mpunct | `.mpunct` | 标点（punctuation） | `,`、`;`、`\colon` |
| minner | `.minner` | 内部（inner） | 分数、根号、`\middle` |

定义在 [src/atoms.ts](https://github.com/KaTeX/KaTeX/blob/main/src/atoms.ts)：

```typescript
const atoms = ["mbin", "mclose", "minner", "mopen", "mpunct", "mrel"];
const nonAtoms = ["accent-token", "mord", "op-token", "spacing", "textord"];
```

### 类型守卫

```typescript
function isAtom(type: string): boolean {
    return atoms.includes(type);
}
```

## Tight Spacing（紧密间距）

在行内公式（T样式）中，如果下标的后面紧跟一个普通原子，间距会更紧密（tight spacing）。这是通过 `.mtight` CSS类和相关样式规则实现的。

`Style.isTight()` 返回 true 当样式为 S 或 SS（script/scriptscript），此时子节点使用更紧凑的间距。

## 间距规则

原子之间的间距由它们的数学类决定，通过CSS margin实现。间距数据在 [src/spacingData.ts](https://github.com/KaTeX/KaTeX/blob/main/src/spacingData.ts) 中定义，是一个8×8的矩阵：

```
            后→  mord  mop   mbin  mrel  mopen mclose mpunct minner
前↓
mord          0    thin  med   thick 0    0      0      thin
mop           thin thin* med   thick 0    0      0      thin
mbin          med  med   ×     ×     ×    med    med    med
mrel          thick thick ×     ×     ×    thick  thick  thick
mopen         0    0     ×     ×     0    0      0      0
mclose        0    thin  med   thick 0    0      0      thin
mpunct        thin thin  ×     ×     ×   thin   thin   thin
minner        thin thin  med   thick 0   thin   thin   thin
```

数值表示：0=无间距，thin=薄间距，med=中间距，thick=厚间距；×=不应该出现的组合；*=大算符有特殊处理。

这些间距通过CSS margin（em单位）实现，buildHTML过程中为相邻原子计算并设置正确的margin值。

## 颜色模型

颜色通过 Options 的 `color` 属性传递，支持以下格式：

- 命名颜色：`red`、`blue`、`black` 等标准HTML/CSS颜色名
- 十六进制：`#f00`、`#ff0000`
- RGB/RGBA：`rgb(255,0,0)`、`rgba(255,0,0,0.5)`
- 透明度：通过 `\definecolor` 定义

`\color{color}` 命令将Options的color设为指定颜色，影响后续所有内容（直到分组结束）。`\textcolor{color}{content}` 只改变参数内内容的颜色。

## 字体切换

数学字体通过 `\mathXX` 命令切换，影响 Options 的 `font` 属性：

| 命令 | font值 | 说明 |
|------|--------|------|
| `\mathrm` | `"mathrm"` | Roman（直立罗马） |
| `\mathit` | `"mathit"` | Italic（斜体） |
| `\mathbf` | `"mathbf"` | Bold（粗体） |
| `\mathbb` | `"mathbb"` | Blackboard Bold（黑板粗体） |
| `\mathcal` | `"mathcal"` | Calligraphic（花体） |
| `\mathfrak` | `"mathfrak"` | Fraktur（哥特体） |
| `\mathscr` | `"mathscr"` | Script（手写体） |
| `\mathsf` | `"mathsf"` | Sans Serif（无衬线） |
| `\mathtt` | `"mathtt"` | Typewriter（打字机体） |

文本字体通过 `\textrm`、`\textbf`、`\textit` 等命令切换，影响 Options 的 `fontWeight`、`fontShape`、`fontFamily` 属性。

## 相关概念

- [配置系统](/concepts/10-settings-options.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [字体度量](/concepts/12-font-metrics.md)
