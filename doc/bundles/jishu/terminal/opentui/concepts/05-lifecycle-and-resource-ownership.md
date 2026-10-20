---
type: Concept
title: Renderer 生命周期与资源所有权
description: 明确应用、框架 root 和 renderer 各自的清理责任，建立覆盖正常退出与异常路径的终端关闭流程。
source: "OpenTUI lifecycle source and official documentation"
tags: [opentui, lifecycle, cleanup, renderer]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: source-code
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
  - id: official-docs
    resource: /references/official-documentation.md
    title: 官方文档
---

# Renderer 生命周期与资源所有权

OpenTUI renderer 会接管终端状态并维护输入、调度、native scene 与输出资源。生命周期设计的第一条规则是：创建 renderer 的应用代码负责关闭它。React root 或 Solid component tree 的卸载是框架层清理，不应被误认为 renderer 已经释放终端。

## Renderer 的创建与销毁

官方推荐用 `createCliRenderer()` 初始化终端。factory 返回后，renderer 的所有权属于调用方；正常退出、异常和初始化后取消等关闭路径都应到达 `renderer.destroy()`。官方文档将 `destroy()` 描述为同步且幂等，并说明它会停止 input 与 scheduling、恢复 OpenTUI 设置的终端模式。[Lifecycle](https://opentui.com/docs/core-concepts/lifecycle/) · [Quickstart](https://opentui.com/docs/getting-started/quickstart/)

若应用还需要等待 renderer 的输出传输完成，应根据生命周期文档使用 `closed` 信号，而不是在调用 `destroy()` 后立即结束进程或关闭宿主 stdout。终端 transport 和 native paint 是不同阶段；有自定义输出流时，需按其提交/交付方式处理。

## Framework root 不拥有 renderer

React `createRoot(renderer)` 接收已有 renderer，并创建 React root。调用 `root.unmount()` 会卸载 React tree，但 renderer 仍可继续使用；renderer destroy 会通知 reconciler 清理其 root。应用可选择先 unmount，让 effect cleanup 先发生，再销毁 renderer。[React lifecycle](https://opentui.com/docs/bindings/react/#lifecycle-and-cleanup)

Solid 的 `render()` 也把 Solid tree 连接到 OpenTUI host。无论 renderer 是调用方传入还是从配置创建，应用都应检查当前 render API 的生命周期契约，并在应用 shutdown 时完成 renderer teardown；不要仅凭函数返回值类型推断所有资源已关闭。[Solid lifecycle](https://opentui.com/docs/bindings/solid/)

## 应用创建的资源

Clipboard service、Tree-sitter client、SSH server 或其它异步资源可能由应用显式创建。这些服务不一定属于 renderer 的同步关闭责任。若服务提供异步 `destroy()`/`dispose()`，应在终端 session 关闭前等待它完成，尤其当服务仍持有 worker、I/O stream 或待完成请求时。具体 API 以各资源自己的官方 reference 为准。[Lifecycle and cleanup](https://opentui.com/docs/core-concepts/lifecycle/)

## 建议的 shutdown 顺序

1. 停止接受新应用操作，并取消定时器或外部请求。
2. 清理应用自己创建的异步 service，并等待其完成。
3. 如有必要，显式卸载 React/Solid root，使框架 effect cleanup 先运行。
4. 调用 `renderer.destroy()` 恢复终端并释放 renderer 资源。
5. 若输出通道要求等待完成，等待 `renderer.closed` 后再终止宿主进程。

完整行为需针对应用的 packages 与输出配置核对。避免把以上顺序误解成所有服务都是 renderer 自动创建或自动销毁。

## 相关概念

- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [React binding](/concepts/06-react-binding.md)
- [Solid binding](/concepts/07-solid-binding.md)
- [Core hello-terminal 示例](/examples/01-core-hello-terminal.md)
