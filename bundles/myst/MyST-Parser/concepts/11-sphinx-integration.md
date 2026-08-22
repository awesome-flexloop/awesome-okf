---
type: Concept
title: Sphinx 集成机制
description: setup_sphinx() 注册流程、source_suffix/source_parser、配置值注册、事件连接
tags: [myst, sphinx, integration, setup, extension, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## Sphinx 集成机制

MyST-Parser 通过 `setup_sphinx()` 函数与 Sphinx 集成，该函数可以独立调用（被 MyST-NB 等外部包复用），也可以通过 `__init__.py` 的 `setup()` 入口调用。

## setup() 入口

Sphinx 加载扩展时调用 `setup(app)`：

```python
def setup(app):
    from myst_parser.sphinx_ext.main import setup_sphinx
    setup_sphinx(app, load_parser=True)
    return {"version": __version__, "parallel_read_safe": True}
```

返回值：
- `version`：扩展版本号（"5.1.0"）
- `parallel_read_safe`：True（支持并行读取）

## setup_sphinx() 注册流程

`setup_sphinx(app, load_parser=False)` 执行以下注册：

### 1. 源文件与解析器注册

当 `load_parser=True` 时：

```python
app.add_source_suffix(".md", "markdown")
app.add_source_parser(MystParser)
```

- 将 `.md` 后缀关联到 `"markdown"` 源类型
- 注册 `MystParser` 作为 `"markdown"` 类型的解析器
- `MystParser.supported = ("md", "markdown", "myst")` 支持三个别名

外部包（如 MyST-NB）调用 `setup_sphinx(app, load_parser=False)` 可以只注册其他组件而不注册 .md 解析器（避免冲突）。

### 2. 指令与角色注册

```python
app.add_role("sub-ref", SubstitutionReferenceRole())
app.add_directive("figure-md", FigureMarkdown)
```

- `sub-ref` 角色：替换引用（docutils 原生未实现 substitution_reference 角色）
- `figure-md` 指令：Markdown 友好的图片指令，支持 HTML `<img>` 标签和 Markdown 格式图注

### 3. Transform 注册

```python
# 替换 Sphinx 内置的脚注检测 Transform
app.registry.transforms.remove(SphinxUnreferencedFootnotesDetector)
app.add_transform(UnreferencedFootnotesDetector)

# 注册引用解析 Post-Transform（优先级 9，高于默认 10）
app.add_post_transform(MystReferenceResolver)
```

`UnreferencedFootnotesDetector` 替换 Sphinx 内置版本以修复 PR #12730 中的问题。

### 4. 节点覆盖

```python
app.add_node(
    nodes.container,
    override=True,
    html=(visit_container_html, depart_container_html),
)
```

覆盖 `nodes.container` 的 HTML 访问方法，对 `is_div=True` 的容器移除 `"container"` CSS 类，避免 Bootstrap 等 CSS 框架的样式冲突。

### 5. 配置值自动注册

```python
for name, default, field in MdParserConfig().as_triple():
    if "sphinx" not in field.metadata.get("omit", []):
        app.add_config_value(f"myst_{name}", default, "env", types=Any)
```

遍历 `MdParserConfig` 的所有字段，自动注册为 Sphinx 配置值：
- 配置名加 `myst_` 前缀
- 默认值来自 dataclass 字段默认值
- 重建级别为 `"env"`（环境变更时触发全量重建）
- 标记了 `omit=["sphinx"]` 的字段（如 `suppress_warnings`、`highlight_code_blocks`、`inventories`）不注册

### 6. 事件连接

```python
app.connect("builder-inited", create_myst_config)
app.connect("builder-inited", override_mathjax)
```

- `create_myst_config`：在 builder 初始化时从 `app.config` 读取所有 `myst_*` 值创建 `MdParserConfig`，存入 `app.env.myst_config`
- `override_mathjax`：当启用 dollarmath 扩展时，配置 MathJax 忽略 `$` 定界符（避免 MathJax 与 MyST 重复处理数学公式）

## builder-inited 配置创建

`create_myst_config(app)` 在 builder 初始化时执行：

```python
def create_myst_config(app):
    values = {
        name: app.config[f"myst_{name}"]
        for name, _, field in MdParserConfig().as_triple()
        if "sphinx" not in field.metadata.get("omit", [])
    }
    try:
        app.env.myst_config = MdParserConfig(**values)
    except (TypeError, ValueError) as error:
        logger.error("myst configuration invalid: %s", error.args[0])
        app.env.myst_config = MdParserConfig()  # 回退默认配置
```

还执行两项警告检查：
- `attrs_image` 扩展已弃用，建议使用 `attrs_inline`
- `linkify` 扩展需要 `linkify-it-py` 包，未安装则警告

## MathJax 配置覆盖

当 `myst_update_mathjax=True`（默认）且启用了 dollarmath 扩展时，`override_mathjax()` 会修改 Sphinx 的 MathJax 配置，将 `$` 从 MathJax 的行内数学定界符中移除，避免 MathJax 和 MyST 双重处理 `$...$` 公式。

还会将 `myst_mathjax_classes`（默认 `"tex2jax_process|mathjax_process|math|output_area"`）添加到 MathJax 处理的类列表中。

## RST include Markdown

在 RST 文件中可以通过 include 指令引入 Markdown 文件：

```rst
.. include:: path/to/file.md
   :parser: myst_parser.sphinx_
```

`myst_parser/sphinx_.py` 文件将 `MystParser` 别名为 `Parser`，使得 `myst_parser.sphinx_` 可以作为 parser 参数值。

## 并行安全

MyST-Parser 标记为 `parallel_read_safe=True`，支持 Sphinx 的并行读取（`sphinx-build -j N`）。但不标记 `parallel_write_safe`（因为 SphinxRenderer 可能依赖全局状态）。

## 扩展点总结

| 注册类型 | API | 注册内容 |
|---------|-----|---------|
| Source Suffix | `app.add_source_suffix()` | `.md` → "markdown" |
| Source Parser | `app.add_source_parser()` | MystParser |
| Role | `app.add_role()` | sub-ref |
| Directive | `app.add_directive()` | figure-md |
| Transform | `app.add_transform()` | UnreferencedFootnotesDetector |
| Post-Transform | `app.add_post_transform()` | MystReferenceResolver (priority=9) |
| Node Override | `app.add_node(override=True)` | nodes.container HTML visit/depart |
| Config Value | `app.add_config_value()` | 30+ myst_* 配置项 |
| Event | `app.connect()` | builder-inited → create_myst_config/override_mathjax |

## 相关概念

- [MyST-Parser 简介](/concepts/00-introduction.md)
- [三阶段解析管线](/concepts/03-architecture-pipeline.md)
- [配置系统](/concepts/04-config-system.md)
- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [数学公式与 MathJax](/concepts/13-math-and-mathjax.md)
- [基础配置示例](/examples/01-basic-setup.md)
