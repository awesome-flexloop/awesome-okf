---
type: Example
title: 使用事件总线
description: 掌握 Cordis EventsService 的五种派发模式（emit/parallel/serial/bail/waterfall），事件监听注册，以及中间件和事件冒泡机制。
tags: [cordis, example, events, event-bus, middleware, emit, waterfall]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: Cordis 源码事实清单
---

## 场景说明

你需要在 Cordis 应用中实现一套完整的事件通信机制，包括：
1. 使用 `emit` 进行同步事件通知
2. 使用 `parallel` 进行并行异步处理
3. 使用 `serial` 和 `bail` 实现短路求值
4. 使用 `waterfall` 构建中间件管道
5. 使用 `on`/`once` 注册监听器，理解 filter 过滤机制
6. 处理事件冒泡和全局事件

## 完整代码

创建 `event-bus-demo.ts`：

```typescript
import { Context } from 'cordis'

const ctx = new Context()

// ========== 1. emit：同步顺序执行 ==========
// emit 是最基础的事件派发方式，同步顺序执行所有监听器
// 任一监听器抛出异常时，立即中断后续监听器并向上抛出

console.log('=== 1. emit 同步事件 ===')

ctx.on('user/login', (userId: string) => {
  console.log(`[Logger] 用户 ${userId} 登录`)
})

ctx.on('user/login', (userId: string) => {
  console.log(`[Audit] 记录登录事件：${userId}`)
})

ctx.emit('user/login', 'user-001')
// 输出（同步顺序）：
// [Logger] 用户 user-001 登录
// [Audit] 记录登录事件：user-001

// 异常传播示例
ctx.on('user/login', () => {
  throw new Error('审计服务不可用')
})

try {
  ctx.emit('user/login', 'user-002')
} catch (err) {
  console.log('捕获异常：', (err as Error).message)
  // 输出：捕获异常：审计服务不可用
  // 注意：第三个监听器抛出异常后，后续监听器不再执行
}

// ========== 2. parallel：并行异步执行 ==========
// parallel 使用 Promise.allSettled 并行执行所有异步监听器
// 所有 rejection 被收集为 AggregateError 抛出（不会因单个失败中断）

console.log('\n=== 2. parallel 并行事件 ===')

ctx.on('notification/send', async (userId: string, message: string) => {
  await new Promise(r => setTimeout(r, 100))
  console.log(`[Email] 发送邮件给 ${userId}: ${message}`)
})

ctx.on('notification/send', async (userId: string, message: string) => {
  await new Promise(r => setTimeout(r, 50))
  console.log(`[SMS] 发送短信给 ${userId}: ${message}`)
})

ctx.on('notification/send', async () => {
  throw new Error('Push 服务暂时不可用')
})

try {
  await ctx.parallel('notification/send', 'user-003', '您有一条新消息')
} catch (err) {
  console.log('AggregateError 包含的异常数：', (err as AggregateError).errors.length)
  // 输出：AggregateError 包含的异常数：1
}
// 输出（并行执行，顺序不确定）：
// [SMS] 发送短信给 user-003: 您有一条新消息
// [Email] 发送邮件给 user-003: 您有一条新消息

// ========== 3. bail：同步短路求值 ==========
// bail 同步顺序执行监听器，遇到 bail 值（非 null/false/undefined）时立即返回
// null/false/undefined 不算 bail（包括 0、''、空对象都算 bail）

console.log('\n=== 3. bail 短路求值 ===')

ctx.on('auth/check', (token: string) => {
  if (token === 'valid-token') return true
  // 返回 undefined，继续下一个监听器
})

ctx.on('auth/check', (token: string) => {
  if (token === 'guest-token') return 'guest'
  return null  // null 不算 bail，继续
})

ctx.on('auth/check', () => {
  return false  // false 不算 bail，继续
})

ctx.on('auth/check', () => {
  return 'denied'  // 任何真值都会 bail
})

console.log(ctx.bail('auth/check', 'valid-token'))   // true
console.log(ctx.bail('auth/check', 'guest-token'))   // 'guest'
console.log(ctx.bail('auth/check', 'bad-token'))     // 'denied'

// ========== 4. serial：异步顺序执行 ==========
// serial 异步顺序执行监听器，遇到 bail 值提前返回
// 与 bail 的区别：支持异步监听器

console.log('\n=== 4. serial 异步顺序 ===')

ctx.on('pipeline/process', async (data: string) => {
  await new Promise(r => setTimeout(r, 30))
  console.log('阶段1：验证数据')
  // 不返回 bail 值，继续下一个
})

ctx.on('pipeline/process', async (data: string) => {
  await new Promise(r => setTimeout(r, 30))
  console.log('阶段2：转换数据')
  if (data.includes('error')) {
    return { error: '数据包含错误' }  // bail，停止流水线
  }
})

ctx.on('pipeline/process', async (data: string) => {
  await new Promise(r => setTimeout(r, 30))
  console.log('阶段3：保存数据')
  return { success: true, data }
})

const result1 = await ctx.serial('pipeline/process', '正常数据')
console.log('结果：', result1)
// 阶段1：验证数据
// 阶段2：转换数据
// 阶段3：保存数据
// 结果：{ success: true, data: '正常数据' }

const result2 = await ctx.serial('pipeline/process', '包含error的数据')
console.log('结果：', result2)
// 阶段1：验证数据
// 阶段2：转换数据
// 结果：{ error: '数据包含错误' }

// ========== 5. waterfall：中间件模式 ==========
// waterfall 是 Koa/Express 风格的中间件模式
// 最后一个参数是 next 函数，调用 next() 将控制权交给下一个中间件
// 不调用 next() 则中断链

console.log('\n=== 5. waterfall 中间件 ===')

// 中间件按注册顺序形成调用链
ctx.on('request/handle', (req: any, next: () => Promise<void>) => {
  console.log(`[中间件1] 开始处理请求：${req.path}`)
  req.startTime = Date.now()
  return next().then(() => {
    const duration = Date.now() - req.startTime
    console.log(`[中间件1] 请求处理完成，耗时 ${duration}ms`)
  })
})

ctx.on('request/handle', async (req: any, next: () => Promise<void>) => {
  console.log(`[中间件2] 认证检查：${req.path}`)
  if (!req.token) {
    req.status = 401
    return  // 不调用 next()，中断链
  }
  await next()
  console.log('[中间件2] 认证通过后处理')
})

ctx.on('request/handle', async (req: any, next: () => Promise<void>) => {
  console.log(`[中间件3] 业务处理：${req.path}`)
  req.status = 200
  req.response = { message: 'Hello World' }
  await next()
})

// 模拟请求
const request1: any = { path: '/api/hello', token: 'abc123' }
await ctx.waterfall('request/handle', request1)
console.log('响应状态：', request1.status, request1.response)
// [中间件1] 开始处理请求：/api/hello
// [中间件2] 认证检查：/api/hello
// [中间件3] 业务处理：/api/hello
// [中间件2] 认证通过后处理
// [中间件1] 请求处理完成，耗时 Xms
// 响应状态：200 { message: 'Hello World' }

const request2: any = { path: '/api/secret' }
await ctx.waterfall('request/handle', request2)
console.log('响应状态：', request2.status)
// [中间件1] 开始处理请求：/api/secret
// [中间件2] 认证检查：/api/secret
// [中间件1] 请求处理完成，耗时 Xms
// 响应状态：401

// ========== 6. once：一次性监听 ==========
// once 注册的监听器在首次执行后自动 dispose

console.log('\n=== 6. once 一次性监听 ===')

ctx.once('app/ready', () => {
  console.log('应用已就绪（只执行一次）')
})

ctx.emit('app/ready')  // 输出：应用已就绪（只执行一次）
ctx.emit('app/ready')  // 无输出（监听器已被自动移除）

// ========== 7. EventOptions：prepend 和 global ==========

console.log('\n=== 7. prepend 和 global 选项 ===')

// prepend: true 将监听器插入到钩子列表头部（先执行）
ctx.on('test/prepend', () => console.log('普通监听器'))
ctx.on('test/prepend', () => console.log('prepend 监听器'), { prepend: true })
ctx.emit('test/prepend')
// 输出：
// prepend 监听器
// 普通监听器

// global: true 注册全局事件，不受 context filter 过滤
// 常用于需要监听所有 context 事件的场景

// ========== 8. 内部事件 ==========

console.log('\n=== 8. 内置内部事件 ===')

// Cordis 内置了多个内部事件，可用于调试和扩展：
// - internal/plugin: fiber 创建/销毁
// - internal/status: fiber 状态变更
// - internal/service: 服务注册/注销
// - internal/update: 配置更新（waterfall 模式）
// - internal/listener: 监听器注册拦截
// - internal/dispatch: 事件派发通知

ctx.on('internal/service', (name: string, oldValue: any) => {
  if (oldValue === undefined) {
    console.log(`[内部事件] 服务注册：${name}`)
  } else {
    console.log(`[内部事件] 服务注销：${name}`)
  }
})

// 注册一个新服务来触发 internal/service
class TempService extends Service {
  constructor(ctx: Context) { super(ctx, 'temp') }
}
ctx.plugin(TempService)
// 输出：[内部事件] 服务注册：temp
```

