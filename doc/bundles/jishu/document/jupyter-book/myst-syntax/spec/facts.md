---
type: facts
title: "myst-syntax 事实清单"
description: "myst-directives和myst-roles包的源码事实清单，包括DirectiveSpec/RoleSpec接口、默认指令和角色列表"
tags: [myst-syntax, facts, directives, roles, myst-directives, myst-roles]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/index.ts"
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/utils.ts"
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/index.ts"
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/utils.ts"
---

# myst-syntax 事实清单

本文档记录从 myst-directives 和 myst-roles 源码中提取的编号事实。

## 指令系统（myst-directives）

### DirectiveSpec 接口

- **F-S001**: DirectiveSpec 定义了指令的元数据和运行逻辑，包括 name、doc、alias、arg、options、body、run()、validate() 等字段。
- **F-S002**: `name` 字段是指令的主名称，`alias` 数组定义别名。
- **F-S003**: `arg` 定义指令参数（冒号行后的内容），type 可以是 String 或 'myst'（解析为 MDAST 节点）。
- **F-S004**: `body` 定义指令体内容，type 可以是 String（原始文本）或 'myst'（解析为 MyST 内容）。required 字段标识是否必须。
- **F-S005**: `options` 是键值对映射，每个选项有 type（String/Boolean/Number）、doc、alias 等属性。
- **F-S006**: `run(data, vfile, ctx)` 方法是指令的核心逻辑，接收 DirectiveData，返回 GenericNode[]。
- **F-S007**: `validate(data, vfile)` 方法是可选的验证钩子，在 run 之前执行，可以修改 data 或输出错误。
- **F-S008**: DirectiveData 包含 node（解析后的指令节点）、name、arg、options、body 等字段。

### 通用选项（commonDirectiveOptions）

- **F-S009**: `commonDirectiveOptions(nodeType)` 返回三个通用选项：class（CSS类名）、label/name（交叉引用标签）、enumerated/numbered（编号开关）和 enumerator/number（显式编号）。
- **F-S010**: `addCommonDirectiveOptions(data, node)` 将 class、label、enumerated/enumerator 选项应用到生成的节点上。
- **F-S011**: label 选项支持 alias: ['name']，normalizeLabel() 用于规范化标签和标识符。

### 默认指令列表（defaultDirectives）

- **F-S012**: defaultDirectives 数组包含 28 个指令：admonitionDirective、bibliographyDirective、csvTableDirective、codeDirective、codeCellDirective、dropdownDirective、embedDirective、blockquoteDirective、figureDirective、iframeDirective、imageDirective、includeDirective、indexDirective、genIndexDirective、tableDirective、listTableDirective、asideDirective、glossaryDirective、mathDirective、mdastDirective、mermaidDirective、mystdemoDirective、rawDirective、rawLatexDirective、rawTypstDirective、divDirective、tocDirective、widgetDirective。

### 各指令详情

