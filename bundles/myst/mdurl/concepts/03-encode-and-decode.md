---
type: Concept
title: URL 编码与解码
description: mdurl 的 encode() 和 decode() 函数——百分号编解码原理、DEFAULT 与 COMPONENT 两种模式、查找表缓存机制与 UTF-8 多字节处理
tags: [mdurl, url, encode, decode, percent-encoding, utf-8]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T01:20:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mdurl-source
    resource: /references/mdurl-source.md
    title: mdurl 源码路径映射
---

## 百分号编码基础

URL 中只允许直接使用 ASCII 字母数字和有限的特殊字符，其他字符必须通过"百分号编码"（percent-encoding）表示为 `%XX` 形式，其中 XX 是字符的 UTF-8 字节的十六进制表示。例如空格编码为 `%20`，中文"你"编码为 `%E4%BD%A0`。

mdurl 提供 `encode()` 和 `decode()` 两个函数进行百分号编码和解码，它们的设计直接对应 JavaScript 的 `encodeURI`/`decodeURI` 和 `encodeURIComponent`/`decodeURIComponent`。

## encode() 函数

```python
from mdurl import encode

encode("hello world")  # "hello%20world"
encode("https://example.com/path?q=hello world")
# "https://example.com/path?q=hello%20world"
```

函数签名：

```python
def encode(
    string: str,
    exclude: str = ENCODE_DEFAULT_CHARS,
    *,
    keep_escaped: bool = True,
) -> str
```

### 参数说明

- **string**：要编码的字符串
- **exclude**：不编码的字符集合（除字母数字外）。字母数字字符始终不编码
- **keep_escaped**：为 `True`（默认）时，已有的合法 `%XX` 序列保持不编码；为 `False` 时，`%` 本身也会被编码为 `%25`

### 两种编码模式

mdurl 预置了两种排除字符集，对应两种编码场景：

**DEFAULT 模式（默认）**——对应 `encodeURI`：

```python
ENCODE_DEFAULT_CHARS = ";/?:@&=+$,-_.!~*'()#"
```

保留 URL 结构字符（`;`, `/`, `?`, `:`, `@`, `&`, `=`, `+`, `$`, `,`, `#` 等），适用于编码完整 URL。这些字符在 URL 中有特殊含义（分隔路径、查询参数、片段等），编码它们会破坏 URL 结构。

**COMPONENT 模式**——对应 `encodeURIComponent`：

```python
ENCODE_COMPONENT_CHARS = "-_.!~*'()"
```

仅保留 RFC 3986 定义的"非保留字符"（unreserved characters），适用于编码 URL 的单个组件（如查询参数值、路径段）。

```python
from mdurl import encode, ENCODE_DEFAULT_CHARS, ENCODE_COMPONENT_CHARS

# DEFAULT 模式：保留 URL 结构字符
encode("a=b&c=d", exclude=ENCODE_DEFAULT_CHARS)
# "a=b&c=d"（& 和 = 不编码）

# COMPONENT 模式：编码 URL 结构字符
encode("a=b&c=d", exclude=ENCODE_COMPONENT_CHARS)
# "a%3Db%26c%3Dd"（& 编码为 %26，= 编码为 %3D）
```

### keep_escaped 参数

```python
from mdurl import encode

# keep_escaped=True（默认）：已有的 %XX 不重复编码
encode("hello%20world")  # "hello%20world"

# keep_escaped=False：% 也被编码
encode("hello%20world", keep_escaped=False)  # "hello%2520world"
```

当 `keep_escaped=True` 时，encode 会检查 `%` 后面是否跟两个十六进制数字（`0-9a-fA-F`），如果是则跳过整个 `%XX` 序列。

### Unicode 代理对处理

对于 Unicode 代理对（surrogate pairs，码点在 0xD800-0xDFFF 范围），encode 进行特殊处理：

- 高代理（0xD800-0xDBFF）后跟低代理（0xDC00-0xDFFF）时，两个代理字符合并后使用 `urllib.parse.quote` 编码
- 孤立的代理字符（没有配对的低代理/高代理）输出 `%EF%BF%BD`（U+FFFD 替换字符的编码）

正常的非 ASCII Unicode 字符（码点 ≥ 128 且不在代理区）直接使用 `urllib.parse.quote` 编码为 UTF-8 字节序列。

## decode() 函数

```python
from mdurl import decode

decode("hello%20world")  # "hello world"
decode("https://example.com/path?q=hello%20world")
# "https://example.com/path?q=hello world"
```

