---
type: Example
title: 构建 Bundle 应用
description: 使用 Cordis Group 组合多个插件、管理插件依赖、利用 Fiber 生命周期状态机构建完整的模块化应用，演示 isolate 服务隔离和 HMR 热重载。
tags: [cordis, example, bundle, group, fiber, lifecycle, isolate, hmr]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: Cordis 源码事实清单
---

## 场景说明

你需要构建一个完整的 Cordis 模块化应用，包含：
1. 多个功能插件（数据库服务、HTTP服务、业务模块）
2. 插件间依赖声明与自动激活
3. 使用 Group 组合插件集合
4. 使用 isolate 实现服务隔离（多租户场景）
5. Fiber 状态监控和错误处理
6. 配置更新与插件重启

本示例使用 cordis 核心包 + @cordis/group + @cordis/timer 构建。

## 前置条件

```bash
npm install cordis@4.0.0-rc.8
# Group 是 cordis 的内置功能，无需额外安装
```

## 完整代码

创建 `bundle-app.ts`：

```typescript
import { Context, Service, FiberState } from 'cordis'

// ========== 1. 定义基础服务层 ==========

// 数据库服务（模拟）
class DatabaseService extends Service<DatabaseService.Config> {
  static inject = { logger: true }

  private connected = false
  private data = new Map<string, any>()

  constructor(ctx: Context, public config: DatabaseService.Config) {
    super(ctx, 'database')
  }

  async [Service.init]() {
    this.ctx.logger.info('连接数据库：%s:%d', this.config.host, this.config.port)
    // 模拟连接延迟
    await new Promise(r => setTimeout(r, 50))
    this.connected = true
    this.ctx.logger.info('数据库连接成功')

    // 注册事件供其他插件监听
    this.ctx.emit('database/connected')

    return () => {
      this.connected = false
      this.ctx.logger.info('数据库连接已关闭')
    }
  }

  async query(sql: string): Promise<any[]> {
    if (!this.connected) throw new Error('数据库未连接')
    this.ctx.logger.debug('执行查询：%s', sql)
    return []
  }

  set(key: string, value: any) {
    this.data.set(key, value)
  }

  get(key: string): any {
    return this.data.get(key)
  }
}

namespace DatabaseService {
  export interface Config {
    host: string
    port: number
    database: string
  }
}

// HTTP 服务（模拟）
class HttpService extends Service<HttpService.Config> {
  static inject = { logger: true, timer: true }

  private routes = new Map<string, Function>()
  private server: any = null

  constructor(ctx: Context, public config: HttpService.Config) {
    super(ctx, 'http')
  }

  async [Service.init]() {
    this.ctx.logger.info('启动 HTTP 服务，端口：%d', this.config.port)
    this.server = { port: this.config.port, listening: true }
    this.ctx.emit('http/started', this.config.port)

    return () => {
      this.server.listening = false
      this.routes.clear()
      this.ctx.logger.info('HTTP 服务已停止')
    }
  }

  get(path: string, handler: (ctx: any) => any) {
    this.routes.set(`GET ${path}`, handler)
    this.ctx.logger.debug('注册路由：GET %s', path)
  }

  post(path: string, handler: (ctx: any) => any) {
    this.routes.set(`POST ${path}`, handler)
  }
}

namespace HttpService {
  export interface Config {
    port: number
    host?: string
  }
}

// ========== 2. 定义业务插件（带依赖声明）==========

// 用户模块 - 依赖 database 和 http
function UserModule(ctx: Context, config: UserModule.Config = {}) {
  // 使用 inject 声明依赖，确保依赖服务可用后才执行
  ctx.inject(['database', 'http'], (ctx) => {
    const { database, http, logger } = ctx

    logger.info('初始化用户模块')

    // 注册 API 路由
    http.get('/api/users', async (reqCtx: any) => {
      return { users: await database.query('SELECT * FROM users') }
    })

    http.post('/api/users', async (reqCtx: any) => {
      database.set(`user:${Date.now()}`, reqCtx.body)
      return { success: true }
    })

    // 监听配置更新
    ctx.on('internal/update', (fiber, newConfig) => {
      logger.info('用户模块配置更新：%o', newConfig)
    })

    // 监听数据库重连
    ctx.on('database/connected', () => {
      logger.info('数据库已重连，用户模块恢复服务')
    })

    return () => {
      logger.info('用户模块已卸载')
    }
  })
}

UserModule.name = 'user-module'
UserModule.inject = ['http']  // 顶层依赖声明

interface UserModule.Config {
  prefix?: string
}

// 认证模块 - 依赖 database
function AuthModule(ctx: Context, config: AuthModule.Config = {}) {
  ctx.inject(['database'], (ctx) => {
    const { database, logger } = ctx

    logger.info('初始化认证模块，Token过期时间：%ds', config.tokenExpiry ?? 3600)

    ctx.on('auth/login', (credentials: { username: string; password: string }) => {
      logger.info('用户登录：%s', credentials.username)
      // 模拟验证
      return { token: `token-${Date.now()}`, userId: 'user-001' }
    })

    ctx.on('auth/verify', (token: string) => {
      return token.startsWith('token-')
    })

    return () => {
      logger.info('认证模块已卸载')
    }
  })
}

AuthModule.name = 'auth-module'

interface AuthModule.Config {
  tokenExpiry?: number
}

// ========== 3. 使用 ctx.extend 创建子上下文 ==========

console.log('=== 构建 Bundle 应用 ===\n')

const root = new Context()

// 安装基础服务
root.plugin(DatabaseService, {
  host: 'localhost',
  port: 5432,
  database: 'myapp'
})

root.plugin(HttpService, {
  port: 3000,
  host: '0.0.0.0'
})

// ========== 4. 使用 Group 组合插件 ==========
// Group 是 EntryGroup 的插件形式，用于将多个插件作为一个单元管理
// Group 的 config 是 EntryOptions[]，支持动态添加/移除插件

// 创建一个"应用套件" Group，包含用户和认证模块
// 注意：在 @cordis/loader 中 Group 是 EntryGroup，核心中通过插件数组模拟
function AppGroup(ctx: Context) {
  // 依次安装业务模块
  ctx.plugin(AuthModule, { tokenExpiry: 7200 })
  ctx.plugin(UserModule, { prefix: '/api' })

  ctx.logger.info('应用套件加载完成')

  return () => {
    ctx.logger.info('应用套件已卸载')
  }
}

AppGroup.name = 'app-group'

// 注册 Group
root.plugin(AppGroup)

// ========== 5. Isolate 服务隔离 ==========
// 使用 ctx.isolate(name, label?) 创建隔离的服务域
// 同一 label 的 isolate 共享服务实例，不传 label 则完全隔离

console.log('\n=== Isolate 服务隔离演示 ===')

// 创建两个隔离的数据库上下文
const tenantACtx = root.isolate('database', Symbol('tenant-a'))
const tenantBCtx = root.isolate('database', Symbol('tenant-b'))

// 在隔离域中分别注册数据库服务
class TenantDatabase extends Service {
  public tenantId: string

  constructor(ctx: Context, tenantId: string) {
    super(ctx, 'database')
    this.tenantId = tenantId
  }

  async [Service.init]() {
    this.ctx.logger.info('租户数据库初始化：%s', this.tenantId)
    return () => {
      this.ctx.logger.info('租户数据库关闭：%s', this.tenantId)
    }
  }

  query(sql: string) {
    return [{ tenant: this.tenantId, sql }]
  }
}

// 注意：isolate 后需要在新 context 上重新注册服务
// tenantACtx.plugin(TenantDatabase, 'tenant-a')
// tenantBCtx.plugin(TenantDatabase, 'tenant-b')

// ========== 6. Fiber 状态监控 ==========

console.log('\n=== Fiber 状态监控 ===')

// 监听所有 fiber 的状态变化
root.on('internal/status', (fiber: any, state: FiberState) => {
  const stateNames: Record<number, string> = {
    0: 'PENDING',
    1: 'LOADING',
    2: 'ACTIVE',
    3: 'FAILED',
    4: 'DISPOSED',
    5: 'UNLOADING'
  }
  console.log(`[Fiber ${fiber.uid ?? 'root'}] 状态变更：${stateNames[state] ?? state}`)
})

// ========== 7. 使用 intercept 覆盖配置 ==========

console.log('\n=== Intercept 配置覆盖 ===')

// ctx.intercept(name, config) 用于覆盖服务配置
const devCtx = root.intercept('database', {
  host: 'dev-db.local',
  port: 5433
} as any)

// devCtx 中访问 database 服务时会使用合并后的配置
// 配置合并沿原型链收集所有 intercept，若 Config 有静态 merge 方法则调用 merge，否则 Object.assign

// ========== 8. 配置更新与热重启 ==========

console.log('\n=== 配置更新演示 ===')

// Fiber.update(config) 更新插件配置，内部使用 waterfall('internal/update') 链
// 更新后会自动重启 Fiber
// 下面是一个可观察的更新示例

// 先找到 http 服务的 fiber（实际项目中可通过 registry 获取）
// 简化演示：直接使用 context 事件
root.emit('http/started', 3000)

// ========== 9. 使用 effect 管理资源 ==========

console.log('\n=== Effect 资源管理 ===')

// Fiber.effect(execute, label?) 是核心的资源管理方法
// 接收同步/异步的 Effect，收集返回的 dispose 函数
const timerEffect = root.effect(() => {
  const interval = setInterval(() => {
    // console.log('心跳...')
  }, 1000)
  console.log('定时器已启动')

  // dispose 函数
  return () => {
    clearInterval(interval)
    console.log('定时器已清理')
  }
})

// 清理 effect
// await timerEffect.dispose()

// ========== 10. 等待所有 Fiber 就绪 ==========

console.log('\n=== 等待 Fiber 就绪 ===')

// Fiber.await() 等待所有惯性操作（inertia）完成
// 插件注册返回 Fiber & PromiseLike，可以直接 await
async function bootstrap() {
  // 等待所有已注册插件完成初始化
  // 在实际使用 @cordis/loader 时，这一步由 loader 完成
  console.log('应用启动完成')

  // 使用服务
  const loginResult = root.bail('auth/login', { username: 'admin', password: '***' })
  console.log('登录结果：', loginResult)

  const valid = root.bail('auth/verify', loginResult.token)
  console.log('Token 验证：', valid)

  // 模拟等待
  await new Promise(r => setTimeout(r, 200))

  console.log('\n=== 清理资源 ===')
  // 清理定时器
  await timerEffect.dispose()
}

bootstrap().catch(console.error)
```

