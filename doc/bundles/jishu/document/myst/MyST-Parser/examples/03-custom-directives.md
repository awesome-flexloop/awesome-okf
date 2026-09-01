---
type: Example
title: 自定义指令与角色
description: 在 MyST Markdown 中创建和使用自定义 Sphinx 指令和角色的完整示例
tags: [myst, sphinx, directive, role, custom, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 自定义指令与角色

MyST-Parser 通过 Mock 桥接层自动支持所有 Sphinx 注册的指令和角色。本示例展示如何在 conf.py 中注册自定义指令/角色并在 Markdown 中使用。

## 自定义指令示例

### 步骤 1：在 conf.py 中定义指令

```python
# conf.py
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx

class FeatureBox(Directive):
    """自定义功能卡片指令"""
    has_content = True
    required_arguments = 1  # 标题
    optional_arguments = 0
    option_spec = {
        "color": directives.unchanged,
        "icon": directives.unchanged,
    }

    def run(self):
        title = self.arguments[0]
        color = self.options.get("color", "blue")
        icon = self.options.get("icon", "✨")

        # 创建外层容器
        container = nodes.container(classes=["feature-box", f"feature-{color}"])

        # 标题节点
        title_node = nodes.paragraph(classes=["feature-title"])
        title_node += nodes.Text(f"{icon} {title}")

        # 内容节点
        body = nodes.container(classes=["feature-body"])
        self.state.nested_parse(self.content, self.content_offset, body)

        container += title_node
        container += body
        return [container]

def setup(app: Sphinx):
    app.add_directive("feature-box", FeatureBox)
    app.add_css_file("custom.css")
    return {"version": "1.0", "parallel_read_safe": True}
```

### 步骤 2：在 Markdown 中使用

````markdown
# 产品特性

:::{feature-box} 简单易用
:color: green
:icon: 🚀

只需一行命令即可安装：

```bash
pip install my-package
```
:::

:::{feature-box} 高性能
:color: blue
:icon: ⚡

比同类产品快 **10 倍**。
:::
````

### 步骤 3：添加 CSS（_static/custom.css）

```css
.feature-box {
    border-left: 4px solid;
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 4px;
}
.feature-green { border-color: #28a745; background: #f0fff4; }
.feature-blue { border-color: #007bff; background: #f0f7ff; }
.feature-title { font-weight: bold; font-size: 1.1em; margin-bottom: 8px; }
```

## 自定义角色示例

### 定义角色

```python
# conf.py（添加到 setup 函数中）
from docutils.parsers.rst import roles
from docutils import nodes

def badge_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """徽章角色：{badge}`text,color`"""
    parts = text.split(",", 1)
    label = parts[0].strip()
    color = parts[1].strip() if len(parts) > 1 else "blue"

    node = nodes.inline(classes=["badge", f"badge-{color}"])
    node += nodes.Text(label)
    return [node], []

def setup(app):
    # ... 指令注册 ...
    app.add_role("badge", badge_role)
    app.add_css_file("custom.css")
    return {"version": "1.0", "parallel_read_safe": True}
```

### 在 Markdown 中使用

```markdown
# 项目状态

当前版本 {badge}`v1.0.0,green` 已发布！

支持 Python {badge}`3.11+,blue`，许可证 {badge}`MIT,yellow`。

兼容性：{badge}`稳定,green` {badge}`测试中,orange` {badge}`实验中,red`
```

## 使用 Sphinx 内置指令

MyST Markdown 可以直接使用所有已注册的 Sphinx 指令：

```markdown
:::{toctree}
:maxdepth: 2
:caption: 目录

getting-started
api/overview
:::

:::{warning}
此 API 在 v2.0 中已变更。
:::

:::{versionadded} 1.0
此功能是新添加的。
:::

:::{deprecated} 2.0
请使用 `new_function()` 替代。
:::

:::{code-block} python
:linenos:
:emphasize-lines: 2,4

def hello():
    name = "World"  # 高亮
    print(f"Hello, {name}!")
    return True      # 高亮
:::
```

## 使用 RST eval-rst

如果需要使用复杂 RST 语法，可以用 eval-rst 指令嵌入：

````markdown
```{eval-rst}
.. csv-table:: 数据表
   :header: "名称", "类型", "说明"
   :widths: 20, 10, 70

   "id", "int", "唯一标识符"
   "name", "str", "名称字段"
```
````

## 相关概念

- [指令与角色](../concepts/07-directives-and-roles.md)
- [MyST 语法概览](../concepts/02-myst-syntax-overview.md)
- [Sphinx 集成机制](../concepts/11-sphinx-integration.md)
