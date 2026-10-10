---
type: tutorial
title: 时序二分类全流程复现
description: 复现博文 [N,T,F] 传感器时序二分类：数据构造、permute+reshape 展平、MLP 训练、PCA/ROC/AUC 评估
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

# 时序二分类全流程复现

> 复刻博文的 [N,T,F] 传感器时序二分类案例（[[F-024~029]](../references/facts.md)）。代码结构与流程与博文一致；固定随机种子以保证可复现。**注**：博文未给出训练后的 Loss / Accuracy / AUC 具体数值，本示例如实输出运行所得，不充当作者宣称的结果。

## 运行环境

- Python 3.10+；依赖：`numpy`、`torch`、`scikit-learn`、`matplotlib`。

## 代码

```python
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.metrics import roc_curve, auc, accuracy_score

np.random.seed(42)
torch.manual_seed(42)

# 1. 构造时序数据：N 样本 × T 时间点 × F 传感器特征
N, T, F = 1200, 60, 3
t = np.linspace(0, 1, T)
X = np.zeros((N, T, F), dtype=np.float32)
y = np.random.randint(0, 2, size=N)
for i in range(N):
    noise = 0.15 * np.random.randn(T, F)
    if y[i] == 0:                       # 类别 0：低频波动
        X[i, :, 0] = np.sin(2 * np.pi * 2 * t)
        X[i, :, 1] = 0.5 * np.cos(2 * np.pi * 3 * t)
        X[i, :, 2] = 0.3 * t
    else:                                # 类别 1：高频 + 趋势变化
        X[i, :, 0] = np.sin(2 * np.pi * 5 * t) + 0.4 * t
        X[i, :, 1] = 0.5 * np.cos(2 * np.pi * 6 * t)
        X[i, :, 2] = 0.8 * t
    X[i] += noise
X = torch.tensor(X)
y = torch.tensor(y, dtype=torch.float32)

# 2. 分层划分训练/测试
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

# 3. 维度调整 [N, T, F] -> [N, F, T] -> 展平 (关键是 reshape 而非 view)
X_train_perm = X_train.permute(0, 2, 1)
print("permute 后是否连续：", X_train_perm.is_contiguous())
X_train_flat = X_train_perm.reshape(X_train_perm.size(0), -1)
X_test_flat  = X_test.permute(0, 2, 1).reshape(X_test.size(0), -1)
print("模型输入形状：", X_train_flat.shape)

# 4. 分类模型
model = nn.Sequential(
    nn.Linear(T * F, 128), nn.ReLU(), nn.Dropout(0.2),
    nn.Linear(128, 32), nn.ReLU(), nn.Linear(32, 1),
)
loss_fn = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# 5. 训练
for epoch in range(150):
    model.train()
    logits = model(X_train_flat).squeeze(1)
    loss = loss_fn(logits, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 30 == 0:
        print(f"Epoch {epoch + 1:3d}, Loss: {loss.item():.4f}")

# 6. 预测与准确率
model.eval()
with torch.no_grad():
    test_prob = torch.sigmoid(model(X_test_flat).squeeze(1))
    test_pred = (test_prob >= 0.5).float()
print("Test Accuracy:", accuracy_score(y_test.numpy(), test_pred.numpy()))

# 7. 全量概率 + PCA + ROC
with torch.no_grad():
    all_prob = torch.sigmoid(model(X.permute(0, 2, 1).reshape(N, -1)).squeeze(1)).numpy()
pca = PCA(n_components=2)
embedding = pca.fit_transform(X.permute(0, 2, 1).reshape(N, -1).numpy())
fpr, tpr, _ = roc_curve(y.numpy(), all_prob)
roc_auc = auc(fpr, tpr)

# 8. 绘图（图一：传感器时序；图二：PCA 表示 + ROC）
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for feature_id in range(3):
    for label, color in [(0, "steelblue"), (1, "tomato")]:
        sel = X[y == label][:40, :, feature_id].numpy()
        mean, std = sel.mean(axis=0), sel.std(axis=0)
        axes[feature_id].plot(t, mean, color=color, label=f"class {label}")
        axes[feature_id].fill_between(t, mean - std, mean + std, color=color, alpha=0.15)
    axes[feature_id].set_title(f"Sensor {feature_id}")
    axes[feature_id].legend()
plt.suptitle("Multi-sensor temporal patterns"); plt.tight_layout(); plt.show()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for label, color in [(0, "steelblue"), (1, "tomato")]:
    mask = y.numpy() == label
    axes[0].scatter(embedding[mask, 0], embedding[mask, 1], s=16, alpha=0.55, color=color,
                    label=f"class {label}")
axes[0].set_title("PCA representation of time-series samples")
axes[0].legend()
axes[1].plot(fpr, tpr, color="darkgreen", label=f"AUC = {roc_auc:.3f}")
axes[1].plot([0, 1], [0, 1], "--", color="gray")
axes[1].set_title("ROC curve")
axes[1].legend()
plt.tight_layout(); plt.show()
```

## 要点回顾

- **展平前先 permute**：`[N,T,F] → [N,F,T]` 改变维度顺序后张量非连续，**用 `reshape` 而非 `view`** 完成展平（见 [概念 02](../concepts/02-transpose-contiguity.md)）。
- 类别区分依赖时域形态（低频 vs 高频+趋势），MLP 展平输入即可学；PCA 与 ROC/AUC 用作高维结构与分类能力评估（[[F-029]](../references/facts.md)）。