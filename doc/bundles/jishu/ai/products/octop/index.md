---
okf_version: "0.2"
type: bundle
title: "Octop：腾讯云开源的本地 AI 工作空间"
description: "腾讯云开源（MIT）自托管多用户、多 Agent AI 助手平台——单进程架构与 Harness 四组件（agent/gateway/memory/browser）、AI 专家团队与长期记忆、RAG 知识库、Browser/Terminal/远程桌面/ACP 工具与多渠道接入，含安装实操（源自微信博文经官方一手核验 17✅/3⚠️/0❌）"
tags: [octop, ai-agent, multi-agent, self-hosted, local-first, long-term-memory, rag, browser-automation, acp, tencent, 博文转化]
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T10:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T10:00:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
    title: 腾讯云开源的本地 AI 工作空间
    account: 智能猩猩AI
  - id: github-repo
    url: "https://github.com/TencentCloud/Octop"
  - id: github-api
    url: "https://api.github.com/repos/TencentCloud/Octop"
  - id: official-home
    url: "https://tencentcloud.github.io/Octop/"
  - id: pypi
    url: "https://pypi.org/project/octop/"
---

# Octop：腾讯云开源的本地 AI 工作空间

> **类型**：技术教程/选型（含可照做 examples/，操作可复现性两问皆"是"，但未在本机实测）
> **信源**：微信公众号「智能猩猩AI」博文（2026-09 期间，成文于 Octop 1.0 GA 之后）→ 2026-10-10 经 GitHub API、官方项目主页与 PyPI 逐项核验
> **核验结论**：20 项 P0/P1 声明 **17✅ / 3⚠️ / 0❌**，无核心声明失败
> **数据时点**：Star 等动态数字为 2026-10-10 GitHub API 快照；功能口径对齐 main 与 v1.0.0

## 本文概要

[Octop](https://github.com/TencentCloud/Octop) 是腾讯云开源的（**MIT**、2026-07-10 正式开源）**自托管多用户、多 Agent AI 助手平台**。它把 AI 助手从「单次对话工具」演进为「可长期使用、可持续扩展」的工作平台：一个 Python 进程承载 Web 控制台、CLI、IM 渠道与定时调度（共享 SQLite），由 **Harness 四组件**（`harness-agent`、`harness-gateway`、`harness-memory`、`harness-browser`）组合而成。在此之上提供**多专业 Agent 专家团队**、**长期记忆（层级召回+全文检索）**、**RAG 知识库**、**Browser/Terminal/远程桌面/ACP 工具调用**与**多渠道接入**能力。

## 阅读路径

**先建立概念（10 分钟）**

1. [Octop 是什么：项目身份与定位](concepts/00-what-is-octop.md)——定位、归属、MIT 许可、热度（带时点）
2. [单进程架构与 Harness 组件](concepts/01-architecture-and-harness.md)——为什么单进程自托管，四大组件各管什么
3. [多 Agent 专家与长期记忆](concepts/02-multi-agent-and-memory.md)——从单聊天机器人到 AI 专家团队、RAG 知识库与用户隔离

**关键子特性**

4. [工具调用与多渠道接入](concepts/03-tools-and-channels.md)——Browser/Terminal/远程桌面/ACP 与 IM 多渠道、定时任务

**再动手实操**

5. [安装与快速上手](concepts/04-install-and-run.md) / [实操示例](examples/00-install-and-run.md)——安装、初始化、启动、登录、配置模型

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 归属 | [TencentCloud/Octop](https://github.com/TencentCloud/Octop)（腾讯云官方组织） |
| 开源时间 / 许可 | 2026-07-08 创建，2026-07-10 正式开源 / **MIT** / Python 3.12+ |
| 源码脉络 | 源自 LightClaw ACE，面向智能体时代系统重构 |
| 社区数据 | Star 8292、Fork 1006、Open Issues 697（**2026-10-10 时点**；博文口径 7.9k） |
| 技术栈 | 后端 FastAPI+uvicorn；前端 React+TS+Vite+AntD；Agent 运行时 LangGraph |
| 架构 | 单 Python 进程承载 Web/CLI/IM/定时；控制面 SQLite（可选 PostgreSQL）；无外部队列 |
| 四大组件 | harness-agent / harness-gateway / harness-memory / harness-browser |
| 能力 | 多 Agent 专家、长期记忆、RAG 知识库、Browser/Terminal/远程桌面、ACP 双向集成、MCP、多渠道（IM/HTTP/SSE/WebSocket）、APScheduler 定时 |
| 默认入口 | 自托管 `octop run` 后访问 `http://127.0.0.1:8088` |

## ⚠️ 阅读前必知的三条口径勘误

1. **Star 数**：博文"7.9k"为成文时口径，本知识包采用官方现值 **8292（2026-10-10）**，动态数字引用须带时点。
2. **四组件命名**：博文称「Octop Harness/Memory/Browser/Gateway」；官方 Harness 细粒度命名为 `harness-agent`/`harness-memory`/`harness-browser`/`harness-gateway`，本包以官方命名为主（见 [01 架构](concepts/01-architecture-and-harness.md)）。
3. **安装脚本托管渠道**：博文安装脚本 URL 为腾讯云 COS 域名，属于可能更新的托管渠道；实操以官方文档当前命令为准（见 [04 安装](concepts/04-install-and-run.md)）。

## 采用提示与已知边界

- **MIT 许可**：宽松，可自由使用、修改、商用（含修改后的 SaaS），比 AGPL 类项目更适合内嵌；仍建议商用前做 License 复核（许可为官方标注，非法律意见）。
- **面向自托管小规模**：单进程模型为家庭/小团队设计，超大并发受单进程吞吐限制（推断，见 [01 架构·边界](concepts/01-architecture-and-harness.md)）。
- **博文特点是「整理摘要」而非「厂商原文」**：信源为第三方 AI 资讯整理号（智能猩猩AI），产品能力与命令经官方一手交叉核验；配图内嵌文字未采集。
- **数字时效**：Star/版本为 2026-10-10 核验时点快照，`stale_after: 2026-12-31`，到期前复核。

## 信源与可信度

- 事实清单与逐条核验状态：[references/facts.md](references/facts.md)（F-001~F-043）
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 信源登记与公开性预检：[references/source-manifest.md](references/source-manifest.md)

## 主题关联

- [todesk-ai](../todesk-ai/index.md)：跨设备 AI 助手的 Computer Use 工具化实践（Agent 工具生态相邻话题）
- [wigolo](../wigolo/index.md)：AI Agent 本地 Web 情报层（同为自托管、local-first 的 Agent 基础设施）
- [loopx](../loopx/index.md)：长程 Agent 控制面（与本包"多 Agent 长期工作平台"主题相邻）
- [orca-ade](../orca-ade/index.md)：多 Agent 桌面工作台（Agent 编排工作区形态对比）
- [coze](../../ecosystems/coze/index.md)：通过对话定义产品需求的 Agent 平台（多 Agent 生态另一形态）

```{toctree}
:maxdepth: 2
:hidden:

concepts/index
examples/index
references/index
log
```