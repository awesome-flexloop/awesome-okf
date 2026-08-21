---
type: Concept
title: Sphinx Autodoc 扩展
description: 使用 autodoc 模块让 Sphinx 自动文档化 Invoke Task 对象，将可复用任务集的 API 文档纳入 Sphinx 文档
tags: [invocations, autodoc, sphinx, documentation, task-documentation]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# Sphinx Autodoc 扩展

`invocations.autodoc` 是一个 [Sphinx 扩展](https://www.sphinx-doc.org/en/master/extdev/index.html)，它让 Sphinx 的 [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) 功能能够识别并文档化 Invoke 的 `Task` 对象。

## 为什么需要它

标准 Sphinx autodoc 只能识别普通的 Python 函数、类和模块。当你使用 `@task` 装饰器将函数包装为 Invoke Task 时，Sphinx 看到的是一个 `Task` 实例而非原始函数，因此 autodoc 默认会跳过它或无法正确提取签名和文档字符串。

`invocations.autodoc` 注册了一个自定义的 `TaskDocumenter`，解决了这个问题。

## 适用场景

这个扩展主要面向**可复用任务库的作者**——即那些将 Invoke 任务定义为可导入 Python 包成员的场景（如 invocations 自身）。对于仅存在于单个项目 `tasks.py` 中的"本地"任务，它也能工作，但需要调整 `sys.path` 让 Sphinx 能导入你的 tasks 模块。

## 安装与配置

### 1. 安装

确保已安装 invocations（它依赖 sphinx）：

```bash
pip install invocations
```

### 2. 在 conf.py 中启用

在你的 Sphinx `conf.py` 的 `extensions` 列表中添加：

```python
# conf.py
extensions = [
    "sphinx.ext.autodoc",
    "invocations.autodoc",  # 添加这一行
    # ... 其他扩展
]
```

`invocations.autodoc` 的 `setup()` 函数会自动加载 `sphinx.ext.autodoc` 作为依赖扩展，因此不需要手动添加。

### 3. 在 RST 文档中使用 automodule

在你的 `.rst` 文档中，使用标准的 `automodule` 指令指向你的任务模块：

```rst
.. automodule:: myproject.tasks
   :members:
```

### 4. 配置 autodoc 选项

在 `conf.py` 中配置默认选项：

```python
autodoc_default_options = {
    "members": True,           # 文档化所有成员
    "undoc-members": True,     # 包含没有 docstring 的任务
    "show-inheritance": True,
}
```

默认情况下，只有带有 docstring 的任务会被文档化。使用 `:undoc-members:` 标志或配置 `"undoc-members": True` 可以包含没有 docstring 的任务。

## TaskDocumenter 的工作原理

`TaskDocumenter` 继承自 Sphinx autodoc 的两个基类：

```python
class TaskDocumenter(
    autodoc.DocstringSignatureMixin,    # 支持从 docstring 提取签名
    autodoc.ModuleLevelDocumenter       # 模块级别的文档化器
):
    objtype = "task"
    directivetype = "function"
```

### 核心方法

| 方法 | 作用 |
|------|------|
| `can_document_member(cls, member, ...)` | 类方法，判断是否能文档化给定对象——通过 `isinstance(member, Task)` 检查 |
| `format_args(self)` | 格式化参数签名——从 `self.object.body`（原始函数）提取 `inspect.signature`，然后通过 `autodoc.stringify_signature()` 转换为字符串 |
| `document_members(self, all_members=False)` | 空实现——阻止 autodoc 递归文档化 Task 对象的内部属性（大部分是实现细节） |

### 签名处理的注意事项

`format_args()` 当前会保留 Context 参数（即函数签名中的第一个 `c` 参数）。这是一个已知的设计选择——因为调用任务时既可以通过 CLI（不需要传 `c`）也可以作为原始 Python 函数调用（需要传 `c`）。Invoke issue #170 讨论了这个问题的改进方向。

## 典型项目结构

使用 autodoc 文档化任务的项目通常有这样的结构：

```
myproject/
├── myproject/
│   ├── __init__.py
│   └── tasks.py          # 你的可复用任务定义
├── docs/
│   ├── conf.py           # 添加 "invocations.autodoc"
│   ├── index.rst
│   └── api.rst           # 使用 automodule
├── tasks.py              # 项目自身的 tasks.py（可选）
└── pyproject.toml
```

`docs/api.rst` 内容：

```rst
API Documentation
=================

.. automodule:: myproject.tasks
   :members:
```

如果你的任务模块不在标准导入路径中，需要在 `conf.py` 中调整路径：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## 文档化效果

启用后，你的任务在 Sphinx 文档中会显示为：
- 任务名（函数名或 `@task(name=...)` 指定的名称）
- 参数签名（从原始函数提取）
- Docstring 内容（包括 `:param:` 等 RST 域标记）
- 看起来和普通函数文档一致（`directivetype = "function"`）

## 与其他 Invocations 模块的关系

`autodoc.py` 是 invocations 中唯一一个不是任务集合的模块——它是一个 Sphinx 扩展，不导出任何 @task 或 Collection。它的存在是为了支持 invocations 自身（以及类似的可复用任务库）的文档构建。

invocations 自己的 docs 构建就使用了这个扩展来文档化其包含的任务。

## 相关概念

- [Sphinx 文档管理](/concepts/04-docs-sphinx.md)
- [Invocations 简介](/concepts/00-introduction.md)
- [组合模式：组装自己的任务集合](/concepts/10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