- **F-S013**: admonitionDirective 主名 'admonition'，别名 10 个：attention/caution/danger/error/important/hint/note/seealso/tip/warning。arg 类型为 'myst'（可选标题），支持 class/icon/open 选项。open:true 自动添加 dropdown 类名。body 开头的粗体或标题可作为 admonition 标题。
- **F-S014**: codeDirective 主名 'code'，别名 ['code-block', 'sourcecode']。arg 为语言类型（String），body 为原始代码（String）。支持 caption/linenos/lineno-start/number-lines/emphasize-lines/filename 选项。有 caption 时包裹在 container(kind:'code') 中。
- **F-S015**: codeCellDirective 主名 'code-cell'，生成可执行代码块。生成 block(kind:'code') 包含 code 节点和空 outputs 节点。支持 tags 选项（逗号分隔的标签列表，也支持 YAML 数组格式），tags 通过 parseTags() 解析。
- **F-S016**: CODE_DIRECTIVE_OPTIONS 定义了代码块共享选项：caption(myst)、linenos(Boolean)、lineno-start(Number)、number-lines(Number)、emphasize-lines(String，支持范围如"3,5,7-9")、filename(String)。
- **F-S017**: getCodeBlockOptions() 解析代码块选项，处理 emphasizeLines 行号范围解析、showLineNumbers 开关、startingLineNumber 起始行号（'lineno-match' 特殊值为 'match'）、filename 默认值。
- **F-S018**: figureDirective 主名 'figure'，arg 为图片路径或 Notebook 单元格 ID（#cell-id）。生成 container(kind:'figure' 或自定义 kind)，包含 image 节点和 body 中的 caption。支持 width/height/alt/align/remove-input/remove-output/placeholder/no-subfigures/kind 选项。width 别名 ['w','figwidth']，height 别名 ['h']，class 别名 ['figclass']。
- **F-S019**: imageDirective 主名 'image'，arg 为图片路径（必填）。生成 image 节点，支持 width(w)/height(h)/alt/align/title 选项。align 默认为 'center'。alt 可从 body 文本提取。
- **F-S020**: tableDirective 主名 'table'，arg 为可选标题（myst），body 为 myst 内容（通常是 Markdown 表格）。生成 container(kind:'table') 包含 caption 和表格。
- **F-S021**: listTableDirective 主名 'list-table'，body 必须是嵌套列表（list of lists）。validate() 验证 body 结构，header-rows 选项指定表头行数。从列表结构生成 table → tableRow → tableCell 节点。
- **F-S022**: csvTableDirective 主名 'csv-table'，使用 csv-parse 库解析 CSV 数据。支持 header/header-rows/delim/keepspace/quote/escape 选项。每个单元格通过 ctx.parseMyst() 解析为 MyST 内容。
- **F-S023**: mathDirective 主名 'math'，body 为 LaTeX 数学表达式（String，必填）。生成 math 块级节点，支持 typst 选项提供 Typst 专用数学内容。tight 字段来自解析器。
- **F-S024**: mermaidDirective 主名 'mermaid'，body 为 Mermaid 图表定义（String，必填），生成 mermaid 节点。
- **F-S025**: includeDirective 主名 'include'，别名 ['literalinclude']。arg 为文件路径（必填）。支持 literal/lang/language/code 选项切换到代码块模式。支持行范围过滤：start-line/end-line/start-at/end-at/start-after/end-before/lines。lines 格式如 "1,3,5-10,20-"。literalinclude 自动设 literal:true。filename 默认显示为被包含文件名。
- **F-S026**: embedDirective 主名 'embed'，arg 为目标标签（支持 # 前缀），生成 embed 节点，source.label 指向目标。支持 remove-input/remove-output 选项（用于 Notebook 单元格）。
- **F-S027**: bibliographyDirective 主名 'bibliography'，生成 bibliography 节点，支持 filter 选项过滤引用条目。
- **F-S028**: glossaryDirective 主名 'glossary'，body 为 myst 内容（必填），生成 glossary 节点。
- **F-S029**: tocDirective 主名 'toc'，别名 ['tableofcontents','table-of-contents','toctree','contents']。context 选项支持 project/children/page/section 四种范围（默认 project，contents 别名默认为 section），depth/maxdepth 控制层级深度。arg 为可选标题。
- **F-S030**: indexDirective 主名 'index'，支持 single/pair/triple/see/seealso 索引条目类型，可通过 arg、options 或 body 定义条目。生成 mystTarget 节点含 indexEntries。选项语法（:single:）会产生警告提示改用新语法。
- **F-S031**: genIndexDirective 主名 'show-index'，别名 ['genindex']，生成 genindex 节点用于显示生成的索引。
- **F-S032**: divDirective 主名 'div'，body 为 myst 内容，生成 div 节点，可添加 class/label 等通用选项。
- **F-S033**: asideDirective 主名 'aside'，别名 ['margin','sidebar','topic']。arg 为可选标题（作为 admonitionTitle），body 为 myst 内容。生成 aside 节点，kind 由指令名决定（sidebar/topic）。
- **F-S034**: dropdownDirective 主名 'dropdown'，arg 为标题（myst），生成 details HTML 元素节点，支持 open 选项控制初始展开状态。arg 内容放入 summary 子节点。
- **F-S035**: iframeDirective 主名 'iframe'，arg 为 URL（必填）。支持 width/align/title/placeholder 选项。有 body 时包裹在 container(kind:'figure') 中作为带标题的 iframe。placeholder 生成占位图片节点用于静态导出。
- **F-S036**: rawDirective 主名 'raw'，arg 为格式（latex/tex/typst/typ），body 为原始内容。生成 raw 节点，根据 lang 设置 tex 或 typst 字段。rawLatexDirective(name:'raw:latex', alias:'raw:tex') 和 rawTypstDirective(name:'raw:typst', alias:'raw:typ') 是格式特定的快捷指令。
- **F-S037**: blockquoteDirective 生成块引用节点。
- **F-S038**: mdastDirective 允许直接嵌入 MDAST 节点（通过 YAML/JSON 定义）。
- **F-S039**: mystdemoDirective 用于 MyST 演示/文档中的指令演示。
- **F-S040**: widgetDirective (anywidget) 支持 Jupyter 交互式小部件。

## 角色系统（myst-roles）

### RoleSpec 接口

