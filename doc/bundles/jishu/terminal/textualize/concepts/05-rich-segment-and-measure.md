---
type: Concept
title: Segment 渲染货币与 Measurement 测量协议
description: Rich 渲染管线的两大核心原语：Segment 作为渲染输出货币（text/style/control 三元组与流式批处理），Measurement 作为测量协议（__rich_measure__ 与 min/max 夹取）。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---

# Segment 渲染货币与 Measurement 测量协议

## 概述

`Segment` 与 `Measurement` 是 Rich 渲染管线的两大核心原语：前者是渲染的**输出货币**，承载一段带样式的文本，可批量流式处理；后者是排版前的**测量协议**，回答"这个 renderable 需要多宽"。本文覆盖事实 **F-R-003..006**（Measurement）与 **F-R-023..026**（Segment），代码位于 `rich/measure.py` 与 `rich/segment.py`。

## Measurement：可渲染对象的尺寸测量

### 数据结构：NamedTuple 三元组

`class Measurement(NamedTuple)`（F-R-003）字段 `minimum: int`、`maximum: int`，分别表示最小/最大所需宽度；属性 `span` 返回 `maximum - minimum`（宽度弹性区间）。

方法（F-R-004）用于约束与伸缩测量值：

- `normalize() -> Measurement`、`with_maximum(width: int)`、`with_minimum(width: int)`
- `clamp(min_width: Optional[int] = None, max_width: Optional[int] = None)`

```python
from rich.measure import Measurement

m = Measurement(10, 40)
assert m.span == 30  # maximum - minimum
assert m.with_maximum(20) == Measurement(10, 20)
assert m.clamp(max_width=15) == Measurement(10, 15)
```

### 测量入口：Measurement.get

`Measurement.get(cls, console, options, renderable) -> Measurement`（F-R-005，classmethod）是统一的测量入口，`Console.measure`（F-R-045）即委托给它。处理分支：

- `options.max_width < 1`：直接返回 `Measurement(0, 0)`。
- str 输入：先 `console.render_str(renderable, markup=options.markup, highlight=False)`。
- 再经 `rich_cast`（F-R-002）解析成 renderable。
- 存在 `__rich_measure__`：调用结果 `.normalize().with_maximum(_max_width)`。
- 否则：返回 `Measurement(0, _max_width)`。
- 非可渲染对象：抛 `errors.NotRenderableError`。

### 批量测量：measure_renderables

`measure_renderables(console, options, renderables: Sequence["RenderableType"]) -> Measurement`（F-R-006）：空序列返回 `Measurement(0, 0)`；否则对每个 renderable 调 `Measurement.get`，用 **minimum 最大者**与 **maximum 最大者**组合成一条——整体所需宽度取各子项的上限。

> 测量协议本身是协议式的：`Measurement.get` 会探测对象是否实现了 `__rich_measure__(self, console, options)` 方法（F-R-040 中 `Group` 即实现该协议以聚合测量其子项）。这是"测量协议"（Measure Protocol）的核心。

## Segment：渲染输出货币

### 三元组结构

`class Segment(NamedTuple)`（F-R-024）字段：

- `text: str`：本段正文
- `style: Optional[Style] = None`：样式
- `control: Optional[Sequence[ControlCode]] = None`：控制码序列

属性 `cell_length`：`control` 非空时返回 0，否则返回 `cell_len(text)`（可见显示宽度）；属性 `is_control` 判断是否为纯控制段。

`class ControlType(IntEnum)`（F-R-023）共 16 个成员，涵盖终端控制：`BELL=1`、`CARRIAGE_RETURN=2`、`HOME=3`、`CLEAR=4`、`SHOW_CURSOR=5`、`HIDE_CURSOR=6`、`ENABLE_ALT_SCREEN=7`、`DISABLE_ALT_SCREEN=8`、`CURSOR_UP=9`、`CURSOR_DOWN=10`、`CURSOR_FORWARD=11`、`CURSOR_BACKWARD=12`、`CURSOR_MOVE_TO_COLUMN=13`、`CURSOR_MOVE_TO=14`、`ERASE_IN_LINE=15`、`SET_WINDOW_TITLE=16`。

### 批量流式操作（Iterable[Segment]）

`Segment` 提供大量类方法操作 `Iterable[Segment]`（F-R-025），构成渲染的流式处理链：

| 方法 | 作用域 | 说明 |
|---|---|---|
| `split_lines` | 行切分 | 按行分割 segment 流 |
| `split_lines_terminator` / `split_and_crop_lines` | 行切分 | 带行终止/裁剪的行分割变体 |
| `adjust_line_length` | 行调整 | 整行对齐到指定长度 |
| `get_line_length(line)` / `get_shape(lines)` / `set_shape` | 几何 | 计算/设定行宽与形状 |
| `align_top` / `align_bottom` / `align_middle` | 对齐 | 单元格内垂直对齐 |
| `simplify` / `strip_links` / `strip_styles` / `remove_color` | 清理 | 简化或剥离样式/链接/颜色 |
| `divide` | 切分 | 按偏移把行切成多段，配合 `split_cells` 与 `measure` 处理回绕 |
| `filter_control` / `line` / `apply_style` | 辅助 | 过滤控制码、产出换行段、叠加样式 |

实例方法 `split_cells(cut: int) -> Tuple[Segment, Segment]` 按可见单元格数把单个 segment 切成两段，内部 `_split_cells` 带 `@lru_cache(1024 * 16)` 缓存（属 16K 条目缓存）。

```python
from rich.segment import Segment

segs = [
    Segment("hello"),
    Segment("世界", style="bold"),
    Segment("", control=(ControlType.CLEAR,)),  # control 非空时 cell_length 为 0
]
for s in segs:
    print(s.text, s.cell_length)
```

### 组合容器

`Segments`（F-R-026）：`__init__(self, segments, new_lines=False)`，实现 `__rich_console__`，把 segment 流包装为可渲染对象。`SegmentLines`：`__init__(self, lines: Iterable[List[Segment]], new_lines=False)`，同样实现 `__rich_console__`，包装"每行是 segment 列表"的行结构。

## 相关概念

- `/concepts/01-rich-console-and-protocol.md`：`Console.render`（F-R-046）把任意 renderable 逐步规约成 `Iterable[Segment]`，`Segment` 是渲染输出链的货币；`Console.measure`（F-R-045）委托 `Measurement.get` 完成测量。