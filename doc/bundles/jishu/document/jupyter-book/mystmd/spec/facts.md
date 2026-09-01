---
type: spec
title: "MySTmd 核心引擎源码事实清单"
---

# MySTmd 核心引擎源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: mystmd 是一个 monorepo 项目，核心包位于 `packages/` 目录，包含 myst-parser、myst-transforms、myst-common、myst-config、myst-frontmatter、myst-spec、myst-spec-ext、simple-validators、mystmd、mystmd-py、markdown-it-myst、citation-js-utils、myst-directives、myst-roles、myst-cli 等多个包
- F-002: myst-parser 的 `package.json` 声明依赖 markdown-it、unist-builder、unist-util-visit、unist-util-select、unist-util-remove、myst-common、myst-directives、myst-roles、myst-spec、vfile、markdown-it-myst、markdown-it-front-matter、markdown-it-footnote、markdown-it-task-lists、markdown-it-deflist、he
- F-003: myst-common 的 `package.json` 声明依赖 myst-spec、myst-frontmatter、unist-util-visit、vfile
- F-004: myst-transforms 的 `package.json` 声明依赖 myst-common、myst-spec、myst-spec-ext、myst-frontmatter、unist-util-visit、unist-util-select、unist-util-remove、vfile

## myst-parser 包入口 `src/index.ts`

- F-005: `src/index.ts` 导出：`* from './myst.js'`、`* from './fromMarkdown.js'`、`tokensToMyst from './tokensToMyst.js'`、`plugins as plugins from './plugins.js'`
- F-006: `src/myst.ts` 定义并导出 `defaultOptions`、`parseOptions()`、`createTokenizer()`、`mystParse()`、`mystParser`

## mystParse 函数 `src/myst.ts`

- F-007: `mystParse(content: string, opts?: Options)` 函数：调用 `parseOptions(opts)` 解析选项，调用 `createTokenizer(parsedOpts)` 创建 tokenizer，调用 `tokensToMyst(content, tokenizer.parse(content, { vfile }), parsedOpts.mdast)` 生成 MDAST 树，然后调用 `applyDirectives(tree, ...)` 和 `applyRoles(tree, ...)`，最后返回 tree
- F-008: `applyDirectives` 接收 `parseMyst` 回调函数，该回调递归调用 `mystParse(source, opts)` 解析指令体内容，并通过 `visit` 修正节点位置偏移（`node.position.start.line += offset; node.position.end.line += offset`）
- F-009: `mystParser` 是一个 unified Plugin，类型为 `Plugin<[Options?], string, GenericParent>`，其 `this.Parser = (content: string) => mystParse(content, opts)`

## createTokenizer 函数 `src/myst.ts`

- F-010: `createTokenizer(opts?: Options)` 创建 MarkdownIt 实例，配置基于 `MARKDOWN_IT_CONFIG`，并根据 extensions 开关启用插件：colonFences→colonFencePlugin、frontmatter→frontMatterPlugin+convertFrontMatter、blocks→blockPlugin、footnotes→footnotePlugin（disable footnote_inline）、citations→citationsPlugin、始终启用 rolePlugin 和 directivePlugin、math→mathPlugin、deflist→deflistPlugin、tasklist→tasklistPlugin
- F-011: `defaultOptions` 中 extensions 默认值：smartquotes=true, colonFences=true, frontmatter=true, math=true, footnotes=true, citations=true, deflist=true, tasklist=true, tables=true, blocks=true, strikethrough=false
- F-012: `defaultOptions` 中 directives 默认值为 `defaultDirectives`（来自 myst-directives），roles 默认值为 `defaultRoles`（来自 myst-roles）
- F-013: `parseOptions(opts?)` 将用户选项与 defaultOptions 合并：vfile 默认 new VFile()，mdast/markdownit/extensions 使用展开合并，directives 和 roles 数组合并（`[...defaultOptions.directives, ...(opts?.directives ?? [])]`）

## MarkdownParseState 类 `src/fromMarkdown.ts`

