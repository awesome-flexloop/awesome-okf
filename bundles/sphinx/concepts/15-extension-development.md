---
type: "concept"
title: "扩展开发详解"
description: "Sphinx扩展开发完整指南——setup函数规范、add_*注册API详解、自定义Directive/Role/Node/Transform/Domain/Builder开发模式、Entry Points分发"
tags: [advanced, extension-development, plugin, API, custom-directive]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: extension-setup
    resource: /references/extension-setup.md
    title: "扩展setup函数签名与返回值"
  - id: registry-py
    resource: sphinx/registry.py
    title: "SphinxComponentRegistry"
---

# 扩展开发详解

Sphinx扩展是Python模块，通过`setup(app)`函数向Sphinx注册组件。扩展机制是Sphinx强大可定制性的根基——几乎Sphinx的所有内置功能（包括核心domain、builder、transform）都以扩展形式加载。

## 扩展的基本结构

### 最小扩展

```python
# my_extension.py
def setup(app):
    # 注册组件...
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

然后在conf.py中启用：
```python
extensions = ['my_extension']
```

### setup 返回值

setup函数必须返回一个字典（ExtensionMetadata），包含 [F-062]：

| 键 | 类型 | 默认值 | 说明 |
|----|------|-------|------|
| `version` | `str` | `'unknown version'` | 扩展版本 |
| `parallel_read_safe` | `bool \| None` | `None` | 是否支持并行读取。None会触发警告 |
| `parallel_write_safe` | `bool` | `True` | 是否支持并行写入 |

### 扩展作为包

大型扩展通常组织为Python包：

```
my_extension/
├── __init__.py      # 包含setup()函数
├── directives.py    # 自定义指令
├── roles.py         # 自定义角色
├── nodes.py         # 自定义节点
└── ...
```

## 扩展API分类

Sphinx通过`app`对象提供的扩展API可分为以下几类：

### 1. 配置类

```python
app.add_config_value(name, default, rebuild, types=Any, description='')
```

注册配置项。`rebuild`参数决定配置变更时需要重建的范围：
- `''`：不影响构建
- `'env'`：需要重新读取所有文档
- `'html'`：只需要重新生成HTML
- `'epub'`/`'gettext'`：只影响特定输出格式

### 2. 事件类

```python
listener_id = app.connect(event, callback, priority=500)
app.disconnect(listener_id)
results = app.emit(event, *args, allowed_exceptions=())
first_result = app.emit_firstresult(event, *args, allowed_exceptions=())
```

详见[事件系统](05-event-system.md)。

### 3. 组件注册类

```python
app.add_builder(builder_cls, override=False)
app.add_domain(domain_cls, override=False)
app.add_directive(name, directive_cls, override=False)
app.add_role(name, role_fn, override=False)
app.add_generic_role(name, nodeclass, override=False)
app.add_transform(transform_cls)
app.add_post_transform(transform_cls)
app.add_node(node, **kwargs)              # kwargs为builder名→(visit, depart)
app.add_enumerable_node(node, figtype, title_getter=None, override=False)
app.add_translator(name, translator_cls, override=False)
app.add_source_parser(parser_cls, override=False)
```

### 4. 域内组件注册

```python
app.add_directive_to_domain(domain, name, cls, override=False)
app.add_role_to_domain(domain, name, role, override=False)
app.add_index_to_domain(domain, index_cls, override=False)
app.add_object_type(directivename, rolename, indextemplate='', ...)
app.add_crossref_type(directivename, rolename, indextemplate='', ...)
```

### 5. 资源注册类

```python
app.add_js_file(filename, priority=500, loading_method=None, **kwargs)
app.add_css_file(filename, priority=500, **kwargs)
app.add_latex_package(packagename, options=None, after_hyperref=False)
app.add_static_dir(path)
app.add_html_theme(name, theme_path)
```

### 6. 扩展管理

```python
app.setup_extension(extname)  # 加载另一个扩展（声明依赖）
app.require_sphinx(version)   # 要求最低Sphinx版本
```

## 自定义指令（Directive）

Sphinx指令继承自docutils的`Directive`或Sphinx的`SphinxDirective`：

```python
from docutils.parsers.rst import Directive
from sphinx.util.docutils import SphinxDirective

class MyDirective(SphinxDirective):
    """自定义指令示例"""
    required_arguments = 1      # 必填参数数量
    optional_arguments = 0      # 可选参数数量
    final_argument_whitespace = False  # 最后一个参数是否可含空格
    option_spec = {             # 选项规范
        'caption': directives.unchanged,
        'width': directives.length_or_percentage_or_unitless,
        'name': directives.unchanged,
    }
    has_content = True          # 是否有内容块

    def run(self):
        # self.arguments: 参数列表
        # self.options: 选项字典
        # self.content: 内容行列表
        # self.env: BuildEnvironment
        # self.config: Config
        # self.state: docutils state

        # 创建节点
        node = nodes.container()
        node['classes'] = ['my-directive']

        # 解析内容
        text = '\n'.join(self.content)
        paragraph = nodes.paragraph(text=text)
        node.append(paragraph)

        return [node]

# 注册
def setup(app):
    app.add_directive('my-directive', MyDirective)
    return {'version': '1.0', 'parallel_read_safe': True}
```

使用方式：
```rst
.. my-directive:: argument_value
   :caption: 标题
   :width: 80%

   这是指令内容。
