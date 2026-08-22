---
type: Concept
title: Agent 核心循环
description: think-act-observe 循环的工程实现——从 ReAct 理论到生产级代码中的执行模式、错误恢复、中断处理与状态管理
tags: [ai-agent, agent-loop, react, execution, moa, tool-calling]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:15:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: hermes
    resource: /references/ai-agent-sources.md#hermes-agent
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: dsh
    resource: /references/ai-agent-sources.md#deepseek-harness
---

# Agent 核心循环

## 从 ReAct 到生产级循环

Agent 的核心是一个**感知-思考-行动**（Perceive-Think-Act）的循环，学术上称为 ReAct（Reasoning + Acting）范式。理论模型很简单：

```
while not done:
    observation = perceive(environment)
    thought = reason(observation, history)
    action = decide(thought)
    result = execute(action)
    history.append(observation, thought, action, result)
```

但在生产级框架中，这个循环需要处理大量工程问题：工具调用授权、并发执行、错误恢复、中断信号、上下文压缩、循环卫生检测、token 预算管理、多代理协调。本文档分析四个框架如何实现这个循环。

## hermes-agent：可配置的工具调用循环

hermes-agent 的核心循环由 `agent/loop.py` 和 `agent_init.init_agent()` 实现，`AIAgent` 类通过 75+ 参数控制循环行为。

### 循环结构

hermes-agent 的循环遵循以下步骤：

1. **构建消息**：将 system prompt、对话历史、工具定义组装为 LLM 请求
2. **LLM 推理**：调用模型获取响应（可能是文本回复或工具调用请求）
3. **处理响应**：
   - 如果是**文本回复**（无工具调用）→ 循环结束，返回结果
   - 如果是**工具调用**→ 进入工具执行阶段
4. **工具执行**：支持三种执行模式（见下文）
5. **工具结果注入**：将工具执行结果追加到消息历史
6. **继续循环**：回到步骤 1

### 三种工具执行模式

hermes-agent 支持三种工具执行模式，通过配置参数选择：

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| **并发（concurrent）** | 使用线程池并行执行所有工具调用 | 独立工具调用（如多个搜索） |
| **顺序（sequential）** | 按 LLM 返回顺序逐个执行 | 有依赖关系的工具调用 |
| **分段（segmented）** | 按类型分组执行（如先读文件后执行命令） | 需要权限分级的场景 |

### 安全与容错机制

- **授权门控（check_fn）**：工具执行前通过 `check_fn` 检查授权，支持 TTL 缓存和瞬态故障抑制
- **插件覆盖授权**：插件可以注册自定义授权逻辑
- **中断处理**：支持用户中断（Ctrl+C）和信号处理
- **循环卫生**：检测无限循环（重复相同工具调用）并自动中断
- **路径安全检查**：文件操作工具检查路径遍历攻击

## Zleap-Agent：三级状态机驱动的 Workspace 循环

Zleap-Agent 将循环分解为 Run → Work → Step 三级状态机，每个级别有独立的生命周期状态。

### Run 级状态机

```
created → session_assembling → planning → working → integrating → delivering → completed
                                                                              ↘ failed
                                                                              ↘ aborted
```

| 状态 | 含义 |
|------|------|
| `created` | Run 已创建，尚未开始 |
| `session_assembling` | 组装会话上下文（system prompt、可用工具、记忆） |
| `planning` | 制定执行计划（可选阶段） |
| `working` | 核心执行阶段，按 Workspace 顺序处理 |
| `integrating` | 整合各 Workspace 产出 |
| `delivering` | 生成最终交付物 |
| `completed/failed/aborted` | 终态 |

### Work 级状态机

每个 Workspace 对应一个 Work：

```
created → queued → loading → active → producing → curating → exited
```

### Step 级状态机

每个工具调用或 LLM 推理是一个 Step：

```
loading → active → producing → curating → exited
```

### Workspace 流水线执行

`AgentRuntime.run()` 的核心逻辑：

```typescript
// 伪代码：Zleap-Agent Workspace 流水线
async run(input, spaces) {
    let artifact = input;
    for (const space of spaces) {
        // 每个 Workspace 有独立的 context
        const context = this.createSpaceContext(space);
        // 工具按 allowedToolIds 过滤
        context.availableTools = this.filterTools(space.allowedToolIds);
        // 上一个 Artifact 作为当前输入
        context.input = artifact;
        // 执行 Workspace handler
        const result = await space.handler(context, signal);
        // 产出作为下一个的输入
        artifact = result.artifact;
    }
    return artifact;
}
```

**关键设计**：Workspace 外的工具调用会抛出 `tool_not_allowed` 异常，实现强隔离。

## deepseek-harness：基于事件瀑布流的 Agent Loop

deepseek-harness 的 agent-loop 包实现了基于 Cordis 事件系统的循环，核心是 **waterfall 监听器链**。

### Waterfall 事件模式

