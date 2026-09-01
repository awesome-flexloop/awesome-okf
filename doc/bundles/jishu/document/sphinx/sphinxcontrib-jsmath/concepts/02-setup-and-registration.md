---
type: Concept
title: 扩展注册与 setup 函数
description: sphinxcontrib-jsmath 的 setup 函数逐行解析、add_html_math_renderer API、扩展元数据返回值
tags: [sphinxcontrib-jsmath, setup, registration, api, sphinx-extension, add_html_math_renderer]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 扩展注册与 setup 函数

## setup 函数是 Sphinx 扩展的入口

每个 Sphinx 扩展都必须定义一个 `setup(app)` 函数，它在扩展被加载时由 Sphinx 调用。`setup` 函数接收一个 `Sphinx` 应用对象作为参数，通过调用该对象的方法来注册扩展的各种功能（指令、角色、配置项、事件回调、转换器等）。

sphinxcontrib-jsmath 的 `setup` 函数是 Sphinx 扩展最小实现的典范——仅 13 行代码完成了全部注册工作：

```python
def setup(app: Sphinx) -> dict[str, Any]:
    app.require_sphinx('5.0')                                    # ①
    app.add_message_catalog(__name__, path.join(package_dir, 'locales'))  # ②
    app.add_html_math_renderer('jsmath',                         # ③
                               (html_visit_math, None),
                               (html_visit_displaymath, None))
    app.add_config_value('jsmath_path', '', False)               # ④
    app.connect('env-updated', install_jsmath)                   # ⑤
    return {                                                     # ⑥
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

下面逐行解析这 6 个注册动作。

## ① 版本要求声明

```python
app.require_sphinx('5.0')
```

`require_sphinx(version)` 声明扩展要求的最低 Sphinx 版本。如果运行环境中的 Sphinx 版本低于指定版本，Sphinx 会在启动时抛出 `VersionRequirementError`，阻止构建继续进行。

sphinxcontrib-jsmath 要求 Sphinx >= 5.0，这是因为从 2.0.0 版本开始它移除了对 Python 3.5-3.8 和旧版 Sphinx 的支持。

## ② 国际化消息目录注册

```python
app.add_message_catalog(__name__, path.join(package_dir, 'locales'))
```

`add_message_catalog(package_name, locale_dir)` 注册一个 gettext 消息目录，使扩展中的用户可见字符串支持多语言翻译。

- 第一个参数 `__name__` 即 `'sphinxcontrib.jsmath'`，作为消息域（message domain）
- 第二个参数指向扩展包内的 `locales/` 目录，其中包含 `.mo` 编译后的翻译文件

本扩展唯一需要翻译的字符串是 "Permalink to this equation"（公式永久链接的 `title` 属性）。该字符串通过 `_('Permalink to this equation')` 标记为可翻译。

## ③ HTML 数学渲染器注册（核心）

```python
app.add_html_math_renderer('jsmath',
                           (html_visit_math, None),
                           (html_visit_displaymath, None))
