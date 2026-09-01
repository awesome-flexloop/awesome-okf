---
type: concept
title: 目标与引用系统（Targets & References）
description: MyST 通过 (target)= 标记锚点目标，支持交叉引用链接到标题、图表、公式、代码块等元素。目标提取、全局编号和引用解析分阶段在 transform 管线中执行。
tags: [mystmd, targets, cross-references, links, identifiers]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-transforms-source.md"
    facts: []
  - path: "/references/myst-common-source.md"
    facts: [F-053, F-067]
  - path: "/references/myst-spec-source.md"
    facts: []
---

## 目标（Target）机制

### 目标语法

在 MyST Markdown 中，目标使用 `(label)=` 语法标记：

```markdown
(my-section)=

## My Section Title

(my-figure)=
```{figure} images/photo.png
An example figure
```

(eq:euler)=
$$
e^{i\pi} + 1 = 0
$$
```

### 目标节点类型

目标被解析为 `mystTarget` MDAST 节点：

```ts
{
  type: 'mystTarget',
  label: 'my-section',       // 原始标签
  position: { ... },
}
```

### mystTargets transform

`mystTargetsPlugin`（basicTransformations 第2步）处理 mystTarget 节点：

1. 查找紧跟目标节点的下一个有意义的元素（标题、容器、数学公式等）
2. 为该元素设置 `identifier`、`label`、`html_id` 属性
3. 通过 `normalizeLabel` 规范化：
   - `identifier`：规范化后的唯一 ID（小写、空格替换为连字符）
   - `label`：原始标签文本
   - `html_id`：HTML 安全 ID（用于锚点链接）
4. 移除 mystTarget 节点本身

### 隐式目标

除显式 `(label)=` 目标外，标题自动生成隐式目标：
- H1/H2/H3 等标题的文本被 slugify 为 identifier
- 编号元素（figure/table/equation）自动获得 identifier

## 目标类型（TargetKind）

```ts
enum TargetKind {
  heading = 'heading',       // 标题
  equation = 'equation',     // 公式
  subequation = 'subequation',  // 子公式
  figure = 'figure',         // 图片
  table = 'table',           // 表格
  code = 'code',             // 代码块
}
```

## 引用语法

### 基本交叉引用

```markdown
See [](my-section) for details.
See [my custom text](my-figure) for the photo.
```

### 编号引用

```markdown
See [](#eq:euler) for Euler's identity.
```

`numref` 角色提供更灵活的编号引用：

```markdown
See {numref}`my-figure` for the figure.       → "Figure 1"
See {numref}`Figure %s <my-figure>`.          → "Figure 1"（自定义格式）
Eq. {eq}`euler`                               → "Eq. (1)"
```

### 引用角色

| 角色 | 说明 | 显示格式 |
|------|------|---------|
| `ref` | 普通引用 | 使用目标标题/label 作为链接文本 |
| `numref` | 编号引用 | 使用编号（如 "Figure 1"） |
| `eq` | 公式引用 | 显示公式编号（如 "(1)"） |
| `eqr` | 公式行内引用 | 括号内公式编号 |
| `doc` | 文档引用 | 跨文档链接 |
| `link` | 外部链接 | 直接 URL |

### 参考文献引用

```markdown
[cite:@key2023]              → 括号引用 (Author, 2023)
{cite:t}`@key2023`           → 叙述引用 Author (2023)
{cite:p}`@key2023`           → 括号引用 (Author, 2023)
[cite:@key1; @key2]          → 多引用 (Author1, 2023; Author2, 2024)
```

## 引用解析流程

### 阶段1：目标收集（document stage）

`mystTargets` transform 处理每个文档的目标，为元素添加 identifier/label/html_id。

### 阶段2：全局编号（project stage）

`enumerateTargets` transform 对项目中所有文档的可编号元素分配 enumerator：
- 标题：基于深度编号（1, 1.1, 1.1.1）
- 图：Figure 1, Figure 2...
- 表：Table 1, Table 2...
- 公式：(1), (2), (3)... 或子公式 (1a), (1b)...
- 代码：Listing 1...

编号受 frontmatter 中的 `numbering` 配置控制。

### 阶段3：引用解析（project stage）

`resolveReferences` transform 处理所有交叉引用：
1. 收集项目中所有 identifier → 目标节点的映射
2. 遍历 crossReference/cite 节点
3. 查找目标节点，填充 url/text/enumerator 等属性
4. 找不到目标 → 上报 refNotFound/citeNotFound 错误

## 交叉引用节点

```ts
{
  type: 'crossReference',
  identifier: 'my-section',    // 目标 identifier
  label: 'my custom text',     // 自定义链接文本（方括号内）
  url: '/docs/page.html#my-section',  // 解析后的 URL
  remote: false,               // 是否跨项目引用
  children: [...],             // 链接文本节点
}
```

```ts
{
  type: 'cite',
  kind: 'parenthetical',       // narrative 或 parenthetical
  label: 'key2023',            // 引用 key
  identifier: 'ref-key2023',   // 生成的引用节点 ID
  children: [...],             // 格式化后的引用文本
}
```

## 标识符规范化（normalizeLabel）

`normalizeLabel` 函数将原始标签转换为标准格式：

```ts
normalizeLabel('My Section!') → {
  identifier: 'my-section',
  label: 'My Section!',
  html_id: 'my-section',
}
```

规则：
- 转为小写
- 空格替换为 `-`
- 移除特殊字符（保留字母数字和连字符）
- html_id 进一步确保 HTML 安全

## 重复标识符检测

`duplicateIdentifier` RuleId 用于检测同一文档中多个元素被分配了相同 identifier 的情况。这在以下场景可能发生：
- 两个标题文本相同导致 slug 冲突
- 显式 `(label)=` 重复定义
- 隐式 slug 与显式目标冲突

处理方式：后续重复目标会被标记为错误，第一个目标正常保留。

## 配置编号行为

在 myst.yml 或页面 frontmatter 中配置编号：

```yaml
numbering:
  heading_1: true       # 对 H1 编号
  heading_2: true       # 对 H2 编号
  heading_3: false      # H3 不编号
  figure: true          # 图编号
  table: true           # 表编号
  equation: true        # 公式编号
  code: false           # 代码块不编号
  start: 1              # 起始编号
```

## 跨文档引用

在项目级处理中，引用可以跨文档解析：
- 同一项目内的文档：相对路径 + anchor
- 跨项目引用（remote）：需要配置 intersphinx 映射
- 外部 URL：直接链接，不验证

## 相关概念

- [MDAST 转换管线](03-myst-transforms.md)
- [公共类型系统](04-myst-common-types.md)
- [Frontmatter 元数据](08-frontmatter.md)
- [引用处理示例](../examples/03-citations-example.md)
