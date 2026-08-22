---
type: Concept
title: 插件化架构模式
description: AI Agent 框架的插件系统设计——从简单注册表到 Cordis 的 Context 原型链、Fiber 生命周期与能力缝模式
tags: [ai-agent, plugin-architecture, cordis, registry, fiber, dependency-injection, capability-seam, lifecycle]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: cordis
    resource: /references/ai-agent-sources.md#cordis
  - id: dsh
    resource: /references/ai-agent-sources.md#deepseek-harness
  - id: hermes
    resource: /references/ai-agent-sources.md#hermes-agent
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
---

# 插件化架构模式

插件化架构是现代 Agent 框架的基石——它让框架核心保持精简，同时允许通过插件扩展功能。从简单的注册表模式到 Cordis 的时空可组合性元框架，不同框架在"可扩展性"上采取了截然不同的设计。本文从简单到复杂分析四种插件架构模式。

## 为什么需要插件化

Agent 框架的功能域极其广泛：LLM 调用、工具执行、文件操作、Web 搜索、终端管理、MCP 协议、沙箱、记忆、压缩、守卫……将所有功能硬编码在核心中会导致：

1. **代码膨胀**：核心变成"上帝对象"
2. **耦合严重**：功能之间隐式依赖
3. **无法裁剪**：所有用户都带着不需要的功能
4. **扩展困难**：添加新功能需要修改核心代码

插件化架构通过**依赖注入**、**控制反转**和**生命周期管理**解决这些问题。

## 模式一：简单注册表（Registry Pattern）

最简单的插件模式是**注册表（Registry）**——一个中心化的字典存储插件实例，提供 register/get/list 方法。

### hermes-agent 的 ToolRegistry

hermes-agent 使用单例注册表管理工具：

```python
class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: dict[str, Tool] = {}
        return cls._instance
    
    def register(self, name: str, func: Callable, **metadata):
        """注册工具"""
        tool = Tool(name=name, func=func, **metadata)
        self._tools[name] = tool
        return tool  # 返回可用于取消注册的句柄
    
    def unregister(self, name: str):
        """取消注册"""
        self._tools.pop(name, None)
    
    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)
    
    def list_all(self) -> list[Tool]:
        return list(self._tools.values())
```

### Zleap-Agent 的多注册表

Zleap-Agent 将注册表模式扩展为**多个独立注册表**，每种资源类型有自己的注册表：

```typescript
class ToolRegistry extends BaseRegistry<Tool> { }
class SkillRegistry extends BaseRegistry<Skill> { }
class WorkSpaceRegistry extends BaseRegistry<Workspace> { }
class AgentRegistry extends BaseRegistry<AgentDef> { }
class ProviderRegistry extends BaseRegistry<ProviderAdapter> { }
class ModelRegistry extends BaseRegistry<ModelDefinition> { }
```

每个注册表遵循相同的 BaseRegistry 接口（register/get/list），但管理不同类型的资源。

### 注册表模式的优缺点

| 优点 | 缺点 |
|------|------|
| 简单直观，易于理解 | 无生命周期管理（注册后如何初始化？何时销毁？） |
| O(1) 查找 | 无依赖注入（插件间依赖需要手动管理） |
| 易于实现 | 无隔离（一个插件的错误可能影响全局） |
| 适合简单场景 | 无热更新支持 |

## 模式二：副作用注册 + Disposer 模式

比简单注册表更进一步的是**注册即副作用**模式——注册时执行初始化逻辑，返回 disposer 函数用于清理。

```typescript
// 概念：副作用注册
class PluginSystem {
    private effects: Array<() => void> = [];
    
    effect(setup: () => (() => void) | void): void {
        // 执行 setup，收集 disposer
        const disposer = setup();
        if (disposer) {
            this.effects.push(disposer);
        }
    }
    
    dispose(): void {
        // 逆序执行所有 disposer
        for (let i = this.effects.length - 1; i >= 0; i--) {
            this.effects[i]();
        }
        this.effects = [];
    }
}

// 使用
system.effect(() => {
    console.log("注册 web_search 工具");
    registry.register("web_search", searchHandler);
    return () => {
        console.log("清理 web_search 工具");
        registry.unregister("web_search");
    };
});
```

这种模式在 React Hooks、VS Code 扩展等系统中广泛使用。它解决了注册表模式缺乏清理机制的问题，但仍然缺乏依赖管理和隔离。

## 模式三：Cordis Fiber 生命周期 + Context 原型链

Cordis 将插件系统提升到了元框架级别，引入了三个核心抽象：**Context**（原型链式作用域）、**Fiber**（插件生命周期）、**Service**（可注入服务）。

### Context：原型链式作用域

Cordis 的 `Context` 使用 JavaScript 的 `Object.create()` 实现**原型链式继承**：

