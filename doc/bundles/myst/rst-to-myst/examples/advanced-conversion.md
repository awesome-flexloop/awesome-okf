---
type: Example
title: 高级转换场景
description: 处理 Sphinx 指令、Front Matter、数学公式和自定义指令映射的示例。
tags: [example, sphinx, directives, front-matter, math]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 转换含 Sphinx 指令的文档

确保已安装 Sphinx 支持：

```bash
pip install "rst-to-myst[sphinx]"
```

创建 Sphinx 文档 `api.rst`：

```rst
:mod:`mymodule`
===============

.. module:: mymodule

.. autoclass:: MyClass
   :members:
   :undoc-members:

.. autofunction:: my_function

.. note::

   这是使用 :py:class:`MyClass` 的注意事项。
```

转换时启用 Sphinx 并加载 autodoc 扩展：

```bash
rst2myst convert --sphinx -e sphinx.ext.autodoc api.rst
```

生成的 `api.md` 将包含正确的 MyST 指令语法：

````markdown
# {py:mod}`mymodule`

```{py:module} mymodule
```

```{py:autoclass} MyClass
:members:
:undoc-members:
```

```{py:autofunction} my_function
```

```{note}
这是使用 {py:class}`MyClass` 的注意事项。
```
````

## Front Matter 自动转换

RST 文档开头的 field list 会自动转换为 YAML front matter：

```rst
:title: 文档标题
:author: 张三
:date: 2024-01-01

=====
正文
=====

内容...
```

转换后：

```markdown
---
title: 文档标题
author: 张三
date: 2024-01-01
---

# 正文

内容...
```

## 数学公式转换

RST 数学会转换为美元定界格式：

```rst
行内数学 :math:`E=mc^2`。

.. math::

   \sum_{i=1}^{n} i = \frac{n(n+1)}{2}
   :label: eq:sum
```

转换后：

```markdown
行内数学 $E=mc^2$。

$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$ (eq:sum)
```

所需扩展：`dollarmath`。

## 自定义指令映射

创建 `conversions.yml` 映射自定义指令：

```yaml
mypackage.directives.MyDirective: eval_rst
```

转换时使用：

```bash
rst2myst convert -c conversions.yml docs/
```

## 使用配置文件

创建 `rst2myst.yml` 配置默认选项：

```yaml
default_domain: py
sphinx: true
consecutive_numbering: true
colon_fences: true
dollar_math: true
```

使用配置文件转换：

```bash
rst2myst --config rst2myst.yml convert docs/
```

## Python API 批量处理并收集警告

```python
from io import StringIO
from rst_to_myst import rst_to_myst, compile_namespace

# 预编译 namespace 提升批量性能
ns = compile_namespace(use_sphinx=True)

rst_files = ["file1.rst", "file2.rst", "file3.rst"]
all_extensions = set()

for path in rst_files:
    with open(path, encoding="utf8") as f:
        text = f.read()

    warning_stream = StringIO()
    output = rst_to_myst(
        text,
        warning_stream=warning_stream,
        namespace=ns,  # 使用预编译 namespace
        raise_on_warning=False,
    )

    warnings = warning_stream.getvalue()
    if warnings:
        print(f"Warnings in {path}:")
        print(warnings)

    all_extensions.update(output.extensions)

    # 写入 .md 文件
    md_path = path.replace(".rst", ".md")
    with open(md_path, "w", encoding="utf8") as f:
        f.write(output.text)

print(f"Required extensions: {all_extensions}")
```

## 查看可用指令和角色

```bash
# 列出所有可用指令
rst2myst directives list

# 查看特定指令信息
rst2myst directives show image

# 列出所有角色
rst2myst roles list

# 查看特定角色信息
rst2myst roles show math
```

## 相关概念

- [转换选项详解](/concepts/10-configuration-options.md)
- [ApplicationNamespace 与 Sphinx 扩展加载机制](/concepts/08-namespace-mocking.md)
- [指令转换机制与 directives.yml 映射](/concepts/05-directive-conversion.md)
- [Front Matter 提取与 YAML 输出](/concepts/09-front-matter.md)