```

### ObjectDescription：描述对象的基类

对于需要描述代码对象（类似`.. py:function::`）的指令，继承`ObjectDescription`：

```python
from sphinx.directives import ObjectDescription

class MyLangFunction(ObjectDescription):
    """描述自定义语言函数的指令"""

    def handle_signature(self, sig, signode):
        """解析签名，添加到signode，返回标识字符串"""
        signode += addnodes.desc_name(text=sig)
        return sig

    def add_target_and_index(self, name, sig, signode):
        """添加引用目标和索引项"""
        signode['ids'].append(f'mylang-{name}')
        self.env.get_domain('mylang').note_object(name, self.env.docname)

    def run(self):
        # 标准处理流程
        return super().run()
```

## 自定义角色（Role）

角色是行内标记，用于引用或格式化文本：

```python
from docutils.nodes import literal, reference, make_id
from sphinx.util.nodes import split_explicit_title

def my_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    Args:
        name: 角色全名（如'my:role'）
        rawtext: 原始文本（含标记）
        text: 角色内容（反引号内的文本）
        lineno: 行号
        inliner: docutils inliner对象
        options: 选项字典
        content: 内容列表

    Returns:
        (list_of_nodes, list_of_messages)
    """
    # 支持显式标题 `显示文本 <target>`_
    has_explicit_title, title, target = split_explicit_title(text)

    # 创建节点
    if target.startswith('http'):
        node = reference(title, title, refuri=target)
    else:
        node = literal(title, title)

    return [node], []

# 注册
def setup(app):
    app.add_role('myrole', my_role)
    return {'version': '1.0'}
```

### XRefRole：交叉引用角色

对于需要解析交叉引用的角色，使用`XRefRole`：

```python
from sphinx.roles import XRefRole

class MyXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        # 处理链接，可以修改refnode属性
        refnode['reftype'] = 'myobj'
        refnode['refdomain'] = 'mylang'
        return title, target
```

## 自定义节点（Node）

自定义节点继承docutils节点类型：

```python
from docutils import nodes

class my_node(nodes.General, nodes.Element):
    """自定义节点"""
    pass

# visit/depart函数
def visit_my_node_html(self, node):
    self.body.append('<div class="my-node">')

def depart_my_node_html(self, node):
    self.body.append('</div>')

def visit_my_node_latex(self, node):
    self.body.append('\\mynode{')

def depart_my_node_latex(self, node):
    self.body.append('}')

def visit_my_node_text(self, node):
    # 纯文本输出：跳过子节点
    raise nodes.SkipNode

# 注册节点（为每个需要支持的builder提供visit/depart）
def setup(app):
    app.add_node(my_node,
                 html=(visit_my_node_html, depart_my_node_html),
                 latex=(visit_my_node_latex, depart_my_node_latex),
                 text=(visit_my_node_text, None))
    return {'version': '1.0'}
```

## 自定义Transform

Transform在文档解析后修改doctree：

```python
from sphinx.transforms import SphinxTransform
from sphinx import addnodes

class MyTransform(SphinxTransform):
    default_priority = 500  # 执行顺序

    def apply(self, **kwargs):
        # 遍历文档中的特定节点
        for node in self.document.findall(nodes.paragraph):
            # 修改节点...
            if 'TODO' in node.astext():
                warning = nodes.warning()
                warning += nodes.paragraph(text='TODO found')
                node.replace_self([warning, node])

class MyPostTransform(SphinxPostTransform):
    default_priority = 500
    builders = ('html',)  # 仅在特定builder上运行

    def apply(self, **kwargs):
        pass

# 注册
def setup(app):
    app.add_transform(MyTransform)
    app.add_post_transform(MyPostTransform)
    return {'version': '1.0'}
```

## 扩展间依赖

使用`app.setup_extension()`声明对其他扩展的依赖：

```python
def setup(app):
    app.setup_extension('sphinx.ext.autodoc')  # 确保autodoc已加载
    app.connect('autodoc-process-docstring', my_handler)
    return {'version': '1.0', 'parallel_read_safe': True}
```

`setup_extension`是幂等的——重复调用不会重复加载。

## Entry Points 分发

通过Python包的entry points，扩展可以自动注册，无需用户在`extensions`中手动添加：

```toml
# pyproject.toml
[project.entry-points."sphinx.builders"]
mybuilder = "my_extension.builders:MyBuilder"

[project.entry-points."sphinx.extensions"]
my_extension = "my_extension"
```

支持的entry points group：
- `sphinx.builders`：Builder类
- `sphinx.domains`：Domain类
- `sphinx.extensions`：扩展模块（自动加载）
- `sphinx.html_themes`：HTML主题

## 扩展调试技巧

1. **使用`-vvv`参数**：增加日志详细程度，查看扩展加载和事件触发
2. **使用`sphinx-build -E`**：清除缓存，强制全量重建
3. **在事件回调中打印调试信息**：使用`sphinx.util.logging`的logger
4. **使用`-W`参数**：将警告转为错误，发现潜在问题
5. **doctree检查**：使用`sphinx.ext.doctest`或输出XML builder检查doctree结构

## 相关概念

- [Sphinx应用类](03-application-class.md)
- [组件注册中心](06-registry.md)
- [事件系统](05-event-system.md)
- [Domain 领域系统](09-domain-system.md)
- [编写第一个Sphinx扩展](../examples/01-first-extension.md)
