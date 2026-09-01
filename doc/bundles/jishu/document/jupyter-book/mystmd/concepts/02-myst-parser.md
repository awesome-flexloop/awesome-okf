---
type: concept
title: MyST 解析器（myst-parser）
description: myst-parser 包提供 MyST Markdown 的核心解析能力，包括 markdown-it 分词器创建、Token 到 MDAST 的转换、指令和角色的后处理，以及 VFile 错误收集。
tags: [mystmd, parser, markdown-it, mdast, tokenization]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-parser-source.md"
    facts: [F-001, F-002, F-003, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045]
---

## 解析器概述

myst-parser 是 MyST Markdown 的核心解析包，负责将 MyST Markdown 字符串转换为 MDAST（Markdown Abstract Syntax Tree）树。解析过程分为三个阶段：

1. **Tokenization（分词）**：使用 markdown-it 将 Markdown 文本转换为 Token 流
2. **MDAST Build（AST 构建）**：通过 `MarkdownParseState` 栈式解析 Token 流，构建 MDAST 树
3. **Directives/Roles Processing（指令/角色后处理）**：将 mystDirective/mystRole 节点替换为具体的扩展节点

## 核心入口

```ts
mystParse(content: string, opts?: Options): GenericParent
```

`mystParse` 是整个解析流程的入口，返回 MDAST 根节点（type: 'root'）。它内部执行：
1. 合并内置 directives/roles 与用户传入的扩展
2. 创建 markdown-it tokenizer
3. 分词得到 Token 数组
4. tokensToMyst 将 Token 转换为 MDAST
5. applyDirectives / applyRoles 处理扩展
6. 返回完整的 MDAST 树

## Options 配置

mystParse 接受的 Options 接口：

```ts
type Options = {
  markdownit?: MarkdownIt.Options & {
    tokens?: boolean;                              // 保留 Token 信息（debug 用）
    linkify?: boolean;                             // 启用链接自动识别
  };
  directives?: DirectiveSpec[];                    // 自定义指令
  roles?: RoleSpec[];                              // 自定义角色
  extensions?: PluginSimple[];                     // 额外 markdown-it 插件
  vfile?: VFile;                                   // 错误收集 VFile（不传则新建）
  mdast?: MdastExtends;                            // Token→MDAST 映射扩展
  positions?: boolean;                             // 记录位置信息（默认 true）
  html?: boolean;                                  // 允许 HTML 内容（默认 false）
  directivesFirst?: boolean;                       // 指令优先处理（默认 true）
};
```

## Tokenization 阶段

### createTokenizer

`createTokenizer` 创建并配置 markdown-it 实例，注册所有必要插件：

```ts
createTokenizer(opts: Record<string, any> = {}): MarkdownIt
```

默认配置的 markdown-it 选项：
- `html: false` — 默认禁止原始 HTML
- `linkify: true` — 启用链接自动识别
- 启用 `replacements` 排版扩展（-- → —, ... → …, (c) → © 等）

### 注册的 markdown-it 插件

| 插件 | 来源 | 功能 |
|------|------|------|
| `frontMatterPlugin` | 本包 | 解析 YAML frontmatter `---...---` |
| `mystBlockPlugin` | myst-directives | 解析 MyST 块注释 |
| `mathPlugin` | markdown-it-texmath | 解析 $...$ 和 $$...$$ 数学公式 |
| `mystDirectivePlugin` | myst-directives | 解析 ```{directive} 和 :::directive 指令语法 |
| `mystRolePlugin` | myst-roles | 解析 {role}...{role} 角色语法 |
| `mystCitationsPlugin` | markdown-it-myst | 解析 [cite:@key] 引用语法 |
| `footnotePlugin` | markdown-it-footnote | 解析脚注 |
| `deflistPlugin` | markdown-it-deflist | 解析定义列表 |
| `tasklistPlugin` | markdown-it-task-lists | 解析 - [x] 任务列表 |

## MDAST Build 阶段

### MarkdownParseState

`MarkdownParseState` 是 Token→MDAST 转换的核心状态机，使用栈式解析维护当前父节点栈：

```ts
class MarkdownParseState {
  stack: GenericParent[];               // 父节点栈
  tokens: Token[];                      // Token 数组
  definitions: Record<string, Token>;   // 引用链接定义
  mdast: MdastConfig;                   // Token→MDAST 映射配置
  positions: boolean;                   // 是否记录位置
  
  constructor(defs, opts);
  
