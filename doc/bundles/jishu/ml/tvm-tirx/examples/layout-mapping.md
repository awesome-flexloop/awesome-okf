---
type: Example
title: Layout 映射手算：元素 57 落到哪些 warp/lane/reg
description: 用纯 Python 复现第一代 TIRx 文档中的 layout 示例——把逻辑坐标 (3,9) 展平、反展平到具名硬件轴，并计算 replica 后的两个 owner
tags: [tvm-tirx, layout, 示例, warp, lane, replica, 手算]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: june-blog
    resource: https://tvm.apache.org/2026/06/22/tirx
---

# Layout 映射手算：元素 57

> 文中 `[F-xxx]` 为编号事实，来源见 [facts.md](../references/facts.md)。本示例复现第一代 TIRx 文档给出的 layout 走查 [F-079]，不依赖 TIRx 安装。

## 1. 目标

给定形状 `(8, 16)` 的逻辑 tile，文档给出的映射规则是：

```text
warp: floor(j / 8) + 5 + 4r,  r ∈ [0, 2)
lane: 4i + floor(j / 2) % 4
reg : j % 2
```

要求：验证逻辑坐标 `(3, 9)`（展平后为元素 57）的 base location 与两个 replica owner。

## 2. 纯 Python 复现

```python
def map_coord(i: int, j: int, shape=(8, 16), replicas=2):
    rows, cols = shape
    flat = i * cols + j                 # flatten
    ii, jj = divmod(flat, cols)         # unflatten
    warp_base = jj // 8 + 5
    lane = 4 * ii + (jj // 2) % 4
    reg = jj % 2
    owners = [(warp_base + 4 * r, lane, reg) for r in range(replicas)]
    return flat, owners


flat, owners = map_coord(3, 9)
print("flat =", flat)
print("base =", owners[0])
print("owners =", owners)
```

输出：

```text
flat = 57
base = (6, 12, 1)
owners = [(6, 12, 1), (10, 12, 1)]
```

与文档结果一致 [F-079]：

```text
base location: 6@warpid, 12@laneid, 1@m
owners（×2）: { warpid=6, laneid=12 }, { warpid=10, laneid=12 }
```

## 3. 逐步解释

| 步骤 | 计算 | 结果 |
|------|------|------|
| 展平 | `3 * 16 + 9` | 57 |
| 反展平 | `divmod(57, 16)` | `(3, 9)` |
| warp | `9 // 8 + 5 + 4r` | `6 + 4r` → 6, 10 |
| lane | `4*3 + (9 // 2) % 4` | `12 + 0` = 12 |
| reg | `9 % 2` | 1 |

## 4. 这个例子说明了什么

1. **layout 是可计算的坐标映射**，不是一句模糊的「数据怎么放」[F-078]。
2. **replica 是显式的**：同一个逻辑元素在两个 warp 上各有一份，`r` 枚举复制偏移 [F-077]。
3. **offset 进入公式**：`+5` 是 warp 轴上的固定偏移 [F-077]。
4. **具名轴让映射可读**：`warpid` / `laneid` / `m` 直接出现在结果里，不依赖上下文猜测 [F-077]。

## 5. 与真实 API 的关系

本示例只复现**第一代文档中的数值规则**，不是 `tvm_tirx` 的 API 调用。真实 layout 用 D/R/O 结构与具名轴构造，再由 tile primitive dispatch 消费 [F-075][F-076]。

第二代的真实 API 形态不同，源码与文档给出的最小例子是 [F-109][F-124]：

```python
from tvm_tirx.tirx.layout import TileLayout, S, R
from tvm_tirx.backend.cuda.axis import laneid, warpid

fragment_layout = TileLayout(S[(32, 4) : (1 @ laneid, 1)])
print(fragment_layout.apply(3, 2, shape=(32, 4)))   # {'laneid': 3, 'm': 2}

# 挂到张量上
fragment = T.alloc_local((32, 4), T.float32, layout=fragment_layout)
lane_values = fragment.view(4, layout="default")
```

因此：

- 手算部分用于理解「逻辑坐标 → 具名硬件轴」的思想；
- 真正写代码时用 `TileLayout(S[...])`、`apply`、`alloc_local(layout=...)`、`view`；
- 第一代公式（`warp/lane/reg`）与第二代 API（`laneid/m`）不是同一套接口，不能混用 [F-097]。

若要在第一代 TIRx 中实际构造该 layout，请参考 `apache-tvm` 0.25.0 的 TIRx layout API [F-071]。

## 6. 练习

- 把 `replicas` 改为 3，观察 owner 分布；
- 把坐标改为 `(7, 15)`，验证 warp/lane/reg 的变化；
- 把形状改为非 2 的幂（如 `(6, 12)`），检查公式是否仍成立（文档称 layout 从设计上支持一般形状 [F-077]）。