- F-014: `MarkdownParseState` 类属性：`src: string`、`stack: GenericNode[]`、`handlers: Record<string, TokenHandler>`
- F-015: `MarkdownParseState.constructor(src, handlers)` 初始化 stack 为 `[u('root', [] as GenericParent[])]`，handlers 调用 `getTokenHandlers(handlers)` 转换
- F-016: `top()` 返回 `this.stack[this.stack.length - 1]`
- F-017: `addNode(node?)` 将 node 添加到 `top().children`，支持 GenericNode 类型
- F-018: `addText(text, token, type='text', attrs?)` 添加文本节点，连续 text 节点自动合并（`last.value += value`）
- F-019: `openNode(type, token, attrs, isLeaf=false)` 创建新节点压入 stack，非叶子节点初始化 children=[]
- F-020: `closeNode()` 弹出 stack 顶部节点并通过 addNode 添加到父节点
- F-021: `parseTokens(tokens?)` 遍历 tokens，跳过 hidden 且不在 UNHIDDEN_TOKENS 集合中的 token，查找 handler 并执行
- F-022: `addPositionsToNode(node, token)` 根据 token.map 计算 position（start: line+1/col+1, end: line/col+1）
- F-023: UNHIDDEN_TOKENS 集合包含：parsed_directive_open/close、directive_arg_open/close、directive_body_open/close、myst_option_open/close、parsed_role_open/close、role_body_open/close

## TokenHandlerSpec 与 getTokenHandlers `src/fromMarkdown.ts`

- F-024: `TokenHandlerSpec` 类型包含：`type: string`、`getAttrs?: (token, tokens, index, state) => Record<string, any>`、`attrs?: Record<string, any>`、`noCloseToken?: boolean`、`isText?: boolean`、`isLeaf?: boolean`
- F-025: `MdastOptions` 类型包含：`handlers?: Record<string, TokenHandlerSpec>`、`hoistSingleImagesOutofParagraphs?: boolean`、`listItemParagraphs?: boolean`、`nestBlocks?: boolean`
- F-026: `AllOptions` 类型包含：`vfile: VFile`、`markdownit: MarkdownIt.Options`、`extensions: {...}`、`mdast: MdastOptions`、`directives: DirectiveSpec[]`、`roles: RoleSpec[]`
- F-027: `getTokenHandlers(specHandlers)` 为每个 token type 生成 handler：noCloseToken 类型（code_inline/code_block/fence 等）直接 openNode→addText→closeNode；有 open/close 的类型分别注册 `type+'_open'`（openNode）和 `type+'_close'`（closeNode）；额外注册 text、inline（递归 parseTokens）、softbreak handlers

## tokensToMyst 函数 `src/tokensToMyst.ts`

- F-028: `tokensToMyst(src: string, tokens: Token[], options=defaultOptions)` 创建 MarkdownParseState，调用 parseTokens(tokens)，循环 closeNode 直到 stack 清空得到 tree
- F-029: tokensToMyst 后处理步骤：1) remove(tree, '_remove') 移除标记节点；2) liftChildren(tree, '_lift') 提升子节点；3) 处理 task list（selectAll listItem[__taskList=true]，提取 checked 属性，移除 inline html）；4) listItemParagraphs 时调用 listItemParagraphsTransform；5) 处理 crossReference（将 value 转为 children 文本节点）；6) nestBlocks 时按 blockBreak 切分嵌套 block 节点；7) hoistSingleImagesOutofParagraphs 时将单图片段落提升为图片节点，否则 nestSingleImagesIntoParagraphs
- F-030: defaultMdast 中定义了 40+ 个 token type 到 MDAST 节点的映射，包括 heading→{type:'heading', depth}、paragraph→'paragraph'、blockquote→'blockquote'、ordered_list/bullet_list→'list'、list_item→'listItem'、em→'emphasis'、strong→'strong'、colon_fence/fence/code_block→'code'、code_inline→'inlineCode'、hardbreak→'break'、link→'link'、image→'image'、dl→'definitionList'、dt→'definitionTerm'、dd→'definitionDescription'、table→'table'、thead/tbody→'_lift'、tr→'tableRow'、th/td→'tableCell'、math_inline→'inlineMath'、math_inline_double/math_block/math_block_label/amsmath→'math'、footnote_ref→'footnoteReference'、footnote_anchor→'_remove'、footnote_block→'_lift'、footnote→'footnoteDefinition'、cite→'cite'、cite_group→'citeGroup'、parsed_directive→'mystDirective'、directive_arg→'mystDirectiveArg'、directive_body→'mystDirectiveBody'、directive_error→'mystDirectiveError'、myst_option→'mystOption'、parsed_role→'mystRole'、role_body→'mystRoleBody'、role_error→'mystRoleError'、myst_target→'mystTarget'、html_inline/html_block→'html'、myst_block_break→'blockBreak'、myst_line_comment→'comment'
- F-031: fence token 的 getAttrs 提取 lang、name（label/identifier）、class、showLineNumbers、startingLineNumber、emphasizeLines 等属性
- F-032: table token 的 getAttrs 提取 kind（undefined）、label/identifier、enumerated、class、align 等属性

