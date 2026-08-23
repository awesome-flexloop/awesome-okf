---
type: reference
title: "myst-exporters 事实清单"
description: "myst-exporters 多格式导出器源码事实采集，编号 F-001 起，零推测"
tags: [myst-exporters, facts, spec]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-html/src/index.ts"
    facts: [F-001]
  - path: "myst-to-tex/src/index.ts"
    facts: [F-002, F-003, F-004, F-005, F-006, F-007, F-008]
  - path: "myst-to-tex/src/types.ts"
    facts: [F-009]
  - path: "myst-to-tex/src/preamble.ts"
    facts: [F-010]
  - path: "myst-to-docx/src/index.ts"
    facts: [F-011]
  - path: "myst-to-docx/src/plugin.ts"
    facts: [F-012]
  - path: "myst-to-jats/src/index.ts"
    facts: [F-013, F-014, F-015, F-016, F-017, F-018]
  - path: "myst-to-md/src/index.ts"
    facts: [F-019, F-020]
  - path: "myst-to-typst/src/index.ts"
    facts: [F-021, F-022, F-023, F-024]
  - path: "jtex/src/jtex.ts"
    facts: [F-025, F-026, F-027]
  - path: "jtex/src/render.ts"
    facts: [F-028]
  - path: "jtex/src/tex/imports.ts"
    facts: [F-029]
  - path: "jtex/src/tex/export.ts"
    facts: [F-030]
  - path: "jtex/src/typst/imports.ts"
    facts: [F-031]
  - path: "jats-to-myst/src/index.ts"
    facts: [F-032, F-033, F-034]
  - path: "tex-to-myst/src/index.ts"
    facts: [F-035]
  - path: "myst-to-html/src/renderMdast.ts"
    facts: [F-036]
  - path: "myst-to-html/src/state.ts"
    facts: [F-037]
  - path: "myst-cli/src/build/build.ts"
    facts: [F-038]
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039, F-040]
---

# myst-exporters 事实清单

> 本文档记录 myst-exporters 相关包的源码级事实，编号 F-001 起。所有事实均经过 Grep 级源码验证，不含推断性表述。

## F-001: myst-to-html 导出入口

- 包路径：`myst-to-html/src/index.ts`
- 导出6个符号：`formatHtml`（来自 `./format.js`）、`addMathRenderers`/`renderMath`（来自 `./renderer.js`）、`mystToHast`（来自 `./schema.js`）、`State`（来自 `./state.js`）、`transform`（来自 `./transforms.js`）、`mystToHtml`（来自 `./renderMdast.js`）
- `formatHtml` 是 rehype-format 的条件包装插件（`format.ts`），当传入布尔 true 时启用格式化

## F-002: myst-to-tex 默认导出插件

- 包路径：`myst-to-tex/src/index.ts`
- 默认导出一个 unified `Plugin<[Options?], Root, VFile>`，其 `this.Compiler` 方法接收 `(node, file)` 参数
- Compiler 内部先调用 `transformLegends(node)`，然后创建 `TexSerializer` 实例，最终返回 `LatexResult` 对象

## F-003: TexSerializer 类

- 类路径：`myst-to-tex/src/index.ts` L496-598
- 实现接口 `ITexSerializer`
- 构造函数接收 `(file: VFile, tree: Root, opts?: Options)`
- 构造时初始化 `data`（含 `mathPlugins: {}`、`imports: new Set()`），预构建 `footnotes`/`glossary`/`abbreviations` 字典，调用 `this.renderChildren(tree)` 完成渲染
- 属性：`file`、`data`、`options`、`handlers`、`references`、`footnotes`、`glossary`、`abbreviations`

## F-004: TexSerializer 核心方法

- `write(value: string)`: 追加字符串到 `file.result`
- `text(value: string, mathMode = false)`: 转义后写入文本（LaTeX数学模式/文本模式分别使用 `stringToLatexMath`/`stringToLatexText`）
- `trimEnd()`: 去除结果末尾空白
- `ensureNewLine(trim = false)`: 确保结果以换行结尾
- `renderChildren(node, inline?, delim?)`: 遍历子节点，查找 handler 调用，未处理的节点通过 `fileError` 报错
- `renderEnvironment(node, env, opts?)`: 生成 `\begin{env}...\end{env}` 环境
- `renderInlineEnvironment(node, env, opts?)`: 生成 `\env{...}` 内联命令
- `closeBlock(node)`: 调用 `ensureNewLine(true)` 并追加换行
- `usePackages(...packageNames)`: 向 `data.imports` Set 中添加包名

