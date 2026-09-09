---
okf_version: "0.2"
type: concept
title: "Codex Agent 工作流概览：从 2-3 亿到 243 亿 Token 的实践跃迁"
description: "作者天地大观 2026年3-5月使用 Codex Pro 的工作方式转型记录：从月耗 2-3 亿 token 跃升至 243 亿，核心四杠杆——并行、大闭环、对抗提升、真实需求驱动"
tags: [codex, agent-workflow, token-economy, personal-practice, ai-coding]
sources:
  - id: blog
    url: https://zhuanlan.zhihu.com/p/2040748661567710711
generated:
  by: "agent:agnes"
  at: "2026-09-09T04:20:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-09T04:30:00+08:00"
status: stable
stale_after: "2026-11-21"
---

# Codex Agent 工作流概览：从 2-3 亿到 243 亿 Token 的实践跃迁

> **说明**：本文为个人技术实践博客，非官方文档。所有数据与观点均来自作者天地大观（志存高远）一手经验，标注"作者观点"或"仅博文单源"处不可视为权威结论。

## 核心数据速览

| 指标 | 3 月前 | 3/16-4/15 | 日均 |
|------|--------|----------|------|
| 月耗 Token | 2-3 亿 [F-018](../article-source.md#F-018) | 243 亿 [F-001](../article-source.md#F-001) | ~10 亿 [F-003](../article-source.md#F-003) |
| 费用（按 API 定价） | — | $12,213 [F-002](../article-source.md#F-002) | — |
| 并行项目数 | — | 2-3 个 [F-011](../article-source.md#F-011) | — |
| 并行 Codex session | — | 3-5 个 [F-013](../article-source.md#F-013) | — |

**跃迁幅度**：约 80-120 倍 [F-018](../article-source.md#F-018)。

## 四大核心杠杆

作者总结成为"Token Billionaire"（月耗千亿级 token）的四个主要杠杆：

### 杠杆一：并行工作

最大杠杆来自并行。具体做法包括：

1. **多项目 + 多 worktree**：2-3 个产品项目并行，每个项目开多个目录/worktree 做多个任务 [F-011](../article-source.md#F-011)
2. **多 session 持续产出**：保持 3-5 个 Codex session 同时工作 [F-013](../article-source.md#F-013)
3. **Sub-agent 并行 review**：code review 时并行启动 3 个 sub-agent，各负责一个特定角度 [F-012](../article-source.md#F-012)
4. **子任务并行分解**：无依赖关系的子任务启用 sub-agent 并行执行，要求模块边界清晰、耦合度低
5. **背景任务**：定时启动 agent 扫描技术债、监控 PR、修复 bug、升级依赖

### 杠杆二：更大闭环

让 agent 工作时间更长、完成更多闭环，减少人类 context switch：

- **目标**：agent 自主完成"写代码 → 测试 → 截图/录屏验证 → code review → 修复问题 → 提 MR → 指出重点 review 区域"全流程
- **OpenAI 极端思维**：每次需要人类介入都视为失败，不断将干预动作内化到 agent 工作流 [F-008](../article-source.md#F-008)
- **基建四要素**：工具提供（让 agent 自助获取日志）、反馈信息（lint/test 等自动化检查）、monorepo 整合、集成测试环境

### 杠杆三：对抗提升

通过消耗更多 token 来提升输出质量，减少人类注意力投入：

- **Review fix loop**：一个 agent 生成，另一个 agent 验证，不断迭代
- **Test fix loop**：测试驱动的自我修复循环
- **Best-of-N**：多个 agent 并行生成方案，再选择最优 [作者观点]

> **关键洞察**：训练模型拥有"批评能力"比训练"自我批评能力"容易得多，因此需要分角色（独立 context）对抗 [作者观点]。

### 杠杆四：更多真实需求

- **更快交付**：feature flag、research preview 比传统分支开发迭代更快 [F-019](../article-source.md#F-019)
- **用户反馈信号自动获取**：借助 agent 分析用户反馈，让流程更 AI native
- **核心原则**：不仅提升开发环节产能，更要放大最终成果 [作者观点]

## 方法论底层原则

> **从 eval 出发选择最优方案** [作者观点]：
> 1. 提出使用 agent 写代码时的具体问题 → 评估 case
> 2. 对同一 case 尝试多种解决方案反复执行
> 3. 找到更优方案（无需完整 eval suite，个人使用适度即可）

## 主题关联

- 与 [`planning-with-files`](../../planning-with-files/index.md) 互补：后者讲 3-File Pattern 文件系统外存，本篇讲 Spec+Plan 文档组合与垂直切片
- 与 [`context-optimization`](../../context-optimization/index.md) 互补：后者侧重 Token 成本优化技术，本篇侧重上下文管理的工作流策略
- 与 [`token-economy-explosion`](../../token-economy-explosion/index.md) 关联：本篇为个人视角 token 消耗实践，上篇为宏观 Token 经济规模分析

```{toctree}
:hidden:
:maxdepth: 1

01-parallel-workflow
02-large-closed-loop
03-adversarial-improvement
04-real-demand-driven
05-review-challenges
06-spec-and-plan
07-quality-assurance
```
