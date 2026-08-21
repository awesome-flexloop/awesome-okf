---
type: "example"
title: "编写第一个Sphinx扩展"
description: "从零编写一个Sphinx扩展——创建扩展模块、实现setup函数、注册配置项、订阅事件、添加简单指令，完整可运行示例"
tags: [example, extension, hello-world, setup]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: extension-setup
    resource: /references/extension-setup.md
    title: "扩展setup函数签名与返回值"
  - id: events
    resource: /references/event-lifecycle.md
    title: "核心事件列表与触发时机"
---

# 编写第一个Sphinx扩展

本示例将引导你从零开始编写一个简单的Sphinx扩展，展示扩展的基本结构和常用API。我们将创建一个"Hello World"扩展，它会在构建时打印问候信息，并添加一个 `.. hello::` 指令。

## 前置知识

- 已安装Sphinx 9.1.1（Python ≥ 3.12）
- 了解Python基础和reStructuredText语法
- 已阅读 [Sphinx 简介](../concepts/00-introduction.md) 和 [扩展开发详解](../concepts/15-extension-development.md)

## 步骤1：创建扩展模块

在你的Sphinx项目中创建一个Python文件，例如 `_ext/hello.py`：

```
mydocs/
├── conf.py
├── index.rst
└── _ext/
    └── hello.py    # ← 我们的扩展
```

## 步骤2：编写最小扩展框架

```python
# _ext/hello.py
"""Hello World extension for Sphinx."""

def setup(app):
    """扩展入口函数。Sphinx在加载扩展时调用此函数。"""
    print("Hello Sphinx! 扩展已加载。")
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

setup函数是扩展的唯一入口。它接收Sphinx应用实例 `app` 作为参数，通过 `app` 的各种方法注册组件。返回值是扩展元数据字典。

## 步骤3：注册配置项

给扩展添加一个可配置的选项——问候语目标：

```python
# _ext/hello.py
from docutils import nodes
from docutils.parsers.rst import Directive

def setup(app):
    # 注册配置项
    app.add_config_value(
        name='hello_target',       # 配置项名称
        default='World',           # 默认值
        rebuild='html',            # 变更时重建级别
        types=(str,),              # 有效值类型
    )

    print(f"Hello {app.config.hello_target}! 扩展已加载。")

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

在conf.py中可以覆盖默认值：

```python
# conf.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '_ext'))

extensions = ['hello']
hello_target = 'Sphinx Users'
```

## 步骤4：订阅构建事件

通过事件系统在构建过程中插入自定义逻辑：

```python
def on_builder_inited(app):
    """Builder初始化完成后执行"""
    print(f"[Hello Extension] 准备构建到: {app.outdir}")

def on_build_finished(app, exception):
    """构建完成后执行"""
    if exception is None:
        print(f"[Hello Extension] 构建成功完成!")
    else:
        print(f"[Hello Extension] 构建出错: {exception}")

def on_source_read(app, docname, source):
    """源文件读取后，打印正在处理的文档"""
    print(f"[Hello Extension] 处理文档: {docname}")

def setup(app):
    app.add_config_value('hello_target', 'World', 'html', (str,))

    # 订阅事件
    app.connect('builder-inited', on_builder_inited)
    app.connect('build-finished', on_build_finished)
    app.connect('source-read', on_source_read)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

运行 `sphinx-build` 时你会看到类似输出：

```
Running Sphinx v9.1.1
Hello Sphinx Users! 扩展已加载。
[Hello Extension] 准备构建到: _build/html
[Hello Extension] 处理文档: index
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 1 source files that are out of date
[Hello Extension] 构建成功完成!
Build succeeded.
```

## 步骤5：添加自定义指令

添加一个 `.. hello::` 指令，在文档中插入一个问候框：

```python
class HelloDirective(Directive):
    """一个简单的hello指令，输出带样式的问候语。"""
    required_arguments = 0          # 不需要参数
    optional_arguments = 1          # 可选一个参数（自定义问候对象）
    final_argument_whitespace = True
    has_content = False             # 不需要内容块

    def run(self):
        # 获取问候对象：指令参数或配置默认值
        if self.arguments:
            target = self.arguments[0]
        else:
            # 通过self.state获取config
            env = self.state.document.settings.env
            target = env.config.hello_target

        # 创建HTML节点
        container = nodes.container(classes=['hello-box'])
        paragraph = nodes.paragraph(
            text=f"👋 Hello, {target}!"
        )
        container += paragraph
        return [container]

def setup(app):
    app.add_config_value('hello_target', 'World', 'html', (str,))
    app.connect('builder-inited', on_builder_inited)
    app.connect('build-finished', on_build_finished)

    # 注册指令
    app.add_directive('hello', HelloDirective)

    # 添加CSS文件来美化问候框
    app.add_css_file('hello.css')

    return {
        'version': '0.2',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

在reST中使用：

```rst
欢迎页面
========

.. hello::

.. hello:: Python Developers
```

创建 `_static/hello.css` 添加样式：

```css
.hello-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin: 1rem 0;
    font-size: 1.1em;
}

.hello-box p {
    margin: 0;
}
```

## 完整扩展代码

```python
# _ext/hello.py
"""Hello World extension for Sphinx - 完整版本."""

from docutils import nodes
from docutils.parsers.rst import Directive


class HelloDirective(Directive):
    """A simple hello directive that outputs a styled greeting."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        env = self.state.document.settings.env
        target = self.arguments[0] if self.arguments else env.config.hello_target

        container = nodes.container(classes=['hello-box'])
        paragraph = nodes.paragraph(text=f"👋 Hello, {target}!")
        container += paragraph
        return [container]


def on_builder_inited(app):
    print(f"[Hello Extension] Building to: {app.outdir}")


def on_build_finished(app, exception):
    if exception is None:
        print("[Hello Extension] Build finished successfully!")
    else:
        print(f"[Hello Extension] Build error: {exception}")


def on_source_read(app, docname, source):
    print(f"[Hello Extension] Processing: {docname}")


def setup(app):
    app.add_config_value('hello_target', 'World', 'html', (str,))
    app.add_directive('hello', HelloDirective)
    app.add_css_file('hello.css')
    app.connect('builder-inited', on_builder_inited)
    app.connect('build-finished', on_build_finished)
    app.connect('source-read', on_source_read)

    return {
        'version': '0.2',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

## 验证

```bash
# 添加_ext目录到path后构建
sphinx-build -b html . _build/html
```

你应该能看到：
1. 控制台输出Hello Extension的调试信息
2. HTML页面中有渐变背景的问候框
3. 自定义参数的指令显示对应问候语

## 下一步

- 学习 [自定义指令和角色](02-custom-directive.md) 的更多技巧
- 阅读 [扩展开发详解](../concepts/15-extension-development.md) 了解完整的API
- 探索 [事件系统](../concepts/05-event-system.md) 的所有可用事件
- 尝试给hello指令添加内容支持和选项
