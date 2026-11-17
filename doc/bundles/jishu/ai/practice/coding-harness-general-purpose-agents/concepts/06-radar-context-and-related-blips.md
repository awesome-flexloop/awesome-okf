---
okf_version: "0.2"
type: Concept
title: "雷达坐标：Vol 35 的 Harness 主题簇"
description: "把该 blip 放回 Thoughtworks Technology Radar Vol 35 的 harness 主题簇，解释 Adopt/Trial/Assess 的关系与观察重点。"
tags: [thoughtworks, technology-radar, vol-35, harness, governance, landscape]
generated: { by: "lobsterai/main", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: "2027-04-30"
sources:
  - id: radar
    resource: https://www.thoughtworks.com/radar
  - id: blip
    resource: https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents
  - id: agent-sandboxing
    resource: https://www.thoughtworks.com/radar/techniques/agent-sandboxing
  - id: managed-runtime
    resource: https://www.thoughtworks.com/radar/techniques/managed-agents-runtime
  - id: enterprise-harness
    resource: https://www.thoughtworks.com/radar/techniques/enterprise-harness
  - id: harness-quality
    resource: https://www.thoughtworks.com/radar/techniques/harness-quality-evaluation
  - id: agent-skills
    resource: https://www.thoughtworks.com/radar/techniques/agent-skills
---

# 雷达坐标：Vol 35 的 Harness 主题簇

> 这篇 blip 不是孤立出现的。Vol 35 同时收录了 Agent sandboxing、Managed agents runtime、Enterprise harness、Harness quality evaluation、Agent plugin marketplace 等条目（F-027～F-031）。把它们放在一起看，才能理解“coding harness”在 2026 年 11 月的技术坐标。

## 1. 雷达怎么读

Thoughtworks Technology Radar 是一年两次的技术 landscape 快照，基于其全球团队的项目经验（F-047）。四个环的含义大致是。

| 环 | 含义 | 对团队的动作 |
|---|---|---|
| Adopt | 已经证明有效，建议默认采用 | 可以直接进入生产 |
| Trial | 值得在真实项目中试用 | 选低风险场景试点 |
| Assess | 值得关注与评估 | 做调研、原型，不急着上线 |
| Caution | 有明确风险或反模式 | 谨慎使用，先解决风险 |

“Coding harness for general-purpose agents” 本期评级是 **Trial**（F-004）：方向被看好，但还不是“所有团队默认采用”的 Adopt。

## 2. Harness 主题簇

| 条目 | 环 | 与本篇的关系 |
|---|---|---|
| Coding harness for general-purpose agents | Trial | 本篇主题：复用编码运行时 |
| Agent sandboxing | Adopt | 运行时安全的底线（F-027、F-034） |
| Managed agents runtime | Trial | 把运行时托管到平台（F-028、F-035） |
| Enterprise harness | Assess | 组织级资产与治理层（F-029、F-032） |
| Harness quality evaluation | Assess | 如何验证 harness 真的有效（F-030、F-033） |
| Agent plugin marketplace | Trial | 技能/插件的分发渠道（F-031） |
| Agent Skills | Trial（2026-04） | 模块化上下文标准（F-026、F-036） |

这七条串起来是一条完整的采用链。

1. 用 **Agent Skills** 把领域知识模块化。
2. 用 **Coding harness** 复用运行时。
3. 用 **Agent sandboxing** 限制影响范围。
4. 用 **Harness quality evaluation** 验证效果。
5. 用 **Agent plugin marketplace** 分发与版本化。
6. 用 **Enterprise harness** 做组织级治理。
7. 需要托管时，用 **Managed agents runtime**。

## 3. 为什么是 Trial 而不是 Adopt

从雷达的措辞与同簇条目可以推断三个原因。

1. **能力差异大**：四家 harness 的沙箱、审批、扩展模型并不一致（F-016、F-017、F-018），没有形成统一最佳实践。
2. **领域适配未验证**：文章明确提醒编码偏向与成本问题（F-020～F-025），说明“通用任务”还在早期。
3. **治理层未成熟**：Enterprise harness 与 Harness quality evaluation 都还在 Assess（F-029、F-030），组织级配套没跟上。

这不代表“不能用”，而是“适合有工程能力的团队先试”。

## 4. 三条观察线

### 4.1 运行时收敛

四家入口正在分化出不同生态。

1. Claude 走“库 + 子进程 + 完整能力”。
2. Codex 走“SDK + app-server 双边界”。
3. OpenCode 走“HTTP/OpenAPI + 多客户端”。
4. Pi 走“最小内核 + 扩展”。

观察点：是否会出现跨 harness 的通用协议，让技能、会话、审批可以迁移。

### 4.2 治理上移

单机配置正在变成组织级平台。

1. Enterprise harness 把技能、工具、策略集中管理（F-032）。
2. Managed agents runtime 把执行、基础设施、凭证、可观测性托管（F-035）。
3. Harness quality evaluation 把质量验证变成常规 CI（F-033）。

观察点：治理层是否会反过来约束 harness 的设计，例如强制审批协议、会话格式、审计字段。

### 4.3 成本透明

文章把 token 成本列为采用风险（F-022、F-023）。随着 agent 进入生产，成本会从“工程问题”变成“财务问题”。

观察点：是否出现标准的成本计量、预算控制与按任务计费方式。

## 5. 与相邻概念的关系

| 概念 | 与本篇的区别 | 关系 |
|---|---|---|
| Agent framework | 自己搭 loop，控制力高 | 竞争/互补；harness 用控制力换成熟度（F-014） |
| Managed agents runtime | 平台托管执行与运维 | 上游；harness 可以跑在托管运行时里（F-035） |
| Enterprise harness | 组织级资产与策略 | 外层；管技能、工具、合规（F-032） |
| Agent Skills | 模块化上下文标准 | 内容层；harness 消费 skills（F-036） |
| Agent sandboxing | 隔离与最小权限 | 安全层；所有 agent 的默认要求（F-034） |

## 6. 什么时候该回看雷达

1. 下一期雷达发布时（约 2027 年 4 月），看该 blip 是否移动。
2. 四家 SDK 出现破坏性变更时，回看能力表与版本边界。
3. 组织准备从试点转生产时，回看 Enterprise harness 与 Harness quality evaluation 是否升级。
4. 成本或安全事件发生后，回看 Agent sandboxing 与审批实践。

## 7. 小结

Coding harness 在 Vol 35 里的位置很清晰：它是 **Trial 级的运行时复用技术**，上游有 Agent Skills 提供内容，下游有 Managed agents runtime 提供托管，外层有 Enterprise harness 与 Harness quality evaluation 提供治理，底层有 Agent sandboxing 提供安全。理解这个主题簇，比记住某一家 SDK 的 API 更重要。
