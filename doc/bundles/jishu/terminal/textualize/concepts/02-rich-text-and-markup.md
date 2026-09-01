---
type: Concept
title: Text 对象与控制台标记语言
description: Text 是 Rich 核心可渲染文本对象，配合 markup 标记语言实现带样式的富文本输出。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources:
  - id: "rich"
    resource: "/references/rich.md"
    title: "Rich 仓库信源登记"
---
# Text 对象与控制台标记语言

## 概述

本概念文档介绍 Rich 的两个基础层：一是**控制台标记语言（markup）**——写在字符串里的 `[bold red] ... [/]` 标签方言，用于声明式地给文本着色/加样式；二是 **Text 对象**——Rich 内部承载富文本的可渲染单位，把纯文本拆成单元格长度、样式区间（`Span`）与渲染方法，是 Console 最终逐段输出的最小实体。两者通过 `markup.render()` → `Text` 闭环衔接。

> 事实范围：F-R-007..011（markup.py）+ F-R-027..035（text.py）。

## 控制台标记语言 markup

`markup.py` 负责把带标签的字符串解析成 `Text`，核心实现是两条正则加一个渲染函数。

### 标签语法

模块级正则 `RE_TAGS = re.compile(r"""((\\*)\[([a-z#/@][^[]*?)])""", re.VERBOSE)` 匹配标签主体，`RE_HANDLER` 则匹配回调型参数。标签由 `Tag` 表示：

- `class Tag(NamedTuple)`，字段 `name: str`、`parameters: Optional[str]`；
- 属性 `markup` 返回 `"[{name}]"` 或 `"[{name}={parameters}]"`。

常见标签形如 `[bold]`、`[red]`、`[#00ff00]`（十六进制色）、`[link=URL]`（`@` 开头回调）。属性从 `=` 处拆分：`partition("=")` 得到 name 与 parameters（F-R-010）。

### 开标签与闭合标签

- `[name]` 为开标签，`[/name]` 为闭合标签；
- 解析器以 `/` 开头判断闭合：显式闭合调用 `pop_style`，非显式闭合调用 `pop()` 隐式回退；若标签失配则抛 `MarkupError`（F-R-011）。

### 转义（escape）

