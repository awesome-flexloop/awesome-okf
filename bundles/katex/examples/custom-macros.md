---
type: Example
title: 自定义宏示例
description: 通过settings.macros和__defineMacro定义KaTeX宏，包括简单别名、带参数宏、函数宏和全局宏注册。
tags: [katex, example, macro, defineMacro, newcommand]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:40:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## settings.macros 配置方式

`settings.macros` 是最常用的自定义宏方式，在单次渲染调用中生效。

### 简单别名（无参数宏）

最基本的用法是给现有命令起短名：

```javascript
katex.render("\\RR^n", el, {
    macros: {
        "\\RR": "\\mathbb{R}",       // 实数集
        "\\NN": "\\mathbb{N}",       // 自然数集
        "\\ZZ": "\\mathbb{Z}",       // 整数集
        "\\QQ": "\\mathbb{Q}",       // 有理数集
        "\\CC": "\\mathbb{C}",       // 复数集
        "\\eps": "\\varepsilon",     // 更美观的epsilon
        "\\vphi": "\\varphi",       // 更美观的phi
    }
});
```

渲染 `\RR^n` 等价于 `\mathbb{R}^n`（ℝⁿ）。

### 带参数宏

使用 `#1`~`#9` 引用参数：

```javascript
katex.render("\\diff{x} + \\ddt{f}", el, {
    macros: {
        // 微分d：\diff{x} → dx（直立d，前面有小间距）
        "\\diff": "\\mathop{}\\!\\mathrm{d}#1",
        // 偏导：\pderiv{f}{x} → ∂f/∂x
        "\\pderiv": "\\frac{\\partial #1}{\\partial #2}",
        // 全导数：\ddt{f} → df/dt
        "\\ddt": "\\frac{\\mathrm{d}#1}{\\mathrm{d}t}",
        // 向量：\v{x} → 粗体x
        "\\v": "\\mathbf{#1}",
        // 矩阵转置：\T{A} → A^T
        "\\T": "#1^{\\mathsf{T}}",
        // 期望：\E[X] → E[X]（直立E）
        "\\E": "\\mathbb{E}\\left[#1\\right]",
        // 概率：\P(A) → P(A)（直立P）
        "\\P": "\\mathbb{P}\\left(#1\\right)",
    }
});
```

### 参数数量说明

KaTeX通过 `#n` 的最大出现次数自动推断参数数量。例如 `\pderiv` 使用了 `#1` 和 `#2`，所以它接受2个参数：

```
\pderiv{f}{x}  →  \frac{\partial f}{\partial x}
```

### 花括号参数与单Token参数

宏参数可以是花括号组或单个Token：

```
\v{x}    →  \mathbf{x}    （花括号组，推荐）
\vx      →  \mathbf{x}    （单Token，x后面的字符作为参数）
\v{AB}   →  \mathbf{AB}   （花括号组内多个字符）
```

### 可重用的宏配置

如果多个渲染调用使用相同的宏，将宏对象提取为变量：

```javascript
const mathMacros = {
    "\\RR": "\\mathbb{R}",
    "\\NN": "\\mathbb{N}",
    "\\ZZ": "\\mathbb{Z}",
    "\\diff": "\\mathop{}\\!\\mathrm{d}#1",
    "\\pderiv": "\\frac{\\partial #1}{\\partial #2}",
    "\\v": "\\mathbf{#1}",
};

// 多个地方使用
katex.render("\\v{x}\\in\\RR^n", el1, {macros: mathMacros});
katex.render("\\pderiv{f}{x}", el2, {macros: mathMacros, displayMode: true});
```

## 在 LaTeX 中用 \newcommand 定义宏

KaTeX 支持在 LaTeX 表达式内部使用 `\newcommand` 定义宏，定义仅在当前表达式内有效：

