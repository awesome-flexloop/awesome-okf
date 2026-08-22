---
type: Concept
title: 社区积分机制
description: trae-skills 通过 GitHub Actions 工作流 + JSON Ledger 台账实现完全自动化的社区贡献积分系统，支持三类积分事件（手动加分、PR合并、Issue关闭），通过 eventKey 幂等键去重，积分数据存储在独立的 community-points-data 分支。
tags: [trae-skills, community-points, github-actions, ledger, idempotent, automation]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 机制概览

社区贡献激励采用完全自动化的积分系统，无需人工干预：

- **驱动方式**：GitHub Actions 工作流自动触发
- **记账方式**：JSON Ledger（台账）实现幂等记账
- **积分存储**：独立 `community-points-data` 分支（不污染 main 分支代码历史）
- **排行榜**：自动生成 Markdown 格式的 `community-leaderboard.md`

核心设计洞察：积分系统的关键不是"算分"而是"防重复"——通过 eventKey 幂等键确保同一贡献事件不会被多次计分。

## 数据文件结构

### community-points.json

积分数据文件初始结构：
```json
{
  "scores": {},
  "ledger": {}
}
```

- `scores`：键值对，存储用户名→积分数
- `ledger`：键值对，存储 eventKey→事件记录，用于防重复记账

### community-leaderboard.md

Markdown 排行榜文件，初始内容包含表格表头和 "_No contributors yet_" 行，末尾有 `Updated at` 时间戳。由 `formatLeaderboard` 函数自动生成，按积分降序排列（同分按用户名排序）。

## 三类积分事件

| 事件类型 | 触发方式 | 积分 | 说明 |
|----------|----------|------|------|
| `workflow_dispatch` | 手动触发工作流 | 自定义 | 支持 manual_user/manual_points/manual_reason/manual_event_key 参数 |
| `pull_request closed`（merged） | PR 合并 | +1 分 | 若 PR 描述引用 close/fix/resolve #issueNumber，关联 Issue 额外 +1 分 |
| `issues closed` | Issue 关闭 | +1 分 | 通过 GraphQL 查询是否由合并 PR 解决；若是则积分给 PR 作者而非关闭者 |

### PR-Issue 关联检测

update-community-points.js 通过正则表达式提取 PR 描述中 close/fix/resolve 关键字引用的 Issue 编号，支持三种格式：

1. **本地引用**：`#123`
2. **跨仓库引用**：`owner/repo#123`
3. **URL 引用**：`https://github.com/owner/repo/issues/123`

当 PR 合并时：
- PR 作者获得 +1 分（eventKey: `pr:{prNumber}:merged`）
- 若 PR 引用了 close/fix/resolve 的 Issue，PR 作者额外获得 +1 分（eventKey: `issue:{issueNumber}:resolved-by-pr:{prNumber}`）

### Issue 关闭的智能判断

当 Issue 被关闭时：
- 通过 GitHub GraphQL API 查询该 Issue 是否由某个合并的 PR 解决
- 如果是：积分已经在 PR 合并时记给 PR 作者，不再重复计分给关闭者
- 如果否（直接关闭）：关闭者获得 +1 分（eventKey: `issue:{issueNumber}:closed`）

## eventKey 幂等键设计

每个积分事件生成唯一的 eventKey，存入 ledger 防止重复记账：

| 事件类型 | eventKey 格式 | 示例 |
|----------|---------------|------|
| 手动加分 | `manual:{eventSuffix}:{user}` | `manual:special-contribution:zhangsan` |
| PR 合并 | `pr:{prNumber}:merged` | `pr:42:merged` |
| PR 解决 Issue | `issue:{issueNumber}:resolved-by-pr:{prNumber}` | `issue:15:resolved-by-pr:42` |
| Issue 关闭 | `issue:{issueNumber}:closed` | `issue:15:closed` |

即使 GitHub Actions 因网络问题重跑，相同的 eventKey 已存在于 ledger 中，不会重复计分。

## Bot 用户忽略

以下用户自动被排除在积分统计外：
- `github-actions[bot]`（硬编码）
- `dependabot[bot]`（硬编码）
- 所有以 `[bot]` 结尾的用户名
- 通过 `POINTS_IGNORE_USERS` 环境变量配置的额外忽略用户

## GitHub Actions 工作流

工作流文件：`.github/workflows/community-points.yml`，名称 "Community Points"。

### 触发条件

```yaml
on:
  workflow_dispatch:
    inputs:
      manual_user: ...
      manual_points: ...
      manual_reason: ...
      manual_event_key: ...
  pull_request:
    types: [closed]
  issues:
    types: [closed]
```

### 权限配置

```yaml
permissions:
  contents: write      # 需要写入 community-points-data 分支
  pull-requests: read  # 读取 PR 信息
  issues: read         # 读取 Issue 信息
```

### 并发控制

```yaml
concurrency:
  group: community-points
  cancel-in-progress: false   # 不取消进行中的，排队执行
```

使用 concurrency group 确保同一时间只有一个积分更新工作流在运行，避免并发写入冲突。

### 执行流程

```
1. checkout（fetch-depth: 0，在默认分支）
    ↓
2. 切换到 community-points-data 分支（不存在则创建）
    ↓
3. 运行 update-community-points.js 脚本
    ↓
4. 检查是否有文件变更
    ↓
5. 如有变更：以 github-actions[bot] 身份提交并推送到 community-points-data 分支
```

### 脚本参数

update-community-points.js 接收以下环境变量：
- `GITHUB_EVENT_PATH`：事件 payload 路径
- `GITHUB_EVENT_NAME`：事件类型
- `GITHUB_ACTOR`：触发事件的用户
- `GITHUB_REPOSITORY`：仓库路径
- `GITHUB_RUN_ID`：工作流运行 ID
- `GITHUB_TOKEN`：API 访问令牌

### 运行环境

- 运行器：`ubuntu-latest`
- 忽略用户列表：`github-actions[bot],dependabot[bot]`

## 架构设计要点

### 1. 独立分支存储

积分数据存储在 `community-points-data` 分支而非 main 分支，好处：
- 积分更新不会污染代码提交历史
- 可以独立控制分支权限
- 积分数据的变更不会触发 CI 检查

### 2. 事件溯源 + 幂等消费

这是一个典型的"事件溯源+幂等消费"架构：
- GitHub Events（PR/Issue 关闭）作为事件源
- Ledger 记录已处理事件，实现幂等消费
- 即使工作流重跑也不会产生副作用

### 3. PR-Issue 关联自动化

通过 close/fix/resolve 关键字自动检测 PR 和 Issue 的关联关系，无需手动标记：
- 积分归贡献者（PR 作者）而非操作者（关闭 Issue 的人）
- 鼓励开发者在 PR 中关联 Issue

### 4. Bot 自动过滤

自动忽略 bot 用户的行为，避免自动化操作产生虚假积分。

## 可复用性

该积分机制可作为其他开源社区贡献激励的参考模板，关键复用点：
1. 独立分支存储积分数据
2. eventKey 幂等键覆盖所有事件类型
3. PR-Issue 关联通过关键字自动检测
4. Bot 用户和忽略名单通过环境变量配置
5. 完全自动化，无需人工审核

## 相关概念

- [Workflow 编排型技能](/concepts/05-workflow-skills.md)
- [脚本辅助型技能](/concepts/04-script-assisted-skills.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)
- [社区积分贡献示例](/examples/points-contribution.md)
