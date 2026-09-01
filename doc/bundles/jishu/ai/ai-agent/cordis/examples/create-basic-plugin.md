---
type: Example
title: 创建基础插件
description: 使用 Cordis 的 Context.plugin、Service 抽象类和 @Inject 装饰器创建一个可复用的插件，演示依赖注入与服务注册的完整流程。
tags: [cordis, example, plugin, service, inject, getting-started]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: Cordis 源码事实清单
---

## 场景说明

你需要在 Cordis 应用中创建一个基础插件，该插件：
1. 定义一个自定义服务（`GreetingService`），提供问候功能
2. 使用 `@Inject` 装饰器声明对内置 `logger` 服务的依赖
3. 通过 `ctx.plugin()` 注册插件到上下文
4. 验证插件生命周期和服务隔离机制

本示例覆盖三种插件形式中的 Constructor 类型（类插件），这是最常用的形式。

## 前置条件

```bash
# 安装 cordis
npm install cordis@4.0.0-rc.8
# 或
yarn add cordis@4.0.0-rc.8
```

## 完整代码

创建 `greeting-plugin.ts`：

```typescript
import { Context, Service } from 'cordis'
import { Inject } from 'cordis'

// ========== 1. 定义服务类 ==========

// 通过继承 Service<T> 定义服务，T 为配置类型
// Service 构造函数接收 (ctx, name?)，name 默认取 constructor.provide
class GreetingService extends Service<GreetingService.Config> {
  // 静态 provide 属性声明服务名，用于 ctx.reflect.provide 注册
  static inject = { logger: true }

  private greetings: string[] = []

  constructor(ctx: Context, public config: GreetingService.Config) {
    super(ctx, 'greeting')
    // config 由 Cordis 通过 @standard-schema/spec 同步验证后传入
  }

  // Service 的 [symbols.init]() 钩子在 Fiber 激活时执行
  // 返回值（函数/迭代器/Promise）作为 Effect 处理
  async [Service.init]() {
    this.logger.info('GreetingService 已启动，配置：%o', this.config)

    // 返回 dispose 函数，插件卸载时自动调用
    return () => {
      this.logger.info('GreetingService 已停止')
    }
  }

  // 公共方法：添加问候语
  addGreeting(text: string) {
    this.greetings.push(text)
    // 使用注入的 logger 服务（通过 @Inject 或 Service 基类的 this.ctx 访问）
    this.ctx.logger.info('添加问候语：%s，当前共 %d 条', text, this.greetings.length)
  }

  // 公共方法：发送问候
  greet(name: string): string {
    const prefix = this.config.prefix ?? 'Hello'
    const message = `${prefix}, ${name}!`
    this.ctx.logger.debug('生成问候：%s', message)
    return message
  }

  // 公共方法：获取所有问候语
  listGreetings(): readonly string[] {
    return this.greetings
  }
}

namespace GreetingService {
  export interface Config {
    prefix?: string
    locale?: string
  }
}

// ========== 2. 定义插件函数（使用 @Inject 装饰器）==========

// @Inject 可以装饰类（添加静态 inject 属性）或类方法
// 这里演示 @Inject 装饰类方法的用法
class GreetingPlugin {
  // 使用 @Inject 装饰器声明方法依赖
  // 在实例化后、[Service.init] 执行前，这些方法会被调用注入依赖
  @Inject('greeting')
  injectGreeting(greeting: GreetingService) {
    greeting.addGreeting('Welcome to Cordis!')
    greeting.addGreeting('插件已成功加载')
  }

  constructor(private ctx: Context, public config: GreetingPlugin.Config) {}

  [Service.init]() {
    // 使用 ctx 上混合的服务方法
    this.ctx.logger.info('GreetingPlugin 初始化完成')

    // 监听配置更新
    this.ctx.on('internal/update', (fiber, config) => {
      this.ctx.logger.info('配置更新：%o', config)
    })

    // 返回 effect dispose
    return () => {
      this.ctx.logger.info('GreetingPlugin 已卸载')
    }
  }
}

namespace GreetingPlugin {
  export interface Config {
    autoGreet?: boolean
  }
}

// ========== 3. 使用插件 ==========

// 创建根 Context
const ctx = new Context()

// 安装 console logger（需要额外安装 @cordis/logger-console）
// import LoggerConsole from '@cordis/logger-console'
// ctx.plugin(LoggerConsole)

// 注册服务
ctx.plugin(GreetingService, { prefix: '你好', locale: 'zh-CN' })

// 注册功能插件（依赖 greeting 服务）
ctx.plugin(GreetingPlugin, { autoGreet: true })

// 直接使用服务
console.log(ctx.greeting.greet('World'))
// 输出：你好, World!

ctx.greeting.addGreeting('今天天气不错')
console.log(ctx.greeting.listGreetings())
// 输出：['Welcome to Cordis!', '插件已成功加载', '今天天气不错']

// ========== 4. 函数式插件（更轻量的写法）==========

interface CounterConfig {
  initial?: number
}

// 函数式插件：(ctx, config) => any
// 返回值作为 Effect 处理（可以返回 dispose 函数）
function CounterPlugin(ctx: Context, config: CounterConfig = {}) {
  let count = config.initial ?? 0

  // 通过 ctx.greeting 访问服务（Reflect proxy 会沿 fiber 链查找）
  ctx.greeting.addGreeting(`CounterPlugin 启动，初始值：${count}`)

  ctx.on('counter/increment', () => {
    count++
    ctx.logger.info('计数器增加：%d', count)
  })

  ctx.on('counter/get', () => {
    return count
  })

  // 返回 dispose 函数
  return () => {
    ctx.logger.info('CounterPlugin 已卸载，最终计数：%d', count)
  }
}

// 标记插件名（可选，用于日志和调试）
CounterPlugin.name = 'counter'

// 注册函数式插件
ctx.plugin(CounterPlugin, { initial: 10 })
ctx.emit('counter/increment')
console.log(ctx.bail('counter/get'))  // 输出：11

// ========== 5. 带 inject 依赖的函数式插件 ==========

// 使用 registry.inject 简写形式
ctx.inject(['greeting'], (ctx) => {
  // 此回调仅在 greeting 服务可用时执行
  ctx.greeting.addGreeting('Inject 回调中的问候')
  ctx.logger.info('所有依赖已满足，Inject 回调执行')
})

console.log(ctx.greeting.listGreetings())
```