## F-005: myst-to-tex handlers 映射表

- 路径：`myst-to-tex/src/index.ts` L116-494
- 定义 `Record<string, Handler>` 类型的 `handlers` 对象
- 覆盖的节点类型：text, paragraph, heading, block, blockquote, definitionList, definitionTerm, definitionDescription, code, list, listItem, thematicBreak, mystRole, mystDirective, div, span, comment, strong, emphasis, underline, inlineCode, subscript, superscript, delete, break, abbreviation, link, admonition, admonitionTitle, table, image, container, proof, caption, crossReference, citeGroup, cite, embed, include, footnoteReference, footnoteDefinition, si, inlineExpression, raw, toc
- heading 映射到 LaTeX 层级命令：depth=-1→`\part`, 0→`\chapter`, 1→`\section`, 2→`\subsection`, 3→`\subsubsection`, 4-6→`\paragraph`/`\subparagraph`
- 支持 Beamer 模式：block 节点带 `outline` metadata 时输出 frame 内容，heading 作为 `\frametitle`
- code 节点支持三种样式：verbatim（默认）、listings（`\usepackage{listings}`）、minted（`\usepackage{minted}`）
- cite 支持 natbib 和 biblatex 两种参考文献风格
- glossary 引用使用 `\gls{}`，缩写使用 `\acrshort{}`（需要 printGlossaries 选项）

## F-006: LatexResult 结构

- 路径：`myst-to-tex/src/types.ts` L19-24
```typescript
type LatexResult = {
  value: string;       // LaTeX 正文内容
  imports: string[];   // 需要的 \usepackage 列表
  preamble: PreambleData; // 导言区数据（proof/index/glossary/abbreviations）
  commands: Record<string, string>; // 数学宏命令
};
```

## F-007: footnote/glossary/acronym 预构建

- `createFootnoteDefinitions(tree)`: 从 tree 中 `selectAll('footnoteDefinition')`，构建 `Record<string, FootnoteDefinition>` 映射
- `createGlossaryDefinitions(tree)`: 从 `glossary > definitionList > definitionTerm/definitionDescription` 对构建 `Record<string, [termText, descriptionText]>`
- `createAcronymDefinitions(tree)`: 从 `selectAll('abbreviation', tree)` 构建 `Record<string, [acronymText, expansion]>`，key 使用小写 trim 后的值
- 三者均在 `TexSerializer` 构造函数中从 AST 一次性提取

## F-008: withRecursiveCommands 数学命令解析

- 路径：`myst-to-tex/src/math.js`（通过 `import MATH_HANDLERS, { withRecursiveCommands } from './math.js'` 引入）
- `withRecursiveCommands(state)` 在 plugin Compiler 中调用，处理 state 中收集的 mathPlugins 生成递归命令

## F-009: ITexSerializer 接口与 Options

- 路径：`myst-to-tex/src/types.ts`
- `Options` 继承 `MystToTexSettings`，可包含 `handlers`、`math`、`bibliography`（'natbib' | 'biblatex'）、`printGlossaries`、`citestyle`、`references`
- `StateData` 包含：isInTable, isInContainer, longFigure, nextCaptionNumbered, nextHeadingIsFrameTitle, nextCaptionId, hasProofs, hasIndex, mathPlugins, imports
- `DEFAULT_IMAGE_WIDTH = 0.7`，`DEFAULT_PAGE_WIDTH_PIXELS = 800`

## F-010: LaTeX 导言区生成

- 路径：`myst-to-tex/src/preamble.ts`
- `generatePreamble(data: PreambleData)` 返回 `{ preamble: string; suffix: string }`
- `hasProofs` 时添加 `TexProofSerializer` 导言
- `hasIndex` 时添加 `\makeindex`
- `printGlossaries` 时创建 `TexGlossaryAndAcronymSerializer`，生成 `\usepackage[acronym]{glossaries}`/`\usepackage{glossaries}` + `\makeglossaries` + `\newglossaryentry`/`\newacronym` 定义，suffix 包含 `\printglossaries`
- `mergePreambles(current, next, warningLogFn)` 合并两个 PreambleData，重复 glossary/acronym key 时警告

