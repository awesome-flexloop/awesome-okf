---
type: spec
scope: deepagents
name: insights
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents 深度洞察——从源码中提炼的架构决策、中间件机制与设计约束
---

# deepagents 深度洞察

## 1. 三层栈定位：不发明运行时，只组装最佳实践

Deep Agents 最核心的架构决策是**不引入新的代理运行时**。它明确地将自身定位为 LangChain `create_agent()` 之上的"opinionated harness"（[F-062](/langchain-ai/deepagents/concepts/overview)）：

```
Deep Agents      opinionated harness: defaults, middleware, backends, profiles
LangChain        agent abstraction: model + tools + middleware -> agent loop
LangGraph        runtime: state, checkpoints, streaming, interrupts
```

这意味着 `create_deep_agent()` 的本质是一个**组装函数**，而非新的图执行引擎。它完成六步组装（[F-063](/langchain-ai/deepagents/concepts/overview)）：解析模型 → 解析后端 → 组装中间件栈 → 构建子代理 → 组合系统提示 → 委托给 `langchain.agents.create_agent()`。最终返回的仍是标准的 `CompiledStateGraph`（[F-012](/langchain-ai/deepagents/references/api)）。

这一决策的深远影响是：任何 LangGraph 图都可以作为 `CompiledSubAgent` 的 `runnable` 传入（[F-018](/langchain-ai/deepagents/concepts/planning-subagents)），自定义编排可以与 harness 默认值并排插拔。Deep Agents 不锁定用户——它只是把长周期代理最常用的零件预先打包好。

## 2. 中间件即能力：模型调用前后的可编程拦截点

Deep Agents 的所有核心能力——文件系统、子代理、摘要压缩、技能、内存、人工审批——都通过 `AgentMiddleware` 实现，而非普通工具函数（[F-014](/langchain-ai/deepagents/references/middleware-stack)）。这是理解整个系统的关键。

中间件与普通工具的本质区别在于 `wrap_model_call()` 钩子，它在**每次 LLM 请求发送前**拦截调用，能够：

- **动态过滤工具**：如 `FilesystemMiddleware` 在后端不支持 shell 时移除 `execute` 工具
- **注入系统提示上下文**：如 `MemoryMiddleware` 和 `SkillsMiddleware` 在每次调用时注入指令
- **变换消息**：如 `SummarizationMiddleware` 计数 token、截断旧工具参数、在上下文窗口填满时替换历史为摘要
- **维护跨轮状态**：中间件可读写在代理轮次间持久化的类型化状态字典

中间件栈有严格的三段式排序（[F-014](/langchain-ai/deepagents/references/middleware-stack)）：基础脚手架在前，用户中间件在中，profile/缓存/内存/审批尾部在后。`_apply_custom_middleware()` 按名称匹配替换——如果用户中间件的 `.name` 与基础栈中的同名，则原地替换保留顺序；否则插入到最后一个核心中间件之后、尾部之前（[graph.py:201-235](d:/spaces/SpecWeave/external/libs/ai/langchain-ai/deepagents/libs/deepagents/deepagents/graph.py)）。

`FilesystemMiddleware` 和 `SubAgentMiddleware` 被标记为 `_REQUIRED_MIDDLEWARE`，不可通过 profile 排除（[F-011](/langchain-ai/deepagents/references/middleware-stack)），因为前者支撑所有内置文件工具和权限强制执行，后者支撑 `task` 工具。这是安全保证而非便利性约束。

## 3. 子代理的上下文隔离与状态传播

子代理系统是 Deep Agents 解决"长任务上下文污染"的核心机制。其设计有三个精妙之处：

**隔离的上下文窗口**：每个子代理调用是无状态的——它只看到父代理通过 `description` 参数传入的提示，返回一条最终报告（[F-021](/langchain-ai/deepagents/concepts/planning-subagents)）。子代理的中间工作、工具结果和状态跟踪对父代理不可见。`_EXCLUDED_STATE_KEYS` 集合排除 `messages`、`todos`、`structured_response`（[F-020](/langchain-ai/deepagents/concepts/planning-subagents)），中间件私有字段也被剥离。