## MARKDOWN_IT_CONFIG `src/config.ts`

- F-033: MARKDOWN_IT_CONFIG 配置 html=true、xhtmlOut=true、breaks=false、langPrefix='language-'、linkify=false、typographer=false、quotes='"\u201c\u201d\u2018\u2019"'、maxNesting=20
- F-034: MARKDOWN_IT_CONFIG.core.rules 包含 normalize、block、inline、linkify、text_join
- F-035: MARKDOWN_IT_CONFIG.block.rules 包含 blockquote、code、fence、heading、hr、html_block、lheading、list、reference、paragraph
- F-036: MARKDOWN_IT_CONFIG.inline.rules 包含 autolink、backticks、emphasis、entity、escape、html_inline、image、link、newline、text
- F-037: EXCLUDE_TLDS 列表：['py', 'md', 'dot', 'next', 'so', 'es', 'java', 'zip', 'sc', 'ir']

## applyDirectives 函数 `src/directives.ts`

- F-038: `applyDirectives(tree, specs: DirectiveSpec[], vfile, ctx: DirectiveContext)` 构建 specLookup（name→DirectiveSpec 映射，支持 alias 数组或字符串），selectAll('mystDirective[processed=false]') 查找所有未处理指令节点
- F-039: 对每个 mystDirective 节点：如果 spec.body.type !== 'myst' 则调用 markChildrenAsProcessed(node) 标记子节点已处理；删除 processed 属性；未知指令调用 fileError 并删除 children
- F-040: 指令处理流程：1) 处理 arg（mystDirectiveArg 子节点，通过 contentFromNode 提取）；2) 处理 options（parseOptions 解析）；3) 处理 body（mystDirectiveBody 子节点）；4) 调用 validate(data, vfile)（如有）；5) 调用 run(data, vfile, ctx) 返回 children 替换 node.children
- F-041: ctx.parseMyst 在 applyDirectives 中被包装为 offset + node.position.start.line 的全局行偏移

## applyRoles 函数 `src/roles.ts`

- F-042: `applyRoles(tree, specs: RoleSpec[], vfile)` 结构与 applyDirectives 类似，构建 specLookup，selectAll('mystRole[processed=false]') 查找角色节点
- F-043: RoleSpec 不包含 arg 字段，只有 body、options、validate、run；run 签名为 `(data: RoleData, vfile: VFile) => GenericNode[]`（无 ctx 参数）

## plugins 模块 `src/plugins.ts`

- F-044: plugins.ts 重新导出：frontMatterPlugin（from markdown-it-front-matter）、footnotePlugin（from markdown-it-footnote）、tasklistPlugin（from markdown-it-task-lists）、deflistPlugin（from markdown-it-deflist）、rolePlugin/directivePlugin/citationsPlugin/blockPlugin/colonFencePlugin/mystPlugin（from markdown-it-myst）、mathPlugin（from ./math.js）
- F-045: convertFrontMatter 是一个 markdown-it 插件，在 core ruler 上 'block' 之后注册 'convert_front_matter'，将 front_matter token 替换为 fence token（info='yaml', content=token.meta）

## myst-common 类型系统 `src/types.ts`

