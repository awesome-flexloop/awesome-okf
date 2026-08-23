---
type: Reference
title: "字段实现源码"
description: "七个核心字段计算函数源码解析：AuthorKind/OpenedAt/TotalLinesChanged/MaintainerEngagement/CIStatus/MergeConflicts/ApprovalStatus，以及未使用的FilesChangedType"
tags: [fields, author-kind, ci-status, merge-conflicts, approval, maintainer-engagement, lines-changed]
sources:
  - id: authorkind-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/authorkind.ts"
    title: "src/fields/authorkind.ts"
  - id: openedat-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/openedat.ts"
    title: "src/fields/openedat.ts"
  - id: totallineschanged-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/totallineschanged.ts"
    title: "src/fields/totallineschanged.ts"
  - id: maintainerengagement-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/maintainerengagement.ts"
    title: "src/fields/maintainerengagement.ts"
  - id: cistatus-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/cistatus.ts"
    title: "src/fields/cistatus.ts"
  - id: mergeconflicts-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/mergeconflicts.ts"
    title: "src/fields/mergeconflicts.ts"
  - id: approvalstatus-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/approvalstatus.ts"
    title: "src/fields/approvalstatus.ts"
  - id: fileschangedtype-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fields/fileschangedtype.ts"
    title: "src/fields/fileschangedtype.ts"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 字段实现源码

每个字段实现文件导出一个 `getValue` 函数，签名为 `(octokit: PaginatedOctokit, pr: any) => Promise<value>`，返回对应类型的值。

## 1. Author Kind（作者类型）

**文件**：`authorkind.ts`
**返回类型**：`"Bot" | "Maintainer" | "First Time Contributor" | "Early Contributor" | "Seasoned Contributor"`

判定逻辑：
1. **Bot检测**：硬编码BOTS列表 `["dependabot", "pre-commit-ci", "jupyterhub-bot"]`，匹配则返回"Bot"
2. **Maintainer检测**：调用 `getCollaborators()` 获取仓库协作者列表（WRITE/MAINTAIN/ADMIN权限），作者在其中则返回"Maintainer"
3. **贡献者分级**：调用memoized的 `getMergedPRCount()` 查询该作者在组织内的已关闭PR数量：
   - 0个 → "First Time Contributor"
   - <10个 → "Early Contributor"
   - ≥10个 → "Seasoned Contributor"

`getMergedPRCount` 使用GraphQL search查询：`org:${organization} author:${username} is:pr state:closed`，注意FIXME注释标注"Only count successfully merged PRs?"——当前包含所有关闭PR（包括未合并的）。

## 2. Opened At（创建日期）

**文件**：`openedat.ts`
**返回类型**：`Date`

```typescript
const d = new Date(pr.createdAt);
d.setUTCHours(0, 0, 0, 0);
return d;
```

将PR的 `createdAt` 转为Date对象，清零时间部分（只保留日期），因为GitHub Project的DATE字段只存储日期。

## 3. Total Lines Changed（总行数变更）

**文件**：`totallineschanged.ts`
**返回类型**：`number`

```typescript
return pr.additions + pr.deletions;
```

简单地将新增行数和删除行数相加，不计算净变化。

## 4. Maintainer Engagement（维护者参与度）

**文件**：`maintainerengagement.ts`
**返回类型**：`"No Maintainer Engagement" | "Single Maintainer Engagement" | "Multiple Maintainer Engagement"`

判定逻辑：
1. 获取仓库协作者集合（WRITE/MAINTAIN/ADMIN权限）
2. 从协作者集合中移除PR作者本人（避免自己算参与）
3. 取PR参与者集合（`pr.participants.nodes`）
4. 计算两个集合的交集（`collaborators.intersection(participants)`）
5. 交集大小为0 → "No Maintainer Engagement"，为1 → "Single"，>1 → "Multiple"

## 5. CI Status（CI状态）

**文件**：`cistatus.ts`
**返回类型**：`"Tests Passing" | "Tests Failing" | null`

判定逻辑：
- `pr.statusCheckRollup.state === "SUCCESS"` → "Tests Passing"
- `pr.statusCheckRollup.state === "FAILURE"` → "Tests Failing"
- 其他状态（PENDING/EXPECTED/ERROR等）或无statusCheckRollup → `null`（字段清空）

遇到未处理状态时会打印日志输出状态值和PR URL，方便调试。

## 6. Merge Conflicts（合并冲突）

**文件**：`mergeconflicts.ts`
**返回类型**：`"Merge Conflicts" | "No Merge Conflicts" | null`

判定逻辑：
- `pr.mergeable === "CONFLICTING"` → "Merge Conflicts"
- `pr.mergeable === "MERGEABLE"` → "No Merge Conflicts"
- `pr.mergeable === "UNKNOWN"` → `null`（GitHub正在计算合并状态）

根据GitHub GraphQL文档，MergeableState枚举值穷尽检查，额外return null作为API变更的防御。

## 7. Approval Status（审批状态）

**文件**：`approvalstatus.ts`
**返回类型**：`"Changes Requested" | "Maintainer Approved" | null`

判定逻辑：
1. 遍历 `pr.reviews.nodes`，筛选条件：`authorCanPushToRepository === true`（可推送=维护者）且 `!isMinimized`（未被最小化/隐藏）
2. **CHANGES_REQUESTED优先**：只要存在任何一个"请求修改"的审查，返回"Changes Requested"
3. **APPROVED次之**：没有"请求修改"但有"批准"审查，返回"Maintainer Approved"
4. 无审查或无可判定审查 → `null`

## 8. Files Changed Type（文件变更类型）——未使用

**文件**：`fileschangedtype.ts`（已实现但未在fieldconfig.ts中注册）
**返回类型**：`string | null`

实现逻辑：
1. 维护扩展名→类型映射：Documentation(.md/.rst)、Python(.py)、Frontend(.js/.jsx/.ts/.tsx/.css/.html/.scss)
2. 遍历变更文件，按扩展名统计增删行数
3. 统计各类型行数，其他扩展名计入otherExtensionsCount
4. 按行数降序排列，若最大类型行数超过otherExtensionsCount则返回该类型名，否则返回null

该字段未被注册到REQUIRED_FIELDS中，属于已实现但未启用的功能。

## 相关信源

- [字段配置体系源码](field-config-source.md)
- [工具函数源码](utils-source.md)