**三种形态统一入口**：`SubAgent`（声明式，自动编译）、`CompiledSubAgent`（预编译 runnable）、`AsyncSubAgent`（远程/后台）通过同一个 `task` 工具暴露（[F-017](/langchain-ai/deepagents/concepts/planning-subagents)、[F-024](/langchain-ai/deepagents/concepts/planning-subagents)）。`create_deep_agent()` 在处理 `subagents` 参数时，通过检查 `"graph_id"` 和 `"runnable"` 键来区分类型（[graph.py:647-655](d:/spaces/SpecWeave/external/libs/ai/langchain-ai/deepagents/libs/deepagents/deepagents/graph.py)）。

**默认通用子代理**：如果调用者未提供名为 `"general-purpose"` 的子代理，系统自动添加一个（[F-019](/langchain-ai/deepagents/concepts/planning-subagents)），它拥有与主代理相同的工具集，用于复杂的上下文密集型搜索任务。可通过 `GeneralPurposeSubagentProfile(enabled=False)` 禁用。

lca-deepagents 的 Sales Assistant 示例展示了关键安全模式（[F-061](/langchain-ai/deepagents/examples/lca-variant)）：受审批控制的工具**仅**放在有门控的专业子代理上，绝不放在主代理上。因为通用子代理继承主代理工具——如果主代理有 `add_customer`，通过 `task` 委派即可绕过审批。

## 4. 后端抽象与 DeltaChannel：持久化的两个维度

Deep Agents 的状态持久化设计分为两个正交维度：

**图状态（LangGraph 层）**：`DeepAgentState` 在 `AgentState` 基础上对 `messages` 字段使用 `DeltaChannel(_messages_delta_reducer, snapshot_frequency=50)`（[F-009](/langchain-ai/deepagents/references/api)），将长线程的检查点增长从 O(N²) 降至 O(N)。每50条消息生成一次快照，中间以增量存储。

**文件/内存持久化（后端层）**：`BackendProtocol` 定义统一的文件操作接口（[F-038](/langchain-ai/deepagents/references/backends)），有七种内置实现（[F-037](/langchain-ai/deepagents/references/backends)）：

| 后端 | 用途 |
|---|---|
| `StateBackend` | 默认，线程作用域的内存存储 |
| `FilesystemBackend` | 磁盘文件系统 |
| `CompositeBackend` | 按路径路由到多个后端 |
| `StoreBackend` | LangGraph BaseStore 持久化 |
| `LocalShellBackend` | 本地 shell 执行 |
| `LangSmithSandbox` | LangSmith 托管沙箱 |
| `ContextHubBackend` | 上下文中心存储 |

`execute` 工具仅在后端实现 `SandboxBackendProtocol` 时可用（[F-041](/langchain-ai/deepagents/references/backends)），非沙箱后端返回错误消息。这是"信任 LLM"安全模型的体现——安全边界在工具/沙箱层，而非期望模型自我约束（README 第112行）。

摘要压缩的卸载策略也值得注意：旧消息通过 LLM 摘要后，完整历史以 Markdown 写入 `/conversation_history/{session_id}.md`，Base64 媒体单独存储并以 XML 引用标签引用（[F-031](/langchain-ai/deepagents/concepts/todo-context)）。`DEEPAGENTS_DEFAULT_SUMMARY_PROMPT` 专门注入媒体引用说明，确保摘要模型保留这些标签（[F-032](/langchain-ai/deepagents/concepts/todo-context)）。

## 5. Profile 系统：模型特化的正交调优

Harness Profile 是一个容易被忽视但架构意义重大的设计。它在模型构造**之后**介入，正交于 `ProviderProfile`（控制模型构造阶段）（[F-042](/langchain-ai/deepagents/references/profiles)）。

Profile 可以调整：系统提示组装（`base_system_prompt`、`system_prompt_suffix`）、工具可见性（`excluded_tools`、`tool_description_overrides`）、中间件裁剪（`excluded_middleware`、`extra_middleware`）、默认子代理行为（`general_purpose_subagent`）。内置 profile 覆盖 Anthropic Sonnet/Opus/Haiku、NVIDIA Nemotron、OpenAI Codex 等模型。

关键约束是 `excluded_middleware` 不能排除脚手架中间件（[F-011](/langchain-ai/deepagents/references/middleware-stack)），且匹配不到任何中间件的排除项会引发 `ValueError`——这防止了拼写错误和过时配置静默降级代理能力。
