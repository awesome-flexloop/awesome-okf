---
title: Agent 学习路线图
type: concept
bundle: /datawhale/Agent-Learning-Hub
description: Agent Learning Hub 的核心结构——9 阶段递进式 Learning Todo List 与 11 级 Project Ladder，每个阶段配有 checklist、推荐阅读和可交付产出物。
related:
  - /datawhale/Agent-Learning-Hub/concepts/resource-curation
  - /datawhale/Agent-Learning-Hub/references/source-repo
sources:
  - id: github-repo
    resource: /references/source-repo.md
    title: Agent-Learning-Hub GitHub 仓库
---

# Agent 学习路线图

Agent Learning Hub 的核心价值在于提供了一条**可执行的 AI Agent 学习路径**，而非零散的资源链接。路线图由两部分组成：**Learning Todo List**（9 阶段技能递进）和 **Project Ladder**（11 级项目阶梯），两者互补——前者按能力维度组织，后者按作品难度组织。

## Learning Todo List（Stage 0-8）

路线图从"理解 Agent 是什么"到"交付真正的 Agent"，共 9 个阶段：

| 阶段 | 主题 | 关键技能 | 产出物 |
|------|------|---------|--------|
| Stage 0 | 理解 Agent | 区分 chatbot/workflow/agent；observe→think→act 循环；何时不该用 agent | 一页短笔记 |
| Stage 1 | 最小 Agent Loop | LLM API、结构化 JSON、工具函数、tool call 解析与执行、步数/超时/错误处理 | 50-150 行最小 agent |
| Stage 2 | 工具、RAG 与记忆 | chunk/embed/retrieve/citation、多类型工具接入、短期/会话/长期记忆、失败处理 | 资料研究助手 |
| Stage 3 | 现代 Agent Harness | harness 目录结构、agent loop/tool registry/permission gate/session store/context compaction、trace 分析 | 可调试的 harness demo |
| Stage 4 | 多 Agent 协调 | planner/executor/reviewer/critic/router 角色、supervisor/graph 管理、职责边界、循环与漂移处理 | 小型多 agent 系统 |
| Stage 5 | Skills 与协议 | Skill vs Tool vs Prompt vs MCP、SKILL.md 编写、smoke test | 可复用 skill |
| Stage 6 | Browser Agent | Playwright/browser-use、安全限制、页面变化/弹窗处理、截图/DOM/日志 | 公开网页 browser agent |
| Stage 7 | 评测与安全 | 固定测试集、成功率/成本/延迟记录、trace 分析、人工确认、prompt injection 防护 | ≥20 任务的 eval 表格 |
| Stage 8 | 交付真正 Agent | 明确用户/任务/标准、日志/trace/重试/超时/成本、权限边界、部署方式、README | 别人能 clone 跑的项目 |

每个阶段的结构一致：**checklist 项**（可勾选）→ **推荐阅读**（官方文档/论文）→ **开源项目参考**（部分阶段）→ **产出物**。这种设计让学习者可以自我验证是否掌握了该阶段内容。

## Project Ladder（11 级）

项目阶梯提供了另一条学习维度——通过构建作品来学习：

| 级别 | 项目 | 核心技能 |
|------|------|---------|
| 1 | Calculator Agent | 最小 tool call loop |
| 2 | Web Research Agent | 搜索、筛选、引用、总结 |
| 3 | PDF QA Agent | RAG、chunk、retrieval、citation |
| 4 | Coding Review Agent | 读取 diff、风险排序、测试建议 |
| 5 | Browser Agent | 页面观察、点击、提取、失败恢复 |
| 6 | Claude Code-like Nano Agent | shell、文件编辑、权限、session、compact |
| 7 | OpenClaw-like Gateway | channel、routing、session、memory、heartbeat |
| 8 | Reusable Skill Pack | SKILL.md、脚本、模板、触发条件、smoke test |
| 9 | Multi-Agent Writer | planner、writer、reviewer 协作 |
| 10 | Personal Agent | 记忆、skills、消息入口 |
| 11 | Production Harness | evals、trace、权限、CI、runner、回放 |

## 当前优先方向

路线图明确标注了当前更值得投入的 5 个方向：

1. **Claude Code / Codex-style coding agents**——最好的 agent 工程样本
2. **Agent harness engineering**——工具协议、权限、状态、反馈、回放、CI、评测
3. **OpenClaw / Hermes-style personal agents**——长运行、本地优先、跨应用、记忆
4. **Skills / MCP / A2A / ACP**——能力复用与标准化连接
5. **Evaluation and safety**——没有 eval/trace/权限边界的 agent 只能算 demo

同时明确不建议把精力重押在老式 crew/role-play 框架上。

## 四类使用方式

- **新手**：从 Stage 0 开始，按顺序完成每个 checklist 项
- **有 LLM 经验者**：从 Stage 2 或 Stage 3 切入，重点补 agent loop、工具调用、评测和工程化
- **做项目者**：直接参考 Project Ladder，每档做一个可运行作品
- **找资料者**：浏览 [核心资源分类](resource-curation.md)，优先读官方文档和经典论文

## 相关概念

- [核心资源分类](resource-curation.md)——路线图各阶段引用的官方指南、开源项目、论文和博客的分类体系
- [信源登记](../references/source-repo.md)——项目 GitHub 仓库与文件结构说明
