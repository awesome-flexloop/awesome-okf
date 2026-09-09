# 行级版本控制机制

> 本文档深入讲解 Dolt 的核心技术机制：Prolly Tree 存储引擎、行级历史视图、分支/合并/回滚原理、MySQL 5.7 兼容机制，以及 MCP Server 与 AI Agent 工作流。对应 F-017~F-029、F-061~F-064、F-070（博文事实）+ F-078~F-085（源码事实）。
> **信源距离**：③ 第三方综述；机制原理解释基于博文描述与官方文档交叉引用，存储引擎架构经本地源码（①）核验。

---

## Prolly Tree 存储引擎

Dolt 的存储引擎基于 Prolly Tree（Proximity Lookup Tree），这是一种为版本控制优化的 BTree 变体。与传统 BTree 不同，Prolly Tree 通过内容的哈希值进行排序而非键值排序，这使得数据的增量变更能够以近似 O(log n) 的代价被追踪——相当于为每一行数据维护了一个不可变的版本链。

这一设计使 Dolt 能够在不复制全量数据的情况下，高效地维护多个版本分支。Dolt 将版本控制放在数据库底层，每一条记录的变化都可以被追踪到（F-070）。

### 源码架构（经本地源码核验，①）

经 `dolt/go/store/prolly/doc.go` 与 `dolt/go/store/datas/doc.go` 核验，存储引擎的分层结构如下（F-078~F-081）：

- **Prolly Tree 层**（`go/store/prolly`）：用 `NodeStore` 抽象构建树，序列化到/自 flatbuffer 消息（`go/serial`）。节点类型含 `AddressMap`、`ProllyTreeNode`、`CommitClosure`；节点通过内容哈希寻址，区分内部节点（值为子节点地址）与叶节点（值为实际数据）。
- **NBS 存储层**（`go/store/nbs`，Noms Block Store）：提供内容寻址 DAG 存储，20 字节哈希寻址，只有 insert/update root/gc（无 update/delete），支持本地磁盘与 AWS S3/DynamoDB 后端（F-079）。
- **Commit 数据结构**（`go/serial/commit.fbs`）：用 flatbuffer 序列化（file identifier "DCMT"），字段含 `root`（根值哈希）、`height`（提交高度）、`parent_addrs`（父提交）、`parent_closure`（父提交闭包，用于 pull/fetch/push 扇出与 FindCommonAncestor）、`signature`（签名）（F-080）。
- **datas 桥接层**（`go/store/datas`）：桥接数据库事务与版本化 commit graph 逻辑；旧存储格式为 NomsBlockStore，新存储格式为 NodeStore。
- **上游渊源**：Dolt 存储引擎源自 Noms 项目（Attic Labs，Apache-2.0）（F-081）。

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

### who/when 审计粒度

通过历史视图，可以查询某一个数据单元格是**谁、在什么时间**修改的（F-062）；对于单条记录（如员工表 ID=0），从最早版本到当前版本的所有变更内容都能直接查看（F-063）。这意味着审计粒度从"时间点恢复"细化到了"单元格级责任追溯"。

---

## 分支/合并/回滚机制

### 分支

Dolt 支持创建数据分支（F-021），分支上修改不影响主分支数据。与数据库事务仅撑几秒不同（F-022），Dolt 的分支可以持续数周甚至数月，非常适合长期数据实验。

提交粒度细到行级——修改一行数据即可提交版本；在分支上做测试不影响主库，确认无误后再合并回去（F-061）。

以往要在生产数据上做实验，一般需要先复制一份数据出来；有了分支工作流后，直接开个分支即可，分支替代了数据复制（F-064）。

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

## MySQL 协议兼容

Dolt 兼容 MySQL 5.7 协议（F-013，✅ 官方确认），默认端口 3306（F-014，✅ 官方确认），默认用户名 root（F-015），默认密码为空（F-016）。

经本地源码核验，Dolt 的 MySQL 兼容基于 **Vitess** 协议层 + **go-mysql-server** SQL 引擎（F-082），服务端版本显示 "5.7.9-Vitess"，客户端支持到 MySQL 8.4 LTS（F-083）。这意味着所有基于 MySQL 协议的客户端工具（Navicat、DBeaver、DataGrip、TablePlus 等）均可直接连接 Dolt，无需额外配置（F-030~F-033）。这一兼容性大幅降低了迁移成本——现有 MySQL 应用只需更改连接地址即可接入 Dolt。

---

## MCP Server 与 AI Agent 工作流

### MCP Server 架构

Dolt 发布了 MCP Server（F-024，✅ 官方仓库 [dolthub/dolt-mcp](https://github.com/dolthub/dolt-mcp)，2025-08-14 正式发布），使 AI Agent 能通过标准协议操作数据库。

MCP（Model Context Protocol）是 Anthropic 提出的 AI Agent 与外部工具交互的标准协议。经本地源码核验，MCP Server 提供 **40+ 工具**，支持 **Dolt/Doltgres/DoltLite 三种方言**，可运行于 HTTP 或 stdio 模式，DoltLite 模式可嵌入单文件数据库无需独立 server（F-084）。其工具按功能分类覆盖：

1. **数据库管理**：list_databases、create_database、drop_database
2. **表操作**：create_table、alter_table、drop_table、describe_table
3. **版本控制**：create_dolt_commit、stage_table、create_dolt_branch、merge_dolt_branch、dolt_reset
4. **远程操作**：clone_database、dolt_push_branch、dolt_pull_branch、dolt_fetch_all_branches
5. **数据操作**：query（只读，带只读标注 + 只读查询校验）、exec（写入）

AI Agent 可借助 MCP Server 在独立分支上操作数据（F-025），执行 SQL 查询、创建/合并/回退分支、查看历史变更。

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

作者认为，对不熟悉 Git 的数据分析师来说，这种带界面的操作友好很多（F-065，作者观点）。

---

## 小结

Dolt 通过 Prolly Tree 存储引擎实现了存储层的 Git 式版本控制，通过 MySQL 5.7 协议兼容降低了使用门槛，通过 MCP Server 为 AI Agent 提供了安全的沙箱操作环境。这三层设计共同构成了"数据库也能像 Git 一样用"的核心能力。

---

*本文档基于博文事实（F-017~F-029、F-061~F-064、F-070）与源码事实（F-078~F-085）生成，MCP Server 与 Workbench 已通过官方仓库核验 ✅，存储引擎架构经本地源码核验 ✅。*
