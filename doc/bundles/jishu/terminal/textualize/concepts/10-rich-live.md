---
type: Concept
title: Live 动态渲染：自动刷新线程与 RenderHook 拦截
description: Rich 的 Live 机制：以固定频率刷新终端显示，通过后台刷新线程与 RenderHook 拦截渲染管线，实现进度条、日志流等动态画面。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---

# Live 动态渲染：自动刷新线程与 RenderHook 拦截

## 概述

`Live` 是 Rich 提供**自动更新的动态显示**机制：可以把任意 renderable 持续展示为"动态画面"，并以固定频率重绘。它由两股力量驱动——一个**后台刷新线程**按 `refresh_per_second` 周期性触发刷新，以及通过实现 **RenderHook 接口**在 `Console` 渲染管线中拦截并注入当前画面。本文覆盖事实 **F-R-079..080**，代码位于 `rich/live.py`，并被 `Progress`（F-R-069）内部复用。

## Live：构造与生命周期

`class Live(JupyterMixin, RenderHook)`（F-R-079）构造签名：

```python
Live(
    renderable=None, *,
    console=None, screen=False, auto_refresh=True,
    refresh_per_second=4, transient=False,
    redirect_stdout=True, redirect_stderr=True,
    vertical_overflow="ellipsis", get_renderable=None,
)
```

- 首行 `assert refresh_per_second > 0` 校验刷新频率合法。
- `self.transient = True if screen else transient`：`screen=True`（替代屏幕模式）时强制 transient。
- 内部创建 `self._live_render = LiveRender(self.get_renderable(), vertical_overflow=vertical_overflow)` 承载实时画面。
- `get_renderable` 提供后（如 `Progress.get_renderable`）作为渲染内容来源，否则回落到 `renderable` 参数。

`Live` 是 `RenderHook` 的子类（F-R-080 方法 `process_renderables` 实现其接口），因此可被注册进 `Console` 的 render hook 栈——这正是 `Progress`（F-R-069）里 `self.live = Live(...)` 能接管整条渲染管线的原因。

## 后台刷新线程：_RefreshThread

`class _RefreshThread(Thread)`（F-R-080）负责按固定间隔自动刷新：

- `__init__(live, refresh_per_second)`：持 `done = Event()`，`super().__init__(daemon=True)` 守护线程。
- `stop()`：`self.done.set()` 触发停止。
- `run()`：`while not self.done.wait(1 / self.refresh_per_second)`——以 `1/refresh_per_second` 秒为周期循环；每次进入先 `with self.live._lock` 加锁，若未停止则调用 `self.live.refresh()` 重绘。

```python
from rich.live import Live
from rich.text import Text

# auto_refresh=True 时会启动 _RefreshThread，以 refresh_per_second=4 节拍刷新
with Live(Text("loading"), refresh_per_second=4) as live:
    for i in range(10):
        live.update(Text(f"progress {i}"))
        # update(renderable, refresh=False) 只换内容；显示靠自动刷新线程或显式 refresh()
```

## 刷新与内容更新：refresh / update

方法（F-R-080）：

- `start(refresh: bool = False)`：启动 live，可选首次立即刷新。
- `stop()`：停止并（按 `transient`）清理画面。
- `__enter__` / `__exit__`：上下文管理器，配合自动刷新线程使用。
- `update(self, renderable, *, refresh=False)`：替换显示内容；str 先经 `console.render_str` 转换；`refresh=True` 时立即 `refresh()`，否则等下一节拍（F-R-Detail）。
- `refresh()`：`with self._lock` 下 `self._live_render.set_renderable(self.renderable)`；嵌套时委托外层 live 刷新；Jupyter 用 `ipywidgets.Output` 重绘，否则终端打印 `Control()` 复位光标重绘。
- 属性 `is_started`（是否已启动）、`renderable`。

私有方法 `_enable_redirect_io()` / `_disable_redirect_io()`：重定向 `stdout`/`stderr`，使 live 显示期间可使用 `print`（对应 `redirect_stdout`/`redirect_stderr` 参数）。

## RenderHook 拦截：process_renderables

`process_renderables(self, renderables)`（F-R-080，实现 `RenderHook` 抽象接口）在每次渲染时被调用，把 live 画面注入渲染管线：

- 同步 `self._live_render.vertical_overflow = self.vertical_overflow`。
- **交互式终端**（`console.is_interactive`）：`with self._lock` 下计算复位控制码（替代屏幕用 `Control.home()`，否则用 `_live_render.position_cursor()` 回退光标），产出 `[reset, *renderables, self._live_render]` —— 前面复位、末尾追加实时画面。
- **非交互/未启动且非 transient**（文件或 dumb terminal）：产出 `[ *renderables, self._live_render]`，最终把最终结果渲染给文件等非交互接收方。

`Live` 借 `_lock` 保护——因为用户线程（`_RefreshThread`）与渲染线程可并发修改 `_live_render` 的 renderable，这一点在 `Progress` 中无需（用户不可并发修改）。

## 相关概念

- `/concepts/01-rich-console-and-protocol.md`：`RenderHook`（F-R-040）抽象接口与 `Console.push_render_hook/pop_render_hook`（F-R-048）是 `Live.process_renderables` 被调用的前提；`Live` 即 `RenderHook` 的子类。
- `rich/progress.py`：`Progress`（F-R-069）内部 `self.live = Live(...)`，其 `start()` 即 `self.live.start(refresh=True)`、`refresh()` 即 `self.live.refresh()`，`Live` 是进度条动态显示的内核。