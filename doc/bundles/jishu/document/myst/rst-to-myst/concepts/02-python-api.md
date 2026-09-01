---
type: Concept
title: Python API 使用指南
description: rst-to-myst 作为 Python 库的核心 API 函数、参数和返回值详解。
tags: [python-api, programming, rst_to_myst, to_docutils_ast, compile_namespace]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 公开 API 总览

rst-to-myst 的包入口 `rst_to_myst/__init__.py` 导出三个核心函数：

```python
from rst_to_myst import rst_to_myst, to_docutils_ast, compile_namespace
```

## rst_to_myst - 一站式转换

`rst_to_myst()` 是最常用的函数，执行完整的 RST→MyST 转换。

### 函数签名

```python
def rst_to_myst(
    text: str,
    *,
    warning_stream: Optional[IO] = None,
    language_code: str = "en",
    use_sphinx: bool = True,
    extensions: Iterable[str] = (),
    conversions: Optional[dict[str, str]] = None,
    default_domain: str = "py",
    default_role: Optional[str] = None,
    raise_on_warning: bool = False,
    cite_prefix: str = "cite_",
    consecutive_numbering: bool = True,
    colon_fences: bool = True,
    dollar_math: bool = True,
) -> ConvertedOutput:
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | `str` | 必填 | 输入 RST 文本 |
| `warning_stream` | `IO` | `None` | 警告输出流（None则创建StringIO） |
| `language_code` | `str` | `"en"` | 指令/角色名语言代码 |
| `use_sphinx` | `bool` | `True` | 是否加载 Sphinx 指令和角色 |
| `extensions` | `Iterable[str]` | `()` | 要加载的 Sphinx 扩展列表 |
| `conversions` | `dict[str, str]` | `None` | 自定义指令转换映射 |
| `default_domain` | `str` | `"py"` | 默认 Sphinx 域 |
| `default_role` | `str` | `None` | 默认角色（None→字面量） |
| `raise_on_warning` | `bool` | `False` | 警告时抛出异常 |
| `cite_prefix` | `str` | `"cite_"` | 引用标签前缀 |
| `consecutive_numbering` | `bool` | `True` | 有序列表连续编号 |
| `colon_fences` | `bool` | `True` | 有内容的指令使用冒号围栏 |
| `dollar_math` | `bool` | `True` | 数学使用美元定界 |

### 返回值：ConvertedOutput

`ConvertedOutput` 是一个 NamedTuple，包含五个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 输出 MyST Markdown 文本 |
| `tokens` | `list[Token]` | markdown-it token 列表 |
| `env` | `dict[str, Any]` | 渲染环境（引用定义等） |
| `warning_stream` | `IO` | 警告输出流（可读取警告内容） |
| `extensions` | `set[str]` | 所需 MyST 扩展集合 |

### 基本用法

```python
from rst_to_myst import rst_to_myst

result = rst_to_myst("*Hello* **world**!")
print(result.text)
# *Hello* **world**!

print(result.extensions)
# set()（此简单文本不需要特殊扩展）
```

### 获取警告信息

```python
from io import StringIO
from rst_to_myst import rst_to_myst

warning_stream = StringIO()
result = rst_to_myst(
    "Some invalid RST",
    warning_stream=warning_stream,
    raise_on_warning=False,
)

warnings = warning_stream.getvalue()
if warnings:
    print("Warnings:", warnings)
```

### 自定义指令转换

```python
from rst_to_myst import rst_to_myst

result = rst_to_myst(
    ".. mydirective:: argument\n\n   content",
    conversions={"mymodule.mydirective": "eval_rst"},
)
```

### 加载 Sphinx 扩展

```python
from rst_to_myst import rst_to_myst

result = rst_to_myst(
    rst_text,
    use_sphinx=True,
    extensions=["sphinx.ext.autodoc", "sphinx.ext.todo"],
)
```

## to_docutils_ast - RST 解析到 AST

`to_docutils_ast()` 将 RST 文本解析为 docutils 文档树，不执行到 Markdown 的转换。适用于需要分析或处理 docutils AST 的场景。

### 函数签名

```python
def to_docutils_ast(
    text: str,
    uri: str = "source",
    report_level: int = 2,
    halt_level: int = 4,
    warning_stream: Optional[StringIO] = None,
    language_code: str = "en",
    use_sphinx: bool = True,
    extensions: Iterable[str] = (),
    default_domain: str = "py",
    conversions: Optional[dict] = None,
    front_matter: bool = True,
    namespace: Optional[ApplicationNamespace] = None,
) -> tuple[nodes.document, StringIO]:
```

### 返回值

返回 `(document, warning_stream)` 元组：
- `document`：docutils `nodes.document` 对象，可通过 walk/walkabout 遍历
- `warning_stream`：包含解析警告的 StringIO

### 基本用法

```python
from rst_to_myst import to_docutils_ast

document, warnings = to_docutils_ast("*Hello* world!")
print(document.pformat())  # 打印 AST 结构
print(document.asdom())    # 转为 DOM
```

### 使用预编译 namespace

如果需要多次解析，可以预编译 namespace 避免重复加载 Sphinx：

```python
from rst_to_myst import to_docutils_ast, compile_namespace

ns = compile_namespace(use_sphinx=True, extensions=["sphinx.ext.autodoc"])

for text in many_rst_texts:
    doc, ws = to_docutils_ast(text, namespace=ns)
```

## compile_namespace - 编译指令/角色命名空间

`compile_namespace()` 创建一个 `ApplicationNamespace` 对象，包含所有可用的指令和角色查找表。

### 函数签名

```python
def compile_namespace(
    extensions: Iterable[str] = (),
    use_sphinx: bool = True,
    default_domain: str = "py",
    language_code: str = "en",
) -> ApplicationNamespace:
```

### ApplicationNamespace 的主要方法

```python
ns = compile_namespace()

# 列出所有指令
all_directives = ns.list_directives()

# 列出所有角色
all_roles = ns.list_roles()

# 获取指令类
directive_cls = ns.get_directive("image")

# 获取角色函数
role_func = ns.get_role("math")

# 获取指令元数据
directive_data = ns.get_directive_data("image")
print(directive_data["required_arguments"])
print(directive_data["has_content"])
print(directive_data["options"])
```

### 线程安全

`compile_namespace` 使用线程锁（`threading.Lock()`）保护全局 docutils 状态的临时修改，可以在多线程环境中安全调用。

## YAML 工具

`rst_to_myst.utils.yaml_dump` 函数提供自定义 YAML 序列化，多行字符串使用 `|` 块标量样式：

```python
from rst_to_myst.utils import yaml_dump

print(yaml_dump({"key": "value", "multiline": "line1\nline2\nline3"}))
# key: value
# multiline: |
#   line1
#   line2
#   line3
```

## 相关概念

- [命令行工具详细用法](01-cli-usage.md)
- [三阶段转换流水线架构](03-conversion-pipeline.md)
- [转换选项详解](10-configuration-options.md)
