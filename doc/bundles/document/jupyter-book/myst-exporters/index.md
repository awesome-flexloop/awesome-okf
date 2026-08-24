---
type: bundle
title: "myst-exporters 多格式导出器"
okf_version: "0.2"
---

# myst-exporters：多格式导出器

myst-exporters 是 MyST 生态的多格式导出引擎，将 MyST Markdown 文档（MDAST）转换为 HTML、LaTeX、PDF、DOCX、JATS XML、Markdown、Typst 等多种输出格式，同时支持 JATS XML 和 LaTeX 的导入。

## 架构核心

所有导出器统一采用 **unified Plugin + Serializer + Handler 表驱动** 架构，各格式导出器共享一致的设计模式。LaTeX/Typst 导出通过 jtex 模板引擎注入模板生成完整可编译文档，PDF 由外部编译器（latexmk/typst）从模板输出编译产生。

## 知识地图

```
myst-exporters
├── 统一导出架构 ─────────────── 所有格式的共性设计
│   ├── HTML 导出 ──────────── mdast→hast→rehype 管线
│   ├── LaTeX 导出 ─────────── TexSerializer + jtex 模板
│   ├── PDF 导出 ───────────── LaTeX→latexmk 或 Typst→typst
│   ├── DOCX 导出 ──────────── docx 库构建 Office XML
│   ├── JATS XML 导出 ─────── 栈式 XML 构建
│   ├── Markdown 导出 ──────── MdSerializer 回环输出
│   └── Typst 导出 ────────── TypstSerializer（与 LaTeX 对称）
├── jtex 模板引擎 ───────────── Nunjucks 模板渲染
└── 导入转换器 ──────────────── JATS/LaTeX → MyST
```

## 文档导航

### 入门示例
- [多格式到处示例](examples/01-multi-format-export.md) — CLI 和编程 API 导出多种格式
- [自定义 jtex 模板](examples/02-custom-jtex-template.md) — 创建自定义 LaTeX 模板
- [LaTeX/JATS 导入示例](examples/03-latex-import.md) — 从 JATS/LaTeX 导入并继续导出

### 核心概念（按学习路径）
1. [统一导出架构](concepts/00-exporter-architecture.md) — Serializer+Handler 模式、unified Plugin
2. [HTML 导出](concepts/01-html-export.md) — mdast→hast→rehype 管线、State 编号
3. [LaTeX 导出](concepts/02-latex-export.md) — TexSerializer、Handler 映射、Beamer、导言区
4. [PDF 导出](concepts/03-pdf-export.md) — LaTeX+latexmk 和 Typst 两条路径
5. [DOCX 导出](concepts/04-docx-export.md) — docx 库构建 Office Open XML
6. [JATS XML 导出](concepts/05-jats-export.md) — JatsSerializer 栈式架构、JatsDocument
7. [Markdown 导出](concepts/06-markdown-export.md) — MdSerializer、MyST 语法回环
8. [Typst 导出](concepts/07-typst-export.md) — TypstSerializer、与 LaTeX 对称设计
9. [jtex 模板引擎](concepts/08-jtex-template-engine.md) — Nunjucks 渲染、imports 合并
10. [导入转换器](concepts/09-import-converters.md) — jats-to-myst、tex-to-myst

### 信源参考
- [导出器入口导出表](references/exporter-entrypoints.md) — 各包入口文件导出的公共 API
- [jtex 模板引擎源码](references/jtex-template-engine.md) — renderTemplate、imports 渲染
- [构建编排与导入器](references/build-orchestration.md) — myst-cli build 层、jats/tex-to-myst

### 规格说明
- [事实清单](spec/facts.md) — 从源码提取的编号事实
- [架构洞察](spec/insights.md) — 核心架构洞察与知识地图

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
