---
type: concept
title: "Cordis 插件模型——Context / Service / Plugin / Fiber"
description: "dsh 的底层框架 Cordis：四个核心抽象、声明合并与依赖注入、五种事件派发模式、effect 副作用栈与 Fiber 六态生命周期。"
tags: [deepseek-harness, cordis, plugin, context, service, fiber, dependency-injection]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 docs/cordis-primer.zh.md 与 docs/cordis-tutorial
---

# Cordis 插件模型：Context / Service / Plugin / Fiber

dsh 把 Cordis 作为 vendored 依赖引入（发布名 `@deepseek-ai/cordis`，上游 `cordis 4.0.0-rc.7`），并带 22 条本地改动（fiber 重入释放加固、`!!js` 惰性配置解析等）。理解 Cordis 是理解 dsh 一切能力的前提。

## 1. 四个核心抽象

| 抽象 | 是什么 | 关键 API |
|---|---|---|
| **Context** | 代理对象，兼作根依赖容器与子容器 | `ctx.extend(meta?)`、`ctx.isolate(name, label?)`、`ctx.intercept(name, config)`、`ctx.get/set/provide/accessor`、`ctx.root`、`ctx.events`、`ctx.registry` |
| **Service** | 基类；子类在构造器 `super(ctx, name)` 时注册为 `ctx.<name>`，随 fiber 卸载移除 | 静态 `init/check/config/invoke/extend/tracker/resolveConfig` |
| **Plugin** | 功能模块，三种形态：函数 `apply(ctx)`、对象 `{name, inject, apply}`、类（`Service` 子类） | `inject`（硬依赖声明） |
| **Fiber** | 单个插件实例的运行时句柄 | `uid/ctx/config/state/dispose/store/inertia/name`、`effect()`、`await()`、`restart()`、`update(config)` |

> ⚠️ **Service 是 Cordis 的 class，不是 TypeScript 的 interface**——这是初读 Cordis 文档最容易踩的坑。

Fiber 状态机：`PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED`，另有 `FAILED`。

## 2. 声明合并与依赖注入

TypeScript 的**声明合并**是 Cordis 的类型安全机制，**纯编译期**，不生成任何接线：

```ts
declare module '@deepseek-ai/cordis' {
  interface Context { greeter: GreeterService }
  interface Events { 'stats/report'(name: string, count: number): void }
}
```

消费方需 `import type {} from './stats.ts'` 才能拿到合并结果。

**硬依赖**用 `inject` 声明：

```ts
export const inject = ['tools']
```

服务缺失时 fiber 保持 PENDING，既不输出也不崩溃；服务消失时依赖方被卸载，服务恢复后自动重载。可选依赖用 `ctx.get('x')` 探测。

```ts
ctx.inject(deps, cb)   // 等价于 ctx.plugin({ inject, apply: cb })
```

服务名共用**扁平命名空间**，因此自定义服务要加前缀——harness 已占用 `tools`、`llm`。

## 3. 五种事件派发模式

| 模式 | await | 顺序 | 返回值 | 调用 |
|---|---|---|---|---|
| `emit` | 否 | 注册序 | 否 | `ctx.emit` |
| `parallel` | 是 | 并行 | 否 | `await ctx.parallel` |
| `serial` | 是 | 注册序，首个非空返回值胜出并停止 | 是 | `await ctx.serial` |
| `bail` | 否 | serial 的同步版 | 是 | `ctx.bail` |
| `waterfall` | 否 | 环绕式中间件 | 是 | `ctx.waterfall` |

**瀑布纪律**：只观察/标注的监听器**必须调用 `next()`**，不调用即短路。dsh 的代表性 waterfall 是 `agent/request` 与 `approval/request`。

`parallel`/`emit`/`serial` 都支持 `thisArg` 重载，供作用域过滤使用。

## 4. effect：可逆副作用栈

`ctx.effect(execute, label?)`：

- `execute` 立即执行，收集到的 disposer 在"调用返回的 disposer"或"fiber 卸载"时**逆序**运行
- 重复调用是 no-op；fiber 已 dispose 时抛 `CordisError('INACTIVE_EFFECT')`
- disposer 可以是异步；多个异步 disposer **并发**运行（需要顺序须合并进同一 disposer）

已经是 effect 的常见操作：`ctx.on`、`ctx.plugin(child)`、服务注册、`ctx.tools.register`。

这一机制是"插件卸载即撤销"的实现基础。

## 5. 配置 schema

插件导出 `interface Config` 与同名 `const Config: Schema<Config> = Schema.object({...})`（Schemastery）。**导出普通对象作 `Config` 不工作**——Cordis 接受任意 Standard Schema 验证器。

- 默认值由 schema 填充
- 校验失败 → fiber FAILED + `ValidationError`
- `.volatile()` 字段支持"不重启即换值"

## 6. HMR：配置热重载

`dsh-hmr` 包提供配置热重载：

- 配置 `base`（默认 Context baseUrl）、`root`（默认 `["."]`，设为 `[]` 则只保留显式注册的配置监听）、`ignored`（默认 `["**/node_modules","**/.*","cache","data"]`）、`debounce`（100ms）
- `runExclusive()` 串行化配置变更、Loader 更新与自动重载；**包安装/删除在该队列之外**
- 文件比较用 inode/size/mtime，沿 ESM 链接与 CJS `children` 传播
- base 以 `root: []` 启用 HMR（仅当 profile 上下文存在时）；headless / SDK / ACP 在 YAML 中禁用它——保证一条 stdio 连接不会观察到依赖被替换

## 7. 为什么 dsh 选 Cordis

Cordis 的论文《A Programming Paradigm for Spatiotemporal Composability》提出：把"能力贡献"与"副作用撤销"变成一等公民。落到 dsh 上：

- **可组合**：任何能力都能被替换成另一个提供方
- **可撤销**：插件卸载时所有注册自动撤销，不留脏状态
- **可热更**：配置与模块的变更可以在运行中生效

## 下一步

- [Profile 与组合包](03-profile-and-bundle.md)——Cordis 配置树在 dsh 里如何被组装
- [写插件与组合包实战](../examples/03-custom-plugin-bundle.md)
- 姊妹束：[Cordis 元框架源码教程](../../cordis/index.md)
