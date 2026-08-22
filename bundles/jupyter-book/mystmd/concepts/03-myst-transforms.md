---
type: Concept
title: MDAST 转换管线（myst-transforms）
description: myst-transforms 包提供 30+ 个 unified Plugin 形式的 AST 转换，basicTransformations 按严格顺序组合 22 个核心 transform，构成 MyST 文档处理的核心管线。
tags: [mystmd, transforms, mdast, pipeline, plugin]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-transforms-source.md"
    facts: [F-075, F-076, F-077, F-078, F-079, F-080, F-081, F-082, F-083]
  - path: "/references/myst-parser-source.md"
    facts: [F-006, F-007]
---

## 转换管线概述

myst-transforms 包实现了 MDAST 树的各种后处理变换。它是 MyST 文档处理管线中最核心的部分——解析器（myst-parser）只负责将 Markdown 转为原始 AST，而真正的语义加工（标题编号、交叉引用、脚注归并、容器包装等）全部由 transforms 完成。

所有 transform 都导出为两种形式：
- **函数形式**：`xxxTransform(tree, opts)` — 直接操作树
- **Plugin 形式**：`xxxPlugin` — unified Plugin 包装，可在 unified 管线中使用

## basicTransformations 有序管线

`basicTransformationsPlugin` 按严格顺序组合了 22 个核心 transform。顺序不可调换，因为存在数据依赖：

```ts
basicTransformationsPlugin = compositePlugin({
  plugins: [
    liftMystDirectivesAndRolesPlugin,   // 1. 提升 mystDirective/mystRole
    mystTargetsPlugin,                  // 2. 提取目标（(target)=）
    blockMetadataPlugin,                // 3. 块元数据（:key: val）
    addChildPreambleNodesPlugin,        // 4. 子节点前言
    containersPlugin,                   // 5. 容器包装（figure/table等）
    headingDepthTransformPlugin,        // 6. 标题深度偏移
    sectionHeadersPlugin,               // 7. 节标题处理
    transformLegacyContentPlugin,       // 8. 遗留内容转换（glossary等）
    extractBlockFromSectionPlugin,      // 9. 从节中提取块
    rootNestingTransformPlugin,         // 10. 根嵌套处理
    footnoteTransformPlugin,            // 11. 脚注归并
    mathTransformPlugin,                // 12. 数学公式编号
    codeTransformPlugin,                // 13. 代码块元数据
    linksTransformPlugin,               // 14. 链接处理
    imageTransformPlugin,               // 15. 图片 alt/title
    removeDirectivesPlugin,             // 16. 移除已处理指令
    abbrPlugin,                         // 17. 缩写
    bulletsToTablePlugin,               // 18. 列表转表格
    paragraphsPlugin,                   // 19. 段落（break/nbsp）
    blocksPlugin,                       // 20. 块/块断点
    joinGatesTransformPlugin,           // 21. 合并门控
  ],
  name: 'basicTransformations',
});
```

### 关键 transform 详解

#### 1. liftMystDirectivesAndRoles（指令/角色提升）

将 mystDirective/mystRole 节点的 children 提升到父节点层级。这是因为 applyDirectives/applyRoles 已将指令/角色的具体 AST 节点放入了 children，但节点本身还是 mystDirective 类型，需要"解包"。

**为什么必须第一个执行**：后续所有 transform 操作的是具体节点类型（如 figure/table/math），而不是包裹它们的 mystDirective 节点。

#### 2. mystTargets（目标提取）

识别 `(target)=` 标记的锚点，为目标节点设置 identifier/label/html_id 属性。这一步必须在 references（引用解析）之前完成，因为引用解析需要知道有哪些目标存在。

#### 3. containers（容器包装）

将 figure/table/quote/code 等块级元素自动包裹在 container 节点中，并处理 caption/legend 的归属。例如：

```markdown
![caption](img.png)
```
→ 解析为 image 节点 → containers 将 image + caption 包装为 container(kind=figure)。

#### 5. headingDepthTransform（标题深度偏移）

根据页面配置调整标题深度。例如子页面嵌入主文档时，H1 应变为 H2。

#### 11. footnoteTransform（脚注归并）

将内联脚注（`^[text]`）转换为 footnoteDefinition，统一放到文档末尾，并将 footnoteReference 链接到正确的定义。

#### 12. mathTransform（数学公式编号）

处理块级数学公式的编号，支持 subequation 环境（(a), (b) 子编号）。

#### 14. linksTransform（链接处理）

