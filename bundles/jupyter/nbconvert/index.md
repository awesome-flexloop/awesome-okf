---
type: "bundle-index"
title: "nbconvert - Jupyter Notebook格式转换工具"
description: "nbconvert完整学习资源包：概念文档、源码参考、可运行示例"
tags: [jupyter, nbconvert, notebook, conversion, export]
version: "7.16.6"
okf_version: "v0.2"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
source_repo: "https://github.com/jupyter/nbconvert"
source_path: "external/libs/jupyter/nbconvert"
status: stable
---

# nbconvert - Jupyter Notebook 格式转换工具

**nbconvert** 是 Jupyter 生态系统中的核心格式转换工具，用于将 `.ipynb` Notebook 文件转换为 HTML、LaTeX、PDF、Markdown、reStructuredText、Python脚本、Reveal.js幻灯片等多种格式。

## 📦 包信息

| 属性 | 值 |
|------|-----|
| 项目名称 | nbconvert |
| 版本 | 7.16.6 |
| 许可证 | BSD-3-Clause |
| Python要求 | >=3.9 |
| 源码路径 | `external/libs/jupyter/nbconvert` |
| PyPI | https://pypi.org/project/nbconvert/ |
| 文档 | https://nbconvert.readthedocs.io/ |
| 仓库 | https://github.com/jupyter/nbconvert |

## 🚀 快速开始

### 安装

```bash
pip install nbconvert
# 或安装完整功能
pip install nbconvert[all]
```

### 基本使用

```bash
# CLI：转换为HTML
jupyter nbconvert --to html notebook.ipynb

# CLI：执行并转换
jupyter nbconvert --execute --to html notebook.ipynb

# Python API
from nbconvert.exporters import HTMLExporter
exporter = HTMLExporter()
output, resources = exporter.from_filename("notebook.ipynb")
```

更多快速上手内容请阅读：[5分钟快速上手](concepts/01-getting-started.md)

## 📚 文档结构

```
nbconvert/
├── index.md              ← 你在这里（Bundle入口）
├── log.md                ← 生成日志
├── concepts/             ← 概念文档（13篇，分入门/核心/进阶三篇）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture-overview.md
│   ├── 03-exporter-hierarchy.md
│   ├── 04-preprocessor-system.md
│   ├── 05-template-system.md
│   ├── 06-filters-system.md
│   ├── 07-writers-and-postprocessors.md
│   ├── 08-cli-and-configuration.md
│   ├── 09-custom-exporter.md
│   ├── 10-custom-preprocessor.md
│   ├── 11-custom-template.md
│   └── 12-execution-and-integration.md
├── examples/             ← 可运行示例（4个Python脚本）
│   ├── index.md
│   ├── 01-basic-conversion.py
│   ├── 02-execute-notebook.py
│   ├── 03-custom-preprocessor-template.py
│   └── 04-batch-conversion-pipeline.py
└── references/           ← 源码参考（8个核心模块解析）
    ├── index.md
    ├── exporter-base-source.md
    ├── template-exporter-source.md
    ├── preprocessor-source.md
    ├── factory-source.md
    ├── filters-source.md
    ├── writer-source.md
    ├── postprocessor-source.md
    └── nbconvert-base-source.md
```

## 🗺️ 内容导航

### [📖 概念文档](concepts/index.md)（13篇）

系统讲解nbconvert的架构原理和使用方法，按三篇组织：

- **入门篇（2篇）**：[介绍](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md)
- **核心篇（7篇）**：
  - [架构总览](concepts/02-architecture-overview.md) — 四阶段流水线
  - [导出器体系](concepts/03-exporter-hierarchy.md) — Exporter类层次
  - [预处理器系统](concepts/04-preprocessor-system.md) — Preprocessor链
  - [模板系统](concepts/05-template-system.md) — Jinja2模板
  - [过滤器系统](concepts/06-filters-system.md) — 40+内置过滤器
  - [写入器与后处理器](concepts/07-writers-and-postprocessors.md) — Writer/PostProcessor
  - [CLI与配置](concepts/08-cli-and-configuration.md) — 命令行与traitlets配置
