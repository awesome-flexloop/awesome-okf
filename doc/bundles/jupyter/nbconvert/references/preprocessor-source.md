---
type: "Reference"
title: "Preprocessor预处理器源码解析"
description: "nbconvert.preprocessors.base模块：Preprocessor基类与预处理器执行机制源码解析"
tags: [preprocessor, base-class, cell-processing, source-code]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: preprocessor-base-py
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/preprocessors/base.py"
    title: "preprocessors/base.py"
  - id: preprocessors-init
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/preprocessors/__init__.py"
    title: "preprocessors/__init__.py"
---

# Preprocessor预处理器源码解析

> 源码路径：`nbconvert/preprocessors/base.py`

## 模块概述

预处理器（Preprocessor）是nbconvert转换流水线的第一阶段，在模板渲染之前对Notebook进行变换操作。每个预处理器可以修改Notebook结构、执行代码、提取资源、清理元数据等。

## Preprocessor类

### 类继承

```
LoggingConfigurable → NbConvertBase → Preprocessor
```

### 关键Trait属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | Bool | False | 是否启用此预处理器 |

> **重要**：Preprocessor默认`enabled=False`，需要在配置中显式启用或通过TemplateExporter的conf.json启用。但Exporter.default_preprocessors中注册的预处理器在`_init_preprocessors()`中通过`register_preprocessor(name, enabled=True)`启用。

### 核心方法

#### `__call__(self, nb, resources)`

```python
def __call__(self, nb, resources):
    if self.enabled:
        self.log.debug("Applying preprocessor: %s", self.__class__.__name__)
        return self.preprocess(nb, resources)
    return nb, resources
```

- 预处理器的调用入口
- 仅当`enabled=True`时执行实际处理
- disabled时直接返回原始(nb, resources)

#### `preprocess(self, nb, resources)`

```python
def preprocess(self, nb, resources):
    for index, cell in enumerate(nb.cells):
        nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
    return nb, resources
```

- 默认实现：遍历所有cell，逐个调用`preprocess_cell()`
- 子类可以覆盖此方法实现notebook级别的处理逻辑
- 必须返回修改后的(nb, resources)元组

#### `preprocess_cell(self, cell, resources, index)`

```python
def preprocess_cell(self, cell, resources, index):
    raise NotImplementedError("should be implemented by subclass")
```

- 子类必须实现此方法
- 对单个cell进行变换
- 参数：cell（NotebookNode）、resources（dict）、index（cell在nb.cells中的索引）
- 必须返回修改后的(cell, resources)元组

## 内置预处理器清单

| 预处理器类 | 模块路径 | 功能 |
|-----------|---------|------|
| `TagRemovePreprocessor` | preprocessors.tagremove | 按cell标签移除cell/输入/输出 |
| `RegexRemovePreprocessor` | preprocessors.regexremove | 按正则匹配模式移除cell |
| `ClearOutputPreprocessor` | preprocessors.clearoutput | 清空所有cell的输出 |
| `CoalesceStreamsPreprocessor` | preprocessors.coalescestreams | 合并连续的stdout/stderr流输出 |
| `ExecutePreprocessor` | preprocessors.execute | 执行notebook代码（基于nbclient） |
| `SVG2PDFPreprocessor` | preprocessors.svg2pdf | 将SVG输出转换为PDF（用于LaTeX导出） |
| `LatexPreprocessor` | preprocessors.latex | LaTeX导出相关的预处理 |
| `HighlightMagicsPreprocessor` | preprocessors.highlightmagics | 高亮IPython magic命令 |
| `ExtractOutputPreprocessor` | preprocessors.extractoutput | 提取输出中的图片等资源到resources |
| `ExtractAttachmentsPreprocessor` | preprocessors.extractattachments | 提取Markdown cell中的附件 |
| `ClearMetadataPreprocessor` | preprocessors.clearmetadata | 清理notebook和cell的元数据 |
| `CSSHTMLHeaderPreprocessor` | preprocessors.csshtmlheader | 处理CSS样式到HTML头部 |
| `ConvertFiguresPreprocessor` | preprocessors.convertfigures | 转换图片格式 |
| `SanitizeHTMLPreprocessor` | preprocessors.sanitize | HTML清洗（XSS防护，基于bleach） |

## 预处理器执行流程

```
Exporter._preprocess(nb, resources)
│
├─ copy.deepcopy(nb)
├─ copy.deepcopy(resources)
├─ validator.normalize(nbc)  # 规范化notebook格式
│
└─ for preprocessor in self._preprocessors:
    │
    ├─ preprocessor(nbc, resc)  # 调用__call__
    │   │
    │   ├─ if not enabled: return nbc, resc (跳过)
    │   │
    │   └─ preprocess(nbc, resc)
    │       │
    │       └─ for index, cell in enumerate(nbc.cells):
    │           └─ preprocess_cell(cell, resc, index)
    │
    └─ if not optimistic_validation:
        └─ nbformat.validate(nbc)  # 验证每个预处理器后的notebook合法性
```

## 自定义预处理器模式

```python
from nbconvert.preprocessors import Preprocessor

class MyCustomPreprocessor(Preprocessor):
    def preprocess_cell(self, cell, resources, index):
        # 对每个cell进行处理
        if cell.cell_type == "code":
            # 修改code cell
            pass
        return cell, resources
```

注册方式：
1. Python API：`exporter.register_preprocessor(MyCustomPreprocessor, enabled=True)`
2. 配置文件：`c.Exporter.preprocessors = ["mymodule.MyCustomPreprocessor"]`
3. 模板conf.json：在preprocessors字段中声明
