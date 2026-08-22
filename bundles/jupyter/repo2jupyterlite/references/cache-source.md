---
type: Reference
title: LRU 缓存工具信源
description: repoproviders/utils.py Cache 类的API登记，基于OrderedDict实现带TTL的LRU缓存
tags: [cache, lru, ordereddict, ttl, utility]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: utils-py
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/repoproviders/utils.py
    title: repoproviders/utils.py 源码
---

## 类概览

`Cache(OrderedDict)` 继承自 `collections.OrderedDict`，实现了一个简单的 LRU（Least Recently Used）缓存，支持可选的 TTL（Time To Live）过期。

## 构造函数

### `__init__(self, max_size=1024, max_age=0)`

**参数**：
- `max_size`：缓存最大条目数，默认 1024
- `max_age`：条目最大存活时间（秒），0 表示永不过期

**初始化属性**：
- `self.max_size`：最大容量
- `self.max_age`：TTL 秒数
- `self._ages = {}`：记录每个 key 的插入时间戳字典

## 公共方法

### `get(self, key, default=None)`

**签名**：`get(self, key, default=None) -&gt; Any`

**行为**：
1. 如果 key 存在且未过期（`_check_expired` 返回 False），调用 `self.move_to_end(key)` 更新访问顺序
2. 调用 `super().get(key, default)` 返回值

**注意**：过期条目会被 `_check_expired` 自动 pop。

### `set(self, key, value)`

**签名**：`set(self, key, value) -&gt; None`

**行为**：
1. 设置 `self[key] = value`
2. 记录 `self._ages[key] = self._now()`（当前时间戳）
3. 调用 `self.move_to_end(key)` 标记为最近使用
4. 如果 `len(self) &gt; self.max_size`，弹出 `next(iter(self))`（最旧条目，即OrderedDict第一项）

### `pop(self, key)`

**签名**：`pop(self, key) -&gt; Any`

**行为**：
1. 调用 `super().pop(key)` 从 OrderedDict 中移除
2. 同步从 `self._ages` 中移除时间戳记录
3. 返回被移除的值

## 内部方法

### `_now(self)`

返回 `time.perf_counter()`，用于高精度时间戳。

### `_check_expired(self, key)`

**签名**：`_check_expired(self, key) -&gt; bool`

**行为**：
- 如果 `self.max_age` 为 0（不启用TTL），返回 False
- 如果 `self._ages[key] + self.max_age &lt; self._now()`（已过期）：
  - 调用 `self.pop(key)` 移除条目
  - 返回 True
- 否则返回 False

## LRU 淘汰策略说明

- 基于 OrderedDict 的插入顺序维护访问时间线
- `get`（命中时）和 `set` 都调用 `move_to_end(key)` 将 key 移动到末尾（最近使用）
- 容量超限时，`next(iter(self))` 获取 OrderedDict 的第一项（最久未使用）并弹出
- TTL 过期检查在 `get` 时触发（懒过期策略），不做主动扫描