## F-011: myst-to-docx 导出入口

- 包路径：`myst-to-docx/src/index.ts`
- 导出：`DocxSerializer`（来自 `./serializer.js`）、`defaultHandlers`（来自 `./schema.js`）、`plugin as mystToDocx`（来自 `./plugin.js`）、`writeDocx`/`createDocFromState`/`fetchImagesAsBuffers`（来自 `./utils.js`）
- 类型导出：`IDocxSerializer`、`DocxResult`、`Handler`、`Options`

## F-012: myst-to-docx plugin 实现

- 路径：`myst-to-docx/src/plugin.ts`
- `plugin: Plugin<[Options], Root, VFile>`，Compiler 中创建 `DocxSerializer(file, opts)`，调用 `state.renderChildren(node)`，再调用 `createDocFromState(state)` 生成 docx `Document`
- 使用 `docx` 库的 `Packer.toBuffer(doc)`（Node.js）或 `Packer.toBlob(doc)`（浏览器）序列化输出
- 返回的 `file.result` 为 Buffer 或 Blob

## F-013: myst-to-jats 默认导出插件

- 包路径：`myst-to-jats/src/index.ts`
- 默认导出 `Plugin<[SourceFileKind, FrontmatterWithParts?, CitationRenderer?, string?, DocumentOptions?], Root, VFile>`
- Compiler 调用 `writeJats(file, { mdast: node, kind, frontmatter, citations, slug }, opts)`

## F-014: JatsSerializer 类

- 路径：`myst-to-jats/src/index.ts` L764-908
- 实现 `IJatsSerializer` 接口
- 构造函数接收 `(file: VFile, mdast: Root, opts?: Options)`
- 初始化 stack 为 `[{ type: 'element', elements: [] }]`，footnotes/expressions/referenceOrder 为空数组
- 构造时调用 `basicTransformations(this.mdast, opts)` 做预处理
- 核心方法：`render(ignoreParts?)`、`openNode(name, attributes?, isLeaf?)`、`closeNode()`、`addLeaf(name, attributes?)`、`renderChildren(node)`、`renderInline(node, name, attributes?)`、`text(text?)`、`pushNode(el?)`

## F-015: JatsSerializer XML 栈模型

- `stack: Element[]` 维护 XML 元素嵌套栈
- `openNode(name, attributes, isLeaf)` 压入新 Element（isLeaf=true 时不创建 elements 数组）
- `closeNode()` 弹出栈顶元素并 pushNode 到新的栈顶
- `addLeaf(name, attributes)` = openNode(isLeaf=true) + closeNode()
- `text(text)` 合并连续 text 节点，XML 转义（`&`→`&amp;`、`<`→`&lt;`、零宽空格移除）
- `elements()` 返回 `this.stack[0].elements` 作为最终结果

## F-016: JatsDocument 类

- 路径：`myst-to-jats/src/index.ts` L910-1063
- 构造函数接收 `(file: VFile, content: ArticleContent, opts?: DocumentOptions)`
- `article(articleType?, specificUse?)` 方法构建完整 JATS `<article>` 元素：
  - 设置 XML 命名空间（mml, xlink, xsi, ali）、dtd-version=1.3、xml:lang=en
  - 创建 articleState（JatsSerializer），处理 Notebook 情况的 subArticle
  - 调用 `referenceTargetTransform`/`affiliationIdTransform`/`referenceResolutionTransform` 系列转换
  - 组装 front（`getFront`）、body、back（`getBack`，含 citations/footnotes/expressions/referenceOrder）、sub-article
- `writeJats(file, content, opts)` 创建 JatsDocument，`writeFullArticle=true` 时输出完整 XML（含 DOCTYPE），否则只输出 body
- 使用 `serializeJatsXml`（来自 jats-utils）序列化 Element 树为 XML 字符串

## F-017: myst-to-jats handlers 覆盖

