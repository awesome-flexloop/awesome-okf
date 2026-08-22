---
type: Concept
title: URL 数据结构
description: mdurl 的核心数据结构——URL namedtuple 的八个字段语义、MutableURL 内部构建器与不可变设计模式
tags: [mdurl, url, namedtuple, data-structure, mutableurl]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T01:10:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mdurl-source
    resource: /references/mdurl-source.md
    title: mdurl 源码路径映射
---

## URL namedtuple

`URL` 是 mdurl 的核心数据结构，它是一个 `collections.namedtuple`，包含 8 个字段，每个字段对应 URL 的一个组成部分。所有字段要么是字符串，要么是 `None`（`slashes` 除外，它是布尔值）。

```python
from mdurl import URL

url = URL(
    protocol="https:",
    slashes=True,
    auth=None,
    port=None,
    hostname="example.com",
    hash="#section",
    search="?q=test",
    pathname="/path/to/page",
)
```

### 八个字段详解

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `protocol` | `str \| None` | 协议部分，包含末尾冒号 | `"https:"`, `"http:"`, `None` |
| `slashes` | `bool` | URL 是否以 `//` 开头（协议后有双斜杠） | `True`, `False` |
| `auth` | `str \| None` | 认证信息（用户名:密码），不含 `@` 符号 | `"user:pass"`, `None` |
| `port` | `str \| None` | 端口号，不含冒号 | `"8080"`, `None` |
| `hostname` | `str \| None` | 主机名（域名或IP），IPv6不含方括号 | `"example.com"`, `"::1"`, `None` |
| `hash` | `str \| None` | 片段标识符，包含 `#` 符号 | `"#section"`, `None` |
| `search` | `str \| None` | 查询字符串，包含 `?` 符号 | `"?q=test"`, `None` |
| `pathname` | `str \| None` | 路径部分 | `"/path/to/page"`, `""`, `None` |

需要注意几个容易混淆的点：

- **protocol 包含冒号**：`"https:"` 而不是 `"https"`，这与 JavaScript 的 URL 类一致
- **port 不含冒号**：`"8080"` 而不是 `":8080"`
- **hash 包含井号**：`"#section"` 而不是 `"section"`
- **search 包含问号**：`"?q=test"` 而不是 `"q=test"`
- **hostname 不含方括号**：IPv6 地址在 hostname 中存储时已去掉 `[` 和 `]`，但 `format()` 输出时会重新添加
- **slashes 是布尔值**：不是字符串 `"//"`，而是 `True`/`False`
- **pathname 可以是空字符串**：对于 `http://example.com?query` 这样的 URL，pathname 为空字符串 `""`（而非 `"/"` 或 `None`）

### 不可变性

`URL` 继承自 `namedtuple`，因此是不可变的。创建后不能直接修改字段值：

```python
url = URL(protocol="http:", slashes=True, hostname="example.com",
          port=None, auth=None, hash=None, search=None, pathname="/")

# 以下操作会报错：
# url.hostname = "other.com"  # AttributeError

# 修改需要创建新实例：
new_url = url._replace(hostname="other.com")
```

可以使用 `namedtuple` 的 `_replace()` 方法创建修改后的新实例。

## MutableURL：内部构建器

虽然公共 API 返回的是不可变 `URL`，但解析过程中使用的是内部的 `MutableURL` 类。`MutableURL` 是一个普通 Python 类，其 8 个属性在初始化时全部设为 `None` 或 `False`，在解析过程中逐步被赋值：

```python
class MutableURL:
    def __init__(self) -> None:
        self.protocol: str | None = None
        self.slashes: bool = False
        self.auth: str | None = None
        self.port: str | None = None
        self.hostname: str | None = None
        self.hash: str | None = None
        self.search: str | None = None
        self.pathname: str | None = None
```

`MutableURL` 有两个方法：

- `parse(url: str, slashes_denote_host: bool) -> MutableURL`：执行实际的 URL 字符串解析，将结果填充到自身属性中，返回 `self` 以支持链式调用
- `parse_host(host: str) -> None`：从 host 字符串中提取端口号和主机名

解析完成后，`url_parse()` 函数用 `MutableURL` 的属性值构造一个不可变的 `URL` namedtuple 返回给调用者。这种"可变构建 → 不可变结果"的模式既保证了解析过程中的灵活性，又保证了返回结果的安全性。

## 字段关系示例

理解字段间的分隔符关系有助于使用 `format()` 重构 URL：

```
  https://user:pass@example.com:8080/path/to/page?q=test#section
  ──┬──  ─┬─ ────┬─── ─────┬───── ─┬─ ───────────┬───────── ─────┬───── ─────┬─────
    │     │      │         │       │              │               │           │
 protocol slashes auth   hostname port        pathname         search       hash
 "https:" True "user:pass" "example.com" "8080" "/path/to/page" "?q=test" "#section"
```

`format()` 函数正是按照这个顺序拼接各字段，在适当位置添加分隔符（`//`、`@`、`:`、`[`、`]`）。

## TYPE_CHECKING 条件类型标注

`_url.py` 使用了 Python 的 `TYPE_CHECKING` 模式来提供类型标注而不引入运行时开销：

```python
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import NamedTuple
    class URL(NamedTuple):
        protocol: str | None
        slashes: bool
        # ... 其他字段类型标注
else:
    URL = namedtuple("URL", ["protocol", "slashes", "auth", ...])
```

在运行时 `TYPE_CHECKING` 为 `False`，所以 `URL` 实际是普通的 `namedtuple`；但类型检查器（如 mypy）会看到 `NamedTuple` 的类型标注，从而提供正确的类型推断。

## 相关概念

- [mdurl 简介](/concepts/00-introduction.md)
- [URL 解析与格式化](/concepts/02-parse-and-format.md)
- [URL 编码与解码](/concepts/03-encode-and-decode.md)
- [基础使用示例](/examples/basic-usage.md)
