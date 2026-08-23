---
type: Concept
title: 国际化与并行安全
description: sphinxcontrib-jsmath 的国际化消息目录机制、并行读写安全声明、get_translation 使用方式
tags: [sphinxcontrib-jsmath, i18n, internationalization, translation, parallel-safety, gettext]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 国际化与并行安全

## 国际化（i18n）支持

### get_translation 机制

sphinxcontrib-jsmath 使用 Sphinx 提供的国际化基础设施支持多语言：

```python
from sphinx.locale import get_translation

_ = get_translation(__name__)
```

`get_translation(domain)` 返回一个翻译函数（通常命名为 `_`），它封装了 Python 的 gettext 机制：

1. 在模块加载时调用 `get_translation(__name__)` 获取翻译函数
2. 使用 `_('字符串')` 标记需要翻译的用户可见文本
3. Sphinx 根据当前语言设置查找对应的 `.mo` 翻译文件
4. 如果找到翻译则返回翻译后的字符串，否则返回原始字符串

### 本扩展的翻译内容

sphinxcontrib-jsmath 只有一个需要翻译的用户可见字符串：

```python
self.add_permalink_ref(node, _('Permalink to this equation'))
```

这是公式编号旁边 ¶ 链接的 `title` 属性，当鼠标悬停在永久链接上时显示。虽然只有一个字符串，但扩展包中包含了 50+ 种语言的翻译文件，覆盖了 Sphinx 文档的主要使用语言。

### 消息目录注册

```python
app.add_message_catalog(__name__, path.join(package_dir, 'locales'))
```

这行代码告诉 Sphinx 去哪里查找翻译文件：
- `__name__` 是消息域（message domain），即 `'sphinxcontrib.jsmath'`
- `path.join(package_dir, 'locales')` 指向扩展包内的 `locales/` 目录

目录结构遵循 gettext 标准布局：

```
sphinxcontrib/jsmath/locales/
├── ar/LC_MESSAGES/sphinxcontrib.jsmath.mo    # 阿拉伯语
├── de/LC_MESSAGES/sphinxcontrib.jsmath.mo    # 德语
├── zh_CN/LC_MESSAGES/sphinxcontrib.jsmath.mo # 简体中文
├── zh_TW/LC_MESSAGES/sphinxcontrib.jsmath.mo # 繁体中文
├── ja/LC_MESSAGES/sphinxcontrib.jsmath.mo    # 日语
└── ...（50+ 种语言）
```

- `.po` 文件是可编辑的翻译源文件（Portable Object）
- `.mo` 文件是编译后的机器可读文件（Machine Object），运行时使用
- `.pot` 文件（`sphinxcontrib.jsmath.pot`）是翻译模板，包含所有需要翻译的字符串

### Babel 配置

`babel.cfg` 文件配置了 Babel（Python 国际化工具）如何从源码中提取可翻译字符串：

```ini
# babel.cfg（项目根目录）
[python: **.py]
encoding = utf-8
```

这个配置告诉 Babel 扫描所有 `.py` 文件，提取被 `_()` 包裹的字符串。

### Transifex 集成

