---
type: Example
title: 自定义扩展示例
description: 使用 __defineFunction 添加自定义 LaTeX 命令，包括装饰命令、无参数符号命令和带参数命令；遵循 v0.18.4 API 规范（顶层 props 字段），同时提供 htmlBuilder 与 mathmlBuilder 以满足无障碍要求。
tags: [katex, example, extension, defineFunction, custom, domTree, mathml, accessibility]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:40:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-migration
    resource: /references/katex-website.md#web-migration
    title: KaTeX 官网 Migration 页面
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
---

## 扩展 API 概览

KaTeX 默认导出对象上暴露以下扩展 API（`__` 前缀表示内部 API，未来版本可能变更）[^src]：

| API | 作用 |
|-----|------|
| `katex.__defineFunction(spec)` | 注册新的 LaTeX 函数命令 |
| `katex.__defineMacro(name, body)` | 注册全局宏 |
| `katex.__defineSymbol(mode, family, cls, char, name)` | 注册单个符号 |
| `katex.__setFontMetrics(family, metrics)` | 扩展字体度量 |
| `katex.__domTree` | 虚拟 DOM 节点类：Span、Anchor、SymbolNode、SvgNode、PathNode、LineNode |
| `katex.__renderToDomTree(expr, options)` | 渲染为虚拟 DOM 树（HTML+MathML） |
| `katex.__renderToHTMLTree(expr, options)` | 渲染为虚拟 DOM 树（仅 HTML） |

> **版本注意**：v0.17.0 起 `__defineFunction` 的属性不再包裹在 `props` 中，需将 `numArgs`、`allowedInText` 等字段直接放在定义对象顶层[^web-migration]。本示例基于 v0.18.4。

## defineFunction 规范结构

`__defineFunction` 接收一个 FunctionSpec 对象[^src]：

```javascript
katex.__defineFunction({
    type: "nodeType",
    names: ["\\cmd"],
    numArgs: 0,
    argTypes: [],
    allowedInText: false,
    allowedInMath: true,
    allowedInArgument: false,
    infix: false,
    primitive: false,
    handler({parser, token, funcName}, args) { /* 返回 ParseNode */ },
    htmlBuilder(group, options) { /* 返回虚拟 DOM 节点 */ },
    mathmlBuilder(group, options) { /* 返回 MathML 节点 */ },
});
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | ParseNode 类型标识，builder 中通过 `group.type` 识别 |
| `names` | string[] | 命令名数组，支持一个实现注册多个别名 |
| `numArgs` | number | 必填参数数量（0~9） |
| `numOptionalArgs` | number | 可选参数数量 |
| `argTypes` | string[] | 各参数的类型（color/size/url/raw/original/hbox/primitive/math/text） |
| `allowedInText` | boolean | 是否允许在文本模式中使用 |
| `allowedInMath` | boolean | 是否允许在数学模式中使用 |
| `handler` | function | 解析阶段回调，返回 ParseNode |
| `htmlBuilder` | function | HTML 渲染阶段回调，返回 domTree 节点 |
| `mathmlBuilder` | function | MathML 渲染阶段回调，返回 MathML 节点 |

### 无障碍要求

KaTeX 默认输出 HTML+MathML 双格式（`output: "htmlAndMathml"`），MathML 供屏幕阅读器识别语义。**自定义函数必须同时提供 `htmlBuilder` 和 `mathmlBuilder`**，缺少 mathmlBuilder 会导致屏幕阅读器无法读取自定义命令[^src]。

## 示例 1：无参数符号命令（\checkbox）

最简单的扩展：注册一个渲染为 Unicode 符号的命令，无需消费参数。

```javascript
import katex from "katex";
import {MathNode, TextNode} from "katex/src/mathMLTree";

katex.__defineFunction({
    type: "checkbox",
    names: ["\\checkbox"],
    numArgs: 0,
    allowedInText: true,
    allowedInMath: true,
    handler({parser}) {
        return {type: "checkbox", mode: parser.mode};
    },
    htmlBuilder(group, options) {
        const {Span, SymbolNode} = katex.__domTree;
        return new Span(
            ["mord"],
            [new SymbolNode("\u2610", 0.8, 0.0, 0, 0, 0.8)]
        );
    },
    mathmlBuilder(group, options) {
        return new MathNode("mtext", [new TextNode("\u2610")]);
    },
});

