---
type: spec
title: mdurl 事实清单
description: mdurl 源码事实清单
tags:
- mdurl
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: mdurl-source
  resource: /references/mdurl-source.md
  title: mdurl mdurl-source
---

# mdurl 事实清单

> R阶段产出。所有事实编号 F-xxx，仅记录源码中可验证的客观内容，不含推断。

## 项目元数据

- F-001: 版本号为 `0.1.2`，定义于 `pyproject.toml` L7 与 `src/mdurl/__init__.py` L12
- F-002: `requires-python = ">=3.10"`，定义于 `pyproject.toml` L13
- F-003: 许可证为 MIT，定义于 `pyproject.toml` L16 与 `LICENSE` 文件；版权归属：Copyright (c) 2015 Vitaly Puzrin, Alex Kocharin; Copyright (c) 2021 Taneli Hukkinen
- F-004: 构建系统使用 `flit_core>=3.2.0,<4`，定义于 `pyproject.toml` L2
- F-005: `pyproject.toml` 中 `description = "Markdown URL utilities"`，keywords = `["markdown", "commonmark"]`
- F-006: README.md 声明 mdurl 是 JavaScript mdurl 包的 Python 端口
- F-007: mdurl 无第三方运行时依赖，仅使用 Python 标准库（`urllib.parse`, `collections`, `re`, `functools`）

## 源码结构

- F-008: 源码位于 `src/mdurl/` 目录，包含 6 个 Python 文件：`__init__.py`, `_url.py`, `_decode.py`, `_encode.py`, `_format.py`, `_parse.py`，以及 `py.typed` 标记文件
- F-009: `__init__.py` 通过 `__all__` 导出 10 个公共名称：`decode`, `DECODE_DEFAULT_CHARS`, `DECODE_COMPONENT_CHARS`, `encode`, `ENCODE_DEFAULT_CHARS`, `ENCODE_COMPONENT_CHARS`, `format`, `parse`, `URL`
- F-010: `__init__.py` 从各子模块导入并重新导出：`decode`/`DECODE_DEFAULT_CHARS`/`DECODE_COMPONENT_CHARS` 来自 `_decode`，`encode`/`ENCODE_DEFAULT_CHARS`/`ENCODE_COMPONENT_CHARS` 来自 `_encode`，`format` 来自 `_format`，`parse` 是 `_parse.url_parse` 的别名，`URL` 来自 `_url`

## URL 数据结构（_url.py）

- F-011: `URL` 在运行时是 `collections.namedtuple`，名称为 `"URL"`，字段列表为 `["protocol", "slashes", "auth", "port", "hostname", "hash", "search", "pathname"]`，定义于 `_url.py` L20-31
- F-012: `URL` 在 TYPE_CHECKING 模式下被声明为 `NamedTuple` 子类，类型标注为：`protocol: str | None`, `slashes: bool`, `auth: str | None`, `port: str | None`, `hostname: str | None`, `hash: str | None`, `search: str | None`, `pathname: str | None`，定义于 `_url.py` L9-17

## URL 解码（_decode.py）

- F-013: 常量 `DECODE_DEFAULT_CHARS = ";/?:@&=+$,#"`，定义于 `_decode.py` L11
- F-014: 常量 `DECODE_COMPONENT_CHARS = ""`（空字符串），定义于 `_decode.py` L12
- F-015: 模块级字典 `decode_cache: dict[str, list[str]] = {}`，定义于 `_decode.py` L14
- F-016: 函数 `get_decode_cache(exclude: str) -> Sequence[str]`：遍历 0-127 的 ASCII 码构建查找表（初始 `cache[i] = chr(i)`），然后将 `exclude` 字符串中每个字符对应位置设为 `"%" + 大写两位十六进制` 形式（即保留其百分号编码），缓存结果到 `decode_cache[exclude]`，定义于 `_decode.py` L17-32
- F-017: 函数 `decode(string: str, exclude: str = DECODE_DEFAULT_CHARS) -> str`：调用 `get_decode_cache(exclude)` 获取查找表，使用 `functools.partial` 绑定 cache 参数，通过 `re.sub(r"(%[a-f0-9]{2})+", repl_func, string, flags=re.IGNORECASE)` 替换所有百分号编码序列，定义于 `_decode.py` L37-40
- F-018: 函数 `repl_func_with_cache(match: re.Match, cache: Sequence[str]) -> str`：逐字节处理匹配到的百分号编码序列：
  - 单字节（`b1 < 0x80`）：直接查 cache 表输出，前进3字符
  - 2字节UTF-8（`(b1 & 0xE0) == 0xC0`，且后续有足够字符）：检查 b2 的续字节标记 `(b2 & 0xC0) == 0x80`，通过 `bytes((b1,b2)).decode()` 解码，失败输出两个 `\ufffd`
  - 3字节UTF-8（`(b1 & 0xF0) == 0xE0`，且后续有足够字符）：检查 b2、b3 的续字节标记，通过 `bytes((b1,b2,b3)).decode()` 解码，失败输出三个 `\ufffd`
  - 4字节UTF-8（`(b1 & 0xF8) == 0xF0`，且后续有足够字符）：检查 b2、b3、b4 的续字节标记，通过 `bytes((b1,b2,b3,b4)).decode()` 解码，失败输出四个 `\ufffd`
  - 不满足以上条件时输出单个 `\ufffd` 并前进3字符，定义于 `_decode.py` L43-108

