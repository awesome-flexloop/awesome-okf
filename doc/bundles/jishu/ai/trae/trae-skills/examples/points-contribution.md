---
type: Example
title: 社区积分贡献示例
description: 演示提交 PR、解决 Issue 后社区积分自动计算的完整链路，包括 eventKey 生成、Ledger 去重、排行榜更新和手动加分操作。
tags: [trae-skills, example, community-points, contribution, github-actions]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 积分贡献完整链路

本示例演示一个贡献者从提交 PR 到积分更新的完整自动化流程。

## 场景 1：提交 PR 被合并（+1 分）

### 步骤

1. 贡献者 `zhangsan` Fork 仓库，创建分支 `feature/cn-punctuation-checker`
2. 开发新技能 `cn-punctuation-checker`
3. 创建 Pull Request #42，描述：
   ```
   添加中文标点检查技能

   这个技能可以检测中文文本中的英文标点错误。
   ```
4. PR 被 Review 并合并到 main 分支

### 自动触发流程

PR 合并触发 `pull_request closed` 事件（merged=true）：

1. GitHub Actions 工作流 `community-points.yml` 被触发
2. 检出代码，切换到 `community-points-data` 分支
3. 运行 `update-community-points.js`：
   - 检测到 PR #42 被合并
   - 检查 actor `zhangsan` 是否在忽略列表（不是 bot）
   - 生成 eventKey：`pr:42:merged`
   - 检查 ledger 中是否已存在该 eventKey（不存在，继续）
   - 给 `zhangsan` 加 1 分：`scores.zhangsan = 1`
   - 记录 ledger：`ledger["pr:42:merged"] = {user: "zhangsan", points: 1, type: "pr_merged"}`
4. 检测到 `community-points.json` 和 `community-leaderboard.md` 有变更
5. 以 `github-actions[bot]` 身份提交并推送到 `community-points-data` 分支

### 结果

```json
// community-points.json
{
  "scores": {
    "zhangsan": 1
  },
  "ledger": {
    "pr:42:merged": {"user": "zhangsan", "points": 1, "type": "pr_merged", "pr": 42}
  }
}
```

排行榜更新为：
```markdown
| 排名 | 用户 | 积分 |
|------|------|------|
| 1 | zhangsan | 1 |

Updated at: 2026-04-22T10:30:00.000Z
```

## 场景 2：PR 解决 Issue（额外 +1 分）

### 步骤

1. 贡献者 `lisi` 发现 Issue #15（"希望添加热榜新闻技能"）
2. 创建 PR #43，描述中引用：
   ```
   添加 daily-hot-news 热榜聚合技能

   Closes #15
   ```
3. PR 被合并

### 自动触发流程

1. PR 合并触发工作流
2. 脚本通过正则检测到 `Closes #15`
3. 查询 GraphQL 确认 Issue #15 确实被此 PR 关闭
4. 生成两个 eventKey：
   - `pr:43:merged`（PR 合并 +1 分）
   - `issue:15:resolved-by-pr:43`（解决 Issue 额外 +1 分）
5. 给 `lisi` 加 2 分

### 结果

```json
{
  "scores": {
    "zhangsan": 1,
    "lisi": 2
  },
  "ledger": {
    "pr:42:merged": {"user": "zhangsan", "points": 1, "type": "pr_merged", "pr": 42},
    "pr:43:merged": {"user": "lisi", "points": 1, "type": "pr_merged", "pr": 43},
    "issue:15:resolved-by-pr:43": {"user": "lisi", "points": 1, "type": "issue_resolved", "issue": 15, "pr": 43}
  }
}
```

支持的 PR-Issue 关联关键字：
- `close #15` / `closes #15` / `closed #15`
- `fix #15` / `fixes #15` / `fixed #15`
- `resolve #15` / `resolves #15` / `resolved #15`
- 跨仓库：`owner/repo#15`
- URL 格式：`https://github.com/owner/repo/issues/15`

