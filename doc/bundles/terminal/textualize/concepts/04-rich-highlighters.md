---
type: Concept
title: Highlighter 体系：从正则到 ReprHighlighter
description: Rich 高亮器分层体系，从 Highlighter/RegexHighlighter 抽象基类到 ReprHighlighter 等具体实现，阐述基于命名分组正则与 _combine_regex 组合的文本着色机制。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---

# Highlighter 体系：从正则到 ReprHighlighter

## 概述

Highlighter（高亮器）是 Rich 中对文本按语义片段**着色**的机制。`Console` 默认使用 `ReprHighlighter`，让打印到终端的对象表现内容（IP、UUID、数字、字符串、路径、URL 等）在显示时自动带上区分性配色。本文的类名/方法名均可在 `external/dao/action/Textualize/rich/rich/highlighter.py` 中直接验证。

> 注意：本文覆盖事实 **F-R-012..018**，聚焦 Rich 侧的高亮器实现。F-R-016 的 `ReprHighlighter` 与 toolong 共享同构实现，toolong 侧细节见 `/concepts/22-toolong.md`。

## 抽象基类 Highlighter 与 NullHighlighter

`class Highlighter(ABC)`（F-R-013）定义了统一的调用入口：

- `__call__(self, text: Union[str, Text]) -> Text`：传入 str 则包装为 `Text(text)`；传入 `Text` 则取 `text.copy()`；其他类型抛 `TypeError`。
- `highlight(self, text: Text) -> None`：抽象方法（`@abstractmethod`），子类实现具体的着色逻辑。

`class NullHighlighter(Highlighter)`（F-R-014）是空实现——`highlight` 方法体为空，作为"不启用高亮"的默认占位（`Console.__init__` 中 `self.highlighter = highlighter or _null_highlighter`，见 F-R-043）。

```python
from rich.highlighter import Highlighter
from rich.text import Text

class MyHighlighter(Highlighter):
    def highlight(self, text: Text) -> None:
        text.highlight_words(("TODO",), style="bold yellow")

hi = MyHighlighter()
result = hi("some TODO note")  # __call__ 内部将 str 包装为 Text 后调用 highlight
```

## 正则驱动的 RegexHighlighter

`class RegexHighlighter(Highlighter)`（F-R-015）是"以正则匹配为最小单元"的高亮器模板：

- 类变量 `highlights: ClassVar[Sequence[str]] = []`、`base_style: ClassVar[str] = ""`。
- `highlight` 对 `highlights` 中的每个正则调用 `text.highlight_regex(re_highlight, style_prefix=self.base_style)`（F-R-031 记录的 `Text.highlight_regex`），即每条正则匹配的命名分组会被赋予 `base_style + 分组名` 的样式。

`_combine_regex(*regexes: str) -> str`（F-R-012）是模块级辅助函数，返回 `"|".join(regexes)`，将多个正则用 `|` 组合成一条，供 `ReprHighlighter` 等将同类目标合并为单一正则使用。

## ReprHighlighter：repr 输出的默认高亮

`class ReprHighlighter(RegexHighlighter)`（F-R-016）`base_style = "repr."`，专用于 `__repr__` 产生的文本。其 `highlights` 序列包含三类正则（均在源码 `highlighter.py` 第 84-103 行可直接验证）：

| 分组 | 正则（部分） | 匹配目标 |
|---|---|---|
| `tag_start` / `tag_name` / `tag_contents` / `tag_end` | `(?P<tag_start><)...(?P<tag_end>>)` | 尖括号包裹的类名表现 |
| `attrib_name` / `attrib_value` | `(?P<attrib_name>[\w_]{1,50})=(?P<attrib_value>"?[\w_]+"?)?` | `name=value` 属性对 |
| `brace` | `[][{}()]` | 各类括号 |

其余为经 `_combine_regex` 合并的一条大正则，包含命名分组：

- `ipv4`、`ipv6`（含 `eui64`/`eui48`）地址
- `uuid`（8-4-4-4-12 十六进制）
- `call`（`[\w.]*?\(`，函数调用后跟括号）
- `bool_true` / `bool_false` / `none`（`True`/`False`/`None`）
- `ellipsis`（`...`）
- `number_complex`（复数 `j`）、`number`（含十六进制 `0x`）
- `path` / `filename`（文件路径分隔与文件名）
- `str`（单双三引号及 `b` 前缀字符串）
- `url`（`file|https|http|ws|wss` 协议开头的 URL）

由于 `base_style = "repr."`，上述命名的样式名依次为 `repr.ipv4`、`repr.uuid`、`repr.number`、`repr.path`、`repr.str`、`repr.url` 等。

```python
from rich.console import Console

console = Console()
console.print("IP 192.168.0.1 UUID 123e4567-e89b-12d3-a456-426614174000")
# 默认 highlighter=ReprHighlighter()，上述 IP/UUID 会被赋予 repr.ipv4 / repr.uuid 样式
```

## 其他具体高亮器

`JSONHighlighter`（F-R-017）：`base_style = "json."`，类属性 `JSON_STR = r'(?<![\\\w])(?P<str>b?".*?(?<!\\)")'`、`JSON_WHITESPACE = {" ", "\n", "\r", "\t"}`；`highlight` 先调 `super().highlight(text)` 处理字符串，再扫描字符串后随 `:` 的位置追加 `Span(start, end, "json.key")` 标记键名。

`ISO8601Highlighter`（F-R-018）：`base_style = "iso8601."`；`highlights` 为 12 条以 `^...$` 锚定的正则，命名分组含 `year`、`month`、`day`、`date`、`week`、`time`、`hour`、`minute`、`second`、`timezone`、`frac`、`ms`、`hyphen`，用于对 ISO 8601 时间戳着色。

## 相关概念

- `/concepts/01-rich-console-and-protocol.md`：`Console` 默认 `highlighter=ReprHighlighter()`、`highlight=True` 开启高亮（F-R-042/043），高亮作为渲染管线的前置环节接入。
- `/concepts/22-toolong.md`：toolong 侧与 Rich 共享同构的 `ReprHighlighter` 实现（如事实支持）。