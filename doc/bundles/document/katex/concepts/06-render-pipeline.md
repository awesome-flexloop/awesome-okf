---
type: Concept
title: 渲染管线
description: KaTeX 从解析树到DOM/HTML输出的渲染流程，包括buildTree、buildHTML、buildMathML、displayWrap和双输出组合机制。
tags: [katex, render, build, html, mathml, pipeline]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 渲染管线总览

解析完成后，KaTeX 进入渲染阶段，将 ParseNode 树转换为最终可显示的输出。渲染管线的核心函数是 `buildTree()`，位于 [src/buildTree.ts](https://github.com/KaTeX/KaTeX/blob/main/src/buildTree.ts)。

```
ParseNode[]  ──▶  buildTree()  ──▶  DomSpan
                     │
                     ├─▶ optionsFromSettings()   创建Options
                     ├─▶ buildHTML()            构建HTML虚拟树
                     ├─▶ buildMathML()          构建MathML虚拟树
                     ├─▶ combineMathMLAndHtml() 组合双输出
                     └─▶ displayWrap()          显示模式包装
```

## buildTree() 入口

```typescript
const buildTree = function(
    tree: AnyParseNode[],
    expression: string,
    settings: Settings
): DomSpan {
    const options = optionsFromSettings(settings);
    // ... 根据 output 设置选择渲染路径
};
```

### 三种输出模式

| settings.output | 行为 | 输出结构 |
|-----------------|------|---------|
| `"mathml"` | 仅生成MathML | `<math>...</math>` |
| `"html"` | 仅生成HTML | `<span class="katex">...</span>` |
| `"htmlAndMathml"`（默认） | 同时生成 | `<span class="katex"><math>...</math><span class="katex-html">...</span></span>` |

### HTML+MathML 双输出

默认模式下，KaTeX 同时生成 MathML（语义）和 HTML（视觉）：

1. 先构建 MathML 树（放在前面，供屏幕阅读器优先读取）
2. 再构建 HTML 树（视觉呈现）
3. MathML 节点通过 CSS 设置为不显示（`aria-hidden` 或视觉隐藏），但屏幕阅读器仍能读取
4. HTML 节点添加 `aria-hidden="true"`，避免屏幕阅读器重复读取

这种设计保证了：
- **视觉上**：用户看到的是高质量的HTML排版
- **语义上**：辅助技术（屏幕阅读器）能通过MathML理解公式结构
- **SEO**：搜索引擎能索引MathML中的语义信息

## buildHTML()：HTML 树构建

`buildHTML()` 位于 [src/buildHTML.ts](https://github.com/KaTeX/KaTeX/blob/main/src/buildHTML.ts)，将 ParseNode 树转换为虚拟 HTML DOM 树。

```typescript
export function buildHTML(
    tree: AnyParseNode[],
    options: Options
): DocumentFragment {
    const groups = [];
    for (let i = 0; i < tree.length; i++) {
        groups.push(buildGroup(tree[i], options));
    }
    return makeFragment(groups);
}
```

### buildGroup()：单节点构建

对于每个 ParseNode，`buildGroup()` 根据节点类型查找对应的 HTML builder（在 `defineFunction()` 时注册的 `htmlBuilder`），调用它生成虚拟DOM节点：

```typescript
export const buildGroup = function(
    group: AnyParseNode,
    options: Options,
    options?: {...}
): HtmlDomSpan {
    const {nodeType, builder} = _htmlGroupBuilders[group.type];
    return builder(group, options);
};
```

### buildExpression()：递归构建表达式

builder 内部通常调用 `buildExpression()` 递归构建子节点列表：

```typescript
export function buildExpression(
    expression: AnyParseNode[],
    options: Options,
    ...
): HtmlDomSpan[] {
    return expression.map(node => buildGroup(node, options));
}
```

## buildMathML()：MathML 树构建

`buildMathML()` 位于 [src/buildMathML.ts](https://github.com/KaTeX/KaTeX/blob/main/src/buildMathML.ts)，生成 MathML 标记。流程与 buildHTML 类似：

1. 为每个 ParseNode 查找注册的 `mathmlBuilder`
2. 递归构建 MathML 节点树
3. 额外生成 `<semantics>` 和 `<annotation>` 节点，包含原始 LaTeX 源码

输出结构大致为：
```xml
<math>
  <semantics>
    <!-- MathML 渲染结果 -->
    <mrow>...</mrow>
    <annotation encoding="application/x-tex">\frac{a}{b}</annotation>
  </semantics>
</math>
```

`<annotation>` 中的原始 LaTeX 源码让工具可以"复制为LaTeX"。

## Options：渲染状态

`Options` 类（[src/Options.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Options.ts)）携带渲染过程中的状态信息：

```typescript
class Options {
    style: Style;            // 当前样式（display/text/script/scriptscript）
    color: string | undefined;
    size: number;            // 字号索引（0-10，对应\tiny~\HUGE）
    textSize: number;        // 文本模式字号
    phantom: boolean;        // 是否为幻影（保留间距但不可见）
    font: string;            // 字体（如 \mathbf、\mathit）
    fontFamily: string;      // 字体族
    fontWeight: string;      // 字重
    fontShape: string;       // 字形（italic/upright）
    sizeMultiplier: number;  // 字号倍数
    maxSize: number;         // 最大尺寸
    minRuleThickness: number; // 最小线条粗细

    havingStyle(style): Options;     // 返回带新样式的Options副本
    withColor(color): Options;       // 返回带新颜色的Options副本
    havingSize(size): Options;       // 返回带新字号的Options副本
    havingCrampedStyle(): Options;   // 返回压缩样式的Options副本
    // ... 其他 with*/having* 方法
}
```

### 不可变设计

Options 的所有 `with*`/`having*` 方法都返回**新的 Options 实例**，不会修改自身。这确保了：
- 子节点的样式变化不影响兄弟节点
- 递归调用时状态隔离
- 不需要手动"恢复"状态

## displayWrap()：显示模式包装

当 `settings.displayMode` 为 true 时，渲染结果会被包裹在额外的 span 中：

```html
<span class="katex-display">
  <span class="katex">...</span>
</span>
```

额外CSS类：
- `.katex-display`：块级显示，居中对齐
- `.leqno`：公式编号左对齐（`settings.leqno = true`）
- `.fleqn`：公式左对齐（`settings.fleqn = true`）

## renderError()：错误渲染

当解析或渲染过程中抛出异常时，`renderError()`（在 katex.ts 中）生成错误显示：

- 如果 `settings.throwOnError = true`：直接抛出异常
- 否则：生成带有 `errorColor`（默认#cc0000）的错误消息节点，保留原始输入文本

## 输出路径

最终 DomSpan 有两个输出路径：

### render()：浏览器DOM渲染
```typescript
export function render(expression, baseNode, options) {
    const node = renderToDomTree(expression, options).toNode();
    baseNode.textContent = '';     // 清空
    baseNode.appendChild(node);    // 插入真实DOM
}
```

### renderToString()：HTML字符串
```typescript
export function renderToString(expression, options) {
    return renderToDomTree(expression, options).toMarkup();
}
```

虚拟 DOM 节点的 `toNode()` 和 `toMarkup()` 方法分别对应这两条路径。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [虚拟DOM树](07-dom-tree.md)
- [配置系统](10-settings-options.md)
- [样式系统](11-style-system.md)
- [函数注册表](08-function-registry.md)
