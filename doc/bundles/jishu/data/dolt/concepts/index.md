# 概念索引（Concepts）

本目录包含 Dolt 知识包三篇核心概念文档，按"发布事实→机制原理→边界趋势"三层递进。

## 概念列表

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [Dolt 概述与产品矩阵](00-dolt-overview.md) | 产品定位、核心功能、产品矩阵（Dolt/DoltHub/DoltLab/Hosted Dolt/MCP/Workbench）、开源协议与生态 | F-006~F-029 |
| 01 | [行级版本控制机制](01-dolt-versioning-mechanism.md) | Prolly Tree 存储引擎、行级历史视图、分支/合并/回滚机制、MySQL 5.7 兼容原理、MCP/AI Agent 工作流 | F-017~F-029 |
| 02 | [边界、限制与选型建议](02-dolt-boundaries-trends.md) | 性能限制（TPC-C 54%）、1G 阈值勘误、迁移成本、适用场景、行业趋势、选型启示 | F-034~F-059、F-060 |

## 阅读路径建议

```
00-dolt-overview（认识产品全貌）
    ↓
01-dolt-versioning-mechanism（理解核心机制）
    ↓
02-dolt-boundaries-trends（明确边界与适用场景）
```

## 概念依赖关系

```
00-dolt-overview
    ├── 01-dolt-versioning-mechanism
    │     └── 02-dolt-boundaries-trends（性能限制/勘误引用前文）
```

```{toctree}
:hidden:
:maxdepth: 7

00-dolt-overview
01-dolt-versioning-mechanism
02-dolt-boundaries-trends
```
