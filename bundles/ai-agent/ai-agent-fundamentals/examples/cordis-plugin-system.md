---
type: Example
title: Cordis 插件系统深度解析
description: 从 Context 原型链到 Fiber 生命周期到 Service 注入——逐行解析 Cordis 元框架的核心抽象与时空可组合性设计
tags: [ai-agent, cordis, plugin, fiber, context, prototype-chain, dependency-injection, typescript]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T02:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md#cordis
---

# Cordis 插件系统深度解析

Cordis 是 deepseek-harness 的底层插件引擎，提出了"时空可组合性"（Spatiotemporal Composability）的编程范式。本示例深入 Cordis 核心源码，解析其 Context、Fiber、Service、Events 四大核心抽象。

## 1. 核心理念：时空可组合性

Cordis 的论文标题是 *A Programming Paradigm for Spatiotemporal Composability*。这个概念可以拆解为：

- **空间可组合性**：插件可以在不同的上下文（Context）中运行，通过原型链继承和隔离实现作用域控制
- **时间可组合性**：插件有完整的生命周期（Fiber），可以动态加载/卸载/重启，副作用有注册就有清理

传统框架往往只解决其中一个：
- DI 容器（空间）：管理依赖注入，但不处理生命周期
- 生命周期钩子（时间）：如 React 的 useEffect，但不管理作用域隔离

Cordis 同时解决两者。

## 2. Context：原型链式作用域

Context 是 Cordis 最核心的抽象——它既是服务容器，也是插件的作用域边界。

### Object.create() 原型链

```typescript
// packages/core/src/context.ts (概念性)
class Context {
    // 核心服务（在 root context 上创建）
    readonly root: Context;
    readonly events: EventsService;
    readonly registry: RegistryService;
    readonly reflect: ReflectService;
    readonly logger: LoggerService;
    fiber: Fiber;
    
    constructor() {
        this.root = this;
        this.events = new EventsService(this);
        this.registry = new RegistryService(this);
        this.reflect = new ReflectService(this);
        this.logger = new LoggerService(this);
    }
    
    extend(): Context {
        // 使用 Object.create 创建原型链子上下文
        const ctx = Object.create(this) as Context;
        // 子上下文可以覆盖/添加属性
        return ctx;
    }
    
    isolate(filter: symbol | ((ctx: Context) => boolean)): Context {
        const ctx = this.extend();
        // 设置隔离标记，通过 symbols.filter 实现
        ctx[symbols.filter] = typeof filter === 'symbol'
            ? (key: symbol) => key !== filter
            : filter;
        return ctx;
    }
    
    intercept(config: Record<string, any>): Context {
        const ctx = this.extend();
        // 创建配置拦截层
        ctx[symbols.intercept] = {
            ...this[symbols.intercept],
            ...config
        };
        return ctx;
    }
}
```

**为什么用 Object.create() 而不是类继承？**

Object.create() 创建的是一个原型链对象：

```
child.__proto__ === parent
```

这意味着：
1. child 上找不到的属性会自动沿原型链查找到 parent
2. child 设置属性不会影响 parent（只是在 child 上 shadow）
3. 可以无限嵌套：grandchild → child → parent → root

这比类继承更灵活——你可以在运行时动态创建任意深度的作用域链，而不需要预定义类层次。

### 三种扩展操作对比

```
root Context (events, registry, reflect, logger, fiber)
    │
    ├─ extend() → child
    │   继承所有服务，可覆盖/添加新属性
    │   适用于：插件运行的子作用域
    │
    ├─ isolate(filter) → isolated
    │   继承+屏蔽特定服务
    │   适用于：需要隔离某些能力的沙箱环境
    │
    └─ intercept(config) → intercepted
        继承+覆盖服务配置
        适用于：配置不同的服务参数
```

## 3. Fiber：插件生命周期管理

每个插件运行在一个 Fiber 中，Fiber 管理插件的完整生命周期。

### Fiber 状态机

```
         start()
PENDING ─────────► LOADING ────────► ACTIVE
                       │                │
                       │ 错误            │ dispose()/restart()
                       ▼                ▼
                     FAILED      UNLOADING ──────► DISPOSED
                                      ▲
                       restart()      │
                       └──────────────┘
```

