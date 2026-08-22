---
type: Reference
title: "工具函数源码"
description: "utils.ts源码解析：PaginatedOctokit类型、getGraphql文件加载、getCollaborators协作者查询与memoize缓存"
tags: [utils, memoize, graphql-loader, collaborators, pagination, cache-key]
sources:
  - id: utils-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/utils.ts"
    title: "src/utils.ts"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 工具函数源码

## 文件概览

`src/utils.ts` 提供两个memoized工具函数和一个类型别名。

## PaginatedOctokit类型

```typescript
export type PaginatedOctokit = Octokit & paginateGraphQLInterface;
```

将基础Octokit类型与paginateGraphQL插件接口交叉组合，表示启用了分页GraphQL插件的Octokit实例。此类型在整个项目中作为octokit参数的标准类型使用。

## getGraphql：GraphQL文件加载器

```typescript
export const getGraphql = memoize((name: string): string => {
    const path = join(import.meta.dirname, "graphql", name);
    return fs.readFileSync(path).toString();
});
```

功能：
- 从 `src/graphql/` 目录同步读取 `.gql` 文件内容
- 使用 `import.meta.dirname`（ES模块特性）获取当前模块目录
- 使用 `path/posix.join` 拼接路径（POSIX风格，跨平台兼容）
- 通过 `memoize` 缓存：同一文件只读一次磁盘，后续调用返回缓存字符串
- 是所有.gql查询文件的统一加载入口

> ⚠️ 使用同步读取（`readFileSync`），因为在模块初始化时调用，不需要异步。

## getCollaborators：协作者查询

```typescript
export const getCollaborators = memoize(async (octokit, owner, repo) => {
    const query = getGraphql("maintainers.gql");
    const resp2 = await octokit.graphql.paginate(query, { owner, repo });
    const allowedPermissions = ['WRITE', 'MAINTAIN', 'ADMIN'];
    return resp2.repository.collaborators.edges
        .filter(edge => allowedPermissions.includes(edge.permission))
        .map(edge => edge.node.login);
}, {
    cacheKey: args => JSON.stringify(args)
});
```

功能：
- 分页查询指定仓库的所有协作者
- 权限过滤：只保留WRITE、MAINTAIN、ADMIN三种权限的协作者（排除TRIAGE和READ）
- 返回协作者登录名数组
- 用于两个场景：Author Kind判定（是否为维护者）和Maintainer Engagement判定（维护者参与数）

### memoize cacheKey配置

```typescript
{ cacheKey: args => JSON.stringify(args) }
```

**关键细节**：`memoize` 库默认**只使用第一个参数作为缓存键**。对于多参数函数（octokit, owner, repo），必须显式配置 `cacheKey` 将所有参数序列化为缓存键，否则不同owner/repo的调用会命中同一个缓存条目，返回错误结果。

代码注释明确指出这一点："By default, all JS memoize functions only memoize on the first arg wtf?"

## memoize使用总览

项目中共有5处使用memoize：

| 位置 | 函数 | 缓存原因 | 自定义cacheKey |
|------|------|---------|---------------|
| utils.ts | getGraphql | 避免重复读文件 | 否（单参数） |
| utils.ts | getCollaborators | 避免重复API调用 | 是（三参数） |
| project.ts | findField | 避免重复遍历fields数组 | 否（单参数） |
| project.ts | SingleSelectField.findOption | 避免重复遍历options数组 | 否（单参数） |
| authorkind.ts | getMergedPRCount | 避免重复API调用 | 是（三参数） |

## 相关信源

- [GraphQL查询源码](graphql-source.md)
- [字段实现源码](field-implementations-source.md)