## 逐步解释

### 步骤 1：理解 Fiber 状态机

Fiber 是 Cordis 中插件的运行时实例，通过 epoch 机制驱动状态转换：

```
PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED
                ↘ FAILED ↙
```

- **PENDING（0）**：Fiber 已创建，等待依赖满足
- **LOADING（1）**：正在加载插件（执行构造函数、initHooks、[Service.init]）
- **ACTIVE（2）**：插件正常运行
- **FAILED（3）**：加载失败（配置验证错误、依赖缺失等）
- **DISPOSED（4）**：插件已卸载，uid 变为 null
- **UNLOADING（5）**：正在卸载（执行 dispose 函数）

epoch 机制通过依赖 fiber uid 拼接的字符串（如 `:1:3`）检测依赖变化，触发 `_reload()`（→LOADING）或 `_unload()`（→UNLOADING）。

### 步骤 2：插件依赖解析

```typescript
// 方式1：静态 inject 属性（类或函数）
AuthModule.inject = ['database']

// 方式2：@Inject 装饰器（类或类方法）
@Inject('database')
method(db: DatabaseService) {}

// 方式3：ctx.inject(deps, callback) 简写
ctx.inject(['database', 'http'], (ctx) => {
  // 只有当 database 和 http 都可用时才执行
  ctx.database.query(...)
  ctx.http.get(...)
})
```