- 路径：`myst-to-jats/src/index.ts` L295-714
- 覆盖节点类型：text, paragraph, section, heading, block, blockquote, definitionList, definitionItem, definitionTerm, definitionDescription, code, list, listItem, thematicBreak, inlineMath, math, mathGroup, mystRole, mystDirective, comment, strong, emphasis, underline, inlineCode, subscript, superscript, delete, smallcaps, span, break, abbreviation, link, admonition, admonitionTitle, attrib, table, tableHead, tableBody, tableFooter, tableRow, tableCell, image, container, caption, captionNumber, crossReference, citeGroup, cite, footnoteReference, footnoteDefinition, si, proof, algorithmLine, outputs, output, embed, supplementaryMaterial, inlineExpression
- math/inlineMath 使用 KaTeX 渲染为 MathML（通过 `renderEquation` + `xml2js`），同时保留 TeX 源码在 `<tex-math>` 中（CDATA），输出 `<alternatives>` 双格式
- crossReference 的 ref-type 映射：heading→sec, figure→fig, equation/subequation→dispFormula, table→table, proof→statement, 其他→custom
- container 根据 kind 映射：figure→`<fig>`, table→`<table-wrap>`, quote→renderChildren, code→`<boxed-text>`
- Notebook 输出通过 `<alternatives>` 包含多种 MIME 类型（image/*→graphic, text/html→media, text/plain→media）

## F-018: JATS 部分渲染

- `renderPart(vfile, mdast, part, opts?)` 使用 `extractPart`（来自 myst-common）提取 mdast 中的命名部分，创建独立 JatsSerializer 渲染
- `renderAbstract(vfile, mdast, def, opts?)` 渲染摘要到 `<abstract>` 元素
- `renderAcknowledgments(vfile, mdast, opts?)` 渲染致谢到 `<ack>` 元素
- `renderBackSection(vfile, mdast, def, opts?)` 渲染后置章节到 `<sec sec-type="...">` 元素
- ABSTRACT_PARTS/ACKNOWLEDGMENT_PARTS 定义在 types.js 中

## F-019: myst-to-md 导出入口

- 包路径：`myst-to-md/src/index.ts`
- 核心函数 `writeMd(file: VFile, node: Root, frontmatter?: PageFrontmatter)`
- 基于 `mdast-util-to-markdown` 的 `toMarkdown` 函数
- handlers 组合：`directiveHandlers`、`roleHandlers`、`referenceHandlers`、`miscHandlers`
- extensions 使用 `gfmFootnoteToMarkdown()` 和 `gfmTableToMarkdown()`（GFM 脚注和表格）
- 配置：`fences: true`（代码块用围栏）、`rule: '-'`（水平线用短横线）
- 最后通过 `addFrontmatter(result, frontmatter)` 添加 YAML frontmatter，通过 `runValidators` 验证指令

## F-020: myst-to-md 默认插件

- 默认导出 `Plugin<[PageFrontmatter?], Root, VFile>`，Compiler 直接调用 `writeMd(file, node, frontmatter)`
- 预处理阶段返回原始 node（无额外转换）
- `unsupportedHandlers(node, handlerKeys, file)` 为不支持的节点类型生成 fallback handler

## F-021: myst-to-typst 默认导出插件

- 包路径：`myst-to-typst/src/index.ts`
- 默认导出 `Plugin<[Options?], Root, VFile>`，Compiler 创建 `TypstSerializer` 实例
- 返回 `TypstResult`：`{ macros: string[], commands: Record<string, string>, value: string }`
- math 选项通过 `resolveRecursiveCommands(math)` 解析递归命令

## F-022: TypstSerializer 类

- 路径：`myst-to-typst/src/index.ts` L497-592
- 实现 `ITypstSerializer` 接口
- 构造函数接收 `(file: VFile, tree: Root, opts?: Options)`
- 初始化 `data: { mathPlugins: {}, macros: new Set(), headingIdentifiers: [] }`
- 预构建 `footnotes`（同 TexSerializer 模式），调用 `renderChildren(tree)`
- 核心方法：`useMacro(macro)`（添加到 macros Set）、`write`、`text`（使用 `stringToTypstText`/`stringToTypstMath`）、`renderChildren`（支持 trailingNewLines/delim/trimEnd/after 选项）、`renderEnvironment`（生成 `#env[\n...\n]`）、`renderInlineEnvironment`（生成 `#env[...]`）

## F-023: myst-to-typst handlers 特征

- 路径：`myst-to-typst/src/index.ts` L107-495
- heading 使用 Typst 原生 `=` 号语法（`=` 一级、`==` 二级等），标识符使用 `<label>` 语法
- 内联格式化：strong→`*text*`/`#strong[...]`、emphasis→`_text_`/`#emph[...]`（根据前后字符判断是否使用函数形式）
- 链接使用 `#link("url")[]` 或 `#link("url")[text]`
- 代码块使用围栏语法（自动增加反引号数量以避免冲突）
- 列表使用 `-`/`+` 语法，缩进表示嵌套，有序列表支持 `#set enum(start: N)` 设置起始编号
- admonition 使用自定义 Typst 函数（预定义 admonition 宏和各类型宏：attention/caution/danger/error/hint/important/note/seealso/tip/warning）
- tabSet/tabItem 也使用预定义 Typst 宏
- 引用使用 `@label` 或 `#link(<label>)[text]`，远程引用转为链接
- 引用文献使用 `#cite(<label>)`，narrative 引用使用 `form: "prose"`
- 图片使用 `#image("path", width: ...)`，TOC 使用 `#outline(depth: N, title: [...])`
- 注释：单行用 `//`，多行用 `/* */`
- 支持 raw typst 直接透传（`node.typst`）
- 支持 metadata tag 过滤：`no-typst`、`no-pdf` 跳过，`page-break`/`new-page`→`#pagebreak(weak: true)`

