---
type: Concept
title: 公共类型系统（myst-common）
description: myst-common 包定义了 MySTmd 所有包共享的核心类型（GenericNode/DirectiveSpec/RoleSpec/TransformSpec/MystPlugin）、RuleId 枚举以及工具函数，是整个引擎的类型基础。
tags: [mystmd, types, common, generic-node, ruleid]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-common-source.md"
    facts: [F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-064, F-065, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074]
---

## 类型系统概述

myst-common 是 MySTmd 所有包的类型基础。它定义了 AST 节点基础类型、插件接口、运行时数据结构和工具函数，确保各包之间类型一致。

## 基础节点类型

### GenericNode<T>

```ts
type GenericNode<T = Record<string, any>> = {
  type: string;
  kind?: string;
  children?: GenericNode<T>[];
  value?: string;
  identifier?: string;
  label?: string;
  position?: Position;
} & T;
```

GenericNode 是所有 MDAST 节点的基础类型。它是一个开放类型（T 泛型），允许附加任意属性。核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | **必须**，节点类型标识（如 paragraph/heading/code/math） |
| `kind` | string? | 子类型分类（如 container.kind = 'figure'/'table'） |
| `children` | GenericNode[]? | 子节点（非叶子节点必须有） |
| `value` | string? | 文本值（叶子节点如 text/code/inlineMath） |
| `identifier` | string? | 唯一标识符（用于交叉引用） |
| `label` | string? | 人类可读标签（(target)= 后的值） |
| `position` | Position? | 源文档中的位置信息（start/end line:col） |

### GenericParent<T>

```ts
type GenericParent<T = Record<string, any>> = GenericNode<T> & {
  children: GenericNode<T>[];
};
```

GenericParent 明确声明 children 为必填数组，用于表示父节点类型。

## 插件接口类型

### DirectiveSpec

指令规范定义块级扩展元素的行为：

```ts
type DirectiveSpec = {
  name: string;
  alias?: string[];
  doc?: string;
  arg?: ArgDefinition;
  options?: Record<string, OptionDefinition>;
  body?: BodyDefinition;
  validate?: (data: DirectiveData, vfile: VFile) => DirectiveData;
  run: (
    data: DirectiveData,
    vfile: VFile,
    ctx: DirectiveContext,
  ) => GenericNode[];
};
```

### RoleSpec

角色规范定义行内扩展元素的行为：

```ts
type RoleSpec = {
  name: string;
  alias?: string[];
  doc?: string;
  options?: Record<string, OptionDefinition>;
  body?: BodyDefinition;
  validate?: (data: RoleData, vfile: VFile) => RoleData;
  run: (data: RoleData, vfile: VFile) => GenericNode[];
};
```

### TransformSpec

转换规范定义 AST 转换插件：

```ts
type TransformSpec = {
  name: string;
  doc?: string;
  stage: 'document' | 'project';
  plugin: Plugin<[PluginOptions?, PluginUtils], GenericParent, GenericParent | Promise<GenericParent>>;
};
```

### MystPlugin / ValidatedMystPlugin

```ts
type MystPlugin = {
  name?: string;
  author?: string;
  license?: string;
  directives?: DirectiveSpec[];
  roles?: RoleSpec[];
  transforms?: TransformSpec[];
};

type ValidatedMystPlugin = Required<Pick<MystPlugin, 'directives' | 'roles' | 'transforms'>> & {
  paths: string[];
};
```

ValidatedMystPlugin 是 MystPlugin 验证后的形式——所有字段填充默认值（空数组），并附加插件加载路径。

## 参数定义系统

### ArgDefinition

```ts
type ArgDefinition = {
  type:
    | ParseTypesEnum
    | typeof Boolean
    | typeof String
    | typeof Number
    | 'myst';
  required?: boolean;
  doc?: string;
};

type BodyDefinition = ArgDefinition;  // 与 ArgDefinition 结构相同
```

### OptionDefinition

```ts
type OptionDefinition = ArgDefinition & {
  alias?: string[];  // 选项别名
};
```

### ParseTypesEnum

```ts
enum ParseTypesEnum {
  string = 'string',
  number = 'number',
  boolean = 'boolean',
  parsed = 'parsed',  // 已解析为 MDAST 节点
}
```

type 字段同时接受 JS 构造函数（Boolean/String/Number）和字符串 `'myst'`，表示：
- `Boolean`/`ParseTypesEnum.boolean` → 布尔值
- `String`/`ParseTypesEnum.string` → 字符串
- `Number`/`ParseTypesEnum.number` → 数字
- `ParseTypesEnum.parsed` → 已解析的 MDAST 节点数组
- `'myst'` → MyST Markdown（递归解析为 MDAST）

### ParseTypes

```ts
type ParseTypes = string | number | boolean | GenericNode[];
```

## 运行时数据类型

| 类型 | 说明 |
|------|------|
| `DirectiveData` | 指令运行时数据：{name, node, arg?, options?, body?} |
| `RoleData` | 角色运行时数据：{name, node, body?, options?} |
| `DirectiveContext` | 指令上下文：{parseMyst: (source, offset?) => GenericParent} |
| `PluginUtils` | 插件工具：{select, selectAll}（unist-util-select 封装） |
| `PluginOptions` | 插件选项：Record<string, any> |
| `Citations` | 引用集合：{order: string[]; data: Record<string, CitationEntry>} |
| `References` | 参考资料：{cite?: Citations; article?: GenericParent} |
| `FrontmatterPart` | Frontmatter 部分：{mdast, frontmatter?} |
| `FrontmatterParts` | Frontmatter 部分集合：Record<string, FrontmatterPart> |

