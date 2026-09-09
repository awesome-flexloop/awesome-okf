# 概念索引（Concepts）

本目录包含 Dolt 知识包六篇核心概念文档，按"发布事实→机制原理→边界趋势→CLI 架构→SQL API→存储内核→生态工作流"七层递进。
博文层三篇 + 源码层三篇，形成"产品全景 → 实现细节"的分层学习路径。

## 概念列表

### 第一层：发布事实层（博文层）

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [Dolt 概述与产品矩阵](00-dolt-overview.md) | 产品定位、核心功能、产品矩阵（Dolt/DoltHub/DoltLab/Hosted Dolt/MCP/Workbench）、开源协议与多协议生态（12 仓库） | F-006~F-029、F-073~F-077 |
| 01 | [行级版本控制机制](01-dolt-versioning-mechanism.md) | Prolly Tree 存储引擎、行级历史视图、分支/合并/回滚机制、MySQL 5.7 兼容原理、MCP/AI Agent 工作流 | F-017~F-029、F-061~F-070、F-078~F-085 |
| 02 | [边界、限制与选型建议](02-dolt-boundaries-trends.md) | 性能限制（TPC-C 54%）、1G 阈值勘误、迁移成本、适用场景、行业趋势、选型启示 | F-034~F-059、F-060 |

### 第二层：源码实现层（CLI 命令层）

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 03 | [CLI 命令体系架构](03-dolt-cli-architecture.md) | main() 入口、Command 接口、SubCommandHandler 分发、三组白名单、DoltEnv 环境模型、Ref 系统、哈希规范、ChunkStore 接口 | F-086~F-111 |

### 第三层：源码实现层（SQL 版本控制层）

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 04 | [SQL 版本控制 API](04-sql-version-control-api.md) | dprocedures（38 条）、dfunctions（10 个）、dtablefunctions（13 个）API 体系、SQL 引擎集成、HistoryTable、SessionDatabase、事务模型、Merge/Conflict | F-112~F-153 |

### 第四层：源码实现层（存储内核层）

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 05 | [存储内核架构](05-storage-kernel-architecture.md) | NBS（内容寻址 DAG）、Prolly Tree（NodeStore/StaticMap/MutableMap）、Flatbuffer 序列化、DoltDB 高层句柄、Commit 模型 | F-157~F-182 |

### 第五层：源码实现层（生态与工作流）

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 06 | [生态与工作流](06-dolt-ecosystem-and-workflows.md) | 远程操作、系统表全景、GraphQL API、Web 服务器、AI Agent 指南（AGENT.md）、测试基准、凭据管理 | F-183~F-192 |

## 阅读路径建议

```
【入门路径】
00-dolt-overview（认识产品全貌 + 12 仓库生态）
    ↓
01-dolt-versioning-mechanism（理解行级版本控制机制）
    ↓
02-dolt-boundaries-trends（明确边界与适用场景 + 勘误说明）

【进阶路径】（源码阅读导向）
03-dolt-cli-architecture（CLI 命令层：入口/分发/环境模型）
    ↓
04-sql-version-control-api（SQL 版本控制 API 层：存储过程/函数/表函数）
    ↓
05-storage-kernel-architecture（存储内核层：NBS + Prolly Tree + Flatbuffer）
    ↓
06-dolt-ecosystem-and-workflows（生态与工作流：系统表/测试/配置）

【快速参考】
- 只想了解产品定位 → 00
- 想理解为什么这样设计 → 00 → 01
- 想深入源码阅读 → 03 → 04 → 05 → 06
- 想了解边界与选型 → 02
```

## 概念依赖关系

```
00-dolt-overview
    ├── 01-dolt-versioning-mechanism
    │     └── 02-dolt-boundaries-trends（性能限制/勘误引用前文）
    │
    └── 03-dolt-cli-architecture（CLI 层实现补充 00）
          ├── 04-sql-version-control-api（SQL API 层依赖 CLI env）
          │     └── 05-storage-kernel-architecture（SQL 层依赖存储内核）
          │           └── 06-dolt-ecosystem-and-workflows（生态层依赖前四层）
```

```{toctree}
:hidden:
:maxdepth: 7

00-dolt-overview
01-dolt-versioning-mechanism
02-dolt-boundaries-trends
03-dolt-cli-architecture
04-sql-version-control-api
05-storage-kernel-architecture
06-dolt-ecosystem-and-workflows
```
