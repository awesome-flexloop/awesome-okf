---
type: Reference
title: Cordis 源码信源登记
description: Cordis 4.0.0-rc.8 源码路径、版本信息、核心模块、关键文件与 API 索引
tags: [cordis, source, reference, v4.0, typescript, meta-framework]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T23:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cordis-github
    resource: https://github.com/cordiverse/cordis
    title: Cordis GitHub 仓库
  - id: cordis-paper
    resource: https://github.com/cordiverse/paper
    title: A Programming Paradigm for Spatiotemporal Composability
---

# Cordis 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | Cordis |
| 版本 | **4.0.0-rc.8**（Release Candidate 8） |
| 描述 | Meta-Framework for Modern Applications —— 面向时空可组合性的 TypeScript 元框架 |
| 作者 | Shigma \<shigma10826@gmail.com\> |
| 许可证 | MIT |
| 语言 | TypeScript |
| 包管理 | Yarn 4.14.1（Workspaces + Lerna 风格 monorepo） |
| 构建工具 | yakumo（esbuild + tsc） |
| 测试框架 | vitest |
| 运行要求 | Node.js（需 `--expose-internals` 标志以支持 ESM Loader 内部 API） |
| 核心依赖 | cosmokit@^1.8.1、@standard-schema/spec@^1.1.0 |
| 官方仓库 | <https://github.com/cordiverse/cordis> |
| 论文 | [_A Programming Paradigm for Spatiotemporal Composability_](https://github.com/cordiverse/paper) |

## 项目概览

Cordis 是一个 TypeScript 元框架（Meta-Framework），其核心理念是"时空可组合性"（Spatiotemporal Composability）。框架以 **Context（上下文）** 为核心，通过 **Proxy** 机制实现属性拦截与服务查找，结合 **Fiber（纤程）** 管理插件生命周期，提供 **Service（服务）** 抽象、**Events（事件）** 系统、**Registry（插件注册）** 和 **Reflect（反射）** 机制，构成一个可组合、可热重载、可隔离的插件化应用运行时。

### 架构总览

```
┌─────────────────────────────────────────────────┐
│                   Context (Proxy)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Events   │ │ Logger   │ │ ReflectService   │  │
│  │ Service  │ │ Service  │ │ (Proxy Handler)  │  │
│  └──────────┘ └──────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────────────────────┐   │
│  │Registry  │ │         Fiber (root)          │   │
│  │ Service  │ │  effect / _hooks / _disposables│  │
│  └──────────┘ └──────────────────────────────┘   │
└─────────────────────────────────────────────────┘
         │ plugin() / inject()
         ▼
┌─────────────────────────────────────────────────┐
│              Fiber (Plugin Instance)             │
│  state: PENDING→LOADING→ACTIVE→FAILED/DISPOSED  │
│  epoch 依赖驱动 · effect 效果管理 · 事件钩子      │
└─────────────────────────────────────────────────┘
```

## 源码位置

Cordis 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/cordis/
```

版本标识定义于 packages/core/package.json：

```json
{
  "name": "cordis",
  "version": "4.0.0-rc.8",
  "description": "Meta-Framework for Modern Applications"
}
```

## Packages 结构

项目采用 monorepo 架构，`packages/` 目录下包含 **9 个子包**：

| 包名 | NPM 包名 | 职责 | 关键依赖 |
|------|----------|------|---------|
| **core** | `cordis` | 框架核心：Context、Fiber、Service、Events、Registry、Reflect、Logger | cosmokit, @standard-schema/spec |
| **loader** | `@cordisjs/plugin-loader` | 配置树管理、ESM 模块加载、Entry/Group/Realm | cordis（core） |
| **hmr** | `@cordisjs/plugin-hmr` | 热模块替换：chokidar 文件监听、依赖分析、缓存备份/回滚 | cordis, loader, timer, chokidar, picomatch |
| **include** | `@cordisjs/plugin-include` | 外部配置文件加载：YAML/JSON 配置读写、patch 机制、JS 表达式插值 | cordis, loader, js-yaml |
| **logger-console** | `@cordisjs/logger-console` | 控制台日志导出器：时间戳、彩色标签、格式化输出 | cordis |
| **timer** | `@cordisjs/plugin-timer` | 定时器服务：timeout/interval/throttle/debounce，支持 AsyncIterable | cordis |
| **group** | `@cordisjs/plugin-group` | 插件分组（re-export loader 的 Group 类） | @cordisjs/plugin-loader |
| **create** | `create-cordis` | CLI 脚手架工具：项目模板下载、Yarn 版本管理、git 初始化 | tar, js-yaml, prompts, kleur |
| **utils** | `@cordisjs/utils` | 工具类：List（可清理列表） | cordis, cosmokit |

### 目录树

```
cordis/
├── package.json              # monorepo 根配置 (yarn workspaces)
├── tsconfig.base.json        # TypeScript 基础配置
├── vitest.config.ts          # vitest 测试配置
├── yakumo.yml                # yakumo 构建配置
├── packages/
│   ├── core/                 # 核心框架
│   │   ├── src/
│   │   │   ├── index.ts      # 入口：re-export 7 个模块
│   │   │   ├── context.ts    # Context 类（Proxy 构造）
│   │   │   ├── events.ts     # EventsService 事件系统
│   │   │   ├── fiber.ts      # Fiber 生命周期管理
│   │   │   ├── logger.ts     # LoggerService 日志系统
│   │   │   ├── reflect.ts    # ReflectService 反射/代理
│   │   │   ├── registry.ts   # RegistryService 插件注册 + @Inject 装饰器
│   │   │   ├── service.ts    # Service 抽象基类
│   │   │   └── utils.ts      # 工具函数/symbols/DisposableList
│   │   ├── tests/            # 13 个测试文件
│   │   └── package.json
│   ├── loader/               # 配置加载器
│   │   ├── src/
│   │   │   ├── index.ts      # Loader 主类
│   │   │   ├── internal.ts   # Node.js ESM ModuleLoader 封装
│   │   │   └── config/
│   │   │       ├── tree.ts   # EntryTree 抽象类
│   │   │       ├── entry.ts  # Entry 条目
│   │   │       ├── group.ts  # EntryGroup / Group 分组
│   │   │       ├── isolate.ts # Realm 隔离机制
│   │   │       └── utils.ts  # JS 表达式求值/插值
│   │   └── tests/
│   ├── hmr/                  # 热重载
│   │   ├── src/
│   │   │   ├── index.ts      # Hmr Service
│   │   │   ├── error.ts      # 错误处理
│   │   │   └── locales/      # i18n (en-US, zh-CN)
│   │   └── tests/
│   ├── include/              # 外部配置文件
│   │   ├── src/index.ts      # Include Service
│   │   └── tests/
│   ├── logger-console/       # 控制台日志
│   │   └── src/
│   │       ├── shared.ts     # ConsoleExporter 共享逻辑
│   │       ├── index.ts      # Node.js 端实现
│   │       └── browser.ts    # 浏览器端实现
│   ├── timer/                # 定时器
│   │   └── src/index.ts      # TimerService
│   ├── group/                # 分组
│   │   └── src/index.ts      # re-export Group
│   ├── create/               # CLI 脚手架
│   │   └── src/
│   │       ├── index.ts      # Scaffold 类 + stageYarnBin
│   │       └── bin.ts        # CLI 入口
│   └── utils/                # 工具包
│       └── src/index.ts      # List 类
```

## 关键文件清单（≥10）

### 核心框架（core）

| 文件 | 行级引用 | 内容 |
|------|---------|------|
| context.ts | L9-L78 | Context 类定义。构造函数返回 Proxy 对象，包含 4 个静态 symbol（effect/filter/isolate/intercept）、静态 `is()` 类型守卫、`extend()`、`isolate()`、`intercept()` 方法 |
| fiber.ts | L78-L486 | Fiber 生命周期核心。FiberState 枚举（6 状态）、Fiber 类（effect 管理、epoch 状态机、_reload/_unload）、CordisError、ValidationError |
| events.ts | L6-L178 | EventsService。5 种派发模式（emit/parallel/serial/bail/waterfall）、8 个内部事件、on/once 注册机制、filter 过滤 |
| service.ts | L5-L80 | Service\<T\> 抽象基类。7 个静态 symbol、createCallable 支持、isolate 过滤、resolveConfig 配置合并、自定义 instanceof |
| reflect.ts | L61-L281 | ReflectService 及 Proxy handler。get/set/has 拦截、provide/accessor/mixin、notify 服务变更通知、bind traceable 回调 |
| registry.ts | L11-L214 | RegistryService 插件注册 + @Inject 装饰器。Plugin 三形态（Function/Constructor/Object）、Inject.resolve、plugin/inject API |
| logger.ts | L18-L246 | LoggerService 可调用服务。LoggerLevel 枚举、printf 格式化、ANSI 颜色哈希、buffer exporter、Exporter 接口 |
| utils.ts | L4-L278 | 工具层。DisposableList、17 个 symbols、isConstructor、joinPrototype、createTraceable/createShadow/createCallable、composeError 长栈追踪 |
| index.ts | L1-L7 | 包入口，re-export 7 个模块（不含 reflect 模块，通过 Context 接口扩展暴露） |

### 加载器（loader）

| 文件 | 行级引用 | 内容 |
|------|---------|------|
| loader/index.ts | L47-L165 | Loader 主类（继承 EntryTree）。ModuleLoader 集成、unwrapExports、internal/update 事件处理、exit/locate/showLog |
| loader/internal.ts | L50-L123 | Node.js 内部 ESM ModuleLoader 封装。兼容 Node 22/23（v1）和 Node 24+（v2）两个版本 API |
| loader/config/tree.ts | L6-L123 | EntryTree 抽象类。层级 ID（`:` 分隔）管理、create/remove/update/resolve/import、cordis: 协议支持 |
| loader/config/entry.ts | L34-L173 | Entry 配置条目。动态 import、fiber 创建、配置插值、patch-context 流程 |
| loader/config/group.ts | L5-L88 | EntryGroup 管理及 Group 插件。配置 diff 与增量更新、internal/update 响应 |
| loader/config/isolate.ts | L25-L169 | Realm 隔离机制。LocalRealm（`#entryId`）、GlobalRealm（`@label`）、isolate map 生成与服务重绑定 |

### 扩展服务

| 文件 | 行级引用 | 内容 |
|------|---------|------|
| hmr/index.ts | L49-L403 | Hmr Service（@Inject('loader') @Inject('timer')）。chokidar 监听、analyzeChanges 分类 accepted/declined、partialReload 缓存备份/回滚 |
| include/index.ts | L48-L219 | Include Service（extends EntryTree）。YAML/JSON 读写、patch 机制（id 定位 + insert/override）、debounce 写入 |
| timer/index.ts | L11-L141 | TimerService（extends Service）。timeout/interval 双模式（回调/Promise/AsyncIterable）、throttle/debounce、ctx.mixin 注入 |
| logger-console/shared.ts | L24-L94 | ConsoleExporter。时间戳、彩色标签、宽度/对齐、时间差、util.inspect 格式化 |

### 工具与脚手架

| 文件 | 内容 |
|------|------|
| create/index.ts | Scaffold 脚手架类：模板下载、stageYarnBin Yarn 版本管理、package.json 写入、git init、依赖安装 |
| utils/index.ts | List\<T\> 可清理列表：基于 effect 的 push/filter/map/iterator |

## 核心类索引

### Context

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `constructor()` | 构造函数 | context.ts:L36-L49 | 返回 Proxy 对象，初始化 root Fiber 和 4 个内置 Service |
| `static effect/filter/isolate/intercept` | symbol | context.ts:L22-L25 | 4 个静态只读 symbol，通过 `Symbol.for('cordis.xxx')` 注册 |
| `static is(value)` | 方法 | context.ts:L27-L34 | 类型守卫，检查 `value[Context.is]` |
| `root` | 属性 | context.ts:L13 | 指向根 Context Proxy（自身） |
| `events/logger/reflect/registry` | 内置服务 | context.ts:L15-L18 | 4 个内置 Service 属性 |
| `fiber` | 属性 | fiber.ts:L10 | 当前 Fiber 实例（通过 module augmentation 声明） |
| `extend(meta)` | 方法 | context.ts:L55-L63 | 创建继承当前 context 的新 Context，复制 meta 属性描述符 |
| `isolate(name, label?)` | 方法 | context.ts:L65-L69 | 创建服务隔离域，新 symbol 或共享 label |
| `intercept(name, config)` | 方法 | context.ts:L71-L77 | 覆盖服务配置拦截 |
| `[inspect.custom]()` | 方法 | context.ts:L51-L53 | Node.js inspect 输出 `Context <name>` |

### Fiber

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `uid` | 属性 | fiber.ts:L104 | 唯一 ID，root=0，dispose 后=null |
| `ctx` | 属性 | fiber.ts:L105 | Fiber 所属的 Context（带 fiber: this 扩展） |
| `config` | 属性 | fiber.ts:L106 | 插件配置 |
| `state` | 属性 | fiber.ts:L107 | FiberState 枚举值 |
| `dispose` | 属性 | fiber.ts:L108 | 异步清理函数 |
| `store` | 属性 | fiber.ts:L109 | 服务实现存储（激活时） |
| `inertia` | 属性 | fiber.ts:L110 | 加载/卸载惯性操作 Promise |
| `runtime` | 属性 | fiber.ts:L126 | Plugin.Runtime（插件注册信息） |
| `parent` | 属性 | fiber.ts:L123 | 父 Context |
| `name` | getter | fiber.ts:L215-L222 | fiber 名称（沿链查找 runtime.name，root 返回 'root'） |
| `effect(execute, label?)` | 方法 | fiber.ts:L275-L340 | 核心效果管理，返回 AsyncDisposable（函数+PromiseLike） |
| `restart()` | 方法 | fiber.ts:L468-L474 | 重启 fiber（卸载→重新检查依赖→激活） |
| `update(config, noSave?)` | 方法 | fiber.ts:L476-L485 | 更新配置并重启 |
| `await()` | 方法 | fiber.ts:L460-L466 | 等待惯性操作完成 |
| `assertActive()` | 方法 | fiber.ts:L224-L227 | uid 为 null 时抛 INACTIVE_EFFECT |
| `getEffects()` | 方法 | fiber.ts:L342-L346 | 获取所有已注册效果的元信息 |

#### FiberState 状态枚举

| 状态 | 值 | 说明 |
|------|-----|------|
| `PENDING` | 0 | 等待中（依赖未满足） |
| `LOADING` | 1 | 加载中（执行插件回调） |
| `ACTIVE` | 2 | 已激活（正常运行） |
| `FAILED` | 3 | 失败（执行出错） |
| `DISPOSED` | 4 | 已销毁（uid=null） |
| `UNLOADING` | 5 | 卸载中（清理 disposables） |

### EventsService

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `emit(name, ...args)` | 方法 | events.ts:L96-L99 | 同步顺序派发，异常立即抛出 |
| `parallel(name, ...args)` | 方法 | events.ts:L89-L94 | Promise.allSettled 并行，AggregateError 收集异常 |
| `serial(name, ...args)` | 方法 | events.ts:L101-L107 | 异步顺序执行，遇 bail 值提前返回 |
| `bail(name, ...args)` | 方法 | events.ts:L109-L115 | 同步顺序执行，遇 bail 值提前返回 |
| `waterfall(name, ...args)` | 方法 | events.ts:L117-L126 | 中间件模式，最后参数为 next 函数 |
| `on(name, listener, options?)` | 方法 | events.ts:L144-L158 | 注册事件监听，返回 dispose 函数 |
| `once(name, listener, options?)` | 方法 | events.ts:L160-L166 | 注册一次性监听 |
| `_hooks` | 属性 | events.ts:L46 | 按事件名组织的 Hook 列表 |

#### 内置内部事件

| 事件名 | 签名 | 说明 |
|--------|------|------|
| `internal/plugin` | `(fiber: Fiber) => void` | Fiber 创建/销毁 |
| `internal/status` | `(fiber: Fiber, oldState: FiberState) => void` | Fiber 状态变更 |
| `internal/service` | `(name: string, value: any) => void` | 服务注册/注销 |
| `internal/update` | `(config, noSave, next) => void` | 配置更新（waterfall 中间件链） |
| `internal/get` | `(ctx, name, error, next) => any` | 属性获取拦截 |
| `internal/set` | `(ctx, name, value, error, next) => boolean` | 属性设置拦截 |
| `internal/listener` | `(name, listener, options) => void` | 监听器注册拦截 |
| `internal/dispatch` | `(mode, name, args, thisArg) => void` | 事件派发通知 |

### Service\<T\>

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `constructor(ctx, name)` | 构造函数 | service.ts:L18-L35 | 注册服务到 reflect，支持 callable（invoke symbol） |
| `static init/check/config/invoke/extend/tracker/resolveConfig` | symbol | service.ts:L6-L12 | 7 个静态 symbol 属性 |
| `ctx` | 属性 | service.ts:L18 | 服务注册时的 Context |
| `name` | 属性 | service.ts:L16 | 服务名称 |
| `[symbols.filter](ctx)` | 方法 | service.ts:L37-L39 | isolate 域过滤：同一域内 context 可见 |
| `[symbols.resolveConfig](base?, head?)` | 方法 | service.ts:L51-L67 | 沿原型链收集 intercept 配置并 merge |
| `[symbols.extend](props?)` | 方法 | service.ts:L41-L49 | 创建服务扩展副本 |
| `static [Symbol.hasInstance]` | 方法 | service.ts:L69-L79 | 自定义 instanceof（处理 Proxy 场景） |

### ReflectService

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `static handler` | ProxyHandler | reflect.ts:L62-L133 | Context 的 Proxy 处理器（get/set/has 拦截） |
| `store` | 属性 | reflect.ts:L135 | 以 isolate symbol 为 key 存储 Impl |
| `props` | 属性 | reflect.ts:L136 | 所有声明的属性（service/accessor 类型） |
| `provide(name, value?, check?)` | 方法 | reflect.ts:L175-L203 | 注册服务，返回 dispose 函数 |
| `get(name, strict?)` | 方法 | reflect.ts:L150-L152 | 获取服务实现（traceable 包装） |
| `set(name, value, error?)` | 方法 | reflect.ts:L162-L173 | 设置服务值 |
| `accessor(name, options)` | 方法 | reflect.ts:L229-L237 | 声明计算属性 |
| `mixin(source, mixins)` | 方法 | reflect.ts:L239-L265 | 将服务方法/属性混合到 Context |
| `notify(names, filter?)` | 方法 | reflect.ts:L205-L227 | 通知依赖 fiber 刷新并触发 internal/service 事件 |
| `bind(callback)` | 方法 | reflect.ts:L271-L280 | 创建 traceable 回调 Proxy |
| `trace(value)` | 方法 | reflect.ts:L267-L269 | 将值包装为 traceable 对象 |

### RegistryService

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `plugin(plugin, config?, getOuterStack?)` | 方法 | registry.ts:L193-L213 | 注册插件，创建 Fiber & PromiseLike 包装 |
| `inject(deps, callback)` | 方法 | registry.ts:L189-L191 | 注入依赖的简写形式 |
| `get/has/delete/keys/values/entries/forEach` | Map API | registry.ts:L152-L187 | 运行时注册表 Map 风格操作 |
| `resolve(plugin)` | 方法 | registry.ts:L144-L150 | 将 Plugin 解析为 callback 函数 |
| `counter` | getter | registry.ts:L136-L138 | 自增生成 uid |

### LoggerService

| 成员 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `(name?)` | 调用签名 | logger.ts:L226-L237 | 可调用对象，返回 Logger 实例 |
| `error/info/warn/debug` | 方法 | logger.ts:L240-L244 | 直接调用等价于 `logger()[type](...args)` |
| `exporter(exporter)` | 方法 | logger.ts:L206-L212 | 注册日志导出器 |
| `buffer/bufferSize` | 属性 | logger.ts:L171-L172 | 内置环形缓冲区（默认 1000 条） |
| `exporters` | 属性 | logger.ts:L177 | 已注册导出器 Map |

### 错误类型

| 类 | 继承 | 定义位置 | 说明 |
|----|------|---------|------|
| `CordisError` | Error | fiber.ts:L87-L99 | 框架错误，含 code 字段；唯一错误码 `INACTIVE_EFFECT` |
| `ValidationError` | TypeError | fiber.ts:L16-L32 | 配置验证失败，通过 @standard-schema/spec 验证 |

## 装饰器与 API 列表

### 装饰器

| 装饰器 | 定义位置 | 适用目标 | 说明 |
|--------|---------|---------|------|
| `@Inject(name, config?)` | registry.ts:L17-L40 | class / class method | 类装饰器：将依赖注入添加到静态 inject 属性（支持原型链继承）；方法装饰器：通过 initHooks 在实例化后注册 ctx.inject 回调 |

### Context API（通过 mixin 注入的方法）

以下方法通过 `reflect.mixin()` 混合到 Context 原型上，可直接在 ctx 上调用：

| API | 来源服务 | 签名 | 说明 |
|-----|---------|------|------|
| `ctx.effect()` | Fiber | `(execute: () => Effect, label?: string) => AsyncDisposable` | 注册效果，返回可取消的 dispose 函数 |
| `ctx.on()` | Events | `(name, listener, options?) => () => boolean` | 注册事件监听器 |
| `ctx.once()` | Events | `(name, listener, options?) => () => boolean` | 注册一次性事件监听器 |
| `ctx.emit()` | Events | `(name, ...args) => void` | 同步事件派发 |
| `ctx.parallel()` | Events | `(name, ...args) => Promise<void>` | 并行事件派发 |
| `ctx.serial()` | Events | `(name, ...args) => Promisify<R>` | 异步顺序派发 |
| `ctx.bail()` | Events | `(name, ...args) => R` | 同步带返回值派发 |
| `ctx.waterfall()` | Events | `(name, ...args) => R` | 中间件模式派发 |
| `ctx.plugin()` | Registry | `(plugin, config?) => Fiber & PromiseLike<Fiber>` | 注册插件 |
| `ctx.inject()` | Registry | `(deps, callback) => Fiber & PromiseLike<Fiber>` | 依赖注入简写 |
| `ctx.get()` | Reflect | `(name, strict?) => any` | 获取服务 |
| `ctx.set()` | Reflect | `(name, value) => void` | 设置服务值 |
| `ctx.provide()` | Reflect | `(name, value?, check?) => () => void` | 提供服务 |
| `ctx.accessor()` | Reflect | `(name, options) => void` | 声明计算属性 |
| `ctx.mixin()` | Reflect | `(source, mixins) => void` | 混入方法到 Context |
| `ctx.logger(name?)` | Logger | `(name?) => Logger` | 获取 Logger 实例（callable） |
| `ctx.extend(meta)` | Context | `(meta?) => Context` | 扩展 Context |
| `ctx.isolate(name, label?)` | Context | `(name, label?) => Context` | 创建隔离域 |
| `ctx.intercept(name, config)` | Context | `(name, config) => Context` | 覆盖服务配置 |

### TimerService API（通过 mixin 注入到 Context）

| API | 签名 | 说明 |
|-----|------|------|
| `ctx.timeout()` | `(callback, delay) => () => void` 或 `(delay) => Promise<void>` | 延时执行，支持回调或 Promise 模式 |
| `ctx.interval()` | `(callback, delay) => () => void` 或 `(delay) => AsyncIterableIterator<void>` | 定时执行，支持回调或 AsyncIterable 模式 |
| `ctx.throttle()` | `(callback, delay, noTrailing?) => F & { dispose }` | 节流包装 |
| `ctx.debounce()` | `(callback, delay) => F & { dispose }` | 防抖包装 |
| `ctx.setTimeout()` | *deprecated* | 同 `ctx.timeout()` |
| `ctx.setInterval()` | *deprecated* | 同 `ctx.interval()` |

### Plugin 类型

| 形态 | 签名 | 说明 |
|------|------|------|
| `Plugin.Function` | `(ctx: Context, config: T) => any` | 函数式插件 |
| `Plugin.Constructor` | `new (ctx: Context, config: T) => any` | 类式插件（支持 `[Service.init]()` 生命周期钩子） |
| `Plugin.Object` | `{ apply(ctx: Context, config: T): any }` | 对象式插件（含 apply 方法） |

插件可选属性：`name?`、`Config?`（StandardSchemaV1）、`inject?`、`provide?`、`intercept?`。

### Symbols 总览（17 个）

| 类别 | Symbol | 注册名 | 用途 |
|------|--------|--------|------|
| 内部 | `shadow` | `cordis.shadow` | Shadow context 标记 |
| 内部 | `caller` | `cordis.caller` | Traceable 调用者 |
| 内部 | `receiver` | `cordis.receiver` | Proxy receiver |
| 内部 | `original` | `cordis.original` | Traceable 原始目标 |
| 内部 | `metadata` | `cordis.metadata` | 装饰器元数据存储 |
| 内部 | `initHooks` | `cordis.initHooks` | @Inject 方法初始化钩子 |
| 内部 | `checkProto` | `cordis.checkProto` | Inject 原型链标记 |
| 上下文 | `effect` | `cordis.effect` | Effect 元信息标记 |
| 上下文 | `filter` | `cordis.filter` | 事件/服务过滤 |
| 上下文 | `isolate` | `cordis.isolate` | 服务隔离 map |
| 上下文 | `intercept` | `cordis.intercept` | 服务配置拦截 map |
| 服务 | `init` | `cordis.init` | 服务初始化钩子 |
| 服务 | `check` | `cordis.check` | 服务可用性检查 |
| 服务 | `config` | `cordis.config` | 服务配置类型标记 |
| 服务 | `invoke` | `cordis.invoke` | 可调用服务的调用签名 |
| 服务 | `extend` | `cordis.extend` | 服务扩展方法 |
| 服务 | `tracker` | `cordis.tracker` | Traceable 行为配置 |
| 服务 | `resolveConfig` | `cordis.resolveConfig` | 配置解析方法 |

### EventOptions

| 属性 | 类型 | 说明 |
|------|------|------|
| `prepend?` | `boolean` | 插入钩子列表头部 |
| `global?` | `boolean` | 全局事件（不受 filter 过滤） |

### Tracker 接口

| 属性 | 类型 | 说明 |
|------|------|------|
| `associate?` | `string` | 关联服务名前缀（service.prop 委托） |
| `property?` | `string` | 注入的 ctx 属性名（如 'ctx'） |
| `noShadow?` | `boolean` | 禁止 shadow 包装 |

### Effect 类型

Effect 支持以下形式作为 `fiber.effect()` 和插件回调的返回值：

| 类型 | 说明 |
|------|------|
| `() => void \| Promise<void>` | 同步/异步 dispose 函数 |
| `Iterable<Disposable>` | Generator 产出 dispose 函数 |
| `Promise<Disposable>` | 异步 resolve 为 dispose 函数 |
| `AsyncIterable<Disposable>` | AsyncGenerator 产出 dispose 函数 |

### 构建与运行命令

| 命令 | 说明 |
|------|------|
| `yarn build` | yakumo esbuild + tsc 构建 |
| `yarn test` | vitest 测试（需 `--expose-internals`） |
| `yarn lint` | ESLint 检查 |
| `node --expose-internals bin.js` | CLI 启动（core 包） |

### Loader 扩展事件

| 事件名 | 签名 | 说明 |
|--------|------|------|
| `exit` | `(signal: NodeJS.Signals) => Promise<void>` | 进程退出 |
| `loader/config-update` | `() => void` | 配置文件更新 |
| `loader/entry-init` | `(entry: Entry) => void` | Entry 初始化 |
| `loader/partial-dispose` | `(entry, legacy, active) => void` | Entry 部分销毁 |
| `loader/patch-context` | `(entry, next) => void` | Context 补丁（isolate 配置） |

### HMR 扩展事件

| 事件名 | 签名 | 说明 |
|--------|------|------|
| `hmr/change` | `(url: string) => void` | 文件变更（非框架/非模块/非配置） |
| `hmr/reload` | `(reloads: Map<Plugin, Reload>) => void` | 热重载完成 |

## 测试文件索引

| 测试文件 | 覆盖范围 |
|---------|---------|
| fiber.spec.ts | Fiber 生命周期、effect 管理 |
| events.spec.ts | 事件派发（5 种模式） |
| plugin.spec.ts | 插件注册、三形态支持 |
| service.spec.ts | Service 抽象、依赖注入 |
| reflect.spec.ts | Reflect 代理、provide/accessor/mixin |
| isolate.spec.ts | 服务隔离域 |
| shadow.spec.ts | Shadow context 机制 |
| dispose.spec.ts | 清理与资源释放 |
| decorator.spec.ts | @Inject 装饰器 |
| invoke.spec.ts | 可调用服务（invoke symbol） |
| associate.spec.ts | Tracker associate 属性委托 |
| logger.spec.ts | 日志系统 |
