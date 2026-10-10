---
type: concepts-index
title: 概念解析——PyTorch view/reshape 张量内存布局
description: view()/reshape() 语义、stride 布布局与连续性、转置后报错机理、选型规约与时序分类案例
sources:
  - id: wechat-article
    url: https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w
status: stable
generated:
  by: trae-solo-agent
  at: "2026-10-10T10:30:00+08:00"
okf_version: "0.2"
---

# 概念解析（Concepts）

| 文档 | 主题 | 核心 F 引用 |
|------|------|-----------|
| [00-overview.md](00-overview.md) | view vs reshape 定位、形状 shape 与存储 storage | F-005/008/015 |
| [01-view-reshape-mechanism.md](01-view-reshape-mechanism.md) | view 零拷贝视图、reshape 视图/复制二态、stride 兼容条件 | F-009/010/011/013/014/021/031 |
| [02-transpose-contiguity.md](02-transpose-contiguity.md) | transpose/permute 后为何 view 报错、is_contiguous/stride、contiguous() 修复 | F-016~022 |
| [03-selection-and-cost.md](03-selection-and-cost.md) | 实际选择规约、contiguous 内存成本、reshape(-1) vs view(-1) | F-023/030/031/032 |
| [04-timeseries-case.md](04-timeseries-case.md) | 完整时序分类案例研读——[N,T,F] 生命周期 | F-024~029 |

```{toctree}
:maxdepth: 2

00-overview
01-view-reshape-mechanism
02-transpose-contiguity
03-selection-and-cost
04-timeseries-case
```