- F-046: `GenericNode<T>` 类型：`{ type: string; kind?: string; children?: GenericNode[]; value?: string; identifier?: string; label?: string; position?: Node['position'] } & T`
- F-047: `GenericParent<T> = GenericNode<T> & { children: GenericNode<T>[] }`
- F-048: `ParseTypesEnum` 枚举：string='string', number='number', boolean='boolean', parsed='parsed'
- F-049: `ParseTypes = string | number | boolean | GenericNode[]`
- F-050: `ArgDefinition` 类型：`{ type: ParseTypesEnum | typeof Boolean | typeof String | typeof Number | 'myst'; required?: boolean; doc?: string }`
- F-051: `BodyDefinition = ArgDefinition`
- F-052: `OptionDefinition = ArgDefinition & { alias?: string[] }`
- F-053: `DirectiveData` 类型：`{ name: string; node: Directive & { tight?: boolean | 'before' | 'after' }; arg?: ParseTypes; options?: Record<string, ParseTypes>; body?: ParseTypes }`
- F-054: `RoleData` 类型：`{ name: string; node: Role; body?: ParseTypes; options?: Record<string, ParseTypes> }`
- F-055: `DirectiveContext` 类型：`{ parseMyst: (source: string, offset?: number) => GenericParent }`
- F-056: `DirectiveSpec` 类型：`{ name: string; alias?: string[]; doc?: string; arg?: ArgDefinition; options?: Record<string, OptionDefinition>; body?: BodyDefinition; validate?: (data, vfile) => DirectiveData; run: (data, vfile, ctx) => GenericNode[] }`
- F-057: `RoleSpec` 类型：`{ name: string; alias?: string[]; doc?: string; options?: Record<string, OptionDefinition>; body?: BodyDefinition; validate?: (data, vfile) => RoleData; run: (data, vfile) => GenericNode[] }`
- F-058: `TransformSpec` 类型：`{ name: string; doc?: string; stage: 'document' | 'project'; plugin: Plugin<[PluginOptions?, PluginUtils], GenericParent, GenericParent | Promise<GenericParent>> }`
- F-059: `MystPlugin` 类型：`{ name?: string; author?: string; license?: string; directives?: DirectiveSpec[]; roles?: RoleSpec[]; transforms?: TransformSpec[] }`
- F-060: `ValidatedMystPlugin = Required<Pick<MystPlugin, 'directives'|'roles'|'transforms'>> & { paths: string[] }`
- F-061: `PluginUtils` 类型：`{ select: Select; selectAll: SelectAll }`，其中 Select=`(selector, tree?) => GenericNode|null`，SelectAll=`(selector, tree?) => GenericNode[]|null`
- F-062: `TargetKind` 枚举：heading='heading', equation='equation', subequation='subequation', figure='figure', table='table', code='code'
- F-063: `AdmonitionKind` 枚举：admonition/attention/caution/danger/error/important/hint/note/seealso/tip/warning
- F-064: `NotebookCell` 枚举：content='notebook-content', code='notebook-code'
- F-065: `NotebookCellTags` 枚举：removeStderr/removeStdout/hideCell/hideInput/hideOutput/removeCell/removeInput/removeOutput/scrollOutput/skipExecution/raisesException（值为 kebab-case）
- F-066: `Citations` 类型：`{ order: string[]; data: Record<string, {label, html, enumerator, doi?, url?}> }`
- F-067: `References` 类型：`{ cite?: Citations; article?: GenericParent }`
- F-068: `FrontmatterPart` 类型：`{ mdast: GenericParent; frontmatter?: PageFrontmatter }`
- F-069: `FrontmatterParts = Record<string, FrontmatterPart>`

## myst-common 工具导出 `src/index.ts`

- F-070: myst-common/index.ts 从 utils.js 导出：admonitionKindToTitle, toText, fileError, fileWarn, fileInfo, createId, normalizeLabel, createHtmlId, transferTargetAttrs, liftChildren, setTextAsChild, copyNode, mergeTextNodes, writeTexLabelledComment, getMetadataTags, slugToUrl
- F-071: myst-common/index.ts 导出：plural、selectBlockParts/extractPart、parseIndexLine/splitEntryValue/createIndexEntries、RuleId/RULE_ID_DESCRIPTIONS/RULE_DEFAULT_SEVERITY、isTargetIdentifierNode/selectMdastNodes、TemplateKind/TemplateOptionType
- F-072: myst-common/index.ts 从 types.js 重新导出枚举：AdmonitionKind、NotebookCell、NotebookCellTags、ParseTypesEnum、TargetKind，以及所有类型定义

## RuleId 枚举 `src/ruleids.ts`

- F-073: RuleId 枚举包含约 80 个规则 ID，涵盖：frontmatter（9个）、export（11个）、parse（4个）、directive/role（7个）、project structure（4个）、image（5个）、math（6个）、reference（7个）、link（9个）、notebook（2个）、content（7个）、citation（3个）、code（6个）、static file（5个）、plugin（1个）、container（1个）、file（1个）、execution（2个）
- F-074: RULE_ID_DESCRIPTIONS 为每个 RuleId 提供英文描述字符串

## myst-transforms 入口 `src/index.ts`

