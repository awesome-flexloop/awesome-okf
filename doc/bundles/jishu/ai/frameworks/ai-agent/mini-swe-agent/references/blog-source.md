---
type: Reference
title: "博客信源事实清单（F-001 ~ F-034）"
description: "第三方博客《mini-SWE-agent：100 行代码如何击败了大多数 Agent 框架》的事实与观点逐条登记，含版本边界与勘误标记"
tags: [信源, 博客, mini-swe-agent, F编号, 勘误]
generated: { by: "seven-concepts-cmd/R", at: "2026-11-10T16:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: blog-mini-swe-agent
    resource: https://lukaxiya.github.io/coding-agent-blog/posts/mini-swe-agent/
    title: "mini-SWE-agent：100 行代码如何击败了大多数 Agent 框架（AI 编程实战笔记，2026-03-22）"
  - id: github-mini-swe-agent
    resource: https://github.com/SWE-agent/mini-swe-agent
    title: "SWE-agent/mini-swe-agent 官方仓库（v2.4.6）"
---

# 博客信源事实清单（F-001 ~ F-034）

> 来源层级：`博客` 表示第三方解读文章的原话或数据；`核验` 表示本次用官方仓库/文档/arXiv 做的独立比对。观点与事实分开登记，勘误在 [verification.md](verification.md) 汇总。

| 编号 | 事实或声明 | 来源层级 | 核验 |
|---|---|---|---|
| F-001 | 博客标题为《mini-SWE-agent：100 行代码如何击败了大多数 Agent 框架》，站点为 “AI 编程实战笔记”（lukaxiya.github.io/coding-agent-blog）。 | 博客 | 单源 |
| F-002 | 博客标注发布于 2026-03-22。 | 博客 | 单源 |
| F-003 | 博客称项目由 Princeton & Stanford 出品。 | 博客 | 通过（作者机构与论文署名一致，见 F-045） |
| F-004 | 博客称项目有 26k+ GitHub Stars。 | 博客 | ❌ 勘误 E-1（实际 9,496，截至 2026-11-10） |
| F-005 | 博客称项目达到 74% 的 SWE-bench verified 修复率。 | 博客 | 通过（官方 docs 同样声明 >74%，见 F-070） |
| F-006 | 博客称核心代码约 100 行。 | 博客 | ⚠️ 口径（README 同样称 100 行；实际 default.py 172 行，见 F-075、F-079） |
| F-007 | 博客称 SWE-agent 团队在 2024 年发布了 SWE-bench。 | 博客 | ❌ 勘误 E-2（SWE-bench arXiv 2310.06770 于 2023-10-10 提交） |
| F-008 | 博客称 2024 年 SWE-agent 的架构为：精心设计的 Agent-Computer Interface（ACI）、专为 LLM 优化的工具调用格式、SWE-bench 上的 SOTA。 | 博客 | 通过（SWE-agent 论文与官方定位一致） |
| F-009 | 博客提出的核心问题是：如果 Agent 框架简化 100 倍，效果还能保持吗？ | 博客 | 通过（README 原文 “What if our agent was 100x simpler”） |
| F-010 | 博客称设计原则 1 是“没有工具，只有 bash”，唯一工具是 `subprocess.run`。 | 博客 | ⚠️ 版本边界（v1/文本模式成立；v2 默认使用 bash tool call，见 F-060、F-087） |
| F-011 | 博客称设计原则 2 是“完全线性历史”，工具结果直接追加到消息历史。 | 博客 | 通过（源码 `add_messages` + `run` 循环，见 F-049） |
| F-012 | 博客称设计原则 3 是“每个动作完全独立”，不维持有状态 shell session。 | 博客 | 通过（`LocalEnvironment` 每次 `subprocess.Popen`，见 F-054） |
| F-013 | 博客称独立执行带来三个简化：调试极简（轨迹=消息历史）、沙箱极简（替换 `subprocess.run`）、扩展极简（无复杂状态机）。 | 博客 | 作者观点（与源码结构一致） |
| F-014 | 博客引用团队原话：“When LLMs have become more capable, a lot of this is not needed at all to build a useful agent!” | 博客 | 通过（README 同句） |
| F-015 | 博客数据表称 Claude 3.7 Sonnet + mini 在 SWE-bench verified 为 65%、full 为 45%。 | 博客 | 单源（未逐项复核，见 F-089） |
| F-016 | 博客数据表称 GPT-4o + mini 为 42% verified、28% full。 | 博客 | 单源 |
| F-017 | 博客数据表称 Gemini 3 Pro + mini 为 74% verified。 | 博客 | 通过（官方 docs 新闻条目，见 F-070） |
| F-018 | 博客数据表称 SWE-agent 1.0 + Claude 3.7 为 54% verified、33% full。 | 博客 | 单源 |
| F-019 | 博客称 mini 轨迹更短、token 更省，因为没有专用 tool_call schema 与中间状态序列化。 | 博客 | 作者观点 |
| F-020 | 博客对比表：SWE-agent 1.0 约 2000 行、有 ACI、树状/有状态、复杂 shell、调试与扩展难、54%；mini 约 100 行、纯 bash、线性、独立 subprocess、调试与扩展易、65%+。 | 博客 | ⚠️ 混合（代码量与结构通过；比例为单源） |
| F-021 | 博客给出伪代码类 `MiniSWEAgent`：`run()` 内构造 system/user 消息，循环 `model.generate` → `env.execute` → `messages.append`。 | 博客 | ⚠️ 示意（真实类名与返回结构不同，见 E-3） |
| F-022 | 博客列出四类环境：Local、Docker、Singularity、Contree。 | 博客 | ⚠️ 不完整（源码另有 bubblewrap、swerex_docker、swerex_modal，见 F-057） |
| F-023 | 博客结论 1：模型能力已经超过框架复杂度，专门设计的 Agent 友好接口反而可能限制模型。 | 博客 | 作者观点 |
| F-024 | 博客结论 2：线性历史 + 独立 subprocess 带来完美可重现性，消息历史即完整轨迹。 | 博客 | 作者观点（与 `serialize` 一致） |
| F-025 | 博客结论 3：极简主义不等于简单，项目解决的是真实问题。 | 博客 | 作者观点 |
| F-026 | 博客列出适合场景：GitHub Issue 修复、大规模代码迁移、研究基准、CI/CD 集成。 | 博客 | 作者观点 |
| F-027 | 博客列出不适合场景：复杂多步骤协作、需要严格权限控制、需要细致人类反馈（HITL）。 | 博客 | ⚠️ 部分过时（v2 `mini` 有 confirm/yolo/human 三模式，见 F-065） |
| F-028 | 博客快速开始为 `pip install mini-swe-agent`，使用 `MiniSWEAgent`、`result.passed`、`result.patch`。 | 博客 | ❌ 勘误 E-3（v2.4.6 无此类/字段） |
| F-029 | 博客称 Gemini 3 Pro 的 74% 来自长上下文、原生代码能力、原生工具调用。 | 博客 | 作者推断（官方未给出归因拆解） |
| F-030 | 博客总结“模型 > 框架；上下文 > 工具”。 | 博客 | 作者观点 |
| F-031 | 博客介绍 SWE-bench 的设计：从真实 GitHub Issues 采样，评估理解、定位、修复、通过测试。 | 博客 | 通过（SWE-bench 论文摘要） |
| F-032 | 博客给出能力边界表：Bug 修复（有测试）74%、性能优化差、架构设计差、多模块重构中、文档编写好。 | 博客 | 作者判断（无逐项基准） |
| F-033 | 博客列出资源：GitHub 仓库、mini-swe-agent.com、arXiv 2405.15793、swe-agent.com。 | 博客 | 通过（链接均有效） |
| F-034 | 博客声明“本文基于 2026-03-22 的最新版本”。 | 博客 | 单源（对应 v1 时代，见 F-039） |

```{toctree}
:hidden:
:maxdepth: 3

../repo-source
../verification
```
