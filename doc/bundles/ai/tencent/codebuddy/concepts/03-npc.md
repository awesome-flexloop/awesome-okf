---
type: Concept
title: "NPC 云端 AI 员工"
description: "NPC 是基于 CodeBuddy 打造的云端 AI 员工，与 CNB 平台深度融合，以目标驱动方式自主完成从需求到 PR 的全流程，支持多 NPC 并行协同与自主修复。"
tags: [codebuddy, npc, cloud-agent, cnb, autonomous, pr, team-collaboration]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: npc-official
    resource: /references/npc.md
    title: CodeBuddy NPC 产品官网
---

# NPC 云端 AI 员工

NPC 是 CodeBuddy 产品矩阵中面向云端自主交付的 AI 员工（Cloud Agent），基于 CodeBuddy 核心能力打造，与 CNB 平台（cnb.cool）深度融合（F-039, F-040）。其理念为"给 NPC 定下目标，下班前验收 Ta 的产出"（F-041），代表了 AI 编程从"人驱动工具"到"人验收产出"的范式转变。

## 产品定位

NPC 不是运行在本地的编程助手，而是部署在云端、对接代码托管与 CI/CD 平台的自主 Agent。它直接访问 CNB 仓库、Issue 与流水线（F-043），能够独立完成软件工程任务并提交 PR，用户只需定义目标并验收结果。

NPC 入口为 https://cnb.cool/npc/CodeBuddy（F-050）。

## 目标驱动范式

NPC 采用目标驱动（Goal-driven）模式，核心原则是用户定义 What（做什么）而非 How（怎么做）（F-042）。用户给出目标后，NPC 自主完成以下工作：

1. **获取上下文**：从 CNB 仓库、ISSUE、流水线中自主读取所需信息（F-043）
2. **规划方案**：拆解任务并制定实施计划
3. **编码实现**：编写并修改代码
4. **提交 PR**：创建 Pull Request
5. **构建验证**：触发构建，检查结果
6. **预览环境**：部署预览环境供验收
7. **验收合入**：等待人工验收后合入（F-045）

## 全流程交付链路

NPC 覆盖从需求到合入的完整流程（F-045）：

```
规划 → 编码 → PR → 构建 → 预览环境 → 验收合入
```

这一链路与传统 AI 编程助手的关键区别在于：NPC 不仅生成代码，还负责提交 PR、响应构建结果、部署预览，形成端到端的交付闭环。

## 自主修复能力

NPC 具备两项关键的自主修复能力：

### 构建报错自主修复

当构建失败时，NPC 会（F-047）：

1. 读取构建日志
2. 查找相关代码
3. 提交修复
4. 重新触发构建
5. 循环直至门禁通过

这意味着 NPC 对 CI 反馈拥有闭环响应能力，而非仅生成一次代码后等待人工介入。

### 合并冲突自动解决

NPC 可自动解决合并冲突（F-048），减少 PR 合入时的人工协调成本。

## 并行与协同

### 并行指派

多个 NPC 可在云端并行工作（F-044），用户可同时指派多个独立任务，大幅缩短批量任务的交付时间。

### NPC Team 协同

NPC 支持多 NPC 协同，NPC Team 按职能分工（F-046）。不同 NPC 可承担不同角色（如开发、测试、审查），形成虚拟团队协作完成复杂任务。

## 可定制性

NPC 支持三方面定制（F-049）：

| 定制维度 | 说明 |
|----------|------|
| 职能（Role） | 定义 NPC 的角色定位与专长 |
| SOP | 标准作业流程，固化团队工程规范 |
| Skill | 可复用技能包，扩展 NPC 能力 |

通过 SOP 和 Skill 定制，团队可将自身工程实践固化到 NPC 行为中，使 AI 员工遵循团队规范。

## 计费模式

NPC 定价按量收取 Agent 执行 Token 消耗（F-051）。使用多 NPC 并行时需关注 Token 总消耗。

## 与本地工具的对比

| 维度 | IDE / CLI（本地） | NPC（云端） |
|------|-------------------|-------------|
| 运行位置 | 本地设备 | CNB 云端 |
| 驱动方式 | 人逐步驱动 | 目标驱动，自主执行 |
| 上下文来源 | 本地工作区 | CNB 仓库/Issue/流水线 |
| 交付物 | 代码修改 | 完整 PR（含构建/预览） |
| 并行能力 | 单会话 | 多 NPC 云端并行 |
| 适用场景 | 日常编码、探索 | 独立需求交付、批量任务 |

NPC 基于 CodeBuddy 核心能力打造（F-039），与 IDE/CLI 共享 Skills 等高级能力（F-018, F-049），但将交互模式从"辅助"升级为"自主交付"。

## 相关概念

- [产品矩阵总览](/concepts/00-product-matrix.md) — NPC 在 CodeBuddy 矩阵中的定位
- [CodeBuddy IDE](/concepts/01-ide.md) — NPC 基于其核心能力打造
- [CLI](/concepts/02-cli.md) — 本地 Sub-agents 与云端 NPC 的能力对比
- [Security 安全审计](/concepts/05-security.md) — NPC 自主修复与安全审计的协同
- [IDE 工作流示例](/examples/ide-workflow.md) — 本地研发流程参考
- [CLI 快速入门](/examples/quick-start-cli.md) — 本地 Sub-agents 使用参考
