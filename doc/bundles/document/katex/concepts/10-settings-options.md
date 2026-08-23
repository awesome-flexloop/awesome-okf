---
type: Concept
title: 配置系统
description: KaTeX 的 Settings 与 Options 双配置层，SETTINGS_SCHEMA 选项定义，strict/trust/globalGroup 默认值与用法，以及 Options 不可变状态传递模型。
tags: [katex, settings, options, configuration, strict, trust]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T21:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T21:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
---

## 配置系统双层模型

KaTeX 使用两个层次的配置对象：

- **Settings**：用户传入的原始配置（`katex.render()` 的第三个参数），定义在 [src/Settings.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Settings.ts)
- **Options**：渲染过程中内部使用的状态对象（包含当前样式、字号、颜色等），定义在 [src/Options.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Options.ts)

```
用户配置 (SettingsOptions)
      │
      ▼
  new Settings(options)   验证+默认值填充
      │
      ▼
optionsFromSettings(settings)  创建渲染Options
      │
      ▼
buildTree / buildHTML / buildMathML  渲染阶段使用
```

## Settings：用户配置层

### SETTINGS_SCHEMA

所有可用选项通过 `SETTINGS_SCHEMA` 数组定义（类似 JSON Schema），每个选项包含：

```typescript
{
    "key": "displayMode",
    "type": "boolean",
    "default": false
}
```

Settings 构造函数根据 SCHEMA 验证用户输入并填充默认值。

### 完整选项列表

