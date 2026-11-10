---
type: Concept
title: "评测与边界：74% 到底证明了什么"
description: "SWE-bench verified 的 74% 成绩、博客对比表的单源边界、能力边界表，以及极简 Agent 不擅长什么"
tags: [SWE-bench, 74%, 评测, 能力边界, Gemini 3 Pro, 基准]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:01:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: blog-mini-swe-agent
    resource: /references/blog-source.md
    title: "博客事实清单（F-001 ~ F-034）"
  - id: repo-mini-swe-agent
    resource: /references/repo-source.md
    title: "仓库事实清单（F-035 ~ F-100）"
  - id: verification
    resource: /references/verification.md
    title: "P0 核验报告"
---

# 评测与边界：74% 到底证明了什么

> 74% 是 mini 最响亮的标签，也是最容易被误读的数字。它证明的是“在 SWE-bench verified 的特定子集、特定模型、特定评测配置下，这个极简脚手架能修好约四分之三的 Issue”，不是“任何模型装上 mini 都能 74%”。

## 1. SWE-bench 是什么

SWE-bench 从真实 GitHub Issues 采样，给模型一个代码库和一条 Issue，要求它修改代码使对应测试通过（F-031）。它测的不是“写一段算法”，而是：

1. 读懂 Issue 与仓库结构。
2. 定位相关文件与函数。
3. 写出能过测试的补丁。
4. 处理边界条件与回归。

SWE-bench verified 是其人工校验子集，常用于对比 Agent 的“真实修 Bug”能力（F-070）。

## 2. 74% 的来源与口径

| 项 | 内容 | 证据 |
|---|---|---|
| 官方声明 | “Scores >74% on the SWE-bench verified benchmark” | F-070 |
| 官方新闻 | “Nov 19: Gemini 3 Pro reaches 74% on SWE-bench verified with mini-swe-agent!” | F-070 |
| 博客表述 | Gemini 3 Pro + mini = 74% verified | F-017 |
| 未公开项 | 模型快照、成本上限、步数上限、重试策略、容器架构、评测日期 | F-088 |

因此，正确的引用方式是：

> 在官方公布的 SWE-bench verified 评测中，Gemini 3 Pro 搭配 mini-swe-agent 达到 74%；官方未公开完整评测配置，该数字不应直接外推到其它模型或其它日期。

### 博客对比表（单源）

| 组合 | verified | full | 证据 |
|---|---|---|---|
| Claude 3.7 Sonnet + mini | 65% | 45% | F-015（单源） |
| GPT-4o + mini | 42% | 28% | F-016（单源） |
| Gemini 3 Pro + mini | 74% | — | F-017（官方佐证） |
| SWE-agent 1.0 + Claude 3.7 | 54% | 33% | F-018（单源） |

这张表的教学价值在于**趋势**：同一脚手架下，模型能力差异远大于框架差异；但具体数字除 74% 外都未逐项复核（F-089），引用时要标注“博客单源”。

## 3. 为什么极简反而高分

博客与 README 给出的解释（F-023、F-029、F-030）：

1. **强模型已经会使用 bash**：不需要为它设计 `read_file`/`edit_file` 之类的“Agent 友好”接口；这些接口反而可能限制它的表达。
2. **线性历史减少信息损失**：没有历史压缩、没有树状分支，模型看到的上下文就是真实执行序列。
3. **失败即反馈**：格式错误、命令失败、测试不通过都进入同一条历史，模型下一轮可以直接修正。
4. **脚手架不抢戏**：没有 planner 的硬编码策略，模型的能力上限就是系统的上限。

反过来说，这也意味着：**当模型不够强时，mini 不会“救”它**。没有工具封装、没有结构化重试、没有领域知识注入，弱模型会在 shell 语法、文件定位、测试理解上反复失败。

## 4. 能力边界

博客给出的边界表（F-032，作者判断）：

| 任务类型 | 表现 | 原因 |
|---|---|---|
| Bug 修复（有测试） | 74% | 目标明确、反馈闭环、可验证 |
| 性能优化（无明确目标） | 差 | 缺少基线、指标与搜索策略 |
| 架构设计（需业务理解） | 差 | 需要领域知识与长期权衡 |
| 多模块重构（需全局视图） | 中 | 线性上下文容易丢失跨文件关系 |
| 文档编写 | 好 | 文本生成是模型强项，验证成本低 |

补充三条来自实现的边界：

1. **不能持久 `cd`/`export`**：每条命令独立，复杂环境准备要写进每条命令或脚本（F-072）。
2. **不做上下文压缩**：长任务会撞上下文窗口；需要外部截断或换更大窗口模型（F-011）。
3. **不做权限审批**：默认 `DefaultAgent` 没有确认层；`mini` CLI 的 confirm 模式是 `InteractiveAgent` 提供的（F-065、F-066）。

## 5. 不适合的场景

| 场景 | 为什么不适合 | 替代方向 |
|---|---|---|
| 复杂多步骤协作 | 没有多 Agent 编排、任务分解、共享黑板 | 多 Agent 框架 / 编排层 |
| 严格权限控制 | 无命令白名单、无审批、无网络策略 | 带 policy 的 harness + 容器 |
| 需要细致 HITL | 默认 Agent 无交互；CLI 只有粗粒度 confirm | InteractiveAgent 定制 / 人工审核流程 |
| 长程项目级重构 | 线性历史 + 无记忆，跨天任务会丢上下文 | 带持久记忆/计划文件的 Agent |
| 非代码任务 | 只给 bash，没有浏览器/API 工具 | 专用工具型 Agent |

## 6. 如何自己复现评测

官方提供批处理与单实例两条路径（F-068、F-069）：

```bash
# 全量批处理
mini-extra swebench \
  --model anthropic/claude-sonnet-4-5-20250929 \
  --subset verified --split test --workers 4

# 单实例调试
mini-extra swebench-single \
  --subset verified --split test \
  -m anthropic/claude-sonnet-4-5-20250929 \
  -i sympy__sympy-15599
```

注意：

1. Docker 镜像默认按 x86 Linux 构建，非 x86 架构可能跑不起来。
2. 需要设置对应模型的 API Key；批量运行会真实计费。
3. `preds.json` 只是预测补丁，最终分数要用 SWE-bench 官方评测器算。
4. 本知识包未在本机执行评测；以上命令来自官方文档（F-068、F-069）。

## 7. 一句话总结

74% 是“强模型 + 极简脚手架 + 特定评测配置”的联合结果。它最大的启示不是“框架不重要”，而是**当模型足够强时，框架的边际收益下降，透明度和可调试性变得更值钱**。
