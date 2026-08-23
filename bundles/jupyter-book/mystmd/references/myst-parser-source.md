---
type: reference
title: myst-parser 解析器源码信源
description: myst-parser 核心解析器源码登记，包含 mystParse、createTokenizer、MarkdownParseState、tokensToMyst、applyDirectives、applyRoles 的完整 API。
tags: [mystmd, parser, markdown-it, mdast, tokenizer]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-parser/src/myst.ts"
    facts: [F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013]
  - path: "myst-parser/src/fromMarkdown.ts"
    facts: [F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027]
  - path: "myst-parser/src/tokensToMyst.ts"
    facts: [F-028, F-029, F-030, F-031, F-032]
  - path: "myst-parser/src/directives.ts"
    facts: [F-038, F-039, F-040, F-041]
  - path: "myst-parser/src/roles.ts"
    facts: [F-042, F-043]
  - path: "myst-parser/src/plugins.ts"
    facts: [F-044, F-045]
  - path: "myst-parser/src/config.ts"
    facts: [F-033, F-034, F-035, F-036, F-037]
  - path: "myst-parser/src/index.ts"
    facts: [F-005]
---

## 源码位置

- `myst-parser/src/myst.ts` — 主入口：mystParse, createTokenizer, defaultOptions, mystParser
- `myst-parser/src/fromMarkdown.ts` — Token→MDAST 状态机：MarkdownParseState, TokenHandlerSpec, MdastOptions, AllOptions
- `myst-parser/src/tokensToMyst.ts` — tokensToMyst 函数与 defaultMdast 映射表（40+ token 映射）
- `myst-parser/src/directives.ts` — applyDirectives：指令处理
- `myst-parser/src/roles.ts` — applyRoles：角色处理
- `myst-parser/src/plugins.ts` — markdown-it 插件重新导出 + convertFrontMatter
- `myst-parser/src/config.ts` — MARKDOWN_IT_CONFIG, EXCLUDE_TLDS
- `myst-parser/src/index.ts` — 包导出入口

## 导出 API

### 核心解析函数

| API | 签名 | 文件 |
|-----|------|------|
| `mystParse` | `(content: string, opts?: Options) => GenericParent` | myst.ts L95 |
| `mystParser` | `Plugin<[Options?], string, GenericParent>` | myst.ts L120 |
| `createTokenizer` | `(opts?: Options) => MarkdownIt` | myst.ts L64 |
| `tokensToMyst` | `(src: string, tokens: Token[], options?: MdastOptions) => GenericParent` | tokensToMyst.ts L527 |
| `applyDirectives` | `(tree: GenericParent, specs: DirectiveSpec[], vfile: VFile, ctx: DirectiveContext) => void` | directives.ts L26 |
| `applyRoles` | `(tree: GenericParent, specs: RoleSpec[], vfile: VFile) => void` | roles.ts L14 |

### 类与类型

| API | 签名 | 文件 |
|-----|------|------|
| `MarkdownParseState` | `class { src, stack, handlers; top(), addNode(), addText(), openNode(), closeNode(), parseTokens(), addPositionsToNode() }` | fromMarkdown.ts L74 |
| `TokenHandlerSpec` | `{ type: string; getAttrs?, attrs?, noCloseToken?, isText?, isLeaf? }` | fromMarkdown.ts L31 |
| `MdastOptions` | `{ handlers?, hoistSingleImagesOutofParagraphs?, listItemParagraphs?, nestBlocks? }` | fromMarkdown.ts L24 |
| `AllOptions` | `{ vfile, markdownit, extensions, mdast, directives, roles }` | fromMarkdown.ts L45 |

### 默认选项

| 选项 | 默认值 |
|------|--------|
| markdownit.html | true |
| extensions.smartquotes | true |
| extensions.colonFences | true |
| extensions.frontmatter | true |
| extensions.math | true |
| extensions.footnotes | true |
| extensions.citations | true |
| extensions.deflist | true |
| extensions.tasklist | true |
| extensions.tables | true |
| extensions.blocks | true |
| extensions.strikethrough | false |
| directives | defaultDirectives（myst-directives） |
| roles | defaultRoles（myst-roles） |

### markdown-it 插件链

createTokenizer 按以下顺序注册插件：
1. colonFencePlugin（若 extensions.colonFences）
2. frontMatterPlugin + convertFrontMatter（若 extensions.frontmatter）
3. blockPlugin（若 extensions.blocks）
4. footnotePlugin（disable footnote_inline）（若 extensions.footnotes）
5. citationsPlugin（若 extensions.citations）
6. rolePlugin + directivePlugin（始终启用）
7. mathPlugin（若 extensions.math）
8. deflistPlugin（若 extensions.deflist）
9. tasklistPlugin（若 extensions.tasklist）

### defaultMdast 映射表关键条目

| markdown-it Token | MDAST type | 备注 |
|-------------------|-----------|------|
| heading | heading | depth 从 tag 提取 |
| paragraph | paragraph | — |
| blockquote | blockquote | — |
| ordered_list | list | ordered=true |
| bullet_list | list | ordered=false |
| list_item | listItem | 处理 task-list-item |
| fence/colon_fence/code_block | code | isLeaf, 提取 lang/linenos/emphasizeLines |
| code_inline | inlineCode | isText |
| link | link | 提取 url/title |
| image | image | 提取 url/alt/title/align/width/height |
| math_inline | inlineMath | isText |
| math_block/math_block_label/amsmath | math | isLeaf, 提取 label/enumerated |
| cite | cite | isLeaf, 提取 identifier/label/kind |
| cite_group | citeGroup | 提取 kind |
| parsed_directive | mystDirective | processed=false |
| parsed_role | mystRole | processed=false |
| myst_target | mystTarget | isLeaf |
| myst_block_break | blockBreak | isLeaf |
| myst_line_comment | comment | isLeaf |
| footnote_ref | footnoteReference | isLeaf |
| footnote_block | _lift | 提升子节点 |
| footnote_anchor | _remove | 删除 |
| html_inline/html_block | html | isText |
| thead/tbody | _lift | 提升 tableRow |

### tokensToMyst 后处理步骤

1. `remove(tree, '_remove')` — 移除标记为 _remove 的节点
2. `liftChildren(tree, '_lift')` — 提升 _lift 节点的子节点
3. 处理 task list（__taskList 属性→checked）
4. listItemParagraphsTransform（确保 listItem 内容被 paragraph 包裹）
5. 处理 crossReference（value→children）
6. nestBlocks（按 blockBreak 切分嵌套 block）
7. hoistSingleImagesOutofParagraphs / nestSingleImagesIntoParagraphs
