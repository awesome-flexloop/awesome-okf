---
type: Concept
title: 函数注册表
description: KaTeX defineFunction机制的工作原理，FunctionSpec结构，handler/htmlBuilder/mathmlBuilder三要素，以及如何自定义LaTeX命令。
tags: [katex, function, registry, extension, defineFunction]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:35:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:35:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 函数注册表的角色

KaTeX 的核心引擎（Lexer+MacroExpander+Parser+buildTree）本身不包含任何具体的 LaTeX 命令实现。所有命令（`\frac`、`\sqrt`、`\alpha`、`\color` 等）都通过**函数注册表**插件式注册。这是 KaTeX 可扩展性的核心机制。

函数注册通过 `defineFunction()` 函数完成，定义在 [src/defineFunction.ts](https://github.com/KaTeX/KaTeX/blob/main/src/defineFunction.ts)。

## 三个全局注册表

`defineFunction()` 维护三个全局 Map：

```typescript
// 函数规格表：命令名 → FunctionSpec
_functions: Record<string, FunctionSpec<any>> = {};

// HTML构建器表：节点类型 → HtmlBuilder
_htmlGroupBuilders: Record<string, HtmlBuilderData> = {};

// MathML构建器表：节点类型 → MathMLBuilder
_mathmlGroupBuilders: Record<string, MathMLBuilderData> = {};
```

注册一个命令需要向这三个表分别提供信息。

## defineFunction() API

```typescript
function defineFunction<N extends NodeType>({
    type: N,                 // 节点类型（ParseNode的type字段）
    names: string[],         // 触发的命令名列表（如 ["\\frac", "\\dfrac", "\\tfrac"]）
    props?: {                // 属性约束
        numArgs?: number;            // 必选参数数量
        argTypes?: ArgType[];        // 每个参数的类型
        numOptionalArgs?: number;    // 可选参数数量
        allowedInText?: boolean;     // 是否允许在text模式中使用
        allowedInMath?: boolean;     // 是否允许在math模式中使用
        allowedInArgument?: boolean; // 是否允许在其他函数参数中使用
        infix?: boolean;             // 是否为中缀运算符
        primitive?: boolean;         // 是否为TeX原语（跳过参数展开）
        primitiveMarkup?: boolean;   // 原始标记
    },
    handler: (context: FunctionContext, args: AnyParseNode[], optArgs: AnyParseNode[])
        => AnyParseNodeByType<N>;     // 解析时调用，返回ParseNode
    htmlBuilder?: (group: AnyParseNodeByType<N>, options: Options)
        => HtmlDomSpan;               // HTML构建时调用，返回虚拟DOM
    mathmlBuilder?: (group: AnyParseNodeByType<N>, options: Options)
        => MathVdomSpan;              // MathML构建时调用，返回虚拟DOM
});
```

## 注册流程示例：以 \frac 为例

以 `\frac{a}{b}`（分数命令）为例，注册过程如下：

### 1. 定义 FunctionSpec

```typescript
defineFunction({
    type: "frac",
    names: ["\\frac", "\\dfrac", "\\tfrac"],
    props: {numArgs: 2},    // 需要两个参数：分子、分母
    handler({parser, token}, args) {
        const numerator = args[0];    // 第一个参数是分子
        const denominator = args[1];  // 第二个参数是分母
        return {
            type: "frac",
            mode: parser.mode,
            loc: token.loc,
            num: numerator,
            denom: denominator,
            size: "auto",
        };
    },
    htmlBuilder(group, options) {
        // 构建分数的HTML结构
        const numer = buildGroup(group.num, options.havingStyle(options.style.fracNum()));
        const denom = buildGroup(group.denom, options.havingStyle(options.style.fracDen()));
        const rule = makeLineSpan("frac-line", options);
        // ... 组装为上下排列的vlist
        return makeSpan(["mfrac"], [numerWrapper, rule, denomWrapper]);
    },
    mathmlBuilder(group, options) {
        // 构建 <mfrac> MathML元素
        return new mathMLTree.MathNode("mfrac", [
            buildGroup(group.num, options),
            buildGroup(group.denom, options),
        ]);
    },
});
```

### 2. 解析阶段（handler）

当 Parser 遇到 `\frac` 时：
1. 查询 `_functions["\\frac"]` 获取 FunctionSpec
2. 检查模式允许性（math模式允许，text模式不允许）
3. 调用 `parseArguments()` 消费两个花括号组参数 `{a}` 和 `{b}`
4. 调用 handler，返回 `{type: "frac", num: a_node, denom: b_node, ...}` ParseNode

### 3. HTML构建阶段（htmlBuilder）

当 buildHTML 遇到 `type: "frac"` 的节点时：
1. 查询 `_htmlGroupBuilders["frac"]` 获取 builder
2. 分子使用 `fracNum()` 样式（上标样式），分母使用 `fracDen()` 样式（下标样式）
3. 分子在上、分数线在中、分母在下，垂直堆叠
4. 返回包含完整分数结构的 Span

### 4. MathML构建阶段（mathmlBuilder）

当 buildMathML 遇到 `type: "frac"` 节点时：
1. 查询 `_mathmlGroupBuilders["frac"]` 获取 builder
2. 生成 `<mfrac><mrow>分子</mrow><mrow>分母</mrow></mfrac>` MathML 结构

## 同一命令族的多命令注册

多个命令名可以映射到同一个 type 和 builder，通过 handler 中的 token 参数区分：

```typescript
defineFunction({
    type: "genfrac",
    names: ["\\frac", "\\dfrac", "\\tfrac", "\\binom", "\\dbinom", "\\tbinom"],
    props: {numArgs: 2},
    handler({parser, token}, args) {
        let hasBarLine = true;
        let size = "auto";
        switch (token.text) {
            case "\\dfrac": case "\\dbinom": size = "display"; break;
            case "\\tfrac": case "\\tbinom": size = "text"; break;
            case "\\binom": case "\\dbinom": case "\\tbinom": hasBarLine = false; break;
        }
        // ...
    },
});
```

## 参数类型（ArgType）

`argTypes` 数组指定每个参数的解析方式：

| ArgType | 说明 |
|---------|------|
| `"math"` | 在 math 模式下解析参数（默认） |
| `"text"` | 在 text 模式下解析参数 |
| `"color"` | 参数解析为颜色值（支持 `red`、`#ff0000`、`rgb(255,0,0)`） |
| `"size"` | 参数解析为尺寸值（如 `1em`、`10pt`、`2ex`） |
| `"url"` | 参数解析为 URL（转义 `#$%&~_^\{}`前的反斜杠） |
| `"raw"` | 原样文本参数（含嵌套花括号，不做解析） |
| `"hbox"` | 在 hbox 模式下解析（类似text但包含水平模式） |
| `"primitive"` | TeX原语参数（跳过宏展开） |
| `"original"` | 保持当前模式解析（用于 \textcolor 的第二个参数等） |

## 可选参数

通过 `numOptionalArgs` 指定可选参数数量，可选参数用 `[...]` 包裹。例如 `\sqrt[3]{x}` 中 `[3]` 是可选参数（开方次数），`{x}` 是必选参数：

```typescript
defineFunction({
    type: "sqrt",
    names: ["\\sqrt"],
    props: {numArgs: 1, numOptionalArgs: 1},  // 1必选+1可选
    handler({parser}, args, optArgs) {
        const index = optArgs[0];  // 可选参数：开方次数
        const body = args[0];      // 必选参数：被开方表达式
        return {type: "sqrt", body, index};
    },
    // ...
});
```

## 中缀命令

`infix: true` 标记中缀运算符，如 `\over`、`\choose`。中缀命令不由 parseFunction 直接处理，而是在 `handleInfixNodes()` 中后处理。

## defineEnvironment()

环境注册与函数注册类似，但用于 `\begin{xxx}...\end{xxx}` 形式：

```typescript
defineEnvironment({
    type: "array",
    names: ["array"],
    props: {numArgs: 1, argTypes: ["raw"] /* 列格式 */},
    handler({parser}, args /* 列格式 */) {
        // 解析 \begin{array}{cc}...\end{array} 中的内容
        return {type: "array", ...};
    },
    htmlBuilder, mathmlBuilder,
});
```

环境与函数的区别：
- 环境有明确的 `\begin` 和 `\end` 标记
- 环境体内容在 handler 中通过 `parser.parseExpression()` 主动消费
- 环境注册在 `_environments` 表中而非 `_functions`

## 公开扩展API

KaTeX 通过 `katex.__defineFunction`、`katex.__defineMacro`、`katex.__defineSymbol` 暴露扩展能力（注意：这些是内部API，前缀双下划线表示不稳定）：

```javascript
katex.__defineFunction({
    type: "mycmd",
    names: ["\\mycmd"],
    props: {numArgs: 1},
    handler(context, args) {
        return {type: "mycmd", mode: context.parser.mode, body: args[0]};
    },
    htmlBuilder(group, options) {
        return katex.__domTree.makeSpan(["mycmd"],
            [buildGroup(group.body, options)]);
    },
    mathmlBuilder(group, options) {
        // MathML构建
    },
});
```

## 函数文件组织

[src/functions/](https://github.com/KaTeX/KaTeX/blob/main/src/functions/) 目录下有43个 .ts 文件，每个文件对应一类命令：

| 文件 | 覆盖命令族 |
|------|-----------|
| `genfrac.ts` | `\frac`、`\dfrac`、`\tfrac`、`\binom`、`\genfrac` 等分数族 |
| `supsub.ts` | 自动导入（处理 ^ 和 _） |
| `op.ts` | `\sum`、`\int`、`\lim`、`\sin`、`\operatorname` 等算符族 |
| `delimsizing.ts` | `\left`、`\right`、`\big`、`\Big` 等分隔符尺寸命令 |
| `sqrt.ts` | `\sqrt` |
| `accent.ts` / `accentunder.ts` | `\hat`、`\bar`、`\vec`、`\underline` 等重音 |
| `color.ts` | `\color`、`\textcolor`、`\colorbox` |
| `font.ts` | `\mathbf`、`\mathit`、`\mathbb`、`\mathcal` 等字体命令 |
| `arrow.ts` | `\rightarrow`、`\xrightarrow` 等箭头 |
| `enclose.ts` | `\cancel`、`\bcancel`、`\boxed`、`\fbox` 等包围命令 |
| `mclass.ts` | `\mathord`、`\mathop`、`\mathbin` 等手动类型设置 |
| `text.ts` | `\text`、`\textrm`、`\textbf` 等文本命令 |
| `raisebox.ts` | `\raisebox` |
| `rule.ts` | `\rule`（画线/矩形） |
| `kern.ts` | `\kern`、`\hspace`（间距） |
| `smash.ts` | `\smash`（取消高度） |
| `phantom.ts` | `\phantom`、`\hphantom`、`\vphantom`（幻影间距） |
| `hbox.ts` | `\hbox`（水平盒子） |
| `href.ts` | `\href`、`\url` |
| ... | ... |

[src/environments/](https://github.com/KaTeX/KaTeX/blob/main/src/environments/) 目录包含：
- `array.ts`：`array`、`matrix`、`pmatrix` 等矩阵/表格环境
- `cd.ts`：CD（commutative diagram，交换图）环境

## 编写自定义函数的要点

1. **三要素不可少**：handler（解析）、htmlBuilder（HTML渲染）、mathmlBuilder（MathML渲染）
2. **Options不可变传递**：在 builder 中调用 `buildGroup`/`buildExpression` 处理子节点时，必须使用 `options.havingStyle()` 等方法创建新 Options，不能直接修改 options 属性
3. **mode检查**：通过 `allowedInText`/`allowedInMath` 控制命令在不同模式下的可用性
4. **参数解析**：使用 `parseArguments` 消费参数，不要直接操作 gullet/fetch
5. **返回虚拟DOM**：htmlBuilder 必须返回 domTree 虚拟节点（使用 makeSpan/makeFragment 等），不能返回字符串或真实DOM
6. **CSS类名**：自定义节点使用的CSS类名需要配合对应的CSS规则，否则视觉效果不正确

## 相关概念

- [架构总览](02-architecture-overview.md)
- [解析器（Parser）](05-parser.md)
- [渲染管线](06-render-pipeline.md)
- [宏系统](09-macro-system.md)
- [自定义扩展示例](../examples/custom-extension.md)