Cordis 的 `waterfall` 事件模式是中间件式的：每个监听器必须调用 `next()` 将控制权传递给链中的下一个监听器，不调用则短路返回。

```typescript
// 伪代码：waterfall 链
ctx.waterfall("agent/loop", async (state, next) => {
    // 前置处理（如注入 system prompt）
    state.systemPrompt = await this.buildSystemPrompt();
    return next(state); // 传递给下一个监听器
});

ctx.waterfall("agent/loop", async (state, next) => {
    // 核心：LLM 调用
    const response = await this.llm.complete(state.messages);
    state.response = response;
    return next(state);
});

ctx.waterfall("agent/loop", async (state, next) => {
    // 工具执行
    if (state.response.toolCalls) {
        state.toolResults = await this.executeTools(state.response.toolCalls);
    }
    return next(state);
});
```

这种设计让插件可以在循环的任意阶段插入逻辑（如 compaction 包在循环前检查上下文长度，guard 包检测无限循环）。

### 模型可见 ⟺ 可日志化原则

deepseek-harness 有一个核心设计原则：**任何到达模型的输入必须可从 session log 重建**。如果新增了模型可见的输入类型，必须新增对应的 session event 类型。这保证了可调试性和可复现性。

## veadk-python：委托式运行时循环

veadk-python 将 Agent 和 Runner 分离，Agent 负责配置和状态，Runner 负责执行循环。Runner 支持将实际执行**委托**给不同的运行时后端。

### Agent/Runner 分层

```python
# veadk-python 分层概念
class Agent(LlmAgent):
    """Agent 持有配置、记忆、工具定义"""
    model_name: str
    model_provider: str
    short_term_memory: ShortTermMemory
    long_term_memory: LongTermMemory
    tools: list[Tool]

class Runner:
    """Runner 负责执行循环"""
    async def run(self, agent: Agent, messages: list) -> Result:
        runtime = self.select_runtime(agent)  # 选择运行时后端
        return await runtime.execute(agent, messages)
```

### 运行时委托

Runner 支持三种运行时后端：

| 运行时 | 特点 |
|--------|------|
| `base_runtime` | 默认本地循环实现 |
| `codex/runtime` | 委托给 OpenAI Codex 运行时 |
| `piagent/runtime` | 委托给 PiAgent 运行时 |

这种委托模式使得同一套 Agent 配置可以在不同执行引擎上运行。

## 四种循环实现对比

| 维度 | hermes-agent | Zleap-Agent | deepseek-harness | veadk-python |
|------|-------------|-------------|-----------------|--------------|
| **循环模型** | 单体 while 循环 | 三级状态机（Run/Work/Step） | Waterfall 事件链 | Agent/Runner 分层委托 |
| **扩展方式** | 参数配置 + 回调 | 9 个 Hook 点 | 插件监听 waterfall 事件 | 运行时后端切换 |
| **工具执行** | 并发/顺序/分段三种 | 按 Workspace 隔离 | 插件化工具服务 | 工具注册 + 运行时委托 |
| **错误恢复** | try/except + TTL 缓存 | 状态机回退 + 信号中断 | guard 包（循环卫生+超时） | 运行时级错误处理 |
| **多代理** | MoA 内置于循环 | Workspace 流水线 | subagent 包委派 | agents/ 模块 |
| **状态可观测** | 回调函数 | EventBus.observe() | Session log（模型可见=可日志化） | Runner 事件 |
| **中断处理** | 信号处理 + check_fn | AbortSignal | guard 超时 | 运行时级控制 |

## 循环设计的关键权衡

### 1. 单体可配置 vs 插件化

hermes-agent 使用大而全的参数化 `AIAgent` 类，配置集中但类本身复杂（75+ 参数）。Cordis/dsh 使用插件 waterfall 链，每个功能是独立插件，但理解完整流程需要追踪多个插件的事件监听顺序。

### 2. 并发 vs 顺序工具执行

并发执行速度快但工具间无法传递中间结果；顺序执行灵活但速度慢。hermes-agent 的分段模式试图兼顾——先并发执行独立工具，再顺序处理有依赖的工具。

### 3. 状态机 vs 事件链

Zleap 的显式状态机让生命周期清晰可见，但增加新状态需要修改状态机定义。dsh 的 waterfall 事件链更灵活（插件随时插入），但控制流不如状态机直观。

### 4. 委托 vs 内置

veadk 的运行时委托提供了最大灵活性（可以切换到 Codex/PiAgent），但增加了抽象层开销和调试复杂度。

## 相关概念

- [工具系统](02-tool-system.md) — 循环中的工具调用如何注册、授权和执行
- [多智能体编排](04-multi-agent.md) — 单 Agent 循环如何扩展为多 Agent 协作
- [插件化架构模式](08-plugin-architecture.md) — Cordis waterfall 链的底层实现
- [上下文管理](06-context-management.md) — 循环中的上下文窗口管理
- [hermes-agent 架构深度走读](/examples/hermes-agent-deep-dive.md) — hermes-agent 循环实现的代码级分析
