---
okf_version: "0.2"
type: "concept"
title: "Project管理类"
description: "Project类的完整API：静态获取、字段查找与创建、条目增删改、动态GraphQL Mutation构造与SingleSelectField类型"
tags: [project-class, projectv2, field-management, crud, mutation, single-select]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: project-source
    resource: /references/project-source.md
    title: "Project管理类源码"
  - id: graphql-source
    resource: /references/graphql-source.md
    title: "GraphQL查询源码"
---

# Project管理类

`Project` 类是GitHub Project V2的操作门面，封装了所有与项目板交互的GraphQL操作，包括字段管理和条目增删改。

## 类结构

```typescript
class Project {
    id: string;           // Project V2节点ID（全局唯一）
    fields: Field[];      // 项目字段列表（含单选字段的选项）
    octokit: Octokit & paginateGraphQLInterface;
    organization: string; // 所属组织名
    number: number;       // 项目编号（URL中可见）
}
```

### Field接口与SingleSelectField类

基础字段接口：
```typescript
interface Field {
    id: string;
    name: string;
}
```

单选选项类：
```typescript
class SingleSelectOption {
    constructor(public id: string, public name: string);
}
```

单选字段类（继承Field概念）：
```typescript
class SingleSelectField implements Field {
    id: string;
    name: string;
    options: SingleSelectOption[];

    constructor(id: string, name: string, options: SingleSelectOption[]);

    // memoized：按选项名查找选项对象（用于获取选项ID）
    findOption = memoize((name: string): SingleSelectOption => { ... });
}
```

> 💡 `findOption` 使用memoize缓存查找结果，避免每次设置单选字段值时都遍历options数组。

## 获取项目实例

```typescript
static async getProject(
    organization: string,
    number: number,
    octokit: Octokit & paginateGraphQLInterface
): Promise<Project>
```

静态工厂方法，执行以下步骤：
1. 调用 `project.gql` 查询，获取项目ID和字段定义
2. 遍历返回的字段节点：
   - 如果字段有 `options` 属性 → 创建 `SingleSelectField` 实例（包含选项映射）
   - 否则 → 创建普通 `Field` 对象 `{id, name}`
3. 返回 Project 实例

使用示例：
```typescript
const project = await Project.getProject("jupyterhub", 4, octokit);
```

## 字段管理

### findField：查找字段

```typescript
findField = memoize((name: string): Field => { ... });
```

按字段名在 `this.fields` 数组中查找字段，使用memoize缓存。找不到时抛出异常（代码注释标注"Learn how to error handle this properly?"，表明错误处理尚未完善）。

### verifyAndCreateFields：验证并创建缺失字段

```typescript
async verifyAndCreateFields(): Promise<void>
```

遍历 `REQUIRED_FIELDS` 注册表，对每个字段：
- 如果项目中已存在（按名称匹配）→ 跳过
- 如果不存在 → 调用 `createField()` 创建

这是机器人的幂等初始化步骤——首次运行自动创建所有必需字段，后续运行跳过。

### createField：创建字段

```typescript
async createField(fieldName: string, fieldSpec: FieldConfig): Promise<Field>
```

根据FieldConfig创建GitHub Project自定义字段：

**SINGLE_SELECT类型**：
```graphql
mutation ($projectId: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!,
          $singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]!) {
    createProjectV2Field(input: {
        projectId: $projectId, name: $name, dataType: $dataType,
        singleSelectOptions: $singleSelectOptions
    }) {
        projectV2Field {
            ... on ProjectV2SingleSelectField { id, name, options { id, name } }
        }
    }
}
```

**其他类型（TEXT/NUMBER/DATE）**：
```graphql
mutation ($projectId: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!) {
    createProjectV2Field(input: {
        projectId: $projectId, name: $name, dataType: $dataType
    }) {
        projectV2Field {
            ... on ProjectV2Field { id, name }
        }
    }
}
```

创建成功后：
1. 根据返回数据构造Field或SingleSelectField实例
2. 将新字段push到 `this.fields` 数组（更新本地缓存）
3. 打印创建日志

## 条目操作

### addContent：添加PR到项目板

```typescript
async addContent(contentId: string): Promise<string>
```

调用 `addProjectV2ItemById` mutation将PR（通过其节点ID）添加到项目板，返回新创建条目的ID。

### deleteItem：从项目板删除条目

```typescript
async deleteItem(itemId: string): Promise<string>
```

调用 `deleteProjectV2Item` mutation删除项目条目（用于清理已关闭/合并的PR条目），返回被删除条目的ID。

### getExistingItems：获取现有条目

```typescript
async getExistingItems(): Promise<any[]>
```

使用 `projectitems.gql` 分页查询项目中的所有条目，过滤掉 `content` 为null的条目（只保留PullRequest类型的条目）。返回的每个条目包含：
- `id`：项目条目ID
- `content.id` / `content.url`：关联的PR ID和URL
- `fieldValues.nodes`：当前字段值（四种类型的union）

### setItemValue：设置字段值

```typescript
async setItemValue(
    projectItemId: string,
    fieldName: string,
    value: Date | string | number | null
): Promise<any>
```

这是最复杂的方法，**动态构造GraphQL Mutation**。根据值类型决定mutation类型和参数：

| 值类型 | Mutation | GraphQL变量类型 | 值字段 |
|--------|----------|----------------|--------|
| `Date` | updateProjectV2ItemFieldValue | `$value: Date!` | `date: $value` |
| `string`（单选） | updateProjectV2ItemFieldValue | `$value: String!` | `singleSelectOptionId: $value`（自动将选项名转为ID） |
| `string`（文本） | updateProjectV2ItemFieldValue | `$value: String!` | `string: $value` |
| `number` | updateProjectV2ItemFieldValue | `$value: Float!` | `number: $value` |
| `null` | clearProjectV2ItemFieldValue | （无value变量） | 清空字段 |

动态拼接的Mutation模板：
```graphql
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID! <valueDef>) {
    <mutationName>(input: {
        projectId: $projectId, itemId: $itemId, fieldId: $fieldId
        <valueProperty>
    }) { projectV2Item { id } }
}
```

> ⚠️ 作者在代码中自嘲："I am creating a query via string interpolation, may i rot in hell"——字符串拼接构造GraphQL查询在安全性和类型安全上存在风险。但由于GitHub GraphQL API对不同字段类型使用不同的input type，无法通过统一参数化query覆盖所有情况，这是务实的妥协。

## 使用流程

在main函数中，Project类的典型使用顺序：

```typescript
// 1. 获取项目实例
const project = await Project.getProject(org, projectNum, octokit);

// 2. 确保字段存在
await project.verifyAndCreateFields();

// 3. 获取已有条目
const existingItems = await project.getExistingItems();

// 4. 删除过期条目
for (const item of staleItems) {
    await project.deleteItem(item.id);
}

// 5. 添加新PR
const itemId = await project.addContent(pr.id);

// 6. 设置字段值
await project.setItemValue(itemId, "CI Status", "Tests Passing");
await project.setItemValue(itemId, "Opened At", new Date());
await project.setItemValue(itemId, "Total Lines Changed", 42);
await project.setItemValue(itemId, "Approval Status", null); // 清空
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [GitHub App认证与Octokit配置](03-auth-and-octokit.md)
- [字段插件体系](05-field-plugin-system.md)
- [同步循环与增量更新](07-sync-loop.md)
