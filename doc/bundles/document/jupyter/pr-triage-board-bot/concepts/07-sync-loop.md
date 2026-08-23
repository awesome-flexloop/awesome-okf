---
okf_version: "0.2"
type: "concept"
title: "同步循环与增量更新"
description: "全量对账同步算法详解：数据获取、映射构建、过期清理、增量更新、值比较策略、Dry Run模式与运行日志"
tags: [sync-loop, reconciliation, incremental-update, diff, stale-cleanup, dry-run, idempotent]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: main-source
    resource: /references/main-source.md
    title: "入口与CLI源码"
  - id: project-source
    resource: /references/project-source.md
    title: "Project管理类源码"
---

# 同步循环与增量更新

同步循环是pr-triage-board-bot的核心业务逻辑，位于main函数中。它采用**全量对账**（Reconciliation）模式：每次运行获取GitHub上的完整状态，计算期望状态，然后只对差异部分执行更新。

## 同步流程概览

```
┌──────────────────────────────────────────────────┐
│ 1. 初始化                                        │
│    Project.getProject() → 获取项目字段定义       │
│    project.verifyAndCreateFields() → 确保字段存在 │
├──────────────────────────────────────────────────┤
│ 2. 双源数据获取（并行概念上）                     │
│    getOpenPRs() → 所有开放PR列表                 │
│    project.getExistingItems() → 看板上现有条目   │
├──────────────────────────────────────────────────┤
│ 3. 构建映射表                                    │
│    currentPRIds: Set<string> → 当前PR的ID集合    │
│    existingItemsByPRId: Map → 已有条目索引       │
│    itemsToDelete: Array → 过期条目列表           │
├──────────────────────────────────────────────────┤
│ 4. 清理过期条目                                  │
│    遍历 itemsToDelete → project.deleteItem()     │
├──────────────────────────────────────────────────┤
│ 5. 逐PR同步字段                                  │
│    for pr in openPRs (sorted by URL):            │
│      ├── addContent() (新PR)                     │
│      └── for field in REQUIRED_FIELDS:           │
│          ├── newValue = field.getValue()         │
│          ├── currentValue = existingValue        │
│          └── changed → setItemValue()            │
├──────────────────────────────────────────────────┤
│ 6. 输出汇总                                      │
│    "Updated N field values, skipped M unchanged" │
└──────────────────────────────────────────────────┘
```

## 步骤详解

### 步骤1：项目初始化

```typescript
const project = await Project.getProject(organization, projectNumber, octokit);
await project.verifyAndCreateFields();
```

首先获取项目元数据（字段ID、选项ID等），然后确保所有REQUIRED_FIELDS中定义的字段都存在于项目板上。缺失字段自动创建，已有字段跳过。

### 步骤2：双源数据获取

```typescript
const openPRs = await getOpenPRs(octokit, organization, repositories);
const existingItems = await project.getExistingItems();
```

- **openPRs**：通过GitHub Search API获取组织（或指定仓库）内所有开放PR，包含additions/deletions/reviews/CI/participants等字段计算所需的全部数据
- **existingItems**：通过Project API分页获取看板上所有条目，包含条目ID和当前字段值

两个数据源的获取是独立的，为后续差异比较做准备。

### 步骤3：构建映射表

```typescript
const currentPRIds = new Set(openPRs.map(pr => pr.id));
const itemsToDelete: {id: string, url: string}[] = [];
const existingItemsByPRId = new Map();

for (const item of existingItems) {
    if (currentPRIds.has(item.content.id)) {
        // PR仍开放：构建字段值映射
        const currentFieldValues = new Map();
        for (const fieldValue of (item.fieldValues?.nodes ?? []).filter(node => node.field?.name)) {
            const value = fieldValue.text
                ?? fieldValue.number
                ?? (fieldValue.date ? new Date(fieldValue.date) : undefined)
                ?? fieldValue.name;
            currentFieldValues.set(fieldValue.field.name, value);
        }
        existingItemsByPRId.set(item.content.id, {
            itemId: item.id,
            fieldValues: currentFieldValues
        });
    } else {
        // PR已关闭/不存在：标记删除
        itemsToDelete.push({ id: item.id, url: item.content.url });
    }
}
```

这个循环完成两件事：
1. 对于仍在openPRs中的PR，提取其当前字段值到Map中（用于后续增量比较）
2. 对于不在openPRs中的条目（PR已关闭/合并），添加到删除列表

字段值提取时需要根据GraphQL返回的类型结构解析：
- 文本字段 → `fieldValue.text`
- 数字字段 → `fieldValue.number`
- 日期字段 → `new Date(fieldValue.date)`
- 单选字段 → `fieldValue.name`（选项名称）

### 步骤4：清理过期条目

```typescript
itemsToDelete.sort((a, b) => a.url.localeCompare(b.url));
for (let i = 0; i < itemsToDelete.length; i++) {
    const item = itemsToDelete[i];
    console.log(`[${i + 1} / ${itemsToDelete.length}] Removing ${item.url}`);
    if (!dryRun) {
        await project.deleteItem(item.id);
    }
}
```

