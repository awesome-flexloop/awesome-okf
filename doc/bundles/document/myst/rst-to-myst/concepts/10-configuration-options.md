---
type: Concept
title: 转换选项详解
description: rst-to-myst 的所有转换选项的作用、默认值和使用场景。
tags: [configuration, options, conversion-settings, colon-fences, dollar-math]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-cli
    resource: /references/source-cli.md
    title: rst-to-myst CLI 命令行接口
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 选项分类

rst-to-myst 的转换选项可分为以下几类：

| 类别 | 选项 |
|------|------|
| 语言与环境 | `language_code`、`use_sphinx`、`extensions`、`default_domain`、`default_role` |
| 转换行为 | `conversions`、`raise_on_warning`、`front_matter` |
| 输出格式 | `consecutive_numbering`、`colon_fences`、`dollar_math`、`cite_prefix` |
| 输入输出 | `warning_stream`、`encoding`（CLI only） |

## 语言与环境选项

### language_code

- **类型**：`str`
- **默认值**：`"en"`
- **CLI**：`--language/-l`

设置指令和角色名称的语言代码。docutils 和 Sphinx 支持多语言，通过此选项可以加载对应语言的翻译表，将非英语的指令/角色名映射到标准名称。

### use_sphinx

- **类型**：`bool`
- **默认值**：`True`
- **CLI**：`--sphinx/--no-sphinx`

控制是否加载 Sphinx 及其内置扩展。启用后可以识别 Sphinx 特有的指令和角色（如 autoclass、toctree 等）。

**注意**：使用 `--sphinx`（默认）需要安装 sphinx 包，否则 CLI 会报错提示安装或使用 `--no-sphinx`。

```bash
# 不需要 Sphinx 时禁用，减少加载时间
rst2myst convert --no-sphinx docs/
```

### extensions

- **类型**：`Iterable[str]`
- **默认值**：`()`（空元组）
- **CLI**：`--extensions/-e`（逗号分隔列表）

指定额外加载的 Sphinx 扩展列表。扩展会被 import 并调用其 `setup(app)` 函数注册指令和角色。

```bash
rst2myst convert -e sphinx.ext.autodoc,sphinx.ext.todo docs/
```

```python
result = rst_to_myst(text, extensions=["sphinx.ext.autodoc"])
```

### default_domain

- **类型**：`str`
- **默认值**：`"py"`
- **CLI**：`--default-domain/-dd`

设置默认 Sphinx 域。查找指令/角色时，如果名称不含冒号前缀，会先在默认域中查找。例如默认域为 `py` 时，`class` 指令等价于 `py:class`。

### default_role

- **类型**：`Optional[str]`
- **默认值**：`None`
- **CLI**：`--default-role/-dr`

设置默认角色。RST 中反引号包裹的文本（\`text\`）会使用默认角色处理。如果设为 `None`，默认角色的内容会转换为字面量（行内代码）。

```python
# 将默认角色设为 math
result = rst_to_myst(text, default_role="math")
```

## 转换行为选项

### conversions

- **类型**：`Optional[dict[str, str]]`
- **默认值**：`None`
- **CLI**：`--conversions/-c`（YAML 文件路径）

自定义指令转换映射，覆盖或追加 `directives.yml` 中的默认映射。键是指令类的完整模块路径，值是转换类型。

CLI 使用方式：
```yaml
# my-conversions.yml
myapp.directives.MyDirective: eval_rst
```

```bash
rst2myst stream -c my-conversions.yml input.rst
```

### raise_on_warning

- **类型**：`bool`
- **默认值**：`False`
- **CLI**：`--raise-on-warning/-W`（仅 convert 子命令）

控制是否在遇到解析/渲染警告时抛出异常。默认行为是将警告写入 warning_stream 并继续转换。启用后遇到未知节点类型等问题会立即失败。

```bash
# 批量转换，遇警告立即停止
rst2myst convert -W -S docs/
```

## 输出格式选项

### consecutive_numbering

- **类型**：`bool`
- **默认值**：`True`
- **CLI**：`--consecutive-numbering/--no-consecutive-numbering`

控制有序列表是否使用连续编号。启用后，所有有序列表项使用连续递增的数字（1, 2, 3...），而非从1重新开始。此选项传递给 mdformat 渲染器。

### colon_fences

- **类型**：`bool`
- **默认值**：`True`
- **CLI**：`--colon-fences/--no-colon-fences`

控制有内容的指令是否使用冒号围栏（`:::`）而非反引号围栏。冒号围栏是 MyST 的扩展语法，允许内容中包含反引号而不与围栏冲突。

启用时（默认）：
```markdown
:::{note}
内容中可以包含 `反引号`
:::
```

禁用时：
````markdown
```{note}
内容中的反引号需要增加围栏长度
```
````

当 `colon_fences=True` 时，`get_myst_extensions()` 会自动检测需要 `colon_fence` 扩展。

### dollar_math

- **类型**：`bool`
- **默认值**：`True`
- **CLI**：`--dollar-math/--no-dollar-math`

控制数学公式是否转换为美元定界格式（`$...$` 和 `$$...$$`）。启用时，RST 的数学指令/角色会转换为 MyST 的美元数学语法；禁用时可能使用其他数学指令格式。

启用时，`get_myst_extensions()` 会检测需要 `dollarmath` 扩展。

### cite_prefix

- **类型**：`str`
- **默认值**：`"cite_"`（CLI 默认 `"cite"`，内部自动加 `_`）
- **CLI**：`--cite-prefix/-cp`

设置引用（citation）标签的前缀。RST 中 `[citekey]` 形式的引用在转换后标签会此前缀，避免与其他链接冲突。

CLI 传入 `"cite"`，内部追加 `_` 变成 `"cite_"`。

## 其他选项

### warning_stream

- **类型**：`Optional[IO]`
- **默认值**：`None`（自动创建 StringIO）

指定警告输出流。所有解析和渲染警告会写入此流。如果为 None，函数内部创建一个新的 StringIO 对象，通过返回值的 `warning_stream` 字段访问。

```python
from io import StringIO
ws = StringIO()
result = rst_to_myst(text, warning_stream=ws)
print(ws.getvalue())  # 读取所有警告
```

### front_matter（仅 Python API）

- **类型**：`bool`
- **默认值**：`True`

控制是否将文档开头的 field_list 提取为 YAML front matter。CLI 不暴露此选项。

### namespace（仅 Python API）

- **类型**：`Optional[ApplicationNamespace]`
- **默认值**：`None`

传入预编译的 ApplicationNamespace 对象。批量转换多个文件时，预编译 namespace 可以避免重复加载 Sphinx 和扩展，显著提升性能。

```python
from rst_to_myst import compile_namespace, rst_to_myst

ns = compile_namespace(use_sphinx=True, extensions=["sphinx.ext.autodoc"])
for text in many_texts:
    result = rst_to_myst(text, namespace=ns)
```

## CLI 专属选项

### --config

YAML 配置文件路径，设置选项默认值。配置文件是 eager 加载的，在其他选项之前解析。

### --encoding

- **默认值**：`"utf8"`
- 仅 `convert` 子命令，设置文件读写编码。

## 相关概念

- [命令行工具详细用法](/concepts/01-cli-usage.md)
- [Python API 使用指南](/concepts/02-python-api.md)
- [mdformat 渲染集成与自定义渲染器](/concepts/07-mdformat-integration.md)
