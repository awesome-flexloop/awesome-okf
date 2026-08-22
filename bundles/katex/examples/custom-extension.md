---
type: Example
title: 自定义扩展示例
description: 使用__defineFunction添加自定义LaTeX命令，包括简单装饰命令、新的数学结构和带可选参数的命令。
tags: [katex, example, extension, defineFunction, custom]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:40:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 扩展API概览

KaTeX 提供三个内部扩展API（注意双下划线前缀表示内部API，未来版本可能变更）：

| API | 作用 |
|-----|------|
| `katex.__defineFunction(spec)` | 注册新的LaTeX函数命令 |
| `katex.__defineMacro(name, body)` | 注册全局宏（等价于 `katex.__defineMacro`） |
| `katex.__defineSymbol(mode, family, cls, char, name)` | 注册单个符号 |
| `katex.__setFontMetrics(family, metrics)` | 扩展字体度量 |
| `katex.__domTree` | 虚拟DOM节点类（Span、Anchor等） |

其中 `__defineFunction` 是最强大的扩展机制，可以添加全新的渲染逻辑。

> **注意**：这些API带有 `__` 前缀，表示它们是内部API。在生产中使用时，请锁定KaTeX版本并关注KaTeX更新日志。

## 示例1：简单装饰命令（\circled）

为内容添加圆圈包围效果：

```javascript
// 注册 \circled{...} 命令
katex.__defineFunction({
    type: "circled",
    names: ["\\circled"],
    props: {
        numArgs: 1,
        allowedInText: true,
        allowedInMath: true,
    },
    // 解析阶段：创建ParseNode
    handler({parser, token}, args) {
        return {
            type: "circled",
            mode: parser.mode,
            loc: token.loc,
            body: args[0],
        };
    },
    // HTML渲染阶段
    htmlBuilder(group, options) {
        // 构建子节点
        const body = katex.__renderToHTMLTree
            ? buildGroup(group.body, options)
            : buildGroupInline(group.body, options);

        // 使用Span创建带圆圈边框的容器
        const node = new katex.__domTree.Span(
            ["circled"],  // CSS类
            [body],       // 子节点
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
        return node;
    },
    // MathML渲染阶段
    mathmlBuilder(group, options) {
        // 简单地将子内容包裹在 <menclose> 中
        return new mathMLTree.MathNode(
            "menclose",
            [buildGroupMathML(group.body, options)],
            {notation: "circle"}
        );
    },
});

// 使用
katex.render("\\circled{x} + \\circled{1}", el);
```

## 示例2：更实际的自定义命令（\ evaluated at）

创建 `\\eval{expr}_{lower}^{upper}` 命令（在指定点求值），类似 `\\left.\\frac{df}{dx}\\right|_{x=0}`：

```javascript
katex.__defineFunction({
    type: "evalat",
    names: ["\\eval"],
    props: {
        numArgs: 1,
        allowedInText: false,
        allowedInMath: true,
    },
    handler({parser, token}, args) {
        // 消费可选的上下标（类似 \sqrt 的可选参数方式）
        let subscript = null;
        let superscript = null;

        // 查看下一个token是否是 _ 或 ^
        let next = parser.gullet.future();
        while (next.text === "_" || next.text === "^") {
            parser.gullet.consume();  // 消费 _ 或 ^
            const arg = parser.parseGroup();
            if (next.text === "_") {
                subscript = arg;
            } else {
                superscript = arg;
            }
            next = parser.gullet.future();
        }

        return {
            type: "evalat",
            mode: parser.mode,
            body: args[0],
            subscript,
            superscript,
        };
    },
    htmlBuilder(group, options) {
        // 构建主体
        const body = buildGroup(group.body, options);

        // 创建竖线（|）
        const bar = new katex.__domTree.Span(
            ["vertical-bar"],
            [],
            { style: { "border-left": "0.06em solid currentColor" } }
        );

        // 组装主容器
        const elements = [body, bar];

        // 添加上下标
        const supsub = [];
        if (group.superscript) {
            const supNode = buildGroup(group.superscript, options.havingStyle(options.style.sup()));
            supsub.push(new katex.__domTree.Span(["vlist-t"], [
                new katex.__domTree.Span(["vlist-r"], [
                    new katex.__domTree.Span(["vlist"], [supNode])
                ])
            ]));
        }
        if (group.subscript) {
            const subNode = buildGroup(group.subscript, options.havingStyle(options.style.sub()));
            supsub.push(new katex.__domTree.Span(["vlist-t"], [
                new katex.__domTree.Span(["vlist-r"], [
                    new katex.__domTree.Span(["vlist"], [subNode])
                ])
            ]));
        }

        const supsubWrap = new katex.__domTree.Span(["msupsub"], [
            new katex.__domTree.Span(["vlist-t", "vlist-r"], supsub)
        ]);

        const inner = new katex.__domTree.Span([], elements);
        return new katex.__domTree.Span(["mord", "evalat"], [inner, supsubWrap]);
    },
    mathmlBuilder(group, options) {
        const children = [buildGroupMathML(group.body, options)];
        // 简单MathML表示
        return new mathMLTree.MathNode("mrow", children);
    },
});

// 使用
katex.render("\\eval{\\frac{x^2}{2}}_0^1", el, {displayMode: true});
// 等价于：\left.\frac{x^2}{2}\right|_0^1 = 1/2 - 0 = 1/2
```

## 示例3：自定义符号（\diamond）

使用 `__defineSymbol` 添加单个数学符号：

