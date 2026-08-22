---
type: Concept
title: "定时器与调度"
description: "Cordis TimerService 定时器服务：setTimeout/setInterval 双模式（回调/Promise/AsyncIterable）、throttle 节流、debounce 防抖、基于 effect 的自动清理与 Fiber 生命周期绑定"
tags: [cordis, timer, scheduler, timeout, interval, throttle, debounce, async-iterable, effect]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-23T00:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:30:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: cordis-source
    resource: /references/cordis-sources.md
---

# 定时器与调度

TimerService 是 Cordis 的定时器调度服务（`@cordisjs/plugin-timer`），提供了比原生 `setTimeout/setInterval` 更强大的定时能力。它基于 Fiber 的 effect 机制，所有定时器自动绑定到创建时的 Fiber 生命周期——Fiber 销毁时定时器自动清理，无需手动 `clearTimeout/clearInterval`。同时支持 Promise 模式、AsyncIterable 模式、节流（throttle）和防抖（debounce）等高级调度功能。

## 设计原理

原生定时器 API（`setTimeout`/`setInterval`）存在以下问题：

1. **生命周期管理困难**：插件卸载时必须手动清理定时器，否则导致内存泄漏和"僵尸回调"
2. **缺乏组合性**：无法用 `for await...of` 消费定时事件，无法与 Promise/async-await 无缝组合
3. **无节流/防抖**：需要引入额外工具库（如 lodash）实现 throttle/debounce
4. **上下文丢失**：回调执行时 this/context 已改变，难以追踪来源

TimerService 通过 effect 机制解决了问题 1，通过重载支持三种调用模式解决了问题 2，内置了 throttle/debounce 解决了问题 3，并通过 mixin 机制将方法注入到 Context 上。

## TimerService 类定义