### Fiber 核心实现

```typescript
// packages/core/src/fiber.ts (概念性)
class Fiber {
    status: FiberStatus = FiberStatus.PENDING;
    private effects: Array<() => void | Promise<void>> = [];
    private cleanupTasks: Array<() => void | Promise<void>> = [];
    private dependencies: Set<string> = new Set();
    private parent?: Fiber;
    private children: Set<Fiber> = new Set();
    
    constructor(
        public readonly ctx: Context,
        private readonly callback: PluginCallback,
        private readonly config?: any
    ) {}
    
    // 注册副作用（返回清理函数）
    effect(setup: () => (() => void) | void | Promise<() => void> | Promise<void>): void {
        this.assertActive();  // 只在 ACTIVE 状态允许
        const cleanup = setup();
        if (cleanup) {
            if (cleanup instanceof Promise) {
                cleanup.then(disposer => {
                    if (disposer) this.cleanupTasks.push(disposer);
                });
            } else {
                this.cleanupTasks.push(cleanup);
            }
        }
    }
    
    // 启动 Fiber
    async start(): Promise<void> {
        if (this.status !== FiberStatus.PENDING) {
            throw new Error(`Cannot start fiber in ${this.status} state`);
        }
        
        this.status = FiberStatus.LOADING;
        
        try {
            // 执行插件函数
            // 支持三种插件形式：函数、类、对象(apply方法)
            const result = await this._invokeCallback();
            
            // 如果插件返回了 disposer
            if (typeof result === 'function') {
                this.cleanupTasks.push(result);
            }
            
            // 等待子 Fiber 启动
            await Promise.all(
                Array.from(this.children).map(child => child.start())
            );
            
            this.status = FiberStatus.ACTIVE;
        } catch (error) {
            this.status = FiberStatus.FAILED;
            // 清理已注册的 effects
            await this._runCleanup();
            throw error;
        }
    }
    
    // 销毁 Fiber（逆序清理）
    async dispose(): Promise<void> {
        if (this.status === FiberStatus.DISPOSED) return;
        
        this.status = FiberStatus.UNLOADING;
        
        // 1. 先销毁所有子 Fiber
        for (const child of this.children) {
            await child.dispose();
        }
        
        // 2. 逆序执行清理任务（后注册的先清理）
        for (let i = this.cleanupTasks.length - 1; i >= 0; i--) {
            try {
                await this.cleanupTasks[i]();
            } catch (e) {
                this.ctx.logger?.error('Cleanup error:', e);
            }
        }
        
        this.cleanupTasks = [];
        this.status = FiberStatus.DISPOSED;
    }
    
    // 重启（HMR 热更新使用）
    async restart(): Promise<void> {
        await this.dispose();
        this.status = FiberStatus.PENDING;
        this.cleanupTasks = [];
        await this.start();
    }
    
    assertActive(): void {
        if (this.status !== FiberStatus.ACTIVE) {
            throw new Error(
                `Fiber is not active (status: ${this.status}). ` +
                `Effects can only be registered in ACTIVE state.`
            );
        }
    }
}
```

### Effect 的四种形式

Cordis 的 `effect()` 支持四种回调形式，覆盖不同的异步模式：

```typescript
// 1. 同步函数 + 同步 disposer
ctx.effect(() => {
    const handler = () => console.log('event');
    emitter.on('event', handler);
    return () => emitter.off('event', handler);  // disposer
});

// 2. 异步函数 + 异步 disposer
ctx.effect(async () => {
    const connection = await db.connect();
    return async () => await connection.close();
});

// 3. Generator（可暂停/恢复）
ctx.effect(function* () {
    const server = http.createServer();
    server.listen(3000);
    yield;  // 暂停点
    server.close();
});

// 4. AsyncGenerator
ctx.effect(async function* () {
    const watcher = chokidar.watch('./src');
    yield;  // 等待 dispose 信号
    await watcher.close();
});
```

## 4. Service：可注入的服务基类

Service 是 Cordis 中可被依赖注入的基类。

