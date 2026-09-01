---
type: Concept
title: Progress：任务、采样窗口与列插件体系
description: Progress 管理一组 Task，用采样窗口算滑动平均速度；ProgressColumn 决定各列渲染。
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
# Progress：任务、采样窗口与列插件体系

## 概述

本概念文档介绍 Rich 的进度条体系，可拆为三层：**Task（任务模型）** 描述单个进度单位——总进度、已完成量、起止时间与滑动速度；**采样窗口（采样队列 + speed_estimate_period）** 负责把离散的完成量采样换算成平均速度与剩余时间；**列插件（ProgressColumn）** 是渲染插件基类，每种列把某个 Task 视角（描述、进度条、百分比、剩余时间等）渲染成可渲染对象，由 Progress 汇总成表格输出。模块级 `track` 函数把任意 `sequence` 封装成带进度的迭代器。

> 事实范围：F-R-063..078（progress.py）。

## 类型与进度模型

模块级类型（F-R-063）：`TaskID = NewType("TaskID", int)`、`ProgressType = TypeVar("ProgressType")`、`GetTimeCallable = Callable[[], float]`。

### 进度采样

`class ProgressSample(NamedTuple)`（F-R-066），字段 `timestamp: float`、`completed: float`——一次「时间点 + 已完成量」的离散采样。

### 任务模型 Task

`class Task`（`@dataclass`）（F-R-067）字段：

- `id: TaskID`、`description: str`、`total: Optional[float]`、`completed: float`；
- `_get_time: GetTimeCallable`、`finished_time=None`、`visible=True`；
- `fields: Dict[str, Any] = field(default_factory=dict)`、`start_time`/`stop_time`（`init=False`）；
- `finished_speed=None`；
- `_progress: Deque[ProgressSample] = field(default_factory=lambda: deque(maxlen=1000), init=False)`——**固定容量 1000 的采样队列**；
- `_lock: RLock`。

派生属性（F-R-068）：

- `started`（`start_time is not None`）、`finished`（`finished_time is not None`）；
- `remaining`：`total - completed`，total 为 `None` 时返回 `None`；
- `elapsed`、`speed`（由采样窗口推出）；
- `percentage`：total 为假值时返回 `0.0`，否则结果经 `min(100.0, max(0.0, ...))` 夹取到 `[0, 100]`；
- `time_remaining`：`ceil(remaining / speed)`。

方法 `get_time()`、`_reset()`。

## Progress 核心类

`class Progress(JupyterMixin)` 构造签名（F-R-069）：

```python
Progress(
    *columns: Union[str, ProgressColumn],
    console=None,
    auto_refresh=True,
    refresh_per_second=10,
    speed_estimate_period=30.0,
    transient=False,
    redirect_stdout=True,
    redirect_stderr=True,
    get_time=None,
    disable=False,
    expand=False,
)
```

- 首行 `assert refresh_per_second > 0`；
- 内部创建 `self.live = Live(console=console or get_console(), ..., get_renderable=self.get_renderable)`，允许 `transient`（结束后清屏）与 stdout/stderr 重定向（供 `Live` 接管，见 [/concepts/01-rich-console-and-protocol.md](01-rich-console-and-protocol.md)）；
- 别名 `self.print = self.console.print`、`self.log = self.console.log`。

### 默认列

`Progress.get_default_columns(cls) -> Tuple[ProgressColumn, ...]`（F-R-070）返回默认四列：`(TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), TimeRemainingColumn())`——即「描述 + 进度条 + 百分比 + 剩余时间」。

### 属性与任务管理

属性（F-R-071）：`console`（返回 `self.live.console`）、`tasks`、`task_ids`、`finished`（所有任务全 finished 才为真，空任务字典返回 True）。

任务管理方法（F-R-072）：

- `add_task(self, description, start=True, total=100.0, completed=0, visible=True, **fields) -> TaskID`；
- `remove_task(task_id)`、`start_task(task_id)`、`stop_task(task_id)`；
- `update(self, task_id, *, total=None, completed=None, advance=None, description=None, visible=None, refresh=False, **fields)`；
- `reset(self, task_id, *, start=True, total=None, completed=0, visible=None, description=None, **fields)`；
- `advance(self, task_id, advance: float = 1)`。

## 采样窗口与平均速度计算

`Progress.update` 的任务状态数据流（F-R-073）：

- `total` 变更时调用 `task._reset()`；
- **采样窗口裁剪**：`speed_estimate_period`（默认 30 秒）之前的老样本经 `_progress.popleft()` 移除，只保留窗口内采样；`_progress` 本身又以 `deque(maxlen=1000)` 为硬上限；
- `update_completed > 0` 时追加 `ProgressSample(current_time, update_completed)`；
- 当 `completed >= total` 且 `finished_time is None` 时，置 `task.finished_time = task.elapsed` 标记完成。

`Task.speed` / `time_remaining`（F-R-068）即基于窗口内样本与总时长换算：平均速度 = 窗口内完成增量 / 时间跨度，剩余时间 = 剩余量 / 速度。期间用 `task._lock: RLock` 保证并发安全（`_TrackThread` 等后台线程读写时加锁）。

## 列插件体系（ProgressColumn）