## F-024: myst-to-typst 宏定义

- admonition 宏定义（L30-59）：定义了 `admonition(body, heading, color)` 通用函数，以及 10 种类型变体（attention/caution/danger/error/hint/important/note/seealso/tip/warning）
- tabSet/tabItem 宏（L61-75）：定义 `tabSet(body)` 和 `tabItem(body, heading)` 函数
- 宏通过 `state.useMacro()` 收集，最终输出到结果中

## F-025: jtex renderTemplate 函数

- 路径：`jtex/src/jtex.ts` L46-104
- 函数签名：`renderTemplate(template: MystTemplate, opts: { contentOrPath, imports?, preamble?, packages?, force?, frontmatter, parts, options, bibliography?, outputPath, sourceFile?, filesPath?, removeVersionComment? })`
- 流程：
  1. 校验 outputPath 扩展名匹配模板 kind（tex→.tex, typst→.typ）
  2. 读取 content（从文件路径或直接字符串）
  3. 调用 `template.prepare(opts)` 获得 `{ options, parts, doc }`
  4. 调用 `renderImports()` 生成 IMPORTS 内容
  5. 构建 renderer 对象：`{ CONTENT, doc, parts, options, IMPORTS }`
  6. 创建 Nunjucks 环境（自定义标签：`[# #]` 块、`[- -]` 变量、`%# #%` 注释），添加 `len` filter
  7. 调用 `env.render(template.getTemplateFilename(), renderer)` 渲染
  8. `ensureDirectoryExists(outputDirectory)`，调用 `template.copyTemplateFiles()` 复制模板文件
  9. 写入输出文件，默认添加版本注释头

## F-026: jtex Nunjucks 环境配置

- 路径：`jtex/src/jtex.ts` L15-31
- `getDefaultEnv(template)` 配置 Nunjucks：
  - `trimBlocks: true`（trim 块标签后的换行）
  - `autoescape: false`（不 HTML 转义，因为输出是 LaTeX/Typst）
  - 自定义标签语法：blockStart=`[#`、blockEnd=`#]`、variableStart=`[-`、variableEnd=`-]`、commentStart=`%#`、commentEnd=`#%`
  - 添加 `len` filter：返回数组长度
- 自定义标签避免与 LaTeX `{ }` `{% %}` 冲突

## F-027: jtex 注释符号与版本头

