---
type: reference
title: "myst-exporters 架构洞察"
description: "myst-exporters 多格式导出器架构洞察与知识地图，3-5个核心洞察四元组"
tags: [myst-exporters, insights, spec, architecture]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-tex/src/index.ts"
    facts: [F-002, F-003, F-004, F-005]
  - path: "myst-to-jats/src/index.ts"
    facts: [F-014, F-015, F-016]
  - path: "myst-to-typst/src/index.ts"
    facts: [F-021, F-022, F-023]
  - path: "jtex/src/jtex.ts"
    facts: [F-025, F-026]
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039, F-040]
---

# myst-exporters 架构洞察

## 洞察 I-001：统一 Serializer + Handler 表驱动架构

**陈述**：所有6种导出器（HTML/TeX/DOCX/JATS/MD/Typst）采用统一的架构模式——unified Plugin 封装 + Serializer 状态类 + 按节点类型分发的 Handler 映射表。

**证据**：
- F-002/F-003/F-004: TexSerializer 类持有 handlers: Record<string, Handler>，renderChildren 按 child.type 查表分发
- F-014/F-015: JatsSerializer 同样模式，栈式 XML 构建
- F-021/F-022: TypstSerializer 同样模式，宏收集机制
- F-040: 所有导出器统一实现为 unified Plugin，Compiler 创建 Serializer 并调用 renderChildren

**反常识**：HTML 导出走了不同的路径——它不直接实现自己的 Serializer，而是基于 mdast→hast→rehype→stringify 的标准 unified 生态管道（mystToHast + rehypeStringify），不是手写 Serializer。这是因为 HTML 有成熟的 hast 生态可以复用。

**行动**：
- 添加新导出格式时，遵循 Serializer + Handler 表模式
- 若目标格式有成熟的 AST 生态（如 HTML 的 hast），优先复用生态插件而非手写
- Handler 表通过 opts.handlers 可覆盖扩展，这是插件化扩展点

## 洞察 I-002：LaTeX/Typst 双引擎共享 jtex 模板层

**陈述**：LaTeX 和 Typst 导出虽然是独立的 Serializer，但它们共享 jtex 包的模板渲染管线——jtex 是一个模板引擎，用 Nunjucks 将 Serializer 输出的内容片段（CONTENT/IMPORTS/doc/parts/options）注入到 LaTeX 或 Typst 模板中。