## URL 编码（_encode.py）

- F-019: 常量 `ASCII_LETTERS_AND_DIGITS` 为 `"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"`，定义于 `_encode.py` L9-11
- F-020: 常量 `HEXDIGITS = "0123456789abcdefABCDEF"`，定义于 `_encode.py` L12
- F-021: 常量 `ENCODE_DEFAULT_CHARS = ";/?:@&=+$,-_.!~*'()#"`，定义于 `_encode.py` L14
- F-022: 常量 `ENCODE_COMPONENT_CHARS = "-_.!~*'()"`，定义于 `_encode.py` L15
- F-023: 模块级字典 `encode_cache: dict[str, list[str]] = {}`，定义于 `_encode.py` L17
- F-024: 函数 `get_encode_cache(exclude: str) -> Sequence[str]`：遍历 0-127 的 ASCII 码构建查找表，字母数字字符保留原样，其他 ASCII 字符设为百分号编码形式，然后将 `exclude` 字符串中每个字符对应位置设为字符本身（即不编码），缓存结果到 `encode_cache[exclude]`，定义于 `_encode.py` L22-41
- F-025: 函数 `encode(string: str, exclude: str = ENCODE_DEFAULT_CHARS, *, keep_escaped: bool = True) -> str`：逐字符处理输入字符串：
  - `keep_escaped=True` 且当前字符是 `%`（0x25）且后两字符为十六进制数字时，保留整个 `%XX` 序列不编码
  - ASCII 字符（`code < 128`）查 cache 表输出
  - Unicode 代理对（`0xD800 <= code <= 0xDFFF`）：高代理（0xD800-0xDBFF）后跟低代理（0xDC00-0xDFFF）时，合并后调用 `urllib.parse.quote`（即 `encode_uri_component`）编码；否则输出 `%EF%BF%BD`（U+FFFD 的百分号编码）
  - 其他非 ASCII 字符调用 `encode_uri_component(string[i])` 编码
  定义于 `_encode.py` L50-89
- F-026: `encode` 函数从 `urllib.parse` 导入 `quote` 并别名为 `encode_uri_component`，定义于 `_encode.py` L3

## URL 格式化（_format.py）

- F-027: 函数 `format(url: URL) -> str`：按顺序拼接 URL 各组件：`url.protocol`（或空串）→ `"//"`（若 `url.slashes` 为 True）→ `url.auth + "@"`（若 auth 非 None）→ hostname（含 `:` 时加方括号 `[hostname]`，否则直接输出 hostname 或空串）→ `":" + url.port`（若 port 非 None）→ `url.pathname`（或空串）→ `url.search`（或空串）→ `url.hash`（或空串），定义于 `_format.py` L8-25

## URL 解析（_parse.py）