- **F-S041**: RoleSpec 定义了角色的元数据和运行逻辑，包括 name、alias、options、body、run() 等字段，结构与 DirectiveSpec 类似但更简化。
- **F-S042**: RoleData 包含 node、name、options、body 等字段。
- **F-S043**: `commonRoleOptions(nodeType)` 返回 class 和 label/name 两个通用选项（角色不支持 enumerated/enumerator）。
- **F-S044**: `addCommonRoleOptions(data, node)` 将 class 和 label 选项应用到生成的节点。

### 默认角色列表（defaultRoles）

- **F-S045**: defaultRoles 数组包含 20 个角色：spanRole、abbreviationRole、chemRole、citeRole、deleteRole、mathRole、refRole、docRole、downloadRole、indexRole、termRole、siRole、evalRole、smallcapsRole、subscriptRole、superscriptRole、underlineRole、keyboardRole、rawLatexRole、rawTypstRole。

### 各角色详情

- **F-S046**: abbreviationRole 主名 'abbreviation'，别名 ['abbr']。body 格式 "缩写(全称)"（如 "CSS(Cascading Style Sheets)"），使用正则 `/^(.+?)\(([^()]+)\)$/` 匹配。生成 abbreviation 节点，title 属性为全称。
- **F-S047**: citeRole 主名 'cite'，别名 18 个：cite:p/cite:t/cite:ps/cite:ts/cite:ct/cite:cts/cite:alp/cite:alps/cite:label/cite:labelpar/cite:year/cite:yearpar/cite:author/cite:authors/cite:authorpar/cite:authorpars/cite:cauthor/cite:cauthors。body 为逗号/分号分隔的引用键。支持前缀后缀语法 {prefix}key{suffix}。kind 根据别名确定：parenthetical（含:p/par/alp）或 narrative。cite:year 设置 partial:'year'，cite:author* 设置 partial:'author'。单引用直接返回 Cite 节点，多引用包裹在 CiteGroup 中。
- **F-S048**: CiteKind 类型为 'parenthetical' | 'narrative'。parenthetical 为括号引用（如 [Author 2020]），narrative 为叙述引用（如 Author (2020)）。
- **F-S049**: refRole 主名 'ref'，别名 ['eq','numref','prf:ref','proof:ref']。body 支持 "显示文本<标签>" 格式（正则 `/^(.+?)<([^<>]+)>$/`）。生成 crossReference 节点，kind 为角色名。
- **F-S050**: mathRole 主名 'math'，body 为 LaTeX 行内数学表达式（必填），生成 inlineMath 节点，支持 typst 选项。
- **F-S051**: chemRole 主名 'chemicalFormula'，别名 ['chem']，body 为化学式字符串，生成 chemicalFormula 节点。
- **F-S052**: siRole 主名 'si'，body 格式 "数值<\\单位命令>"（如 "10<\\kilo\\gram>"），使用正则 /([0-9.,eE-]+)\s?<([\\a-zA-Z\s]+)>/ 匹配。解析 \\command 形式的单位，通过 UNITS 映射表转换为符号（如 \\kilo→k, \\gram→g）。包含完整的 SI 基本单位、导出单位、词头映射表（yocto~yotta, Å 等特殊单位）。
- **F-S053**: spanRole 生成行内容器 span 节点，支持 class/label 选项。
- **F-S054**: deleteRole 生成删除线节点（strikethrough/delete）。
- **F-S055**: subscriptRole 生成下标节点，superscriptRole 生成上标节点。
- **F-S056**: underlineRole 生成下划线节点。
- **F-S057**: smallcapsRole 生成小型大写字母节点。
- **F-S058**: keyboardRole 生成键盘按键节点（kbd）。
- **F-S059**: docRole 用于跨文档引用，downloadRole 生成下载链接。
- **F-S060**: termRole 用于术语引用（链接到 glossary 中的术语定义）。
- **F-S061**: indexRole 用于行内索引条目。
- **F-S062**: evalRole (inlineExpression) 支持行内表达式计算。
- **F-S063**: rawLatexRole (raw:latex/raw:tex) 生成行内原始 LaTeX 内容，rawTypstRole (raw:typst/raw:typ) 生成行内原始 Typst 内容。

## 指令与角色的注册机制

- **F-S064**: 指令和角色通过数组导出（defaultDirectives/defaultRoles），在 myst-cli 处理管线中通过 myst-common 的解析器注册。
- **F-S065**: 插件可以通过 transforms 扩展自定义指令和角色。
- **F-S066**: 指令体类型为 'myst' 时，body 内容被递归解析为 MDAST 树；type 为 String 时保持原始文本。
- **F-S067**: 选项的 alias 字段定义选项名的替代名称（如 figure 的 width 别名 w/figwidth）。
- **F-S068**: 指令的 alias 字段定义指令名的替代名称（如 code 的别名 code-block/sourcecode）。
