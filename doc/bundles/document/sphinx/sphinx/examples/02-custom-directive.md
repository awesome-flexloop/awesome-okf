---
type: "example"
title: 自定义reST指令
description: 完整的自定义指令开发示例，包含参数解析、选项处理、内容体处理和子节点生成。
tags: [sphinx, directive, rest, custom-directive]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-dev
    resource: /concepts/07-extension-dev.md
    title: 扩展开发指南
---
# 自定义reST指令

本例展示如何开发功能完整的reST指令，包括参数、选项、内容处理和嵌套指令。

## 示例：NoteBox指令

创建一个带标题、图标和内容的提示框指令。

### 使用效果（reST源码）

```rst
.. notebox:: 重要提示
   :type: warning
   :icon: ⚠️

   这是一个重要的警告信息。
   内容可以包含 **多行文本** 和 ``行内标记``。

   也可以包含段落和列表：

   - 第一项
   - 第二项
```

### 完整实现

```python
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList


class NoteBoxNode(nodes.General, nodes.Element):
    """自定义节点类型，代表提示框。"""
    pass


def visit_notebox_html(self, node):
    """HTML渲染：开始标签。"""
    box_type = node.get('type', 'note')
    icon = node.get('icon', 'ℹ️')
    title = node.get('title', 'Note')

    # CSS类名映射
    type_class = {
        'note': 'note-box note',
        'warning': 'note-box warning',
        'tip': 'note-box tip',
        'important': 'note-box important',
    }.get(box_type, 'note-box note')

    self.body.append(f'<div class="{type_class}">')
    self.body.append(f'<div class="note-box-title">{icon} {title}</div>')
    self.body.append('<div class="note-box-content">')


def depart_notebox_html(self, node):
    """HTML渲染：结束标签。"""
    self.body.append('</div></div>')


def visit_notebox_latex(self, node):
    """LaTeX渲染：使用sphinxlightbox或加粗。"""
    self.body.append('\n\\textbf{' + node.get('title', 'Note') + '}\n\n')


def depart_notebox_latex(self, node):
    pass


class NoteBoxDirective(Directive):
    """提示框指令。

    用法：
        .. notebox:: [标题文本]
           :type: note|warning|tip|important
           :icon: emoji图标
    """
    # 可选的位置参数（标题）
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True  # 标题可以包含空格

    # 选项
    option_spec = {
        'type': directives.unchanged,  # 原样返回字符串
        'icon': directives.unchanged,
    }

    # 是否允许内容体
    has_content = True

    def run(self):
        # 1. 处理参数
        title = self.arguments[0] if self.arguments else 'Note'

        # 2. 处理选项
        box_type = self.options.get('type', 'note')
        icon = self.options.get('icon', {
            'note': 'ℹ️',
            'warning': '⚠️',
            'tip': '💡',
            'important': '❗',
        }.get(box_type, 'ℹ️'))

        # 3. 创建自定义节点
        node = NoteBoxNode()
        node['title'] = title
        node['type'] = box_type
        node['icon'] = icon

        # 4. 解析内容体（支持reST标记）
        if self.content:
            # 创建嵌套节点容器
            content_node = nodes.container()
            # 使用state.nested_parse解析内容体中的reST标记
            self.state.nested_parse(
                self.content,    # 内容行列表
                self.content_offset,  # 内容偏移量
                content_node     # 解析结果容器
            )
            node += content_node

        return [node]


def setup(app):
    # 注册节点（为不同builder指定visitor）
    app.add_node(NoteBoxNode,
                 html=(visit_notebox_html, depart_notebox_html),
                 latex=(visit_notebox_latex, depart_notebox_latex))

    # 注册指令
    app.add_directive('notebox', NoteBoxDirective)

    # 添加CSS样式
    app.add_css_file('notebox.css')

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

### 配套CSS（_static/notebox.css）

```css
.note-box {
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 6px;
    border-left: 4px solid;
}
.note-box.note {
    background: #e7f3ff;
    border-left-color: #2196F3;
}
.note-box.warning {
    background: #fff3e0;
    border-left-color: #ff9800;
}
.note-box.tip {
    background: #e8f5e9;
    border-left-color: #4CAF50;
}
.note-box.important {
    background: #fce4ec;
    border-left-color: #e91e63;
}
.note-box-title {
    font-weight: bold;
    margin-bottom: 8px;
}
```

## Directive类关键属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `required_arguments` | `int` | 必需位置参数数量 |
| `optional_arguments` | `int` | 可选位置参数数量 |
| `final_argument_whitespace` | `bool` | 最后参数是否可含空格（通常用于标题/描述） |
| `option_spec` | `dict` | 选项名→转换器映射 |
| `has_content` | `bool` | 是否允许内容体 |

## 常用选项转换器

`option_spec` 中可以使用docutils提供的转换器：

| 转换器 | 返回值 | 用途 |
|--------|--------|------|
| `directives.unchanged` | `str` | 原样返回字符串 |
| `directives.flag` | `None` | 布尔标志（选项存在即为True） |
| `directives.unchanged_required` | `str` | 必须提供值的字符串选项 |
| `directives.choice(options)` | `str` | 从选项列表中选择 |
| `directives.class_option` | `list[str]` | CSS类名列表（空格分隔） |
| `directives.uri` | `str` | URI/路径 |
| `directives.nonnegative_int` | `int` | 非负整数 |
| `directives.percentage` | `int` | 0-100整数 |
| `directives.length_or_unitless` | `str` | CSS长度 |
| `directives.positive_int` | `int` | 正整数 |
| `int` | `int` | Python int转换 |
| `bool` | `bool` | Python bool转换 |

### 选项示例

```python
class MyDirective(Directive):
    option_spec = {
        'width': directives.length_or_percentage_or_unitless,
        'align': directives.choice(('left', 'center', 'right')),
        'name': directives.unchanged,
        'visible': directives.flag,
        'depth': directives.nonnegative_int,
    }
```

## 内容解析技巧

### 嵌套解析内容体（支持reST标记）

```python
def run(self):
    node = MyNode()
    if self.content:
        container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, container)
        node += container
    return [node]
```

### 程序化插入reST内容

```python
def run(self):
    # 程序化生成reST内容并解析
    rst_content = StringList()
    rst_content.append('.. note::', '<my-directive>')
    rst_content.append(f'   This is auto-generated content with {title}', '<my-directive>')
    container = nodes.container()
    self.state.nested_parse(rst_content, 0, container)
    return container.children
```

### 无内容的指令

```python
class SimpleDirective(Directive):
    has_content = False
    required_arguments = 1

    def run(self):
        value = self.arguments[0]
        return [nodes.emphasis(text=value)]
```

## 相关参考

- 扩展开发指南 — 扩展基础
- [组件注册表](../concepts/06-registry.md) — add_node和add_directive
- 03-事件处理模式 — 结合事件使用指令