## 逐步解释

### 步骤 1：理解 Service 抽象类

```typescript
class GreetingService extends Service<Config> {
  static inject = { logger: true }
}
```

- `Service<T>` 是 Cordis 的服务基类，泛型 `T` 是配置类型
- 静态 `inject` 属性声明该服务依赖的其他服务，`{ logger: true }` 表示需要 logger 服务但不传入配置
- 构造函数必须调用 `super(ctx, name)`，`name` 参数是服务注册名，默认为 `constructor['provide']`
- 服务实例通过 `ctx.reflect.provide(name, self, check?)` 注册到上下文
- 服务通过 isolate 机制实现作用域隔离：同一 isolate 域内的 context 共享同一服务实例

### 步骤 2：使用 @Inject 装饰器

```typescript
@Inject('greeting')
injectGreeting(greeting: GreetingService) {
  greeting.addGreeting('Welcome to Cordis!')
}
```

- `@Inject(name, config?)` 可以装饰类或类方法
- 装饰类时：将 inject 添加到类的静态 `inject` 属性，支持原型链继承
- 装饰方法时：在 metadata 中记录 inject，通过 initHooks 在实例化后注册回调
- 方法在 Fiber 激活时、`[Service.init]()` 之前被调用，注入的服务作为参数传入
- 这确保在初始化方法执行时，所有依赖已经可用

### 步骤 3：Service.init 生命周期钩子

```typescript
async [Service.init]() {
  this.logger.info('服务启动')
  return () => {
    this.logger.info('服务停止')
  }
}
```

