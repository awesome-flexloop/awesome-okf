---
type: Concept
title: "OpenCode 插件契约、加载与生命周期"
description: "从公开Schema追到managed policy、激活后缀重建与Scope释放"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, schema, plugin, scope]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 插件契约、加载与生命周期

读插件需要区分公开信息、加载检查和运行资源释放。本篇深化[模型与工具扩展](07-model-tool-extensibility.md)，只覆盖固定`2.0.32`的代表性插件链，不重复Provider/MCP概述。事实依据为[F-131～F-135](../spec/facts-deepening-2.0.32.md)。

## 公开信息不是加载实现

`Plugin.Info`公开source、features与state，state为active/failed；`plugin.updated`是data为空对象的ephemeral event。这里表达可见信息和通知，不足以推导重载顺序、重试策略或插件已完成哪些副作用。（F-131）

事件定义还有独立版本语义：`Event.latest`按durable version选择最新，歧义重复抛错；`durableMap`只收durable事件，以`type.version`为键，拒绝重复。不要把所有事件都当作持久事件，或从名称相同推断版本选择。（F-132）

## Effect与Promise两种契约怎样释放

以下为源码接口节选，不是本轮运行过的插件：

```ts
export interface Plugin<R = Scope.Scope> {
  readonly id: string
  readonly effect: (context: Context) => Effect.Effect<void, never, R>
}
```

Promise接口的`setup(context)`返回Cleanup或void，也可返回其Promise。adapter以`Effect.acquireRelease`取得setup结果，释放时调用Cleanup，将Promise资源清理接入Effect Scope。两种表面API可以共用宿主生命周期，但不能把void返回当作存在显式cleanup。（F-133）

## 加载前先检查policy

`PluginModule`在模块读取或npm解析前检查`integration.use` managed policy。default导出需含string id及effect/setup函数；`install=false`且非本地无入口时返回pending。policy检查、模块结构检查、pending、最终active/failed不是同一阶段。（F-134）

读到permission工具调用规则并不等于已经解释插件加载许可；本路径的managed policy明确发生在模块加载前，应与工具执行权限分别定位。

## 激活列表保留前缀、重建后缀

`activate`保留id/revision相同的前缀，逆序关闭变化后缀，再顺序加载新后缀。相同失败revision不会仅因重排而重试；新revision可重试，健康fallback也有重新加载路径。这里的顺序和revision决定实际生命周期，不是“列表变化就全部重载”。（F-135）

Hook按注册顺序遍历，Scope finalizer或dispose移除注册。这解释了为什么判断重载是否干净，不能只看Info状态：还要核对旧Scope是否关闭、旧hook是否移除，以及失败时保留或恢复了什么。

## 源码导读顺序

1. 看schema plugin/event，识别外部可见状态及事件类型。
2. 看Effect/Promise插件签名及adapter，确认资源释放契约。
3. 看module的policy与default结构检查。
4. 看activate的prefix、revision、suffix关闭及fallback。
5. 看hooks的注册顺序与finalizer。

Event测试正文已读；Core module/plugin测试由只读研究片段对照并经主代理关键实现核验。本轮没有运行插件加载实验；其他领域Schema、完整插件生态及所有失败组合未穷尽。上述导读帮助读者建立验证问题，不构成插件代码可信或安全的通用证明。

## 相关概念

- [Protocol、Server、Client与SDK](08-protocol-server-client-sdk.md)
- [Codemode运行时边界](11-codemode-runtime-boundaries.md)
- [配置与上下文解析](10-config-context-resolution.md)
