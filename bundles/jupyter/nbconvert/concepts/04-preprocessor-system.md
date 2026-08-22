---
type: "concept"
title: "预处理器系统"
description: "Preprocessor基类机制、11个内置预处理器详解、执行顺序与自定义预处理器"
tags: [preprocessor, execute, cell-processing, pipeline]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: preprocessor
    resource: ../references/preprocessor-source.md
    title: "Preprocessor预处理器源码解析"
  - id: exporter-base
    resource: ../references/exporter-base-source.md
    title: "Exporter基类源码解析"
---

# 预处理器系统

预处理器（Preprocessor）是nbconvert转换流水线的第一阶段，在Jinja2模板渲染之前对Notebook进行变换。每个预处理器按注册顺序依次执行，可以修改Notebook结构、执行代码、提取资源、清理数据等。

## Preprocessor 基类

所有预处理器继承自 `Preprocessor` 类，后者继承自 `NbConvertBase`。

### 核心方法

#### `__call__(nb, resources)`

预处理器的调用入口。检查`self.enabled`标志：
- 如果`enabled=True`，调用`self.preprocess(nb, resources)`
- 如果`enabled=False`，直接返回原始(nb, resources)，不做任何处理

#### `preprocess(nb, resources)`

默认实现遍历所有cell，逐个调用`preprocess_cell()`：

```python
def preprocess(self, nb, resources):
    for index, cell in enumerate(nb.cells):
        nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
    return nb, resources
```

子类可以覆盖此方法实现notebook级别的处理（如需要访问cell间关系时）。

#### `preprocess_cell(cell, resources, index)`

子类必须实现的方法，对单个cell进行变换：
- `cell`：当前cell对象（NotebookNode）
- `resources`：资源字典
- `index`：cell在notebook中的索引
- 必须返回修改后的(cell, resources)元组

### 默认disabled

Preprocessor基类的`enabled`默认为`False`。预处理器被注册后默认不执行，需要以下方式之一启用：

1. **配置文件**：`c.Exporter.preprocessors = ["mymodule.MyPreprocessor"]`（用户指定的默认enabled=True）
2. **Python API**：`exporter.register_preprocessor(MyPreprocessor(), enabled=True)`
3. **conf.json**：模板配置中声明的预处理器会被启用
4. **TemplateExporter默认配置**：RegexRemovePreprocessor和TagRemovePreprocessor在default_config中启用

## 执行流程

```
Exporter._preprocess(nb, resources)
│
├─ nbc = copy.deepcopy(nb)
├─ resc = copy.deepcopy(resources)
├─ validator.normalize(nbc)  # 规范化notebook
│
└─ for preprocessor in self._preprocessors:
    │
    ├─ if not preprocessor.enabled → continue（跳过）
    │
    ├─ preprocessor(nbc, resc) → __call__
    │   └─ preprocess(nbc, resc)
    │       └─ for each cell: preprocess_cell(cell, resc, index)
    │
    └─ if not optimistic_validation:
        └─ nbformat.validate(nbc)  # 验证notebook合法性
```

关键特性：
- 每个预处理器接收前一个预处理器的输出
- 默认在每个预处理器后执行nbformat验证（`optimistic_validation=False`）
- `optimistic_validation=True`时仅在所有预处理器完成后验证一次（性能更好，但调试困难）
- 预处理器可以通过修改resources字典向模板传递数据

## 内置预处理器详解

### 1. TagRemovePreprocessor

**功能**：根据cell的metadata标签移除cell或cell的部分内容。

**配置**：
```python
c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
c.TagRemovePreprocessor.remove_input_tags = ("remove_input",)
c.TagRemovePreprocessor.remove_all_outputs_tags = ("remove_output",)
c.TagRemovePreprocessor.remove_single_output_tags = ()
```

**使用方式**：在Notebook中给cell添加metadata标签，如：
```json
{
  "tags": ["remove_cell"]
}
```

**在TemplateExporter中默认启用**。

### 2. RegexRemovePreprocessor

**功能**：根据cell输出是否匹配正则模式来移除cell。

**配置**：
```python
c.RegexRemovePreprocessor.patterns = ["\\s*pattern\\s*"]
```

**在TemplateExporter中默认启用**。

### 3. ClearOutputPreprocessor

**功能**：清空所有code cell的输出（outputs和execution_count）。

**用途**：生成干净的Notebook模板，或减小文件体积。

### 4. CoalesceStreamsPreprocessor

**功能**：合并连续的stdout/stderr流输出。

**背景**：Notebook执行中可能产生多个连续的stream输出（如多次print），此预处理器将它们合并为单个stream输出，减少冗余。

