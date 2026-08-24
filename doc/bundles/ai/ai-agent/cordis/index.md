---
okf_version: "0.2"
title: "Cordis"
description: "面向可组合插件应用的服务框架 - DI容器+Context原型链+Fiber生命周期的元框架"
tags:
  - ai-agent
  - framework
  - dependency-injection
  - plugin-architecture
  - typescript
  - service-locator
  - event-bus
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/cordis-lib/cordis
related:
  - "[[ai-agent-fundamentals]]"
  - "[[hermes-agent]]"
  - "[[zleap-agent]]"
  - "[[deepseek-harness]]"
---

# Cordis

Cordis 是面向可组合插件应用的服务框架（TypeScript实现），核心是Context依赖注入容器+Proxy代理构造、Fiber纤程生命周期六状态机（pending/loading/active/disposing/disposed/failed）、五种事件派发模式（emit/parallel/bubble/serial/waterfall）、Reflect元数据反射代理系统，以及Timer定时器服务。Hermes Agent、ZLEAP Agent、DeepSeek Harness等多个Agent框架均基于Cordis构建。

## 🧩 概念导航（Concepts）

### 核心机制
- [context-container](concepts/context-container.md) — Context容器：Proxy代理构造、插件注册、配置管理、Mixin混入、Isolate隔离、Effect追踪
- [service-registry](concepts/service-registry.md) — Service注册表：Service<T>抽象基类、@Inject装饰器、声明合并、name+inject+Config+apply契约
- [fiber-lifecycle](concepts/fiber-lifecycle.md) — Fiber生命周期：FiberState六状态机、epoch依赖驱动、effect效果管理、启动/停止/重启流程
- [reflect-metadata](concepts/reflect-metadata.md) — Reflect元数据系统：Proxy handler属性拦截、provide/accessor/mixin声明、Tracker追踪、traceable/shadow/callable包装

### 事件与插件
- [event-system](concepts/event-system.md) — 事件系统：5种dispatch模式（emit/parallel/bubble/serial/waterfall）、事件冒泡与过滤、中间件模式
- [plugin-module](concepts/plugin-module.md) — 插件模块系统：三形态（函数/类/对象）、Loader加载器、EntryTree配置树、Group分组、HMR热更新、Bundle组合
- [timer-scheduler](concepts/timer-scheduler.md) — 定时器与调度：setTimeout/setInterval双模式、throttle节流、debounce防抖、effect自动清理

## 🎯 示例导航（Examples）

- [create-basic-plugin](examples/create-basic-plugin.md) — 创建基础插件：Context.plugin、Service抽象类、@Inject装饰器的完整依赖注入流程
- [use-event-bus](examples/use-event-bus.md) — 使用事件总线：五种派发模式、事件监听注册、中间件和事件冒泡机制
- [build-bundle-app](examples/build-bundle-app.md) — 构建Bundle应用：Group组合多插件、插件依赖管理、Fiber状态机、isolate隔离、HMR热重载

## 📚 参考导航（References）

- [cordis-sources](references/cordis-sources.md) — Cordis 4.0.0-rc.8 源码路径、版本信息、核心模块、关键文件与API索引

## 🔗 关联 Bundle

- [hermes-agent](../hermes-agent/index.md) — Hermes Agent，Cordis的Python应用参考
- [zleap-agent](../zleap-agent/index.md) — ZLEAP Agent，Cordis的TypeScript深度应用
- [deepseek-harness](../deepseek-harness/index.md) — DeepSeek Harness，Cordis的Python应用参考
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与插件架构模式

---

> **信任声明**：本文档基于 Cordis 4.0.0-rc.8 源码逐模块分析，经 OKF 五阶段流程（R→I→E→V→C）生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：7 个概念 + 3 个示例 + 1 个信源 = 11 个内容文档

```{toctree}
:hidden:

concepts/context-container
concepts/event-system
concepts/fiber-lifecycle
concepts/plugin-module
concepts/reflect-metadata
concepts/service-registry
concepts/timer-scheduler
examples/build-bundle-app
examples/create-basic-plugin
examples/use-event-bus
references/cordis-sources
.spec/facts
```
