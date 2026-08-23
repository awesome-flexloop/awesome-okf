---
type: concept
title: 统一插件架构（unified/micromark/markdown-it）
description: MySTmd 的插件体系基于 unified 生态的 Plugin 接口，但底层解析使用 markdown-it 而非 micromark。DirectiveSpec/RoleSpec/TransformSpec/MystPlugin 构成完整的扩展契约。
tags: [mystmd, unified, plugin, markdown-it, directive, role, transform]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-common-source.md"
    facts: [F-056, F-057, F-058, F-059, F-060, F-061]
  - path: "/references/myst-transforms-source.md"
    facts: [F-075, F-076, F-077, F-079, F-080]
  - path: "/references/myst-parser-source.md"
    facts: [F-009, F-010, F-044]
---

## unified 生态与 MySTmd 的关系

[unified](https://unifiedjs.com) 是一个文本处理的接口规范，核心概念包括：
- **Plugin**：`(options?) => (tree, file) => void | tree` 形式的函数
- **Processor**：组合 parser、transformer、compiler 的管线
- **VFile**：虚拟文件，携带 path、messages（错误/警告）、data 等
- **Node**：AST 节点，遵循 unist 规范（type + children/value + position）

MySTmd 兼容 unified Plugin 接口，但有以下架构差异：

| 方面 | 标准 unified 生态 | MySTmd |
|------|------------------|--------|
| 分词器 | micromark | markdown-it |
| AST 构建 | mdast-util-from-markdown | 自定义 MarkdownParseState |
| Parser 插件 | micromark 扩展 | markdown-it 插件 |
| Transform 插件 | unified Plugin | unified Plugin（兼容） |

## MySTmd 的三种插件 Spec

### 1. DirectiveSpec（指令）

指令是块级扩展元素，如 ` ```{note} `、` ```{figure} ` 等。

```ts
type DirectiveSpec = {
  name: string;                    // 指令名称
  alias?: string[];                // 别名
  doc?: string;                    // 文档
  arg?: ArgDefinition;             // 参数定义
  options?: Record<string, OptionDefinition>;  // 选项定义
  body?: BodyDefinition;           // 内容体定义
  validate?: (data: DirectiveData, vfile: VFile) => DirectiveData;
  run: (data: DirectiveData, vfile: VFile, ctx: DirectiveContext) => GenericNode[];
};
```

ArgDefinition/BodyDefinition 支持的 type：
- `ParseTypesEnum.string` — 字符串
- `ParseTypesEnum.number` — 数字
- `ParseTypesEnum.boolean` — 布尔值
- `ParseTypesEnum.parsed` — 已解析的 MDAST 节点
- `'myst'` — MyST Markdown（递归解析）
- `Boolean`/`String`/`Number` — JS 构造函数形式

`run` 方法返回 GenericNode[]，替换指令节点的 children。`ctx.parseMyst` 回调可递归解析嵌套的 MyST 内容。

### 2. RoleSpec（角色）

角色是行内扩展元素，如 `{math}`...`{math}`、`{cite}`key`{cite}` 等。

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

RoleSpec 与 DirectiveSpec 的区别：
- 无 `arg` 字段（角色只有 body，没有独立参数行）
- `run` 方法无 `ctx` 参数（角色不需要递归解析 MyST，嵌套解析由指令机制处理）

### 3. TransformSpec（转换插件）

转换插件在 MDAST 构建完成后执行，对 AST 进行变换。

```ts
type TransformSpec = {
  name: string;
  doc?: string;
  stage: 'document' | 'project';   // 单文档阶段或跨文档项目阶段
  plugin: Plugin<
    [PluginOptions | undefined, PluginUtils],
    GenericParent,
    GenericParent | Promise<GenericParent>
  >;
};
```

- **document 阶段**：单文档处理，如 basicTransformations 中的 22 个 transform
- **project 阶段**：跨文档处理，如引用解析（resolveReferences）、目录生成（buildToc）

`PluginUtils` 提供 `select`/`selectAll` 工具（封装 unist-util-select）。

## MystPlugin 集合

```ts
type MystPlugin = {
  name?: string;
  author?: string;
  license?: string;
  directives?: DirectiveSpec[];
  roles?: RoleSpec[];
  transforms?: TransformSpec[];
};
```

MystPlugin 是插件分发的单位，第三方包可以导出一个 MystPlugin 对象，同时注册多个指令、角色和转换。

## markdown-it 插件层

MyST 语法扩展（指令、角色、引用、块分隔、冒号围栏）通过 markdown-it 插件实现，这些插件在 createTokenizer 中注册：

```ts
// markdown-it-myst 提供的插件
import {
  rolePlugin,        // 解析 {role}...{role} 语法
  directivePlugin,   // 解析 ```{directive} 语法
  citationsPlugin,   // 解析 [cite:@key] 语法
  blockPlugin,       // 解析 +++ 块分隔
  colonFencePlugin,  // 解析 ::: 围栏
} from 'markdown-it-myst';
```

这些 markdown-it 插件将扩展语法解析为自定义 Token 类型（parsed_directive、parsed_role、cite_group 等），再由 defaultMdast 映射表转换为 mystDirective/mystRole/cite/citeGroup 等 MDAST 节点。

## 插件注册与执行流程

```
 mystParse(content, { directives, roles })
        │
        ▼
 createTokenizer → MarkdownIt 实例
   ├─ use(rolePlugin) ──────────┐
   ├─ use(directivePlugin) ─────┤  ← markdown-it 插件层
   ├─ use(citationsPlugin) ─────┤    生成自定义 Token
   ├─ use(colonFencePlugin) ────┤
   ├─ use(blockPlugin) ─────────┘
   └─ (其他扩展插件)
        │
        ▼
 tokenizer.parse(content) → Token[]
        │
        ▼
 tokensToMyst → MDAST 树（基础节点 + mystDirective/mystRole）
        │
        ▼
 applyDirectives(tree, directives, vfile, ctx)
   └─ 遍历 mystDirective[processed=false]
      └─ spec.run(data, vfile, ctx) → GenericNode[]
         └─ 替换 node.children
        │
        ▼
 applyRoles(tree, roles, vfile)
   └─ 遍历 mystRole[processed=false]
      └─ spec.run(data, vfile) → GenericNode[]
         └─ 替换 node.children
        │
        ▼
 basicTransformations(tree, file, opts)
   └─ 按序执行 22 个 transform
        │
        ▼
 project stage transforms (跨文档)
```

## transform 的双模式导出

myst-transforms 中的每个转换都提供两种形式：
1. **函数形式**：直接操作 tree，如 `liftMystDirectivesAndRolesTransform(tree)`
2. **Plugin 形式**：unified Plugin 包装，如 `liftMystDirectivesAndRolesPlugin`

```ts
// 函数形式：直接调用
liftMystDirectivesAndRolesTransform(tree);

// Plugin 形式：在 unified pipeline 中使用
processor.use(liftMystDirectivesAndRolesPlugin);
```

## 相关概念

- [MyST 解析器](/concepts/02-myst-parser.md)
- [MDAST 转换管线](/concepts/03-myst-transforms.md)
- [公共类型系统](/concepts/04-myst-common-types.md)
- [自定义指令示例](/examples/05-custom-directive.md)
- [编写自定义 Transform](/examples/02-custom-transform.md)
