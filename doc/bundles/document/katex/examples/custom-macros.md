---
type: Example
title: 自定义宏示例
description: 通过 settings.macros 和 __defineMacro 定义 KaTeX 宏，包括简单别名、带参数宏、函数宏、展开对象、共享 macros 对象与 \gdef 持久化，以及多用户场景下的宏安全边界。
tags: [katex, example, macro, defineMacro, newcommand, persistent-macros, gdef, security]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:40:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-api
    resource: /references/katex-website.md#web-api
    title: KaTeX 官网 API 页面
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
---

## settings.macros 配置方式

`settings.macros` 是最常用的自定义宏方式。宏值支持三种形式[^web-options]：

| 宏值形式 | 类型 | 用途 |
|---------|------|------|
| 字符串 | `string` | 简单展开，支持 `#1`~`#9` 参数占位符 |
| 函数 | `function` | 动态展开，接收 MacroExpander 实例并返回字符串 |
| 展开对象 | `{tokens, numArgs}` | 模拟 `\def`/`\let` 的底层 token 序列 |

### 简单别名（无参数宏）

最基本的用法是给现有命令起短名：

```javascript
katex.render("\\RR^n", el, {
    macros: {
        "\\RR": "\\mathbb{R}",
        "\\NN": "\\mathbb{N}",
        "\\ZZ": "\\mathbb{Z}",
        "\\QQ": "\\mathbb{Q}",
        "\\CC": "\\mathbb{C}",
        "\\eps": "\\varepsilon",
        "\\vphi": "\\varphi",
    }
});
```

渲染 `\RR^n` 等价于 `\mathbb{R}^n`。

### 带参数宏

使用 `#1`~`#9` 引用参数，KaTeX 通过 `#n` 的最大出现次数自动推断参数数量[^src]：

```javascript
katex.render("\\diff{x} + \\pderiv{f}{x}", el, {
    macros: {
        "\\diff": "\\mathop{}\\!\\mathrm{d}#1",
        "\\pderiv": "\\frac{\\partial #1}{\\partial #2}",
        "\\ddt": "\\frac{\\mathrm{d}#1}{\\mathrm{d}t}",
        "\\v": "\\mathbf{#1}",
        "\\T": "#1^{\\mathsf{T}}",
        "\\E": "\\mathbb{E}\\left[#1\\right]",
        "\\P": "\\mathbb{P}\\left(#1\\right)",
    }
});
```

`\pderiv{f}{x}` 使用了 `#1` 和 `#2`，因此接受两个参数，展开为 `\frac{\partial f}{\partial x}`。

`##` 在宏定义中转义为单个 `#`。

### 花括号参数与单 Token 参数

宏参数可以是花括号组或单个 Token：

```text
\v{x}    →  \mathbf{x}    （花括号组，推荐）
\vx      →  \mathbf{x}    （单 Token，x 后面的字符作为参数）
\v{AB}   →  \mathbf{AB}   （花括号组内多个字符）
```

### 展开对象（模拟 \let/\def）

展开对象以 token 序列形式定义宏，可精确控制展开行为，常用于模拟 `\let`[^web-options]：

```javascript
katex.render("\\realint_0^1 f(x)\\,dx", el, {
    macros: {
        "\\realint": {
            tokens: [{text: "\\int", noexpand: true}],
            numArgs: 0
        }
    }
});
```

`noexpand: true` 表示该 token 在宏展开阶段不被继续展开，等价于 TeX 中 `\let\realint=\int` 的效果。

### 函数宏（动态展开）

宏值可以是函数，接收宏展开器上下文并返回展开字符串[^web-options]：

```javascript
katex.render("\\myop{a}{b}", el, {
    macros: {
        "\\myop": function(context) {
            const arg1 = context.consumeArg(false, "original");
            const arg2 = context.consumeArg(false, "original");
            return "\\left\\langle " + arg1 + "\\;\\middle|\\;" + arg2 + "\\right\\rangle";
        }
    }
});
```

函数宏通过 MacroContextInterface 访问宏展开器方法：

| 方法 | 作用 |
|------|------|
| `context.consumeArg()` | 消费一个参数（返回 Token 数组） |
| `context.expandNextToken()` | 展开下一个 Token |
| `context.fetch()` | 获取下一个已展开 Token |
| `context.switchMode(mode)` | 切换 math/text 模式 |

> **注意**：函数宏接收的 MacroExpander 属内部 API，可能发生非向后兼容的变更[^web-options]。大多数场景使用字符串宏或展开对象即可。

## 持久宏：共享 macros 对象

