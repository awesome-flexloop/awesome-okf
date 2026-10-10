---
type: concept
title: 为什么 transpose() 后 view() 会报错——连续性、stride 与 contiguous()
description: transpose/permute 改步长不重排数据 → is_contiguous=False → view 报错；contiguous() 修复与语义
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

# 为什么 transpose() 后 view() 会报错

> 关联：[view/reshape 机制](01-view-reshape-mechanism.md) · [选型与成本](03-selection-and-cost.md)
> 事实依据：[[F-016/017/018/019/020]](../references/facts.md)、[[F-021/022]](../references/facts.md)

## 一、转置并不「重排数据」，它只改访问步长

考虑 [[F-016]](../references/facts.md)：

```python
x = torch.arange(12).view(3, 4)
print(x.is_contiguous())          # True
x_t = x.transpose(0, 1)           # shape (4, 3)
print(x_t.is_contiguous())        # False
```

`transpose()` **没有真的把数据重新排列**，它只是修改了读写数据时的步长（stride）[[F-018]](../references/facts.md)。原张量按行读取 `0 1 2 3 / 4 5 6 7 / 8 9 10 11`；转置后希望按列读取 `0 4 8 / 1 5 9 / 2 6 10 / 3 7 11` [[F-019]](../references/facts.md)。访问步长变化 → 张量**不再连续**。

## 二、随之而来的 `view(-1)` 报错

非连续张量不满足 `view` 的 stride 兼容条件，直接展平会抛错 [[F-020]](../references/facts.md)：

```text
RuntimeError: view size is not compatible with input tensor's size and stride
```

而 `x_t.reshape(-1)` **通常正常运行**——`reshape()` 在需要时自动创建连续副本 [[F-021]](../references/facts.md)。

## 三、`contiguous()`：显式复制，恢复连续

若明确想用 `view()`，可先调用 `contiguous()` 把数据按逻辑顺序复制到连续布局 [[F-022]](../references/facts.md)：

```python
x_t.contiguous().view(-1)
```

`contiguous()` **会真正复制一份数据**，把 stride 调整为连续条件，之后 `view()` 即可成立。

## 四、两条常用写法

[[F-023]](../references/facts.md) 给出两条等价但意图不同的写法：

```python
# 更安全、更直接：布局不兼容时自动复制
x = x.permute(0, 2, 1).reshape(batch_size, -1)

# 明确控制内存布局：先显式复制，再做零拷贝 view
x = x.permute(0, 2, 1).contiguous().view(batch_size, -1)
```

- 前者以 `reshape` 兜底，少写一步、更稳健；
- 后者把复制时机显式化，适合需要明确掌控内存拷贝语义的场景。

> 扩展阅读：`permute()` 是 `transpose()` 的通用 N 维版本；两者都不重排数据、都可能导致非连续布局。