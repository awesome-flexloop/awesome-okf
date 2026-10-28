---
okf_version: "0.2"
type: Concept
title: "插件三形态选型：Skills（知识）× Tools（执行）× Hooks（生命周期）"
description: "Agent 插件的三种正交形态定义与选型矩阵——知识型（SKILL.md 渐进披露）、执行型（entry points/MCP Tools）、生命周期型（pluggy 钩子）；上下文成本与故障半径双轴选型"
tags: [Agent插件, Skills, Tools, Hooks, 上下文工程, 选型矩阵]
generated: { by: "agent/seven-concepts-research", at: "2026-10-28T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T18:00:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: mcp-spec-2026
    resource: https://modelcontextprotocol.io/specification/2026-07-28
  - id: anthropic-skills
    resource: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
  - id: pluggy-docs
    resource: https://pluggy.readthedocs.io/en/stable/
---

# 插件三形态选型：Skills（知识）× Tools（执行）× Hooks（生命周期）

把 Agent 的「插件」都当「工具」是最常见的形态错配。三形态各自回答不同的问题：

| 形态 | 回答的问题 | 载体 | 消费者 | 失配代价 |
|------|-----------|------|--------|---------|
| **Skills（知识）** | 「这类任务该怎么做？」 | SKILL.md（文档） | 模型阅读 | 当 Tool 用 → 上下文爆炸（知识被塞进系统提示词） |
| **Tools（执行）** | 「这个动作谁能做？」 | 函数/服务（代码） | 模型调用 | 当 Skill 用 → 能力缺失（模型知道该做但做不了） |
| **Hooks（生命周期）** | 「这个时机该发生什么？」 | 钩子实现（代码） | 宿主调度 | 当 Tool 用 → 人类流程无法自动化（要靠模型自觉） |

三形态**正交**：一个完整能力可以同时是三者——例如「日报生成」能力 = 一个 Skill（日报格式规范）+ 一个 Tool（数据聚合函数）+ 一个 Hook（每日 18:00 触发）。

## 上下文成本轴：为什么知识必须渐进披露

Agent 的系统上下文是稀缺资源。三种形态的上下文成本模型：

- **Skill（渐进披露）**：常驻成本 = 名称 + 一行描述（frontmatter）；正文与脚本按需加载——成本随任务相关性伸缩。
- **Tool schema**：工具的名称/描述/参数 schema 常驻（供模型选择调用）；执行结果按调用产生。
- **Hook**：几乎零上下文成本——它根本不经过模型，由宿主在确定时机执行。

**选型第一问：这个能力需要模型「知道」还是「会做」还是「无需知道地发生」？** 知识塞进常驻上下文（CLAUDE.md 式全量注入）会在技能数量增长时线性侵蚀上下文——渐进披露（项目级 `.claude/skills/` 目录 + frontmatter 常驻 + 正文按需）是规模化路径。

## 故障半径轴：执行型内部的再分层

执行型能力（Tools）内部按故障半径再分层：

| 层 | 机制 | 故障传播 | 适用 |
|----|------|---------|------|
| 同进程函数 | entry points 注册 | 异常直接抛进宿主调用栈 | 自研、测试覆盖的核心能力 |
| 同进程钩子 | pluggy hookimpl | 异常可被钩子机制包裹处理 | 宿主流程切面（日志/审计/重试） |
| 子进程服务 | MCP stdio | Server 崩溃 = 该工具不可用，宿主存活 | 重依赖（浏览器/OCR/DB）、不可信或第三方 |
| 远程服务 | MCP Streamable HTTP | 同上 + 网络故障域 | 团队共享、云端能力 |

## 三形态 × 四机制选型矩阵

| | entry points | pluggy | MCP | Agent Skills |
|---|:---:|:---:|:---:|:---:|
| **Skills（知识）** | ✗ | ✗ | △ Skills over MCP 扩展 | ✅ 原生形态 |
| **Tools（执行）** | ✅ 进程内注册 | △（可但非本职） | ✅ 原生形态（Tools 特性） | ✗ |
| **Hooks（生命周期）** | △ 手工约定 | ✅ 原生形态（hookspec） | △ Tasks 扩展（异步长任务） | ✗ |

（✅ 原生最优；△ 特定条件下可行；✗ 不适用）

**MCP 的 Tasks 扩展**覆盖了「长时间执行的生命周期任务」（轮询、中途输入、持久句柄），但会话级钩子（如「每次工具调用后写审计日志」）仍是 pluggy/宿主内钩子的领地——跨进程做不到零延迟切面。

## 形态错配的三个真实症状

1. **上下文爆炸**：系统提示词里塞了三十段「使用说明」——该拆成 Skills 目录，常驻只剩三十行目录。
2. **能力幻觉**：模型详细描述了「该怎么做日报」但从不产出日报——知识有了，缺 Tool。
3. **人工兜底**：每次都靠人记得触发某个流程——缺 Hook，流程没有宿主侧的确定性触发点。

## 关键要点回顾

- 三形态正交：知识（模型知道）、执行（模型会做）、生命周期（无需模型知道地发生）。
- 上下文成本轴决定知识型能力必须渐进披露；故障半径轴决定执行型能力的进程边界。
- 完整能力 = Skill + Tool + Hook 三件套；只做其中一件是 MVP，三件齐是产品化。
- 选型顺序：先定形态（三选一或组合），再定机制（四谱选一）——反过来做是框架先行的常见错误。
