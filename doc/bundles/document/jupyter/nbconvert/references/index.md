---
type: "index"
title: "nbconvert 源码参考索引"
description: "nbconvert核心模块源码解析文档索引"
tags: [references, source-code, api]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
---

# nbconvert 源码参考索引

本目录包含nbconvert核心模块的源码解析文档，是概念文档的信源基础。

## 核心模块解析

| 文档 | 源文件 | 说明 |
|------|--------|------|
| [Exporter基类](exporter-base-source.md) | `nbconvert/exporters/exporter.py` | Exporter抽象基类，预处理器管道管理 |
| [TemplateExporter](template-exporter-source.md) | `nbconvert/exporters/templateexporter.py` | 基于Jinja2的模板导出核心，693行 |
| [Preprocessor预处理器](preprocessor-source.md) | `nbconvert/preprocessors/base.py` | 预处理器基类与11个内置预处理器 |
| [导出器工厂](factory-source.md) | `nbconvert/exporters/base.py` | `get_exporter`/`get_export_names`工厂函数 |
| [过滤器](filters-source.md) | `nbconvert/exporters/filters.py` 等 | 40+内置Jinja2过滤器详解 |
| [Writer写入器](writer-source.md) | `nbconvert/writers/` | FilesWriter/StdoutWriter/DebugWriter |
| [PostProcessor后处理器](postprocessor-source.md) | `nbconvert/postprocessors/` | ServePostProcessor等后处理器 |
| [NbConvertBase](nbconvert-base-source.md) | `nbconvert/utils/base.py` | 全局配置基类与默认值 |

## 源码路径

```
nbconvert/
├── nbconvertapp.py          # CLI入口应用
├── exporters/
│   ├── exporter.py          # Exporter基类
│   ├── templateexporter.py  # TemplateExporter核心
│   ├── html.py              # HTMLExporter
│   ├── latex.py             # LatexExporter
│   ├── markdown.py          # MarkdownExporter
│   ├── pdf.py               # PDFExporter
│   ├── python.py            # PythonExporter
│   ├── slides.py            # SlidesExporter
│   ├── rst.py               # RSTExporter
│   ├── asciidoc.py          # AsciidocExporter
│   ├── notebook.py          # NotebookExporter
│   ├── qtpdf.py             # QtPDFExporter
│   ├── webpdf.py            # WebPDFExporter
│   └── base.py              # 工厂函数与名称映射
├── preprocessors/
│   ├── base.py              # Preprocessor基类
│   ├── execute.py           # ExecutePreprocessor (nbclient)
│   ├── tagremove.py         # TagRemovePreprocessor
│   ├── clearoutput.py       # ClearOutputPreprocessor
│   ├── coalesce_streams.py  # CoalesceStreamsPreprocessor
│   ├── extractoutput.py     # ExtractOutputPreprocessor
│   ├── csshtmlheader.py     # CSSHTMLHeaderPreprocessor
│   ├── highlightmagics.py   # HighlightMagicsPreprocessor
│   ├── latex.py             # LatexPreprocessor
│   ├── svg2pdf.py           # SVG2PDFPreprocessor
│   └── regexremove.py       # RegexRemovePreprocessor
├── writers/
│   ├── base.py              # WriterBase
│   ├── files.py             # FilesWriter
│   └── stdout.py            # StdoutWriter
├── postprocessors/
│   ├── base.py              # PostProcessorBase
│   └── serve.py             # ServePostProcessor
├── templates/               # 内置Jinja2模板
│   ├── base/
│   ├── lab/
│   ├── classic/
│   ├── reveal/
│   ├── markdown/
│   ├── rst/
│   ├── asciidoc/
│   └── ...
└── filters/                 # 过滤器函数（部分内联在templateexporter中）
```

## 关键类继承关系

```
LoggingConfigurable (traitlets)
├── NbConvertBase (utils/base.py)
│   ├── Exporter (exporters/exporter.py)
│   │   └── TemplateExporter (exporters/templateexporter.py)
│   │       ├── HTMLExporter
│   │       ├── LatexExporter
│   │       ├── MarkdownExporter
│   │       ├── SlidesExporter
│   │       ├── PythonExporter
│   │       ├── PDFExporter
│   │       ├── WebPDFExporter
│   │       └── ...
│   ├── Preprocessor (preprocessors/base.py)
│   │   ├── ExecutePreprocessor
│   │   ├── TagRemovePreprocessor
│   │   ├── ClearOutputPreprocessor
│   │   └── ...
│   ├── WriterBase (writers/base.py)
│   │   ├── FilesWriter
│   │   └── StdoutWriter
│   └── PostProcessorBase (postprocessors/base.py)
│       └── ServePostProcessor
└── NbConvertApp (nbconvertapp.py)
```

## 阅读建议

1. **初次阅读**：先读[Exporter基类](exporter-base-source.md)理解整体流程
2. **深入理解**：读[TemplateExporter](template-exporter-source.md)理解模板渲染核心
3. **扩展开发**：读[Preprocessor预处理器](preprocessor-source.md)和[过滤器](filters-source.md)
4. **CLI使用**：参考[NbConvertBase](nbconvert-base-source.md)配置体系

```{toctree}
:hidden:

exporter-base-source
factory-source
filters-source
nbconvert-base-source
postprocessor-source
preprocessor-source
template-exporter-source
writer-source
```
