---
type: concept
title: 案例研读——[N,T,F] 时序分类中的 permute + reshape 生命周期
description: 完整研读博文时序分类案例：数据构造、permute/reshape 展平、MLP 训练、PCA/ROC/AUC 评估与维度转换要点
sources:
  - id: wechat-article
    url: https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w
status: stable
stale_after: "2027-10-10"
generated:
  by: trae-solo-agent
  at: "2026-10-10T10:30:00+08:00"
okf_version: "0.2"
---

# 案例研读：时序分类中的 [N,T,F] 生命周期

> 关联：[转置与连续性](02-transpose-contiguity.md) · 可复现代码见 [examples/01-timeseries-classification](../examples/01-timeseries-classification.md)
> 事实依据：[[F-024/025/026/027/028/029]](../references/facts.md)

## 一、数据长什么样

博文构造一个**传感器时序分类**任务 [[F-024]](../references/facts.md)：

- 每条样本含 **60 个时间点（T）× 3 个传感器特征（F）**；
- 共 **1200 条样本（N）**、**两个类别**；
- 类别 0 信号近似**低频波动**；类别 1 额外叠加**高频变化与趋势变化** [[F-025]](../references/facts.md)；
- 每条样本叠加 `0.15 × randn` 高斯噪声。

数据原始形状为 `[N, T, F] = [样本数, 时间步, 特征数]`；模型输入通常需展平成 `[N, T × F]` [[F-026]](../references/facts.md)。

## 二、维度转换：这条链路是核心

案例在最关键的展平处演示了「为什么要用 reshape 而非 view」 [[F-027]](../references/facts.md)：

```python
X_train_perm = X_train.permute(0, 2, 1)      # [N, T, F] -> [N, F, T]，可能非连续
X_train_flat = X_train_perm.reshape(X_train_perm.size(0), -1)   # -> [N, F*T]
```

- `permute(0, 2, 1)` 改变维度顺序后，张量**很可能已非连续**（`is_contiguous()` 打印验证）。
- 此时若用 `view(-1)` 会抛 `view size ... stride` 错误；用 `reshape(size(0), -1)` 则可利用自动复制兜底完成展平 [[F-021]](../references/facts.md)。

> 这正是把 [02-transpose-contiguity](02-transpose-contiguity.md) 的机制落到真实管线：**先 permute、后 reshape 而非 view**。

## 三、模型与训练

分层划分训练/测试（25% 测试、`stratify`），构造一个 MLP [[F-028]](../references/facts.md)：

```python
model = nn.Sequential(
    nn.Linear(T * F, 128), nn.ReLU(), nn.Dropout(0.2),
    nn.Linear(128, 32),  nn.ReLU(), nn.Linear(32, 1),
)
loss_fn = nn.BCEWithLogitsLoss()          # 二分类
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
# 150 epochs，logits.squeeze(1) 后计算损失
```

固定随机种子 42（NumPy 与 torch），保证可复现 [[F-024]](../references/facts.md)。

## 四、结果分析

评估方式 [[F-029]](../references/facts.md)：

- 预测概率经 `sigmoid` 后以阈值 0.5 判类，用 `accuracy_score` 输出 Test Accuracy；
- **图一**：绘制 3 个传感器随时间的均值曲线 ± 标准差带，观察两个类别的时序模式差异；
- **图二左**：`PCA(n_components=2)` 将展平特征降维，观察高维时序特征是否形成类别结构；
- **图二右**：ROC 曲线与 AUC，分析模型在不同阈值下的分类能力。

> 说明：博文未给出消确的训练 Loss / Accuracy / AUC 数值，本束不复刻它可能产生的具体数值，仅复现代码结构与流程（见 [examples/01-timeseries-classification](../examples/01-timeseries-classification.md)）。