---
type: Concept
title: "OpenCode 2.0.32 模型、工具与扩展机制"
description: "区分 Agent 与 Provider 服务、模型流、本地工具执行、MCP 权限检查及插件宿主边界"
tags: [opencode, provider, tool, mcp, plugin, permission, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T12:01:30+08:00 }
verified: { by: "process:seven-concepts-e", at: 2026-10-20T12:01:30+08:00 }
status: draft
stale_after: 2027-04-20
sources:
  - id: opencode-source-map-2.0.32
    resource: /references/source-code-map-2.0.32.md
    title: OpenCode 2.0.32 固定源码地图
---

# OpenCode 2.0.32 模型、工具与扩展机制

在 OpenCode 2.0.32 中，“模型给出工具调用”“本地运行时执行工具”和“扩展服务被宿主装配”是不同边界。读代码时应把 Agent/Provider 的服务接口、LLM stream、工具 schema 与执行、Permission、MCP 和 Plugin host 分开追踪，再沿会话 runner 的调用点把它们连起来。（F-086～F-092、F-097）

本篇只描述固定 commit `6ec56821d63100fe5bda45b759364f561c56b359` 中有事实支持的接口和路径；并不声称已通读每个 provider adapter、插件或工具实现。

## Agent 与 Provider 服务

`Agent.Interface` 声明 `get`、`resolve`、`select` 与 `list`；`Provider.Interface` 声明 `get`、`all`、`available` 与 `snapshot`。两者通过各自的 service node 注册，并依赖相应的服务上下文。因而它们不是可随意替换名称的同一类“模型配置对象”，而是核心服务层中职责不同的接口。（F-086、F-087）

Provider 包加载路径也有明确分支：`loadPackage` 先检查内置包映射，再尝试模块解析；如果解析失败且没有 `npm` 接口，会返回 `LoadError`；若提供 `npm` 接口，则调用 `npm.add(root)` 后再解析和加载模块。描述 Provider 扩展时应保留这一路径条件，不要简写为“未安装时总会自动安装”。（F-088）

## 工具定义与本地执行边界

会话 step 消费 `llm.stream` 产生的事件。对非 provider 执行的 `tool-call`，runner 创建本地工具执行 fiber，并在流结束后等待该 fiber。这个判断点很关键：流里出现工具调用并不意味着 provider 已完成本地副作用。（F-097）

`tool/runtime.ts` 在执行前解码工具输入；若工具声明了 output schema，却未提供 `output`，运行时会产生工具错误；返回值则经输出 schema 编码。由此可见，schema 不只是给模型展示的描述文本，也是 runtime 输入与结果处理路径的一部分。（F-090）

## MCP 与权限检查

MCP 工具发现后会获得 namespace、description、输入与输出 schema；MCP 工具执行路径调用 `permission.assert(...)`。另一个层次的通用 Permission 评估逻辑会展平规则集，寻找最后一条同时匹配 action 与 resource 的规则；没有匹配时返回 `effect: "ask"` 的规则。（F-089、F-091）

这意味着阅读权限行为时要区分规则匹配函数与具体工具调用路径：前者描述如何选择匹配结果，后者说明 MCP 调用会进入断言。不能仅根据模型可见的工具名称推断其授权结果，也不能把上述事实推广到本轮未深读的每一种工具。

## Plugin host 与存储命名空间

`PluginHost.make` 从 Effect Context 获取 Agent、Provider、Model、MCP、Tool、Permission、Session、Worktree 等服务。插件存储前缀不是简单地拼接原始 plugin ID：实现会把 ID 中各 UTF-16 code unit 转为四位十六进制字符串，再与 `plugin:` 前缀及结尾冒号组合。（F-092）

这个编码细节说明扩展边界不仅是“加载插件”的入口，也包括服务上下文与插件存储隔离的实现约定。需要复核具体实现时，应直接查看固定源码中的 [Plugin host](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin/host.ts)，不要从插件 ID 的可读形式猜测持久化键名。

## 读码顺序与覆盖限制

建议从会话生命周期篇定位 runner 的 `tool-call` 分支，再依次检查 `tool/runtime.ts`、MCP 执行路径、Permission 评估逻辑和 Plugin host。这样可以分辨接口声明、调度时机和副作用执行，而不会把多个层次折叠成“模型直接调用工具”。（F-089～F-097）

上述覆盖来自代表性源码文件，不代表已审查全部工具、Provider、MCP server 或插件。包级覆盖等级和未深读边界见[workspace 覆盖矩阵](/spec/facts-2.0.32.md)；版本坐标及源码入口见[固定源码地图](/references/source-code-map-2.0.32.md)。

## 相关概念

- [OpenCode Monorepo 包地图](/concepts/05-monorepo-package-map.md)
- [会话执行生命周期](/concepts/06-session-execution-lifecycle.md)
- [Protocol、Server、Client 与 SDK 边界](/concepts/08-protocol-server-client-sdk.md)