## 逐步解释

### 五种派发模式对比

| 模式 | 执行方式 | 异常处理 | Bail 行为 | 适用场景 |
|------|---------|---------|----------|---------|
| `emit` | 同步顺序 | 立即抛出，中断后续 | 不支持 | 日志、通知、简单事件 |
| `parallel` | Promise.allSettled 并行 | 收集为 AggregateError | 不支持 | 广播通知、并行IO |
| `bail` | 同步顺序 | 立即抛出 | 返回非null/false/undefined时短路 | 权限检查、责任链 |
| `serial` | 异步顺序 | 立即抛出 | 返回bail值时短路 | 异步流水线 |
| `waterfall` | 中间件链 | 透传异常 | 不调用next()中断 | 请求处理、洋葱模型 |

### Bail 值判定规则

```typescript
// isBailed 函数判断逻辑
function isBailed(value) {
  return value !== null && value !== false && value !== undefined
}
```

这意味着：
- `null`、`false`、`undefined` → 继续执行下一个监听器
- `0`、`''`（空字符串）、`{}`（空对象）、`[]`（空数组）→ **会 bail**
- 任意 truthy 值 → bail

### waterfall 中间件的洋葱模型

waterfall 模式实现了经典的"洋葱模型"：

```
请求 → [中间件1 前] → [中间件2 前] → [中间件3 前] → 核心处理
      ← [中间件1 后] ← [中间件2 后] ← [中间件3 后] ←
```

