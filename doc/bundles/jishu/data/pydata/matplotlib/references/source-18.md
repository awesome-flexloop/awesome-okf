---
type: Reference
title: 信源登记：Matplotlib 事件处理（简书 9048dc53e33a）
description: 简书文章《Matplotlib 事件处理》信源登记：URL、标题、时点与 F-162~F-169 事实清单，供 event-handling 示例引用
tags: [matplotlib, event-handling, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-9048dc53e33a
    url: https://www.jianshu.com/p/9048dc53e33a
    title: Matplotlib 事件处理（水之心，2020 年前后）
---

# 信源登记：Matplotlib 事件处理

本文登记简书文章《Matplotlib 事件处理》的信源信息与编号事实，供本束示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | Matplotlib 事件处理 |
| URL | https://www.jianshu.com/p/9048dc53e33a |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-06-11，最后编辑 2020-06-11） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |
| 原始出处 | 翻译自 matplotlib 官方文档 Event handling and picking |

## 事实清单（F-162 ~ F-169）

- **F-162**：matplotlib 使用 wxpython、tkinter、qt4、gtk 和 macosx 等用户界面工具包，事件处理 API 基于 GTK 模型（GUI 中立）。
- **F-163**：`fig.canvas.mpl_connect('button_press_event', onclick)` 连接回调，`mpl_connect()` 返回连接 id（整数），用 `fig.canvas.mpl_disconnect(cid)` 断开。
- **F-164**：可连接事件名含 'button_press_event'、'button_release_event'、'close_event'、'draw_event'、'key_press_event'、'key_release_event'、'motion_notify_event'、'pick_event'、'resize_event'、'scroll_event'、'figure_enter_event'、'figure_leave_event'、'axes_enter_event'、'axes_leave_event'。
- **F-165**：所有 matplotlib 事件继承自 `matplotlib.backend_bases.Event`，储存 `name`、`canvas`、`guiEvent` 属性。
- **F-166**：`KeyEvent` 和 `MouseEvent` 派生自 `LocationEvent`，具有 `x`、`y`、`inaxes`、`xdata`、`ydata` 属性；`MouseEvent` 的 `button` 取值 `None`、`1`、`2`、`3`、`'up'`、`'down'`（后两者对应滚动事件）。
- **F-167**：DraggableRectangle 可拖拽矩形类在 `connect()` 中分别连接 'button_press_event'、'button_release_event'、'motion_notify_event'；`on_press` 调用 `self.rect.contains(event)` 检测命中，`on_motion` 调用 `self.rect.set_x(x0+dx)`、`self.rect.set_y(y0+dy)`。
- **F-168**：鼠标进入/离开示例连接 'figure_enter_event'、'figure_leave_event'、'axes_enter_event'、'axes_leave_event'，回调中调用 `event.inaxes.patch.set_facecolor('yellow')` 等改变背景色。
- **F-169**：设置 Artist 的 `picker` 属性启用对象拾取；`picker` 可为 `None`、boolean、float（点的 epsilon 容差）、function（签名 `hit, props = picker(artist, mouseevent)`）；示例 `line, = ax.plot(np.random.rand(100), 'o', picker=5)`，`onpick` 回调读取 `event.artist` 与 `event.ind`，经 `fig.canvas.mpl_connect('pick_event', onpick)` 连接。

## 文档引用

- 本束示例 [event-handling](../examples/event-handling.md) 引用本文信源。