```typescript
// packages/core/src/service.ts (概念性)
abstract class Service<T = any> {
    static [symbols.service] = true;
    static Config?: Schema<any>;  // Standard Schema for config validation
    static inject?: string[];     // 依赖声明
    static merge?: (base: any, override: any) => any;  // 配置合并策略
    
    constructor(protected ctx: Context, public name: string) {
        // 通过 reflect.provide 注册到上下文
        ctx.reflect.provide(name, this);
    }
    
    // 启动钩子（在 Fiber ACTIVE 后调用）
    async start?(): Promise<void>;
    
    // 停止钩子（在 Fiber dispose 前调用）
    async stop?(): Promise<void>;
}
```

### 定义和使用 Service

```typescript
// 1. 定义 Service（Definition 角色）
interface LLMService {
    complete(messages: Message[]): Promise<LLMResponse>;
}

// 2. 实现 Service（Provider 角色）
class DeepSeekLLM extends Service implements LLMService {
    static inject = ['http', 'logger'];  // 声明依赖
    
    constructor(ctx: Context, public config: DeepSeekConfig) {
        super(ctx, 'llm');
    }
    
    async complete(messages: Message[]): Promise<LLMResponse> {
        // 使用注入的 http 服务
        const response = await this.ctx.http.post(
            this.config.apiBase + '/chat/completions',
            { messages, model: this.config.model }
        );
        return response.data;
    }
}

// 3. 注册 Service
ctx.plugin(DeepSeekLLM, { apiBase: 'https://api.deepseek.com', model: 'deepseek-chat' });

// 4. 使用 Service（Consumer 角色）—— 方式一：ctx.inject
ctx.inject(['llm'], async (llm: LLMService) => {
    const response = await llm.complete(messages);
});

// 方式二：@Inject 装饰器
class MyPlugin extends Service {
    @Inject('llm')
    private llm!: LLMService;
    
    async start() {
        // this.llm 已自动注入
    }
}
```

## 5. Events：五种事件分发模式

EventsService 是 Cordis 的事件总线，提供五种分发模式：

```typescript
// packages/core/src/events.ts (概念性)
class EventsService {
    // 1. emit：同步广播，忽略返回值
    emit(event: string, ...args: any[]): void {
        for (const listener of this.getListeners(event)) {
            listener(...args);  // 不等待、不收集返回值
        }
    }
    
    // 2. parallel：并行执行，Promise.allSettled，聚合错误
    async parallel(event: string, ...args: any[]): Promise<any[]> {
        const tasks = this.getListeners(event).map(fn => 
            fn(...args).catch(e => ({ error: e }))
        );
        return Promise.allSettled(tasks);
    }
    
    // 3. serial：串行异步，遇到 truthy 返回值提前返回
    async serial(event: string, ...args: any[]): Promise<any> {
        for (const listener of this.getListeners(event)) {
            const result = await listener(...args);
            if (result) return result;  // 第一个 truthy 结果返回
        }
    }
    
    // 4. bail：同步串行，遇到 truthy 返回值提前返回
    bail(event: string, ...args: any[]): any {
        for (const listener of this.getListeners(event)) {
            const result = listener(...args);
            if (result) return result;
        }
    }
    
    // 5. waterfall：中间件模式，必须调用 next()
    async waterfall(event: string, ...args: any[]): Promise<any> {
        const listeners = this.getListeners(event);
        let index = 0;
        let currentArgs = args;
        
        const next = async (...newArgs: any[]) => {
            if (newArgs.length) currentArgs = newArgs;
            if (index >= listeners.length) return currentArgs[0];
            const listener = listeners[index++];
            return listener(...currentArgs, next);
        };
        
        return next();
    }
}
```

### waterfall 模式的实际应用——agent-loop

deepseek-harness 的 agent-loop 大量使用 waterfall 模式：