- F-075: myst-transforms 导出 30+ 个 transform 插件，包括：admonitionHeadersPlugin/admonitionHeadersTransform/admonitionBlockquotePlugin/admonitionBlockquoteTransform/admonitionQmdTransform/admonitionQmdPlugin（from admonitions）、captionParagraphPlugin/Transform（caption）、footnotesPlugin/Transform（footnotes）、htmlPlugin/Transform/reconstructHtmlPlugin/Transform（html）、htmlIdsPlugin/Transform（htmlIds）、keysPlugin/Transform（keys）、mathPlugin/LabelPlugin/NestingPlugin/Transform/LabelTransform/NestingTransform/renderEquation（math）、inlineMathSimplificationPlugin/Transform（mathSimplifications）、blockNestingPlugin/Transform/blockMetadataPlugin/Transform（blocks）、codePlugin/Transform/inlineCodeFlattenPlugin/Transform（code）、blockquotePlugin/Transform（blockquote）、imageAltTextPlugin/Transform（images）、buildIndexTransform/indexIdentifierPlugin/Transform（indices）、liftMystDirectivesAndRolesPlugin/Transform（liftMystDirectivesAndRoles）、links 子模块全部导出、mystTargetsPlugin/Transform/headingLabelPlugin/Transform（targets）、joinGatesPlugin/Transform（joinGates）、glossaryPlugin/Transform（glossary）、abbreviationPlugin/Transform（abbreviations）、includeDirectivePlugin/Transform（include）、containerChildrenPlugin/Transform（containers）、headingDepthPlugin/Transform（headings）、buildTocTransform（toc）
- F-076: myst-transforms 导出 enumerate 相关：addChildrenFromTargetNode、enumerateTargetsTransform/Plugin、resolveLinksAndCitationsTransform、resolveReferencesTransform/Plugin、ReferenceState、MultiPageReferenceResolver、IReferenceStateResolver、ReferenceKind、TargetCounts
- F-077: myst-transforms 导出复合插件：basicTransformationsPlugin、basicTransformations（from basic）
- F-078: myst-transforms 导出 unnestTransform（from unnest）、getFrontmatter（from frontmatter）

## basicTransformations 复合插件 `src/basic.ts`

- F-079: `basicTransformations(tree, file, opts?)` 按序执行 21 个 transform：1) liftMystDirectivesAndRolesTransform；2) mystTargetsTransform；3) captionParagraphTransform；4) codeBlockToDirectiveTransform(tree, file, {translate:['math','mermaid']})；5) mathNestingTransform；6) mathLabelTransform；7) subequationTransform；8) headingLabelTransform；9) admonitionQmdTransform；10) admonitionBlockquoteTransform；11) admonitionHeadersTransform；12) joinGatesTransform；13) blockNestingTransform；14) blockMetadataTransform；15) blockToFigureTransform(tree, opts)；16) containerChildrenTransform；17) htmlIdsTransform；18) imageAltTextTransform；19) blockquoteTransform；20) removeUnicodeTransform；21) headingDepthTransform；22) inlineCodeFlattenTransform
- F-080: basicTransformationsPlugin 是 unified Plugin 类型，接收 opts 参数，在 plugin 函数中调用 basicTransformations(tree, file, opts)

## liftMystDirectivesAndRolesTransform `src/liftMystDirectivesAndRoles.ts`

- F-081: liftMystDirectivesAndRolesTransform selectAll('mystDirective,mystRole') 节点：对首个子节点有 identifier 的节点，删除父节点的 identifier/label/html_id，调用 transferTargetAttrs(n, child) 将目标属性转移给子节点；然后 liftChildren(tree, 'mystDirective') 和 liftChildren(tree, 'mystRole') 提升指令和角色节点

## getFrontmatter `src/frontmatter.ts`

- F-082: `getFrontmatter(file, tree, opts={propagateTargets:true})` 返回 `{tree, frontmatter, identifiers}`：propagateTargets 时先执行 liftMystDirectivesAndRolesTransform 和 mystTargetsTransform；查找第一个 code 节点（lang==='yaml'）解析为 YAML frontmatter，标记为 __delete__；preFrontmatter 通过 fillProjectFrontmatter 合并；frontmatter.title 为空时取第一个 heading 文本；H1 标题与 frontmatter.title 相同时删除 heading 节点；remove(tree, '__delete__') 清理
- F-083: getFrontmatter 处理 block 嵌套结构：如果 tree.children[0] 是 block 类型，从该 block 中查找 firstNode

