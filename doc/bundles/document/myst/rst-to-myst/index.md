---
type: bundle
title: rst-to-myst
description: 将 reStructuredText 转换为 MyST Markdown 的 CLI 工具和 Python 库，支持 Sphinx 指令、数学公式、Front Matter 等。
okf_version: "0.2"
tags: [rst, myst, markdown, conversion, sphinx, docutils]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
---

# rst-to-myst

rst-to-myst 是 [Executable Books](https://executablebooks.org/) 项目开发的工具，用于将 reStructuredText（RST）文档转换为 MyST（Markedly Structured Text）Markdown 格式。提供 CLI 命令行工具和 Python API，支持 Sphinx 扩展加载、自定义指令映射、Front Matter 提取等功能。

- **版本**：0.4.0
- **Python 要求**：≥ 3.9
- **CLI 命令**：`rst2myst`
- **源码**：`rst_to_myst/`

## 快速开始

```bash
pip install rst-to-myst
pip install "rst-to-myst[sphinx]"  # 带 Sphinx 支持

# 单文件转换
rst2myst stream document.rst

# 批量转换
rst2myst convert docs/*.rst
```

Python API：

```python
from rst_to_myst import rst_to_myst
output = rst_to_myst("*Hello* **world**!")
print(output.text)
```

## 三阶段转换流水线

```
RST 文本 → LosslessRSTParser → docutils AST → MarkdownItRenderer → markdown-it tokens → mdformat → MyST Markdown
```

## 文档导航

### [概念文档](/concepts/index.md)

**入门组**

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [项目介绍与安装](/concepts/00-introduction.md) | 安装、核心能力、CLI和API快速开始 |
| 01 | [命令行工具详细用法](/concepts/01-cli-usage.md) | 所有子命令、全局选项和配置文件 |
| 02 | [Python API 使用指南](/concepts/02-python-api.md) | 核心API函数、参数、返回值和代码示例 |

**核心组**

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | [三阶段转换流水线架构](/concepts/03-conversion-pipeline.md) | RST→AST→Tokens→Markdown 转换流程 |
| 04 | [LosslessRSTParser 与自定义 Transform](/concepts/04-lossless-parser.md) | 无损解析器设计和自定义AST变换 |
| 05 | [指令转换机制与 directives.yml 映射](/concepts/05-directive-conversion.md) | RST指令到MyST指令的语法级映射 |
| 06 | [MarkdownItRenderer 与 AST→Token 遍历](/concepts/06-token-rendering.md) | Visitor模式、token生成和inline管理 |
| 07 | [mdformat 渲染集成与自定义渲染器](/concepts/07-mdformat-integration.md) | mdformat引擎使用和自定义渲染器 |

**进机组**

| 序号 | 文档 | 说明 |
|------|------|------|
| 08 | [ApplicationNamespace 与 Sphinx 扩展加载机制](/concepts/08-namespace-mocking.md) | Mock Sphinx应用收集指令/角色 |
| 09 | [Front Matter 提取与 YAML 输出](/concepts/09-front-matter.md) | RST field list 到 YAML front matter |
| 10 | [转换选项详解](/concepts/10-configuration-options.md) | 所有转换选项的作用和使用场景 |

### [示例文档](/examples/index.md)

| 文档 | 说明 |
|------|------|
| [基本 RST 到 MyST 转换](/examples/basic-conversion.md) | CLI流式转换、批量转换、Python API基础用法 |
| [高级转换场景](/examples/advanced-conversion.md) | Sphinx指令、Front Matter、数学公式、自定义映射 |

### [信源参考](/references/index.md)

| 文档 | 对应源码文件 | 说明 |
|------|-------------|------|
| [CLI 命令行接口](/references/source-cli.md) | `cli.py` | 子命令和选项定义 |
| [RST 解析器模块](/references/source-parser.md) | `parser.py` | LosslessRSTParser和Transforms |
| [MarkdownIt 渲染器](/references/source-markdownit.md) | `markdownit.py` | AST到token转换 |
| [mdformat 渲染集成](/references/source-mdformat-render.md) | `mdformat_render.py` | token到Markdown渲染 |
| [命名空间 Mock 系统](/references/source-namespace.md) | `namespace.py` | Sphinx Mock和指令/角色收集 |

### 规范文档

- [事实清单](/spec/facts.md) - R阶段零推断事实采集（71条事实）
- [架构洞察](/spec/insights.md) - I阶段5个核心洞察四元组与知识地图

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
