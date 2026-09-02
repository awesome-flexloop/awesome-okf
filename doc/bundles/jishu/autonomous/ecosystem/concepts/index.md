# 概念文档（Concepts）

本目录包含无人驾驶生态知识包的核心概念文档，按"数据集 → 车载术语 → 学习资源 → 开发环境"组织。

## 学习路径

| 序号 | 文档 | 核心问题 |
|------|------|---------|
| 00 | [无人驾驶常用数据集盘点](00-datasets.md) | 有哪些常用数据集？各自规模与用途 |
| 01 | [车载术语：ECU 与 CAN](01-vehicle-terms.md) | 车载系统开发中的 ECU 与 CAN 是什么 |
| 02 | [无人驾驶学习资源导航](02-resources.md) | 有哪些学习与研究资源入口 |
| 03 | [WSL2 GPU 深度学习环境搭建](03-wsl2-gpu-deep-learning.md) | 如何在 WSL2 上配置多框架 GPU 深度学习环境 |

### 路径建议

```
00 数据集（认识数据）
   ↓
01 车载术语（认识车辆）
   ↓
02 学习资源（资源导航）
   ↓
03 WSL2 GPU 环境（动手环境）
```

四篇文档相互独立，可按需阅读；与 [Autoware / Autoware.Auto](../autoware/index.md) 配套阅读可获得搭建环境的完整视角。

```{toctree}
:hidden:
:maxdepth: 7

00-datasets
01-vehicle-terms
02-resources
03-wsl2-gpu-deep-learning
```
