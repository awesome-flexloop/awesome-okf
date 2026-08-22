---
type: spec
title: mdurl 架构洞察
description: mdurl 源码洞察记录
tags:
- mdurl
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdurl-source
  resource: /references/mdurl-source.md
  title: mdurl mdurl-source
---

# mdurl 架构洞察

> I阶段产出。基于 45 条源码事实（F-001~F-045）提炼。

## 核心洞察

### 洞察1：不可变数据 + 可变构建器的分离设计

- **陈述**：mdurl 的核心数据结构 `URL` 是不可变的 `namedtuple`（8个字段），而解析过程使用内部可变类 `MutableURL` 逐步填充各字段，最终一次性构造不可变 `URL` 返回。
- **证据**：F-011（URL 是 namedtuple）、F-042（MutableURL 初始化8个属性为 None/False）、F-045（url_parse 创建 MutableURL 解析后转为 URL 返回）
- **反常识**：Python 开发者可能期望 `URL` 是一个带方法的类，但实际上 mdurl 完全采用函数式风格——`URL` 是纯数据，所有操作（parse/format/encode/decode）都是独立函数。
- **行动**：概念文档需要明确区分"URL 数据结构"与"操作函数"两个层面，强调 URL 实例不可变，修改需要重新 parse 或构造新实例。

### 洞察2：预计算查找表 + 缓存的性能策略

- **陈述**：encode 和 decode 都使用 128 项的 ASCII 查找表（list[str]），以 exclude 字符串为 key 缓存到模块级字典。逐字符处理时通过数组下标 O(1) 查找，避免逐字符的条件判断和字符串操作。
- **证据**：F-015~F-017（decode_cache 与 get_decode_cache）、F-023~F-025（encode_cache 与 get_encode_cache）、F-016（get_decode_cache 构建0-127 ASCII查找表）
- **反常识**：查找表只覆盖 ASCII（0-127），非 ASCII 字符走慢路径（encode 用 urllib.parse.quote，decode 用 bytes.decode()）。这意味着纯 ASCII URL 处理极快，但含 Unicode 的 URL 性能下降。
- **行动**：概念文档需要解释查找表机制和缓存策略，帮助理解为什么 encode/decode 对 ASCII 输入高效。

### 洞察3：从 Node.js 移植的解析器，与标准库 urllib.parse 行为不同

- **陈述**：`_parse.py` 移植自 JavaScript mdurl，后者源自 Joyent 的 Node.js `url` 模块，并有 6 处明确记录的行为差异。解析逻辑是一个大型手写状态机（约180行），不使用 Python 标准库的 `urllib.parse`。
- **证据**：F-006（JS mdurl 的 Python 端口）、F-028（6处与 Node.js 的差异：无前导斜杠、反斜杠不替换、尾部冒号归路径、不自动编码、无 parseQueryString、移除冗余属性）、F-043（MutableURL.parse 方法的完整解析流程）、F-029~F-041（预编译正则和特殊协议字典）
- **反常识**：Python 标准库已有 `urllib.parse.urlparse`，但 mdurl 没有使用它——因为 markdown-it 需要的 URL 解析行为（特别是 CommonMark/GFM 规范中对 autolink 和 link 目的地的解析规则）与标准库不同。例如 mdurl 的 `slashes_denote_host` 参数默认为 False，这与 urllib.parse 的行为差异很大。
- **行动**：概念文档需要对比 mdurl 解析行为与 urllib.parse 的关键差异，解释为什么 markdown-it-py 依赖 mdurl 而非标准库。

### 洞察4：双模式编码体系——encodeURI 对应 DEFAULT，encodeURIComponent 对应 COMPONENT

- **陈述**：mdurl 提供两组编码/解码常量和默认参数：`ENCODE_DEFAULT_CHARS`/`DECODE_DEFAULT_CHARS` 保留 URL 结构字符（`;/?:@&=+$,#`等），对应 JS 的 `encodeURI`/`decodeURI`；`ENCODE_COMPONENT_CHARS`/`DECODE_COMPONENT_CHARS` 仅保留非保留字符（`-_.!~*'()`），对应 JS 的 `encodeURIComponent`/`decodeURIComponent`。
- **证据**：F-013/F-014（DECODE_DEFAULT_CHARS vs DECODE_COMPONENT_CHARS）、F-021/F-022（ENCODE_DEFAULT_CHARS vs ENCODE_COMPONENT_CHARS）、F-017（decode 默认用 DECODE_DEFAULT_CHARS）、F-025（encode 默认用 ENCODE_DEFAULT_CHARS）
- **反常识**：`DECODE_COMPONENT_CHARS` 是空字符串，意味着 decode(component=True) 会解码所有百分号编码序列（不排除任何字符）；而 DEFAULT 模式会排除 `;/?:@&=+$,#` 这些 URL 结构字符不对其解码。这与 encode 的行为对称但方向相反。
- **行动**：概念文档需要清晰区分两种编码模式的使用场景。

## 知识地图

### 文档清单

**concepts/（4篇）**
1. `00-introduction.md` — mdurl 简介：是什么、从何而来、在 markdown-it-py 生态中的角色。覆盖 F-001~F-007。
2. `01-url-data-structure.md` — URL 数据结构：URL namedtuple 的8个字段语义、MutableURL 内部类、不可变设计。覆盖 F-008~F-012、F-042。
3. `02-parse-and-format.md` — URL 解析与格式化：parse() 函数、slashes_denote_host 参数、MutableURL.parse 流程、format() 逆向拼接、与 urllib.parse 的差异。覆盖 F-027~F-045。
4. `03-encode-and-decode.md` — URL 编码与解码：百分号编码原理、DEFAULT vs COMPONENT 两种模式、查找表缓存机制、UTF-8多字节处理、代理对处理。覆盖 F-013~F-026。

**examples/（1篇）**
1. `basic-usage.md` — 基础使用：parse→修改→format 流水线、encode/decode 示例、slashes_denote_host 效果对比。覆盖全部核心API。

**references/（1篇）**
1. `mdurl-source.md` — 源码路径映射：6个核心文件路径、职责、关键函数/类/常量表。覆盖 F-001~F-045。

### 学习路径

```
00-introduction（了解是什么）
    ↓
01-url-data-structure（理解核心数据结构）
    ↓
02-parse-and-format（掌握解析与格式化）  ←→  examples/basic-usage（动手实践）
    ↓
03-encode-and-decode（深入编码解码机制）
```

建议学习顺序：先了解 URL 数据结构（01），再学解析格式化（02），最后学编码解码（03）。示例文档配合 02 和 03 一起阅读。
