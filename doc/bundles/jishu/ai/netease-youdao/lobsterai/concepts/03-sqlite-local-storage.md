---
type: concept
title: "SQLite 本地优先存储层"
description: "SqliteStore 工厂建库、better-sqlite3 同步驱动、13 张表的五域划分、PRAGMA 列存在性迁移策略，以及消息级联删除与索引设计。"
tags: [lobsterai, sqlite, better-sqlite3, migration, local-first]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# SQLite 本地优先存储层

LobsterAI 的全部持久化状态集中在一个 SQLite 数据库中，由 better-sqlite3 驱动（F-la-004）——这是一个明确的「本地优先」架构宣言：会话、消息、记忆、Agent 定义、MCP 服务器配置、定时任务绑定、插件安装、子代理运行记录，全部落在用户本机一个数据库文件里。

## 一、建库与迁移

`SqliteStore` 提供静态工厂方法 `static async create(userDataPath?)`（F-la-015）：调用方不传路径时使用 Electron `userData` 目录，工厂内部完成建库与全部建表。

迁移策略**不用版本化迁移框架**（如 knex/drizzle），而是对每张表做 `PRAGMA table_info()` 列存在性检查、就地补列（F-la-015）：

```ts
// 伪代码，逻辑忠实于 sqliteStore.ts 迁移段
const colNames = this.db.pragma(`table_info(cowork_sessions)`).map((c: any) => c.name);
if (!colNames.includes('fork_mode')) {
  this.db.exec("ALTER TABLE cowork_sessions ADD COLUMN fork_mode TEXT NOT NULL DEFAULT 'none';");
}
```

源码中 fork 相关四列（`fork_mode`、`fork_workspace_path`、`fork_git_branch`、`fork_git_base_ref`）正是以这种方式补入 `cowork_sessions` 的。该策略的适用前提是 schema 演进**以加列为主**：代码量小、无迁移历史包袱；代价是无迁移历史、无法回滚，出现改列/删列需求时应回到版本化迁移。

## 二、13 张表的五域划分

数据库共 13 张表（`CREATE TABLE IF NOT EXISTS` 逐条计数，F-la-016），可按职责划分为五域：

| 域 | 表 | 说明 |
|---|---|---|
| 键值 | `kv` | 通用键值存储 |
| 会话/消息 | `cowork_sessions`、`cowork_messages`、`cowork_session_capsules` | 会话元数据（含 `claude_session_id`、`scheduled_task_id`、`fork_*` 列）、消息体、连续性胶囊 |
| 配置与记忆 | `cowork_config`、`user_memories`、`user_memory_sources` | 应用配置、用户记忆及其来源 |
| Agent/MCP/插件 | `agents`、`mcp_servers`、`mcp_launch_resolutions`、`user_plugins` | 外部集成配置 |
| 子代理 | `subagent_runs`、`subagent_messages` | 子代理运行记录 |

### 会话表：fork 与定时任务的双向绑定

`cowork_sessions` 的列设计揭示了跨子系统的数据关系（F-la-016）：`claude_session_id` 关联 OpenClaw 运行时会话，`scheduled_task_id` 反向指向创建它的定时任务（定时任务子系统据此实现会话绑定，见 [/concepts/10-scheduled-tasks.md](10-scheduled-tasks.md)），`fork_*` 四列记录会话分叉元数据（见 [/concepts/04-session-message-store.md](04-session-message-store.md)）。

### agents 表：JSON 列存储技能绑定

`agents` 表共 20 列（F-la-018），其中 `skill_ids` 以 JSON 字符串存储技能 ID 列表，另有 `source`、`preset_id` 列标识来源与预设关系（Agent 体系详见 [/concepts/06-agent-preset-system.md](06-agent-preset-system.md)）。以 JSON 列承载"一对多且结构稳定"的技能绑定，避免了关联表 join 的复杂度。

### 消息表：级联删除与会话索引

`cowork_messages` 外键关联会话表且 `ON DELETE CASCADE`，并建有 `idx_cowork_messages_session_id` 索引（F-la-017）：删除会话即自动清理全部消息，消息分页查询走覆盖索引。本地优先应用必须对"删除会话"这类级联操作有清晰的数据完整性约定，外键级联是最省事且最不易漏的实现。

## 三、与测试工程的关系

`tests/` 目录含 `sqlite-backup/` 子目录（F-la-073），指向数据库备份/恢复的专项测试——本地单文件数据库的天然优势是备份即复制文件，天然风险是热备份一致性，值得独立测试目录。

## 设计启示

1. 表划分可直接复用为本地优先 Agent 产品的数据域模板：键值 / 会话消息 / 配置记忆 / 外部集成 / 子代理五域；
2. ad-hoc 列存在性迁移适合"只加列"的演进曲线，采纳前须确认团队能接受无回滚的约束；
3. 跨子系统的绑定关系（`scheduled_task_id`、fork 元数据）直接落在会话表的列上，而非独立关联表——单库内聚时这是合理的简化。

## 相关概念

- [/concepts/00-overall-architecture.md](00-overall-architecture.md)
- [/concepts/04-session-message-store.md](04-session-message-store.md)
- [/concepts/06-agent-preset-system.md](06-agent-preset-system.md)