## myst-config 包 `src/index.ts`

- F-084: myst-config/index.ts 导出 project 和 site 子模块的全部内容，并定义 `Config` 类型：`{ version: 1; extend?: string[]; project?: ProjectConfig; site?: SiteConfig }`
- F-085: ProjectConfig 类型（src/project/types.ts）：扩展 ProjectFrontmatter，添加 `remote?: string`、`index?: string`、`exclude?: string[]`、`plugins?: PluginInfo[]`、`error_rules?: ErrorRule[]`
- F-086: PluginInfo 类型：`{ type: PluginTypes; path: string }`，PluginTypes 枚举：javascript='javascript', executable='executable'
- F-087: VERSION 常量 = 1（src/project/types.ts）
- F-088: SiteConfig 类型（src/site/types.ts）：扩展 SiteFrontmatter，添加 `projects?: SiteProject[]`（deprecated，1:1映射）、`nav?: SiteNavItem[]`、`actions?: SiteAction[]`、`domains?: string[]`、`template?: string`
- F-089: SiteNavItem 类型：`{ title: string; url?: string; internal?: boolean; children?: SiteNavItem[]; static?: boolean }`
- F-090: SiteAction 类型：`{ title: string; url: string; filename?: string; format?: ExportFormats; internal?: boolean; static?: boolean }`
- F-091: SiteProject 类型：`{ slug?: string; remote?: string; path?: string }`
- F-092: ErrorRule 类型（src/errorRules/types.ts）：`{ id: string; severity: 'ignore'|'warn'|'error'; key?: string } & Record<string, any>`
- F-093: SiteManifest 类型：`{ version: number; myst: string; id?: string; projects?: ManifestProject[]; nav?; actions?; domains?; favicon?; template?; parts?: FrontmatterParts }`（不含 SiteFrontmatter.parts）

## myst-frontmatter 包 `src/index.ts`

- F-094: myst-frontmatter/index.ts 导出 20+ 个子模块：affiliations、biblio、contributors、downloads、exports、funding、jupytext、kernelspec、licenses、numbering、page、project、references、settings、site、thebe、utils、venues、socials、math、execute

## myst-spec 节点类型 `src/index.ts` 与 `src/ext.ts`

- F-095: myst-spec/src/index.ts 从 schema.d.ts 重新导出基础类型：Abbreviation、AdmonitionTitle、Alternative、Association、BlockBreak、Blockquote、Break、Caption、Comment、Definition、Directive、Emphasis、FlowContent、HTML、ImageReference、InlineCode、Legend、LinkReference、List、ListContent、Literal、Node、OptionalAssociation、Paragraph、Parent、PhrasingContent、Point、Position、Reference、Resource、Role、Root、StaticPhrasingContent、Strong、Subscript、Superscript、Table、TableRow、Target、Text、ThematicBreak、UnderlineStatic
- F-096: myst-spec/src/index.ts 从 ext.ts 导出扩展类型：Admonition、AlgorithmLine、AnyWidget、Aside、Block、CaptionNumber、Cite、CiteGroup、CiteKind、Code、CodeBlock、Container、CrossReference、DefinitionDescription、DefinitionList、DefinitionTerm、Delete、Dependency、Embed、FootnoteDefinition、FootnoteReference、Heading、Iframe、Image、Include、IndexEntry、IExpressionResult、InlineExpression、InlineMath、Link、ListItem、Math、MathGroup、Output、Outputs、Raw、SiUnit、Smallcaps、TabItem、TableCell、TabSet、Underline
- F-097: myst-spec/src/index.ts 导出 SourceFileKind 枚举（Article/Notebook/Part）
- F-098: myst-spec/src/ext.ts 定义 InlineMath（扩展 Target 类型，添加 typst? 字段）、Math（kind?:'subequation', tight?:'before'|'after'|boolean, typst?）、MathGroup（type:'mathGroup', enumerated?, enumerator?, children:Math[]）、Cite（type:'cite', kind:CiteKind='narrative'|'parenthetical', label, identifier?, children?, error?, prefix?, suffix?, partial?:'author'|'year', enumerator?）、CiteGroup（type:'citeGroup', kind, children:Cite[]）
- F-099: myst-spec/src/ext.ts 定义 Delete（type:'delete'）、Underline（type:'underline'）、Smallcaps（type:'smallcaps'）、DefinitionList/Term/Description、CaptionNumber、AlgorithmLine（indent?, enumerator?）、TabSet/TabItem（title, sync?, selected?）
- F-100: myst-spec/src/ext.ts 定义 Heading（扩展 SpecHeading & Target，implicit?:true）、Image（urlSource?, urlOptimized?, height?, placeholder?）、Iframe（src, width?, align?, class?, title?, children?:Image[]）、Admonition（icon?, open?）、Block（kind?, visibility?:'show'|'hide'|'remove'）、Code（executable?, filename?, visibility?）、ListItem（checked?）
- F-101: myst-spec/src/ext.ts 定义 CrossReference（urlSource?, remote?, url?, dataUrl?, remoteBaseUrl?, html_id?, class?）、Link（urlSource?, dataUrl?, internal?, static?, protocol?, error?, class?）、Container（kind:'figure'|'table'|'quote'|'code'|string, source?, subcontainer?, noSubcontainers?, parentEnumerator?）、Include（file, literal?, filter?, lang?, showLineNumbers?, startingLineNumber?, emphasizeLines?, filename?, identifier?, label?）、Embed、Raw（lang?, tex?, typst?, value?）、Output/Outputs、Aside、AnyWidget、Output、Outputs、InlineExpression（value, identifier?, result?, children?）
- F-102: myst-spec/src/search.ts 导出 ContentRecord、DocumentHierarchy、HeadingRecord、MystSearchIndex、SearchRecord、SearchRecordBase 类型