**证据**：
- F-025: renderTemplate 函数接收 MystTemplate，调用 template.prepare() 获取 doc/parts/options，构建 renderer 对象，使用 Nunjucks 渲染模板文件
- F-026: Nunjucks 环境配置了自定义标签语法（[# #]/[- -]/%# #%），避免与 LaTeX 花括号冲突
- F-028/F-029/F-031: renderImports 根据 kind 分发到 renderTexImports 或 renderTypstImports，分别处理 usepackage/newcommand 和 #import/#let
- F-030: PDF 导出通过 latexmk 命令编译 .tex 文件

**反常识**：jtex 不是直接将 MDAST 转为 LaTeX/Typst 的转换器，而是一个模板填充引擎——MDAST→TeX/Typst 的转换在 myst-to-tex/myst-to-typst 中完成（生成 CONTENT 和 IMPORTS），jtex 负责将这些片段放入模板文件（如 `template.tex`）中。模板文件定义了文档结构（documentclass/preamble/layout），jtex 使用 Nunjucks 语法插值。

**行动**：
- 自定义 LaTeX/Typst 输出外观应通过创建自定义模板（template.tex/template.yml）而非修改 Serializer
- 理解 [CONTENT]、[-IMPORTS-]、[-doc.title-] 等模板变量是定制模板的关键
- PDF 生成是 .tex→latexmk 的两步过程，不是直接从 MDAST 到 PDF

## 洞察 I-003：JATS 导出是唯一结构化双工转换器

**陈述**：在所有导出器中，JATS 是唯一同时具备导出（myst-to-jats）和导入（jats-to-myst）双向能力的格式。JatsSerializer 和 JatsParser 形成对称的栈式构建/解析架构。

**证据**：
- F-013-F-018: JatsSerializer 使用栈模型构建 XML Element 树（openNode/closeNode/pushNode），输出带 MathML/TeX 双格式数学公式的 JATS XML
- F-032-F-034: JatsParser 使用对称的栈模型将 JATS XML 元素还原为 MyST MDAST 节点
- F-017: JATS 导出时数学公式同时生成 MathML（KaTeX 渲染）和 TeX 源码（CDATA），确保下游兼容性
- F-016: JatsDocument 处理完整的 article 结构（front/body/back/sub-article），支持 Notebook 子文章表示
- F-034: JATS 导入时对 eLife/JOSS/PLOS/PMC 等出版商有专门的图片 URL 解析逻辑

**反常识**：tex-to-myst 虽然存在但成熟度远不如 jats-to-myst——从源码看 jats-to-myst 有完整的 handler 表和 referenceData 提取，而 tex-to-myst 仅导出了 TexParser 和 DEFAULT_HANDLERS，解析 LaTeX 的复杂度远高于 JATS XML。

**行动**：
- 需要从学术出版商导入内容时使用 jats-to-myst
- JATS 导出面向学术存档（PubMed Central等），注重结构完整性而非视觉呈现
- LaTeX 导入功能有限，复杂 LaTeX 文档可能需要手动调整

## 洞察 I-004：格式导出在 myst-cli 层编排，不在 exporter 包中

**陈述**：myst-to-* 包只负责单文件 MDAST→目标格式的转换，多文件项目构建、PDF 编译（latexmk）、模板下载、文件输出、watch 模式等编排逻辑全部在 myst-cli 的 build 层实现。

**证据**：
- F-038: build() 函数在 myst-cli 中实现，负责 collectAllBuildExportOptions（收集导出配置）→ localArticleExport（分发执行）→ buildSite（站点构建）
- F-039: localArticleExport 根据 format 字段分发到 runTexExport/runWordExport/runJatsExport/runMdExport/runTypstExport 等函数
- F-039: PDF 导出是两步流程：先 runTexExport 生成 .tex，再 createPdfGivenTexExport 调用 latexmk 编译
- F-039: MECA 导出在所有其他格式之后执行，因为 MECA 打包包含其他格式的产物

**反常识**：myst-to-tex 不直接生成 PDF——它只生成 .tex 内容（LatexResult），PDF 编译是 myst-cli 通过 latexmk 命令完成的。这意味着 myst-to-tex 本身是纯转换库，不依赖系统 LaTeX 安装。

**行动**：
- 编程式使用单文件转换时直接调用 myst-to-* 包
- 需要完整项目构建（含模板、PDF编译、多文件）时通过 myst-cli 的 build 层
- 各 runXxxExport 函数在 myst-cli/src/build/ 下，负责文件 I/O 和模板整合

## 洞察 I-005：元数据标签实现条件导出与分页控制

**陈述**：block 节点的 metadata tags（通过 getMetadataTags 提取）控制导出行为，实现"某些内容只在特定格式中显示"和分页控制。

**证据**：
- F-005: TeX 导出中，block 的 metadata tags 控制：`no-tex`/`no-pdf` 跳过、`new-page`→`\newpage`、`page-break`→`\pagebreak`、`outline`（Beamer 模式）特殊处理
- F-023: Typst 导出中，`no-typst`/`no-pdf` 跳过、`page-break`/`new-page`→`#pagebreak(weak: true)`
- F-005: Beamer 模式下 heading 映射到 \frametitle，block 映射到 \begin{frame}...\end{frame}
- F-005: `part: 'index'` 的 block 触发 \printindex 和 imakeidx 包

**反常识**：条件导出不是通过"配置项禁用某类节点"实现的，而是在每个节点的 handler 中检查 metadata tag 并跳过/转换。这使得控制粒度到单个 block 级别。

**行动**：
- 编写 MyST 文档时用 `:class: no-tex` 等标签标记不需要导出到特定格式的内容
- Beamer 演示文稿通过 `+++ {"outline": true}` 元数据标记大纲页
- 分页控制使用 `:class: new-page` 或 `:class: page-break`

## 知识地图

```
myst-exporters 知识地图
=======================

                    MDAST (MyST Abstract Syntax Tree)
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  直接转换  │   │  栈式构建  │   │  生态复用  │
    │  系列器    │   │  系列器    │   │           │
    ├───────────┤   ├───────────┤   ├───────────┤
    │ myst-to-  │   │ myst-to-  │   │ myst-to-  │
    │ tex       │   │ jats      │   │ html      │
    │ typst     │   │ docx      │   │ (mdast→   │
    │           │   │           │   │  hast→    │
    │ Handler表 │   │ Handler表 │   │  rehype)  │
    │ +State    │   │ +Stack    │   │           │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐         │
    │ LatexResult│   │ JATS XML  │   ┌─────▼─────┐
    │ TypstResult│   │ DOCX      │   │ HTML 字符串│
    └─────┬─────┘   │ Buffer    │   └───────────┘
          │         └───────────┘
    ┌─────▼─────┐
    │   jtex    │◄──── 模板引擎 (Nunjucks)
    │ 模板渲染   │       template.tex/template.typ
    └─────┬─────┘       [CONTENT] / [-IMPORTS-]
          │
    ┌─────▼─────┐   ┌─────────────┐
    │ .tex文件  ├──►│  latexmk    ├──► PDF
    │ .typ文件  ├──►│  typst CLI  ├──► PDF
    └───────────┘   └─────────────┘
          (编译在 myst-cli 层，不在 exporter 包)

  ┌─────────────────────────────────────────┐
  │            导入转换器（反向）             │
  │  jats-to-myst: JATS XML → MDAST         │
  │  tex-to-myst:  LaTeX → MDAST (有限支持)  │
  └─────────────────────────────────────────┘

  ┌─────────────────────────────────────────┐
  │            编排层 (myst-cli)             │
  │  build() → localArticleExport()         │
  │  格式分发 → 模板下载 → 文件I/O → watch   │
  └─────────────────────────────────────────┘
```