katex.render("\\checkbox \\text{未完成}", el);
```

`SymbolNode`（HTML）构造参数为 `(text, height, depth, italic, skew, width)`，这些度量值影响排版对齐。MathML 节点 `MathNode`/`TextNode` 需从 `katex/src/mathMLTree` 导入，不通过 `__domTree` 暴露。

## 示例 2：带参数的装饰命令（\circled）

注册一个接收一个参数并用圆圈包围的命令。由于递归渲染任意 ParseNode 需要内部 `buildGroup`（未公开暴露），本示例通过从 KaTeX 源码导入内部构建模块实现：

```javascript
import katex from "katex";
import {buildGroup as buildHTMLGroup} from "katex/src/buildHTML";
import {buildGroup as buildMathMLGroup} from "katex/src/buildMathML";

katex.__defineFunction({
    type: "circled",
    names: ["\\circled"],
    numArgs: 1,
    allowedInText: true,
    allowedInMath: true,
    handler({parser, token}, args) {
        return {
            type: "circled",
            mode: parser.mode,
            loc: token.loc,
            body: args[0],
        };
    },
    htmlBuilder(group, options) {
        const {Span} = katex.__domTree;
        const body = buildHTMLGroup(group.body, options);
        return new Span(
            ["mord", "circled"],
            [body],
            {
                style: {
                    display: "inline-block",
                    border: "1px solid currentColor",
                    "border-radius": "50%",
                    padding: "0 0.3em",
                    "min-width": "1.2em",
                    "text-align": "center",
                    "box-sizing": "border-box",
                }
            }
        );
    },
    mathmlBuilder(group, options) {
        return buildMathMLGroup(group.body, options);
    },
});

katex.render("\\circled{x} + \\circled{1}", el);
```

> **说明**：`buildGroup` 是 KaTeX 内部分发函数，接收单个 `AnyParseNode` 和 `Options`，委托给已注册的 htmlBuilder/mathmlBuilder。默认导出的 `buildHTML(tree, options)` 接收 ParseNode **数组**并返回整棵 DomSpan（含 display 包装），`buildMathML(tree, texExpression, options, isDisplayMode, forMathmlOnly)` 需要 5 个参数并返回 `<math><semantics>` 包装——二者用于构建完整表达式，不适合嵌入自定义 builder 的子节点。这些内部 API 不包含在公共 API 中，从 `katex/src/` 深度导入需要打包工具（webpack/rollup）配置，且不保证跨版本稳定。若不想依赖内部模块，可直接操作 `katex.__domTree` 节点类手动构建 HTML 子树，但无法自动处理任意嵌套数学表达式；MathML 节点需从 `katex/src/mathMLTree` 导入。

### 配套 CSS

```css
.katex .circled {
    line-height: 1.2;
}
```

## 示例 3：使用 __defineSymbol 注册符号

对于仅映射到单个字符的命令，`__defineSymbol` 比 `__defineFunction` 更简洁：

```javascript
katex.__defineSymbol(
    "math",
    "main",
    "mord",
    "\u25ca",
    "\\diamond"
);

katex.render("A\\diamond B", el);
```

参数依次为：模式（`"math"`/`"text"`）、字体族、数学类（`mord`/`mop`/`mbin`/`mrel` 等）、Unicode 字符、命令名。

## 示例 4：自包含 IIFE 扩展

推荐将扩展包装在 IIFE 中，在 KaTeX 加载后注册：

```javascript
import katex from "katex";
import {MathNode, TextNode} from "katex/src/mathMLTree";

(function() {
    const {Span, SymbolNode} = katex.__domTree;

    katex.__defineFunction({
        type: "checkedbox",
        names: ["\\checked"],
        numArgs: 0,
        allowedInText: true,
        allowedInMath: true,
        handler({parser}) {
            return {type: "checkedbox", mode: parser.mode};
        },
        htmlBuilder() {
            return new Span(
                ["mord"],
                [new SymbolNode("\u2611", 0.8, 0.0, 0, 0, 0.8)]
            );
        },
        mathmlBuilder() {
            return new MathNode("mtext", [new TextNode("\u2611")]);
        },
    });

    katex.__defineFunction({
        type: "emptybox",
        names: ["\\square"],
        numArgs: 0,
        allowedInText: true,
        allowedInMath: true,
        handler({parser}) {
            return {type: "emptybox", mode: parser.mode};
        },
        htmlBuilder() {
            return new Span(
                ["mord"],
                [new SymbolNode("\u2610", 0.8, 0.0, 0, 0, 0.8)]
            );
        },
        mathmlBuilder() {
            return new MathNode("mtext", [new TextNode("\u2610")]);
        },
    });
})();