关键规则：
1. 必须返回 `next()` 的 Promise 或在 async 函数中 `await next()`，否则后续中间件执行后无法回到当前中间件
2. 不调用 `next()` 会中断整个链条，后续中间件和上游响应处理都不会执行
3. `next()` 返回 Promise，可以在其后添加响应后处理逻辑

### EventOptions 详解

```typescript
interface EventOptions {
  prepend?: boolean  // 插入钩子列表头部（先执行）
  global?: boolean   // 全局事件，不受 filter 过滤
}
```

- **prepend**：当你需要在所有已有监听器之前执行时使用（如错误拦截器、性能监控）
- **global**：当使用 context filter 过滤事件时，标记 global 的监听器仍会收到事件

### Context Filter 机制

事件派发时，`_resolve()` 方法检查第一个参数是否为 object/function：
- 如果 thisArg 有 `Context.filter` 符号属性
- 则只回调 `hook.global === true` 或 `filter.call(thisArg, hook.ctx) === true` 的钩子
- Service 的事件天然使用这个机制：`ctx.emit(serviceInstance, event)` 时，Service 的 `[symbols.filter]` 方法确保只有同一 isolate 域的监听器收到事件

### 移除监听器

`ctx.on()` 返回一个 dispose 函数，调用它即可移除监听器：

```typescript
const dispose = ctx.on('event', handler)
// ...
dispose()  // 移除监听器
```

监听器也通过 Fiber effect 管理——当注册监听器的 Fiber 被 dispose 时，该 Fiber 上注册的所有监听器自动清理。

## 相关概念

- [事件系统详解](../concepts/event-system.md)
- [Context 容器系统](../concepts/context-container.md)
- [Fiber 生命周期](../concepts/fiber-lifecycle.md)
- [插件与模块系统](../concepts/plugin-module.md)
- [定时器调度器](../concepts/timer-scheduler.md)
