---
type: Reference
title: "入口与CLI源码"
description: "main.ts入口文件源码解析：Octokit创建、CLI参数解析、getOpenPRs查询、主同步循环"
tags: [entry, cli, commander, octokit, main-loop, dry-run]
sources:
  - id: main-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/main.ts"
    title: "src/main.ts"
  - id: package-json
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/package.json"
    title: "package.json"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 入口与CLI源码

## 文件概览

`src/main.ts` 是 pr-triage-board-bot 的入口文件，包含：CLI参数解析、Octokit实例创建、开放PR查询、主同步循环。

## makeOctokit：认证Octokit工厂

```typescript
function makeOctokit(appId: number, installationId: number, keyPath: string) {
    const PaginatedOctokitConstructor = Octokit.plugin(paginateGraphQL, throttling)
    return new PaginatedOctokitConstructor({
        authStrategy: createAppAuth,
        auth: { appId, installationId, privateKey: fs.readFileSync(keyPath).toString() },
        throttle: { /* onRateLimit / onSecondaryRateLimit 回调 */ },
        log: { debug, info, warn, error }
    });
}
```

关键点：
- 使用 `Octokit.plugin()` 组合 `paginateGraphQL` 和 `throttling` 两个插件
- 认证方式为 GitHub App 认证（`createAppAuth`），需要 appId、installationId 和私钥文件
- 限流回调配置：主限流和次级限流均最多重试2次
- 日志直接绑定到 console 方法

## getOpenPRs：开放PR查询

```typescript
async function getOpenPRs(octokit: PaginatedOctokit, organization: string, repositories?: string[]) {
    const query = getGraphql("openprs.gql");
    const searchQuery = repositories?.length
        ? repositories.map(r => `repo:${organization}/${r}`).join(' ') + " is:pr state:open archived:false"
        : `org:${organization} is:pr state:open archived:false`;
    const resp = await octokit.graphql.paginate(query, {searchQuery});
    return resp.search.nodes;
}
```

关键点：
- 支持两种查询模式：全组织查询（`org:X`）和指定仓库查询（`repo:X/repo1 repo:X/repo2`）
- 使用 `octokit.graphql.paginate()` 自动分页获取所有结果
- 搜索条件固定为：PR类型、open状态、非归档仓库

## main：主同步函数

```typescript
async function main(organization, projectNumber, octokit, repositories?, dryRun = false)
```

执行流程：
1. **获取项目**：`Project.getProject()` 获取项目元数据和字段定义
2. **验证字段**：`project.verifyAndCreateFields()` 检查并自动创建缺失字段
3. **获取数据**：并行获取开放PR列表（`getOpenPRs`）和现有项目条目（`project.getExistingItems`）
4. **构建映射**：
   - `currentPRIds`：当前开放PR的ID集合（Set）
   - `existingItemsByPRId`：已有条目按PR ID索引的Map（包含itemId和fieldValues）
   - `itemsToDelete`：不在当前PR列表中的过期条目列表
5. **删除过期条目**：遍历 itemsToDelete，按URL排序，逐个删除（dry-run时只打印）
6. **同步字段值**：遍历开放PR（按URL排序），对每个PR：
   - 获取或创建项目条目（addContent）
   - 遍历 REQUIRED_FIELDS，计算新值（getValue），与现有值比较
   - Date类型用 `getTime()` 比较，其他类型用 `===` 比较
   - 值变化时调用 `setItemValue` 更新，否则跳过
7. **输出汇总**：打印更新数和跳过数

## CLI参数（commander）

| 参数 | 类型 | 说明 |
|------|------|------|
| `--dry-run` | boolean | 试运行模式，不实际修改项目板 |
| `--gh-app-id <number>` | number | GitHub App ID |
| `--gh-app-installation-id <number>` | number | GitHub App Installation ID |
| `--gh-app-pem-file <string>` | string | 私钥.pem文件路径 |
| `--repositories <repos>` | string | 逗号分隔的仓库名列表（可选） |
| `<organization>` | argument | GitHub组织名（必填） |
| `<projectNumber>` | argument | 项目板编号（必填） |

`--repositories` 参数值通过 `split(',').map(repo => repo.trim())` 解析为数组。

## 值比较逻辑

```typescript
if ((newValue instanceof Date && currentValue instanceof Date)
    ? currentValue.getTime() === newValue.getTime()
    : currentValue === (newValue ?? undefined)) {
    // 值未变化，跳过
} else {
    // 值变化，更新
}
```

- Date对象：比较时间戳（getTime()）
- 其他类型：严格相等（===）
- `null`（清空字段）对应 `undefined`（未设置），二者视为等价

## 相关信源

- [Project管理类源码](project-source.md)
- [字段配置体系源码](field-config-source.md)
- [工具函数源码](utils-source.md)
- [GraphQL查询源码](graphql-source.md)
