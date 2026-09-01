---
type: Example
title: rich 示例：track 一行进度条与自定义列
description: 用 Rich 的 track 模块级函数一行渲染进度条，并演示自定义 ProgressColumn 列与 Progress 表格式进度显示的构建。
tags: [textualize, rich, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---

# rich 示例：track 一行进度条与自定义列

> 关联概念：[09-rich-progress](/concepts/09-rich-progress.md)

## 概述

Rich 的进度显示由 `rich.progress.Progress` 实现：模块级函数 [`track`](F-R-077) 用一个 for 循环封装任意可迭代对象，以"一行"代码获得实时进度条；`Progress` 则把进度渲染成一张表格，默认列组合见 [`get_default_columns`](F-R-070)，并可通过继承 `ProgressColumn` 自定义列（[F-R-064](F-R-064)）。本例演示两种最常见的用法。

## 示例一：track 一行进度条

`rich.progress.track` 是模块级便捷函数，签名见 [F-R-077](F-R-077)。它内部创建 `Progress`、调用 `add_task` 并把任务与序列绑定，每次迭代自动推进：

```python
import time

from rich.progress import track

for n in track(range(20), description="Downloading..."):
    time.sleep(0.05)

print("done!")
```

**期望输出**：终端先出现一行 "Downloading..." 进度条实时推进；序列耗尽后打印 `done!`。当 `total` 未显式给出时，`track` 用 `length_hint(sequence)` 推断总数（[F-R-075](F-R-075)）。

## 示例二：Progress 表格式进度与自定义列

`Progress(...)` 构造时接受若干个列（字符串会自动转成 `TextColumn`），默认列来自 [`get_default_columns`](F-R-070)：

```
TextColumn("[progress.description]{task.description}") + BarColumn() + TaskProgressColumn() + TimeRemainingColumn()
```

`ProgressColumn` 是抽象基类，只需实现 `render(self, task)`（[F-R-064](F-R-064)）。下面继承它自定义一列"下载速度"，并与其他内置列组合：

```python
import time

from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    Task,
    TextColumn,
    TimeRemainingColumn,
)

class SpeedColumn(ProgressColumn):
    """自定义列：把任务 speed（单位/s）格式化为 MB/s 显示。"""

    def render(self, task: Task) -> str:
        speed = task.speed
        if speed is None:
            return "?"
        return f"{speed / 1e6:.2f} MB/s"

with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    SpeedColumn(),
    TimeRemainingColumn(),
) as progress:
    task_id = progress.add_task("Copy", total=500)
    while not progress.finished:
        progress.advance(task_id, 10)
        time.sleep(0.05)
```

**期望输出**：先打印一行带表头的进度表格（描述、进度条、百分比、MB/s、剩余时间），随后各行实时刷新直至完成。核心 API 为 `Progress.add_task`（[F-R-072](F-R-072)）、`progress.advance` 与 `Progress.track`。

## 讲解

- `track(range(20), description=...)` 内部走 `Progress.track`（[F-R-075](F-R-075)）：`auto_refresh=True` 时在后台 `_TrackThread` 内按 `update_period` 刷新，否则每次迭代 `advance` + `refresh`。
- `ProgressColumn.render` 拿到 `Task` 对象，读取其动态属性即可渲染自定义内容；通过 `max_refresh` 可以限制该列刷新频率（[F-R-064](F-R-064)）。
- `Progress` 是 `JupyterMixin`，构造时内部持有 `Live` 渲染器；默认 `redirect_stdout=True` 会把期间的普通 print 也纳入刷新（[F-R-069](F-R-069)）。

## 相关概念

- [09-rich-progress](/concepts/09-rich-progress.md)