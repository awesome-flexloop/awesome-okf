---
type: Concept
title: 指令与角色
description: MyST 中使用指令（Directive）和角色（Role）的语法、Mock 桥接机制、自定义指令注册
tags: [myst, sphinx, directive, role, mock, bridge, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 指令与角色

指令（Directive）和角色（Role）是 docutils/Sphinx 生态中扩展 Markdown 表达力的核心机制。MyST-Parser 通过 Mock 桥接层复用 docutils 的指令/角色基础设施，使得 MyST Markdown 可以直接使用生态中所有已注册的指令和角色。

## 指令语法

### 反引号围栏语法

````markdown
```{directivename} 参数
:option1: 值1
:option2: 值2

指令内容（支持 Markdown 格式）
```
````

### 冒号围栏语法（需启用 colon_fence）

```markdown
:::{directivename} 参数
:option: 值

内容
:::
```

冒号围栏支持任意深度嵌套：

````markdown
::::{important}
外层提示
:::{note}
嵌套提示
```python
print("代码块")
```
:::
::::
````

### 常用指令示例

```markdown
```{note} 注意标题
这是注意内容，支持 **Markdown** 格式。
```

```{warning}
这是警告内容。
```

```{image} _static/logo.png
:alt: Logo
:width: 200px
```

```{figure} _static/diagram.png
:align: center
:width: 80%

图注文本，支持 *斜体*。
```

```{code-block} python
:linenos:
:emphasize-lines: 2,4

def hello():
    print("Hello")    # 此行高亮
    return True
```

```{eval-rst}
.. note::

   这里面可以写原生 RST 内容
```

```{list-table} 标题
:header-rows: 1

* - 列1
  - 列2
* - A
  - B
```

```{include} subpage.md
```

```{figure-md} my-figure
<img src="img/fun-fish.png" alt="fish" width="200px">

这是 **Markdown** 格式的图注
```
```

## 角色语法

### 基本格式

```markdown
{role-name}`文本内容`
```

### 常用角色

```markdown
{math}`E=mc^2`                     — 行内数学公式
{py:func}`print`                   — Python 函数交叉引用
{py:class}`list`                   — Python 类交叉引用
{doc}`/other-page`                 — 文档引用
{ref}`my-label`                    — 标签引用
{abbr}`CSS (Cascading Style Sheets)` — 缩写
{sub-ref}`variable_name`           — 替换引用
{download}`file.pdf`               — 下载链接
```

### 嵌套语法

角色文本内可以嵌套其他行内 Markdown 语法：

```markdown
{ref}`[**粗体链接**](my-label)`
```

## Mock 桥接机制

MyST-Parser 没有重新实现指令/角色解析逻辑，而是通过 `mocking.py` 中的 Mock 对象模拟 RST 解析器的状态接口，直接复用 docutils 的指令/角色系统。

### 核心 Mock 类

| Mock 类 | 模拟对象 | 作用 |
|---------|---------|------|
| `MockState` | docutils.statemachine.State | RST 解析状态，提供 nested_parse 方法 |
| `MockInliner` | docutils.parsers.rst.states.Inliner | 行内解析器 |
| `MockStateMachine` | docutils.statemachine.StateMachine | 状态机 |
| `MockRSTParser` | docutils.parsers.rst.Parser | RST 解析器 |
| `MockIncludeDirective` | docutils Include 指令 | include 指令适配 |

### 工作原理

1. 渲染器遇到 MyST 指令 Token 时，创建 `MockState`（持有对渲染器的引用）
2. 解析指令参数和选项（使用 `parse_directive_text()`）
3. 从 docutils 指令注册表查找指令类（`directives.directive()`）
4. 通过 `MockState.nested_parse()` 将指令内容递归渲染为 docutils 节点
5. 指令类的 `run()` 方法返回节点列表，添加到当前节点

这意味着任何通过 `app.add_directive()` 注册的 Sphinx 指令在 MyST Markdown 中立即可用，无需额外适配。

## 自定义指令（figure-md）

MyST-Parser 自带一个 Markdown 友好的图片指令 `figure-md`：

```python
class FigureMarkdown(SphinxDirective):
    required_arguments = 0
    optional_arguments = 1
    has_content = True
    option_spec = {
        "width": figwidth_value,
        "class": directives.class_option,
        "align": align,
        "name": directives.unchanged,
    }
```

`figure-md` 指令在运行时临时启用 `html_image` 扩展解析 HTML `<img>` 标签，然后将图片和后续段落组合为 `nodes.figure`。

## 自定义角色（sub-ref）

MyST-Parser 注册了 `sub-ref` 角色处理替换引用：

```python
class SubstitutionReferenceRole(SphinxRole):
    def run(self):
        subref_node = nodes.substitution_reference(self.rawtext, self.text)
        subref_node["refname"] = nodes.fully_normalize_name(self.text)
        return [subref_node], []
```

## 相关概念

- [MyST 语法概览](/concepts/02-myst-syntax-overview.md)
- [扩展语法系统](/concepts/05-extension-system.md)
- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [交叉引用](/concepts/08-cross-references.md)
- [基础配置示例](/examples/01-basic-setup.md)
