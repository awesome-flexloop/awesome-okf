---
type: example
title: 连接数据库
description: 详细讲解如何连接 MySQL、PostgreSQL、Dolt、Doltgres、SQLite 和 DoltLite
tags: [dolt-workbench, database-connection, tutorial]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: conn-provider
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/graphql-server/src/connections/connection.provider.ts
    title: ConnectionProvider 实现
  - id: data-store
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/graphql-server/src/dataStore/dataStore.service.ts
    title: DataStore 持久化服务
  - id: db-resolver
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/graphql-server/src/databases/database.resolver.ts
    title: DatabaseResolver
---

# 连接数据库

## 连接类型

dolt-workbench 支持 6 种数据库连接类型：

| 类型 | 标识 | 协议 | 说明 |
|---|---|---|---|
| MySQL | `mysql` | TCP/IP | 标准 MySQL 数据库 |
| PostgreSQL | `postgres` | TCP/IP | 标准 PostgreSQL 数据库 |
| Dolt | `mysql` (自动检测) | MySQL 协议 | Dolt 版本控制数据库 |
| Doltgres | `postgres` (自动检测) | PostgreSQL 协议 | Dolt 版本控制数据库 |
| SQLite | `sqlite` | 文件 | 标准 SQLite 数据库 |
| DoltLite | `sqlite` (自动检测) | SQLite 文件 | 无服务器版 Dolt |

## 连接流程

### 1. 添加连接

通过 GraphQL Mutation 添加连接：

```graphql
mutation AddConnection($input: AddDatabaseConnectionInput!) {
  addDatabaseConnection(input: $input) {
    connection {
      name
      type
      isDolt
      host
      port
    }
  }
}
```

变量：
```json
{
  "input": {
    "connectionUrl": "mysql://user:pass@localhost:3306/dbname",
    "name": "My Database",
    "type": "mysql",
    "port": 3306,
    "user": "user",
    "password": "pass",
    "dbName": "dbname",
    "useSSL": false
  }
}
```

### 2. 连接存储策略

```
DataStoreService (TypeORM, 服务端持久化)
         ↓ 不可用时降级
FileStoreService (JSON 文件, 本地持久化)
```

`dataStore.service.ts` 中的优先级逻辑：
```typescript
async addStoredConnection(connection: DatabaseConnection): Promise<void> {
  try {
    // 优先使用 TypeORM 持久化
    await this.dataStoreRepository.save(connection);
  } catch (e) {
    // 降级到文件存储
    await this.fileStoreService.addConnection(connection);
  }
}
```

### 3. 数据库类型自动检测

连接创建后，系统自动检测数据库类型：

```typescript
// 检测 Dolt/Doltgres
const doltVersion = await ds.query("SELECT dolt_version()");
const isDolt = doltVersion.length > 0;

// 检测 DoltLite
const engineInfo = await ds.query("SELECT doltlite_engine()");
const isDoltLite = engineInfo.length > 0;
```

## MySQL 连接

### 连接参数

```typescript
type MySQLConnection = {
  type: "mysql";
  host: string;       // 主机地址
  port: number;       // 端口（默认 3306）
  user: string;       // 用户名
  password: string;   // 密码
  database: string;   // 数据库名
  useSSL: boolean;    // 是否使用 SSL
};
```

### 示例连接字符串

```
mysql://root:password@localhost:3306/my_database
```

### Dolt 连接

Dolt 使用 MySQL 协议，连接方式相同：

```bash
# 启动 Dolt sql-server
dolt sql-server --listen-address=:3306

# 连接参数
Host: localhost
Port: 3306
User: root
Password: (空)
Database: my_dolt_database
```

连接后会显示 Dolt 专属功能（分支、提交、diff 等）。

## PostgreSQL 连接

### 连接参数

```typescript
type PostgresConnection = {
  type: "postgres";
  host: string;
  port: number;       // 端口（默认 5432）
  user: string;
  password: string;
  database: string;
  useSSL: boolean;
};
```

### 示例连接字符串

```
postgres://user:password@localhost:5432/my_database
```

### Doltgres 连接

Doltgres 使用 PostgreSQL 协议：

```bash
# 启动 Doltgres
doltgres server

# 连接参数（同 PostgreSQL）
Host: localhost
Port: 5432
User: postgres
Password: (空)
Database: my_doltgres_database
```

## SQLite 连接

### 连接参数

```typescript
type SQLiteConnection = {
  type: "sqlite";
  databaseFile: string;  // SQLite 数据库文件路径
};
```

### 示例

```
Database File: /path/to/your/database.sqlite
```

## DoltLite 连接

### 创建新数据库

```typescript
// IPC Handler: create-doltlite-database-file
// 返回值: { path: string, fileName: string }
```

### 连接已有数据库

```
Database File: /path/to/your/database.db
```

注意：DoltLite 数据库文件扩展名应为 `.db`。

## 连接管理

### 查看所有连接

```graphql
query {
  storedConnections {
    id
    name
    type
    host
    port
    isDolt
    isLocalDolt
  }
}
```

### 删除连接

```graphql
mutation {
  removeDatabaseConnection(id: "connection-id") {
    success
  }
}
```

### 连接信息模型

```typescript
// DatabaseConnection GraphQL 类型
type DatabaseConnection {
  connectionUrl: String
  name: String
  port: Int
  hideDoltFeatures: Boolean
  useSSL: Boolean
  type: DatabaseType!
  isDolt: Boolean
  isLocalDolt: Boolean
  host: String
  user: String
  password: String
}
```

## 文件上传（跨数据库支持）

不同数据库的文件上传方式不同：

### MySQL

```sql
-- 使用 LOAD DATA LOCAL INFILE
LOAD DATA LOCAL INFILE '/path/to/file.csv'
INTO TABLE my_table
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

### PostgreSQL / Doltgres

```sql
-- 使用 COPY FROM STDIN
COPY my_table (column1, column2) FROM STDIN WITH (FORMAT csv, HEADER true);
```

### SQLite / DoltLite

**不支持文件上传**，会抛出错误。

## 参考文档

- [快速开始](./00-getting-started.md)
- [使用 Agent Mode](./02-using-agent-mode.md)
