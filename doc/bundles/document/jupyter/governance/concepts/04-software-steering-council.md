---
type: Concept
title: "软件指导委员会（SSC）"
description: "Software Steering Council管辖Jupyter跨项目软件决策，管理JEP流程、安全漏洞、孵化和归档，由各子项目代表组成。"
tags: [software-steering-council, SSC, software, JEP, cross-project]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ssc
    resource: /references/ssc-source.md
    title: "SSC信源"
---

## 软件指导委员会的定位

软件指导委员会（Software Steering Council，简称 SSC）是 Jupyter 项目中**负责软件相关跨项目决策**的机构。它的核心定位不是"控制所有技术决策"，而是：

1. **跨项目协调者**：处理影响多个子项目的决策
2. **信息共享平台**：各子项目代表交流信息和专业知识
3. **升级决策机制**：当某个决策超出单个子项目范围时，通过 JEP 流程升级到 SSC

**关键原则**：SSC 未明确参与的技术决策，自动下放给各子项目自主管理——子项目在日常活动、创建新仓库等方面享有独立性和自主权。

## 专属职责

### JEP 流程管理
- 定义 Jupyter Enhancement Proposals（JEPs，Jupyter 增强提案）的提交、审查和批准流程
- 维护 JEP 流程的包容性和参与性，确保合适的利益相关者提供反馈
- 在收到社区反馈后对 JEPs 做出决策（JEPs 是将软件决策/想法升级到整个项目层面的机制）

参考起点：[NumFOCUS DISCOVER Cookbook](https://github.com/numfocus/DISCOVER-Cookbook)

### 项目生命周期管理
- **Incubation（孵化）**：拥有和管理 [jupyter-incubator](https://github.com/jupyter-incubator) 流程
- **Attic（归档）**：拥有和管理项目归档流程（[archived repositories](https://github.com/orgs/jupyter/repositories?type=source&q=archived%3Atrue)）

### 跨项目标准与安全
- 管理涉及跨领域关注点、标准、协议和其他影响整个项目的架构问题的讨论
- 拥有和管理全项目的安全漏洞事务，包括 Jupyter 安全列表、私有安全仓库等

### 代表权审批
- 投票决定是否接受 EC 提名的 Working Group 在 SSC 拥有代表

## 与 EC 的共享职责

与 EC 双重批准事项：治理模型变更、新子项目创建/移除（详见 [执行委员会](03-executive-council.md)）。

## 成员构成

### 代表来源

SSC 成员来自以下方面：

| 来源 | 说明 |
|------|------|
| **软件子项目** | 每个官方 Jupyter 子项目派一名代表 |
| **特定 Working Group** | 经 EC 提名、SSC 批准的工作组（如 DEI） |
| **特定 Standing Committee** | 对 SSC 活动有重要影响的常设委员会（如国际化） |

### 代表资格与规则
- 任何 Subproject Council 成员都有资格代表该子项目参加 SSC
- 一人**可同时代表多个子项目**（虽然不理想），此时可对每个代表的子项目投一票
- 不可同时在 SSC 和 EC 任职
- **无固定任期**：各子项目自行决定代表选拔方式和任期，鼓励健康轮换避免倦怠

### 罢免
SSC 可投票罢免成员，需全体成员的**2/3多数**通过（包括被罢免者参与投票）。

## 沟通机制

### 会议
SSC 会议时间公布在 [Jupyter Community Calendar](https://jupyter.org/community#calendar) 上。

### 邮件列表
- 地址：[jupyter-software-steering-council@googlegroups.com](mailto:jupyter-software-steering-council@googlegroups.com)

### Team Compass
SSC 的日常运营信息在其 [Team Compass](https://github.com/jupyter/software-steering-council-team-compass/) 上。

## 反常识要点

- **SSC 不是"最高技术权威"**：它的职责是协调和决策跨项目事务，而非审批每个子项目的技术选择。各子项目在其范围内高度自治。
- **一人可代表多子项目**：虽然不理想，但规则允许。这在小项目缺乏足够活跃成员时是务实的设计。
- **安全漏洞管理归属 SSC**：安全是跨项目关注点，由 SSC 统一管理而非各子项目各自为政，这确保了安全响应的一致性。

## 相关概念

- [三主体治理模型](01-governance-model.md)
- [执行委员会（EC）](03-executive-council.md)
- [软件子项目体系](06-software-subprojects.md)
- [决策制定流程](09-decision-making.md)
- [新子项目准入与孵化](11-new-subprojects.md)
