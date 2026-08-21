---
type: "example"
title: "自定义指令和角色"
description: "实战——创建带选项和内容的自定义Directive、XRefRole交叉引用角色、自定义docutils节点及多格式输出支持"
tags: [example, directive, role, node, custom]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: extension-setup
    resource: /references/extension-setup.md
    title: "扩展setup函数签名与返回值"
---

# 自定义指令和角色

本示例演示如何创建功能完整的自定义指令（Directive）和角色（Role），包括选项处理、内容解析、自定义节点以及多格式输出支持。

## 前置知识

- 完成 [编写第一个Sphinx扩展](01-first-extension.md)
- 了解docutils节点系统，参阅 [项目管理与 Docutils 集成](../concepts/08-project-and-docutils.md)
- 了解SphinxDirective基类和XRefRole类

## 示例1：提示框指令（admonition）

创建一个 `.. note-box::` 指令，支持标题、颜色和图标选项：

```python
# _ext/notebox.py
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective


class note_box(nodes.General, nodes.Element):
    """自定义节点：提示框"""
    pass


class NoteBoxDirective(SphinxDirective):
    """可定制的提示框指令。

    用法：
    .. note-box:: 标题文本
       :type: info|warning|success|danger
       :icon: 💡

       提示内容...
    """
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'type': directives.unchanged,  # info/warning/success/danger
        'icon': directives.unchanged,
        'class': directives.class_option,
    }
    has_content = True

    def run(self):
        # 获取参数
        title = self.arguments[0] if self.arguments else ''
        box_type = self.options.get('type', 'info')
        icon = self.options.get('icon', '')
        extra_classes = self.options.get('class', [])

        # 创建节点
        node = note_box()
        node['box_type'] = box_type
        node['title'] = title
        node['icon'] = icon
        node['classes'] = ['note-box', f'note-box-{box_type}'] + extra_classes

        # 解析内容（支持reST格式）
        if self.content:
            # 用self.parse_content_to_nodes()解析reST内容
            content_node = nodes.container()
            self.state.nested_parse(self.content, self.content_offset, content_node)
            node += content_node
        else:
            # 无内容时创建空段落
            node += nodes.paragraph('')

        # 添加标题
        if title:
            title_node = nodes.paragraph(classes=['note-box-title'])
            if icon:
                title_node += nodes.inline(text=f'{icon} ')
            title_node += nodes.inline(text=title)
            node.insert(0, title_node)

        return [node]
```

## 注册节点的多格式输出

为自定义节点添加HTML和LaTeX输出支持：

```python
def visit_note_box_html(self, node):
    self.body.append(self.starttag(node, 'div', CLASS='note-box'))

def depart_note_box_html(self, node):
    self.body.append('</div>\n')

def visit_note_box_latex(self, node):
    box_type = node['box_type']
    colors = {
        'info': 'blue!10',
        'warning': 'orange!10',
        'success': 'green!10',
        'danger': 'red!10',
    }
    color = colors.get(box_type, 'gray!10')
    self.body.append(f'\n\\begin{{sphinxadmonition}}{{{color}}}{{')
    if node['icon'] or node['title']:
        title = f"{node['icon']} {node['title']}".strip()
        self.body.append(title)
    self.body.append('}\n')

def depart_note_box_latex(self, node):
    self.body.append('\\end{sphinxadmonition}\n')

def visit_note_box_text(self, node):
    self.add_text(f"[{node['box_type'].upper()}] ")

def depart_note_box_text(self, node):
    self.add_text('\n')
```

## 注册指令和节点

```python
def setup(app):
    app.add_directive('note-box', NoteBoxDirective)
    app.add_node(note_box,
                 html=(visit_note_box_html, depart_note_box_html),
                 latex=(visit_note_box_latex, depart_note_box_latex),
                 text=(visit_note_box_text, depart_note_box_text))
    app.add_css_file('notebox.css')
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

## 示例2：交叉引用角色

创建一个自定义角色来引用RFC文档：

```python
from docutils import nodes
from sphinx.util.nodes import split_explicit_title
from urllib.parse import quote


def rfc_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """引用RFC文档的角色。

    用法：
    :rfc:`9110`              → 链接到RFC 9110
    :rfc:`HTTP语义 <9110>`    → 自定义显示文本
    """
    options = options or {}
    has_explicit_title, title, target = split_explicit_title(text)

    if not has_explicit_title:
        # 自动生成标题
        title = f'RFC {target}'

    url = f'https://www.rfc-editor.org/rfc/rfc{target}'
    node = nodes.reference(rawtext, title, refuri=url, **options)
    return [node], []
