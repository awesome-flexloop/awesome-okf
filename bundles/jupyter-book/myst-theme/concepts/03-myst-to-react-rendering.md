---
type: concept
title: "MDAST 到 React 的组件渲染架构"
description: "myst-to-react 包将 MyST AST 节点映射为 React 组件的核心机制，包括渲染器覆盖和扩展"
tags: [myst-theme, myst-to-react, react, mdast, rendering]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "packages/myst-to-react/src/index.tsx"
    facts: [F-005, F-030, F-031]
  - path: "spec/facts.md"
    facts: [F-032, F-033, F-034]
---

# MDAST 到 React 的组件渲染架构

## 核心机制

myst-to-react 是 myst-theme 的渲染核心，负责将 MyST Markdown 解析后的 MDAST（Markdown Abstract Syntax Tree）转换为 React 组件树。其核心 API 是 `<MyST>` 组件：

```tsx
import { MyST } from '@myst-theme/myst-to-react';

function Document({ mdast }) {
  return <MyST ast={mdast} />;
}
```

## 节点到组件的映射

`<MyST>` 组件递归遍历 MDAST 树，对每个节点：
1. 读取节点的 `type` 属性
2. 从渲染器映射表中查找对应的 React 组件
3. 将节点属性作为 props 传入
4. 递归渲染子节点（`children`）

### 内置节点组件

| 节点类型 | React 组件 | 说明 |
|---------|-----------|------|
| `root` | Fragment | 根节点，不产生 DOM |
| `paragraph` | `<p>` | 段落 |
| `heading` | `Heading` | 标题（h1-h6），带锚点链接 |
| `text` | 文本节点 | 纯文本 |
| `strong` | `<strong>` | 粗体 |
| `emphasis` | `<em>` | 斜体 |
| `delete` | `<del>` | 删除线 |
| `inlineCode` | `<code>` | 行内代码 |
| `code` | `CodeBlock` | 代码块（语法高亮+复制按钮） |
| `blockquote` | `Blockquote` | 引用块 |
| `thematicBreak` | `<hr>` | 分隔线 |
| `list` | `<ul>`/`<ol>` | 列表 |
| `link` | `Link` | 超链接 |
| `image` | `Image` | 图片 |
| `admonition` | `Admonition` | 提示框（note/warning/tip 等） |
| `container` | `Block` | 通用块容器 |
| `figure` | `Figure` | 图表（带标题） |
| `table` | `Table` | 表格 |
| `math` | `Math` | 数学公式（KaTeX） |
| `inlineMath` | `InlineMath` | 行内公式 |
| `footnoteReference` | `Footnote` | 脚注 |
| `cite` | `Cite` | 文献引用 |
| `crossReference` | `CrossReference` | 交叉引用 |
| `tabs`/`tabItem` | `Tabs`/`TabItem` | 标签页 |
| `grid`/`gridItem` | `Grid`/`GridItem` | 网格布局 |
| `card` | `Card` | 卡片 |
| `dropdown` | `Dropdown` | 折叠块 |
| `proof` | `Proof` | 证明环境 |
| `exercise` | `Exercise` | 练习 |
| `reactive` | `Reactive` | 响应式组件 |
| `iframe` | `Iframe` | 嵌入框架 |
| `mermaid` | `Mermaid` | Mermaid 图表 |
| `html` | `HtmlNode` | 原始 HTML |
| `comment` | null | 注释（不渲染） |
| `unknown` | `UnknownNode` | 未知节点（开发警告） |

## 渲染器覆盖（Dependency Injection）

ThemeProvider 接受 `renderers` prop，允许覆盖或扩展任何节点类型的渲染：

```tsx
import { ThemeProvider } from '@myst-theme/providers';
import { MyST, DEFAULT_RENDERERS } from '@myst-theme/myst-to-react';

const customRenderers = {
  ...DEFAULT_RENDERERS,
  // 完全替换 code 节点渲染
  code: { base: MyCustomCodeBlock },
  // 使用 CSS 选择器精确匹配 admonition[kind=warning]
  admonition: {
    base: DefaultAdmonition,
    'admonition[kind=warning]': CustomWarningAdmonition,
    'admonition[kind=danger]': DangerAdmonition,
  },
};

<ThemeProvider renderers={customRenderers}>
  <MyST ast={mdast} />
</ThemeProvider>
```

渲染器匹配使用 `unist-util-select` 语法，支持：
- 类型匹配：`code`
- 属性匹配：`admonition[kind=warning]`
- 组合匹配：`container[kind=figure] > caption`

## 扩展组件

### extensions/ 子目录

提供超出 MyST 核心规范的扩展渲染：

- `chemicalFormula`：化学式渲染（ mhchem 语法）
- `siunits`：SI 物理单位渲染

### links/ 子目录

处理特殊链接协议的智能解析：

- `github`：GitHub 链接（自动提取 issue/PR 编号、仓库信息）
- `ror`：Research Organization Registry 链接（显示组织名称）
- `rrid`：Research Resource Identifier 链接
- `wiki`：维基百科链接（多语言支持）

### 子组件

- `CopyIcon`：代码块复制按钮
- `HoverPopover`：悬停弹出预览（用于引用、脚注）
- `LinkCard`：链接卡片预览

## HashLink 与锚点

每个 heading 自动生成 `HashLink`——一个悬停时显示的锚点图标（¶），点击后 URL 更新为该标题的锚点。锚点 ID 由 `createHtmlId` 从标题文本生成，支持中文和特殊字符。

## 错误边界

myst-to-react 对每个节点渲染进行错误隔离：
- 单个节点渲染失败不会导致整页崩溃
- 失败节点显示 `InlineError` 组件（开发模式显示错误详情，生产模式静默）
- `unknown` 类型节点在开发控制台输出警告，帮助发现未处理的节点类型

## 与 jupyterlab-myst 的关系

jupyterlab-myst 直接使用 myst-to-react 作为渲染基础，通过 `renderers` prop 添加：
- `inlineExpression`：Jupyter 内联表达式输出
- Jupyter 输出相关节点的自定义渲染
- 适配 JupyterLab 主题的颜色映射
