---
type: Reference
title: "Project管理类源码"
description: "Project类、SingleSelectField/SingleSelectOption源码解析：项目获取、字段管理、条目增删改、动态GraphQL Mutation"
tags: [project, projectv2, graphql-mutation, field-management, crud, single-select]
sources:
  - id: project-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/project.ts"
    title: "src/project.ts"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# Project管理类源码

## 文件概览

`src/project.ts` 定义了GitHub Project V2的操作封装，包含三个核心类和一个接口：

| 类型 | 名称 | 职责 |
|------|------|------|
| interface | `Field` | 字段基础接口（id + name） |
| class | `SingleSelectOption` | 单选选项（id + name） |
| class | `SingleSelectField` | 单选字段（含options数组，findOption方法） |
| class | `Project` | 项目板操作门面类 |

## SingleSelectField

```typescript
export class SingleSelectField implements Field {
    id: string;
    name: string;
    options: SingleSelectOption[];

    constructor(id: string, name: string, options: SingleSelectOption[]);
    findOption = memoize((name: string): SingleSelectOption => { ... });
}
```

- `findOption(name)`：memoized方法，按名称查找选项，找不到时抛出异常
- 使用 `memoize` 缓存查找结果，避免重复遍历options数组

## Project类

### 属性

```typescript
class Project {
    id: string;           // Project V2节点ID
    fields: Field[];      // 项目字段列表
    octokit: Octokit & paginateGraphQLInterface;
    organization: string; // 组织名
    number: number;       // 项目编号
}
```

### 静态方法：getProject

```typescript
static getProject(organization, number, octokit): Promise<Project>
```

1. 使用 `project.gql` 查询获取项目字段
2. 遍历返回的字段节点：
   - 含 `options` 的字段 → 构造为 `SingleSelectField`（含选项映射）
   - 不含 `options` → 构造为普通 `Field` 对象 `{id, name}`
3. 返回 Project 实例

### 字段操作

**findField(name)**：memoized方法，按名称在 `this.fields` 中查找字段。

**verifyAndCreateFields()**：
1. 构建现有字段名集合 `existingFieldNames`
2. 遍历 `REQUIRED_FIELDS`，对不存在的字段调用 `createField()` 创建

**createField(fieldName, fieldSpec)**：
- SINGLE_SELECT类型：调用带 `singleSelectOptions` 参数的 `createProjectV2Field` mutation
- 其他类型：调用基础 `createProjectV2Field` mutation
- 创建成功后将字段添加到 `this.fields` 数组
- 使用 GraphQL fragment (`... on ProjectV2SingleSelectField` / `... on ProjectV2Field`) 获取返回的字段ID和名称

### 条目操作

**addContent(contentId)**：
```graphql
mutation ($projectId: ID!, $contentId: ID!) {
    addProjectV2ItemById(input: {projectId:$projectId, contentId:$contentId}) {
        item { id }
    }
}
```
返回新创建条目的ID。

**deleteItem(itemId)**：
```graphql
mutation ($projectId: ID!, $itemId: ID!) {
    deleteProjectV2Item(input: {projectId:$projectId, itemId:$itemId}) {
        deletedItemId
    }
}
```

**getExistingItems()**：
- 使用 `projectitems.gql` 分页查询项目条目
- 过滤掉 `content` 为null的条目（非PR条目）
- 返回包含 `{id, content: {id, url}, fieldValues}` 的条目列表

### setItemValue：动态Mutation构造

`setItemValue(itemId, fieldName, value)` 是最复杂的方法，根据值类型动态构造GraphQL mutation：

| 值类型 | Mutation名称 | 变量定义 | 值映射方式 |
|--------|-------------|---------|-----------|
| `Date` | updateProjectV2ItemFieldValue | `$value: Date!` | `date: $value` |
| `string`（单选字段） | updateProjectV2ItemFieldValue | `$value: String!` | `singleSelectOptionId: $value`（将选项名转为ID） |
| `string`（文本字段） | updateProjectV2ItemFieldValue | `$value: String!` | `string: $value` |
| `number` | updateProjectV2ItemFieldValue | `$value: Float!` | `number: $value` |
| `null` | clearProjectV2ItemFieldValue | （无value变量） | 清空字段值 |

> ⚠️ 代码注释自嘲："I am creating a query via string interpolation, may i rot in hell"——通过字符串拼接构造GraphQL查询在类型安全上存在风险，但此处因GitHub GraphQL API对不同字段类型使用不同的input type，无法用统一参数化查询覆盖。

## 相关信源

- [字段配置体系源码](field-config-source.md)
- [入口与CLI源码](main-source.md)
- [GraphQL查询源码](graphql-source.md)