过期条目按URL字母序排序，确保日志输出顺序一致。逐条删除并打印进度。

### 步骤5：逐PR同步字段（核心循环）

```typescript
openPRs.sort((a: any, b: any) => a.url.localeCompare(b.url));
for (const pr of openPRs) {
    count += 1;

    // 获取或创建条目
    const existingItem = existingItemsByPRId.get(pr.id);
    const itemId = existingItem
        ? existingItem.itemId
        : (!dryRun && await project.addContent(pr.id));

    // 逐字段计算和更新
    for (const [fieldName, fieldConfig] of Object.entries(REQUIRED_FIELDS)) {
        const newValue = await fieldConfig.getValue(octokit, pr);
        const currentValue = existingItem?.fieldValues.get(fieldName);

        // 值比较
        const unchanged = (newValue instanceof Date && currentValue instanceof Date)
            ? currentValue.getTime() === newValue.getTime()
            : currentValue === (newValue ?? undefined);

        if (unchanged) {
            skippedCount++;
        } else {
            console.log(`[${count} / ${openPRs.length}] Setting ${fieldName} to ${newValue} for ${pr.url}`);
            if (!dryRun) {
                await project.setItemValue(itemId, fieldName, newValue);
            }
            updatedCount++;
        }
    }
}
```

关键点：
- PR按URL排序，保证日志输出顺序一致
- 新PR调用 `addContent()` 添加到项目板，已有PR直接使用现有itemId
- 每个字段独立计算和比较，只有值变化才调用API更新
- Dry run模式下不执行addContent和setItemValue

## 值比较策略

```typescript
if ((newValue instanceof Date && currentValue instanceof Date)
    ? currentValue.getTime() === newValue.getTime()
    : currentValue === (newValue ?? undefined)) {
    // 值未变化
}
```

比较逻辑分两种情况：
1. **Date对象**：不能用 `===`（两个不同Date对象引用不同），必须比较 `getTime()` 时间戳
2. **其他类型**：使用严格相等 `===`
3. **null vs undefined**：`newValue ?? undefined` 将null映射为undefined，确保"清空字段"和"字段未设置"视为等价

这个比较确保了只有真正变化的字段才触发API调用，避免不必要的Project活动记录和API消耗。

## Dry Run模式

通过 `--dry-run` 命令行参数启用：
- 打印所有将要执行的操作（添加/更新/删除）
- 不调用任何GraphQL mutation（addContent/setItemValue/deleteItem/createField均跳过）
- verifyAndCreateFields的字段创建也会跳过吗？——代码中dryRun检查在createField之前吗？注意：`verifyAndCreateFields` 中的createField调用**没有**检查dryRun，这意味着dry run模式下仍会创建缺失字段。这是一个潜在问题（dry run模式下仍可能产生副作用）。

实际上查看代码：`verifyAndCreateFields()` 调用在dryRun检查之后但createField内部没有dryRun判断。dryRun只在删除、添加、设置值时检查。

## 运行日志

运行过程输出结构化日志：

```
DRY RUN MODE - No changes will be made.        # dry run提示
Verifying project fields...                    # 字段验证开始
Field already exists: Author Kind              # 字段已存在
Missing field detected: CI Status              # 发现缺失字段
Created field: CI Status (SINGLE_SELECT)       # 创建字段
Field verification complete.                   # 字段验证完成
Fetching open PRs...                           # 获取PR
Fetching existing project items...             # 获取现有条目
Found 42 open PRs and 38 existing project items.
Syncing project fields...                      # 开始同步
[1 / 4] Removing https://github.com/org/repo/pull/123  # 删除过期
[1 / 42] Setting Author Kind to Maintainer for https://...  # 更新字段
[2 / 42] Setting CI Status to Tests Passing for https://...
...
Summary: Updated 15 field values, skipped 279 unchanged values  # 汇总
```

## 幂等性保证

同步循环的设计天然幂等：
- **确定性计算**：相同的PR数据产生相同的字段值
- **增量更新**：值未变化时跳过，重复运行不会重复写入
- **自动修复**：人工修改的字段在下次运行时被恢复为正确值
- **过期清理**：已关闭PR自动从看板移除

这意味着可以安全地每小时定时运行，不需要担心重复执行产生副作用。

## 性能考虑

1. **memoize缓存**：getGraphql、findField、findOption、getCollaborators、getMergedPRCount均被缓存，避免重复计算和API调用
2. **增量更新**：值比较减少API调用次数（通常大部分字段值不变）
3. **分页获取**：所有列表查询使用pagination自动获取全部数据
4. **串行执行**：当前实现是串行处理每个PR和每个字段（await在循环内），保证API调用顺序和日志可读性，但也限制了速度

## 相关概念

- [Project管理类](04-project-class.md)
- [字段插件体系](05-field-plugin-system.md)
- [七个核心字段详解](06-core-fields.md)
- [CLI与GitHub Action集成](08-cli-and-action.md)