```

`add_html_math_renderer(name, inline_visitors, block_visitors)` 是本扩展最核心的 API 调用。它向 Sphinx 注册一个**命名的 HTML 数学渲染器**。

### 参数详解

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 渲染器名称，如 `'jsmath'`。用户在 `conf.py` 中通过设置某个配置来选择使用哪个渲染器 |
| `inline_visitors` | `tuple[callable, callable]` | 行内数学（`nodes.math`）的访问者元组：`(visit_func, depart_func)` |
| `block_visitors` | `tuple[callable, callable]` | 块级数学（`nodes.math_block`）的访问者元组：`(visit_func, depart_func)` |

### 为什么 depart_func 是 None？

元组第二个元素 `None` 表示没有 depart 函数。docutils 的 visitor 模式通常是成对的：`visit_xxx` 在进入节点时调用，`depart_xxx` 在离开节点时调用。对于数学节点，sphinxcontrib-jsmath 在 visit 函数中直接输出完整的 HTML 标签并 `raise nodes.SkipNode`，因此不需要 depart 函数——`SkipNode` 异常会跳过子节点遍历和 depart 调用。

### 多个渲染器如何选择？

Sphinx 内置了 mathjax 渲染器。当安装多个 math renderer 扩展后，Sphinx 通过内部机制选择渲染器。`app.builder.math_renderer_name` 属性在构建时确定当前使用的渲染器名称，install_jsmath 回调会检查此值来决定是否加载 JS（详见[智能JS加载机制](04-smart-js-loading.md)）。

## ④ 配置值注册

```python
app.add_config_value('jsmath_path', '', False)
```

`add_config_value(name, default, rebuild)` 向 Sphinx 添加一个新的配置项，用户可以在 `conf.py` 中设置。

| 参数 | 说明 |
|------|------|
| `name` | 配置项名称，即 `jsmath_path` |
| `default` | 默认值，空字符串 `''`。空字符串在 install_jsmath 中被视为"未配置"，会抛出错误 |
| `rebuild` | 重建触发条件。`False`（即 `''`）表示修改此配置不需要触发完整重建；`'html'` 表示修改后需要重新构建 HTML；`'env'` 表示需要重新读取环境 |

`rebuild` 参数的取值含义：
- `False` / `''`：不触发重建
- `'html'`：HTML 文件需要重写
- `'env'`：整个 build environment 需要重建（代价最高）
- `'all'`：所有输出需要完全重建

## ⑤ 事件连接

```python
app.connect('env-updated', install_jsmath)
```

`connect(event, callback)` 将扩展函数连接到 Sphinx 事件系统。当指定事件触发时，回调函数被调用。

`env-updated` 事件在 build environment 更新完成后触发（所有源文件已读取和解析完毕），此时 Sphinx 知道文档中是否包含数学公式，适合做条件性的资源添加。

为什么不在 `setup` 中直接 `add_js_file`？因为：
1. `setup` 执行时还未读取源文件，不知道文档是否有公式
2. 非 HTML 构建（如 LaTeX、PDF）不需要 jsMath
3. 只有当前 math renderer 是 'jsmath' 时才应加载

## ⑥ 扩展元数据返回

```python
return {
    'version': __version__,
    'parallel_read_safe': True,
    'parallel_write_safe': True,
}
```

`setup` 函数返回一个字典，包含扩展的元数据：

| 键 | 类型 | 说明 |
|----|------|------|
| `version` | `str` | 扩展版本号，用于扩展依赖检查和日志 |
| `parallel_read_safe` | `bool` | 是否支持并行读取（`sphinx-build -j auto`）。`True` 表示扩展在读取源文件阶段无共享状态，可安全并行 |
| `parallel_write_safe` | `bool` | 是否支持并行写入。`True` 表示扩展在写入输出文件阶段无全局副作用 |

### 为什么 parallel_read_safe 是 True？

sphinxcontrib-jsmath 满足并行安全条件：
- 不修改全局/共享状态
- visit 函数只操作传入的 `self`（HTMLTranslator 实例），每个线程/进程有独立实例
- `install_jsmath` 虽然在 `env-updated` 中操作 builder，但 env-updated 在单线程中执行

## 扩展的完整注册流程

当 Sphinx 加载 sphinxcontrib-jsmath 时，实际执行流程：

```
Sphinx 启动
  ↓
读取 conf.py，发现 'sphinxcontrib.jsmath' 在 extensions 列表中
  ↓
import sphinxcontrib.jsmath
  ↓
调用 setup(app)
  ├─ require_sphinx('5.0') → 版本检查
  ├─ add_message_catalog(...) → 注册翻译
  ├─ add_html_math_renderer(...) → 注册 math visitor
  ├─ add_config_value(...) → 注册 jsmath_path 配置
  └─ connect('env-updated', install_jsmath) → 注册事件回调
  ↓
构建过程中...
  ├─ 解析 rst 文件，遇到 math/math_block 节点
  ├─ HTML 写入时，调用注册的 visit 函数生成 HTML
  └─ env-updated 事件 → install_jsmath() → 条件添加 JS 文件
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [数学节点访问者](03-math-node-visitors.md)
- [智能JS加载机制](04-smart-js-loading.md)
- [国际化与并行安全](05-i18n-and-parallel.md)
- [源码信源登记](../references/jsmath-source.md)
