---
type: example
title: 使用 Agent Mode
description: 如何使用 Claude AI Agent 进行智能数据库查询和操作
tags: [dolt-workbench, agent, claude, ai, tutorial]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: agent-src
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/web/main/agent/anthropicAgent.ts
    title: ClaudeAgent 实现
  - id: agent-ipc
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/web/main/agent/ipcHandlers.ts
    title: IPC Agent Handlers
---

# 使用 Agent Mode

## 概述

Agent Mode 允许用户使用自然语言与数据库交互。Claude AI 会理解您的查询，生成 SQL，执行并展示结果。

## 启用 Agent

### 1. 配置 API Key

在 Agent 面板中输入您的 Anthropic API Key：

```
Settings → Agent → API Key → [输入您的 key]
```

### 2. 选择数据库

确保已连接到数据库，Agent 会根据当前数据库类型生成相应的查询。

### 3. 打开通话面板

点击界面右侧的 "Agent" 按钮打开通话面板。

## 基本用法

### 查询数据

**自然语言**: "Show me all customers from New York"

**生成的 SQL**:
```sql
SELECT * FROM customers WHERE city = 'New York';
```

### 统计查询

**自然语言**: "How many orders did we have last month?"

**生成的 SQL**:
```sql
SELECT COUNT(*) as order_count 
FROM orders 
WHERE created_at >= DATE('now', '-1 month');
```

### Schema 查询

**自然语言**: "What tables are in this database?"

**生成的 SQL**:
```sql
SHOW TABLES;
-- 或
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'your_database';
```

## 高级用法

### 分支操作（Dolt/Doltgres）

**自然语言**: "Create a new branch called feature/user-profile"

**生成的 SQL**:
```sql
CALL DOLT_BRANCH('feature/user-profile');
```

**自然语言**: "Show me the diff between master and feature/user-profile"

**生成的 SQL**:
```sql
SELECT * FROM dolt_diff('master', 'feature/user-profile');
```

### 提交操作

**自然语言**: "Commit my changes with message 'Fix user validation'"

**生成的 SQL**:
```sql
CALL DOLT_COMMIT('-a', '-m', 'Fix user validation');
```

### 合并操作

**自然语言**: "Merge feature/user-profile into master"

**生成的 SQL**:
```sql
CALL DOLT_MERGE('feature/user-profile');
```

## 工具调用确认

以下操作需要用户确认才能执行：

| 工具 | 说明 |
|---|---|
| `create_dolt_commit` | 创建提交 |
| `delete_dolt_branch` | 删除分支 |
| `move_dolt_branch` | 移动分支 |
| `dolt_reset_hard` | 硬重置 |

当 AI 尝试执行这些操作时，会弹出确认对话框。

## MCP 工具

Agent 注册了 3 个自定义 MCP 工具：

### switch_branch

切换数据库分支。

**使用示例**:
```
Switch to the feature/auth branch
```

### refresh_page

刷新当前页面数据。

**使用示例**:
```
Refresh the current view
```

### display_image

在聊天中显示图片。

**使用示例**:
```
Show me the ER diagram
```

## 会话管理

### 创建新会话

点击 Agent 面板的 "New Session" 按钮。

### 列出会话

```
List all my sessions
```

### 切换会话

```
Switch to session: [session-name]
```

### 清除历史

```
Clear our conversation
```

## 最佳实践

### 1. 明确指定数据库

```
In the orders table, show me...
```

### 2. 使用表名和列名

```
Show columns in the customers table
```

### 3. 指定排序和限制

```
Show the top 10 customers by total spending
```

### 4. 询问解释

```
Explain what this query does
```

## 错误处理

如果 Agent 生成的 SQL 有误：

1. **查看错误信息**: Agent 会显示错误详情
2. **修正提示**: 告诉 AI 哪里出错了
3. **重试**: 让 AI 重新生成查询

常见错误：
- 表名不存在
- 列名拼写错误
- SQL 语法错误

## 安全提示

- API Key 存储在本地，不会上传到服务器
- 敏感操作需要确认
- 建议在只读副本上测试复杂查询

## 参考文档

- [快速开始](./00-getting-started.md)
- [连接数据库](./01-connecting-databases.md)
