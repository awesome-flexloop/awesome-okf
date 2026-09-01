---
type: Reference
title: sphinxcontrib-jsmath 源码信源登记
description: sphinx-doc/sphinxcontrib-jsmath 源码路径、版本信息、核心文件清单、API 注册表与模块结构
tags: [sphinxcontrib-jsmath, source, reference, sphinx, math, jsmath]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-github
    resource: https://github.com/sphinx-doc/sphinxcontrib-jsmath
    title: sphinxcontrib-jsmath GitHub 仓库
    author: human:georg-brandl
  - id: jsmath-pypi
    resource: https://pypi.org/project/sphinxcontrib-jsmath/
    title: sphinxcontrib-jsmath on PyPI
---

# sphinxcontrib-jsmath 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | sphinxcontrib-jsmath |
| 包名 | `sphinxcontrib.jsmath` |
| 仓库 | sphinx-doc/sphinxcontrib-jsmath |
| 描述 | A sphinx extension which renders display math in HTML via JavaScript |
| 作者 | Georg Brandl (georg@python.org) |
| 许可证 | BSD 2-Clause License |
| 当前版本 | 1.0.2 |
| 构建后端 | flit_core >= 3.7 |
| Python 要求 | >= 3.9 |
| Sphinx 要求 | >= 5.0 |
| 运行时依赖 | 无（Sphinx 作为可选依赖在 standalone extra 中） |
| 官方仓库 | <https://github.com/sphinx-doc/sphinxcontrib-jsmath> |
| PyPI | <https://pypi.org/project/sphinxcontrib-jsmath/> |

## 源码位置

sphinxcontrib-jsmath 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/docs/sphinxcontrib-jsmath/
```

该目录通过 git submodule 引入，本地不做修改。

## 核心文件清单

| 文件 | 行数 | 说明 |
|------|------|------|
| `sphinxcontrib/jsmath/__init__.py` | 88 | **唯一核心模块**，包含全部扩展逻辑（setup函数、两个访问者函数、JS加载回调） |
| `sphinxcontrib/jsmath/py.typed` | 1 | PEP 561 类型标记文件，声明包内含类型信息 |
| `pyproject.toml` | 106 | 项目元数据、构建配置、mypy 严格类型检查配置 |
| `tests/test_jsmath.py` | 55 | 3个测试用例：基本渲染、numfig编号、无公式时不加载JS |
| `tests/conftest.py` | 14 | pytest 配置，使用 sphinx.testing.fixtures 插件 |
| `tests/roots/test-basic/conf.py` | 4 | 测试配置：启用扩展、设置 jsmath_path |
| `tests/roots/test-basic/index.rst` | 7 | 测试根文档，包含 math.rst 子文档 |
| `tests/roots/test-basic/math.rst` | 18 | 测试数学公式：行内公式、块级公式、带标签公式、split环境 |
| `tests/roots/test-nomath/conf.py` | 4 | 无公式测试配置（同 basic） |
| `tests/roots/test-nomath/index.rst` | 3 | 无公式测试根文档（仅标题） |
| `README.rst` | 22 | 简介和安装说明 |
| `CHANGES.rst` | 21 | 版本变更记录 |
| `LICENCE.rst` | - | BSD 2-Clause 许可证文本 |
| `Makefile` | - | 构建/发布辅助 Makefile |
| `tox.ini` | - | tox 多环境测试配置 |
| `.ruff.toml` | - | Ruff linter 配置 |
| `babel.cfg` | - | Babel 国际化提取配置 |

## 核心模块结构（__init__.py）

### 模块级常量与导入

```python
from __future__ import annotations
from os import path
from typing import TYPE_CHECKING, Any, cast
from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.domains.math import MathDomain
from sphinx.errors import ExtensionError
from sphinx.locale import get_translation
from sphinx.util.math import get_node_equation_number

__version__ = '1.0.2'
__version_info__ = (1, 0, 2)
package_dir = path.abspath(path.dirname(__file__))
_ = get_translation(__name__)
```

### 公共函数一览

| 函数 | 签名 | 作用 |
|------|------|------|
| `html_visit_math` | `(self: HTMLTranslator, node: nodes.math) -> None` | 行内数学节点访问者，输出 `<span class="math">` |
| `html_visit_displaymath` | `(self: HTMLTranslator, node: nodes.math_block) -> None` | 块级数学节点访问者，输出 `<div class="math">`，处理编号和split环境 |
| `install_jsmath` | `(app: Sphinx, env: BuildEnvironment) -> None` | `env-updated` 事件回调，三重条件检查后加载 jsmath.js |
| `setup` | `(app: Sphinx) -> dict[str, Any]` | 扩展入口函数，注册渲染器、配置值、事件和消息目录 |

### setup 函数注册的 API 调用

| API | 参数 | 作用 |
|-----|------|------|
| `app.require_sphinx('5.0')` | 版本字符串 | 声明最低 Sphinx 版本要求 |
| `app.add_message_catalog(__name__, ...)` | 包名、locale 目录路径 | 注册国际化翻译消息目录 |
| `app.add_html_math_renderer('jsmath', ...)` | 渲染器名称、行内访问者元组、块级访问者元组 | 注册名为 'jsmath' 的 HTML 数学渲染器 |
| `app.add_config_value('jsmath_path', '', False)` | 配置名、默认值、重建条件 | 添加 `jsmath_path` 配置项，默认空字符串 |
| `app.connect('env-updated', install_jsmath)` | 事件名、回调函数 | 连接 env-updated 事件到 install_jsmath |

### setup 返回值

```python
{
    'version': __version__,           # '1.0.2'
    'parallel_read_safe': True,       # 支持并行读取
    'parallel_write_safe': True,      # 支持并行写入
}
```

## HTML 输出结构

### 行内数学（`nodes.math`）

```html
<span class="math notranslate nohighlight">公式内容</span>
```

### 块级数学无编号（`nodes.math_block`, nowrap=True）

```html
<div class="math notranslate nohighlight">公式内容</div>
```

### 块级数学有编号（`nodes.math_block`, number=True）

```html
<span class="eqno">(1)<a class="headerlink" href="#equation-label" title="Permalink to this equation">¶</a></span>
<div class="math notranslate nohighlight" id="equation-label">
公式内容
</div>
```

### 块级数学多段落（含 & 或 \\）

```html
<div class="math notranslate nohighlight">
\begin{split}...\end{split}
</div>
```

后续段落输出为 `<div class="math">`（无 `notranslate nohighlight`）。

## 国际化支持

`sphinxcontrib/jsmath/locales/` 目录包含 50+ 语言的翻译文件（.mo/.po），翻译的唯一字符串是 "Permalink to this equation"（公式永久链接的 title 属性）。

## 测试覆盖

| 测试函数 | 测试场景 | 验证内容 |
|---------|---------|---------|
| `test_basic` | 基本渲染 | 无编号公式HTML、有编号公式HTML（含eqno和permalink）、split环境HTML、公式交叉引用 |
| `test_numfig_enabled` | numfig编号 | 启用 `numfig=True, math_numfig=True` 后公式编号格式为 `(章号.序号)` 如 `(1.1)` |
| `test_disabled_when_equations_not_found` | 无公式不加载 | 文档无数学公式时，输出HTML中不包含 `jsmath.js` |