```typescript
// 插件在不同阶段插入逻辑
// compaction 包：循环前检查上下文长度
ctx.waterfall('agent/loop', async (state, next) => {
    if (await ctx.llm.countTokens(state.messages) > state.maxTokens * 0.8) {
        state.messages = await this.compact(state.messages);
    }
    return next(state);
});

// guard 包：循环后检查工具调用次数
ctx.waterfall('agent/loop', async (state, next) => {
    state.iterationCount++;
    if (state.iterationCount > this.config.maxIterations) {
        throw new Error('Max iterations exceeded');
    }
    return next(state);
});

// core 包：执行 LLM 调用
ctx.waterfall('agent/loop', async (state, next) => {
    state.response = await ctx.llm.complete(state.messages, {
        tools: state.toolDefinitions
    });
    return next(state);
});
```

waterfall 的关键特性是**不调用 next() 则短路**——如果某个监听器决定不需要继续链中的后续步骤，可以直接返回值终止链。

## 6. Registry：插件注册与依赖

```typescript
// packages/core/src/registry.ts (概念性)
class RegistryService {
    private entries: Map<string, any> = new Map();
    
    // 注册插件
    plugin(plugin: Plugin, config?: any): Fiber {
        const fiber = new Fiber(this.ctx, plugin, config);
        return fiber;
    }
    
    // 注入依赖（命令式）
    inject(deps: string[], callback: (...services: any[]) => any): () => void {
        const resolveServices = () => 
            deps.map(name => this.ctx.reflect.get(name));
        // 立即检查依赖
        for (const dep of deps) {
            if (!this.ctx.reflect.has(dep)) {
                throw new Error(`Missing dependency: ${dep}`);
            }
        }
        // 执行回调
        return callback(...resolveServices());
    }
    
    get<T>(name: string): T | undefined {
        return this.entries.get(name) ?? this._resolveFromPrototype(name);
    }
    
    has(name: string): boolean {
        return this.entries.has(name) || 
               (this.ctx !== this.ctx.root && this.ctx.root.registry.has(name));
    }
}
```

## 7. 配置加载器（@cordisjs/loader）

Cordis 的 loader 包支持通过 YAML 声明式配置插件：

```yaml
# cordis.yml
plugins:
  # 简单配置
  llm:
    provider: deepseek
    model: deepseek-chat
  
  # 带动态配置
  fs:
    policy: !!js |
      (ctx) => ({
        allowRead: ctx.config.workspace + '/**',
        denyWrite: ['**/.env', '**/node_modules/**']
      })
  
  # 分组
  group:security:
    plugins:
      sandbox:
        provider: e2b
      guard:
        maxIterations: 50
        toolTimeout: 30000
  
  # 隔离
  isolate:
    - untrusted-plugin
```

loader 负责：
1. 解析 YAML 配置
2. 按依赖顺序加载插件
3. 处理 `!!js` 动态配置
4. 管理 group 分组和 isolate 隔离
5. 支持配置热更新（HMR）

## 8. Cordis 与传统 DI 容器的对比

| 维度 | InversifyJS/NestJS | Cordis |
|------|-------------------|--------|
| 作用域 | 容器级 | Context 原型链（可任意嵌套） |
| 生命周期 | request/singleton/transient | Fiber 状态机（完整生命周期管理） |
| 事件系统 | 无内置 | 5 种分发模式（含 waterfall 中间件） |
| 配置 | 装饰器/静态 | YAML 声明式 + intercept 覆盖 |
| 热更新 | 不支持 | Fiber.restart() + @cordisjs/hmr |
| 隔离 | 子容器 | isolate() 符号过滤 |
| 学习曲线 | 中等（装饰器+容器API） | 较高（需理解Context/Fiber/Service三者关系） |

## 关键收获

Cordis 的核心创新在于将**作用域（Context 原型链）**和**生命周期（Fiber 状态机）**统一在一个元框架中：

1. **Object.create() 原型链**比类继承更适合运行时动态作用域
2. **注册即副作用**（effect+disposer）确保资源不会泄漏
3. **五种事件模式**覆盖了从广播到中间件的所有通信需求
4. **waterfall 模式**是实现可组合 Agent 循环的关键（dsh 的实践证明）
5. **三角色 Capability Seam**（Definition/Provider/Consumer）让接口与实现分离
6. **YAML 声明式组合**让非程序员也能配置插件组合
