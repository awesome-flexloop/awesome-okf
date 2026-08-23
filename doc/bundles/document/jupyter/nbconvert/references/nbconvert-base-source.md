---
type: "Reference"
title: "NbConvertBase配置基类源码解析"
description: "nbconvert.utils.base模块：NbConvertBase全局配置基类源码解析"
tags: [base-class, configuration, display-data-priority, traitlets, source-code]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: base-util
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/utils/base.py"
    title: "utils/base.py"
---

# NbConvertBase配置基类源码解析

> 源码路径：`nbconvert/utils/base.py`

## 模块概述

`NbConvertBase`是nbconvert所有可配置组件（Exporter、Preprocessor、Writer、Filter、PostProcessor）的共同基类，定义了全局共享的配置项。

## NbConvertBase类

### 类继承

```
LoggingConfigurable → NbConvertBase
```

`LoggingConfigurable`来自traitlets.config，提供：
- 配置管理（Config对象合并）
- 日志记录（self.log）
- Trait属性自动配置

### 关键Trait属性

#### display_data_priority

```python
display_data_priority = List([
    "text/html",
    "application/pdf",
    "text/latex",
    "image/svg+xml",
    "image/png",
    "image/jpeg",
    "text/markdown",
    "text/plain",
], help="An ordered list of preferred output type...").tag(config=True)
```

- 有序列表，定义display_data输出的MIME类型优先级
- DataTypeFilter过滤器使用此列表选择输出格式
- 优先级从高到低：HTML > PDF > LaTeX > SVG > PNG > JPEG > Markdown > 纯文本
- 用户可通过配置修改顺序或添加新的MIME类型

#### default_language

```python
default_language = Unicode("ipython",
    help="Deprecated default highlight language as of 5.0...").tag(config=True)
```

- 默认高亮语言（已废弃，5.0版本后推荐使用cell metadata中的language_info）

## 在组件体系中的位置

```
NbConvertBase
├── Exporter（导出器基类）
│   └── TemplateExporter（模板导出器）
│       ├── HTMLExporter
│       ├── LatexExporter
│       ├── MarkdownExporter
│       ├── PDFExporter
│       ├── SlidesExporter
│       ├── PythonExporter
│       ├── ScriptExporter
│       ├── RSTExporter
│       ├── ASCIIDocExporter
│       ├── NotebookExporter
│       ├── WebPDFExporter
│       ├── QtPDFExporter
│       └── QtPNGExporter
├── Preprocessor（预处理器基类）
│   ├── TagRemovePreprocessor
│   ├── RegexRemovePreprocessor
│   ├── ClearOutputPreprocessor
│   ├── ExecutePreprocessor
│   └── ...（其他预处理器）
├── WriterBase（写入器基类）
│   ├── FilesWriter
│   ├── StdoutWriter
│   └── DebugWriter
├── PostProcessorBase（后处理器基类）
│   └── ServePostProcessor
└── Highlight2HTML / Highlight2Latex（高亮过滤器类）
```

所有子类都可以通过配置系统修改`display_data_priority`：

```python
c = Config()
c.NbConvertBase.display_data_priority = [
    "image/png",
    "image/jpeg",
    "text/html",
    "text/plain",
]
```