```javascript
// 直接映射到Unicode字符
katex.__defineSymbol(
    "math",        // 模式：math或text
    "main",        // 字体族
    "mord",        // 数学类
    "\u25ca",      // Unicode字符（◇ LOZENGE）
    "\\diamond"    // LaTeX命令名
);

katex.render("A\\diamond B", el);
// 渲染：A ◇ B
```

## 示例4：颜色常量宏

通过 `__defineMacro` 注册常用颜色简写：

```javascript
// 注意：__defineMacro的第二个参数可以是字符串（简单替换）
katex.__defineMacro("\\red", "\\textcolor{#df0000}{#1}");
katex.__defineMacro("\\blue", "\\textcolor{#0000df}{#1}");
katex.__defineMacro("\\green", "\\textcolor{#008000}{#1}");

// 使用：\red{x} → 红色的x
katex.render("\\red{x} + \\blue{y} = \\green{z}", el);
```

注意：带参数的宏通过 `#1` 引用参数，KaTeX 自动推断参数数量。

## 编写htmlBuilder的要点

### 虚拟DOM工具函数

在扩展中构建虚拟DOM节点时，可以使用 KaTeX 内部暴露的 `katex.__domTree` 中的类：

```javascript
const {Span, Anchor, SymbolNode, SvgNode, DocumentFragment} = katex.__domTree;
```

但更方便的是使用 buildCommon 中的工具函数（这些函数不直接暴露，需要参考KaTeX源码使用模式）。

### 样式传递（不可变Options）

在htmlBuilder中渲染子节点时，**必须**使用新的Options对象：

```javascript
htmlBuilder(group, options) {
    // 子节点使用上标样式（缩小）
    const supOptions = options.havingStyle(options.style.sup());
    const childHtml = buildGroup(group.child, supOptions);

    // 子节点使用红色
    const redOptions = options.withColor("#ff0000");
    const redChild = buildGroup(group.body, redOptions);

    // 不可直接修改：options.color = "red"; ← 错误！
}
```

### CSS类名约定

尽量使用KaTeX已有的CSS类名来获得正确的间距和大小：

| 类名 | 用途 |
|------|------|
| `.mord`, `.mop`, `.mbin`, `.mrel` 等 | 数学类，影响间距 |
| `.vlist-t`, `.vlist-r`, `.vlist`, `.vlist-s` | 垂直列表布局 |
| `.msupsub` | 上下标容器 |
| `.pstrut` | 支柱（撑开行高） |
| `.sizing`, `.size1`~`.size11` | 字号控制 |
| `.delimsizing` | 分隔符尺寸 |
| `.mtight` | 紧密间距（script样式下自动添加） |

## 完整的简单扩展示例：\checkbox

一个自包含的、最小的扩展示例（可直接复制使用）：

```javascript
(function() {
    // 检查katex是否已加载
    if (typeof katex === "undefined") {
        console.warn("KaTeX not loaded; custom \\checkbox not registered.");
        return;
    }

    katex.__defineFunction({
        type: "checkbox",
        names: ["\\checkbox", "\\square"],
        props: {
            numArgs: 0,
            allowedInText: true,
            allowedInMath: true,
        },
        handler({parser, token}) {
            return {
                type: "checkbox",
                mode: parser.mode,
            };
        },
        htmlBuilder(group, options) {
            // 创建一个空方框（□）
            const size = options.sizeMultiplier * 1.0;  // 1em大小
            return new katex.__domTree.Span(
                ["mord", "checkbox-symbol"],
                [new katex.__domTree.SymbolNode(
                    "\u2610",  // □ BALLOT BOX
                    0.8,  // height
                    0.0,  // depth
                    0,    // italic
                    0,    // skew
                    0.8   // width
                )],
                {
                    style: {
                        position: "relative",
                        top: "-0.1em",
                    }
                }
            );
        },
        mathmlBuilder(group, options) {
            return new mathMLTree.MathNode("mo", [
                new mathMLTree.TextNode("\u2610")
            ]);
        },
    });

    // \checked 命令（打勾的方框☑）
    katex.__defineFunction({
        type: "checked",
        names: ["\\checked", "\\boxtimes"],
        props: {numArgs: 0, allowedInText: true, allowedInMath: true},
        handler({parser}) {
            return {type: "checked", mode: parser.mode};
        },
        htmlBuilder(group, options) {
            return new katex.__domTree.Span(
                ["mord"],
                [new katex.__domTree.SymbolNode("\u2611", 0.8, 0.0, 0, 0, 0.8)]
            );
        },
        mathmlBuilder(group, options) {
            return new mathMLTree.MathNode("mo", [
                new mathMLTree.TextNode("\u2611")
            ]);
        },
    });
})();

// 使用
katex.render("\\checkbox \\text{未完成} \\quad \\checked \\text{已完成}", el);
```

## 扩展加载最佳实践

1. **版本锁定**：由于 `__` API不稳定，在package.json中锁定KaTeX版本
2. **加载顺序**：扩展脚本必须在katex.js之后、渲染调用之前加载
3. **错误处理**：扩展注册失败时给console警告，不要阻断其他渲染
4. **命名空间**：自定义CSS类名加前缀（如 `.myext-circled`），避免与KaTeX内置类冲突
5. **MathML支持**：始终提供mathmlBuilder，否则屏幕阅读器无法读取自定义命令
6. **测试**：在displayMode和inlineMode下都测试自定义命令的渲染效果
7. **考虑贡献**：如果扩展有通用价值，考虑贡献到KaTeX官方contrib/目录

## 相关内容

- [函数注册表](/concepts/08-function-registry.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [虚拟DOM树](/concepts/07-dom-tree.md)
- [自定义宏示例](/examples/custom-macros.md)
