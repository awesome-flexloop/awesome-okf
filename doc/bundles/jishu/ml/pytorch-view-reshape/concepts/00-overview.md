---
type: concept
title: 总览——view() 与 reshape() 是什么
description: 两个形态改变操作的定位差异：view 不复制视图 vs reshape 必要时复制；shape 与 storage 概念
sources:
  - id: wechat-article
    url: https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w
  - id: pytorch-view
    resource: https://pytorch.org/docs/stable/generated/torch.Tensor.view.html
  - id: pytorch-reshape
    resource: https://pytorch.org/docs/stable/generated/torch.Tensor.reshape.html
status: stable
stale_after: "2027-10-10"
generated:
  by: trae-solo-agent
  at: "2026-10-10T10:30:00+08:00"
okf_version: "0.2"
---

# 总览：view() 与 reshape() 是什么

> 关联概念文档：[view/reshape 机制](01-view-reshape-mechanism.md) · [转置与连续性](02-transpose-contiguity.md) · [选型与成本](03-selection-and-cost.md) · [时序分类案例](04-timeseries-case.md)
> 事实依据：[[F-005]](../references/facts.md)、[[F-008]](../references/facts.md)、[[F-015]](../references/facts.md)

## 一、两者都能改变张量形状……

`view()` 与 `reshape()` 都是「改形状不改元素个数」的运算。给定张量

```python
x = torch.tensor([[1, 2, 3],
                  [4, 5, 6]])          # shape (2, 3)，6 个元素
```

`x.reshape(3, 2)` 得到同样的 6 个数重新排布为 3 行 2 列 [[F-006/007]](../references/facts.md)：

```text
[[1, 2],
 [3, 4],
 [5, 6]]
```

## 二、……但背后的逻辑不同

「改形状」涉及两层概念 [[F-008]](../references/facts.md)：

- **形状 shape**：张量在逻辑上是几行几列（`x.shape`）。
- **存储 storage / 内存布局**：这些元素在底层内存中如何连续排列（定义访问步长 stride）。

作者的关键论断是 [[F-005]](../references/facts.md)：

> `view()` 与 `reshape()` 都能改变张量形状，但背后的逻辑并不完全一样。

## 三、一句话定位

| 操作 | 本质 | 底层内存 |
|------|------|---------|
| `view()` | 换个角度看同一块内存 | **不复制**；要求新形状与 size+stride 布局天然兼容 [[F-009]](../references/facts.md) |
| `reshape()` | 尽力而为 | 布局兼容→退化为 view；不兼容→**先复制再返回** [[F-010]](../references/facts.md) |

真正的差异集中在**非连续张量**上显现 [[F-015]](../references/facts.md)：当张量经过 `transpose()`、`permute()`、切片后，`view()` 常直接报错，`reshape()` 却能兜底运行。

参考：PyTorch `reshape()` 文档明确「若 shape 兼容则返回 view，否则等价于 `contiguous()` 后返回」[^reshape]；`view()` 文档给出 stride 连续性条件[^view]。

[^view]: <https://pytorch.org/docs/stable/generated/torch.Tensor.view.html>
[^reshape]: <https://pytorch.org/docs/stable/generated/torch.Tensor.reshape.html>