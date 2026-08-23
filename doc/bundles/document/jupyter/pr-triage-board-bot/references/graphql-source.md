---
type: Reference
title: "GraphQL查询源码"
description: "四个GraphQL查询文件解析：openprs.gql开放PR搜索、project.gql项目字段查询、projectitems.gql条目分页、maintainers.gql协作者查询"
tags: [graphql, query, pagination, search, fragments, projectv2]
sources:
  - id: openprs-gql
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/graphql/openprs.gql"
    title: "src/graphql/openprs.gql"
  - id: project-gql
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/graphql/project.gql"
    title: "src/graphql/project.gql"
  - id: projectitems-gql
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/graphql/projectitems.gql"
    title: "src/graphql/projectitems.gql"
  - id: maintainers-gql
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/graphql/maintainers.gql"
    title: "src/graphql/maintainers.gql"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# GraphQL查询源码

所有GraphQL查询文件存放在 `src/graphql/` 目录，通过 `getGraphql(name)` 函数读取并memoize缓存。

## openprs.gql：开放PR搜索查询

```graphql
query ($cursor: String, $searchQuery: String!) {
  search(type: ISSUE, first: 30, query: $searchQuery, after: $cursor) {
    nodes {
      ... on PullRequest {
        id, url, createdAt, lastEditedAt,
        deletions, additions,
        statusCheckRollup { state },
        mergeable,
        participants(first: 100) { nodes { login } },
        files(first: 100) { nodes { path, additions, deletions } },
        reviews(first: 100) {
          nodes { authorCanPushToRepository, isMinimized, state }
        },
        repository { id, name, owner { login } },
        author { login },
        title
      }
    }
    pageInfo { hasNextPage, endCursor }
  }
}
```

关键点：
- 使用GitHub Search API（`search(type: ISSUE)`）搜索PR
- 分页大小为30（first:30），通过cursor分页
- 使用inline fragment `... on PullRequest` 限定返回类型
- **statusCheckRollup** 获取CI状态汇总
- **participants**（first:100）获取PR参与者列表
- **files**（first:100）获取变更文件列表，包含路径和增删行数
- **reviews**（first:100）获取审查记录，包含是否可推送、是否被最小化、审查状态
- **注意**：files和reviews均限制first:100，超过100个文件/审查的PR可能数据不完整

## project.gql：项目字段查询

```graphql
query($organization: String!, $number: Int!) {
  organization(login: $organization) {
    projectV2(number: $number) {
      id,
      fields(first: 100) {
        nodes {
          ... on ProjectV2Field { id, name }
          ... on ProjectV2SingleSelectField { id, name, options { id, name } }
        }
      }
    }
  }
}
```

关键点：
- 查询指定组织的ProjectV2
- 使用fragment区分普通字段和单选字段：单选字段额外返回options列表
- 字段查询上限100个

## projectitems.gql：项目条目分页查询

```graphql
query($organization: String!, $number: Int!, $cursor: String) {
  organization(login: $organization) {
    projectV2(number: $number) {
      id,
      items(first: 100, after: $cursor) {
        nodes {
          id,
          content { ... on PullRequest { id, url } },
          fieldValues(first: 50) {
            nodes {
              ... on ProjectV2ItemFieldTextValue   { text,    field { ... on ProjectV2Field { name } } }
              ... on ProjectV2ItemFieldNumberValue { number,  field { ... on ProjectV2Field { name } } }
              ... on ProjectV2ItemFieldDateValue   { date,    field { ... on ProjectV2Field { name } } }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name, field { ... on ProjectV2SingleSelectField { name } }
              }
            }
          }
        }
        pageInfo { hasNextPage, endCursor }
      }
    }
  }
}
```

关键点：
- 分页获取项目中的所有条目（items），每页100条
- content字段只取PullRequest的id和url（其他类型content为null，会被过滤掉）
- fieldValues使用四个inline fragment覆盖四种值类型：Text/Number/Date/SingleSelect
- 每个fieldValue返回字段值和对应字段名称
- 字段值查询上限50个

## maintainers.gql：仓库协作者查询

```graphql
query ($cursor: String, $owner: String!, $repo: String!) {
  repository(name: $repo, owner: $owner) {
    collaborators(after: $cursor, first: 100) {
      edges {
        permission,
        node { login }
      }
      pageInfo { hasNextPage, endCursor }
    }
  }
}
```

关键点：
- 查询仓库的协作者列表（含权限级别）
- 返回edges结构（含permission和node.login），而非直接nodes
- 分页大小100
- 调用方过滤权限：只保留WRITE/MAINTAIN/ADMIN权限的协作者（排除TRIAGE和READ）

## 内联Mutation（project.ts中动态构造）

与查询文件分离，Mutation在project.ts中通过字符串模板动态构造：
- `addProjectV2ItemById`：添加PR到项目板
- `deleteProjectV2Item`：从项目板删除条目
- `updateProjectV2ItemFieldValue`：更新字段值（支持date/string/number/singleSelectOptionId）
- `clearProjectV2ItemFieldValue`：清空字段值
- `createProjectV2Field`：创建自定义字段（区分SINGLE_SELECT和其他类型）

## 相关信源

- [Project管理类源码](project-source.md)
- [工具函数源码](utils-source.md)
