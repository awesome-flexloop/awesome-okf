---
type: Concept
title: "Dolt MCP Server 概述"
description: "dolt-mcp 是什么——给 AI 助手提供 Dolt/DoltgreSQL/DoltLite 数据库访问能力的 MCP Server：产品定位、解决的核心问题、三方言后端、45 工具能力版图与适用场景"
tags: [dolt-mcp, mcp, ai-agent, database, overview, dolthub]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-source
    resource: /references/source.md
    title: dolt-mcp 源码事实登记
---

# Dolt MCP Server 概述

> 本文介绍 dolt-mcp 的产品定位与能力版图。对应 [F-001~F-008、F-160~F-162](/references/source.md)。

## 是什么

**Dolt MCP Server**（`github.com/dolthub/dolt-mcp`）是一个 Model Context Protocol（MCP）服务器 [F-006]，作为 AI 助手（如 Claude）与 Dolt 版本化 SQL 数据库之间的桥 [F-160]。它把"数据库操作 + 版本控制工作流 + 数据管理"封装成一组可供 AI 直接调用的工具——数据库管理、表操作、版本控制（分支/提交/合并/diff）、数据读写、远程仓库操作（clone/fetch/push/pull）[F-160]。

一句话定位：**让 AI 助手能安全、结构化地操作一个 Git 式版本控制的 SQL 数据库**。

| 维度 | 说明 |
|------|------|
| 仓库 | `github.com/dolthub/dolt-mcp`（F-001） |
| 模块名 | `github.com/dolthub/dolt-mcp`，Go 1.25（F-001） |
| 服务名/版本 | `dolt-mcp` / 0.3.8（F-002） |
| MCP 协议实现 | `mark3labs/mcp-go` v0.34.0（F-006） |
| 分析版本 | HEAD `cde8e48`（v0.3.8 + 5 commits，2026-08-18） |
| 生态归属 | DoltHub 数据版本控制产品家族 |

## 解决的核心问题

AI 助手要"认真操作数据库"时天然面临三重障碍，dolt-mcp 逐一拆解：

1. **接入协议多样**：AI 原生理解 MCP，不熟悉 MySQL/PostgreSQL 线协议。dolt-mcp 在中间做协议翻译——AI 走 MCP，dolt-mcp 走 MySQL 或 PostgreSQL 线协议连库（F-060/F-064）。
2. **裸 SQL 太危险**：让 AI 直接执行任意 SQL，一个误写就破坏数据。dolt-mcp 把能力切成 `query`（只读）/`exec`（写入）双通道，且每条语句先过方言 SQL 解析器校验（F-113/F-114/F-062/F-068）。
3. **数据实验要沙箱**：版本控制数据库的价值在于"随便试、可回滚"。dolt-mcp 把分支/提交/合并/diff 变成 AI 可调用的工具，使 AI 能在分支上做数据实验而不污染主分支（F-117~F-136）。

## 三方言后端

同一份 server 逻辑通过 `Dialect` 抽象适配三种数据库引擎（F-043），启动时用标志位选择：

| 方言 | 兼容协议 | 启动标志 | 端口默认 | 典型角色 |
|------|---------|---------|---------|---------|
| Dolt | MySQL | `--dolt`（默认） | 3306 | MySQL 兼容的版本化数据库 |
| DoltgreSQL | PostgreSQL | `--doltgres` | 5432 | Postgres 兼容的版本化数据库 |
| DoltLite | SQLite fork | `--doltlite` | -（内嵌） | 单文件版本化数据库，零运维本地优先 |

三者互斥（F-025）；DoltLite 需要特殊构建的二进制（含 cgo + libdoltlite），把整个数据库引擎编译进进程（F-090）。

## 45 工具能力版图

注册表中 **45 项工具**（F-014/F-015）按 README 宣称分六大类（F-160），对应关系见 [工具全景](03-tools-overview.md)：

```
数据库管理（list_databases / create_database / drop_database / clone_database / select_version）
表操作（show_tables / show_create_table / describe_table / create_table / alter_table / drop_table）
数据读写（query 只读 / exec 写入）
分支管理（list_dolt_branches / select_active_branch / create_dolt_branch / create_dolt_branch_from_head / delete_dolt_branch / move_dolt_branch）
版本控制（list_dolt_commits / create_dolt_commit / stage_table_for_dolt_commit / stage_all_tables_for_dolt_commit / unstage_table / unstage_all_tables）
diff/状态（list_dolt_diff_changes_* / get_dolt_merge_status）
合并（merge_dolt_branch / merge_dolt_branch_no_fast_forward）
重置（dolt_reset_soft / dolt_reset_hard）
远程（list/add/remove_dolt_remote / dolt_fetch_branch / dolt_fetch_all_branches / dolt_push_branch / dolt_pull_branch）
测试（run_dolt_tests / add_dolt_test / remove_dolt_test）
```

## 部署形态

两种传输模式（F-022）：

- **stdio**：AI 助手以子进程方式拉起 server，通过标准输入输出通信——Claude Desktop / CLI 集成的主流方式（F-085）。
- **HTTP**：独立监听端口（默认 8080，端点 `/mcp`）的流式 HTTP server，面向 Web 应用与自定义集成；支持 JWT bearer 认证与 HTTPS（F-080~F-084）。

另有官方 Docker 镜像 `dolthub/dolt-mcp`，提供 `latest` 与 `-doltlite` 两个变体（F-033），详见 [部署与配置](02-deployment-configuration.md)。

## 典型适用场景

- **AI 驱动的数据分析**：让 Claude 直接对销售/订单表执行查询、按需创建临时分支做数据变换实验 [F-160]
- **数据版本控制工作流自动化**：AI 在 `feature-users` 分支建表→提交→合并回 main，形成可审计的变更链路（F-119~F-127）
- **本地优先 AI 数据应用**：DoltLite 单文件内嵌，AI 应用随数据文件即开即用（F-161）

## 与相邻束的关系

- **dolt 束**（[dolt/index.md](../dolt/index.md)）：讲 Dolt 数据库本身（Prolly Tree 存储、行级历史、Git 式版本控制机制）；本束聚焦把 Dolt 能力接入 AI 的 MCP Server 层。
- **dolthub-cli（dh）束**（`../dolthub-cli/index.md`，待该束发布后生效）：操作 DoltHub 云平台的 `dh` CLI；本束面向任意 Dolt/Doltgres/DoltLite 实例。

## 相关概念

* [架构分层](/concepts/01-architecture.md)
* [工具全景](/concepts/03-tools-overview.md)
* [DoltLite 内嵌模式](/concepts/06-doltlite-mode.md)