  top(): GenericParent;                 // 栈顶
  push(node: GenericNode): void;        // 向当前父节点追加子节点
  openNode(attributes: GenericNode): void;  // 入栈新节点
  closeNode(): GenericNode;             // 出栈
  addText(text: string, position?): void;  // 添加文本节点
  render(tokens: Token[]): GenericNode[];  // 处理所有 Token
}
```

### render() 处理 Token 的状态机逻辑

Token 处理遵循"开闭配对"模式：
- `nesting === 1`（open）→ openNode 创建新节点并入栈
- `nesting === 0`（self-closing）→ 直接 push 节点
- `nesting === -1`（close）→ closeNode 出栈并 push 到新的栈顶

对 inline 类型 Token，会递归处理其子 Token（inline 节点的 children 由其自身的 children Token 列表构成）。

位置信息通过 `openPosition`/`closePosition` 从 Token 的 `map` 属性计算并附加到节点。

### defaultMdast 映射表

`defaultMdast` 对象定义了 40+ 种 Token 类型到 MDAST 节点的映射规则：

| Token 类型 | MDAST type | 说明 |
|-----------|-----------|------|
| text | text | 纯文本 |
| paragraph_open/close | paragraph | 段落 |
| heading_open/close | heading（depth 取自 hLevel） | 标题 |
| bullet_list_open/close | list（ordered=false） | 无序列表 |
| ordered_list_open/close | list（ordered=true） | 有序列表 |
| list_item_open/close | listItem（checked 来自 info） | 列表项 |
| code_block/fence | code | 代码块 |
| code_inline | inlineCode | 行内代码 |
| em_open/close | emphasis | 斜体 |
| strong_open/close | strong | 粗体 |
| s_open/close | delete | 删除线 |
| link_open/close | link（url/title） | 链接 |
| image | image（src/alt/title） | 图片 |
| blockquote_open/close | blockquote | 引用块 |
| hr | thematicBreak | 水平分隔线 |
| table_open/close | table | 表格 |
| math_inline | inlineMath | 行内公式 |
| math_block | math | 块级公式 |
| parsed_directive_open/close | mystDirective | MyST 指令 |
| parsed_role_open/close | mystRole | MyST 角色 |
| cite_group | citeGroup | 引用组 |
| cite | cite（kind 取自 meta.enumerator） | 单个引用 |
| dl_open/close | definitionList | 定义列表 |
| footnote_ref | footnoteReference | 脚注引用 |
| front_matter | __delete__（被过滤） | YAML frontmatter |

## Directives/Roles 处理阶段

### applyDirectives

```ts
applyDirectives(tree, directives, vfile, stack, ctx)
```

遍历树中的 `mystDirective[processed!==true]` 节点：
1. 根据节点名称从 directives 映射中查找 DirectiveSpec
2. 找不到 → 报告 unknownDirective 错误
3. 解析选项（通过 yaml 或键值对解析）
4. 调用 `spec.run(data, vfile, ctx)` 获取子节点数组
5. 将返回节点作为指令节点的 children，并标记 `processed: true`
6. 处理 alias（别名指令名）

`ctx.parseMyst(source, offset)` 回调允许指令递归解析嵌套的 MyST 内容。

### applyRoles

```ts
applyRoles(tree, roles, vfile, vfilePath)
```

遍历树中的 `mystRole[processed!==true]` 节点：
1. 根据节点名称从 roles 映射中查找 RoleSpec
2. 找不到 → 报告 unknownRole 错误
3. 调用 `spec.run(data, vfile)` 获取子节点数组
4. 将返回节点作为角色节点的 children，并标记 `processed: true`

RoleSpec 与 DirectiveSpec 的区别：run 方法无 ctx 参数，角色内部不直接递归解析 MyST。

## Token 过滤与去重

### flattenInlineTokens

行内 Token 数组经过 `flattenInlineTokens` 处理：
- 递归展平嵌套的 Token 数组（处理 markdown-it 插件产生的嵌套 Token）
- 合并相邻的同类型 text Token（避免多个小 text 节点）

### 特殊节点处理

- **footnote_open/close**：当 `info === 'p'` 时创建 footnoteDefinition（非内联脚注）
- **front_matter Token**：被映射为 `__delete__`，从最终 AST 中移除
- **Link 节点**：通过 `parseLinkText(state, url, title, position)` 处理内联链接文本的 Token
- **图片节点**：自闭合 Token，直接创建 image 节点并解析内部 alt 文本

## 相关概念

- [统一插件架构](01-unified-plugin-architecture.md)
- [MDAST 转换管线](03-myst-transforms.md)
- [指令与角色系统](06-directives-and-roles.md)
- [VFile 错误处理](05-error-handling.md)
- [使用 mystParse 解析文档](../examples/00-basic-parsing.md)
