---
type: concept
title: DoltLite Revision 缓存机制
description: DoltLite 通过 DataSource 缓存实现 revision 级别的只读隔离
tags: [dolt-workbench, doltlite, revision, cache, sqlite]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: doltlite-src
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/graphql-server/src/queryFactory/doltlite/index.ts
    title: DoltLiteQueryFactory 完整实现
---

# DoltLite Revision 缓存机制

## 问题背景

DoltLite 是基于 SQLite 的无服务器版 Dolt，不支持原生的 `to...from` 语法进行 three-dot diff。此外，SQLite 的连接管理需要特殊处理——每次查询不同 revision 时，需要能够切换到该 revision 的快照。

## RevisionSource 类型

```typescript
type RevisionSource = {
  revision: string;       // revision 标识（branch name / tag / commit hash）
  ds: DataSource;         // 独立的 TypeORM DataSource
  activeRunners: number;  // 当前活跃查询数（引用计数）
  retired: boolean;       // 是否已退役（等待清理）
  destroyPromise?: Promise<void>;  // 异步销毁 promise
}
```

## 核心机制

### 1. withDetachedFallback()

当 refName 找不到对应的 branch/tag 时，自动解析为 commit hash 并创建 detached session：

```typescript
async withDetachedFallback(fn: (ds: DataSource) => Promise<T>, refName: string): Promise<T> {
  try {
    // 正常路径：直接使用 refName
    return await this.withDataSource(refName, fn);
  } catch (e) {
    // fallback：解析为 commit hash
    const commitHash = await this.resolveRefToCommit(refName);
    const ds = await this.acquireDataSource(`file@${commitHash}`);
    try {
      return await fn(ds);
    } finally {
      await this.releaseDataSource(`file@${commitHash}`);
    }
  }
}
```

### 2. acquireRevisionSource()

每个 revision 对应一个独立的 DataSource，通过 activeRunners 引用计数管理生命周期：

```typescript
async acquireRevisionSource(revision: string): Promise<RevisionSource> {
  // 检查缓存
  let source = this.revisionCache.get(revision);
  
  if (!source) {
    // 创建新的 DataSource
    source = {
      revision,
      ds: await this.createDataSourceForRevision(revision),
      activeRunners: 0,
      retired: false,
    };
    this.revisionCache.set(revision, source);
  }
  
  source.activeRunners++;
  return source;
}

async releaseRevisionSource(source: RevisionSource): Promise<void> {
  source.activeRunners--;
  
  if (source.activeRunners === 0 && source.retired) {
    // 清理 DataSource
    await this.destroyDataSource(source);
    this.revisionCache.delete(source.revision);
  }
}
```

### 3. file@revision 语法

DoltLite 使用 SQLite 的 URI 文件名语法来实现 revision 级别的只读访问：

```
file:/path/to/database.db?mode=ro&revision=<commit-hash>
```

这使得每个 revision 都有独立的 SQLite 连接，互不干扰。

## Three-dot Diff 手动实现

由于 DoltLite 不支持原生 `to...from` 语法，需要手动计算 merge-base：

```typescript
async resolveThreeDotRefs(fromRef: string, toRef: string): Promise<{
  mergeBase: string;
  fromRef: string;
  toRef: string;
}> {
  // 1. 获取两个 ref 的 commit hash
  const fromHash = await this.getCommitHash(fromRef);
  const toHash = await this.getCommitHash(toRef);
  
  // 2. 手动计算 merge-base
  const mergeBase = await this.getMergeBase(fromHash, toHash);
  
  return { mergeBase, fromRef, toRef };
}
```

## Merge 事务模式差异

| 方法 | 事务模式 | 说明 |
|---|---|---|
| `callMerge()` | autocommit | 无显式事务，冲突时直接抛错 |
| `callMergeWithResolveConflicts()` | BEGIN/ROLLBACK | 有事务支持，允许冲突解决后回滚 |

## callPushRemote 后额外 fetch

DoltLite 推送后不自动更新 tracking ref，需要额外调用 fetch：

```typescript
async callPushRemote(args: PushRemoteArgs): Promise<MutationResult> {
  const result = await super.callPushRemote(args);
  
  // DoltLite 推送后手动 fetch 以更新 tracking ref
  await this.callFetchRemote(args);
  
  return result;
}
```

## saveTests 手动填充 generatedMaps

better-sqlite3 不自动填充 generated maps，需要手动处理：

```typescript
async saveTests(args: SaveTestsArgs): Promise<Test[]> {
  // 手动构建 INSERT 语句
  const queries = args.tests.map(test => ({
    testName: test.testName,
    testGroup: test.testGroup,
    testQuery: test.testQuery,
    assertionType: test.assertionType,
    assertionComparator: test.assertionComparator,
    assertionValue: test.assertionValue,
  }));
  
  // better-sqlite3 不自动填充 ID，手动赋值
  const inserted = await this.queryMultiple(
    async query => {
      const results = [];
      for (const q of queries) {
        const result = await query(qh.insertTestQuery, [
          q.testName, q.testGroup, q.testQuery,
          q.assertionType, q.assertionComparator, q.assertionValue,
        ]);
        results.push({ ...q, _id: result.insertId });
      }
      return results;
    },
    args.databaseName,
    args.refName,
  );
  
  return inserted;
}
```

## 不支持的功能

以下功能在 DoltLite 中不可用：

| 功能 | 错误信息 |
|---|---|
| `getPullConflictsSummary()` | "Merge conflict previews are not supported for DoltLite" |
| `getPullRowConflicts()` | "Merge conflict previews are not supported for DoltLite" |

## 自定义 TypeORM Driver

`doltliteDriver.ts` 提供了 TypeORM better-sqlite3 driver 的完整适配器：

```typescript
// DoltLiteStatement: 包装 StatementSync
class DoltLiteStatement implements Statement {
  constructor(private stmt: StatementSync) {}
  
  all(...params: any[]): any[] { ... }
  get(...params: any[]): any { ... }
  run(...params: any[]): RunResult { ... }
  
  // reader 属性检测是否返回结果集
  get reader() { return this.stmt.reader; }
}

// DoltLiteConnection: 包装 DatabaseSync
class DoltLiteConnection implements Connection {
  constructor(private db: DatabaseSync) {}
  
  prepare(sql: string): Statement { ... }
  async execute(sql: string, params?: any[]): Promise<void> { ... }
  close(): void { ... }
}

// 工厂函数
function doltliteDriver(dbPath: string, options?: { readOnly?: boolean; fileMustExist?: boolean }) {
  return new DoltLiteConnection(new DatabaseSync(dbPath, options));
}
```

## 参考文档

- [QueryFactory 工厂模式](./02-query-factory-pattern.md)
- [架构总览](./01-architecture.md)
