---
type: concept
title: 三层架构设计
description: DoltWorkbench 的 Electron + NestJS GraphQL + Next.js 三层架构详解
tags: [dolt-workbench, architecture, electron, nestjs, nextjs]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: dolt-workbench-bg
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/web/main/background.ts
    title: Electron 主进程入口
  - id: dolt-workbench-app
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/graphql-server/src/app.module.ts
    title: NestJS AppModule
  - id: dolt-workbench-appx
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/web/renderer/pages/_app.tsx
    title: Next.js App 组件
---

# 三层架构设计

## 架构总览

DoltWorkbench 采用经典的 Electron 桌面应用架构，分为三层：

```
┌──────────────────────────────────────────────────────────────┐
│                    Layer 1: Electron Main                      │
│                     background.ts (~530 lines)                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ GraphQL Server  │  │ Dolt sql-server │  │   Claude     │ │
│  │ 进程管理         │  │ 进程管理          │  │   Agent      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  IPC Handlers (18) │ Menu System │ Session Management        │
├──────────────────────────────────────────────────────────────┤
│                 Layer 2: NestJS GraphQL Server                  │
│                      :9002                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  Connection      │  │  QueryFactory    │  │   22 Resolvers│ │
│  │  Provider        │  │  工厂模式         │  │             │ │
│  └──────────────────┘  └──────────────────┘  └─────────────┘ │
│  TypeORM DataStore │ FileStore (fallback)                     │
├──────────────────────────────────────────────────────────────┤
│                 Layer 3: Next.js Renderer                       │
│                      :3002                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  30+ Pages       │  │  Apollo Client   │  │  SWR Cache  │ │
│  │  路由系统         │  │  GraphQL 客户端   │  │  数据缓存    │ │
│  └──────────────────┘  └──────────────────┘  └─────────────┘ │
│  SqlEditor (Ace) │ DataTable │ Agent Panel                      │
└──────────────────────────────────────────────────────────────┘
```

## Layer 1: Electron 主进程

### 入口文件

`web/main/background.ts` 是 Electron 主进程入口，约 530 行。

### 关键环境变量

```typescript
NEXT_PUBLIC_FOR_ELECTRON = "true"  // 标识运行在 Electron 环境
NEXT_PUBLIC_FOR_MAC_NAV        // macOS 导航栏支持
NEXT_PUBLIC_USER_DATA_PATH      // 用户数据目录
```

### GraphQL Server 进程管理

```typescript
createGraphqlSeverProcess() {
  // 使用 utilityProcess.fork() 启动 graphql-server
  // 根据平台定位 dist/main.js
}

waitForGraphQLServer(url, timeout) {
  // 轮询 GraphQL server 健康检查
  // 超时 30s
}
```

### 18 个 IPC Handler

| Handler ID | 功能 |
|---|---|
| `start-dolt-server` | 启动 Dolt sql-server 进程 |
| `remove-dolt-connection` | 移除 Dolt 连接 |
| `dolt-login` | DoltHub 登录 |
| `cancel-dolt-login` | 取消 DoltHub 登录 |
| `clone-dolthub-db` | 克隆 DoltHub 数据库 |
| `select-sqlite-database-file` | 选择 SQLite 数据库文件 |
| `select-sqlite-database-directory` | 选择 SQLite 数据库目录 |
| `get-doltlite-database-destination` | 获取 DoltLite 数据库目标路径 |
| `create-doltlite-database-file` | 创建 DoltLite 数据库文件 |
| `discard-created-doltlite-database-file` | 丢弃已创建的 DoltLite 数据库 |
| `retain-created-doltlite-database-file` | 保留已创建的 DoltLite 数据库 |
| `set-commit-author` / `get-commit-author` | 提交作者设置 |
| `toggle-left-sidebar` | 切换侧边栏 |
| `api-config` / `get-headers` | API 配置 |
| `update-menu` | 更新菜单栏 |

### 窗口约束

- 最小尺寸：1200x780
- `before-quit` 清理：kill graphqlServerProcess、doltServerProcess、cleanupAgent

## Layer 2: NestJS GraphQL Server

### 模块注册

`app.module.ts` 使用 `@Module` 装饰器注册：

```typescript
@Module({
  imports: [
    GraphQLModule.forRoot<ApolloDriverConfig>({
      autoSchemaFile: process.env.NEXT_PUBLIC_FOR_ELECTRON === "true"
        ? process.env.SCHEMA_PATH
        : "schema.gql",
      context: ctx => ctx,
      driver: ApolloDriver,
    }),
    FileStoreModule,
    TerminusModule,
    ConfigModule.forRoot({ isGlobal: true }),
    DataStoreModule,
  ],
  providers: [ConnectionProvider, ...resolvers],
})
export class AppModule {}
```

### 连接持久化策略

```
DataStoreService (TypeORM)
       ↓ 降级
FileStoreService (JSON 文件)
```

### HTTP 配置

- 端口：9002
- CORS：允许 credentials 和 wildcard origin
- 文件上传：`graphqlUploadExpress` (maxFileSize=400MB, maxFiles=1)
- Cookie：`cookieParser()`

## Layer 3: Next.js Renderer

### App 组件

`_app.tsx` 定义了应用的根组件结构：

```tsx
<SWRConfig value={{ fetcher }}>
  <ServerConfigProvider>
    <ThemeProvider themeRGBOverrides={workbenchTailwindColorTheme}>
      <AgentProvider>
        <Inner pageProps={pageProps} Component={Component} />
        <GlobalAgentPanel />
      </AgentProvider>
    </ThemeProvider>
  </ServerConfigProvider>
</SWRConfig>
```

### 关键上下文

| Context | 功能 |
|---|---|
| `SqlEditorContext` | SQL 编辑器状态（editorString, executeQuery, error, loading） |
| `DataTableContext` | 数据表格状态（rows, columns, foreignKeys, error） |
| `AgentContext` | Claude AI Agent 状态管理 |
| `ServerConfigContext` | 服务端配置（graphqlApiUrl） |

### Apollo 客户端配置

```typescript
// 默认 GraphQL URL
const DEFAULT_GRAPHQL_URL = "http://localhost:9002/graphql";

// Apollo Client 配置
export const ApolloProvider = withApollo(({ graphqlApiUrl }, params) => {
  return new ApolloClient({
    link: ApolloLink.from([uploadLink, errorLink, authLink, new HttpLink({ uri: graphqlApiUrl })]),
    cache: new InMemoryCache(),
  });
});
```

## 数据流

```
用户操作 → Next.js Page → GraphQL Query/Mutation
                              ↓
                         Apollo Client
                              ↓
                    http://localhost:9002/graphql
                              ↓
                         NestJS Server
                              ↓
                    ConnectionProvider
                              ↓
                         QueryFactory
                              ↓
                    DataSource (TypeORM)
                              ↓
                    数据库连接 (MySQL/PG/Dolt/etc.)
```

## 参考文档

- [QueryFactory 工厂模式](./02-query-factory-pattern.md)
- [DoltLite Revision 缓存](./03-dolt-lite-revision-cache.md)
- [Agent Mode 实现](./04-agent-mode.md)