[timer/index.ts:L11-L140](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts#L11-L140)

```typescript
export class TimerService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'timer')
    ctx.mixin('timer', ['timeout', 'interval', 'throttle', 'debounce', 'setTimeout', 'setInterval'])
  }

  setTimeout(callback: () => void, delay: number): () => void
  setTimeout(delay: number): Promise<void>
  setTimeout(...args: any[]): any { return this.timeout(...args) }

  setInterval(callback: () => void, delay: number): () => void
  setInterval(delay: number): AsyncIterableIterator<void>
  setInterval(...args: any[]): any { return this.interval(...args) }

  timeout(callback: () => void, delay: number): () => void
  timeout(delay: number): Promise<void>
  timeout(...args: any[]): any { ... }

  interval(callback: () => void, delay: number): () => void
  interval<R = any>(delay: number): AsyncIterableIterator<void, R, void>
  interval(...args: any[]): any { ... }

  throttle<F extends (...args: any[]) => void>(callback: F, delay: number, noTrailing?: boolean): WithDispose<F>
  debounce<F extends (...args: any[]) => void>(callback: F, delay: number): WithDispose<F>
}
```

TimerService 继承 Service，通过 `ctx.mixin()` 将 6 个方法注入到 Context 上，可以直接通过 `ctx.timeout()`、`ctx.interval()` 等调用。

通过 module augmentation 扩展 Context 类型：

```typescript
declare module 'cordis' {
  interface Context extends Pick<TimerService, 'interval' | 'timeout' | 'throttle' | 'debounce' | 'setTimeout' | 'setInterval'> {
    timer: TimerService
  }
}
```

## timeout — 延时执行

[timer/index.ts:L27-L52](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts#L27-L52)

`timeout()` 有两种调用模式，通过参数类型自动推导：

### 模式一：回调模式

```typescript
timeout(callback: () => void, delay: number): () => void
```

传入回调函数和延迟时间，返回一个 dispose 函数用于取消定时器：

```typescript
// 回调模式
const dispose = ctx.timeout(() => {
  console.log('1 秒后执行')
}, 1000)

// 需要时可以手动取消
dispose()
```

实现：

```typescript
if (callback) {
  const dispose = this.ctx.effect(() => {
    const timer = setTimeout(() => {
      dispose()        // 执行后自动从 effect 中移除（自动清理）
      callback()
    }, delay)
    return () => clearTimeout(timer)
  }, 'ctx.timeout()')
  return dispose
}
```

关键点：
- 通过 `ctx.effect()` 注册，Fiber 销毁时自动 `clearTimeout`
- 回调执行后自动调用 `dispose()` 清理 effect（避免内存泄漏）
- 返回的 dispose 函数可手动取消

### 模式二：Promise 模式

```typescript
timeout(delay: number): Promise<void>
```

只传延迟时间（不传回调），返回一个 Promise，延迟结束后 resolve，Context 销毁时 reject：

```typescript
// Promise 模式
try {
  await ctx.timeout(5000)  // 等待 5 秒
  console.log('5 秒到了')
} catch (e) {
  // Context 被销毁时 Promise reject
  console.log('Context 已销毁')
}
```

实现：

```typescript
else {
  const { promise, resolve, reject } = Promise.withResolvers<void>()
  const dispose = this.ctx.effect(() => {
    const timer = setTimeout(resolve, delay)
    return () => {
      clearTimeout(timer)
      reject(new Error('Context has been disposed'))
    }
  }, 'ctx.timeout()')
  return promise.finally(dispose)
}
```

关键点：
- 使用 `Promise.withResolvers()` 创建可控 Promise
- Fiber 销毁时 reject 错误 "Context has been disposed"
- `promise.finally(dispose)` 确保 Promise settle 后自动清理

## interval — 定时执行

[timer/index.ts:L54-L101](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts#L54-L101)

`interval()` 同样支持两种模式：

### 模式一：回调模式

```typescript
interval(callback: () => void, delay: number): () => void
```

```typescript
// 回调模式：每秒执行一次
const stop = ctx.interval(() => {
  console.log('tick')
}, 1000)

// 停止
stop()
```

实现：

```typescript
if (callback) {
  return this.ctx.effect(() => {
    const timer = setInterval(callback, delay)
    return () => clearInterval(timer)
  }, 'ctx.interval()')
}
```

与 timeout 回调模式不同，interval 的回调不会自动 dispose——它会一直执行直到 Fiber 销毁或手动调用 dispose。

### 模式二：AsyncIterable 模式

```typescript
interval<R = any>(delay: number): AsyncIterableIterator<void, R, void>
```

不传回调时返回一个 `AsyncIterableIterator`，可以用 `for await...of` 消费：

```typescript
// AsyncIterable 模式
const iter = ctx.interval(1000)
for await (const _ of iter) {
  console.log('tick')
  if (shouldStop()) break  // break 时自动清理定时器
}
```

实现：

```typescript
else {
  let done: { kind: 'return'; value: any } | { kind: 'throw'; reason: any } | undefined
  let nextTask: PromiseWithResolvers<IteratorResult<void>> | undefined
  const dispose = this.ctx.effect(() => {
    const timer = setInterval(() => {
      nextTask?.resolve({ done: false, value: undefined })
    }, delay)
    return () => {
      clearInterval(timer)
      if (done) return
      done = { kind: 'throw', reason: new Error('Context has been disposed') }
      nextTask?.reject(done.reason)
    }
  }, 'ctx.interval()')
  return {
    next: () => {
      if (!done) return (nextTask = Promise.withResolvers()).promise
      if (done.kind === 'return') return Promise.resolve({ done: true, value: done.value })
      return Promise.reject(done.reason)
    },
    return: (value) => {
      if (!done) done = { kind: 'return', value }
      nextTask?.resolve({ done: true, value })
      dispose()  // 迭代器 return 时自动清理
      return Promise.resolve({ done: true, value })
    },
    throw: (reason) => {
      if (!done) done = { kind: 'throw', reason }
      nextTask?.reject(reason)
      dispose()  // 迭代器 throw 时自动清理
      return Promise.resolve({ done: true, value: undefined })
    },
    [Symbol.asyncIterator]() { return this },
  } satisfies AsyncIterableIterator<void>
}
```

AsyncIterable 模式的关键设计：
- 实现了完整的 `AsyncIterableIterator` 接口（next/return/throw/Symbol.asyncIterator）
- 使用 `nextTask` PromiseWithResolvers 实现按需等待
- `for await...of` 循环中 `break` 触发 `return()` 自动清理
- Fiber 销毁时 reject 错误终止迭代
- 支持 `iter.return(value)` 提前结束并返回值

## throttle — 节流包装

[timer/index.ts:L117-L132](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts#L117-L132)

```typescript
throttle<F extends (...args: any[]) => void>(callback: F, delay: number, noTrailing?: boolean): WithDispose<F>
```

throttle 创建一个节流包装函数，确保在 delay 时间内最多执行一次回调：

```typescript
// 节流：滚动事件中每 100ms 最多执行一次
const onScroll = ctx.throttle((event) => {
  console.log('scroll position:', event.scrollY)
}, 100)

window.addEventListener('scroll', onScroll)

// noTrailing = true：禁用尾部执行
const onResize = ctx.throttle(doSomething, 200, true)

// 手动停止节流
onScroll.dispose()
```

实现：

```typescript
throttle<F extends (...args: any[]) => void>(callback: F, delay: number, noTrailing?: boolean): WithDispose<F> {
  let lastCall = -Infinity
  const execute = (...args: any[]) => {
    lastCall = Date.now()
    callback(...args)
  }
  return this._schedule('ctx.throttle()', (args, isDisposed) => {
    const now = Date.now()
    const remaining = delay - now + lastCall
    if (remaining <= 0) {
      execute(...args)
    } else if (!isDisposed) {
      return setTimeout(execute, remaining, ...args)  // trailing call
    }
  }, noTrailing)
}
```

节流逻辑：
1. 记录上次执行时间 `lastCall`
2. 调用时计算剩余时间 `remaining = delay - (now - lastCall)`
3. 如果剩余时间 ≤ 0，立即执行
4. 否则设置 trailing 定时器（在剩余时间后执行最后一次调用）
5. `noTrailing=true` 时禁用 trailing 调用

## debounce — 防抖包装

[timer/index.ts:L134-L139](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts#L134-L139)

```typescript
debounce<F extends (...args: any[]) => void>(callback: F, delay: number): WithDispose<F>
```

debounce 创建防抖包装函数，延迟 delay 毫秒后执行，期间如果再次调用则重置计时：

```typescript
// 防抖：搜索输入停止 300ms 后才发起请求
const search = ctx.debounce((query: string) => {
  fetchResults(query)
}, 300)

input.addEventListener('input', (e) => search(e.target.value))

// 手动取消防抖
search.dispose()
```

实现：

```typescript
debounce<F extends (...args: any[]) => void>(callback: F, delay: number): WithDispose<F> {
  return this._schedule('ctx.debounce()', (args, isDisposed) => {
    if (isDisposed) return
    return setTimeout(callback, delay, ...args)
  })
}
```

防抖逻辑：每次调用时清除之前的定时器，重新设置新的定时器。只有最后一次调用后等待 delay 毫秒无新调用时才执行。

## _schedule — 通用调度器

[timer/index.ts:L103-L115](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts#L103-L115)

throttle 和 debounce 都基于内部的 `_schedule` 方法实现：

```typescript
private _schedule(label: string, trigger: (args: any[], isDisposed: boolean) => any, isDisposed = false) {
  let timer: number | NodeJS.Timeout | undefined
  const dispose = this.ctx.effect(() => () => {
    isDisposed = true
    clearTimeout(timer)
  }, label)
  const wrapper: any = (...args: any[]) => {
    clearTimeout(timer)              // 每次调用先清除之前的定时器
    timer = trigger(args, isDisposed) // trigger 返回新定时器（或 undefined）
  }
  wrapper.dispose = dispose
  return wrapper
}
```

_schedule 提供了统一的调度模式：
1. 通过 `ctx.effect()` 注册清理逻辑（Fiber 销毁时标记 isDisposed 并清除定时器）
2. 返回的 wrapper 函数每次调用先 `clearTimeout(timer)` 再调用 trigger
3. wrapper 上附加 dispose 方法，支持手动清理
4. trigger 函数根据逻辑返回新的 setTimeout 句柄或 undefined

## 生命周期绑定

所有 TimerService 方法都通过 `ctx.effect()` 注册，这意味着：

```mermaid
sequenceDiagram
    participant Plugin as 插件代码
    participant Fiber as Fiber
    participant Timer as TimerService
    participant Node as Node.js timers

    Plugin->>Timer: ctx.setInterval(cb, 1000)
    Timer->>Fiber: ctx.effect(() => { timer = setInterval(cb); return () => clearInterval(timer) })
    Fiber->>Fiber: _disposables.push(clearInterval)
    Fiber->>Node: setInterval(cb, 1000)

    Note over Node: 每秒触发回调

    Plugin->>Fiber: fiber.dispose() / 配置更新
    Fiber->>Fiber: _unload()
    Fiber->>Node: clearInterval(timer)  (自动清理!)
    Note over Plugin: 无需手动清理定时器
```

### 自动清理场景

| 场景 | 行为 |
|------|------|
| Fiber 正常 dispose | 所有定时器 clearTimeout/clearInterval |
| Fiber 重启（配置更新） | 旧定时器清理，新定时器在 _reload 后创建 |
| Fiber 加载失败 | effect 执行时的异常触发 dispose() 清理 |
| AsyncIterable break/return | iterator.return() 调用 dispose() |
| Promise 模式 resolve/reject | finally(dispose) 清理 |
| timeout 回调执行后 | 自动调用 dispose() |

### 废弃别名

`ctx.setTimeout()` 和 `ctx.setInterval()` 是 `ctx.timeout()` 和 `ctx.interval()` 的别名，标记为 `@deprecated`，建议使用新名称。

## 使用模式

### 轮询模式

```typescript
// 使用 AsyncIterable 实现轮询
ctx.inject(['database'], async (ctx) => {
  for await (const _ of ctx.interval(5000)) {
    const pending = await ctx.database.query('SELECT * FROM tasks WHERE status = ?', ['pending'])
    for (const task of pending) {
      await processTask(task)
    }
  }
})
```

### 超时控制

```typescript
// Promise.race 实现超时
async function fetchWithTimeout(url: string, timeout = 5000) {
  return Promise.race([
    fetch(url),
    ctx.timeout(timeout).then(() => { throw new Error('Request timeout') })
  ])
}
```

### 搜索防抖

```typescript
class SearchService extends Service {
  @Inject('http')
  async search(keyword: string) {
    // debounce 在 Service 方法中使用时，需要注意 this 绑定
  }
}

// 更好的方式：在 init 中创建防抖函数
async [Service.init]() {
  const doSearch = this.ctx.debounce(async (keyword: string) => {
    const results = await this.ctx.http.get('/search', { params: { q: keyword } })
    this.ctx.emit('search/results', results)
  }, 300)
  this.ctx.on('search/input', doSearch)
}
```

### 心跳检测

```typescript
ctx.plugin((ctx) => {
  let lastHeartbeat = Date.now()
  
  ctx.on('heartbeat', () => {
    lastHeartbeat = Date.now()
  })

  // 每 10 秒检查一次心跳
  const stop = ctx.interval(() => {
    if (Date.now() - lastHeartbeat > 30000) {
      ctx.logger.warn('Heartbeat timeout, reconnecting...')
      reconnect()
    }
  }, 10000)

  // 插件卸载时自动停止检查
})
```

## 类型签名汇总

```typescript
type WithDispose<T> = T & { dispose: () => void }

class TimerService extends Service {
  constructor(ctx: Context)

  // 延时执行
  timeout(callback: () => void, delay: number): () => void
  timeout(delay: number): Promise<void>

  // 定时执行
  interval(callback: () => void, delay: number): () => void
  interval<R = any>(delay: number): AsyncIterableIterator<void, R, void>

  // 节流
  throttle<F extends (...args: any[]) => void>(
    callback: F, delay: number, noTrailing?: boolean
  ): WithDispose<F>

  // 防抖
  debounce<F extends (...args: any[]) => void>(
    callback: F, delay: number
  ): WithDispose<F>

  // 废弃别名
  /** @deprecated */ setTimeout(callback: () => void, delay: number): () => void
  /** @deprecated */ setTimeout(delay: number): Promise<void>
  /** @deprecated */ setInterval(callback: () => void, delay: number): () => void
  /** @deprecated */ setInterval(delay: number): AsyncIterableIterator<void>
}
```

## 源码引用

| 文件 | 内容 |
|------|------|
| [timer/index.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/timer/src/index.ts) | TimerService 完整实现：timeout/interval 双模式、throttle/debounce、AsyncIterable |
| [fiber.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/core/src/fiber.ts) | Fiber.effect() 效果管理，定时器自动清理的底层机制 |
| [context.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/packages/core/src/context.ts) | Context 扩展，通过 mixin 注入 timer 方法 |