katex.render("\\square \\text{待办} \\quad \\checked \\text{完成}", el);
```

## htmlBuilder 编写要点

### 虚拟 DOM 节点

通过 `katex.__domTree` 访问虚拟节点类[^src]：

```javascript
const {
    Span,
    Anchor,
    SymbolNode,
    SvgNode,
    PathNode,
    LineNode,
} = katex.__domTree;
```

| 类 | 用途 |
|----|------|
| `Span` | 最常用的容器节点，对应 `<span>` |
| `Anchor` | 超链接节点，对应 `<a>` |
| `SymbolNode` | 单个字符符号，携带度量信息 |
| `SvgNode` | SVG 容器 |
| `PathNode` | SVG 路径 |
| `LineNode` | 线条（分数线、根号等） |

### 不可变 Options 传递

渲染子节点时必须通过 `options.having*()` 或 `options.with*()` 创建新 Options 实例，不得直接修改 `options` 属性[^src]：

```javascript
htmlBuilder(group, options) {
    const supOptions = options.havingStyle(options.style.sup());
    const redOptions = options.withColor("#ff0000");
    // 使用新 options 渲染子节点...
}
```

常用转换方法：

| 方法 | 作用 |
|------|------|
| `options.havingStyle(style)` | 切换 TeX 样式（sup/sub/fracNum/fracDen 等） |
| `options.withColor(color)` | 切换颜色 |
| `options.withSize(size)` | 切换字号 |
| `options.withFont(font)` | 切换字体族 |
| `options.havingCrampedStyle()` | 切换到 cramped 样式 |

### CSS 类名约定

尽量复用 KaTeX 已有 CSS 类名以获得正确的间距和大小：

| 类名 | 用途 |
|------|------|
| `.mord`、`.mop`、`.mbin`、`.mrel` 等 | 数学原子类，影响间距 |
| `.vlist-t`、`.vlist-r`、`.vlist`、`.vlist-s` | 垂直列表布局 |
| `.msupsub` | 上下标容器 |
| `.pstrut` | 支柱（撑开行高） |
| `.sizing`、`.size1`~`.size11` | 字号控制 |
| `.mtight` | 紧密间距（script 样式下自动添加） |

自定义类名应加前缀（如 `.myext-circled`），避免与 KaTeX 内置类冲突。

## MathML 与无障碍

### 双输出架构

KaTeX 默认 `output: "htmlAndMathml"`，MathML 节点放在 HTML 节点之前，通过 CSS 视觉上隐藏 MathML 但屏幕阅读器可读取。自定义函数的 `mathmlBuilder` 应返回有语义的 MathML 结构。

### mathmlBuilder 简化策略

若构建完整 MathML 子树较复杂，最低限度应返回包含文本内容的 MathML 节点，使屏幕阅读器能读出命令含义。MathML 节点类需从 `katex/src/mathMLTree` 导入，不通过 `__domTree` 暴露：

```javascript
import {MathNode, TextNode} from "katex/src/mathMLTree";

mathmlBuilder(group, options) {
    if (group.type === "checkbox") {
        return new MathNode("mtext", [new TextNode("\u2610")]);
    }
}
```

对于装饰性命令，可在 MathML 中使用 `<menclose>` 或 `<mrow>` 包裹子内容（需从源码导入 `mathMLTree` 模块）。

## 扩展加载最佳实践

1. **版本锁定**：`__` API 不保证向后兼容，在 `package.json` 中锁定 KaTeX 版本
2. **加载顺序**：扩展脚本必须在 `katex.js` 之后、渲染调用之前加载
3. **存在性检查**：注册前检查 `typeof katex !== "undefined"`，失败时给 console 警告而非阻断
4. **命名空间**：自定义 CSS 类名加前缀，自定义命令名避免与内置命令冲突
5. **双 builder**：始终同时提供 `htmlBuilder` 和 `mathmlBuilder`，确保无障碍访问
6. **模式测试**：在 `displayMode: true` 和 `false` 下分别测试自定义命令
7. **Options 不可变**：builder 中不得直接修改 `options`，使用 `having*`/`with*` 方法
8. **考虑贡献**：通用扩展可考虑贡献到 KaTeX 官方 `contrib/` 目录

## 相关内容

- [函数注册表](/concepts/08-function-registry.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [虚拟 DOM 树](/concepts/07-dom-tree.md)
- [配置选项](/concepts/10-settings-options.md)
- [版本迁移](/concepts/22-migration.md)
- [自定义宏示例](/examples/custom-macros.md)
- [安全信任示例](/examples/security-trust.md)

[^src]: 源码信源见 [references/katex-source.md](/references/katex-source.md)，FunctionSpec 定义于 `src/defineFunction.ts`，虚拟 DOM 节点定义于 `src/domTree.ts`。
[^web-migration]: 官网 Migration 页面，https://katex.org/docs/migration；v0.17.0 变更说明 `__defineFunction` 属性不再包裹在 `props` 中。
