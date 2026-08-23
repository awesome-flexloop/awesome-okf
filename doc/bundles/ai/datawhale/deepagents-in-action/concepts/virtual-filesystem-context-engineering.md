---
title: 虚拟文件系统与 Context Engineering
type: concept
bundle: /datawhale/deepagents-in-action
description: Deep Agents 的上下文工程核心机制——以 FilesystemBackend 虚拟文件系统为底座，支撑内容落盘、Skills渐进式加载、长期记忆与namespace隔离，是Agent管理长程上下文的基础设施。
related:
  - /datawhale/deepagents-in-action/concepts/agent-harness
  - /datawhale/deepagents-in-action/references/readme-source
sources:
  - id: github-repo
    resource: /references/readme-source.md
    title: deepagents-in-action GitHub 仓库
---

# 虚拟文件系统与 Context Engineering

第3章标题直接点明："虚拟文件系统——Deep Agents 的 Context Engineering 核心"。虚拟文件系统是 Deep Agents Harness 层最基础的设施，其他能力（Skills、长期记忆、权限控制）都构建在其上。

## 核心机制

### FilesystemBackend

`FilesystemBackend` 是虚拟文件系统的核心实现，负责让 Agent 将内容、中间结果和 Skills 落盘到文件系统。第3章使用 `deepagents/content-builder` 模板观察这一过程。

关键版本特性：
- `virtual_mode` 参数需要 `deepagents>=0.5.0`
- `FilesystemPermission` 基础权限需要 `deepagents>=0.5.2`

### 为什么是文件系统？

传统 Agent 将全部上下文塞入对话历史窗口，导致：
- 上下文窗口爆炸
- 无关信息干扰推理
- 跨会话状态丢失

虚拟文件系统将上下文管理从"塞进prompt"转变为"读写文件"：
- Agent 像人类操作文件一样组织信息
- 中间结果落盘，不占用对话窗口
- Skills 以文件形式按需加载
- 权限通过声明式规则控制读写边界

## 能力延伸

虚拟文件系统是多个进阶能力的共同底座：

| 能力 | 章节 | 与文件系统的关系 |
|------|------|------------------|
| Skills 渐进式加载 | 第7章 | Skills 以文件形式存在，按需匹配和加载 |
| 长期记忆 | 第8章 | CompositeBackend 组合 StoreBackend 与文件系统，namespace 隔离运行时 |
| 文件系统权限 | 第11章 | FilesystemPermission 声明式控制读写边界 |
| 沙箱执行 | 第10章 | 沙箱内文件读写与清理 |

### CompositeBackend 与 StoreBackend

第8章引入 `CompositeBackend` 和 `StoreBackend`，在文件系统基础上叠加跨对话记忆能力，并通过运行时 namespace 实现上下文隔离。这表明文件系统不是孤立的存储层，而是可组合的后端架构。

### FilesystemPermission

第11章的 `FilesystemPermission` 在文件系统之上叠加声明式权限规则，控制 Agent 能读什么、能写什么。这是从"能存"到"安全地存"的演进。

## 模板关联

虚拟文件系统相关章节统一使用 `deepagents/content-builder` 模板：

- 第3章：直接观察 FilesystemBackend 落盘
- 第7章：观察 Skills 如何通过文件系统匹配和加载
- 第8章：在模板基础上加入 CompositeBackend、StoreBackend、namespace
- 第11章：在模板基础上加入 FilesystemPermission

这一模板聚类设计让学习者能横向对比同一文件系统底座在不同能力叠加下的变化。

## Context Engineering 的定位

"Context Engineering"（上下文工程）是 Deep Agents 区别于传统 prompt engineering 的关键概念：

- Prompt Engineering：优化单次输入的措辞
- Context Engineering：设计 Agent 运行时的上下文管理架构——什么信息持久化、什么按需加载、什么隔离、什么共享

虚拟文件系统正是 Context Engineering 的物理实现——它给了 Agent 一个"工作台"，让 Agent 像人类一样把资料摊在桌上、归档到文件夹、在需要时取出。

## 相关概念

- [Agent Harness——从框架到运行时外壳](./agent-harness.md)——理解虚拟文件系统在 Harness 层中的定位
- [信源登记](../references/readme-source.md)——版本要求与章节结构
