---
type: Concept
title: 多智能体编排
description: 从 Mixture of Agents 到 Workspace 流水线到子代理委派——多 Agent 协作的架构模式对比
tags: [ai-agent, multi-agent, moa, orchestration, workspace, subagent, delegation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:30:00+08:00" }
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
  - id: agency
    resource: /references/ai-agent-sources.md#agency-agents
  - id: secondme
    resource: /references/ai-agent-sources.md#second-me
---

# 多智能体编排

单个 Agent 能做的事情有限——复杂任务往往需要多个 specialized Agent 协作。多智能体编排（Multi-Agent Orchestration）研究如何组织多个 Agent 分工协作，共同完成复杂任务。本文分析四种主流编排模式：MoA（Mixture of Agents）、Workspace 流水线、子代理委派和去中心化协作。

## 模式一：MoA（Mixture of Agents）

hermes-agent 实现了 MoA 模式，灵感来自 MoE（Mixture of Experts），核心思想是 **reference fan-out → aggregator** 两阶段推理。

### 两阶段架构

```
用户提问
    │
    ▼
┌─────────────┐
│  Aggregator  │ ← 主 Agent（通常是更强的模型）
└──────┬──────┘
       │ 发起 reference 请求
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌─────────────┐┌─────────────┐┌─────────────┐
│ Reference 1  ││ Reference 2  ││ Reference N  │ ← 多个参考 Agent
│ (模型A/视角A) ││ (模型B/视角B) ││ (模型N/视角N) │    （不同模型或不同角色）
└──────┬──────┘└──────┬──────┘└──────┬──────┘
       │              │              │
       └──────────────┴──────────────┘
                      │ 各自返回参考回答
                      ▼
┌─────────────┐
│  Aggregator  │ ← 聚合所有参考回答，生成最终回复
└─────────────┘
```

### hermes-agent 实现

hermes-agent 通过 `MoAClient` 和 `MoAChatCompletions` 类实现 MoA，对外暴露**与 OpenAI 客户端兼容的接口**——这意味着使用 MoA 和使用普通单模型调用在 API 层面没有区别：

```python
# 概念性伪代码：hermes-agent MoA 接口
class MoAClient:
    """MoA 客户端，模拟 OpenAI 客户端接口"""
    
    def __init__(self, aggregator_config: dict, reference_configs: list[dict]):
        self.aggregator = self._create_agent(aggregator_config)
        self.references = [
            self._create_agent(config) for config in reference_configs
        ]
    
    async def chat_completions(self, messages: list, **kwargs):
        """兼容 OpenAI 的 chat.completions.create() 接口"""
        # Phase 1: Fan-out - 并行调用所有 reference agents
        reference_tasks = [
            ref.chat(messages) for ref in self.references
        ]
        reference_responses = await asyncio.gather(*reference_tasks)
        
        # Phase 2: Aggregate - 主 Agent 聚合所有参考回答
        aggregator_messages = self._build_aggregator_messages(
            messages, reference_responses
        )
        return await self.aggregator.chat(aggregator_messages)
```

### MoA 的设计要点

- **模型异构**：Reference agents 可以使用不同模型（如同时用 GPT-4、Claude、DeepSeek），利用不同模型的强项
- **视角多样性**：Reference agents 可以被赋予不同角色（如"从安全角度审查"、"从性能角度审查"）
- **接口透明**：Aggregator 对外暴露与单模型一致的接口，调用方无需感知 MoA 内部结构
- **并行执行**：Reference 阶段并行执行，延迟约等于最慢的那个 reference 而非串行时间之和

## 模式二：Workspace 流水线

Zleap-Agent 实现了 Workspace 流水线模式，核心思想是将任务分解为**有序的 Workspace**，每个 Workspace 有独立的上下文和工具权限，上一个 Workspace 的产出作为下一个的输入。

### 流水线结构

```
[用户输入]
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Workspace 1  │────▶│  Workspace 2  │────▶│  Workspace 3  │────▶│  Workspace N  │
│  角色：规划者  │ Artf.│  角色：执行者  │ Artf.│  角色：审查者  │ Artf.│  角色：交付者  │
│  工具：搜索    │     │  工具：终端/文件│     │  工具：LSP/测试│     │  工具：格式化  │
│  记忆：全局    │     │  记忆：执行相关│     │  记忆：质量标准│     │  记忆：格式规范│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                          │
                                                                          ▼
                                                                     [最终交付物]
```

### 实现机制

每个 Workspace 在运行时获得独立的 `WorkContext`：

```typescript
interface WorkContext {
    input: Artifact;              // 上一个 Workspace 的产出
    availableTools: Map<string, Tool>;  // 当前 Workspace 可用工具（过滤后）
    skills: Skill[];              // 当前 Workspace 可用技能
    queryMemory(query: string): Promise<Memory[]>;  // 记忆查询
    callTool(toolId: string, args: any): Promise<any>;  // 工具调用（运行时权限检查）
    signal: AbortSignal;          // 中断信号
}

// Workspace 定义
interface Workspace {
    id: string;
    name: string;
    handler: (context: WorkContext, signal: AbortSignal) => Promise<WorkspaceResult>;
    allowedToolIds: Set<string>;  // 工具白名单
    prompt: string;               // Workspace 专属 system prompt
    memoryScope: MemoryScope;     // 记忆访问范围
}
```

### 流水线 vs 单循环

Workspace 流水线与传统 Agent 循环的关键区别：

| 维度 | 单 Agent 循环 | Workspace 流水线 |
|------|-------------|-----------------|
| 工具可见性 | 所有工具始终可见 | 每个阶段只看到相关工具 |
| 上下文 | 全部对话历史 | 前序产出 + 当前 Workspace 指令 |
| 错误隔离 | 一个错误可能破坏整个任务 | Workspace 边界提供故障隔离 |
| 复杂度 | 单循环管理所有状态 | 每个 Workspace 逻辑简单 |
| 适用场景 | 开放域对话、简单任务 | 多步骤复杂任务、有明确阶段划分 |

## 模式三：子代理委派

deepseek-harness 通过 `subagent` 包实现子代理委派模式。核心思想是主 Agent 可以**动态创建子代理**执行子任务，子代理运行在独立的上下文中，完成后返回结果。

### 委派模型

```
┌─────────────────────────────────┐
│          主 Agent                │
│  ┌───────────────────────────┐  │
│  │  任务：实现一个登录功能     │  │
│  └─────────┬─────────────────┘  │
│            │ 委派                │
│            ▼                     │
│  ┌─────────────────┐  ┌────────┐│
│  │ 子Agent: 前端    │  │子Agent: ││
│  │ 实现登录表单     │  │后端     ││
│  │ 返回: 组件代码   │  │API实现  ││
│  └─────────────────┘  │返回:    ││
│                       │接口代码  ││
│                       └────────┘│
│            │ 收集结果            │
│            ▼                     │
│  ┌───────────────────────────┐  │
│  │  整合：前后端联调           │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 与 MoA 和 Workspace 的区别

| 维度 | MoA | Workspace 流水线 | 子代理委派 |
|------|-----|-----------------|-----------|
| 拓扑 | 星形（1个aggregator+N个reference） | 线性流水线 | 树形（主Agent动态创建子Agent） |
| 预定义 | Reference agents 预配置 | Workspace 序列预定义 | 子代理动态创建，数量和角色不固定 |
| 上下文 | References 看到完整问题 | 每个Workspace看到input+prompt | 子代理看到委派的子任务 |
| 通信 | References 之间不通信 | 线性传递 Artifact | 子代理完成后返回主Agent |
| 适用 | 需要多角度审查/生成 | 有明确阶段的任务 | 复杂任务的动态分解 |

## 模式四：去中心化 Agent 网络（AI Space）

Second-Me 实现了更激进的去中心化协作模式——**AI Space**，多个本地 Second Me（个人 AI 分身）可以在网络空间中协作讨论。

### Host-Participant 双策略

```
┌──────────────────────────────────────────────┐
│                 AI Space                      │
│                                              │
│  ┌──────────┐                                │
│  │ Host Me  │ ← 发起讨论，主导流程             │
│  │ (用户A)  │                                │
│  └────┬─────┘                                │
│       │ host_strategies                       │
│       │ （引导讨论、综合观点、做出决策）        │
│       │                                      │
│  ┌────┴─────┐  ┌──────────┐  ┌──────────┐   │
│  │Participant│  │Participant│  │Participant│   │
│  │   Me B   │  │   Me C   │  │   Me D   │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│       │              │              │         │
│       └──────────────┴──────────────┘         │
│         participant_strategies                │
│         （基于各自的记忆和人格发表观点）         │
└──────────────────────────────────────────────┘
```

Host 和 Participant 使用不同的策略（strategy）：
- **host_strategies**：引导讨论方向、综合各 participant 观点、做出最终决策
- **participant_strategies**：基于各自 Second Me 的 L1/L2 记忆和人格，提供个性化的观点

### 与其他模式的本质区别

AI Space 模式与前三种有本质区别：
- 每个 Agent 是**独立的个人 AI 分身**，代表不同用户
- Agent 之间是**对等网络**关系，不是主从关系
- 每个 Agent 有自己的**私有记忆**（L0-L2），不共享
- 通过**网络协议**通信，而非进程内调用
- 支持 Roleplay（同一 Second Me 可切换不同人格角色）

## agency-agents：编排层的 Persona 方法

agency-agents 不是运行时框架，但提供了多代理编排的**persona 层**支持：

- **Agents Orchestrator**（`specialized/agents-orchestrator.md`）：定义多 Agent 协调角色，负责任务分解、分配、综合
- **Playbooks**（`strategy/playbooks/`）：6 阶段协作流程（discovery → strategy → foundation → build → hardening → launch）
- **Runbooks**：预定义的协作场景（企业功能、事件响应、营销、创业 MVP）
- **Handoff Templates**：Agent 之间的交接模板

这种"Persona + Playbook"方法将多Agent协作的**角色和流程**编码为 Markdown 文件，可以在任意支持 Markdown persona 的 Agent 框架上运行。

## 多智能体编排模式选择指南

| 场景 | 推荐模式 | 代表框架 |
|------|---------|---------|
| 需要多角度审查代码/方案 | MoA（并行参考+聚合） | hermes-agent |
| 有明确步骤的复杂任务（如PRD→代码→测试→部署） | Workspace 流水线 | Zleap-Agent |
| 开放域复杂问题，需要动态分解 | 子代理委派 | deepseek-harness |
| 多个人类用户的 AI 协作讨论 | 去中心化 AI Space | Second-Me |
| 快速搭建多角色协作流程 | Persona + Playbook | agency-agents |

## 相关概念

- [Agent 核心循环](01-agent-loop.md) — 单个 Agent 的循环如何被编排为多 Agent 协作
- [工具系统](02-tool-system.md) — 子代理委派如何将"创建子代理"实现为一种工具
- [插件化架构模式](08-plugin-architecture.md) — subagent 包如何作为 Cordis 插件注册
- [技能与 Persona 系统](07-skill-persona.md) — agency-agents 的 persona 编排方法