`class ProgressColumn(ABC)`（F-R-064）是列插件基类：

- 类属性 `max_refresh: Optional[float] = None`；
- `__init__(self, table_column: Optional[Column] = None)`；
- `get_table_column() -> Column`，返回 `self._table_column or Column()`；
- `__call__(self, task) -> RenderableType`：按 `max_refresh` 与 `_renderable_cache` 缓存渲染结果；
- 抽象方法 `render(self, task) -> RenderableType` 由子类实现「从 Task 提取某种视角」。

内置列插件（F-R-065）：

- `RenderableColumn(renderable="", *, table_column=None)`——直接渲染固定对象；
- `SpinnerColumn(spinner_name="dots", style="progress.spinner", speed=1.0, finished_text=" ", table_column=None)`，含 `set_spinner(...)`——加载动画列；
- `TextColumn(text_format, style="none", justify="left", markup=True, highlighter=None, table_column=None)`——格式化文本列，render 中 `self.text_format.format(task=task)`（支持 `{task.description}` 之类模板字段）；
- `BarColumn(bar_width=40, style="bar.back", complete_style="bar.complete", finished_style="bar.finished", pulse_style="bar.pulse", table_column=None)`——render 返回 `ProgressBar(...)` 进度条；
- `TimeElapsedColumn`——已用时间列；
- `TaskProgressColumn(TextColumn)`——百分比列（覆盖 TextColumn 的模板）；
- `TimeRemainingColumn`——剩余时间列；
- `FileSizeColumn`、`TotalFileSizeColumn`——文件大小列；
- `MofNCompleteColumn`——「已完成/总数」列；
- `DownloadColumn(binary_units=False, table_column=None)`——下载字节列；
- `TransferSpeedColumn`——传输速率列。

### 渲染成表格

`Progress.get_renderables()` → `make_tasks_table(tasks) -> Table`（F-R-074）：经 `Table.grid(*table_columns, padding=(0, 1), expand=self.expand)` 构建；其中 str 列经 `column.format(task=task)`，`ProgressColumn` 列经 `column(task)` 取值（见 [/concepts/06-rich-table.md](06-rich-table.md) 的 table 机制）。`get_renderable()` 返回 `Group(*self.get_renderables())`，最后 `start()` 调 `self.live.start(refresh=True)`、`stop()`、`__enter__`/`__exit__`、`refresh()`（`self.live.refresh()`）把表格交给 `Live` 动态刷新。

## 序列进度：Progress.track 与模块级 track

### Progress.track

`Progress.track(self, sequence, total=None, completed=0, task_id=None, description="Working...", update_period=0.1)`（F-R-075）：

- `total` 为 `None` 时取 `float(length_hint(sequence)) or None`（由序列长度提示推断）;
- `live.auto_refresh` 为真时在 `_TrackThread` 后台线程内产出（线程自己按 `update_period` 周期性推进），否则每次 yield 后 `advance(task_id, 1)` + `refresh()`。

### 模块级 track 函数

模块级 `track(sequence, ...)`（F-R-077）签名：

```python
track(
    sequence,
    description="Working...",
    total=None,
    completed=0,
    auto_refresh=True,
    console=None,
    transient=False,
    get_time=None,
    refresh_per_second=10,
    style="bar.back",
    complete_style="bar.complete",
    finished_style="bar.finished",
    pulse_style="bar.pulse",
    update_period=0.1,
    disable=False,
    show_speed=True,
) -> Iterable[ProgressType]
```

它是顶层便捷入口：在内部创建一次性 `Progress` 并把 `sequence` 用 `track` 包成生成器逐项产出，供 `for item in track(items):` 使用——把样式参数透传给内部 `BarColumn`，`show_speed` 控制是否追加速度列。

### 文件任务（wrap_file / open）

- `Progress.wrap_file(self, file: BinaryIO, total=None, *, task_id=None, description="Reading...") -> BinaryIO`（F-R-076）：无法确定 total 时抛 `ValueError`；返回 `_Reader(file, self, task_id, close_handle=False)`；
- `Progress.open(...)` 支持 `"r"`/`"rb"`/`"rt"` 模式（其他抛 `ValueError`）；total 缺省取 `stat(file).st_size`；文本模式以 `io.TextIOWrapper` 包装。

## 辅助线程与读写适配器

辅助类（F-R-078）：

- `class _TrackThread(Thread)`：`__init__(progress, task_id, update_period)`，`run` 中 `while not wait(update_period) and self.progress.live.is_started`（周期推进、随 live 停止而退出），支持 `__enter__`/`__exit__`；
- `class _Reader(RawIOBase, BinaryIO)`：`wrap_file` 返回的二进制读取适配器；
- `class _ReadContext(ContextManager[_I], Generic[_I])`：文件读上下文管理器。

## 相关概念

- 动态刷新依赖 Live 机制：[/concepts/01-rich-console-and-protocol.md](01-rich-console-and-protocol.md)
- 进度行列由 Table.grid 组装：[/concepts/01-rich-console-and-protocol.md](01-rich-console-and-protocol.md)
- Segment 与测量原语支撑列渲染：[/concepts/05-rich-segment-and-measure.md](05-rich-segment-and-measure.md)
- 信源登记：[/references/rich.md](/references/rich.md)