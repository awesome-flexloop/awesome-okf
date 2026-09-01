---
type: Concept
title: "Table：Column/Row 数据模型与宽度计算"
description: 解析 Rich 表格组件 Table 的数据模型与宽度算法：Table/Column/Row 三层结构、add_column/add_row 数据流、基于 Measurement 的自适应列宽计算与 Box 边框协作。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---
# Table：Column/Row 数据模型与宽度计算

## 概述

`rich.table.Table`（F-R-052）是 Rich 的结构化二维网格渲染组件，负责把「表头 + 单元格」数据渲染为带边框、对齐、样式与自适应列宽的终端表格。它建立在三个数据模型之上：结构 `Table`（继承 `JupyterMixin`，持有列头与边框配置）、`Column`（每列的外观与测量属性）与 `Row`（行的样式与分段标记）。本文依事实 F-R-050..056 拆解其构造、默认值、数据流，以及**基于 `Measurement` 的自适应列宽计算**这一核心算法。

## Table 构造与默认值

`Table(*headers, ...)` 把每个 `str` 类型的位置参数经 `self.add_column(header=header)` 转换为列（F-R-052），因此既可以传 `Column` 对象以显式控制，也可以直接传字符串快速声明列。

```python
from rich.table import Table

# 直接传字符串头（内部转为 add_column）
table = Table("序号", "名称")

# 传 Column 对象以获得更细控制
from rich.table import Column
t2 = Table(Column("k", style="bold", justify="center"))
```

构造关键字参数的默认值体现了表格渲染的关键偏好（F-R-052）：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `box` | `box.HEAVY_HEAD` | 默认采用「重点表头」边框（见 Box 一文的 18 种边框） |
| `padding` | `(0, 1)` | 单元格上下左右内边距（top,right,bottom,left） |
| `show_header` / `show_footer` | `True` / `False` | 表头默认显示、表脚默认隐藏 |
| `show_edge` / `show_lines` | `True` / `False` | 外框默认绘制、内部横线默认不绘制 |
| `expand` | `False` | 默认不强制铺满 console 宽度（见「宽度计算」） |
| `header_style` / `footer_style` | `"table.header"` / `"table.footer"` | 表头表脚引用默认样式表样式名 |
| `title_justify` / `caption_justify` | `"center"` | 标题/说明默认居中 |

`Table.grid(*headers, padding=0, collapse_padding=True, pad_edge=False, expand=False)` 是快速构建「网格」表格的 classmethod（F-R-053），内部以 `box=None, show_header=False, show_footer=False, show_edge=False` 构造，因此无边框、无表头表脚，常用于组装多栏并排布局（如 `Progress.make_tasks_table` 的应用模式）。

## Column 数据模型

`Column` 是 `@dataclass`，携带列的全部外观与测量声明字段（F-R-050）：

```python
Column(
    header="", footer="",              # 表头/表脚文本
    header_style="", footer_style="",  # 表头表脚样式
    style="",                          # 单元格默认样式
    justify="left", vertical="top",    # 水平/垂直对齐
    overflow="ellipsis",               # 溢出省略策略
    width=None, min_width=None,
    max_width=None,
    ratio=None,                        # 弹性分配比例权重
    no_wrap=False, highlight=False,
)
```

关键属性与方法（F-R-050）：

- `_cells: List[Any]`：实际单元格数据容器，默认 `field(default_factory=list)`；`cells` 属性暴露之。
- `flexible` 属性：返回 `self.ratio is not None`——当且仅当设置了 `ratio` 时该列参与宽度弹性分配。
- `copy()`：经 `dataclasses.replace(self, _cells=[])` 复制列配置但**清空单元格数据**。

## Row 数据模型与 add_row

`Row` 是 `@dataclass`，仅两个字段（F-R-051）：`style: Optional[StyleType] = None` 与 `end_section: bool = False`。`end_section` 用于标记「分段行」——其后的行以粗横线分隔。

`Table.add_row(*renderables, style=None, end_section=False) -> None`（F-R-055）内部调用 `add_cell`，把每个 renderable 追加到对应 `Column._cells` 列表；`style` 就地包装为一个 `Row(style=style)`，`end_section=True` 同样保留为 `Row.end_section`。因此 `Table` 采用"列优先"存储：数据按列存于各列 `_cells`，行是渲染时按行索引取各列第 i 个单元格拼装出来的逻辑视图。

```python
table = Table("名称", "数量")
table.add_column("价格", justify="right")   # 运行时动态加列
table.add_row("苹果", 3, "¥2.5", style="green")
table.add_row("橙子", 5, "¥1.8")
```

`add_column(header="", footer="", *, header_style=None, ... render 参数与 Column 对应)`（F-R-054）允许在构造后继续追加列，其行为等价于向 `Table.columns` 追加一个构造好的 `Column`。`add_section()`（F-R-055）插入一个分段行。

## 宽度计算

表格渲染在 `__rich_console__` / `__rich_measure__` 中启动，宽度自适应由 `_calculate_column_widths(...)`（F-R-056）完成，核心思路是**逐列测量 + 总量约束分配**：

1. **逐列测量**：用 `Measurement.get(console, options, header)` 与各单元格文本测出每列的最小/最大测量值，`_measure_column(...)`（F-R-056）据此得到每列的自然宽度区间。
2. **内边距**：`_get_padding_width(column_index)`（F-R-056）按 `padding` 配置累加每列水平内边距。
3. **弹性分配**：对设置了 `ratio` 的 `flexible` 列，把剩余宽度按比例权重分配（`_extra_width` 描述总可分配额度），使表格在 `expand=True` 或存在剩余空间时铺满目标宽度；`_collapse_widths(...)`（F-R-056）用于在总宽不足时压缩各列至最小宽度。
4. **总量约束**：`__rich_measure__` 用 `Measurement` 汇总各列最小/最大与表头，交由 `Console` 决定最终渲染宽度；`expand` 与 `width` 参数携手决定表格是否拉伸。

`row_count` 属性（F-R-056）返回当前行数，为 Table 自动化（如求解每列最佳宽度）提供统计入口。因为 `Table` 继承 `Measureable`/`JupyterMixin` 同时实现 `__rich_measure__` 与 `__rich_console__`（F-R-056），它既是"可测量的"，也是"可渲染的"，从而能被 Console 纳入统一布局计算。

## 与渲染协议的关系

`Table` 的宽度自适应是测量协议（`Measurement`，F-R-003..006）在复合组件上的落地：单行文本经 `Text` 的测量返回 `Measurement(minimum, maximum)`，`Table` 把这些单元测量聚合成列宽，再经 Console 的 `ConsoleOptions.max_width` 约束收敛。因此理解 Table 的宽度算法，需要先理解 /concepts/05-rich-segment-and-measure.md 中的测量原语。

## 相关概念

- /concepts/05-rich-segment-and-measure.md —— Measurement 测量原语，Table 宽度计算的基础
- /concepts/07-rich-panel-and-box.md —— Box 边框模型，Table 的 `box` 参数来源
- /concepts/01-rich-console-and-protocol.md —— Console 渲染入口与测量协议
- /references/rich.md —— Rich 仓库信源登记