处理 wiki 链接 `[[target]]`、内部链接路径解析、外部链接验证。

## 项目级 transforms

basicTransformations 处理单文档。项目级 transforms 在多个文档间执行：

| Transform | 阶段 | 说明 |
|-----------|------|------|
| `enumerateTargets` | project | 全局编号标题/公式/图表，分配 enumerator |
| `resolveReferences` | project | 解析交叉引用，将 xref 链接到目标节点 |
| `buildToc` | project | 构建目录树（Table of Contents） |
| `includeFiles` | project | 处理 `{include}` 指令，嵌入外部文件内容 |
| `transformCitations` | document/project | 处理参考文献引用，格式化 cite 节点 |
| `embedNodes` | project | 处理 `{embed}` 指令，嵌入其他文档节点 |
| `transformOutputs` | project | 处理 Notebook 输出单元格 |

### 两阶段执行模式

```
单文档阶段 (document stage)
├── mystParse → 原始 AST
├── applyDirectives/applyRoles → 指令/角色展开
└── basicTransformations → 22 个基础 transform
        │
        ▼
跨文档阶段 (project stage)
├── enumerateTargets → 全局编号
├── buildToc → 目录结构
├── includeFiles → 嵌入外部文件
├── resolveReferences → 交叉引用解析
└── embedNodes → 节点嵌入
```

## 核心 transform 列表

### 结构处理
- `liftMystDirectivesAndRoles` — 提升指令/角色子节点
- `containers` — 容器包装
- `sectionHeaders` / `headingDepthTransform` — 标题处理
- `blocks` / `blockMetadata` / `blockToMetadata` — 块与元数据
- `rootNestingTransform` / `nestBlockNestings` / `extractBlockFromSection` — 嵌套处理
- `joinGatesTransform` — 合并门控

### 引用与链接
- `mystTargets` — 目标提取
- `linksTransform` / `checkLinksTransform` / `indexIdentifierTransform` / `simplifyMathIdentifiers` — 链接与标识符
- `footnoteTransform` / `footnoteReferences` — 脚注

### 内容变换
- `mathTransform` — 数学公式
- `codeTransform` / `codeAnchorsTransform` / `inlineCodeTransform` — 代码
- `imageTransform` / `imagesTransform` — 图片
- `paragraphs` / `breaksToText` / `nbspTransform` — 段落与空白
- `abbreviations` / `bulletsToTable` / `blocksToTables` — 缩写与表格
- `siUnitsTransform` / `diff` / `glossary` / `mathAlignmentTransform` — 特殊内容

### 清理
- `removeDirectives` / `hoistSingleDirective` — 移除/提升指令节点
- `transformLegacyJupyterBook` / `transformLegacyContent` / `staticNotebookCellTransform` — 遗留/静态内容
- `logMessagesTransform` / `addCommonDirectives` / `missingReferences` — 日志与缺失引用
- `fillFrontmatter` / `finalizeFrontmatter` — Frontmatter 完善
- `transformLinkedText` / `transformBanner` / `codeHeaderTransform` / `embedAttachmentsTransform` — 其他

### Notebook/输出
- `transformOutputs` / `outputNestedFoldersTransform` / `outputComparisonTransform` — 输出处理
- `transformCollapse` — 可折叠内容
- `transformPlaceholderChildren` — 占位符子节点

### 项目级
- `enumerateTargets` / `enumerateLineNumbers` / `resolveReferences` — 编号与引用
- `buildToc` / `includeFiles` / `embedNodes` — 目录与嵌入
- `transformCitations` / `transformBiblio` / `citationRenderers` — 参考文献
- `transformThumbnail` / `transformDownloads` / `transformBanner` / `embedAttachmentsTransform` — 资源
- `reduceOutputs` / `walkArticles` / `initialize` / `state` — 项目工具

## compositePlugin 机制

`compositePlugin` 将多个 Plugin 按序组合为一个 Plugin，是 basicTransformationsPlugin 的实现方式：

```ts
compositePlugin({ plugins, name }) => Plugin
```

它在内部维护插件数组，processor.use() 时依次注册所有子插件，并提供 name 属性标识组合插件。

## 相关概念

- [MyST 解析器](/concepts/02-myst-parser.md)
- [统一插件架构](/concepts/01-unified-plugin-architecture.md)
- [目标与引用系统](/concepts/07-targets-references.md)
- [错误处理与规则 ID](/concepts/05-error-handling.md)
- [编写自定义 Transform](/examples/02-custom-transform.md)