```typescript
// Cordis Context 核心概念
class Context {
    readonly root: Context;
    readonly events: EventsService;
    readonly registry: RegistryService;
    readonly reflect: ReflectService;
    readonly logger: LoggerService;
    readonly fiber: Fiber;
    
    // 创建子上下文（继承父上下文的所有服务）
    extend(): Context {
        const child = Object.create(this);
        // 子上下文可以覆盖父上下文的属性
        return child;
    }
    
    // 创建隔离上下文（不继承某些服务）
    isolate(filter: symbol | Service): Context {
        const child = this.extend();
        // 使用 symbols.filter 标记隔离边界
        return child;
    }
    
    // 拦截/覆盖服务配置
    intercept(config: object): Context {
        const child = this.extend();
        // 创建配置覆盖层
        return child;
    }
}
```

**三种扩展操作**：

| 操作 | 行为 | 类比 |
|------|------|------|
| `extend()` | 创建子上下文，继承所有服务 | 子类继承父类 |
| `isolate()` | 创建隔离边界，屏蔽特定服务 | 进程隔离 |
| `intercept(config)` | 覆盖服务配置 | 环境变量覆盖 |

这种设计让插件可以在自己的 Fiber 上下文中运行，不干扰其他插件；同时通过原型链继承共享核心服务。

### Fiber：插件生命周期管理

Fiber 管理每个插件的完整生命周期：

```
PENDING → LOADING → ACTIVE → DISPOSED
                  ↘ FAILED
                  ↘ UNLOADING → DISPOSED
```

```typescript
class Fiber {
    status: FiberStatus;  // PENDING | LOADING | ACTIVE | FAILED | DISPOSED | UNLOADING
    private effects: Array<() => void | Promise<void>> = [];
    private dependencies: Set<string>;  // 依赖的服务名
    
    // 注册副作用（返回 AsyncDisposable）
    effect(setup: EffectCallback): void {
        // 支持四种 effect 形式：
        // 1. 同步函数 → 返回 disposer
        // 2. 异步函数 → 返回 Promise<disposer>
        // 3. Generator → yield 步骤
        // 4. AsyncGenerator → 异步 yield
    }
    
    // 启动 Fiber
    async start(): Promise<void> {
        this.status = FiberStatus.LOADING;
        // 检查依赖是否可用
        this.checkDependencies();
        // 执行插件函数/类
        await this.activate();
        this.status = FiberStatus.ACTIVE;
    }
    
    // 销毁 Fiber（逆序清理 effects）
    async dispose(): Promise<void> {
        this.status = FiberStatus.UNLOADING;
        for (let i = this.effects.length - 1; i >= 0; i--) {
            await this.effects[i]();
        }
        this.status = FiberStatus.DISPOSED;
    }
    
    // 重启（HMR 热更新使用）
    async restart(): Promise<void> {
        await this.dispose();
        await this.start();
    }
    
    assertActive(): void {
        if (this.status !== FiberStatus.ACTIVE) {
            throw new Error(`Fiber not active: ${this.status}`);
        }
    }
}
```

### 插件的三种形态

Cordis 支持三种插件定义形式：

```typescript
// 1. 函数式插件
function myPlugin(ctx: Context, config: MyConfig) {
    ctx.effect(() => {
        // 注册服务、监听事件等
        ctx.registry.set("my-service", createService());
        return () => cleanup();
    });
}

// 2. 类插件
class MyPlugin extends Service {
    constructor(ctx: Context, public config: MyConfig) {
        super(ctx);
    }
    
    constructor() {
        // 初始化逻辑
    }
}

// 3. 对象插件（带 apply 方法）
const myPlugin = {
    name: "my-plugin",
    inject: ["llm", "fs"],  // 声明依赖
    apply(ctx: Context, config: MyConfig) {
        ctx.effect(() => { /* ... */ });
    }
};
```

### 依赖注入

Cordis 通过 `inject` 声明和 `@Inject()` 装饰器实现依赖注入：

```typescript
// 声明式注入
ctx.inject(['llm', 'fs'], (llm, fs) => {
    // llm 和 fs 是解析后的服务实例
    // 当依赖变化时自动重新执行
});

// 装饰器注入
class MyService extends Service {
    @Inject('llm')
    private llm: LLMService;
}
```

### Service 系统

`Service<T>` 是 Cordis 中可被注入的服务基类：

```typescript
abstract class Service<T = any> {
    constructor(protected ctx: Context, public name: string) {
        // 通过 reflect.provide 注册到上下文
        ctx.reflect.provide(name, this);
    }
    
    // 支持配置合并
    static Config?: Schema<ServiceConfig>;
    static merge?: (base: any, override: any) => any;
}
```

### 五种事件分发模式

Cordis 的 EventsService 提供五种事件分发模式，适应不同场景：

```typescript
class EventsService {
    // 1. emit：同步广播，忽略返回值
    emit(event: string, ...args: any[]): void;
    
    // 2. parallel：并行执行，Promise.allSettled，聚合错误
    parallel(event: string, ...args: any[]): Promise<any[]>;
    
    // 3. serial：串行异步，遇到 truthy 返回值则提前返回
    serial(event: string, ...args: any[]): Promise<any>;
    
    // 4. bail：同步串行，遇到 truthy 返回值则提前返回
    bail(event: string, ...args: any[]): any;
    
    // 5. waterfall：中间件模式，必须调用 next() 传递
    waterfall(event: string, ...args: any[]): Promise<any>;
}
```

