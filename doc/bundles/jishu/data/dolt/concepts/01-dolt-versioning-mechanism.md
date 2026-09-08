# 行级版本控制机制

> 本文档深入讲解 Dolt 的核心技术机制：Prolly Tree 存储引擎、行级历史视图、分支/合并/回滚原理、MySQL 5.7 兼容机制，以及 MCP Server 与 AI Agent 工作流。对应 F-017~F-029。
> **信源距离**：③ 第三方综述；机制原理解释基于博文描述与官方文档交叉引用。

---

## Prolly Tree 存储引擎

Dolt 的存储引擎基于 Prolly Tree（Proximity Lookup Tree），这是一种为版本控制优化的 BTree 变体。与传统 BTree 不同，Prolly Tree 通过内容的哈希值进行排序而非键值排序，这使得数据的增量变更能够以近似 O(log n) 的代价被追踪——相当于为每一行数据维护了一个不可变的版本链。

这一设计使 Dolt 能够在不复制全量数据的情况下，高效地维护多个版本分支。

---

## 行级历史视图

### 自动生成的历史表

Dolt 为每个表自动生成名为 `dolt_history_<tablename>` 的历史视图（F-017），无需额外设置（F-020）。示例表名如 `dolt_history_employees`（F-018）。

查询方式与传统 SQL 一致：

```sql
SELECT * FROM dolt_history_employees WHERE id = 0;
```

（F-019）

这一设计使得行级回溯成为可能——你可以精确查询"某一行在某个时间点是什么样子"，而传统数据库方案只能做到时间点级恢复。

---

## 分支/合并/回滚机制

### 分支

Dolt 支持创建数据分支（F-021），分支上修改不影响主分支数据。与数据库事务仅撑几秒不同（F-022），Dolt 的分支可以持续数周甚至数月，非常适合长期数据实验。

```bash
dolt branch experiment    # 创建实验分支
dolt checkout experiment  # 切换到实验分支
# ... 在分支上操作数据 ...
dolt checkout main        # 切回主分支
```

### 合并

Dolt 合并分支时如有冲突会检测并提示（F-023）。合并操作与传统 Git 类似，支持自动合并、人工解决冲突等流程。

### 回滚

通过分支切换或重置提交，可实现数据回滚。这也是 Dolt 相比传统备份方案的优势之一——回滚粒度可以到单行级别。

---

## MySQL 5.7 协议兼容

Dolt 兼容 MySQL 5.7 协议（F-013，✅ 官方确认），默认端口 3306（F-014，✅ 官方确认），默认用户名 root（F-015），默认密码为空（F-016）。

这意味着所有基于 MySQL 协议的客户端工具（Navicat、DBeaver、DataGrip、TablePlus 等）均可直接连接 Dolt，无需额外配置（F-030~F-033）。这一兼容性大幅降低了迁移成本——现有 MySQL 应用只需更改连接地址即可接入 Dolt。

---

## MCP Server 与 AI Agent 工作流

### MCP Server 架构

Dolt 发布了 MCP Server（F-024，✅ 官方仓库 [dolthub/dolt-mcp](https://github.com/dolthub/dolt-mcp)，2025-08-14 正式发布），使 AI Agent 能通过标准协议操作数据库。

MCP（Model Context Protocol）是 Anthropic 提出的 AI Agent 与外部工具交互的标准协议。Dolt 的 MCP Server 使 AI Agent 可以：

1. 在独立分支上读取/写入数据（F-025）
2. 执行 SQL 查询与分析
3. 创建、合并、回退分支
4. 查看所有历史变更记录

### AI Agent 安全操作工作流

1. **沙箱操作**：AI Agent 在独立分支上执行数据操作，不会影响主分支数据
2. **验证确认**：人工或自动验证分支上的数据变更
3. **安全合并**：确认无误后合并到主分支；有问题则放弃分支

这一机制使得 AI Agent 可以安全地探索、分析和修改数据库，而不会污染生产数据。正如作者所言："Dolt 比直接把 AI 放到生产库跑 SQL 要安全得多"（F-059，作者观点）。

---

## Dolt Workbench

Dolt Workbench（F-026，✅ 官方仓库 [dolthub/dolt-workbench](https://github.com/dolthub/dolt-workbench)，2023-12 发布）是 Dolt 的开源图形化工作台，提供以下核心功能：

| 功能 | 说明 |
|------|------|
| 分支切换 | 可视化切换不同数据分支 |
| 提交日志 | 查看完整的数据变更历史 |
| 差异对比 | 对比两个分支/提交的数据差异 |
| 一键操作 | 点击按钮实现创建、合并和回退（F-029） |
| 多数据库支持 | 支持 Dolt、MySQL、PostgreSQL（F-027） |

2026-08 更新新增 DoltLite 支持，使其能够嵌入轻量级应用场景。

---

## 小结

Dolt 通过 Prolly Tree 存储引擎实现了存储层的 Git 式版本控制，通过 MySQL 5.7 协议兼容降低了使用门槛，通过 MCP Server 为 AI Agent 提供了安全的沙箱操作环境。这三层设计共同构成了"数据库也能像 Git 一样用"的核心能力。

---

*本文档基于博文事实（F-017~F-029）生成，MCP Server 与 Workbench 已通过官方仓库核验 ✅。*
