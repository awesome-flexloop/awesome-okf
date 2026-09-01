---
type: bundle
title: "myst-syntax 语法扩展"
okf_version: "0.2"
---

# myst-syntax 语法扩展知识库

本知识包是 [MyST Markdown](https://mystmd.org) 语法扩展（myst-directives 和 myst-roles）的系统化中文文档，基于 mystmd 源码（`mystmd/packages/myst-directives/` 和 `mystmd/packages/myst-roles/` 目录）深度阅读生成，覆盖从指令/角色基础、提示框、代码块、图表、表格、数学公式到交叉引用、文件包含、Mermaid图表、SI单位等完整语法扩展体系。所有内容均溯源至源码，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 核心概念（concepts/）

* [指令与角色基础](concepts/00-directive-role-basics.md) — DirectiveSpec/RoleSpec 声明式接口、arg/options/body 输入模式、String/'myst' 类型系统、通用选项（class/label/enumerated）、别名系统、指令vs角色对比、run() 方法约定、注册机制。
* [提示框与标注](concepts/01-admonition-callouts.md) — admonition 11种语义类型（note/tip/warning/danger/error等）、自定义标题、icon隐藏、open可折叠、dropdown折叠面板、aside/margin/sidebar/topic边栏、blockquote块引用。
* [代码块](concepts/02-code-blocks.md) — code/code-block/sourcecode指令、code-cell可执行单元格、linenos/lineno-start/number-lines行号控制、emphasize-lines高亮行（范围语法"3,5,7-9"）、filename文件名标签、caption带标题编号、tags单元格标签（remove-input/hide-cell等）。
* [图片与图表](concepts/03-figures-images.md) — image独立图片、figure带标题编号的图表容器、width/height/alt/align选项、notebook单元格嵌入（#cell-id）、placeholder静态导出占位图、no-subfigures子图控制、iframe网页嵌入。
* [表格](concepts/04-tables.md) — table包裹Markdown表格、list-table嵌套列表表格（复杂单元格内容）、csv-table CSV数据表格（MyST单元格解析、delim/quote/escape选项、header/header-rows）、三种表格对比。
* [数学公式](concepts/05-math.md) — math指令（块级$$）和math角色（行内$）、LaTeX数学语法、label标签+eq引用、typst备用内容、aligned多行对齐、tight排版。
* [交叉引用与引用](concepts/06-cross-references-citations.md) — ref/eq/numref交叉引用（自定义显示文本语法）、cite/cite:p/cite:t等18种引用风格（parenthetical/narrative/year/author/alpha）、前缀后缀语法、bibliography参考文献列表、term术语引用、doc文档引用、download下载链接、abbr缩写、glossary术语表。
* [包含与嵌入](concepts/07-include-embed.md) — include/literalinclude文件包含、literal/lang代码块模式、行过滤（start-line/end-line/start-at/end-at/start-after/end-before/lines精确选择）、lineno-match源文件行号、extToLanguage自动语言推断、embed内容嵌入复用、div通用容器。
* [高级指令与角色](concepts/08-advanced-directives.md) — mermaid图表（flowchart/sequenceDiagram/classDiagram等）、toc目录（project/children/page/section四种context）、raw/raw:latex/raw:typst格式定向内容、index/show-index索引系统、chem化学式、si SI单位（完整单位映射表）、kbd键盘按键、sub/sup/u/del/smallcaps文本格式化。

## 实战示例（examples/）

* [常用指令实战](examples/01-common-directives.md) — admonition全类型示例、code-block行号/高亮/标题/标签、figure图片图表、三种表格（Markdown/CSV/list-table）、math公式、dropdown折叠、iframe嵌入。
* [引用与交叉引用实战](examples/02-citations-references.md) — ref交叉引用（figure/table/equation/code）、cite文献引用（narrative/parenthetical/year/author/multi-cite/prefix-suffix）、abbr缩写、glossary术语表、bibliography参考文献、sidebar边栏、toc目录、学术论文片段综合示例。
* [高级语法实战](examples/03-advanced-syntax.md) — Mermaid全图表类型（流程图/时序图/类图/状态图/甘特图/ER图）、include文件包含（行范围/文本标记/lines精确选择）、embed内容嵌入、raw LaTeX/Typst内容、si单位、chem化学式、kbd键盘按键、文本格式化角色、索引标记与生成。

## 信源登记簿（references/）

* [DirectiveSpec 接口与指令注册](references/directive-spec.md) — `myst-directives/src/index.ts` defaultDirectives（28个指令）、`utils.ts` commonDirectiveOptions/class/label/enumeration、addCommonDirectiveOptions、DirectiveSpec/DirectiveData类型。
* [角色系统：RoleSpec 接口与默认角色](references/role-spec.md) — `myst-roles/src/index.ts` defaultRoles（20个角色）、`utils.ts` commonRoleOptions（class/label）、cite角色详解（18个别名/kind判定/前缀后缀/CiteGroup分组）、ref角色详解（REF_PATTERN自定义文本）、RoleSpec/RoleData类型。
* [核心指令源码](references/core-directives.md) — `admonition.ts`（11别名/open→dropdown/icon）、`code.ts`（CODE_DIRECTIVE_OPTIONS/parseEmphasizeLines/parseTags/codeCell输出结构）、`figure.ts`（container/image/placeholder/subfigures/kind）、`table.ts`（table/list-table/csv-table/parseCSV）、`math.ts`（typst选项/tight）。
* [扩展指令源码](references/extended-directives.md) — `include.ts`（literal模式/行过滤互斥/parseLinesString/extToLanguage）、`embed.ts`（#前缀/source.label）、`mermaid.ts`、`toc.ts`（4种context/contents别名）、`raw.ts`（rawLatex/rawTypst快捷指令）、`image.ts`（alt自动提取/默认center）、`iframe.ts`（placeholder/container包裹）、`aside.ts`（margin/sidebar/topic别名）、`dropdown.ts`（details/summary）、`div/bibliography/glossary/index/genindex/blockquote`。

## 事实与洞察

* [事实提取](facts.md) — 68个编号源码事实（F-S001 ~ F-S068），覆盖 DirectiveSpec/RoleSpec 接口、28个默认指令、20个默认角色、通用选项、各指令/角色的参数/选项/输出结构。
* [关键洞察](insights.md) — 从源码阅读中提炼的架构洞察，包括声明式DirectiveSpec设计、通用选项混入模式、别名系统多源兼容、Admonition多态设计、Container包装模式、代码块出版级控制、Include行片段选择、Cite BibTeX风格映射、CSV内联解析、TOC多上下文、Raw格式定向输出、SI单位LaTeX命令映射。

## 学习路径建议

1. **快速上手**：00-directive-role-basics → 01-admonition-callouts → 运行 examples/01-common-directives.md
2. **技术文档核心**：02-code-blocks → 03-figures-images → 04-tables → 05-math → examples/01继续
3. **学术写作**：06-cross-references-citations → examples/02-citations-references.md
4. **高级功能**：07-include-embed → 08-advanced-directives → examples/03-advanced-syntax.md
5. **源码溯源**：阅读 references/ 中的信源文档，理解各指令/角色的底层实现

## 信任与生命周期说明

* **status 判定依据**：全部 23 个内容文档（9 个概念 + 3 个示例 + 4 个信源登记）+ facts.md + insights.md + 根 index.md，非 index/log 文件均 `status: stable`。内容基于对 mystmd 源码（`external/libs/ai/jupyter-book/mystmd/packages/` 目录）myst-directives（26个源文件）和 myst-roles（20个源文件）的逐文件阅读与事实提取（68个编号源码事实 F-S001 ~ F-S068）。
* **stale_after 解释**：统一设置为 `2027-12-31`。MyST 语法扩展核心（DirectiveSpec/RoleSpec 接口、admonition/code/figure/table/math等核心指令、cite/ref等核心角色）在 mystmd 1.x 中保持稳定，该日期作为对未来大版本变化的保守重新评估节点。
* **核验链路**：`generated` 记录原始生成时刻（2026-08-23）；`verified: true` 记录过程核验，所有指令名、选项名、别名、输出节点类型均通过源码 Read/Grep 验证。
* **覆盖范围**：覆盖 myst-directives 的全部 28 个默认指令（admonition/code/code-cell/figure/image/table/list-table/csv-table/math/mermaid/include/embed/bibliography/glossary/toc/index/genindex/div/aside/dropdown/iframe/raw/rawLatex/rawTypst/blockquote/mdast/mystdemo/widget）和 myst-roles 的全部 20 个默认角色（span/abbr/chem/cite/delete/math/ref/doc/download/index/term/si/eval/smallcaps/subscript/superscript/underline/keyboard/rawLatex/rawTypst）；未覆盖 mdastDirective/mystdemoDirective/widgetDirective(anywidget) 的详细内部实现（属于特定用途/实验性功能）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
facts
insights
log
```
