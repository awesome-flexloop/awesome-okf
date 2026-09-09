# Dolt 概述与产品矩阵

> 本文档覆盖 Dolt 产品定位、核心功能、产品矩阵、开源协议与兼容生态。对应 F-006~F-029、F-066~F-069。
> **信源距离**：③ 第三方综述（公众号「开源日记」转述官方数据）；部分事实经官方源核验（①）确认。

---

## 产品定位

Dolt 是一个在 GitHub 上发布的开源项目（F-006），目标是"让你用 Git 的方式来管理数据库"（F-008）。它从存储层原生支持分支、提交、合并等操作（F-009），被描述为"目前最接近'Git for Database'理念的 SQL 数据库之一"（F-010，作者观点）。

| 属性 | 值 | 信源 |
|------|---|------|
| 开源协议 | Apache-2.0（F-011，✅ 官方确认） | [GitHub LICENSE](https://github.com/dolthub/dolt/blob/main/LICENSE) |
| 官方仓库 | https://github.com/dolthub/dolt（F-012） | — |
| GitHub Stars | 约 23K（博文发布时，F-007，✅ 时点值合理） | 官方 Blog 2026-02 达 20K；gstars.dev 2026-08 约 24K |
| 协议兼容性 | MySQL 5.7（F-013，✅ 官方确认） | [docs.doltdb.com](https://docs.doltdb.com/) |
| 默认端口 | 3306（F-014，✅ 官方确认） | 同上 |
| 默认用户 | root（F-015） | — |
| 默认密码 | 空（F-016） | — |

---

## 核心功能特性

### 行级历史追踪

Dolt 为每个表自动生成名为 `dolt_history_<tablename>` 的历史视图（F-017），无需额外设置（F-020）。示例表名如 `dolt_history_employees`（F-018），查询方式与传统 SQL 一致（F-019）：

```sql
SELECT * FROM dolt_history_employees WHERE id = 0;
```

### 分支与合并工作流

Dolt 支持创建数据分支，分支上的修改不影响主分支数据（F-021）。与数据库事务仅撑几秒不同，Dolt 的分支可以持续数周甚至数月（F-022）。合并分支时如有冲突会检测并提示（F-023）。

### MCP Server 与 AI Agent 安全操作

Dolt 发布了 MCP Server（F-024，✅ 官方仓库 [dolthub/dolt-mcp](https://github.com/dolthub/dolt-mcp)，2025-08-14 正式发布），使 AI Agent 能通过标准协议操作数据库。AI Agent 可在独立分支上操作数据，确认后合并或放弃（F-025），这比直接把 AI 放到生产库跑 SQL 安全得多（F-059，作者观点）。

### Dolt Workbench

Dolt Workbench 是 Dolt 的开源图形化工作台（F-026，✅ 官方仓库 [dolthub/dolt-workbench](https://github.com/dolthub/dolt-workbench)，2023-12 发布，2026-08 新增 DoltLite 支持），可用于操作 MySQL 和 PostgreSQL（F-027）。它提供切换分支、查看提交日志、对比分支差异的可视化界面（F-028），并支持点击按钮实现创建、合并和回退操作（F-029）。

---

## 产品矩阵

| 产品 | 说明 | 状态 |
|------|------|------|
| **Dolt** | 核心版本化 SQL 数据库（CLI + MySQL 协议） | 生产可用 |
| **DoltHub** | 云端托管服务，支持分支/协作 | 运营中 |
| **DoltLab** | 企业版功能（权限、审计等） | 商业化 |
| **Hosted Dolt** | 托管数据库服务 | 运营中 |
| **Dolt MCP Server** | AI Agent 标准协议接口 | 2025-08-14 发布 |
| **Dolt Workbench** | 开源图形化工作台 | 2023-12 首版，2026-08 支持 DoltLite |

> 产品矩阵信息综合自博文转述与官方仓库 README，具体功能以各产品官方文档为准。

---

## 兼容生态

Dolt 兼容 MySQL 5.7 协议（F-013），主流数据库客户端工具可直接连接，无需额外配置。博文称绝大多数 MySQL 客户端都能直接连接使用（F-066）：

| 工具 | 连接方式 | 备注 |
|------|---------|------|
| Navicat（F-030） | 直接连接 | 无需额外配置 |
| DBeaver（F-031） | 直接连接 | 无需额外配置 |
| DataGrip（F-032） | 直接连接 | 无需额外配置 |
| TablePlus（F-033） | 直接连接 | 无需额外配置 |

---

## 安装与快速开始

Dolt 提供 Mac、Windows、Linux 三平台安装包（F-034），下载地址为 GitHub Releases（F-035）。安装后需设置用户名、邮箱等信息（与 Git 类似，F-036）。

```bash
# 初始化数据库
dolt init                              # F-037

# 启动 SQL 服务器（默认端口 3306）
dolt sql server                         # F-038

# 连接数据库
mysql --host=127.0.0.1 --port=3306 -u root  # F-039

# 体验分支/合并/日志
dolt branch                             # F-041
dolt merge                              # F-041
dolt log                                # F-041
```

> **建议**：先用小数据量测试版本控制功能（F-040），熟悉后再用于生产场景。

连接之后即可正常建表、插数据、做 commit（F-067）。作者实测称，用 TablePlus 或 DBeaver 直接连接后，创建表、插入数据、执行 commit 等操作都十分自然（F-068，作者实测观点）。

---

## 与传统备份方案的对比

传统"数据库版本控制"通常指定期备份 + binlog 回放（F-050），颗粒度大，可恢复到时间点但看不到谁修改了哪一行（F-051）。多人同时修改数据时需互相锁定或通过沟通防止冲突（F-052）。

此外，传统方案的痛点在于时效性：过去改错数据，要么靠备份恢复，要么翻审计日志倒查，发现问题时往往已经晚了（F-069）。

Dolt 的思路是：备份变"提交"，恢复变"回滚"，数据实验变"分支"（F-053，作者观点）。此外，Dolt 可在修改之前看到差别（diff 机制，F-054）。

---

*本文档基于博文事实（F-006~F-029、F-066~F-069）生成，P0 声明（F-007/F-011/F-013/F-014/F-024/F-026）已全部核验 ✅。*