## myst-spec-ext 包 `src/index.ts`

- F-103: myst-spec-ext/src/index.ts 重新导出 myst-spec 的所有扩展类型，并标记为 @deprecated（"Use ... from myst-spec instead"），共 38 个 deprecated 类型别名
- F-104: myst-spec-ext 重复声明 SourceFileKind 枚举（注释说明 esbuild/bun 兼容性问题）

## simple-validators 包 `src/index.ts`

- F-105: simple-validators/src/index.ts 导出类型 ValidationOptions、KeyOptions（from types）
- F-106: simple-validators/src/index.ts 导出函数：defined、locationSuffix、incrementOptions、validationError、validationWarning、validateBoolean、validateString、validateNumber、validateUrl、validateSubdomain、validateDomain、validateEmail、validateChoice、validateEnum、validateDate、validateObject、validateKeys、validateObjectKeys、validateList、fillMissingKeys、filterKeys
- F-107: validateBoolean 接受 'true'/'false' 字符串（不区分大小写）和布尔值，其他值返回 validationError
- F-108: validateNumber 使用 Number(input) 强制转换，支持 min/max/integer 选项
- F-109: validationError 检查 suppressErrors，将错误推入 messages.errors 数组，调用 errorLogFn
- F-110: validationWarning 检查 suppressWarnings，将警告推入 messages.warnings 数组，调用 warningLogFn
- F-111: incrementOptions(property, opts) 返回新的 ValidationOptions，更新 property 和 location（`opts.location.opts.property`）
- F-112: defined(val) 返回 val != null（排除 null 和 undefined）

## mystmd CLI 主入口 `src/index.ts`

- F-113: mystmd/src/index.ts 使用 commander 创建 Command 程序，注册子命令：makeInitCLI(program)、makeBuildCLI(program)、makeStartCLI(program)、makeCleanCLI(program)、makeTemplatesCLI(program)
- F-114: CLI 全局选项：-v/--version（输出版本号）、-d/--debug（日志输出错误）、--config <config-file>（指定替代YAML配置文件）
- F-115: CLI 启动时导入 core-js/actual 提供向后兼容，抑制 punycode DeprecationWarning
- F-116: makeBuildCLI 调用 clirun(Session, build, program, {keepAlive: (_,opts)=>!!opts.watch})

## mystmd CLI 子命令

- F-117: mystmd/src/build.ts 中 makeBuildCLI 从 myst-cli 导入 makeBuildCommand 和 build/Session，使用 clirun 包装
- F-118: myst-cli 的 build 命令支持 --watch 选项（keepAlive 为 true）
- F-119: mystmd/src/init.ts 导出 makeInitCLI 和 addDefaultCommand
- F-120: mystmd/src/clean.ts 导出 makeCleanCLI
- F-121: mystmd/src/start.ts 导出 makeStartCLI
- F-122: mystmd/src/templates.ts 导出 makeTemplatesCLI
- F-123: mystmd/src/options.ts 定义 CLI 选项
- F-124: mystmd/src/clirun.ts 提供 CLI 运行时包装器