- `commentSymbol(kind)`：typst→`//`，其他（tex）→`%`
- 输出文件默认添加 `% Created with jtex v.{version}\n`（LaTeX）或 `// Created with jtex v.{version}\n`（Typst）版本头，`removeVersionComment=true` 时跳过

## F-028: renderImports 分发函数

- 路径：`jtex/src/render.ts`
- `renderImports(kind, output, imports?, packages?, preamble?)` 根据 `kind` 分发：
  - `TemplateKind.tex` → `renderTexImports(imports as TexTemplateImports, packages, preamble)`
  - `TemplateKind.typst` → `renderTypstImports(output, imports as TypstTemplateImports, preamble)`

## F-029: jtex LaTeX imports 渲染

- 路径：`jtex/src/tex/imports.ts`
- `createTexImportCommands(commands, existingPackages?)`: 排序后过滤已有包，生成 `\usepackage{name}` 列表
- `createTexMathCommands(plugins)`: 将 `Record<string, string>` 转为 `\newcommand{\name}[nArgs]{definition}` 列表，自动检测参数个数
- `renderTexImports(templateImports?, existingPackages?, preamble?)`: 组装带注释分隔线的完整 imports 块（标记 `% imports` 和 `% math commands` 区域）
- `mergeTexTemplateImports(current?, next?)`: 合并两个 TexTemplateImports（commands 合并，imports 去重并集）

## F-030: jtex LaTeX PDF 导出命令

- 路径：`jtex/src/tex/export.ts`
- `pdfTexExportCommand(texFile, logFile, template?)`: 生成 latexmk 命令，engine 默认为 `-xelatex`（可从 template.yml 的 build.engine 配置），完整命令：`latexmk -f {engine} -synctex=1 -interaction=batchmode -file-line-error -latexoption="-shell-escape" {texFile}`
- `texMakeGlossariesCommand(texFile, logFile)`: 生成 `makeglossaries {fileNameNoExt}` 命令

## F-031: jtex Typst imports 渲染

- 路径：`jtex/src/typst/imports.ts`
- `renderTypstImports(output, templateImports?, preamble?)`:
  - 有 macros 时添加 `#import "myst-imports.typ": *`，并将 macros 写入同目录 `myst-imports.typ` 文件
  - math commands 转为 `#let \name = $definition$` 格式
  - preamble 追加在末尾
- `mergeTypstTemplateImports(current?, next?)`: 合并两个 TypstTemplateImports（commands 合并，macros 去重并集）

## F-032: jats-to-myst 导入转换器

- 包路径：`jats-to-myst/src/index.ts`
- 导出 `JatsParser` 类、`jatsToMystPlugin`、`jatsToMystTransform` 函数、`DEFAULT_HANDLERS`
- `jatsToMystTransform(data, opts?)` 是高层入口，接收 JATS XML 字符串或 `Jats` 对象，返回 `{ tree, jats, file, references }`

## F-033: JatsParser 类

- 路径：`jats-to-myst/src/index.ts` L351-453
- 栈模型与 JatsSerializer 对称：`stack: GenericNode[]` 初始为 `[{ type: 'root', children: [] }]`
- 构造时接收 `(file: VFile, jats: Jats, opts?: Options)`
- 核心方法同 JatsSerializer：`openNode/closeNode/pushNode/text/renderChildren/renderInline/addLeaf/warn/error`
- `unhandled: string[]` 记录未处理的节点类型

## F-034: jats-to-myst handlers 与 JATS 元素映射

- 路径：`jats-to-myst/src/index.ts` L33-347
- JATS 元素→MyST 节点映射：
  - body→renderChildren, p→paragraph, heading→heading, block→block, disp-quote→blockquote
  - list→list（list-type=ordered 映射 ordered:true）, list-item→listItem
  - bold→strong, italic→emphasis, underline→underline, monospace→inlineCode
  - sub→subscript, sup→superscript, strike→delete, sc→smallcaps
  - ext-link→link（xlink:href→url）, boxed-text→admonition(kind=info)
  - xref→cite（ref-type=bibr）/crossReference（ref-type=sec/fig/dispFormula/table/custom）
  - fig-group→tabSet（每个 fig 转为 tabItem）
  - fig→container+image+caption（支持 eLife/JOSS/PLOS/PMC 图片URL特殊处理）
