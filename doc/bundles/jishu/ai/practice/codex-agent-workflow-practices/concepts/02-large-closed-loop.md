---
okf_version: "0.2"
type: concept
title: "大闭环工作流：让 Agent 持续工作数小时而不迷失"
description: "通过工具提供、反馈闭环、monorepo 整合、集成测试环境以及 Spec+Plan 文档组合，实现 agent 长时间自主工作"
tags: [codex, closed-loop, monorepo, integration-test, spec-document]
sources:
  - id: blog
    url: https://zhuanlan.zhihu.com/p/2040748661567710711
generated:
  by: "agent:agnes"
  at: "2026-09-09T04:25:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-09T04:30:00+08:00"
status: stable
stale_after: "2026-11-21"
---

# 大闭环工作流：让 Agent 持续工作数小时而不迷失

## 核心问题：人类 Context Switch 瓶颈

如果每 5 分钟都需要人去沟通和下达新指令，**大脑的 context switch 能力会比 token 更早达到瓶颈** [作者观点]。

因此目标是：让 agent 不止写代码，还能自主完成测试验证、code review、问题修复、提 MR 的完整闭环。

## 闭环全流程

```
写代码 → 自测（截图/录屏）→ code review → 修复问题 → 提 MR → 贴验证结果 → 指出重点 review 区域
```

原先需要多次人工干预的环节，变成相对自动化的流程，只有在必要时才让人类介入 [作者观点]。

## OpenAI 极端思维

> "把每次需要人类介入 agent 工作的点都看作失败" [F-008](../article-source.md#F-008)

随着模型能力增强，不断检验自己的干预动作是否可以内化到 agent 工作流程中。

## 基建四要素

### 1. 工具提供

将原先需人工提供的信息转为 agent 自助获取的工具：

- **线上日志获取**：原先手动粘贴日志给 agent → 做成工具让 agent 自己获取
- **浏览器操作**：让 agent 操作浏览器做端到端测试

### 2. 反馈信息

添加自动化检查脚本，让 agent 能自行获取反馈并修复：

- **Lint / Test**：常见反馈来源
- **Arch check 脚本**：发现 agent 代码违反架构准则时，让 agent 自行执行并修复 [作者观点]
- **Anthropic 案例**：设计品味评估的自动化检查 [F-009](../article-source.md#F-009)

### 3. Monorepo 整合

将多个项目合并到 monorepo，使 agent 能端到端完成前后端开发和联调 [作者实践]。

> 作者团队花费半天将三个项目合并到 monorepo。

### 4. 集成测试环境

不仅让 agent setup worktree 做单元测试，还能启动完整环境做端到端测试验证。

结合并行化：多任务同时拉起整套集成环境需要较多基建工作 [作者观点]。

## 长程任务不迷失的关键：文档 + Context 压缩

完成基建后，如何让 agent 持续工作数小时不出现智力下降和方向跑偏？两个关键转变：

### 转变一：文档价值

做长程任务时，需要：

- **PRD 作为参照**：有一份参照的 PRD
- **随时更新的执行计划**：帮助 agent 聚焦，不会遗忘关键信息

### 转变二：利用 Codex 自动压缩

- Codex 的"自动压缩"功能足够用，无需手动管理 context [F-015](../article-source.md#F-015)
- 经常有跑几个小时的任务，过程中触发多次 context 打满后的自动压缩
- 结合文档记录，基本都能顺利完成 [作者实践]

> **Context 压缩与 eval 是适合模型厂商直接优化的场景** [F-026](../article-source.md#F-026)。

## 主题关联

- 与 [01-parallel-workflow](01-parallel-workflow.md) 互补：大闭环解决单任务深度，并行解决并发广度
- 与 [06-spec-and-plan](06-spec-and-plan.md) 深度关联：Spec+Plan 文档是大闭环的基础设施
- 与 [07-quality-assurance](07-quality-assurance.md) 衔接：技术债控制和质量保障是大闭环的自然延伸

```{toctree}
:hidden:
:maxdepth: 1
```