### 5. ExecutePreprocessor

**功能**：执行Notebook中的代码cell（基于nbclient库）。

**关键配置**：
```python
c.ExecutePreprocessor.timeout = 30        # 单个cell超时（秒）
c.ExecutePreprocessor.kernel_name = "python3"  # 内核名称
c.ExecutePreprocessor.allow_errors = False      # 是否允许错误继续
```

**对应CLI选项**：`--execute`

这是最复杂的预处理器，启动Jupyter内核执行代码，将输出填充回Notebook。

### 6. SVG2PDFPreprocessor

**功能**：将输出中的SVG图片转换为PDF格式。

**用途**：LaTeX/PDF导出时，PDF不直接支持SVG，需要转换为PDF格式。

**依赖**：需要系统安装`inkscape`或`cairosvg`。

### 7. LatexPreprocessor

**功能**：LaTeX导出相关的预处理，包括：
- 处理LaTeX特殊字符
- 调整数学环境
- 处理文档类和包引用

### 8. HighlightMagicsPreprocessor

**功能**：对IPython magic命令（`%matplotlib inline`、`%%timeit`等）进行特殊处理，确保代码高亮正确显示。

**工作方式**：在magic行前添加注释标记，配合highlight过滤器正确处理。

### 9. ExtractOutputPreprocessor

**功能**：提取cell输出中的二进制数据（图片等）到resources字典。

**工作方式**：
- 遍历所有outputs
- 将image/png、image/jpeg、image/svg+xml等数据提取到`resources["outputs"]`
- 将输出中的数据替换为文件名引用
- Writer随后将这些文件写入磁盘

**关键配置**：
```python
c.ExtractOutputPreprocessor.output_filename_template = "{unique_key}_{cell_index}_{index}{extension}"
```

### 10. ExtractAttachmentsPreprocessor

**功能**：提取Markdown cell中的附件（attachments）。

**背景**：Markdown cell可以内嵌图片附件，此预处理器将附件数据提取到resources中。

### 11. ClearMetadataPreprocessor

**功能**：清理Notebook和cell的元数据，移除不必要的字段。

**配置**：
```python
c.ClearMetadataPreprocessor.clear_notebook_metadata = True
c.ClearMetadataPreprocessor.clear_cell_metadata = True
c.ClearMetadataPreprocessor.preserve_nb_metadata_mask = set()
c.ClearMetadataPreprocessor.preserve_cell_metadata_mask = set()
```

### 其他预处理器

| 预处理器 | 功能 |
|---------|------|
| `CSSHTMLHeaderPreprocessor` | 将CSS样式提取到HTML头部 |
| `ConvertFiguresPreprocessor` | 转换图片格式（用于不同输出） |
| `SanitizeHTMLPreprocessor` | 基于bleach清洗HTML，防止XSS攻击 |

## 预处理器顺序的重要性

预处理器按注册顺序执行，顺序很重要：

1. **TagRemove/RegexRemove**（先执行）：移除不需要的cell，减少后续处理量
2. **Execute**：执行代码生成输出
3. **CoalesceStreams/ClearOutput**：整理输出
4. **SVG2PDF/HighlightMagics/Latex**：格式相关处理
5. **ExtractOutput/ExtractAttachments**：提取资源文件（在输出处理完之后）
6. **ClearMetadata**：最后清理元数据

## 自定义预处理器

```python
from nbconvert.preprocessors import Preprocessor

class RemoveEmptyCellPreprocessor(Preprocessor):
    """移除空code cell的预处理器"""
    
    def preprocess(self, nb, resources):
        # notebook级别处理：过滤空cell
        new_cells = []
        for index, cell in enumerate(nb.cells):
            if cell.cell_type == "code" and not cell.source.strip():
                continue  # 跳过空code cell
            cell, resources = self.preprocess_cell(cell, resources, index)
            new_cells.append(cell)
        nb.cells = new_cells
        return nb, resources
    
    def preprocess_cell(self, cell, resources, index):
        # cell级别处理
        return cell, resources
```

注册使用：

```python
from nbconvert.exporters import HTMLExporter

exporter = HTMLExporter()
exporter.register_preprocessor(RemoveEmptyCellPreprocessor, enabled=True)
output, resources = exporter.from_filename("notebook.ipynb")
```

## 相关概念

- [导出器体系](03-exporter-hierarchy.md)
- [模板系统](05-template-system.md)
- [Notebook执行与生态集成](12-execution-and-integration.md)
- [自定义预处理器](10-custom-preprocessor.md)
