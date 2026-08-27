---
type: Concept
title: URL 解析与格式化
description: mdurl 的 parse() 和 format() 函数详解——URL 字符串解析为 URL namedtuple 的完整流程、slashes_denote_host 参数、以及反向格式化
tags: [mdurl, url, parse, format, slashes_denote_host]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T01:15:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mdurl-source
    resource: /references/mdurl-source.md
    title: mdurl 源码路径映射
---

## parse() 函数

`parse()` 是 mdurl 最核心的函数，它将 URL 字符串解析为不可变的 `URL` namedtuple。

```python
from mdurl import parse

url = parse("https://example.com/path?q=test#section")
print(url.hostname)  # "example.com"
print(url.pathname)  # "/path"
print(url.search)    # "?q=test"
print(url.hash)      # "#section"
```

函数签名：

```python
def url_parse(url: URL | str, *, slashes_denote_host: bool = False) -> URL
```

`parse` 是 `url_parse` 的别名。注意两个关键行为：

1. **如果传入的已经是 `URL` 实例**，直接返回，不做任何处理。这使得 `parse()` 可以安全地用于不确定输入是字符串还是已解析 URL 的场景。
2. **`slashes_denote_host` 参数**控制 `//` 是否被解释为主机名的开始标记，默认为 `False`。

## slashes_denote_host 参数

这是 mdurl 解析行为中最重要的参数，直接影响如何区分主机名和路径。

- **`slashes_denote_host=False`（默认）**：`//` 不自动表示主机名。相对路径 `//foo/bar` 不会被解析为 host=`foo`、path=`/bar`，而是作为路径处理。这是 Markdown 场景的默认行为——Markdown 链接中的 `//foo/bar` 通常是协议相对 URL，但 Markdown 解析器需要精确控制何时将 `//` 视为主机标记。

- **`slashes_denote_host=True`**：`//` 被解释为主机名的开始。这更接近浏览器和 `urllib.parse` 的行为。

```python
from mdurl import parse

# 默认模式：slashes_denote_host=False
url1 = parse("//example.com/path")
print(url1.hostname)  # None（因为没有协议，//不触发主机解析）
print(url1.pathname)  # "//example.com/path"

# slashes_denote_host=True
url2 = parse("//example.com/path", slashes_denote_host=True)
print(url2.hostname)  # "example.com"
print(url2.slashes)   # True
print(url2.pathname)  # "/path"

# 有协议时，两种模式行为一致
url3 = parse("https://example.com/path")
print(url3.hostname)  # "example.com"（协议存在时自动触发主机解析）
```

## 解析流程详解

`parse()` 内部创建 `MutableURL` 对象并调用其 `parse()` 方法，解析流程如下：

### 1. 预处理：空白修剪

输入字符串首先调用 `strip()` 去除首尾空白字符，使得 `parse("  http://foo.com  \n")` 能正确解析。

### 2. 快速路径：简单路径匹配

当 `slashes_denote_host=False` 且 URL 不含 `#` 时，尝试用 `SIMPLE_PATH_PATTERN`（正则 `^(//?(?!/)[^?\s]*)(\?[^\s]*)?$`）快速匹配简单路径 URL。匹配成功则直接设置 pathname 和 search，跳过后续复杂解析。

### 3. 协议提取

用 `PROTOCOL_PATTERN`（正则 `^([a-z0-9.+-]+:)`，忽略大小写）匹配协议部分。协议由字母、数字、点、加号、减号组成，以冒号结尾。匹配成功后，协议部分存入 `self.protocol`，剩余字符串继续解析。

### 4. Slashes 判断

以下条件满足时检查 `//`：
- `slashes_denote_host=True`，或
- 存在协议（`proto` 非空），或
- 匹配 `//[^@/]+@[^@/]+` 模式（user@server 形式）

如果 rest 以 `//` 开头且协议不是 `javascript:`（无主机协议），则设置 `slashes=True` 并去掉前两个字符。

### 5. 主机名解析

当存在主机名时（非 HOSTLESS_PROTOCOL，且有 slashes 或有非 SLASHED_PROTOCOL 的协议），执行主机解析：