函数签名：

```python
def decode(string: str, exclude: str = DECODE_DEFAULT_CHARS) -> str
```

### 参数说明

- **string**：要解码的百分号编码字符串
- **exclude**：不解码的字符集合（即这些字符的 `%XX` 形式保持编码状态）

### 两种解码模式

**DEFAULT 模式（默认）**：

```python
DECODE_DEFAULT_CHARS = ";/?:@&=+$,#"
```

这些 URL 结构字符的百分号编码形式不被解码。例如 `%3F`（`?`的编码）不会被解码为 `?`，因为 `?` 在 URL 中分隔查询字符串，提前解码可能改变 URL 语义。

**COMPONENT 模式**：

```python
DECODE_COMPONENT_CHARS = ""  # 空字符串
```

空字符串意味着没有字符被排除，所有百分号编码序列都会被解码。

```python
from mdurl import decode, DECODE_DEFAULT_CHARS, DECODE_COMPONENT_CHARS

# DEFAULT 模式：不解码 URL 结构字符
decode("hello%3Fworld", exclude=DECODE_DEFAULT_CHARS)
# "hello%3Fworld"（%3F 即 ? 不解码）

# COMPONENT 模式：全部解码
decode("hello%3Fworld", exclude=DECODE_COMPONENT_CHARS)
# "hello?world"
```

### UTF-8 多字节解码

decode 内部识别 UTF-8 编码的多字节序列：

- **1字节**（`0xxxxxxx`，码点 0-127）：直接查预计算查找表输出
- **2字节**（`110xxxxx 10xxxxxx`）：组合两字节，通过 `bytes((b1,b2)).decode()` 解码
- **3字节**（`1110xxxx 10xxxxxx 10xxxxxx`）：组合三字节解码
- **4字节**（`11110xxx 10xxxxxx 10xxxxxx 10xxxxxx`）：组合四字节解码

解码失败时（非法 UTF-8 序列），输出对应数量的 U+FFFD（替换字符 `\ufffd`）。不符合任何有效 UTF-8 起始字节模式的 `%XX` 序列，输出单个 U+FFFD 并跳过。

## 查找表缓存机制

encode 和 decode 都使用预计算的 ASCII 查找表来加速处理：

### 编码查找表

`get_encode_cache(exclude)` 构建一个 128 项的列表（对应 ASCII 0-127）：

1. 初始化：字母数字字符设为字符本身（不编码），其余设为 `%XX` 形式
2. 覆盖：`exclude` 中的字符设为字符本身（不编码）
3. 缓存：结果存入 `encode_cache[exclude]`，下次相同 exclude 参数直接复用

### 解码查找表

`get_decode_cache(exclude)` 构建一个 128 项的列表：

1. 初始化：所有 ASCII 字符设为字符本身
2. 覆盖：`exclude` 中的字符设为 `%XX` 形式（保持编码状态不被解码）
3. 缓存：结果存入 `decode_cache[exclude]`

这种设计使得逐字符处理时，对于 ASCII 范围内的字符只需要一次数组下标查找（O(1)），不需要逐字符判断和字符串操作。非 ASCII 字符走慢路径（encode 用 `urllib.parse.quote`，decode 用 `bytes.decode()`）。

```python
# 缓存是模块级字典，相同 exclude 参数只构建一次
from mdurl._encode import encode_cache
from mdurl._decode import decode_cache
# 首次调用 encode() 或 decode() 后，cache 中会有对应条目
```

## 编解码实践建议

1. **处理完整 URL 时用 DEFAULT 模式**，避免编码 `/`、`?`、`&`、`=` 等结构字符导致 URL 损坏
2. **处理 URL 组件（如查询参数值）时用 COMPONENT 模式**，确保所有特殊字符被编码
3. **对不确定是否已编码的字符串用 keep_escaped=True**（默认），避免重复编码
4. **需要完全规范化编码时用 keep_escaped=False**，确保所有 `%` 都被编码
5. **decode 时注意 exclude 参数**：在解析 URL 组件后再对各组件做 COMPONENT 解码，而不是对整个 URL 做 COMPONENT 解码

## 相关概念

- [URL 数据结构](/concepts/01-url-data-structure.md)
- [URL 解析与格式化](/concepts/02-parse-and-format.md)
- [基础使用示例](/examples/basic-usage.md)
- [mdurl 简介](/concepts/00-introduction.md)
