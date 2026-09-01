---
type: Example
title: textual 示例：DataTable 数据表增删改与选择消息
description: 用 textual 的 DataTable 演示建表与增删改（update_cell/remove_row/clear），以及 CellSelected 等选择消息。
tags: [textualize, textual, tui, example, datatable, widget, message]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# textual 示例：DataTable 数据表增删改与选择消息

## 概述

`DataTable(ScrollView, Generic[CellType], can_focus=True)` 是 textual 内置的表格组件（`src/textual/widgets/_data_table.py:268`）：数据以 `RowKey` / `ColumnKey` 标识行列，光标移动投递 `*Highlighted` 消息、按 Enter 投递 `*Selected` 消息（F-T-096~F-T-100）。本示例演示：

- **建表**：`on_mount` 中先 `add_columns("Name", "Age", "City")` 再 `add_rows(...)` 批量加 5 行；`zebra_stripes=True` 开斑马条纹。
- **选择消息**：默认 `cursor_type="cell"` 时 Enter 触发 `CellSelected`（携带 `value`/`coordinate`/`cell_key`）；按 `t` 切到 `cursor_type="row"` 后 Enter 触发 `RowSelected`（携带 `cursor_row`/`row_key`），处理器命名为 `on_data_table_cell_selected` / `on_data_table_row_selected`。
- **增删改**：按键 `a` 加行、`d` 删光标所在行、`u` 更新光标格、`c` 清空（`clear(columns=True)`），状态显示在 `Label`，取值用 `get_cell(row_key, column_key)`。

## 可运行示例

```python
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Label

INITIAL_ROWS = [
    ("Alice", "30", "Beijing"),
    ("Bob", "25", "Shanghai"),
    ("Carol", "41", "Guangzhou"),
    ("Dave", "33", "Shenzhen"),
    ("Eve", "28", "Hangzhou"),
]


class DataTableDemo(App):
    """DataTable 增删改与选择消息示例。"""

    BINDINGS = [
        Binding("a", "add_row", "加行"),
        Binding("d", "delete_row", "删行"),
        Binding("u", "update_cell", "更新光标格"),
        Binding("t", "toggle_cursor", "切换光标类型"),
        Binding("c", "clear_table", "清空"),
        Binding("q", "quit", "退出"),
    ]

    CSS = """
    #hint {
        margin: 1 2;
    }
    #status {
        margin: 1 2;
        text-style: bold;
        color: $accent;
    }
    DataTable {
        height: 1fr;
        margin: 0 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._row_seq = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "DataTable 演示：方向键移动 / Enter 选择；"
            "a 加行、d 删行、u 更新光标格、t 切换 cell/row 光标、c 清空、q 退出",
            id="hint",
        )
        # zebra_stripes=True 开启斑马条纹（对应组件类 datatable--odd-row/even-row）
        yield DataTable(zebra_stripes=True, id="table")
        yield Label("状态：等待选择", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        # 必须先 add_column(s) 再 add_row(s)：cells 数量超过列数会抛 ValueError
        table.add_columns("Name", "Age", "City")
        table.add_rows(INITIAL_ROWS)

    # cursor_type="cell"（默认）时按 Enter 投递 CellSelected（F-T-098）
    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        table = event.data_table
        # event.cell_key 是 CellKey(row_key, column_key)；用 get_cell 按键取值
        value = table.get_cell(event.cell_key.row_key, event.cell_key.column_key)
        self._set_status(f"CellSelected：坐标 {event.coordinate}，值={value!r}")

    # cursor_type="row" 时按 Enter 投递 RowSelected（F-T-098）
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        # RowSelected 只携带 row_key 与 cursor_row，逐列 get_cell 取整行内容
        row_values = [
            table.get_cell(event.row_key, column.key)
            for column in table.ordered_columns
        ]
        self._set_status(
            f"RowSelected：第 {event.cursor_row} 行，row_key={event.row_key!r}，"
            f"内容={row_values}"
        )

    def action_add_row(self) -> None:
        self._row_seq += 1
        table = self.query_one("#table", DataTable)
        # 显式 key 便于回溯；key 重复会抛 DuplicateKey
        row_key = table.add_row(
            f"NewUser{self._row_seq}",
            str(20 + self._row_seq),
            "Chengdu",
            key=f"new-{self._row_seq}",
        )
        self._set_status(f"已 add_row 新行，返回 RowKey(value={row_key.value!r})")

    def action_delete_row(self) -> None:
        table = self.query_one("#table", DataTable)
        if table.row_count == 0:
            self._set_status("表已空，无可删行")
            return
        # 由当前光标坐标解析出 CellKey(row_key, column_key)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        table.remove_row(row_key)  # 行不存在抛 RowDoesNotExist
        self._set_status(f"已 remove_row：{row_key.value!r}")

    def action_update_cell(self) -> None:
        table = self.query_one("#table", DataTable)
        if table.row_count == 0:
            self._set_status("表已空，无可更新格")
            return
        cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
        table.update_cell(cell_key.row_key, cell_key.column_key, "已更新")
        self._set_status(f"已 update_cell：{cell_key}")

    def action_toggle_cursor(self) -> None:
        table = self.query_one("#table", DataTable)
        # CursorType = Literal["cell", "row", "column", "none"]（_data_table.py:53）
        table.cursor_type = "row" if table.cursor_type == "cell" else "cell"
        self._set_status(
            f"cursor_type 切换为 {table.cursor_type!r}"
            "（row 模式 Enter 触发 RowSelected，cell 模式触发 CellSelected）"
        )

    def action_clear_table(self) -> None:
        table = self.query_one("#table", DataTable)
        table.clear(columns=True)  # 连列一起清空
        # 列被清空后 add_row 的 cells 数不能超过列数，故重建列以便继续操作
        table.add_columns("Name", "Age", "City")
        self._set_status("已 clear(columns=True) 清空数据并重建列")

    def _set_status(self, text: str) -> None:
        self.query_one("#status", Label).update(f"状态：{text}")


if __name__ == "__main__":
    DataTableDemo().run()
```