- plugin Compiler 处理 abstract 前置、floats-group 后置、basicTransformations、referenceData 提取、referenceOrder 追踪、keysTransform

## F-035: tex-to-myst 入口

- 包路径：`tex-to-myst/src/index.ts`
- 导出类型和 `TexParser` 类、`DEFAULT_HANDLERS`
- 包路径存在但核心逻辑在 `./parser.js`

## F-036: mystToHtml 统一入口函数

- 路径：`myst-to-html/src/renderMdast.ts` L10-34
- 函数签名：`mystToHtml(tree, opts?)`，opts 包含 `formatHtml?`、`hast?`、`stringifyHtml?`
- unified 管道：`transform(state)` → `mystToHast(opts?.hast)` → `formatHtml(opts?.formatHtml)` → `rehypeStringify(opts?.stringifyHtml)`
- 创建 State 实例用于编号和引用解析
- 返回 trim 后的 HTML 字符串

## F-037: myst-to-html State 类

- 路径：`myst-to-html/src/state.ts` L86-192
- 管理编号目标和引用解析
- `targets: Record<string, Target>` 存储可引用目标（heading/math/figure/table/code）
- `targetCounts: TargetCounts` 存储各类计数器（heading 是6级数组，其他是数字）
- `addTarget(node)`: 为 enumerated!==false 的节点分配编号，记录到 targets
- `incrementCount(node, kind)`: heading 使用层级编号（如 1.2.3），其他使用简单递增
- `resolveReferenceContent(node)`: 根据 ref 类型（eq/ref/numref）和 target 类型（math/heading/figure/table）填充引用文本
- `enumerateTargets(state, tree, opts)`: 遍历 tree 为 container/math/heading 添加编号
- `resolveReferences(state, tree)`: 将 URL 链接转为 crossReference，解析引用内容

## F-038: myst-cli build 格式分发

- 路径：`myst-cli/src/build/build.ts`
- `getAllowedExportFormats(opts)`: 根据 CLI flag（--docx/--pdf/--tex/--typst/--xml/--md/--meca/--cff/--all）确定导出格式列表
- pdf 格式同时导出 ExportFormats.pdf、pdftex、typst；tex 格式同时导出 tex、pdftex
- `collectAllBuildExportOptions(session, files, opts)`: 收集所有导出配置，支持单文件指定output、多文件批量、项目级导出
- `build(session, files, opts)`: 主构建函数，先执行 localArticleExport 导出各种格式，再执行 site 构建（buildSite 或 buildHtml）

## F-039: localArticleExport 格式调度

- 路径：`myst-cli/src/build/utils/localArticleExport.ts`
- `_localArticleExport(session, exportOptionsList, opts)`: 根据 format 分发到具体导出函数：
  - tex: `runTexExport` 或 `runTexZipExport`（.zip）
  - typst: `runTypstExport`、`runTypstZipExport`（.zip）或 `runTypstPdfExport`（.pdf）
  - docx: `runWordExport`
  - xml: `runJatsExport`
  - md: `runMdExport`
  - meca: `runMecaExport`
  - cff: `runCffExport`
  - pdf/pdftex: 先 `texExportOptionsFromPdf` → `runTexExport` → `createPdfGivenTexExport`（latexmk 编译）
- 支持 watch 模式（chokidar 监听文件变化自动重新导出）
- MECA 导出在最后执行（因为 MECA 包含其他格式的产物）

## F-040: 导出器 unified 插件统一模式

- 所有导出器（html/tex/docx/jats/md/typst）均实现为 unified Plugin
- 统一模式：`this.Compiler = (node, file) => { ... return file; }` + `return (node: Root) => node;`（预处理透传）
- Compiler 内创建 Serializer 实例，调用 `renderChildren(tree)` 遍历 AST
- 每个 Serializer 维护 handlers 映射表（节点类型→渲染函数）和状态对象
- 输出写入 `file.result`，类型各格式不同：
  - HTML: string
  - TeX: LatexResult（value+imports+preamble+commands）
  - Typst: TypstResult（value+macros+commands）
  - DOCX: Buffer/Blob
  - JATS: string（XML）
  - MD: string（带 frontmatter）
