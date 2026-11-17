---
type: Concept
title: CrewAI 与 Microsoft Agent Framework
description: 角色型多 Agent 的速度取舍，与 MAF 合并 Semantic Kernel/AutoGen 后的企业架构、语言对齐和协议能力
tags: [CrewAI, Microsoft Agent Framework, 多Agent, Semantic Kernel, AutoGen, A2A, MCP]
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T14:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: maf-blog
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
  - id: maf-learn
    resource: https://learn.microsoft.com/en-us/agent-framework/overview/
---

# CrewAI 与 Microsoft Agent Framework

这两个框架代表相反的下注：CrewAI 把复杂度藏在“角色”后面，MAF 把复杂度收进“企业基础设施”。放在一起看，更容易理解“速度”和“治理”之间的交换。

## CrewAI：用角色换速度

CrewAI 不画图。你描述一个 crew：researcher、writer、reviewer，各自有 role/goal/backstory，然后框架编排它们协作（F-024）。原文称这是最容易上手的多 Agent 团队搭建方式（F-025），并转述团队反馈“从想法到生产不到一周”（F-026）。

这条“一周”没有客户名与项目细节，属于作者/厂商自述，不能当作基准（F-080）。但它的机制解释是成立的：角色抽象把“谁在什么时候做什么”变成自然语言配置，省掉了状态机与边的设计成本。

代价同样明确（F-027、F-028）：

1. 角色 crew 行为异常时，可用的精确杠杆少于图模型。
2. 复杂分支逻辑会与角色抽象打架。
3. 一旦需要持久化、精确重试、审计每一步，往往要迁移到图框架。

因此原文的定位是“第一站”而不是“终点”：PoC、内部工具、角色能自然映射的流程先用 CrewAI；需要可靠运行的部分再迁到 LangGraph，并为重写留预算（F-029）。

## Microsoft Agent Framework：结束分叉的企业合并

MAF 1.0 于 2026 年 4 月 3 日发布，把微软自己的两条线合并了：企业向的 Semantic Kernel 与研究向的 AutoGen（F-030、F-031）。微软的表述是“Semantic Kernel 的企业级基础 + AutoGen 的创新编排”，落成稳定 API 与长期支持（F-032）。

### 分层架构

1. **基础层**：Semantic Kernel 提供会话状态、类型安全、中间件、遥测（F-033）。
2. **编排层**：AutoGen 风格的图工作流，用于显式多 Agent 编排（F-034）。

这等于把“企业管道”和“研究型协作”装进同一个 SDK，而不是让团队自己粘。

### 对企业最实际的两点

1. **.NET 与 Python 一等公民对齐**：C# 团队不再追着 Python 功能集跑（F-035）。对已经把 Azure/.NET 作为标准栈的组织，这是决定性因素（F-039）。
2. **协议与模型连接器**：MCP 原生；A2A 已有集成，但 1.0 公告同时写明“A2A 1.0 support coming soon”，所以“A2A 完全原生”是过度表述（F-036、F-074）。模型侧开箱支持 Azure OpenAI、OpenAI、Anthropic Claude、Amazon Bedrock、Google Gemini、Ollama 六个连接器（F-037、F-073）；“一行代码切换”是宣传语，实际还涉及认证、能力差异与回归测试（F-038）。

### 时点更新（2026-10）

Microsoft Learn 当前版本已新增 Go 公开预览，连接器以 Microsoft Foundry 为第一方入口；.NET/Python 对齐仍成立（F-078）。如果你在 2026 年底做选型，应以这一版文档为准，而不是只读 4 月的 1.0 公告。

## 怎么在这两者之间选

| 你的处境 | 更合适 | 理由 |
|---------|--------|------|
| 两周内验证角色协作想法 | CrewAI | 角色抽象省掉图设计成本（F-024、F-026） |
| 已标准化在 Azure/.NET | MAF | 语言对齐、会话状态、企业中间件与遥测（F-033、F-035、F-039） |
| 需要精确分支与逐步审计 | 两者都不如 LangGraph | MAF 有图工作流，但企业集成层更重；LangGraph 更贴近“纯编排” |
| 需要跨 .NET 与 Python 团队协作 | MAF | 同一 API 的双语言一等支持（F-035） |

## 与本站其他知识包的关系

- MAF 的完整官方文档教程见 [microsoft-agent-framework](../../../microsoft-agent-framework/index.md)（10 概念 + 5 示例）。
- 角色型多 Agent 的编排模式可对照 [agency-agents](../../agency-agents/index.md) 与 [orca](../../orca/index.md)。
- A2A/MCP 的协议分工见 [a2a-mcp-convergence](../../a2a-mcp-convergence/index.md)。