KaTeX 的 `render`/`renderToString` 表面上是无状态调用，但通过传入**同一个** `macros` 对象可实现宏定义在多次调用间持久化[^web-api]。

### 基本共享模式

```javascript
const sharedMacros = {
    "\\RR": "\\mathbb{R}",
    "\\diff": "\\mathop{}\\!\\mathrm{d}#1",
};

katex.render("\\v{x}\\in\\RR^n", el1, {macros: sharedMacros});
katex.render("\\diff{x}", el2, {macros: sharedMacros, displayMode: true});
katex.renderToString("\\RR^3", {macros: sharedMacros});
```

关键点：必须传入**同一对象引用**，每次调用创建新对象无法实现持久化。

### \gdef 持久化

当 LaTeX 代码使用 `\gdef`（或 `\global\let`）定义宏时，KaTeX 会将定义写入传入的 `macros` 对象，使其在后续调用中可见[^web-api]：

```javascript
const macros = {};

katex.render("\\gdef\\half{\\tfrac{1}{2}}", el1, {macros});
katex.render("\\half + \\half = 1", el2, {macros});
```

第二个渲染调用能识别 `\half`，因为 `\gdef` 已将其插入同一个 `macros` 对象。

### 局部组与 globalGroup

默认情况下，`\begin{equation}`、`$$` 等构造创建局部组，`\def`、`\newcommand`、`\let` 的定义仅在组内可见，块外不可见；只有 `\gdef` 和 `\global\let` 能逃逸局部组[^web-options]。

设 `globalGroup: true` 可改变此行为，使顶层 `\def`/`\newcommand` 定义加入 `macros` 对象并在后续调用中使用：

```javascript
const macros = {};

katex.render("$$\\def\\foo{42}$$", elA, {macros});
// \foo 在外部不可见（$$ 创建局部组，默认 globalGroup: false）

katex.render("\\def\\bar{42}", elB, {macros, globalGroup: true});
katex.render("\\bar", elC, {macros, globalGroup: true});
// \bar 可见，因为 globalGroup: true 使顶层定义进入 macros 对象
```

### 可重用的宏配置

将常用宏集提取为模块，在应用初始化时一次性创建：

```javascript
const mathMacros = {
    "\\RR": "\\mathbb{R}",
    "\\NN": "\\mathbb{N}",
    "\\ZZ": "\\mathbb{Z}",
    "\\diff": "\\mathop{}\\!\\mathrm{d}#1",
    "\\pderiv": "\\frac{\\partial #1}{\\partial #2}",
    "\\v": "\\mathbf{#1}",
};

export function renderMath(expr, el, options = {}) {
    return katex.render(expr, el, {macros: mathMacros, ...options});
}
```

## 宏安全边界

持久宏可改变 KaTeX 行为（如重定义标准命令），必须关注其安全影响[^web-api]。

### 可信场景：共享 macros

在同一信任域内（如同一位作者的多篇文章、同一页面的多个公式块），共享 `macros` 对象可实现连续方程宏复用：

```javascript
const articleMacros = {};

document.querySelectorAll(".math-block").forEach(el => {
    katex.render(el.textContent, el, {
        macros: articleMacros,
        throwOnError: false,
    });
});
```

### 不可信场景：每消息独立 macros

处理多用户输入（如评论、聊天消息、论坛帖子）时，**必须为每条消息创建独立的 `macros` 对象**，不得跨用户或跨消息共享[^web-api]：

```javascript
function renderUserMessage(message, el) {
    katex.render(message, el, {
        macros: {},
        throwOnError: false,
        trust: false,
        maxExpand: 1000,
    });
}

messages.forEach(msg => {
    const el = document.createElement("div");
    renderUserMessage(msg.latex, el);
});
```

恶意用户可能通过 `\gdef` 重定义 `\frac`、`\sqrt` 等标准命令，若共享 `macros` 对象，后续所有用户的公式都会被污染。

### 安全检查清单

| 场景 | macros 对象 | globalGroup | trust |
|------|------------|-------------|-------|
| 单条可信公式 | 可复用预设对象 | false | 按需 |
| 同一作者多篇公式 | 共享同一对象 | false | 按需 |
| 多用户/不可信输入 | 每消息独立 `{}` | false | false |
| 需要 \gdef 跨块 | 共享对象 | false | 按需 |
| 需要顶层 \def 持久化 | 共享对象 | true | 可信内容才启用 |

## 在 LaTeX 中用 \newcommand 定义宏

KaTeX 支持在 LaTeX 表达式内部使用 `\newcommand` 定义宏，定义仅在当前表达式内有效：

