---
type: concept
title: "Agent 与预设体系"
description: "AgentManager 对 CoworkStore 的委托模式、agents 表 20 列（含 JSON 存储的 skill_ids）、内置预设 Agent 的查询与添加流程。"
tags: [lobsterai, agent, preset, manager, delegation]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# Agent 与预设体系

LobsterAI 的 Agent（不同人格/能力配置的 AI 助手）以"用户可增删改"的一等资源存在：会话可绑定不同 Agent（`listSessionIdsByAgent`，F-la-019），渲染层有专门的 Agent 视图。本篇讲解 Agent 数据模型与 `AgentManager` 的薄封装设计。

## 一、数据模型：agents 表

Agent 持久化在 `agents` 表，共 20 列（F-la-018），关键列包括：

| 列 | 说明 |
|---|---|
| `skill_ids` | JSON 字符串存储的技能 ID 列表（绑定 [/concepts/09-skill-system.md](09-skill-system.md) 的技能） |
| `source` | Agent 来源标识 |
| `preset_id` | 若由预设创建，回指预设 ID |

以 JSON 列存储一对多的技能绑定，免去了关联表的 join 成本；`source` 与 `preset_id` 使"用户自建 Agent"与"从预设添加的 Agent"在数据层可区分、可溯源。

## 二、AgentManager：刻意保持薄的委托层

`AgentManager`（`src/main/agentManager.ts`）的方法几乎一一委托给 CoworkStore（F-la-023）：

```ts
// 忠实于 agentManager.ts 的方法签名（F-la-023）
class AgentManager {
  listAgents(): Agent[]              // → store.listAgents()
  getAgent(agentId: string): Agent | null
  getDefaultAgent(): Agent           // 从 listAgents 中解析默认项
  createAgent(request: CreateAgentRequest, defaultModel?: string): Agent
  updateAgent(agentId: string, updates: UpdateAgentRequest): Agent | null
  reorderAgents(agentIds: string[]): Agent[]
  deleteAgent(agentId: string): boolean
}
```

教学要点：Manager 层没有另起数据访问，而是**复用 CoworkStore 的存储能力**，自己只保留两类增值逻辑——默认 Agent 解析（`getDefaultAgent` 在列表上推导）与创建时的请求组装（`createAgent` 接收 `CreateAgentRequest` 并补充 `defaultModel` 后转交）。在单数据访问层已足够内聚的本地应用中，额外的 Manager 抽象若只是透传便不值得存在；这里的 Manager 是"领域语义壳"而非"数据缓存层"。

## 三、预设 Agent：内置模板的分发

除用户 Agent 外，`AgentManager` 提供三个预设方法（F-la-023）：

| 方法 | 职责 |
|---|---|
| `getPresetAgents()` | 列出尚未被添加的内置预设（与现有 Agent 列表比对过滤） |
| `getAllPresetAgents()` | 列出全部内置预设，不做过滤 |
| `addPresetAgent(presetId, defaultModel?)` | 按预设 ID 实例化为用户 Agent（经 `store.getAgent(preset.id)` 查重后 `store.createAgent`） |

预设模式的教学价值：**内置能力以"只读模板"形式分发，落地为"可演化实体"**。预设本身不进用户数据（升级应用即升级预设目录），用户添加后才成为 `agents` 表中的一行，此后可自由修改而不影响预设模板。`getPresetAgents` 与 `getAllPresetAgents` 的过滤/全量拆分，让 UI 可以分别渲染"可添加"与"全部"两个视图。

## 四、与周边子系统的关系

- **技能**：Agent 经 `skill_ids` 列绑定技能，技能体系见 [/concepts/09-skill-system.md](09-skill-system.md)；
- **会话**：`listSessionIdsByAgent` 支持按 Agent 归集会话，会话数据访问见 [/concepts/04-session-message-store.md](04-session-message-store.md)；
- **运行时**：Agent 定义最终经 OpenClaw 网关执行（[/concepts/00-overall-architecture.md](00-overall-architecture.md) 的分工）。

## 设计启示

1. "预设 = 只读模板，添加 = 实例化"是分发内置 Agent 的干净模式，升级与个性化互不干扰；
2. Manager 层只保留领域语义（默认解析、请求组装、查重），存储一律下沉单一 Store；
3. 来源溯源（`source`/`preset_id`）在建表时即预留，避免事后补列。

## 相关概念

- [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md)
- [/concepts/04-session-message-store.md](04-session-message-store.md)
- [/concepts/09-skill-system.md](09-skill-system.md)
