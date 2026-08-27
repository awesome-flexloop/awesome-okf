---
okf_version: "0.2"
type: index
title: "Claude for Financial Services 金融服务行业库"
description: "Anthropic官方金融服务行业参考agents/skills/data connectors库中文文档——10个端到端金融Agents、9个垂直行业插件、12个MCP数据连接器、双模式部署架构（Cowork插件+Managed Agents API）详解。"
tags: [financial-services, agents, skills, mcp, connectors, investment-banking, equity-research, private-equity, wealth-management, fund-admin]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# Claude for Financial Services 金融服务行业库

**Claude for Financial Services** 是 Anthropic 官方提供的金融服务行业参考 agents/skills/data connectors 库，专为投行、券商、PE、财富管理、基金运营等金融机构设计。该库提供开箱即用的端到端 AI 工作流，覆盖从 pitch deck 制作、财报分析、估值建模到基金对账、KYC 审核的全流程金融业务场景。

## 金融服务 AI 生态核心概念

| 概念 | 说明 |
|------|------|
| **双模式部署** | Claude Cowork 插件模式（在 claude.com 中安装）+ Claude Managed Agents API 模式（通过 `/v1/agents` API 无头部署），一套源码两种运行方式 |
| **10个 End-to-End Agents** | 自包含的端到端工作流插件，自动绑定所需 skills，覆盖四大功能域 |
| **9个 Vertical Plugins** | 按金融垂直领域组织的 Skills + Commands 技能包，含7个官方vertical + 2个合作方插件 |
| **12个 MCP 数据连接器** | 集成主流金融数据提供商（Daloopa、Morningstar、S&P Global、FactSet等），集中在 financial-analysis 核心插件 |
| **人工审核要求** | 所有输出需经合格专业人员审核；agents 不提供投资建议、不执行交易、不绑定风险、不记账、不审批开户 |

## 四大功能域

| 功能域 | 覆盖场景 | 包含 Agents |
|--------|----------|-------------|
| **覆盖与顾问** | Pitch deck 制作、客户会议准备 | Pitch Agent、Meeting Prep Agent |
| **研究与建模** | 行业研究、财报分析、估值建模（DCF/LBO/三表模型） | Market Researcher、Earnings Reviewer、Model Builder |
| **基金管理与财务运营** | GP包估值、GL对账、月末结账、LP报表审计 | Valuation Reviewer、GL Reconciler、Month-End Closer、Statement Auditor |
| **运营与开户** | KYC 文档解析与规则引擎审核 | KYC Screener |

## 文档导航

### 📚 概念文档（4 篇）

| 主题 | 说明 |
|------|------|
| [Claude for Financial Services概览](concepts/00-overview.md) | 产品定位、双模式架构详解、四大功能域介绍、免责声明、适用场景、与Anthropic其他产品的关系 |
| [10个金融Agents详解](concepts/01-agents.md) | Agent概念、按四大功能域分节介绍每个Agent的功能、输入输出、包含的skills、Managed Agent部署方式 |
| [垂直行业Skills与Commands](concepts/02-vertical-skills.md) | Vertical插件概念、7个官方vertical详解（financial-analysis核心→IB→ER→PE→WM→fund-admin→ops）、Skills同步机制 |
| [数据连接器与部署](concepts/03-connectors-deployment.md) | 12个MCP数据连接器清单、Claude Cowork/Code CLI/Managed Agents API三种部署方式、Microsoft 365插件、自定义扩展方法 |

### 📖 参考文档（1 篇）

| 参考 | 说明 |
|------|------|
| [Agents与Skills完整索引](references/agents-skills-index.md) | 10个Agents表 + 7个Vertical Plugins的Skills/Commands对照表 + 12个MCP连接器表的完整索引 |

## 与其他子 bundle 的交叉链接

| 相关 bundle | 链接 | 关系说明 |
|------------|------|---------|
| **Anthropic 官方 Skills 库** | [/official-skills/concepts/00-overview.md](/official-skills/concepts/00-overview.md) | Financial Services 的 Skills 机制基于官方 Skills 规范构建，是通用 Skills 在金融垂直领域的专业化封装 |
| **Claude Code Wiki** | [/claude-code/concepts/01-plugin-system.md](/claude-code/concepts/01-plugin-system.md) | Claude Cowork 和 Claude Code CLI 插件安装遵循 Claude Code 插件体系规范 |
| **Python SDK Wiki** | [/python-sdk/concepts/08-beta-agents.md](/python-sdk/concepts/08-beta-agents.md) | Managed Agents API 模式通过 Python SDK 的 `/v1/agents` Beta API 实现无头部署 |

## 重要免责声明

> ⚠️ **本仓库内容不构成投资、法律、税务或会计建议。** 所有输出需经合格专业人员审核。Agents 不做投资建议、不执行交易、不绑定风险、不记账、不审批开户——每个输出都需人工签核。

完整变更记录见 [log.md](log.md)。

```{toctree}
:maxdepth: 3

concepts/index
references/index
log
```