- `[Service.init]()` 是服务的初始化钩子，在 Fiber 进入 ACTIVE 状态时调用
- 对于 Constructor 类型插件，Fiber 执行流程为：`new 实例` → `执行 initHooks（@Inject方法）` → `调用 [Service.init]()`
- 返回值可以是：
  - **函数**：作为 dispose 清理函数，插件卸载时按注册逆序执行
  - **Promise**：等待异步操作完成
  - **Iterable/AsyncIterable**：迭代器的每个 yield 作为 effect 处理
- 不要在构造函数中做副作用操作，构造函数只做属性赋值

### 步骤 4：三种插件形式对比

| 形式 | 定义方式 | 适用场景 |
|------|---------|---------|
| Constructor | `class extends Service` | 需要生命周期管理、配置验证、服务提供 |
| Function | `(ctx, config) => dispose` | 简单功能、事件监听、中间件 |
| Object | `{ apply(ctx, config) }` | 从其他模块导出的插件对象 |

三种形式都可包含可选属性：`name?`、`Config?`（StandardSchemaV1）、`inject?`、`provide?`、`intercept?`。

### 步骤 5：配置验证

```typescript
// 可以通过静态 Config 属性配置 Standard Schema 验证
import { z } from 'zod'

GreetingService.Config = z.object({
  prefix: z.string().default('Hello'),
  locale: z.enum(['zh-CN', 'en-US']).default('en-US')
})
```

- Cordis 使用 `@standard-schema/spec` 进行配置验证（同步验证，不支持异步）
- 验证失败时抛出 `ValidationError`，消息格式为 `invalid config:\n  - {message} (at {path})`
- 配置通过 `Service[symbols.resolveConfig]()` 沿原型链收集 intercept 中的配置，支持 merge

## 运行示例

```bash
# 使用 tsx 或 ts-node 运行
npx tsx greeting-plugin.ts
```

预期输出：
```
[greeting] GreetingService 已启动，配置：{ prefix: '你好', locale: 'zh-CN' }
[greeting] 添加问候语：Welcome to Cordis!，当前共 1 条
[greeting] 添加问候语：插件已成功加载，当前共 2 条
[greeting] GreetingPlugin 初始化完成
你好, World!
[greeting] 添加问候语：今天天气不错，当前共 3 条
['Welcome to Cordis!', '插件已成功加载', '今天天气不错']
[greeting] 添加问候语：CounterPlugin 启动，初始值：10
[counter] 计数器增加：11
11
[greeting] 添加问候语：Inject 回调中的问候
[greeting] 所有依赖已满足，Inject 回调执行
['Welcome to Cordis!', '插件已成功加载', '今天天气不错', 'CounterPlugin 启动，初始值：10', 'Inject 回调中的问候']
```

## 常见问题

**Q: 为什么通过 `ctx.greeting` 访问服务而不是手动 import？**

A: Cordis 使用 Reflect Proxy 拦截属性访问。当你访问 `ctx.greeting` 时，`ReflectService.handler` 的 get 拦截器沿 fiber 链查找服务实现。这使得：
- 服务可以被 isolate 隔离（不同子 context 可以有不同实例）
- 服务可以被 intercept 覆盖配置
- 未注册的服务访问返回 `undefined` 而非抛错

**Q: dispose 函数何时被调用？**

A: 以下情况触发 dispose：
1. 调用 `ctx.registry.delete(plugin)` 卸载插件
2. Fiber 被重启（`fiber.restart()`）时先 dispose 旧 effect
3. Fiber 依赖的服务不可用时自动卸载
4. Root context 销毁时

所有 dispose 函数按注册逆序执行，支持异步串行清理。

## 相关概念

- [Context 容器系统](../concepts/context-container.md)
- [服务注册与发现](../concepts/service-registry.md)
- [Fiber 生命周期](../concepts/fiber-lifecycle.md)
- [Reflect 元数据系统](../concepts/reflect-metadata.md)
- [插件与模块系统](../concepts/plugin-module.md)