- F-028: `_parse.py` 文件头版权声明源自 Joyent Node.js `url` 模块，注释列出 6 处与 Node.js 原始实现的差异：(1)路径无前导斜杠 (2)反斜杠不替换为正斜杠 (3)尾部冒号作为路径一部分 (4)结果对象中无 URL 编码 (5)无 `parseQueryString` 参数 (6)移除了 host/path/query 等冗余属性
- F-029: 正则 `PROTOCOL_PATTERN = re.compile(r"^([a-z0-9.+-]+:)", flags=re.IGNORECASE)`，定义于 `_parse.py` L53
- F-030: 正则 `PORT_PATTERN = re.compile(r":[0-9]*$")`，定义于 `_parse.py` L54
- F-031: 正则 `SIMPLE_PATH_PATTERN = re.compile(r"^(//?(?!/)[^?\s]*)(\?[^\s]*)?$")`，定义于 `_parse.py` L57
- F-032: 元组 `DELIMS = ("<", ">", '"', "\x60", " ", "\r", "\n", "\t")`，定义于 `_parse.py` L61
- F-033: 元组 `UNWISE = ("{", "}", "|", "\\", "^", "`") + DELIMS`，定义于 `_parse.py` L64
- F-034: 元组 `AUTO_ESCAPE = ("'",) + UNWISE`，定义于 `_parse.py` L67
- F-035: 元组 `NON_HOST_CHARS = ("%", "/", "?", ";", "#") + AUTO_ESCAPE`，定义于 `_parse.py` L72
- F-036: 元组 `HOST_ENDING_CHARS = ("/", "?", "#")`，定义于 `_parse.py` L73
- F-037: 常量 `HOSTNAME_MAX_LEN = 255`，定义于 `_parse.py` L74
- F-038: 正则 `HOSTNAME_PART_PATTERN = re.compile(r"^[+a-z0-9A-Z_-]{0,63}$")`，定义于 `_parse.py` L75
- F-039: 正则 `HOSTNAME_PART_START = re.compile(r"^([+a-z0-9A-Z_-]{0,63})(.*)$")`，定义于 `_parse.py` L76
- F-040: `HOSTLESS_PROTOCOL` 是 `collections.defaultdict(bool)`，包含键 `"javascript"` 和 `"javascript:"` 映射为 `True`，定义于 `_parse.py` L80-86
- F-041: `SLASHED_PROTOCOL` 是 `collections.defaultdict(bool)`，包含键 `"http"`, `"https"`, `"ftp"`, `"gopher"`, `"file"` 及其带冒号版本（`"http:"`, `"https:"`, `"ftp:"`, `"gopher:"`, `"file:"`）映射为 `True`，定义于 `_parse.py` L88-102
- F-042: 类 `MutableURL`：`__init__(self)` 初始化 8 个实例属性：`protocol=None`, `slashes=False`, `auth=None`, `port=None`, `hostname=None`, `hash=None`, `search=None`, `pathname=None`，定义于 `_parse.py` L105-114
- F-043: 方法 `MutableURL.parse(self, url: str, slashes_denote_host: bool) -> MutableURL`：解析流程如下（定义于 `_parse.py` L116-283）：
  1. 对输入 `url` 调用 `strip()` 修剪空白
  2. 若 `slashes_denote_host=False` 且 URL 不含 `#`，尝试 `SIMPLE_PATH_PATTERN` 快速路径匹配，成功则设置 pathname 和 search 后返回
  3. 用 `PROTOCOL_PATTERN` 匹配协议部分，若匹配则设置 `self.protocol`，从 rest 中移除协议，记录 `lower_proto`
  4. 判断 slashes：若 `slashes_denote_host=True` 或有协议或匹配 `//[^@/]+@[^@/]+` 模式，检查 rest 是否以 `//` 开头；若以 `//` 开头且协议不是 HOSTLESS_PROTOCOL，则设置 `self.slashes=True`，rest 去掉前两个字符
  5. 若协议不是 HOSTLESS_PROTOCOL 且（有 slashes 或有协议且不是 SLASHED_PROTOCOL），则解析主机部分：
     a. 在 rest 中查找第一个 `HOST_ENDING_CHARS`（`/`, `?`, `#`）的位置 `host_end`
     b. 根据 `host_end` 确定 `@` 的位置：`host_end==-1` 时用 `rfind("@")`，否则在 `0` 到 `host_end` 范围内 `rfind("@")`
     c. 若有 `@`，`@` 前部分为 auth，设置 `self.auth`，rest 去掉 auth 部分
     d. 在剩余 rest 中查找第一个 `NON_HOST_CHARS` 的位置作为 host 结束位置
     e. 若 host 末尾是 `:`，host_end 减 1
     f. 调用 `self.parse_host(host)` 提取 port 和 hostname
     g. hostname 验证：非 IPv6（不以 `[` 开头或以 `]` 结尾）时，按 `.` 分割 hostname，逐段用 `HOSTNAME_PART_PATTERN` 验证；含非 ASCII 字符时替换为 `x` 后再验证；不合法部分截断到 pathname 中
     h. hostname 长度超过 255 时设为空字符串
     i. IPv6 地址去掉首尾方括号
  6. 从尾部解析：先找 `#` 提取 hash（含 `#`），再找 `?` 提取 search（含 `?`），剩余为 pathname
  7. 若协议是 SLASHED_PROTOCOL 且有 hostname 且 pathname 未设置，则设为空字符串
- F-044: 方法 `MutableURL.parse_host(self, host: str) -> None`：用 `PORT_PATTERN` 在 host 末尾匹配端口号（`:数字`），若匹配且端口部分不是单纯的 `:`，设置 `self.port`（去掉开头冒号），剩余部分设为 `self.hostname`，定义于 `_parse.py` L285-293
- F-045: 函数 `url_parse(url: URL | str, *, slashes_denote_host: bool = False) -> URL`：若 `url` 已是 `URL` 实例则直接返回；否则创建 `MutableURL()` 实例，调用 `u.parse(url, slashes_denote_host)`，然后用 MutableURL 的 8 个属性构造不可变 `URL` namedtuple 返回，定义于 `_parse.py` L296-303