以下默认值以官网 Options 页面为权威来源；`strict`、`trust`、`globalGroup` 等选项的默认值在源码类型定义中未以人类可读方式标注，须以官网为准。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `displayMode` | `boolean` | `false` | 显示模式（块级居中，大符号；禁用最外层自动换行） |
| `output` | `"html" \| "mathml" \| "htmlAndMathml"` | `"htmlAndMathml"` | 输出格式；htmlAndMathml 输出 HTML 供视觉并含 MathML 供无障碍 |
| `leqno` | `boolean` | `false` | 公式编号渲染在左侧（leqno = left equation numbers） |
| `fleqn` | `boolean` | `false` | 公式左对齐并带 2em 左边距（fleqn = flush left equations） |
| `throwOnError` | `boolean` | `true` | 解析错误时抛出 ParseError；设为 `false` 则渲染错误文本 |
| `errorColor` | `string` | `"#cc0000"` | throwOnError=false 时不支持命令和无效 LaTeX 的渲染颜色 |
| `macros` | `object` | `{}` | 自定义宏映射，详见下方 [macros 宏配置](#macros-宏配置) |
| `colorIsTextColor` | `boolean` | `false` | 设为 `true` 使 `\color` 行为类似 `\textcolor`（两参数模式） |
| `minRuleThickness` | `number` | 未设置 | 分数线、根号、array 竖线、边框等的最小粗细（em）；通常值为 0.04，生效取值约 0.05 或 0.06；负值被忽略 |
| `maxSize` | `number` | `Infinity` | 用户指定尺寸（如 `\rule`）的上限（em） |
| `maxExpand` | `number` | `1000` | 宏展开次数上限；设为 `Infinity` 时完全展开 |
| `strict` | `boolean \| string \| function` | `"warn"` | 严格模式级别，详见下方 [strict 严格模式](#strict-严格模式) |
| `trust` | `boolean \| function` | `false` | 是否信任输入，控制潜在危险命令，详见下方 [trust 信任模式](#trust-信任模式) |
| `globalGroup` | `boolean` | `false` | 设为 `true` 时在全局组中运行，使顶层 `\def`/`\newcommand` 写入 macros 参数 |

### strict 严格模式

`strict` 选项控制 KaTeX 对非标准或不推荐 LaTeX 用法的处理。**默认值为 `"warn"`**（不是 `false`）。

| 值 | 行为 |
|----|------|
| `"warn"`（默认） | 通过 `console.warn` 输出警告 |
| `false` / `"ignore"` | 静默忽略，允许便利但非 (Xe)LaTeX 支持的特性 |
| `true` / `"error"` | LaTeX 忠实模式，对违规抛出 ParseError |
| `function(errorCode, errorMsg, token)` | 自定义处理函数，返回 `"ignore"` / `"error"` / `"warn"` |

strict 会检查的 errorCode 包括：

- 抛错类：`"unknownSymbol"`（未知 Unicode 符号）、`"unicodeTextInMathMode"`（数学模式中使用 Unicode 文本字符）、`"mathVsTextUnits"`（数学/文本命令与单位/模式不匹配）、`"commentAtEnd"`（无终止换行的 `%` 注释）、`"htmlExtension"`（`\html` 前缀命令，需放宽此设置）
- 行为类：`"newLineInDisplayMode"`（显示模式中使用 `\\` 或 `\newline`，严格模式下不产生换行）

示例：

```javascript
katex.render(expr, el, {
    strict: function(errorCode, errorMsg, token) {
        if (errorCode === "unknownSymbol") return "ignore";
        return "warn";
    }
});
```

### trust 信任模式

`trust` 选项控制是否允许可能加载外部资源或改变 HTML 属性的命令（如 `\url`、`\href`、`\includegraphics`）。**默认值为 `false`**，此时这些命令以 errorColor 渲染为错误状态。

| 值 | 行为 |
|----|------|
| `false`（默认） | 阻止所有潜在危险命令 |
| `true` | 允许所有此类命令（仅在完全信任输入时使用） |
| `function(context)` | 自定义判断函数，接收 context 对象，返回 `true`/`false` |

trust context 对象包含以下字段（按命令类型不同）：

| 命令 | context 字段 |
|------|-------------|
| `\url`、`\href`、`\includegraphics` | `{ command, url, protocol }` |
| `\htmlClass` | `{ command, class }` |
| `\htmlId` | `{ command, id }` |
| `\htmlStyle` | `{ command, style }` |
| `\htmlData` | `{ command, attributes }` |

其中 `protocol` 为小写字符串（如 `"http"`、`"https"`）；相对 URL 的 protocol 为 `"_relative"`。

示例（只允许 HTTPS 和相对路径链接）：

```javascript
katex.render(expr, el, {
    trust: function(context) {
        if (context.protocol === "https") return true;
        if (context.protocol === "_relative") return true;
        return false;
    }
});
```

> **安全提示**：处理不可信输入时应保持 `trust: false`，如需启用部分命令请使用自定义函数按协议/命令白名单放行。KaTeX 生成的 HTML 仍建议进行消毒，白名单需包含部分 SVG 和 MathML 以支持全部功能。详见 [安全与错误处理](/concepts/18-security-and-errors.md)。

### macros 宏配置

`macros` 选项是一个键值对集合。键为以反斜杠开头的命令名（如 `"\\foo"`）或单字符（如 `"α"`），值支持三种形式：

**1. 字符串（简单展开）**

支持 `#1`~`#9` 参数占位符，`##` 转义为 `#`：

```javascript
katex.render(expr, el, {
    macros: {
        "\\RR": "\\mathbb{R}",
        "\\frac": "\\frac{#1}{#2}"
    }
});
```

**2. 函数（动态展开）**

函数接收 `MacroExpander` 实例并返回展开字符串。注意：MacroExpander 为内部 API，可能发生非向后兼容的变更：

```javascript
katex.render(expr, el, {
    macros: {
        "\\foo": function(expander) {
            return "\\bar";
        }
    }
});
```

**3. 展开对象（模拟 `\let`）**

包含 `tokens` 和 `numArgs` 的对象，可模拟 `\let` 结果：

```javascript
katex.render(expr, el, {
    macros: {
        "\\realint": { tokens: [{ text: "\\int", noexpand: true }], numArgs: 0 }
    }
});
```

`macros` 对象在 LaTeX 代码通过 `\gdef`、`\global\let`（或 `globalGroup` 下的 `\def`/`\newcommand`/`\let`）定义宏时会被修改。传入同一对象可使多次 `render`/`renderToString` 调用共享宏状态。详见 [快速开始·持久宏](/concepts/01-getting-started.md#持久宏persistent-macros)。

### globalGroup

`globalGroup` 默认为 `false`。默认行为下，`$$`、`\begin{equation}` 等构造创建局部组，阻止 `\gdef` 以外的宏定义在块外可见。设为 `true` 时，KaTeX 代码在全局组中运行，顶层 `\def`/`\newcommand` 定义的宏会加入 macros 参数，可在后续渲染调用中使用。

### 错误处理

当 `throwOnError` 为 `false` 时，解析错误不会中断渲染，而是：

1. 将不支持的命令渲染为文本、无效 LaTeX 以源码形式渲染（hover 文本显示错误消息）
2. 使用 `errorColor` 指定的颜色
3. 添加 `.katex-error` CSS 类

```javascript
katex.render("\\invalid", el, {
    throwOnError: false,
    errorColor: "#cc0000"
});
```

## Options：渲染状态层

Options 是渲染阶段的内部状态对象，携带当前渲染上下文的所有视觉属性：

```typescript
class Options {
    static BASESIZE = 6;

    style: Style;
    color: string | undefined;
    size: number;
    textSize: number;
    phantom: boolean;
    font: string;
    fontFamily: string;
    fontWeight: string;
    fontShape: string;
    sizeMultiplier: number;
    maxSize: number;
    minRuleThickness: number;
}
```

### 不可变设计模式

Options 采用**不可变（immutable）**设计：所有修改方法返回新实例，不修改自身。这彻底避免了子树渲染污染父节点状态的问题，是 CSS 继承模型在 JavaScript 中的正确实现。

```typescript
const redOptions = options.withColor("red");
buildGroup(childNode, redOptions);
```

Options 提供的 with*/having* 方法：

| 方法 | 作用 |
|------|------|
| `havingStyle(style): Options` | 返回指定 Style 的新 Options |
| `withColor(color): Options` | 返回指定颜色的新 Options |
| `withColorTentative(color): Options` | 暂设颜色（color 为 undefined 时不改变） |
| `havingSize(size): Options` | 返回指定字号的新 Options |
| `havingCrampedStyle(): Options` | 返回压缩（cramped）样式的新 Options |
| `havingPhantom(): Options` | 返回幻影模式的新 Options |
| `withFont(font): Options` | 返回指定数学字体的新 Options |
| `withTextFont(...): Options` | 返回指定文本字体的新 Options |
| `withStyle(style): Options` | 同 havingStyle |

### extend()：浅拷贝实现

所有 with* 方法内部调用 `extend()` 创建新实例：

```typescript
extend(attributes: Partial<Options>): Options {
    return new Options(this, attributes);
}

constructor(base?: Options, override?: Partial<Options>) {
    if (base) {
        Object.setPrototypeOf(this, base);
    }
    if (override) {
        Object.assign(this, override);
    }
}
```

新 Options 对象以原 Options 为原型，覆盖属性直接设置在实例上，实现了浅拷贝效果，同时避免逐个复制所有属性。Style 只有 8 种预创建实例（0-7），Options 的 extend 是浅拷贝，因此不可变设计的实际开销很小。

### optionsFromSettings()

从 Settings 创建初始 Options：

```typescript
function optionsFromSettings(settings: Settings): Options {
    const style = settings.displayMode
        ? Style.DISPLAY
        : Style.TEXT;
    return new Options({
        style,
        size: Options.BASESIZE,
        textSize: Options.BASESIZE,
        sizeMultiplier: 1.0,
        maxSize: settings.maxSize,
        minRuleThickness: settings.minRuleThickness,
        phantom: false,
    });
}
```

## 样式与字号映射

字号索引 0~10（共 11 项）对应 LaTeX 中的 `\tiny` 到 `\HUGE`，其中索引 5 为 `\normalsize`（`BASESIZE = 6`，数组下标 `size-1 = 5`）：

| 索引 | 命令 | 倍数 |
|------|------|------|
| 0 | `\tiny` | 0.5 |
| 1 | `\scriptsize` | 0.6 |
| 2 | `\footnotesize` | 0.7 |
| 3 | `\small` | 0.8 |
| 4 | `\normalsize`-1 | 0.9 |
| 5 | `\normalsize` | 1.0 |
| 6 | `\large` | 1.2 |
| 7 | `\Large` | 1.44 |
| 8 | `\LARGE` | 1.728 |
| 9 | `\huge` | 2.074 |
| 10 | `\HUGE` | 2.488 |

sizeStyleMap 进一步将每个字号在不同 Style 下映射到实际的字号索引（处理 script/scriptscript 样式下的字号缩放）。

## 相关概念

- [样式系统](/concepts/11-style-system.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [虚拟DOM树](/concepts/07-dom-tree.md)
- [宏系统](/concepts/09-macro-system.md)
- [安全与错误处理](/concepts/18-security-and-errors.md)
- [错误处理示例](/examples/error-handling.md)
