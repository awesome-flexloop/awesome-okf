---
type: Concept
title: Reactive：validate → watcher → compute → refresh 链路
description: 拆解 Textual 响应式属性机制：Reactive 描述符构造、_reactive_{name} 内部存储、私有/公开 validate 与 watch、compute_xxx 每次重读、只读 compute 赋值抛错，以及变更落 refresh 的完整更新链路。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# Reactive：validate → watcher → compute → refresh 链路

## 概述

Textual 用**响应式属性（Reactive）**让组件状态与界面自动联动：你只需声明 `Reactive(default, ...)` 描述符并赋值，框架便沿「校验 → 通知 watcher → 计算派生值 → 触发重绘/重布局」的链路自动刷新。本文覆盖 textual 响应式核心：`Reactive`/`reactive`/`var` 三类描述符的构造差异（F-T-017、F-T-018）、`_reactive_{name}` 内部存储名与初始化（F-T-023）、私有/公开 `validate_<name>` 与 `watch_<name>` 的调用次序（F-T-020）、`compute_<name>` 每次读取即重算及其**只读**约束（F-T-019、F-T-021）、watcher 的注册与异步调用媒介 `invoke_watcher`（F-T-022），以及因 `_set` 触发的 `obj.refresh(...)` 落盘链路（F-T-114）。并顺带覆盖 `DOMNode.set_reactive`/`watch`（F-T-040、F-T-041）。代码位于 `src/textual/reactive.py`、`src/textual/dom.py`。

## Reactive 描述符家族

`Reactive(Generic[ReactiveType])` 构造签名（F-T-017、`reactive.py:142-154`）：

```python
Reactive(default, *, layout=False, repaint=True, init=False,
         always_update=False, compute=True, recompose=False,
         bindings=False, toggle_class=None)
```

三个派生描述符（F-T-018）：

- **`reactive(Reactive)`**：与基类唯一差异是 `init=True`（声明时即初始化）。
- **`var(Reactive)`**：固定传 `layout=False, repaint=False`，签名 `__init__(default, init=True, always_update=False, bindings=False, toggle_class=None)`——适用于"纯数据、不参与布局/重绘"的内部状态（如 `Input.restrict`）。
- 两者的默认行为不同：`Reactive` 默认 `init=False`、`repaint=True`；`reactive` 默认 `init=True`；`var` 则两者皆关。

标志位语义（贯穿 `_set`）：`layout`（置脏区要求重布局）、`repaint`（要求重绘）、`recompute`（是否参与派生计算）、`recompose`（触发整 Widget 重新 `compose`）、`always_update`（值不变也更新）、`bindings`（变更时 `refresh_bindings`）、`toggle_class`（按真值切换 CSS 类）。

## 内部存储：_reactive_{name}

`Reactive._initialize_reactive(obj, name)`（F-T-023、:196-228）确立内部命名：**任何 reactive 属性的真实值存于 `obj._reactive_{name}`**；`init=True` 且存在 `compute_<name>` 方法时，以计算方法结果作为默认值；`toggle_class` 在初始化时按默认值真值性 `set_class`。`DOMNode.__init_subclass__` 沿 MRO 把 `Reactive` 实例收集进 `cls._reactives`，并在 `_post_mount` 调用 `Reactive._initialize_object(self)` 触发整对象初始化（F-T-037、F-T-042）。

> 这也解释了实例属性名：`self._reactive_focus` 存 `focus` 的真实值，而非 `self.focus`（那走的是描述符 `__get__`）。

## __get__：compute_xxx 每次读取即重算

`Reactive.__get__(obj, obj_type)`（F-T-019、:290-315）有两个关键行为：

1. `obj` 缺少 `id` 属性时抛 `ReactiveError`——描述符强依赖 DOM 节点的 `id` 存在。
2. 对象存在 `compute_<name>` 方法时，**每次读取都调用该计算方法**，并用返回值刷新内部存储值后再返回。派生属性不是缓存的，而是每次 `.__get__` 现算。

配合 F-T-037：`DOMNode.__init_subclass__` 会收集以 `compute_`（或 `_compute_`）开头的方法进 `cls._computes`，供派发计算用。

## _set：validate → watcher → compute → refresh

`Reactive._set(obj, value, always=False)`（F-T-020、:316-369）是整条链路的枢纽：