## 枚举类型

### TargetKind

```ts
enum TargetKind {
  heading = 'heading',
  equation = 'equation',
  subequation = 'subequation',
  figure = 'figure',
  table = 'table',
  code = 'code',
}
```

### AdmonitionKind

```ts
enum AdmonitionKind {
  admonition = 'admonition',
  attention = 'attention',
  caution = 'caution',
  danger = 'danger',
  error = 'error',
  important = 'important',
  hint = 'hint',
  note = 'note',
  seealso = 'seealso',
  tip = 'tip',
  warning = 'warning',
}
```

`admonitionKindToTitle` 工具函数将枚举值映射为默认标题文本（如 note→"Note"、warning→"Warning"）。

### NotebookCell

```ts
enum NotebookCell {
  content = 'content',
  code = 'code',
}
```

### NotebookCellTags

Notebook 单元格的控制标签（kebab-case 字符串值）：

| 标签 | 作用 |
|------|------|
| `remove-stderr` | 移除 stderr 输出 |
| `remove-stdout` | 移除 stdout 输出 |
| `hide-cell` | 隐藏整个单元格 |
| `hide-input` | 隐藏输入代码 |
| `hide-output` | 隐藏输出 |
| `remove-cell` | 移除整个单元格 |
| `remove-input` | 移除输入代码 |
| `remove-output` | 移除输出 |
| `scroll-output` | 输出可滚动 |
| `skip-execution` | 跳过执行 |
| `raises-exception` | 标记为预期异常 |

## RuleId 枚举

RuleId 定义了 80+ 种错误/警告规则 ID，用于 VFile 消息分类：

| 类别 | 示例 RuleId | 说明 |
|------|------------|------|
| 解析 | `unknownDirective`, `unknownRole`, `unknownJumpable` | 未知指令/角色/锚点 |
| 引用 | `refNotFound`, `citeNotFound`, `xrefLoop` | 引用目标不存在/循环引用 |
| 链接 | `linkNotFound`, `externalLinkNotFound` | 内部/外部链接失效 |
| 数学 | `mathLabel`, `mathAlignment`, `mathMetadata` | 数学公式问题 |
| 图片 | `imageNotFound`, `imageAltText` | 图片缺失/无 alt 文本 |
| 配置 | `projectConfig`, `siteConfig`, `frontmatter` | 配置错误 |
| 代码 | `codeMetadata`, `executable`, `kernel` | 代码/执行问题 |
| 指令 | `directiveArgs`, `directiveOptions`, `directiveBody` | 指令参数/选项/体错误 |
| 导出 | `exportNotFound`, `exportNoFormat` | 导出问题 |
| 其他 | `duplicateIdentifier`, `missingTOC`, `notebookRun` | 杂项 |

每个 RuleId 都有默认严重级别（error/warn/info），可通过 ErrorRule 配置覆盖。

## 工具函数

### VFile 报告工具

| 函数 | 签名 | 说明 |
|------|------|------|
| `fileError` | `(vfile, message, node, source, ruleId, opts?) => VFileMessage` | 上报错误 |
| `fileWarn` | `(vfile, message, node, source, ruleId, opts?) => VFileMessage` | 上报警告 |
| `fileInfo` | `(vfile, message, node, source, ruleId, opts?) => VFileMessage` | 上报信息 |

### AST 操作工具

| 函数 | 说明 |
|------|------|
| `toText(node)` | 将节点树递归转为纯文本字符串 |
| `createId()` | 创建唯一标识符（基于计数器） |
| `normalizeLabel(raw)` | 规范化标签：生成 {identifier, label, html_id} |
| `createHtmlId(identifier)` | 将 identifier 转为 HTML-safe ID（kebab-case） |
| `liftChildren(tree, test, props?)` | 将匹配节点的子节点提升到父层级 |
| `transferTargetAttrs(sourceNode, targetNode)` | 转移 identifier/label/html_id 属性 |
| `setTextAsChild(node, text)` | 将字符串设置为节点的 text 子节点 |
| `copyNode(node, shallow?)` | 复制节点（深/浅复制） |
| `mergeTextNodes(tree)` | 合并相邻的 text 节点 |

### 文档工具

| 函数 | 说明 |
|------|------|
| `selectBlockParts(tree, selector)` | 按选择器提取文档部分 |
| `extractPart(part, nodeType)` | 从部分中提取指定类型节点 |
| `parseIndexLine(value)` | 解析索引条目行 |
| `createIndexEntries(entry)` | 创建索引条目节点 |
| `selectMdastNodes(tree, identifier, opts?)` | 按 identifier 选择节点 |
| `plural(word, count)` | 英文复数化（简单 s/es 规则） |
| `slugToUrl(slug, opts?)` | 将 slug 转为 URL 路径 |

## 相关概念

- [统一插件架构](/concepts/01-unified-plugin-architecture.md)
- [错误处理与规则 ID](/concepts/05-error-handling.md)
- [MyST 解析器](/concepts/02-myst-parser.md)