- **进阶篇（4篇）**：
  - [自定义导出器](concepts/09-custom-exporter.md)
  - [自定义预处理器](concepts/10-custom-preprocessor.md)
  - [自定义模板](concepts/11-custom-template.md)
  - [Notebook执行与生态集成](concepts/12-execution-and-integration.md)

### [💻 示例代码](examples/index.md)（4个）

可直接运行的Python脚本，从基础到高级：

1. [基本转换](examples/01-basic-conversion.py) — 各种格式导出、Writer使用
2. [执行Notebook](examples/02-execute-notebook.py) — ExecutePreprocessor、报告生成
3. [自定义预处理器和模板](examples/03-custom-preprocessor-template.py) — 深度定制
4. [批量转换与流水线](examples/04-batch-conversion-pipeline.py) — 批量处理、文档站点

### [🔍 源码参考](references/index.md)（8篇）

基于源码深度阅读的模块解析文档，作为概念文档的信源：

- Exporter基类、TemplateExporter核心、Preprocessor系统
- 导出器工厂、过滤器、Writer、PostProcessor、NbConvertBase

## 🏗️ 核心架构

nbconvert采用**四阶段流水线**架构：

```
Notebook (.ipynb)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Preprocessors（预处理器链）                           │
│    ExecutePreprocessor → TagRemovePreprocessor → ...    │
│    执行代码 / 过滤cell / 提取输出 / 清洗元数据            │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Exporter（导出器）                                    │
│    TemplateExporter 子类                                │
│    Jinja2模板渲染（模板 + 过滤器 → 输出字符串）           │
│    支持: HTML/LaTeX/PDF/Markdown/Slides/Python/...      │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Writer（写入器）                                      │
│    FilesWriter（文件）/ StdoutWriter（标准输出）          │
│    写入输出文件 + 二进制资源（图片等）                     │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. PostProcessor（后处理器）                             │
│    ServePostProcessor（HTTP预览服务器）                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    输出文件（HTML/PDF/MD/PY/...）
```

## 🔑 核心组件一览

| 组件 | 数量 | 说明 |
|------|------|------|
| Exporter | 14个内置 | HTML/LaTeX/PDF/WebPDF/Markdown/RST/AsciiDoc/Slides/Python/Script/Notebook/QtPDF/QtPNG/Custom |
| Preprocessor | 11个内置 | Execute/TagRemove/ClearOutput/CoalesceStreams/ExtractOutput/CSSHTMLHeader/HighlightMagics/Latex/SVG2PDF/RegexRemove/ClearMetadata |
| Template | 7套内置 | base/lab/classic/reveal/markdown/rst/asciidoc（+ article/lab/classic在LaTeX中） |
| Filter | 40+内置 | Markdown转换/代码高亮/ANSI处理/HTML清洗/LaTeX转义/文本处理 |
| Writer | 3个内置 | FilesWriter/StdoutWriter/DebugWriter |
| PostProcessor | 1个内置 | ServePostProcessor（HTTP预览） |

## 📖 推荐阅读路径

- **新用户**：[介绍](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [CLI与配置](concepts/08-cli-and-configuration.md)
- **理解架构**：[架构总览](concepts/02-architecture-overview.md) → [导出器体系](concepts/03-exporter-hierarchy.md) → [预处理器系统](concepts/04-preprocessor-system.md)
- **扩展开发**：[自定义导出器](concepts/09-custom-exporter.md) → [自定义预处理器](concepts/10-custom-preprocessor.md) → [自定义模板](concepts/11-custom-template.md)
- **实战示例**：直接运行 [examples/](examples/index.md) 目录下的Python脚本

## 📝 注意事项

1. 本Bundle基于nbconvert 7.16.6源码分析生成，API可能随版本变化
2. LaTeX/PDF导出需要安装pandoc和TeX Live
3. Notebook执行（ExecutePreprocessor）需要安装对应Kernel（如ipykernel）
4. WebPDF导出需要playwright和Chromium浏览器

---

*本文档由OKF v0.2格式生成，通过source-code-to-okf-wiki技能从源码自动萃取*