## markdown-it-myst 包 `src/index.ts`

- F-125: markdown-it-myst/src/index.ts 导出 rolePlugin（from roles）、directivePlugin（from directives）、citationsPlugin（from citations）、blockPlugin（from block）、colonFencePlugin（from colonFence）
- F-126: markdown-it-myst 提供 mystPlugin（已 deprecated），内部 md.use(rolePlugin).use(directivePlugin)

## citation-js-utils 包 `src/index.ts`

- F-127: citation-js-utils 使用 @citation-js/core、@citation-js/plugin-bibtex、@citation-js/plugin-csl 处理引用
- F-128: citation-js-utils 配置 bibtex 插件：config.format.useIdAsLabel=true, config.format.checkLabel=false
- F-129: CSL 类型定义包含 type、id、author、issued、accessed、publisher、title、citation-key、container-title、abstract、DOI、URL、ISBN、ISSN、issue、keyword、page、volume 等字段
- F-130: CitationJSStyles 枚举：apa='citation-apa', vancouver='citation-vancouver', harvard='citation-harvard1'
- F-131: InlineCite 枚举：p='p', t='t'
- F-132: getInlineCitation(data: CSL, kind: InlineCite, opts?) 根据作者数量生成不同的内联引用文本（1人→Family, 2人→Family & Family, 3+人→Family et al.），支持 partial:'author'|'year' 选项
- F-133: parseBibTeX(source: string) 调用 new Cite(source).data 返回 CSL[]
- F-134: parseCSLJSON(source: object[]) 调用 cleanCSL(source) 返回清理后的 CSL[]
- F-135: getCitationRenderers(data: CSL[]) 返回 CitationRenderer（Record<string, {render, inline, getDOI, getURL, cite, getLabel, exportBibTeX}>），每个条目的 render 使用 citation-js 的 bibliography 模板格式化（HTML输出）
- F-136: getCitations(bibtex: string) 是 getCitationRenderers 的兼容垫片（先 parseBibTeX 再 getCitationRenderers）
- F-137: yearFromCitation(data: CSL) 从 issued 或 accessed 提取年份，支持 date-parts 和 literal 两种格式，无年份返回 'n.d.'
- F-138: createSanitizer() 返回 cleanCitationHtml 方法，使用 sanitize-html 仅允许 b/a/u/i 标签

## myst-cli 包结构

- F-139: myst-cli/src/index.ts 是 CLI 核心入口，包含 config.ts、docs.ts、executablePlugin.ts、frontmatter.ts、plugins.ts、spec-version.ts
- F-140: myst-cli/src/build/ 包含各格式构建器：docx、html、jats、md、meca、pdf、site、tex，以及 build.ts、clean.ts、legacy.ts、typst.ts、cff.ts
- F-141: myst-cli/src/process/ 包含文件处理：citations、file、mdast、myst、notebook、search、site
- F-142: myst-cli/src/project/ 包含项目加载：fromPath、fromTOC、load、toTOC、utils
- F-143: myst-cli/src/transforms/ 包含 CLI 层 transform：code、dois、embed、images、links、mdast、parts、raw、ror
- F-144: myst-cli/src/session/ 包含 session 和 cache 管理

## 核心数据流

- F-145: Markdown 字符串 → MarkdownIt tokenizer（createTokenizer）→ markdown-it Token 流 → tokensToMyst（MarkdownParseState 栈式解析）→ MDAST 树（root + 基础节点）→ applyDirectives（处理 mystDirective 节点，调用 DirectiveSpec.run 替换 children）→ applyRoles（处理 mystRole 节点，调用 RoleSpec.run 替换 children）→ 最终 MDAST 树
- F-146: MDAST 树 → basicTransformationsPlugin（21步复合转换）→ 各专项 transform（enumerate、links、include、footnotes 等）→ 输出渲染（HTML/LaTeX/DOCX/PDF/Typst/JATS/Markdown）
- F-147: 配置加载：myst.yml → Config 类型（version=1, project?, site?, extend?）→ 验证（validateProjectConfig/validateSiteConfig）→ 合并 extend 继承 → ProjectConfig/SiteConfig
- F-148: Frontmatter 解析：文件首个 YAML code block → js-yaml 解析 → fillProjectFrontmatter 合并预定义 frontmatter → 与第一个 H1 标题合并标题 → PageFrontmatter