保存为 `datatable_demo.py`，运行 `python datatable_demo.py`：方向键移动光标、Enter 选择（cell 模式看 `CellSelected`，按 `t` 切到 row 模式看 `RowSelected`）；`a` 加行、`d` 删行、`u` 改格、`c` 清空、`q` 退出。

## 讲解

### 1. 先列后行与 Key 体系

建表顺序必须是**先列后行**：`add_column(label, *, width=None, key=None, default=None) -> ColumnKey`（`_data_table.py:1611`）返回列键，`add_row(*cells, height=1, key=None, label=None) -> RowKey`（`:1669`）返回行键；`add_row` 中 cells 数量超过列数抛 `ValueError`（`:1699-1700`），重复 key 抛 `DuplicateKey`（`:1635/1693`）。批量版 `add_columns(...)`（`:1738`，支持 `(label, key)` 元组）与 `add_rows(rows)`（`:1776`）。键对象 `RowKey`/`ColumnKey` 是 `StringKey` 子类（`:127/135`），包装字符串且与等价字符串在字典中互通；`CellKey` 是 `(row_key, column_key)` 的 NamedTuple（`:143-155`），`coordinate_to_cell_key(coordinate)`（`:1278`）在坐标与键之间转换。行/列位置会因排序增删改变，但键始终指向同一行/列。

### 2. 选择消息与 cursor_type

`cursor_type` 是 reactive 属性，类型 `CursorType = Literal["cell", "row", "column", "none"]`（`:53/417`），默认 `"cell"`。消息类均为 `DataTable` 的内嵌 `Message`：`CellHighlighted`（`:435`）/`CellSelected`（`:472`）只在 cell 模式投递，携带 `value`、`coordinate`、`cell_key`；`RowHighlighted`（`:507`）/`RowSelected`（`:536`）只在 row 模式投递，携带 `cursor_row`、`row_key`；`ColumnSelected`（`:594`）对应 column 模式；`HeaderSelected`（`:623`）在点击列头时投递，携带 `column_key`/`column_index`/`label`。处理器按 `on_<widget类名小写>_<消息名小写下划线>` 约定命名，源码 docstring 明确给出 `on_data_table_cell_selected`、`on_data_table_row_selected`（`:476/541`）。消息默认冒泡，App 层可直接接收；`event.control`/`event.data_table` 都指向发表消息的表格。

### 3. 增删改 API 与异常

- 改：`update_cell(row_key, column_key, value, *, update_width=False)`（`:871`）按键更新单元格，键不存在抛 `CellDoesNotExist`；坐标版 `update_cell_at(coordinate, value)`（`:915`）。读：`get_cell(row_key, column_key)`（`:932`）、`get_cell_at(coordinate)`（`:950`）。
- 删：`remove_row(row_key)`（`:1793`）行不存在抛 `RowDoesNotExist`（`:1802-1803`）；`remove_column(column_key)`（`:1832`）列不存在抛 `ColumnDoesNotExist`（`:1841-1842`）；删除后内部位置索引自动重排。
- 清：`clear(columns=False)`（`:1582`）默认只清数据行，`columns=True` 连列一起清空并重置光标坐标；清列后若直接 `add_row` 传 3 个 cell 会因列数为 0 抛 `ValueError`，需重新 `add_columns`。
- 内置交互：`BINDINGS` 提供 `enter → select_cursor`、方向键 → `cursor_*`、`pageup/pagedown → page_*`、`home/end` 等（`:273-285`，均 `show=False`）；`COMPONENT_CLASSES` 含 `datatable--cursor`、`datatable--header`、`datatable--fixed`、`datatable--odd-row`、`datatable--even-row` 等 9 项（`:302-312`），`zebra_stripes` 开启后奇偶行组件类才生效。

## 相关概念

- [16 · DOMNode、Widget 与内置组件剖析（Button/Input/DataTable/TextArea）](/concepts/16-textual-dom-widget-builtin.md)
- [14 · 消息系统：Message / MessagePump 与派发约定](/concepts/14-textual-message-system.md)
- [17 · 事件体系、按键绑定与 @on 装饰器](/concepts/17-textual-events-bindings.md)
