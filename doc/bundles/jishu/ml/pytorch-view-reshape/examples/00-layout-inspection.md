---
type: tutorial
title: 张量布局诊断——is_contiguous 与 stride 实战
description: 一段可运行的布局诊断脚本，观察 view/transpose/permute/contiguous 对连续性、stride 与存储偏移的影响
sources:
  - id: wechat-article
    url: https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w
  - id: pytorch-view
    resource: https://pytorch.org/docs/stable/generated/torch.Tensor.view.html
status: stable
stale_after: "2027-10-10"
generated:
  by: trae-solo-agent
  at: "2026-10-10T10:30:00+08:00"
okf_version: "0.2"
---

# 张量布局诊断：is_contiguous 与 stride 实战

> 依据 [[F-016/017/018]](../references/facts.md) 与 [[F-032]](../references/facts.md) 建议的练习方向。该脚本打印每个操作前后 `is_contiguous()` 与 `stride()`，直观呈现「转置只改步长、不重排数据」。

## 运行环境

- Python 3.10+，PyTorch（CPU 即可）。

## 脚本

```python
import torch

x = torch.arange(12).view(3, 4)
print("x        ", x.shape, x.is_contiguous(), tuple(x.stride()))

# transpose：不重排数据，只改步长
x_t = x.transpose(0, 1)
print("x_t      ", x_t.shape, x_t.is_contiguous(), tuple(x_t.stride()))

# 非连续张量直接 view(-1) 会报错
try:
    x_t.view(-1)
except RuntimeError as e:
    print("view(-1)  -> RuntimeError:", e)

# reshape：布局不兼容时自动复制，可成功
print("reshape  ->", x_t.reshape(-1))

# contiguous：显式复制恢复连续布局
x_c = x_t.contiguous()
print("x_c      ", x_c.shape, x_c.is_contiguous(), tuple(x_c.stride()))
print("contig   ->", x_c.view(-1))
```

## 预期输出解读

| 变量 | shape | contiguous | stride | 说明 |
|------|-------|-----------|--------|------|
| `x` | (3,4) | `True` | (4,1) | 连续布局，行主序 |
| `x_t` | (4,3) | `False` | (1,4) | 转置只交换步长 (4,1)→(1,4)，数据未搬移 |
| `x_c` | (4,3) | `True` | (3,1) | `contiguous()` 复制后恢复连续 |

- `x_t` 的 `stride()` 是 `(1,4)`——沿第 0 维一步走 1 个元素，沿第 1 维走 4 个元素，说明它是「按列读」的视图，底层仍是 `x` 的原数据。
- `x_t.view(-1)` 抛 `RuntimeError`；`x_t.reshape(-1)` 与 `x_t.contiguous().view(-1)` 都能得到 `[0,4,8,1,5,9,2,6,10,3,7,11]`。

> 把这段脚本里的操作换成 `permute(0,2,1)`、切片 `x[:, ::2]`、`reshape` 等，即可系统观察哪些操作引入非连续布局。