- **auth 提取**：在主机结束标记（`/`、`?`、`#`）之前查找最后一个 `@`，`@` 前为认证信息（auth），`@` 后继续解析主机。例如 `http://a@b@c/` 解析为 auth=`a@b`、host=`c`。
- **port 提取**：调用 `parse_host()` 方法，用 `PORT_PATTERN`（正则 `:[0-9]*$`）匹配末尾的端口号。如果端口部分只是 `:`（无数字），则不设 port。
- **hostname 验证**：非 IPv6 地址时，按 `.` 分割，每段用 `HOSTNAME_PART_PATTERN`（正则 `^[+a-z0-9A-Z_-]{0,63}$`）验证。含非 ASCII 字符时替换为 `x` 后再验证，不合法部分截断归入路径。
- **长度限制**：hostname 超过 255 字符时设为空字符串。
- **IPv6 处理**：hostname 以 `[` 开头以 `]` 结尾时识别为 IPv6，去掉方括号存储。

### 6. 尾部组件解析（从右向左）

- **hash 提取**：查找第一个 `#`，`#` 及其后内容存入 `self.hash`（包含 `#` 本身）
- **search 提取**：剩余部分查找第一个 `?`，`?` 及其后内容存入 `self.search`（包含 `?` 本身）
- **pathname**：最终剩余部分存入 `self.pathname`

### 7. 特殊协议处理

- **HOSTLESS_PROTOCOL**：`javascript:` 和 `javascript:javascript` 被标记为无主机协议，解析时跳过主机名部分
- **SLASHED_PROTOCOL**：`http:`, `https:`, `ftp:`, `gopher:`, `file:` 被标记为带斜杠协议，当有 hostname 但无 pathname 时，pathname 设为空字符串（而非 `None`）

## format() 函数

`format()` 是 `parse()` 的逆操作，将 `URL` namedtuple 拼接回 URL 字符串：

```python
from mdurl import URL, format

url = URL(
    protocol="https:",
    slashes=True,
    auth="user:pass",
    hostname="example.com",
    port="8080",
    pathname="/path",
    search="?q=test",
    hash="#section",
)
print(format(url))
# "https://user:pass@example.com:8080/path?q=test#section"
```

拼接顺序和分隔符规则：

1. `protocol`（或空串）直接拼接
2. `slashes=True` 时拼接 `"//"`
3. `auth` 非 None 时拼接 `auth + "@"`
4. hostname 处理：含 `:` 时加方括号 `[hostname]`（IPv6），否则直接拼接 hostname（或空串）
5. `port` 非 None 时拼接 `":" + port`
6. `pathname`（或空串）直接拼接
7. `search`（或空串）直接拼接
8. `hash`（或空串）直接拼接

### parse/format 往返一致性

```python
from mdurl import parse, format

original = "https://example.com/path?q=test#section"
result = format(parse(original))
print(result)  # "https://example.com/path?q=test#section"
print(result == original)  # True
```

对于合法 URL，`format(parse(url))` 通常能还原原始字符串。但需要注意，`parse()` 不做 URL 解码，所以已编码的字符在往返后保持编码形式。

## 与 urllib.parse 的关键差异

| 行为 | mdurl.parse | urllib.parse.urlparse |
|------|------------|----------------------|
| 无前导斜杠路径 | `http://foo?bar` → pathname=`""` | path=`/` |
| 反斜杠处理 | `http:\\example.org\` → 相对路径 | 反斜杠替换为正斜杠 |
| 尾部冒号 | `http://example.org:foo` → port=None, pathname=":foo" | 可能解析失败 |
| slashes_denote_host | 默认 False，// 不自动表主机 | // 总是表主机 |
| 冗余属性 | 无 host/path/query | 有 hostname/netloc/path/query 等 |
| 查询字符串解析 | 不解析（search 是原始字符串） | 可通过 parse_qs 解析 |

mdurl 的行为是为 Markdown 链接解析场景精确调整的，这也是 markdown-it-py 依赖 mdurl 而非标准库的原因。

## 相关概念

- [URL 数据结构](01-url-data-structure.md)
- [URL 编码与解码](03-encode-and-decode.md)
- [基础使用示例](../examples/basic-usage.md)
- [mdurl 简介](00-introduction.md)
