---
type: Example
title: "Reactive 计数器：响应式属性 + watch 回调自动刷新"
description: 用可运行的计数器演示 Textual 响应式机制：reactive() 声明状态、watch_&lt;name&gt; 方法作为 watcher 自动注册、赋值触发 _set 校验与 refresh 落盘重绘，状态与界面零手工同步。
tags: [textualize, textual, tui, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# Reactive 计数器：响应式属性 + watch 回调自动刷新

## 概述

Textual 的发射式核心是**响应式属性（Reactive）**：你用 `reactive()` 声明一个状态（F-T-017/018），赋值会走 `Reactive._set` 的「校验 → 通知 watcher → refresh」链路（F-T-020、F-T-114），`watch_<name>` 方法由框架自动注册为 watcher（F-T-022、F-T-053）。本例用"加一 / 归零"计数器演示：改一个 reactive 值，界面自动刷新，完全不用手工调用重绘。

```python
from textual.app import App, ComposeResult
from textual import reactive
from textual.widgets import Button, Static


class Counter(Static):
    """计数器：reactive 状态 + watch_<name> 自动回调刷新。"""

    count = reactive(0)            # F-T-018：reactive() 即 Reactive 派生，init=True、repaint=True

    def watch_count(self, count: int) -> None:
        # F-T-022/053：watch_<name> 方法被 _check_watchers 自动发现并注册为 watcher
        self.update(f"当前计数：{count}")

    def increment(self) -> None:
        self.count += 1            # 赋值 → Reactive._set → watcher → refresh

    def reset(self) -> None:
        self.count = 0


class CounterApp(App):
    TITLE = "Reactive 计数器"

    def compose(self) -> ComposeResult:
        yield Button("+1", id="increment")
        yield Button("归零", id="reset")
        yield Counter("当前计数：0", id="counter")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        counter = self.query_one("#counter", Counter)
        if event.button.id == "increment":
            counter.increment()
        elif event.button.id == "reset":
            counter.reset()


if __name__ == "__main__":
    CounterApp().run()
```

## 运行

```bash
python textual-reactive-counter.md  # 实际使用时把示例代码另存为 .py 文件执行
```

启动后可见两个按钮和一行 `当前计数：0`。每点一次 `+1` 数字递增并即时刷新，点 `归零` 恢复为 0。按 `Ctrl+Q` 退出。

## 讲解

### 1. 声明响应式状态：reactive(default)（F-T-017/018）

`count = reactive(0)` 声明一个响应式属性。`reactive` 是 `Reactive` 的子类，二者唯一差异是 `init=True`（`reactive.py:437-502`）——子类实例构造时即初始化，并在 `_post_mount` 阶段触发首次 watcher。默认 `repaint=True`，所以任何赋值都会触发组件重绘（F-T-020）。

### 2. 读取与存储（F-T-019/023）

内部真实值存于 `self._reactive_count`（F-T-023，`_initialize_reactive` 确立内部命名），而 `self.count` 是一个描述符，`Reactive.__get__` 在对象缺少 `id` 属性时会抛 `ReactiveError`（F-T-019）——这也是 Reactive 只能挂在 DOM 组件上的原因。

### 3. 赋值触发 _set 链路（F-T-020）

每次 `self.count += 1` 都会调用 `Reactive._set(obj, value)`，其固定次序为：

1. 依次调用 `_validate_count`、`validate_count`（本例无，返回原值）；
2. 值发生变化（`1 → 2`）时写入内部值 `_reactive_count`；
3. `_check_watchers` 通知 watcher；
4. 按 `repaint=True` 调用 `obj.refresh(...)`。

### 4. watch_<name> 自动注册（F-T-022/053）

只要定义了 `def watch_count(self, count)` 方法，`_check_watchers`（`reactive.py:377-411`）就会自动找到它作为公开 watcher 并调用（`invoke_watcher` 按参数个数传入新值，`reactive.py:90-121`）。watcher 与 `_set` 是**同步串行的**：赋值 → watcher 更新 `update()` 文本 → refresh 置脏区，真正重绘推迟到下一 idle 事件（F-T-048/F-T-114），因此 UI 绝不会因为状态与显示不同步而闪烁。

> **扩展**：`Reactive` 构造还支持 `layout`（重布局）、`repaint`（重绘）、`always_update`（值不变也触发 watcher）、`toggle_class`（按真值切 CSS 类）、`compute`（派生计算）等标志（F-T-017）——本例只触及默认的 `repaint=True`。

## 相关概念

- [15-textual-reactive.md](/concepts/15-textual-reactive.md) — validate → watcher → compute → refresh 完整链路
- [13-textual-app-entry.md](/concepts/13-textual-app-entry.md) — App 入口与 compose 装配