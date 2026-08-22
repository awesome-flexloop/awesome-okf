---
type: Reference
title: myst-common 公共类型与工具源码信源
description: myst-common 包的核心类型定义（GenericNode/DirectiveSpec/RoleSpec/TransformSpec/MystPlugin）、RuleId 枚举以及工具函数的源码登记。
tags: [mystmd, common, types, plugin, directive, role, transform]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-common/src/types.ts"
    facts: [F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-064, F-065, F-066, F-067, F-068, F-069]
  - path: "myst-common/src/index.ts"
    facts: [F-070, F-071, F-072]
  - path: "myst-common/src/ruleids.ts"
    facts: [F-073, F-074]
---

## 源码位置

- `myst-common/src/types.ts` — 核心类型定义
- `myst-common/src/index.ts` — 包导出入口
- `myst-common/src/ruleids.ts` — RuleId 枚举与 RULE_ID_DESCRIPTIONS
- `myst-common/src/utils.ts` — 工具函数（fileError/fileWarn/normalizeLabel/liftChildren 等）
- `myst-common/src/selectNodes.ts` — 节点选择工具
- `myst-common/src/indices.ts` — 索引条目处理
- `myst-common/src/templates.ts` — 模板类型
- `myst-common/src/extractParts.ts` — 部分提取
- `myst-common/src/plural.ts` — 复数处理

## 核心类型

### 基础节点类型

| 类型 | 定义 | 说明 |
|------|------|------|
| `GenericNode<T>` | `{ type: string; kind?; children?; value?; identifier?; label?; position? } & T` | 通用 AST 节点 |
| `GenericParent<T>` | `GenericNode<T> & { children: GenericNode<T>[] }` | 有子节点的通用 AST 节点 |

### 插件接口类型

| 类型 | 定义 | 说明 |
|------|------|------|
| `DirectiveSpec` | `{ name; alias?; doc?; arg?; options?; body?; validate?; run: (data, vfile, ctx) => GenericNode[] }` | 指令规范 |
| `RoleSpec` | `{ name; alias?; doc?; options?; body?; validate?; run: (data, vfile) => GenericNode[] }` | 角色规范（无 arg、无 ctx） |
| `TransformSpec` | `{ name; doc?; stage: 'document'\|'project'; plugin: Plugin<...> }` | 转换插件规范 |
| `MystPlugin` | `{ name?; author?; license?; directives?; roles?; transforms? }` | MyST 插件集合 |
| `ValidatedMystPlugin` | `Required<Pick<MystPlugin,'directives'\|'roles'\|'transforms'>> & { paths: string[] }` | 验证后的插件 |

### 参数定义类型

| 类型 | 定义 | 说明 |
|------|------|------|
| `ArgDefinition` | `{ type: ParseTypesEnum\|Boolean\|String\|Number\|'myst'; required?; doc? }` | 参数定义 |
| `BodyDefinition` | `= ArgDefinition` | 指令体定义 |
| `OptionDefinition` | `ArgDefinition & { alias?: string[] }` | 选项定义（含 alias） |
| `ParseTypesEnum` | `string\|number\|boolean\|parsed` | 解析类型枚举 |
| `ParseTypes` | `string \| number \| boolean \| GenericNode[]` | 解析结果类型 |

### 数据类型

| 类型 | 说明 |
|------|------|
| `DirectiveData` | `{ name; node: Directive; arg?; options?; body? }` | 指令运行时数据 |
| `RoleData` | `{ name; node: Role; body?; options? }` | 角色运行时数据 |
| `DirectiveContext` | `{ parseMyst: (source: string, offset?) => GenericParent }` | 指令上下文（递归解析回调） |
| `PluginUtils` | `{ select, selectAll }` | 插件工具（节点选择器） |
| `PluginOptions` | `Record<string, any>` | 插件选项 |
| `Citations` | `{ order: string[]; data: Record<string, {label, html, enumerator, doi?, url?}> }` | 引用集合 |
| `References` | `{ cite?: Citations; article?: GenericParent }` | 参考资料 |
| `FrontmatterPart` | `{ mdast: GenericParent; frontmatter?: PageFrontmatter }` | Frontmatter 部分 |
| `FrontmatterParts` | `Record<string, FrontmatterPart>` | Frontmatter 部分集合 |

### 枚举类型

| 枚举 | 值 | 说明 |
|------|-----|------|
| `TargetKind` | heading/equation/subequation/figure/table/code | 目标类型 |
| `AdmonitionKind` | admonition/attention/caution/danger/error/important/hint/note/seealso/tip/warning | Admonition 类型 |
| `NotebookCell` | content/code | Notebook 单元格类型 |
| `NotebookCellTags` | removeStderr/removeStdout/hideCell/hideInput/hideOutput/removeCell/removeInput/removeOutput/scrollOutput/skipExecution/raisesException | 单元格标签（kebab-case 值） |

### 导出工具函数

| 函数 | 来源 | 说明 |
|------|------|------|
| `fileError/fileWarn/fileInfo` | utils.ts | VFile 错误/警告/信息上报 |
| `toText` | utils.ts | 将节点树转为纯文本 |
| `createId` | utils.ts | 创建标识符 |
| `normalizeLabel` | utils.ts | 规范化标签（生成 identifier/label/html_id） |
| `createHtmlId` | utils.ts | 创建 HTML ID |
| `liftChildren` | utils.ts | 将指定类型节点的子节点提升到父层级 |
| `transferTargetAttrs` | utils.ts | 转移目标属性（identifier/label/html_id） |
| `setTextAsChild` | utils.ts | 将字符串设置为节点的 text 子节点 |
| `copyNode` | utils.ts | 复制节点 |
| `mergeTextNodes` | utils.ts | 合并相邻文本节点 |
| `admonitionKindToTitle` | utils.ts | Admonition 类型转标题文本 |
| `slugToUrl` | utils.ts | slug 转 URL |
| `selectBlockParts/extractPart` | extractParts.ts | 选择/提取文档部分 |
| `parseIndexLine/splitEntryValue/createIndexEntries` | indices.ts | 索引条目解析 |
| `isTargetIdentifierNode/selectMdastNodes` | selectNodes.ts | 节点选择工具 |
| `plural` | plural.ts | 英文复数化 |
| `RuleId` | ruleids.ts | 80+ 规则 ID 枚举 |
| `RULE_ID_DESCRIPTIONS` | ruleids.ts | 规则 ID→描述映射 |
| `TemplateKind/TemplateOptionType` | templates.ts | 模板类型枚举 |
