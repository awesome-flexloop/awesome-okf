---
type: "index"
title: "nbconvert 示例代码索引"
description: "nbconvert可运行示例代码，覆盖基本用法到高级扩展"
tags: [examples, code-samples, tutorial]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
---

# nbconvert 示例代码索引

本目录包含可直接运行的Python示例脚本，展示nbconvert的各种使用模式。

## 示例列表

| 序号 | 示例文件 | 主题 | 核心API | 难度 |
|------|---------|------|---------|------|
| 01 | [基本转换](01-basic-conversion.py) | Notebook转换为各种格式 | HTMLExporter, MarkdownExporter, FilesWriter | ⭐ 入门 |
| 02 | [执行Notebook](02-execute-notebook.py) | 执行代码并生成报告 | ExecutePreprocessor, 时间记录, 错误处理 | ⭐⭐ 基础 |
| 03 | [自定义预处理器和模板](03-custom-preprocessor-template.py) | 深度定制转换流程 | Preprocessor子类, 自定义Jinja2模板, 自定义Filter | ⭐⭐⭐ 进阶 |
| 04 | [批量转换与自动化流水线](04-batch-conversion-pipeline.py) | 批量处理和文档生成 | BatchConverter, DocSiteGenerator, 配置文件 | ⭐⭐⭐ 进阶 |

## 运行说明

所有示例均为独立Python脚本，可直接运行：

```bash
# 安装依赖
pip install nbconvert nbformat ipykernel matplotlib

# 运行单个示例
cd examples
python 01-basic-conversion.py
```

## 示例对应概念文档

| 示例 | 主要对应概念文档 |
|------|----------------|
| 01-basic-conversion.py | [01-getting-started](../concepts/01-getting-started.md), [03-exporter-hierarchy](../concepts/03-exporter-hierarchy.md), [07-writers-and-postprocessors](../concepts/07-writers-and-postprocessors.md) |
| 02-execute-notebook.py | [04-preprocessor-system](../concepts/04-preprocessor-system.md), [12-execution-and-integration](../concepts/12-execution-and-integration.md) |
| 03-custom-preprocessor-template.py | [10-custom-preprocessor](../concepts/10-custom-preprocessor.md), [11-custom-template](../concepts/11-custom-template.md), [06-filters-system](../concepts/06-filters-system.md) |
| 04-batch-conversion-pipeline.py | [08-cli-and-configuration](../concepts/08-cli-and-configuration.md), [09-custom-exporter](../concepts/09-custom-exporter.md) |

## 前置依赖

```python
# 必需依赖
import nbconvert
import nbformat

# 示例02需要（执行Notebook）
# pip install ipykernel
# python -m ipykernel install --user

# 示例02/03中的图表需要
# pip install matplotlib

# PDF导出示例需要
# 安装TeX Live（LaTeX方式）或 playwright（WebPDF方式）
```

## 学习路径建议

1. **从示例01开始**：了解基本的导出API和Writer用法
2. **示例02**：学习Notebook执行机制，理解自动报告生成
3. **示例03**：掌握自定义扩展能力，创建自己的预处理器和模板
4. **示例04**：学习构建完整的文档自动化流水线
