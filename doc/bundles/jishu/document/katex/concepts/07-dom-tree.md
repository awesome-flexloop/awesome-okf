---
type: Concept
title: 虚拟DOM树
description: KaTeX domTree 模块的虚拟节点类型（Span/Anchor/SymbolNode/SvgNode等），toNode()和toMarkup()双输出能力，以及与真实DOM/HTML字符串的转换。
tags: [katex, dom, virtual-dom, span, svg, markup]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 虚拟DOM层的角色

KaTeX 的构建阶段不直接操作浏览器 DOM 或拼接 HTML 字符串，而是先构建一层**轻量虚拟 DOM 树**，定义在 [src/domTree.ts](https://github.com/KaTeX/KaTeX/blob/main/src/domTree.ts)。

虚拟DOM层的价值：
- **同构渲染**：同一棵虚拟树既可输出为浏览器真实 DOM（`render()`），也可输出为 HTML 字符串（`renderToString()`）
- **构建简化**：虚拟节点比真实 DOM 更轻量，属性设置和样式计算更高效
- **类型安全**：虚拟节点的类层次结构为构建过程提供类型约束

## 节点类型继承关系

```
VirtualNode（树基类）
├── DocumentFragment    文档片段（多节点容器）
└── domNode（单节点基类）
    ├── Anchor          <a> 链接元素
    ├── Span            <span> 通用容器
    ├── SymbolNode      带字体信息的文本节点
    ├── SvgNode         <svg> SVG容器
    │   ├── PathNode        <path> 路径元素
    │   └── LineNode        <line> 线条元素
    └── imgNode         <img> 图片元素（includegraphics用）
```

（MathML有独立的虚拟节点体系，定义在 src/mathMLTree.ts）

## 核心类

### VirtualNode（基类）

```typescript
class VirtualNode {
    toNode(): Node;               // 转为真实DOM节点
    toMarkup(): string;           // 转为HTML字符串
    toText(): string;             // 提取文本内容
}
```

### domNode（DOM节点基类）

```typescript
class domNode extends VirtualNode {
    classes: string[];            // CSS类名列表
    style: CssStyle;              // 内联样式对象
    attributes: AttrList;         // HTML属性
    children: VirtualNode[];      // 子节点

    constructor(classes, children, options);
    setAttribute(name, value);
    setStyle(name, value);
    hasClass(className);
}
```

### Span

Span 是最常用的容器节点，对应 HTML `<span>` 元素：

```typescript
class Span extends domNode {
    constructor(
        classes?: string[],
        children?: VirtualNode[],
        options?: {
            style?: CssStyle;
            attributes?: AttrList;
        }
    );
}
```

创建 Span 的便捷函数是 `makeSpan()`（定义在 [src/buildCommon.ts](https://github.com/KaTeX/KaTeX/blob/main/src/buildCommon.ts)）：

```typescript
function makeSpan(
    classes?: string[],
    children?: VirtualNode[],
    options?: {...},
    cls?: string      // 额外的单类名（历史参数）
): Span;
```

### Anchor

Anchor 是超链接节点，对应 `<a>` 元素，用于 `\href` 和 `\url` 命令：

```typescript
class Anchor extends domNode {
    constructor(
        href: string,
        classes?: string[],
        children?: VirtualNode[],
        options?: {...}
    );
}
```

注意：Anchor 需要 `settings.trust` 为 true 或自定义信任函数才会创建，防止 XSS 攻击。

### SymbolNode

SymbolNode 是文本字符节点，带有字体和位置信息，是公式中所有字符的基础：

```typescript
class SymbolNode extends domNode {
    text: string;           // 字符内容（通常是单个Unicode字符）
    italic: number;         // 斜体修正值（em单位）
    skew: number;           // 倾斜修正值
    height: number;         // 字符高度（em）
    depth: number;          // 字符深度（基线以下，em）
    maxFontSize: number;    // 最大字号（防止溢出）

    constructor(
        text: string,
        height?: number,
        depth?: number,
        italic?: number,
        skew?: number,
        width?: number,
        classes?: string[],
        style?: CssStyle
    );
}
```

SymbolNode 携带的度量信息（height/depth/italic/skew）来自字体度量数据，用于精确的排版间距计算。

### SvgNode / PathNode / LineNode

这些节点用于渲染需要矢量图形的数学符号：
- **SvgNode**：`<svg>` 容器，包裹路径和线条
- **PathNode**：`<path>` 元素，用于复杂形状（根号、花括号、箭头）
- **LineNode**：`<line>` 元素，用于简单线条（分数线、分数线条等）

```typescript
class SvgNode extends domNode {
    constructor(children?: VirtualNode[], options?: {...});
}
class PathNode extends domNode {
    constructor(pathName: string, options?: {...});  // pathName引用预定义SVG路径
}
class LineNode extends domNode {
    constructor(length?: number, options?: {...});
}
```

## 双输出方法

每个虚拟节点都实现两个输出方法：

### toNode()：转为真实DOM

在浏览器环境中（`render()` 使用），`toNode()` 通过 `document.createElement()` 创建真实 DOM 元素：

```typescript
toNode() {
    const node = document.createElement('span');  // 或 'a'、'svg'、'path'等
    // 设置class
    this.classes.forEach(cls => node.classList.add(cls));
    // 设置style
    Object.keys(this.style).forEach(prop => {
        node.style[cssPropertyName(prop)] = this.style[prop];
    });
    // 设置属性
    Object.keys(this.attributes).forEach(attr => {
        node.setAttribute(attr, this.attributes[attr]);
    });
    // 递归添加子节点
    this.children.forEach(child => node.appendChild(child.toNode()));
    return node;
}
```

### toMarkup()：转为HTML字符串

在 Node.js 或 SSR 环境中（`renderToString()` 使用），`toMarkup()` 递归序列化为 HTML 字符串：

```typescript
toMarkup() {
    const attrs = [];
    // 构建class属性
    if (this.classes.length) attrs.push(`class="${this.classes.join(' ')}"`);
    // 构建style属性
    if (Object.keys(this.style).length) attrs.push(`style="${...}"`);
    // 构建其他属性
    Object.keys(this.attributes).forEach(attr => {
        attrs.push(`${attr}="${escape(this.attributes[attr])}"`);
    });
    // 递归序列化子节点
    const innerMarkup = this.children
        .map(child => child.toMarkup())
        .join('');
    return `<span ${attrs.join(' ')}>${innerMarkup}</span>`;
}
```

## DocumentFragment

DocumentFragment 是一个特殊的多节点容器，不对应具体的 HTML 元素：

```typescript
class DocumentFragment extends VirtualNode {
    children: VirtualNode[];
    constructor(children?: VirtualNode[]);
    
    toNode() {
        const fragment = document.createDocumentFragment();
        this.children.forEach(child => fragment.appendChild(child.toNode()));
        return fragment;
    }
    toMarkup() {
        return this.children.map(c => c.toMarkup()).join('');
    }
}
```

它在 `buildExpression()` 中用于返回多个兄弟节点的集合。

## makeAnchor / makeSvgSpan 等工具

[src/buildCommon.ts](https://github.com/KaTeX/KaTeX/blob/main/src/buildCommon.ts) 中提供了创建各种虚拟节点的便捷函数：

| 函数 | 创建的节点 |
|------|-----------|
| `makeSpan(classes, children, options)` | Span |
| `makeAnchor(href, classes, children, options)` | Anchor |
| `makeFragment(children)` | DocumentFragment |
| `makeSvgSpan(classes, children, options)` | 带SVG样式的Span |
| `makeSymbol(value, fontFamily, ...)` | SymbolNode |
| `makeOrd(...)` / `makeOp(...)` 等 | 带数学类的Span |

## CSS类名约定

KaTeX 的虚拟节点广泛使用 CSS 类名来控制样式，常见类名前缀：

| 类名 | 含义 |
|------|------|
| `.katex` | 根元素 |
| `.katex-display` | 显示模式包裹器 |
| `.katex-html` | HTML视觉部分 |
| `.mord`、`.mop`、`.mbin`、`.mrel`、`.mopen`、`.mclose`、`.mpunct`、`.minner` | 数学原子类 |
| `.mspace` | 间距元素 |
| `.msupsub` | 上下标容器 |
| `.mfrac` | 分数 |
| `.sqrt` | 根号 |
| `.accent` | 重音符号 |
| `.op-symbol` | 算符符号 |
| `.size1`~`.size11` | 字号类 |
| `.delimsizing` | 可伸缩分隔符 |
| `.vlist-t`/`.vlist-r`/`.vlist-s`/`.vlist` | 垂直列表（用于分数、根号等堆叠布局） |
| `.pstrut` | 支柱（用于撑开行高） |
| `.nulldelimiter` | 空分隔符（`\left.`等） |

## 相关概念

- [渲染管线](06-render-pipeline.md)
- [样式系统](11-style-system.md)
- [配置系统](10-settings-options.md)
