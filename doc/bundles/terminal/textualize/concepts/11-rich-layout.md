---
type: Concept
title: Layout 布局系统：row/column 分割器与区域映射
description: Rich 的 Layout 布局系统：以 Row/Column 分割器将矩形区域递归切分为子布局，并通过 Region 区域映射（RegionMap）把每个 Layout 映射到具体绘制区域。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---

# Layout 布局系统：row/column 分割器与区域映射

## 概述

`Layout` 是 Rich 用于**把固定区域递归划分成行或列**的可渲染容器。核心机制是一对**分割器**（`RowSplitter`/`ColumnSplitter`）：把父 `Layout` 所占的矩形区域（`Region`），按比例拆分成若干**子区域**，再交给各自的子 `Layout`，最终形成一棵以"区域映射"组织的渲染树。本文覆盖事实 **F-R-081..084**，代码位于 `rich/layout.py`，并依赖 `rich/_ratio.py` 的 `ratio_resolve` 解析弹性比例。

## 数据与异常类型

`class LayoutRender(NamedTuple)`（F-R-081）：字段 `region: Region`、`render: List[List[Segment]]`——记录单个布局的绘制区域与渲染行（每行是 segment 列表）。

类型别名与异常：

- `RegionMap = Dict["Layout", Region]`：布局 → 矩形区域的映射。
- `RenderMap = Dict["Layout", LayoutRender]`：布局 → 渲染结果的映射。
- 异常 `class LayoutError(Exception)` 与 `class NoSplitter(LayoutError)`：未知分割器名时抛出。

```python
from rich.layout import Layout, LayoutError

r = Layout()
try:
    r.split(Layout(), Layout(), splitter="grid")  # 不存在的 splitter
except LayoutError as e:
    print(type(e).__name__, e)  # NoSplitter
```

## 分割器：Splitter / RowSplitter / ColumnSplitter

`class Splitter(ABC)`（F-R-082），抽象基类：

- 类属性 `name: str = ""`。
- 抽象方法 `get_tree_icon() -> str`（`tree()` 展示用的图标）与 `divide(self, children: Sequence[Layout], region: Region) -> Iterable[Tuple[Layout, Region]]`（把区域切分给子布局并产出 `(子布局, 子区域)`）。

两个内置实现：

- `class RowSplitter(Splitter)`：`name = "row"`，`get_tree_icon` 返回 `"[layout.tree.row]⬌"`。`divide` 用 `ratio_resolve(width, children)` 横向计算各子行宽度，按 `offset` 递增产出水平相邻的 `Region(x+offset, y, child_width, height)`——**左右并排**。
- `class ColumnSplitter(Splitter)`：`name = "column"`，图标 `"[layout.tree.column]⬍"`。`divide` 用 `ratio_resolve(height, children)` 纵向计算各子列高度，按 `offset` 递增产出上下堆叠的 `Region(x, y+offset, width, child_height)`——**上下排布**。

> 命名容易混淆：`RowSplitter` 产出"行"（子宽度横向切，布局水平并排），`ColumnSplitter` 产出"列"（子高度纵向切，布局垂直堆叠）。

## Layout：构造与分割 API

`class Layout`（`@rich_repr`）构造签名（F-R-083）：

```python
Layout(renderable=None, *, name=None, size=None,
       minimum_size=1, ratio=1, visible=True)
```

- 类属性 `splitters = {"row": RowSplitter, "column": ColumnSplitter}`，注册可用分割器（按名查表）。
- `renderable` 为 None 时以 `_Placeholder(self)` 占位。
- 默认 `self.splitter = self.splitters["column"]()`——默认采取垂直堆叠的列分割器。

分割与更新 API（F-R-084）：

- `split(self, *layouts, splitter="column")`：把本布局切成子布局数组；`splitter` 传 `Splitter` 实例或名字——未知名抛 `NoSplitter`；非 `Layout` 参数自动包为 `Layout`，然后 `self._children[:] = _layouts` 整体替换子布局。
- `add_split(*layouts)`：追加子布局到已有分割（`_children.extend`）。
- `split_row(*layouts)`：`split(*layouts, splitter="row")` 快捷入口。
- `split_column(*layouts)`：`split(*layouts, splitter="column")` 快捷入口。
- `unsplit()`：撤销所有子分割。
- `update(renderable)`：更新本布局的渲染内容。
- `refresh_screen(console, layout_name)`：仅重绘指定 Layout 的屏幕区域。
- 查询：`get(name) -> Optional[Layout]`、`__getitem__(name)`；展示 `tree()`。

```python
from rich.layout import Layout

layout = Layout()
# 一列收个 header，一列里并排放两个子面板
layout.split_column(
    Layout(name="header", ratio=1),
    Layout(name="body", ratio=3).split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1),
    ),
)
```

## 区域映射：render / _make_region_map

- `render(console, options) -> RenderMap`：从根布局递归调用 `_make_region_map` 得到 `RegionMap`，再查 `RenderMap` 产出各布局的渲染结果。
- `_make_region_map(width, height) -> RegionMap`（F-R-084）：对每个含分割器的布局，调用其 `splitter.divide(children, region)` 把宽高展开成各子布局的区域矩形，自顶向下填充映射表。
- `__rich_console__`：以 `region` 为裁剪框渲染出对齐的 segment 行。

属性 `renderable`、`children`（子布局列表）、`map`（区域映射，供按名取区域）。

`Layout` 把这些原语组合成布局树：`split_row`/`split_column` 决定树形结构，`ratio`/`size`/`minimum_size` 参与 `ratio_resolve` 的比例分配，最终 `render` 把树展平成一张 `RegionMap` 驱动绘制。

## 相关概念

- `/concepts/01-rich-console-and-protocol.md`：`Segment`（F-R-024）是 `LayoutRender.render` 的行单元；`Console.render`（F-R-046）最终消费这些 renderable。
- `/concepts/05-rich-segment-and-measure.md`：`Segment` 流式批处理（F-R-025）支撑 `LayoutRender` 按行渲染；测量协议用于布局宽度分配。
- `rich/panel.py`：`Panel`（F-R-085）常作为 `Layout` 子节点的常见可渲染内容。