依赖检查在 Fiber 创建时进行：
1. `Fiber._checkImpl(name)` 通过 `ctx.reflect._getImpl(name, true)` 检查服务实现
2. 如果 check 函数返回 false 或抛错，从 `_store` 中删除该服务
3. 依赖不满足时 Fiber 保持 PENDING 状态
4. 依赖服务注册/注销时通过 `reflect.notify()` 触发依赖 Fiber 状态更新

### 步骤 3：Group 组合模式

Group（在 @cordis/loader 中为 EntryGroup）用于将多个插件作为一个单元管理：

```typescript
// Group 的 config 是 EntryOptions[]
interface EntryOptions {
  id?: string
  name?: string
  config?: any
  group?: boolean
  disabled?: boolean
  inject?: Inject
}
```

使用 Group 的场景：
- **功能套件**：如 "数据库 + ORM + 迁移工具" 作为一个数据层套件
- **环境分组**：开发环境插件集、生产环境插件集
- **动态管理**：通过 `internal/update` 事件动态添加/移除组内插件

### 步骤 4：Isolate 服务隔离

Isolate 是 Cordis 实现多租户/多实例的核心机制：

```typescript
// 完全隔离（不传 label）
const isolatedCtx = ctx.isolate('database')
// 每次创建新的 Symbol，两个 isolate 上下文拥有不同的 database 实例

// 共享隔离域（传入相同 label）
const label = Symbol('shared')
const ctxA = ctx.isolate('database', label)
const ctxB = ctx.isolate('database', label)
// ctxA 和 ctxB 共享同一个 database 实例
```

