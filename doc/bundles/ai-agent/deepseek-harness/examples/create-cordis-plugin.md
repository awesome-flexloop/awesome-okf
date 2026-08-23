---
type: Example
title: 创建 Cordis 插件
description: 学习如何在 DeepSeek Harness 中创建一个 Cordis 插件，包括 Service 定义、配置 Schema、依赖注入和声明合并。
tags:
  - cordis
  - plugin
  - service
  - dependency-injection
  - declaration-merging
related:
  - define-custom-tool
  - connect-mcp-server
  - build-agent-loop
sources:
  - packages/mcp/mcp-client/src/index.ts
  - packages/fs/tool-fs/src/index.ts
  - packages/core/tools/src/index.ts
  - packages/boot/app-boot/src/index.ts
---

# 创建 Cordis 插件

## 场景说明

DeepSeek Harness 基于 [Cordis](https://github.com/koishijs/cordis) 插件框架构建。每个功能模块（LLM 适配器、工具、沙箱、MCP 客户端等）都是一个 Cordis 插件，通过统一的 `name` / `inject` / `Config` / `apply` 契约注册到应用上下文中。本示例演示如何从零创建一个提供「问候服务」的自定义插件，涵盖：

- 插件的基本结构（`name`、`inject`、`Config`、`apply`）
- 使用 `@deepseek-ai/schemastery` 定义配置 Schema 并设置默认值
- 自定义 Service 类的定义与注册
- 通过 `declare module` 进行 TypeScript 声明合并，让 `ctx.greeter` 获得类型提示
- 使用 `ctx.effect()` 管理插件生命周期
- 在 `cordis.yml` 中加载插件

## 完整代码示例

创建文件 `plugins/greeter/index.ts`：

```typescript
/**
 * 一个简单的问候服务插件：注册 ctx.greeter 服务，支持多语言问候。
 * @module my-dsh-greeter
 */

import type { Context } from '@deepseek-ai/cordis'
import { Service } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'

// ---- 插件元信息 ----

/** Cordis 插件名称，用于 Loader 诊断和重复检测。 */
export const name = 'greeter'

/**
 * 本插件依赖的服务列表。Cordis 会在这些服务就绪后才调用 apply，
 * 并在注入的上下文上提供类型安全的 ctx.get() / ctx.xxx 访问。
 * 此处声明依赖 tools 服务，演示插件间协作。
 */
export const inject = ['tools']

// ---- 配置 Schema ----

export interface Config {
  /** 默认语言，支持 'en' | 'zh' | 'ja'。 */
  defaultLanguage?: 'en' | 'zh' | 'ja'
  /** 问候语前缀，默认为空字符串。 */
  prefix?: string
  /** 是否在插件激活时打印一条欢迎日志。 */
  logOnStart?: boolean
}

/**
 * 使用 @deepseek-ai/schemastery 定义配置 Schema。
 * Schemastery 在 Loader 加载 cordis.yml 时自动校验配置并填充默认值。
 */
export const Config: z<Config> = z.object({
  defaultLanguage: z.union(['en', 'zh', 'ja'] as const).default('en'),
  prefix: z.string().default(''),
  logOnStart: z.boolean().default(true),
})

// ---- 声明合并（Declaration Merging）----

/**
 * 通过 TypeScript 的 declare module 语法扩展 Cordis 的 Context 接口，
 * 让 ctx.greeter 在整个应用中获得类型提示。这是 Cordis 插件的标准模式：
 * - 所有通过 ctx.service() 注册的服务都应在此声明
 * - 事件通过 interface Events 扩展
 */
declare module '@deepseek-ai/cordis' {
  interface Context {
    greeter: GreeterService
  }

  interface Events {
    /**
     * 当 greet() 被调用时触发，监听器可修改返回值或记录日志。
     * @param name - 被问候者名称
     * @param language - 使用的语言
     */
    'greeter/greet'(this: GreeterService, name: string, language: string): void
  }
}

// ---- 服务实现 ----

type ResolvedConfig = Required<Config>

/** 多语言问候语模板。 */
const GREETINGS: Record<string, string> = {
  en: 'Hello, {name}!',
  zh: '你好，{name}！',
  ja: 'こんにちは、{name}さん！',
}

/**
 * 自定义 Service 类。继承自 Cordis 的 Service 基类，
 * 通过 super(ctx, 'greeter') 将自身注册到 ctx.greeter。
 */
export class GreeterService extends Service {
  private readonly config: ResolvedConfig
  private callCount = 0

  constructor(ctx: Context, config: Config) {
    super(ctx, 'greeter')
    // Schemastery 已填充所有默认值，此处安全地转换为 Required
    this.config = config as ResolvedConfig
  }

  /**
   * 插件初始化逻辑。Cordis 在构造函数后立即调用 start()（如果存在）。
   * 适合执行需要依赖其他服务的启动工作。
   */
  protected start(): void {
    if (this.config.logOnStart) {
      this.ctx.logger.info(`greeter plugin started, default language: ${this.config.defaultLanguage}`)
    }
  }

  /**
   * 生成问候语。
   * @param name - 被问候者名称
   * @param language - 语言代码，不传则使用默认语言
   * @returns 格式化后的问候字符串
   */
  greet(name: string, language?: string): string {
    const lang = language ?? this.config.defaultLanguage
    const template = GREETINGS[lang] ?? GREETINGS.en
    const result = this.config.prefix + template.replace('{name}', name)

    this.callCount++
    // 触发事件，其他插件可监听
    this.ctx.emit('greeter/greet', name, lang)

    return result
  }

  /** 获取当前调用次数。 */
  get stats(): { calls: number } {
    return { calls: this.callCount }
  }
}

// ---- 插件 apply 函数 ----

/**
 * 插件入口函数。Cordis Loader 在解析 cordis.yml 并满足所有 inject 依赖后调用此函数。
 * @param ctx - 注入后的上下文，已包含 inject 中声明的服务
 * @param config - 经 Schemastery 校验并填充默认值后的配置
 */
export function apply(ctx: Context, config: Config): void {
  // ctx.effect() 注册一个带自动清理的副作用：
  // - 插件被禁用/HMR 热更新/应用关闭时，返回的清理函数会自动执行
  // - 第二个参数是调试标签，出现在错误栈和 HMR 日志中
  ctx.effect(() => {
    // 注册服务：ctx.service(serviceClass, config) 会实例化 Service 子类
    // 并将其挂载到 ctx.greeter（由 Service 构造函数的第二个参数决定名称）
    ctx.service(GreeterService, config)
    this.ctx.logger.info('greeter: service registered')

    // 返回清理函数：插件卸载时自动执行
    return () => {
      ctx.logger.info('greeter: service disposed')
    }
  }, 'greeter.service')

  // 监听自己的事件，演示插件内部事件处理
  ctx.on('greeter/greet', (name, lang) => {
    ctx.logger.debug(`greeter: greeted "${name}" in ${lang}`)
  })
}
```

在 `cordis.yml` 中加载此插件：

```yaml
# cordis.yml
- id: greeter
  name: './plugins/greeter'  # 相对路径或包名
  config:
    defaultLanguage: zh
    prefix: '🌟 '
    logOnStart: true

# 其他插件可以依赖 greeter 服务：
# - id: my-other-plugin
#   name: './plugins/my-other-plugin'
#   inject:
#     - greeter  # 声明依赖后 ctx.greeter 在 apply 中可用
```

## 逐步解释

### 1. 插件元信息：`name` 和 `inject`

```typescript
export const name = 'greeter'
export const inject = ['tools']
```

- `name` 是插件的唯一标识符，Cordis Loader 使用它做诊断和重复检测。命名约定使用 kebab-case。
- `inject` 声明插件的依赖服务列表。Cordis 会确保这些服务在 `apply` 调用前已就绪，并且在注入后的 `ctx` 上提供类型安全的访问。如果依赖未满足，插件会处于 `PENDING` 状态直到依赖可用。

### 2. 配置 Schema 与默认值

```typescript
export const Config: z<Config> = z.object({
  defaultLanguage: z.union(['en', 'zh', 'ja'] as const).default('en'),
  prefix: z.string().default(''),
  logOnStart: z.boolean().default(true),
})
```

使用 `@deepseek-ai/schemastery` 定义配置：
- `.default()` 提供默认值，YAML 中未配置的字段自动填充
- `.union()` 定义联合类型（枚举值），非法值在加载时直接报错
- `z<Config>` 类型断言确保 Schema 与 TypeScript 接口一致
- Loader 还支持 YAML 中的 `!!js` 表达式来动态计算配置值

### 3. 声明合并（Declaration Merging）

```typescript
declare module '@deepseek-ai/cordis' {
  interface Context {
    greeter: GreeterService
  }
  interface Events {
    'greeter/greet'(name: string, language: string): void
  }
}
```

这是 Cordis 插件开发的**关键模式**：
- 扩展 `Context` 接口让 `ctx.greeter` 全局获得类型提示
- 扩展 `Events` 接口让 `ctx.emit('greeter/greet', ...)` 和 `ctx.on('greeter/greet', ...)` 获得类型检查
- 不进行声明合并，代码仍然能运行，但失去类型安全

### 4. Service 类定义

```typescript
export class GreeterService extends Service {
  constructor(ctx: Context, config: Config) {
    super(ctx, 'greeter')  // 'greeter' 对应 ctx.greeter 的属性名
  }
  protected start(): void { /* 初始化逻辑 */ }
}
```

- 继承 `Service` 基类，通过构造函数第二个参数指定服务名称（即挂载到 `ctx` 上的属性名）
- `start()` 方法是可选的生命周期钩子，在服务注册后、依赖就绪后调用
- 服务自动获得 `this.ctx`（所属上下文）、`this.ctx.logger`（带插件名前缀的日志器）等能力

### 5. apply 函数与生命周期管理

```typescript
export function apply(ctx: Context, config: Config): void {
  ctx.effect(() => {
    ctx.service(GreeterService, config)
    return () => { /* 清理逻辑 */ }
  }, 'greeter.service')
}
```

- `apply` 是插件入口，所有注册和初始化逻辑在此执行
- `ctx.effect()` 管理副作用生命周期，返回的 disposer 在插件卸载时自动调用
- `ctx.service(ServiceClass, ...args)` 实例化并注册服务
- 事件监听器（`ctx.on`/`ctx.once`/`ctx.waterfall`）在 effect 内注册时，会在清理时自动解绑，无需手动管理

## 输出结果

启动应用（假设已配置好 `DEEPSEEK_API_KEY` 环境变量）：

```bash
$ dsh --config cordis.yml
[greeter] greeter plugin started, default language: zh
[greeter] greeter: service registered
# ... 其他插件加载日志 ...
# Agent 就绪后，用户发送 "greet Alice"
[greeter] greeter: greeted "Alice" in zh
# 模型调用 greet("Alice") 返回 "🌟 你好，Alice！"
```

## 注意事项

1. **命名规范**：插件 `name` 使用 kebab-case，事件名使用 `plugin-name/event-name` 格式（如 `greeter/greet`），避免与其他插件冲突。

2. **inject 顺序**：`inject` 中的服务名必须与其他插件通过 `declare module` 声明的名称完全一致。拼写错误会导致插件永久 PENDING。

3. **effect 清理**：所有需要在卸载时释放的资源（定时器、文件句柄、子进程等）必须通过 `ctx.effect()` 返回的 disposer 清理，否则 HMR 热更新时会泄漏资源。

4. **Schemastery 校验**：`Config` Schema 是运行时校验，不仅是类型注解。YAML 中配置了非法值会在加载时立即报错，不会静默降级。

5. **Service 名称唯一性**：`super(ctx, 'greeter')` 中的名称必须全局唯一，重复注册会抛出错误。命名建议与插件 `name` 一致。

6. **声明合并位置**：`declare module '@deepseek-ai/cordis'` 必须在 `.ts` 源文件中（而非 `.d.ts`），并确保该文件被 TypeScript 编译入口包含。如果类型不生效，检查 `tsconfig.json` 的 `include` 是否覆盖了插件目录。

7. **async apply**：`apply` 可以是 `async function`（如 MCP 客户端插件），Cordis 会等待 Promise resolve 后才标记插件为 ACTIVE。但需注意 `ctx.effect()` 内的注册在 apply 返回前就应完成，否则其他插件可能观察到部分就绪状态。
