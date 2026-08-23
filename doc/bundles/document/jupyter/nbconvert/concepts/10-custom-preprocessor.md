---
type: "concept"
title: "自定义预处理器"
description: "继承Preprocessor创建自定义cell/Notebook转换器、注册方法与使用场景"
tags: [custom-preprocessor, preprocessor, cell, notebook-transform]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: preprocessor
    resource: ../references/preprocessor-source.md
    title: "预处理器系统源码解析"
  - id: exporter-base
    resource: ../references/exporter-base-source.md
    title: "Exporter基类源码解析"
---

# 自定义预处理器

预处理器（Preprocessor）是nbconvert扩展机制中最常用的定制点。通过继承`Preprocessor`基类，可以在渲染前对Notebook进行任意修改。

## Preprocessor 基类接口

```python
from nbconvert.preprocessors import Preprocessor

class MyPreprocessor(Preprocessor):
    enabled = False  # 默认禁用，需配置启用
    
    def preprocess(self, nb, resources):
        """Notebook级预处理，遍历所有cell"""
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources
    
    def preprocess_cell(self, cell, resources, index):
        """Cell级处理，子类必须实现"""
        raise NotImplementedError
```

## 自定义预处理器类型

### Cell级预处理器（最常见）

实现`preprocess_cell`方法，对每个cell进行处理：

```python
from nbconvert.preprocessors import Preprocessor

class CellTypeRemover(Preprocessor):
    """移除指定类型的cell"""
    enabled = True
    
    # 配置项：要移除的cell类型列表
    remove_cell_types = List(["raw"]).tag(config=True)
    
    def preprocess(self, nb, resources):
        # 重写preprocess来移除cell（而非逐个修改）
        nb.cells = [
            cell for cell in nb.cells
            if cell.cell_type not in self.remove_cell_types
        ]
        return nb, resources
    
    def preprocess_cell(self, cell, resources, index):
        return cell, resources
```

### 元数据修改预处理器

```python
class MetadataCleaner(Preprocessor):
    """清理cell和notebook级别的多余元数据"""
    enabled = True
    
    keep_cell_metadata = List(["tags", "collapsed"]).tag(config=True)
    
    def preprocess_cell(self, cell, resources, index):
        # 只保留指定的cell元数据键
        cell.metadata = {
            k: v for k, v in cell.metadata.items()
            if k in self.keep_cell_metadata
        }
        return cell, resources
```

### 资源注入预处理器

向`resources`字典中注入额外数据供模板使用：

```python
class TOCGenerator(Preprocessor):
    """生成目录（TOC）注入到resources"""
    enabled = True
    
    def preprocess(self, nb, resources):
        toc = []
        for index, cell in enumerate(nb.cells):
            if cell.cell_type == "markdown":
                # 简单提取Markdown标题
                for line in cell.source.splitlines():
                    if line.startswith("#"):
                        level = len(line.split()[0])
                        title = line.lstrip("#").strip()
                        toc.append({
                            "level": level,
                            "title": title,
                            "cell_index": index,
                        })
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        resources["toc"] = toc
        return nb, resources
    
    def preprocess_cell(self, cell, resources, index):
        return cell, resources
```

模板中使用注入的TOC：
```jinja2
{% if resources.toc %}
<nav class="toc">
{% for item in resources.toc %}
  <div class="toc-level-{{ item.level }}">{{ item.title }}</div>
{% endfor %}
</nav>
{% endif %}
```

### 输出修改预处理器

修改code cell的输出内容：

```python
class OutputFilter(Preprocessor):
    """过滤code cell输出中的大图片"""
    max_image_size = Int(1024 * 1024).tag(config=True)  # 1MB
    
    enabled = True
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == "code" and cell.outputs:
            filtered_outputs = []
            for output in cell.outputs:
                if output.output_type == "display_data":
                    # 检查图片大小
                    for key, data in output.data.items():
                        if key.startswith("image/"):
                            if isinstance(data, str) and len(data) > self.max_image_size:
                                # 替换为占位符
                                output.data = {"text/plain": "[大图片已省略]"}
                filtered_outputs.append(output)
            cell.outputs = filtered_outputs
        return cell, resources
```

## 注册自定义预处理器

### 方式1：通过Python API注册到导出器

```python
from nbconvert.exporters import HTMLExporter
from mymodule import TOCGenerator

exporter = HTMLExporter()
exporter.register_preprocessor(TOCGenerator, enabled=True)

output, resources = exporter.from_filename("notebook.ipynb")
```

### 方式2：通过配置文件注册

```python
# config.py
c = get_config()

# 方法A：使用点路径字符串
c.HTMLExporter.preprocessors = [
    "mymodule.TOCGenerator",
    "mymodule.MetadataCleaner",
]

# 方法B：导入类直接引用
import sys
sys.path.insert(0, ".")
from mymodule import TOCGenerator
c.HTMLExporter.preprocessors = [TOCGenerator]

# 配置自定义预处理器
c.TOCGenerator.enabled = True
c.MetadataCleaner.keep_cell_metadata = ["tags"]
```

```bash
jupyter nbconvert --config config.py --to html notebook.ipynb
```

### 方式3：通过entry points注册（插件方式）

```toml
[project.entry-points."nbconvert.preprocessors"]
toc = "mymodule:TOCGenerator"
```

## 预处理器执行顺序

预处理器按以下顺序执行：

1. **`default_preprocessors`列表**：导出器默认配置的预处理器
2. **`_preprocessors`列表**：通过`register_preprocessor`注册的预处理器
3. **`preprocessors`配置项**：用户通过配置添加的预处理器

在`_preprocess()`方法中，按列表顺序依次调用每个预处理器的`__call__()`方法。前一个预处理器的输出是后一个预处理器的输入。

```python
def _preprocess(self, nb, resources):
    for preprocessor in self._preprocessors:
        nb, resources = preprocessor(nb, resources)
    return nb, resources
```

## 常用自定义预处理器模式

### Cell标签过滤

```python
class TagBasedFilter(Preprocessor):
    """基于cell标签进行过滤的通用预处理器"""
    
    enabled = True
    
    def preprocess(self, nb, resources):
        new_cells = []
        for index, cell in enumerate(nb.cells):
            tags = cell.metadata.get("tags", [])
            # 保留没有特定标签的cell
            if "skip_export" not in tags:
                cell, resources = self.preprocess_cell(cell, resources, index)
                new_cells.append(cell)
        nb.cells = new_cells
        return nb, resources
    
    def preprocess_cell(self, cell, resources, index):
        return cell, resources
```

### 水印/版权注入

```python
class WatermarkInjector(Preprocessor):
    """在Notebook末尾注入版权声明"""
    enabled = True
    watermark = Unicode("© 2024 My Company").tag(config=True)
    
    def preprocess(self, nb, resources):
        resources["watermark"] = self.watermark
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources
    
    def preprocess_cell(self, cell, resources, index):
        return cell, resources
```

### 代码替换

```python
import re

class MacroExpander(Preprocessor):
    """展开代码中的宏指令"""
    enabled = True
    
    macros = Dict({
        "@VERSION@": "1.0.0",
        "@DATE@": "2024-01-01",
    }).tag(config=True)
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == "code":
            source = cell.source
            for macro, value in self.macros.items():
                source = source.replace(macro, value)
            cell.source = source
        return cell, resources
```

## 相关概念

- [预处理器系统](04-preprocessor-system.md)
- [架构总览](02-architecture-overview.md)
- [自定义导出器](09-custom-exporter.md)
