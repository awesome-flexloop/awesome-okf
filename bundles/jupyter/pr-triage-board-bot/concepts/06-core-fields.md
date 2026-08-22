---
okf_version: "0.2"
type: "concept"
title: "七个核心字段详解"
description: "逐一详解七个核心分类字段的计算逻辑：作者类型、创建日期、变更行数、维护者参与度、CI状态、合并冲突、审批状态"
tags: [core-fields, author-kind, ci-status, approval, merge-conflicts, maintainer-engagement, field-logic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: field-impl-source
    resource: /references/field-implementations-source.md
    title: "字段实现源码"
  - id: utils-source
    resource: /references/utils-source.md
    title: "工具函数源码"
---

# 七个核心字段详解

REQUIRED_FIELDS注册表中包含7个核心字段，每个字段对应一个独立的TypeScript模块，导出getValue函数计算字段值。

## 1. Author Kind（作者类型）

**文件**：`fields/authorkind.ts`
**类型**：SINGLE_SELECT
**选项**：Bot / Maintainer / First Time Contributor / Early Contributor / Seasoned Contributor

### 判定逻辑（优先级从高到低）

```
PR作者登录名
    │
    ├── 在 BOTS 列表中？ ──→ "Bot"
    │   ["dependabot", "pre-commit-ci", "jupyterhub-bot"]
    │
    ├── 是仓库协作者？ ──→ "Maintainer"
    │   (WRITE/MAINTAIN/ADMIN权限)
    │
    └── 查询组织内已关闭PR数
        ├── 0个 ──→ "First Time Contributor"
        ├── <10个 ──→ "Early Contributor"
        └── ≥10个 ──→ "Seasoned Contributor"
```

### 关键细节

- **Bot列表硬编码**：当前只识别3个bot（dependabot、pre-commit-ci、jupyterhub-bot），其他bot账户可能被误判
- **协作者查询使用memoize**：getCollaborators对每个(owner, repo)组合只查询一次
- **PR计数查询**：`getMergedPRCount` 使用GitHub Search API查询 `org:X author:Y is:pr state:closed`，代码中FIXME标注当前统计的是所有关闭PR而非仅已合并PR
- **PR计数也memoize**：使用自定义cacheKey（JSON.stringify(args)）确保多参数正确缓存

## 2. Opened At（创建日期）

**文件**：`fields/openedat.ts`
**类型**：DATE

```typescript
const d = new Date(pr.createdAt);
d.setUTCHours(0, 0, 0, 0);
return d;
```

将PR的 `createdAt`（ISO 8601时间字符串）转为Date对象后，清零UTC时间部分（时/分/秒/毫秒）。这是因为GitHub Project的DATE字段只存储日期，不存储时间。

## 3. Total Lines Changed（变更总行数）

**文件**：`fields/totallineschanged.ts`
**类型**：NUMBER

```typescript
return pr.additions + pr.deletions;
```

将新增行数（additions）和删除行数（deletions）相加。这是变更的总规模，而非净变化（additions - deletions）。例如：一个修改了100行、删除了50行的PR，该字段值为150。

## 4. Maintainer Engagement（维护者参与度）

**文件**：`fields/maintainerengagement.ts`
**类型**：SINGLE_SELECT
**选项**：No Maintainer Engagement / Single Maintainer Engagement / Multiple Maintainer Engagement

### 判定逻辑

```
1. 获取仓库协作者集合（WRITE/MAINTAIN/ADMIN权限）
2. 从协作者集合中移除PR作者本人
3. 获取PR参与者集合（pr.participants.nodes）
4. 计算两个集合的交集
5. 交集大小 → 参与度级别
```

```typescript
const collaborators = new Set(await getCollaborators(octokit, owner, repo));
collaborators.delete(pr.author.login); // 排除作者自己
const participants = new Set(pr.participants.nodes.map(i => i.login));
const collabParticipants = collaborators.intersection(participants);

if (collabParticipants.size === 0) return "No Maintainer Engagement";
if (collabParticipants.size === 1) return "Single Maintainer Engagement";
return "Multiple Maintainer Engagement";
```

> 💡 使用ES2024的 `Set.intersection()` 方法计算交集。参与者列表限制为first:100，超大型PR可能数据不完整。

## 5. CI Status（CI状态）

**文件**：`fields/cistatus.ts`
**类型**：SINGLE_SELECT
**选项**：Tests Passing / Tests Failing

### 判定逻辑

```typescript
if (pr.statusCheckRollup) {
    if (pr.statusCheckRollup.state === "SUCCESS") return "Tests Passing";
    if (pr.statusCheckRollup.state === "FAILURE") return "Tests Failing";
    console.log('found unhandled rollup state:', pr.statusCheckRollup.state);
    return null;
}
return null;
```

`statusCheckRollup` 是PR所有check run的聚合状态。只有明确的SUCCESS和FAILURE被映射：
- **PENDING/EXPECTED/ERROR**等状态 → null（字段清空）
- **无statusCheckRollup**（没有任何check run）→ null

遇到未处理状态时会打印日志，方便调试和扩展。

## 6. Merge Conflicts（合并冲突）

**文件**：`fields/mergeconflicts.ts`
**类型**：SINGLE_SELECT
**选项**：Merge Conflicts / No Merge Conflicts

### 判定逻辑

```typescript
switch(pr.mergeable) {
    case "CONFLICTING": return "Merge Conflicts";
    case "MERGEABLE":   return "No Merge Conflicts";
    case "UNKNOWN":     return null;
}
return null; // 防御性默认
```

GitHub GraphQL的 `mergeable` 字段有三个值：
- **CONFLICTING**：PR存在合并冲突
- **MERGEABLE**：可以无冲突合并
- **UNKNOWN**：GitHub尚未计算完成合并状态（常见于新提交刚push后）

UNKNOWN状态返回null而非猜测结果。代码通过switch穷举所有枚举值，并在末尾有防御性return null应对未来API变更。

## 7. Approval Status（审批状态）

**文件**：`fields/approvalstatus.ts`
**类型**：SINGLE_SELECT
**选项**：Changes Requested / Maintainer Approved

### 判定逻辑

```
1. 遍历 pr.reviews.nodes
2. 筛选条件：authorCanPushToRepository === true（可推送到仓库=维护者）
            && !isMinimized（未被隐藏/最小化）
3. 收集有效审查的state
4. 判断优先级：
   ├── 存在 CHANGES_REQUESTED → "Changes Requested"（优先）
   ├── 存在 APPROVED → "Maintainer Approved"
   └── 其他（无审查/仅评论）→ null
```

关键规则：
- **CHANGES_REQUESTED优先级最高**：只要有一个维护者请求修改，不管有多少批准，都标记为"Changes Requested"
- **作者自己的review不算**：通过authorCanPushToRepository排除非维护者，但作者本人如果也有push权限，自己的review会被计入——但在实际中作者不会review自己的PR
- **isMinimized过滤**：被标记为"过时"(outdated)或最小化的review不参与计算
- **reviews限制first:100**：超过100条review的PR可能数据不完整

## 未使用字段：Files Changed Type

**文件**：`fields/fileschangedtype.ts`（已实现但未注册）

该字段根据变更文件的扩展名判断主要变更类型：
- **Documentation**：.md, .rst
- **Python**：.py
- **Frontend**：.js, .jsx, .ts, .tsx, .css, .html, .scss

逻辑：按扩展名统计增删行数，取行数最多且超过"其他"类型总数的类型返回。此功能已完整实现但未在fieldconfig.ts中注册，属于待启用功能。

## 字段值与GitHub Project类型映射

| 字段 | TypeScript值类型 | GraphQL值类型 | Mutation中的值字段 |
|------|-----------------|--------------|-------------------|
| Author Kind | 字符串字面量 | singleSelectOptionId | 选项名→选项ID转换 |
| Opened At | Date | Date | date: $value |
| Total Lines Changed | number | Float | number: $value |
| Maintainer Engagement | 字符串字面量 | singleSelectOptionId | 选项名→选项ID转换 |
| CI Status | 字符串字面量/null | singleSelectOptionId/null | 更新或清空 |
| Merge Conflicts | 字符串字面量/null | singleSelectOptionId/null | 更新或清空 |
| Approval Status | 字符串字面量/null | singleSelectOptionId/null | 更新或清空 |

## 相关概念

- [字段插件体系](05-field-plugin-system.md)
- [Project管理类](04-project-class.md)
- [同步循环与增量更新](07-sync-loop.md)