```javascript
katex.render(`
    \\newcommand{\\biswap}[2]{#2\\leftrightarrow #1}
    \\biswap{a}{b}
`, el);
```

等价于：

```javascript
katex.render("\\biswap{a}{b}", el, {
    macros: {"\\biswap": "#2\\leftrightarrow #1"}
});
```

`\newcommand` 定义受局部组作用域控制，默认不会泄漏到 `macros` 对象外部。

## 使用 \def 定义宏

KaTeX 也支持 TeX 原语 `\def`：

```javascript
katex.render(`
    \\def\\RR{\\mathbb{R}}
    \\def\\vec#1{\\mathbf{#1}}
    \\vec{x}\\in\\RR^3
`, el);
```

`\gdef`（全局 def）不受分组作用域限制：

```javascript
katex.render(`
    {
        \\def\\a{局部}
        \\gdef\\b{全局}
    }
    \\b
`, el);
```

## 全局宏注册（__defineMacro）

`katex.__defineMacro()` 在全局层面注册宏，对所有后续渲染生效：

```javascript
katex.__defineMacro("\\RR", "\\mathbb{R}");
katex.__defineMacro("\\NN", "\\mathbb{N}");
katex.__defineMacro("\\diff", "\\mathop{}\\!\\mathrm{d}#1");
katex.__defineMacro("\\v", "\\mathbf{#1}");

katex.render("\\v{x}\\in\\RR^n", el);
katex.render("\\diff{x}", el2);
```

### 全局宏 vs 配置宏

| 特性 | settings.macros | __defineMacro |
|------|-----------------|---------------|
| 作用范围 | 单次 render 调用 | 全局，所有后续调用 |
| 适合场景 | 每个页面/组件有不同宏集 | 应用级统一宏定义 |
| 覆盖 | 可覆盖同名全局宏 | 覆盖之前的全局宏 |
| 安全隔离 | 可通过独立对象隔离 | 全局污染，无法按调用隔离 |

处理不可信输入时，不应使用 `__defineMacro`，因为它会影响所有调用且无法按请求隔离。

## 宏展开计数限制

复杂递归宏可能触发展开次数上限（默认 1000）[^web-options]：

```javascript
try {
    katex.render(complexExpr, el, {macros: myMacros});
} catch (e) {
    if (e.message.includes("Too many expansions")) {
        katex.render(complexExpr, el, {
            macros: myMacros,
            maxExpand: 5000,
        });
    }
}
```

不要对不可信输入设 `maxExpand: Infinity`，否则恶意宏循环可能导致拒绝服务。

## 实际场景：常用物理/数学宏集合

```javascript
const physicsMacros = {
    "\\RR": "\\mathbb{R}",
    "\\NN": "\\mathbb{N}",
    "\\ZZ": "\\mathbb{Z}",
    "\\CC": "\\mathbb{C}",
    "\\diff": "\\mathop{}\\!\\mathrm{d}",
    "\\dd": "\\mathop{}\\!\\mathrm{d}",
    "\\pdv": "\\frac{\\partial #1}{\\partial #2}",
    "\\vb": "\\mathbf{#1}",
    "\\va": "\\vec{#1}",
    "\\lr": "\\left(#1\\right)",
    "\\lrs": "\\left[#1\\right]",
    "\\lrc": "\\left\\{#1\\right\\}",
    "\\lra": "\\left\\langle#1\\right\\rangle",
    "\\abs": "\\left|#1\\right|",
    "\\norm": "\\left\\|#1\\right\\|",
    "\\E": "\\mathbb{E}",
    "\\Var": "\\operatorname{Var}",
    "\\Cov": "\\operatorname{Cov}",
    "\\const": "\\text{const}",
    "\\iff": "\\Longleftrightarrow",
    "\\implies": "\\Longrightarrow",
};

katex.render(
    "\\E[X]=\\int_\\RR x\\,f(x)\\diff x",
    el, {macros: physicsMacros}
);
```

## 相关内容

- [宏系统](/concepts/09-macro-system.md)
- [宏展开器](/concepts/04-macro-expander.md)
- [函数注册表](/concepts/08-function-registry.md)
- [配置选项](/concepts/10-settings-options.md)
- [安全信任示例](/examples/security-trust.md)
- [基础渲染示例](/examples/basic-render.md)
- [自定义扩展示例](/examples/custom-extension.md)

[^web-api]: 官网 API 页面，https://katex.org/docs/api
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
[^src]: 宏参数 `#1`~`#9` 与 `##` 转义规则见 [src/MacroExpander.ts](https://github.com/KaTeX/KaTeX/blob/v0.18.4/src/MacroExpander.ts)