```python
# 源码节选语义（reactive.py）
# 1) 校验
private_validate = getattr(obj, f"_validate_{name}", None)  # _validate_<name> 优先
if callable(private_validate): value = private_validate(value)
public_validate  = getattr(obj, f"validate_{name}", None)   # validate_<name> 次位
if callable(public_validate):  value = public_validate(value)
# 2) toggle_class 切换
# 3) 值变化（或 always / always_update）时：
#    - 写入内部值
#    - _check_watchers(obj, name, old_value)   # 通知 watcher
#    - 按需 _compute（派生值）
#    - bindings=True → refresh_bindings()
#    - 按 _layout/_repaint/_recompose 标志 → obj.refresh(...)
```

要点：

- **校验次序固定**：私有 `_validate_<name>` 先于公开 `validate_<name>`。公开校验器可返回转换后的新值（如 `Input.validate_selection`，F-T-095）。
- **watcher 通知**：`_check_watchers`（:377-411）同时"私有 watcher `_watch_<name>`"与"公开 watcher `watch_<name>`"都调用（F-T-053 可见 `watch_hover_style`、`watch_disabled` 等真实示例），再调用外部经 `DOMNode.watch` 注册到 `__watchers` 的回调。
- **异步媒介 `invoke_watcher`**：`invoke_watcher`（F-T-022、:90）统一派发 watcher，同步结果直接返回、`awaitable` 结果交给 `await_watcher` 挂起到事件循环（:82/:120）——保证**watcher 可写成 async 方法**而不阻塞派发。
- **computed 派生**：需要时计算关联 `compute_` 派生值并触发其 watcher。
- **刷新落盘**：最终按 `layout/repaint/recompose` 标志调用 `obj.refresh(...)`。`Widget.refresh` 置脏区并 `check_idle()`，**真正重绘推迟到下一个 idle 事件**（F-T-114），与消息派发天然解耦（见 `/concepts/14-textual-message-system.md`）。

## compute 赋值 = 只读

对带 `compute_<name>` 方法的 reactive 属性赋值，`_set` 直接抛 `AttributeError`（F-T-021、`reactive.py:330-333`，消息 "reactive attributes with a compute method are read-only"）。派生属性的值只能由 `compute` 计算得出，不可外部覆写。

## set_reactive 与 watch：外部接线

`DOMNode` 提供两个配套（F-T-040、F-T-041）：

- **`DOMNode.set_reactive(reactive, value) -> None`**（`dom.py:249`）：直接设置 reactive 值，**且不调用 validators 也不触发 watchers**（docstring 明示）——适合在初始化阶段"填值但不触发副作用"（如 `Button.__init__` 设置 `label`，F-T-088）。
- **`DOMNode.watch(obj, attribute_name, callback, init=True)`**（`dom.py:1256`）：监听**另一对象**上的 reactive 属性变化，`init=True` 时注册即回调当前值。其底层即模块级 `_watch`（F-T-022、:505），将回调按属性名注册进 `__watchers` 字典。

## 约定与陷阱

- **内部价存 `_reactive_{name}`**：想绕过描述符直接读取真实值时用此名（非 `self.<name>`）。
- **校验/观察器命名成对**：私有 `_validate_name`/`_watch_name` 优先于公开 `validate_name`/`watch_name`，且两者常同时被触发——别重复实现。
- **`compute_` 只读且每次重算**：别拿派生属性当缓存；要做缓存需自己维护。赋值即抛 `AttributeError`。
- **watcher 可异步**：通过 `invoke_watcher`/`await_watcher`，同步/异步回调统一调度。
- **`set_reactive` 极其静默**：跳过 validate 与 watcher，仅用于"设值不联动"，别误用于常规赋值。
- **三路标志别配错**：`var` 默认关布局/重绘（纯数据），`Reactive` 默认重绘但不布局，`reactive` 默认初始化；`recompose=True` 会走整 Widget 重组、成本高。
- **`refresh` 是异步落盘**：`_set` 只置脏区，实际重绘在下一 idle 事件（F-T-114）。

## 相关概念

- [14-textual-message-system.md](/concepts/14-textual-message-system.md) — reactive 变更最终经消息泵 idle 驱动重绘
- [16-textual-dom-widget-builtin.md](/concepts/16-textual-dom-widget-builtin.md) — DOMNode 基类与 Widget 内置反应式属性