`escape(markup: str, _escape=...) -> str`：把 `[...]` 标签形态的反斜杠加倍转义，使其作为字面文本而非标签输出；若结果以单个 `\` 结尾再补一个 `\`（F-R-009）。

```python
from rich.markup import escape
print(escape("foo[bar]"))  # 中括号被当作文本而非标签
```

### 解析与渲染（render）

`render(markup, style: Union[str, Style] = "", emoji: bool = True, emoji_variant=None) -> Text`（F-R-011）：

- 无 `[` 时直接返回 `Text(...)`，不走标签解析；
- 否则维护 `style_stack: List[Tuple[int, Tag]]` 与备选的 `spans: List[Span]`，随开/闭标签进出栈；
- 以 `@` 开头的开标签参数经 `ast.literal_eval` 求值为调用参数；
- 结束时 `text.spans = sorted(spans[::-1], key=attrgetter("start"))`，保证 span 按起始位置有序。

### `_parse` 迭代协议

`_parse(markup)` 基于 `RE_TAGS.finditer` 产出 `(position, text, tag)` 三元组；转义反斜杠数量按 `divmod(len(escapes), 2)` 拆分（成对反斜杠转义、单个残留按字面处理）（F-R-010）。

### emoji 支持

`render` 的 `emoji: bool = True` 参数控制标记文本中的 emoji 别名（如 `:heart:`）是否渲染，`emoji_variant` 指定 emoji 变体。emoji 与 markup 同属 `rich/` 包的工具模块（`emoji.py`），此处给出其开关语义与入口参数。

## Text 对象模型

`Text` 继承 `JupyterMixin`，是 Rich 富文本的核心容器（F-R-028）。

### Text 构造与内部存储

构造签名（F-R-028）：

```python
Text(
    text: str = "",
    style: Union[str, Style] = "",
    *,
    justify=None,
    overflow=None,
    no_wrap=None,
    end="\n",
    tab_size=None,
    spans=None,
)
```

- `__slots__` 为 `_text, style, justify, overflow, no_wrap, end, tab_size, _spans, _length`；
- 构造时对输入执行 `strip_control_codes(text)`，`_text` 存为单元素列表（便于随后的切片/形变操作）。

### Span 与样式区间

`class Span(NamedTuple)`（F-R-027）：字段 `start: int`、`end: int`、`style: Union[str, Style]`；方法 `split(offset)`、`move(offset)`、`right_crop(offset)`、`extend(cells)`；`__bool__` 返回 `end > start`（空区间视为假）。一个 Span 声明 `[_text 的 start, end)` 一段字符使用的样式，不变更原始文本字符，只在渲染时叠加样式。

### 工厂类方法（classmethod）

`Text` 提供工厂（F-R-029）：`from_markup(...)`、`from_ansi(...)`、`styled(...)`、`assemble(...)`——分别从 markup 字符串、ANSI 转义序列、预置样式与零散片段装配文本。

### 样式操作

`stylize(...)`、`stylize_before(...)`、`apply_meta(...)`、`on(meta=None, **handlers)`、`get_style_at_offset(console, offset)`、`extend_style(spaces)`、`copy_styles(text)`（F-R-030）。

### 高亮

`highlight_regex(...)`、`highlight_words(...)`（F-R-031）——regex/词语级按位置追加 Span 样式区间，供 `Highlighter`（见 `/concepts/04-rich-highlighters.md`）复用。

### 追加与拼接

`append(...)`、`append_text(text)`、`append_tokens(...)`、`join(lines: Iterable[Text]) -> Text`、`__add__(self, other)`（F-R-033）。

### 形变方法

`truncate(...)`、`pad(count, character=" ")`、`pad_left(...)`、`pad_right(...)`、`align(align, width, character=" ")`、`rstrip()`、`rstrip_end(size)`、`set_length(new_length)`、`right_crop(amount=1)`、`expand_tabs(tab_size=None)`、`remove_suffix(suffix)`（F-R-034）。

### 换行、适配与分片

- `wrap(self, console, width, *, justify=None, overflow=None, tab_size=8, no_wrap=None) -> Lines`；
- `fit(self, width) -> Lines`；
- `split(...)`、`divide(self, offsets) -> Lines`；
- `detect_indentation() -> int`、`with_indent_guides(...)`（F-R-035）。

### 渲染与测量

`Text` 实现 `__rich_console__(self, console, options)`、`__rich_measure__(self, console, options)` 与 `render(self, console, end: str = "") -> Iterable[Segment]`（F-R-032）——将文本区间样式转成可输出段，供 Console 消费。

## Style 与 Span 边界

- **Style**（`style.py`，见 `/concepts/03-rich-style-system.md`）描述「长什么样」：颜色 + 位掩码布尔效果，是可复用的样式定义对象；
- **Span**（`text.py`）描述「在哪一段生效」：`[start, end)` 字符区间 + 一个 Style 引用；
- **Text** 是「外壳」：保存全体字符与 `_spans` 列表，渲染时把各 Span 的 Style 叠加到对应区间上。

一句话区分：Style 是「样式值」，Span 是「样式区间绑定」，Text 是「区间绑定的载体」。markup 解析的本质就是生成 `(start, end, style)` 型的 Span，再由 Text 统一渲染。

## 相关概念

- 样式值本体与位掩码存储：[/concepts/03-rich-style-system.md](03-rich-style-system.md)
- Console 如何消费 Text 并输出：[/concepts/01-rich-console-and-protocol.md](01-rich-console-and-protocol.md)
- 基于 Span 区间的正则/词语高亮：[/concepts/04-rich-highlighters.md](04-rich-highlighters.md)
- 信源登记：[/references/rich.md](/references/rich.md)