```

使用XRefRole实现更复杂的交叉引用（需要Domain支持解析）：

```python
from sphinx.roles import XRefRole


class RFCReference:
    """模拟一个简单的RFC索引"""
    _rfcs = {}

    @classmethod
    def add(cls, number, title, docname):
        cls._rfcs[number] = (title, docname)

    @classmethod
    def lookup(cls, number):
        return cls._rfcs.get(number)


class RFCXRefRole(XRefRole):
    """支持交叉引用到文档内RFC描述的角色"""
    def process_link(self, env, refnode, has_explicit_title, title, target):
        # 设置refnode属性供resolve_xref使用
        refnode['reftype'] = 'rfc'
        refnode['refdomain'] = ''  # 使用std域或自定义域
        refnode['reftarget'] = target
        return title, target
```

## 示例3：带Transform的条件内容指令

创建一个 `.. only-output::` 指令，只在特定输出格式中显示内容：

```python
from docutils import nodes
from sphinx.transforms import SphinxTransform
from sphinx.util.docutils import SphinxDirective


class only_output(nodes.General, nodes.Element):
    """条件输出节点"""
    pass


class OnlyOutputDirective(SphinxDirective):
    """只在指定输出格式中显示内容。

    .. only-output:: html

       这段内容只在HTML输出中显示。

    .. only-output:: latex,text

       这段内容在LaTeX和纯文本输出中显示。
    """
    required_arguments = 1
    has_content = True

    def run(self):
        formats = [f.strip() for f in self.arguments[0].split(',')]
        node = only_output()
        node['formats'] = formats
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class OnlyOutputTransform(SphinxTransform):
    """在特定Builder下移除不匹配的only_output节点"""
    default_priority = 500

    def apply(self, **kwargs):
        builder_format = self.app.builder.format
        for node in self.document.findall(only_output):
            if builder_format not in node['formats']:
                # 不匹配的输出格式：移除节点
                node.parent.remove(node)
```

注册：

```python
def setup(app):
    app.add_directive('only-output', OnlyOutputDirective)
    app.add_node(only_output,
                 html=(lambda s, n: None, lambda s, n: None),
                 latex=(lambda s, n: None, lambda s, n: None),
                 text=(lambda s, n: None, lambda s, n: None))
    app.add_transform(OnlyOutputTransform)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

> **注意**：Sphinx内置的 `.. only::` 指令已经提供了类似功能（基于标签），这里仅作演示。

## CSS样式

为note-box添加 `_static/notebox.css`：

```css
.note-box {
    padding: 0.75rem 1rem;
    margin: 1rem 0;
    border-left: 4px solid;
    border-radius: 0 4px 4px 0;
}

.note-box-title {
    font-weight: bold;
    margin-bottom: 0.25rem;
}

.note-box-info {
    background-color: #e7f3ff;
    border-left-color: #2196F3;
}

.note-box-warning {
    background-color: #fff8e1;
    border-left-color: #FFC107;
}

.note-box-success {
    background-color: #e8f5e9;
    border-left-color: #4CAF50;
}

.note-box-danger {
    background-color: #ffebee;
    border-left-color: #f44336;
}
```

## 在reST中使用

```rst
.. note-box:: 提示
   :type: info
   :icon: 💡

   这是一条信息提示。

.. note-box:: 警告
   :type: warning
   :icon: ⚠️

   这个操作不可撤销！

请参阅 :rfc:`9110` 获取HTTP语义规范，
或阅读 :rfc:`HTTP缓存 <9111>`。

.. only-output:: html

   此内容仅在HTML中可见（点击交互等）。
```

## 关键API回顾

| API | 用途 |
|-----|------|
| `SphinxDirective` | 推荐的指令基类（自动注入env/config） |
| `self.state.nested_parse()` | 解析reST格式的内容块 |
| `directives.unchanged` | 选项类型：原样返回字符串 |
| `directives.class_option` | 选项类型：CSS类列表 |
| `directives.flag` | 选项类型：布尔标志（存在即为True） |
| `split_explicit_title()` | 解析 `显示文本 <目标>` 格式 |
| `XRefRole` | 交叉引用角色基类 |
| `nodes.SkipNode` | 在visitor中抛出，跳过子节点 |

## 相关资源

- [编写第一个Sphinx扩展](01-first-extension.md)
- [扩展开发详解](../concepts/15-extension-development.md)
- [项目管理与 Docutils 集成](../concepts/08-project-and-docutils.md)