`.github/workflows/transifex.yml` 表明项目使用 [Transifex](https://www.transifex.com/) 平台进行协作翻译。社区译者可以在 Transifex 上贡献翻译，GitHub Actions 自动同步翻译文件。

## 并行安全

### parallel_read_safe

```python
'parallel_read_safe': True,
```

`parallel_read_safe: True` 声明扩展在**源文件读取阶段**支持并行执行（`sphinx-build -j auto`）。

Sphinx 的并行构建分为两个阶段：
1. **并行读取阶段**：多个 worker 进程并行读取和解析源文件
2. **串行写入阶段**：通常单进程写入输出文件（某些 builder 支持并行写入）

在读取阶段，每个 worker 处理独立的源文件，生成各自的 doctree。扩展的 visit 函数在写入阶段调用，但 `doctree-resolved` 等读取阶段的事件回调可能在多进程环境中执行。

sphinxcontrib-jsmath 满足并行读取安全的条件：
- 不使用模块级全局变量存储可变状态
- visit 函数只操作传入的 `self`（HTMLTranslator 实例），每个进程有独立实例
- `install_jsmath` 在 `env-updated` 中执行，该事件在读取阶段结束后的单线程阶段触发
- 不修改共享的环境数据（除了通过 Sphinx 提供的 API，这些 API 是并行安全的）

### parallel_write_safe

```python
'parallel_write_safe': True,
```

`parallel_write_safe: True` 声明扩展在**写入阶段**也支持并行执行。

并行写入意味着多个 HTML 页面可以同时生成。这要求：
- visit 函数不使用共享的可变状态
- `add_js_file` 等 builder 方法是线程安全的（由 Sphinx 保证）
- 不依赖写入顺序

sphinxcontrib-jsmath 的 visit 函数满足这些条件，因为它们只追加 `self.body` 列表（每个页面有独立的 HTMLTranslator），不操作跨页面共享状态。

### 并行安全的重要性

如果扩展声明 `parallel_read_safe: False` 或 `parallel_write_safe: False`，当用户使用 `-j` 参数启用并行构建时，Sphinx 会：
1. 发出警告，说明某扩展不支持并行
2. 回退到串行模式（或在读取/写入阶段使用单进程）
3. 显著降低构建速度（尤其对大型文档项目）

因此，声明并行安全不仅是技术正确性问题，也直接影响用户体验。sphinxcontrib-jsmath 作为极简扩展，天然满足并行安全条件。

## 类型注解与 mypy 严格模式

sphinxcontrib-jsmath 使用严格的 mypy 类型检查，pyproject.toml 中的 mypy 配置体现了这一点：

```toml
[tool.mypy]
python_version = "3.9"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_decorators = true
disallow_untyped_defs = true
explicit_package_bases = true
extra_checks = true
no_implicit_reexport = true
strict_optional = true
warn_redundant_casts = true
warn_unused_configs = true
warn_unused_ignores = true
```

这些配置启用了 mypy 最严格的检查级别，包括：
- `disallow_untyped_defs`：所有函数必须有类型注解
- `strict_optional`：`None` 和非 `None` 类型严格区分
- `no_implicit_reexport`：不隐式重新导出导入的名称
- `warn_redundant_casts`：冗余的 `cast()` 调用会产生警告

核心代码中使用了 `TYPE_CHECKING` 条件导入来避免运行时循环导入：

```python
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.writers.html import HTMLTranslator
```

`TYPE_CHECKING` 在静态类型检查时为 `True`，在运行时为 `False`。这使得类型注解可以引用仅用于类型检查的模块，而不会在运行时产生导入开销或循环依赖问题。

函数签名中的类型注解：

```python
def html_visit_math(self: HTMLTranslator, node: nodes.math) -> None:
def html_visit_displaymath(self: HTMLTranslator, node: nodes.math_block) -> None:
def install_jsmath(app: Sphinx, env: BuildEnvironment) -> None:
def setup(app: Sphinx) -> dict[str, Any]:
```

每个函数都标注了参数类型和返回值类型，`self` 参数也显式标注了类型（这是为类型检查器提供的，Python 运行时不需要）。

## py.typed 标记文件

```
sphinxcontrib/jsmath/py.typed
```

这个空文件是 [PEP 561](https://peps.python.org/pep-0561/) 规定的类型包标记。它的存在告诉类型检查器（如 mypy、pyright）：这个包包含内联类型注解，可以对使用该包的代码进行类型检查。

如果一个包没有 `py.typed` 文件，mypy 在严格模式下会报告 "missing imports" 错误，即使包代码中有类型注解。

## 相关概念

- [扩展注册与 setup 函数](/concepts/02-setup-and-registration.md)
- [数学节点访问者](/concepts/03-math-node-visitors.md)
- [智能JS加载机制](/concepts/04-smart-js-loading.md)
- [源码信源登记](/references/jsmath-source.md)