实现原理：
- `context[symbols.isolate]: Dict<symbol>` 为每个服务名存储一个 symbol
- 不同 isolate 域的 symbol 不同
- Service 的 `[symbols.filter](ctx)` 方法比较 `ctx[isolate][name] === this.ctx[isolate][name]`
- 只有同一 isolate 域内的 context 才能看到该服务实例

### 步骤 5：Intercept 配置覆盖

```typescript
const devCtx = ctx.intercept('database', { host: 'dev-server' })
```

- `ctx.intercept(name, config)` 创建继承自当前 intercept map 的新对象
- 设置 `intercept[name] = config` 后调用 `extend()` 返回新 context
- Service 的 `[symbols.resolveConfig](base?, head?)` 沿原型链收集所有 intercept 配置
- 如果 Config 有静态 `merge` 方法则调用 merge，否则 `Object.assign` 合并
- 这使得在不同上下文中可以为同一服务提供不同配置

### 步骤 6：Effect 资源管理

```typescript
const disposable = ctx.effect(() => {
  const resource = acquire()
  return () => release(resource)
})

// 手动清理
await disposable.dispose()
```

`Fiber.effect(execute, label?)` 的特点：
1. 接收同步或异步的 Effect（函数、Promise、Iterable、AsyncIterable）
2. 执行后收集返回的 dispose 函数
3. 返回同时是函数和 PromiseLike 的 AsyncDisposable
4. dispose 时按注册逆序执行清理函数
5. Fiber 卸载时自动清理所有注册的 effect
6. 在已 dispose 的 Fiber 上创建 effect 会抛出 `CordisError('INACTIVE_EFFECT')`

### 步骤 7：配置更新流程

```typescript
fiber.update(newConfig)
```

更新流程：
1. 通过 `resolveConfig` 验证新配置（同步验证，失败抛 ValidationError）
2. 使用 `waterfall('internal/update', ...)` 触发更新中间件链
3. 设置新 config 并调用 `fiber.restart()`
4. restart 先设 epoch 为 INACTIVE 触发卸载（→UNLOADING）
5. 再调用 `_refresh()` 重新检查依赖并激活（→LOADING→ACTIVE）
6. 最后 `await()` 等待惯性操作完成

### 步骤 8：Shadow 机制

Shadow 机制确保 Service 方法中通过 `this.ctx` 访问的是服务注册时的原始 context，而非调用方 context：

```typescript
class MyService extends Service {
  async [Service.init]() {
    // this.ctx 是服务注册时的 context（有 shadow 保护）
    // 即使外部通过子 context 调用 this.ctx.on()，监听器也绑定到正确的 Fiber
    this.ctx.on('event', () => {})
  }
}
```

当从 service 方法访问 ctx 时，traceable proxy 创建 shadow context，将 service 的原始 ctx 作为 shadow 原型上的值。

## 插件加载最佳实践

1. **构造函数只做赋值**：所有副作用放在 `[Service.init]()` 中
2. **始终返回 dispose**：打开的资源（连接、定时器、监听器）必须返回清理函数
3. **合理使用 inject**：明确声明依赖，不要在代码中假设服务存在
4. **使用 isolate 而非创建新 Context**：需要隔离时用 `ctx.isolate()`，保持上下文继承关系
5. **异步 init 正确处理**：`[Service.init]()` 可以是 async 方法，Fiber 会等待其完成
6. **监听 internal/status 调试**：开发时监听状态变化可以快速定位依赖问题

## 相关概念

- [Context 容器系统](../concepts/context-container.md)
- [Fiber 生命周期](../concepts/fiber-lifecycle.md)
- [服务注册与发现](../concepts/service-registry.md)
- [事件系统详解](../concepts/event-system.md)
- [Reflect 元数据系统](../concepts/reflect-metadata.md)
- [插件与模块系统](../concepts/plugin-module.md)