```javascript
katex.render(`
    \\newcommand{\\biswap}[2]{#2\\leftrightarrow #1}
    \\biswap{a}{b}
`, el);
```

这等价于：

```javascript
katex.render("\\biswap{a}{b}", el, {
    macros: {
        "\\biswap": "#2\\leftrightarrow #1"
    }
});
```

### 带可选参数的 \newcommand

```javascript
// \newcommand{\cmd}[参数数][默认值]{定义}
katex.render(`
    \\newcommand{\\paren}[1][(]{\\left#1 ... \\right.}
    \\paren{x}        % 默认圆括号
    \\paren[{]x}      % 方括号
`, el);
```

注意：KaTeX 对 `\newcommand` 的可选参数支持有局限，与LaTeX不完全一致。

## 函数宏（动态展开）

宏的值可以是函数而非字符串，用于动态逻辑：

```javascript
katex.render("\\myop{a}{b}", el, {
    macros: {
        "\\myop": function(context) {
            // context 是 MacroExpander 实例
            // 消费两个参数
            const arg1 = context.consumeArg(false, "original");
            const arg2 = context.consumeArg(false, "original");
            // 返回展开字符串
            return "\\left\\langle " + arg1 + "\\;\\middle|\\;" + arg2 + "\\right\\rangle";
        }
    }
});
```

函数宏通过 MacroContextInterface 访问宏展开器的方法：

| 方法 | 作用 |
|------|------|
| `context.consumeArg()` | 消费一个参数（返回Token数组） |
| `context.expandNextToken()` | 展开下一个Token |
| `context.fetch()` | 获取下一个已展开Token |
| `context.switchMode(mode)` | 切换math/text模式 |

> **注意**：函数宏需要对 KaTeX 内部 API（MacroContextInterface）有较深理解，大多数场景使用字符串宏即可。

## 全局宏注册（__defineMacro）

`katex.__defineMacro()` 在全局层面注册宏，对所有后续渲染生效：

```javascript
// 在应用初始化时注册一次
katex.__defineMacro("\\RR", "\\mathbb{R}");
katex.__defineMacro("\\NN", "\\mathbb{N}");
katex.__defineMacro("\\ZZ", "\\mathbb{Z}");
katex.__defineMacro("\\diff", "\\mathop{}\\!\\mathrm{d}#1");
katex.__defineMacro("\\v", "\\mathbf{#1}");

// 之后所有渲染无需传递macros选项
katex.render("\\v{x}\\in\\RR^n", el);
katex.render("\\diff{x}", el2);
```

### 全局宏 vs 配置宏

| 特性 | settings.macros | __defineMacro |
|------|-----------------|---------------|
| 作用范围 | 单次render调用 | 全局，所有后续调用 |
| 适合场景 | 每个页面/组件有不同宏集 | 应用级统一宏定义 |
| 覆盖 | 可覆盖同名全局宏 | 覆盖之前的全局宏 |
| 与分组交互 | 受{...}分组作用域控制 | 在全局层，{...}内可临时遮蔽 |

## 使用 \def 定义宏

KaTeX也支持TeX原语 `\def`：

```javascript
katex.render(`
    \\def\\RR{\\mathbb{R}}
    \\def\\vec#1{\\mathbf{#1}}
    \\vec{x}\\in\\RR^3
`, el);
```

`\gdef`（全局def）不受分组作用域限制：

```javascript
katex.render(`
    {
        \\def\\a{局部}
        \\gdef\\b{全局}
    }
    \\b   % 正常输出"全局"
    % \\a  % 错误！\a在分组外不可见
`, el);
```

## 宏展开计数限制

复杂递归宏可能触发展开次数上限（默认1000）：

```javascript
// 如果出现 "Too many expansions" 错误
katex.render(complexExpr, el, {
    macros: myMacros,
    maxExpand: 5000  // 增大上限
});
```

## 实际场景：常用物理/数学宏集合

```javascript
const physicsMacros = {
    // 数集
    "\\RR": "\\mathbb{R}",
    "\\NN": "\\mathbb{N}",
    "\\ZZ": "\\mathbb{Z}",
    "\\CC": "\\mathbb{C}",
    // 微分与导数
    "\\diff": "\\mathop{}\\!\\mathrm{d}",
    "\\dd": "\\mathop{}\\!\\mathrm{d}",
    "\\dv[2]": "\\frac{\\mathrm{d}^{#1}#2}{\\mathrm{d}#3^{#1}}",
    "\\pdv": "\\frac{\\partial #1}{\\partial #2}",
    // 向量与矩阵
    "\\vb": "\\mathbf{#1}",
    "\\va": "\\vec{#1}",
    "\\hat": "\\hat{#1}",
    // 括号
    "\\lr": "\\left(#1\\right)",
    "\\lrs": "\\left[#1\\right]",
    "\\lrc": "\\left\\{#1\\right\\}",
    "\\lra": "\\left\\langle#1\\right\\rangle",
    "\\abs": "\\left|#1\\right|",
    "\\norm": "\\left\\|#1\\right\\|",
    // 概率统计
    "\\E": "\\mathbb{E}",
    "\\Var": "\\operatorname{Var}",
    "\\Cov": "\\operatorname{Cov}",
    // 缩写
    "\\const": "\\text{const}",
    "\\iff": "\\Longleftrightarrow",
    "\\implies": "\\Longrightarrow",
};

// 使用
katex.render(
    "\\E[X]=\\int_\\RR x\\,f(x)\\diff x",
    el, {macros: physicsMacros}
);
```

## 相关内容

- [宏系统](/concepts/09-macro-system.md)
- [宏展开器](/concepts/04-macro-expander.md)
- [函数注册表](/concepts/08-function-registry.md)
- [基础渲染示例](/examples/basic-render.md)
- [自定义扩展示例](/examples/custom-extension.md)
