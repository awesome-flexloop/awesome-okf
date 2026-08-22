---
type: Example
title: mdurl 基础使用
description: mdurl 核心 API 的完整可运行示例——URL 解析、字段访问、修改重构、编码解码的实战演示
tags: [mdurl, url, example, basic-usage]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T01:25:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mdurl-source
    resource: /references/mdurl-source.md
    title: mdurl 源码路径映射
---

## 解析 URL 并访问字段

```python
from mdurl import parse

# 解析完整 URL
url = parse("https://user:pass@example.com:8080/path/to/page?q=hello&lang=en#section")

print(url.protocol)   # "https:"
print(url.slashes)    # True
print(url.auth)       # "user:pass"
print(url.hostname)   # "example.com"
print(url.port)       # "8080"
print(url.pathname)   # "/path/to/page"
print(url.search)     # "?q=hello&lang=en"
print(url.hash)       # "#section"
```

### 解析相对路径

```python
from mdurl import parse

# 相对路径
url = parse("/path/to/page?q=test")
print(url.protocol)   # None
print(url.hostname)   # None
print(url.pathname)   # "/path/to/page"
print(url.search)     # "?q=test"

# 无路径的 URL
url2 = parse("http://example.com?query")
print(url2.pathname)  # ""（空字符串，不是 "/" 也不是 None）
print(url2.hostname)  # "example.com"
print(url2.search)    # "?query"
```

### slashes_denote_host 参数对比

```python
from mdurl import parse

# 默认模式（slashes_denote_host=False）：// 不自动表主机
url1 = parse("//example.com/path")
print(url1.hostname)  # None
print(url1.pathname)  # "//example.com/path"

# 开启后：// 表示主机开始
url2 = parse("//example.com/path", slashes_denote_host=True)
print(url2.hostname)  # "example.com"
print(url2.slashes)   # True
print(url2.pathname)  # "/path"

# 有协议时两种模式一致
url3 = parse("https://example.com/path")
print(url3.hostname)  # "example.com"
```

### parse 接受 URL 实例（幂等）

```python
from mdurl import parse, URL

url = URL(protocol="https:", slashes=True, hostname="example.com",
          auth=None, port=None, hash=None, search=None, pathname="/")

# 传入已解析的 URL，直接返回
url2 = parse(url)
print(url2 is url)  # True
```

## 修改 URL 并格式化

由于 `URL` 是不可变 namedtuple，修改字段需使用 `_replace()`：

```python
from mdurl import parse, format

url = parse("https://example.com/path?q=test#section")

# 修改 hostname
new_url = url._replace(hostname="other.com")
print(format(new_url))  # "https://other.com/path?q=test#section"

# 修改 port 和 pathname
new_url2 = url._replace(port="8443", pathname="/api/v1")
print(format(new_url2))  # "https://example.com:8443/api/v1?q=test#section"

# 移除 search 和 hash
clean_url = url._replace(search=None, hash=None)
print(format(clean_url))  # "https://example.com/path"
```

### 从零构造 URL

```python
from mdurl import URL, format

url = URL(
    protocol="https:",
    slashes=True,
    auth=None,
    hostname="api.example.com",
    port="443",
    pathname="/v1/users",
    search="?page=1&limit=20",
    hash=None,
)
print(format(url))
# "https://api.example.com:443/v1/users?page=1&limit=20"
```

### IPv6 地址格式化

```python
from mdurl import URL, format

url = URL(
    protocol="http:",
    slashes=True,
    auth=None,
    hostname="::1",
    port="8080",
    pathname="/",
    search=None,
    hash=None,
)
print(format(url))  # "http://[::1]:8080/"
```

## URL 编码

```python
from mdurl import encode, ENCODE_DEFAULT_CHARS, ENCODE_COMPONENT_CHARS

# 基础编码：空格编码为 %20
print(encode("hello world"))  # "hello%20world"

# DEFAULT 模式（默认）：保留 URL 结构字符
print(encode("a=b&c=d", exclude=ENCODE_DEFAULT_CHARS))
# "a=b&c=d"（& 和 = 不编码，它们是 URL 结构字符）

# COMPONENT 模式：编码 URL 结构字符
print(encode("a=b&c=d", exclude=ENCODE_COMPONENT_CHARS))
# "a%3Db%26c%3Dd"

# 中文编码
print(encode("你好世界"))  # "%E4%BD%A0%E5%A5%BD%E4%B8%96%E7%95%8C"
```

### keep_escaped 参数

```python
from mdurl import encode

# 默认 keep_escaped=True：已编码序列不重复编码
print(encode("hello%20world"))  # "hello%20world"

# keep_escaped=False：% 也被编码
print(encode("hello%20world", keep_escaped=False))  # "hello%2520world"
```

## URL 解码

```python
from mdurl import decode, DECODE_DEFAULT_CHARS, DECODE_COMPONENT_CHARS

# 基础解码
print(decode("hello%20world"))  # "hello world"

# DEFAULT 模式（默认）：不解码 URL 结构字符
print(decode("hello%3Fworld", exclude=DECODE_DEFAULT_CHARS))
# "hello%3Fworld"（%3F 即 ?，不解码）

# COMPONENT 模式：全部解码
print(decode("hello%3Fworld", exclude=DECODE_COMPONENT_CHARS))
# "hello?world"

# 中文解码
print(decode("%E4%BD%A0%E5%A5%BD"))  # "你好"
```

### UTF-8 多字节解码

```python
from mdurl import decode

# 4字节 UTF-8（emoji）
print(decode("%F0%9F%8C%8D"))  # "🌍"

# 非法 UTF-8 序列产生替换字符
print(decode("%C0%AF"))  # 含 U+FFFD 替换字符
```

## 完整流水线示例

以下示例演示 parse → 修改字段 → encode → format 的完整流程：

```python
from mdurl import parse, format, encode, ENCODE_COMPONENT_CHARS

# 原始 URL
original = "https://example.com/search?q=hello world&lang=zh"

# 1. 解析
url = parse(original)

# 2. 修改查询参数（对参数值做 COMPONENT 编码）
new_query = "?q=" + encode("你好 世界", exclude=ENCODE_COMPONENT_CHARS) + "&lang=zh"
url = url._replace(search=new_query)

# 3. 格式化回字符串
result = format(url)
print(result)
# "https://example.com/search?q=%E4%BD%A0%E5%A5%BD%20%E4%B8%96%E7%95%8C&lang=zh"
```

## 相关概念

- [mdurl 简介](/concepts/00-introduction.md)
- [URL 数据结构](/concepts/01-url-data-structure.md)
- [URL 解析与格式化](/concepts/02-parse-and-format.md)
- [URL 编码与解码](/concepts/03-encode-and-decode.md)