**waterfall 模式**是 dsh agent-loop 的核心机制——每个插件通过 waterfall 监听在循环的不同阶段插入逻辑。

## 模式四：Capability Seam（能力缝）

deepseek-harness 在 Cordis 基础上提出了**能力缝（Capability Seam）**模式，每个能力由三部分组成：

```
┌─────────────────────────────────────────────┐
│           Capability Seam                    │
│                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────┐│
│  │  Definition   │  │  Provider    │  │  C  ││
│  │  (接口+Schema)│→ │  (实现+注册) │→ │  o  ││
│  │               │  │              │  │  n  ││
│  └──────────────┘  └──────────────┘  │  s  ││
│                                      │  u  ││
│                                      │  m  ││
│                                      │  e  ││
│                                      │  r  ││
│                                      └─────┘│
└─────────────────────────────────────────────┘
```

三者完整才构成一个 seam，缺一不可：
- **Definition** 没有 Provider → 接口定义了但没人实现
- **Provider** 没有 Definition → 实现了但没有契约，类型不安全
- **没有 Consumer** → 能力存在但无人使用（死代码）

dsh 的每个能力包（llm/shell/fs/web/mcp/...）都遵循这个三角色模式。

### 声明式组合（cordis.yml）

Cordis 的 loader 支持通过 YAML 配置文件声明式组合插件：

```yaml
# cordis.yml 示例
plugins:
  llm:
    provider: deepseek
    model: deepseek-chat
  fs:
    policy: strict
  shell:
    provider: local
  web:
    search: true
    fetch: true
  mcp:
    servers:
      - command: npx
        args: ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
  sandbox:
    provider: e2b
  guard:
    maxIterations: 50
    toolTimeout: 30000
  compaction:
    threshold: 0.8
```

支持高级配置：
- `!!js` 动态配置（嵌入 JavaScript 表达式）
- `group` 分组（批量配置一组插件）
- `isolate` 隔离（插件在隔离上下文中运行）
- overlay 覆盖（不同环境覆盖配置）

## 四种插件模式对比

| 维度 | 简单注册表 | 副作用+Disposer | Cordis Fiber | Capability Seam |
|------|-----------|----------------|-------------|----------------|
| 生命周期 | ❌ 无 | ✅ dispose 清理 | ✅ Fiber 状态机 | ✅ Fiber 状态机 |
| 依赖注入 | ❌ 手动管理 | ❌ 手动 | ✅ @Inject/ctx.inject | ✅ Service inject |
| 隔离 | ❌ 全局共享 | ❌ 全局共享 | ✅ extend/isolate | ✅ isolate |
| 热更新 | ❌ | ❌ | ✅ Fiber.restart() | ✅ HMR |
| 配置管理 | ❌ | ❌ | ✅ intercept() + YAML | ✅ cordis.yml |
| 事件系统 | ❌ | ❌ | ✅ 5种模式 | ✅ waterfall链 |
| 复杂度 | ★☆☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ |
| 适用项目 | 小型工具 | 中型应用 | 平台级框架 | 企业级可组合平台 |

## deepseek-harness 插件全景

deepseek-harness 将"一切皆插件"贯彻到底，30+ 个包都是独立的 Cordis 插件：

| 层级 | 插件包 | 功能 |
|------|--------|------|
| **核心** | core | Session、agent-loop、system-prompt、tools |
| **能力** | llm/shell/fs/web/mcp/lsp/terminal | 基础能力 seams |
| **安全** | sandbox/guard | 沙箱执行、循环卫生、超时守卫 |
| **智能** | subagent/plan/compaction | 子代理、计划模式、上下文压缩 |
| **集成** | hooks/credentials/settings | Claude Code/Codex hook桥接、凭证管理 |
| **扩展** | skill/preset/bundle/extensions | 技能、预设组合、bundle安装、扩展点 |
| **交互** | feedback/schedule/jobs/todo/interaction | 审批反馈、定时调度、任务、Todo工具 |
| **传输** | api/sdk/acp/client | BFF/JSON-RPC SDK/ACP server/Web客户端 |
| **基础** | boot/util/storage/subprocess/context/host | 应用胶水、工具、存储、子进程、宿主管理 |

## 相关概念

- [工具系统](02-tool-system.md) — 工具注册是插件系统最常见的用途
- [Agent 核心循环](01-agent-loop.md) — dsh 通过 waterfall 插件链实现 agent loop
- [技能与 Persona 系统](07-skill-persona.md) — Zleap 的 Skill 也通过注册表管理
- [Cordis 插件系统深度解析](/examples/cordis-plugin-system.md) — Cordis 核心源码的代码级走读