## 场景 3：直接关闭 Issue（+1 分）

### 步骤

1. 贡献者 `wangwu` 发现 Issue #20 是一个重复问题
2. 直接关闭 Issue（没有通过 PR 解决）

### 自动触发流程

1. Issue 关闭触发 `issues closed` 事件
2. 脚本通过 GraphQL 查询：Issue #20 是否由某个合并的 PR 解决？
3. 查询结果：否（直接关闭，无关联 PR）
4. 生成 eventKey：`issue:20:closed`
5. 给 `wangwu` 加 1 分

### 关键：积分归谁？

如果 Issue 是被 PR 合并关闭的：
- 积分归 **PR 作者**（在 PR 合并时已经记分）
- 关闭 Issue 的人不得分（避免重复计分）

如果 Issue 是直接关闭的（非 PR 解决）：
- 积分归 **关闭 Issue 的人**

## 场景 4：手动加分

### 操作步骤

1. 仓库维护者在 GitHub Actions 页面手动触发 `Community Points` 工作流
2. 输入参数：
   - `manual_user`: `zhangsan`
   - `manual_points`: `3`
   - `manual_reason`: `特殊贡献：提供了视频处理算法设计`
   - `manual_event_key`: `video-algorithm-design`

### 自动触发流程

1. `workflow_dispatch` 事件触发工作流
2. 生成 eventKey：`manual:video-algorithm-design:zhangsan`
3. 检查 ledger（无重复）
4. 给 `zhangsan` 加 3 分
5. ledger 记录 reason 信息

### 结果

`zhangsan` 积分从 1 变为 4。

## 场景 5：幂等性验证（重跑不重复计分）

### 场景

由于网络问题，PR #42 合并时的 Actions 工作流执行了两次（第一次超时，GitHub 自动重跑）。

### 幂等处理

1. 第一次执行：eventKey `pr:42:merged` 不存在，正常给 `zhangsan` 加 1 分
2. 第二次执行：检查 ledger，`pr:42:merged` 已存在，**跳过此次计分**
3. 最终 `zhangsan` 仍为 1 分，不会变成 2 分

这就是 Ledger 幂等键的核心价值——确保同一事件不会被重复计分。

## Bot 用户自动忽略

以下用户的行为不会触发积分：

| 用户 | 原因 |
|------|------|
| `github-actions[bot]` | 硬编码忽略 |
| `dependabot[bot]` | 硬编码忽略 |
| 任何 `*[bot]` 用户 | 正则匹配忽略 |
| `POINTS_IGNORE_USERS` 环境变量中的用户 | 可配置忽略 |

例如：dependabot 提交的依赖升级 PR 被合并后，不会给 dependabot[bot] 加分。

## 排行榜排序规则

`formatLeaderboard` 函数生成排行榜：
- 按积分**降序**排列
- 同分按用户名**字母序**排列
- 前三名无特殊标记（无 emoji）

## 数据存储隔离

积分数据存储在独立的 `community-points-data` 分支，而非 main 分支：

**好处**：
1. 积分更新不会污染代码提交历史
2. 可以对 data 分支设置独立的权限控制
3. 积分数据变更不会触发 CI 检查
4. 可以独立管理 data 分支的合并策略

工作流中 checkout 步骤使用 `fetch-depth: 0` 获取完整历史，然后切换到 `community-points-data` 分支（不存在则自动创建）。

## 并发控制

工作流使用 concurrency group 防止并发冲突：

```yaml
concurrency:
  group: community-points
  cancel-in-progress: false
```

- 同一时间只有一个积分更新工作流在运行
- 后续触发排队等待，不会取消进行中的
- 避免多个工作流同时读写 community-points.json 导致数据冲突

## 相关概念

- [社区积分机制](../concepts/06-community-points.md)
- [编写自定义 Skill](../concepts/07-write-skill.md)

## 相关内容

- [源码信源索引](../references/skills-source.md)
