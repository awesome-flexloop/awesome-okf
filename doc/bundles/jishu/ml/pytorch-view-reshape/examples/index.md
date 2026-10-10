---
type: examples-index
title: 实操示例——张量布局诊断与时序分类复现
description: is_contiguous/stride 布局诊断片段 + 完整时序分类可复现示例（固定种子、自包含）
sources:
  - id: wechat-article
    url: https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w
status: stable
generated:
  by: trae-solo-agent
  at: "2026-10-10T10:30:00+08:00"
okf_version: "0.2"
---

# 实操示例（Examples）

> 根据知识图谱「可复现性两问」判定，本案例具备明确输入、过程、可观测输出且可独立复现，故建 examples/（见 [knowledge-map 第 4 节](../knowledge-map.md)）。示例复刻博文代码结构与流程，不虚构文章未给出的具体训练数值。

| 文档 | 内容 | 前置 |
|------|------|------|
| [00-layout-inspection.md](00-layout-inspection.md) | `is_contiguous()` + `stride()` 布局诊断片段——观察 view/transpose/permute/contiguous 对布局的影响 | Python + PyTorch |
| [01-timeseries-classification.md](01-timeseries-classification.md) | 完整时序二分类复现——[N,T,F] 构造、permute+reshape 展平、MLP 训练、PCA/ROC/AUC 评估 | NumPy + PyTorch + scikit-learn + matplotlib |

```{toctree}
:maxdepth: 2

00-layout-inspection
01-timeseries-classification
```