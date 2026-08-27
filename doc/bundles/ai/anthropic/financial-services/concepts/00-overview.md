---
type: concept
title: "Claude for Financial Services 概览"
tags: [financial-services, agents, skills, mcp, connectors, cowok, managed-agents]
sources:
  - id: anthropic-financial-services
    title: Claude for Financial Services Official Repository
---

# Claude for Financial Services 概览

**Claude for Financial Services** 是 Anthropic 官方提供的金融服务行业参考库，集成了开箱即用的 agents（智能代理）、skills（技能包）和 data connectors（数据连接器），专为金融机构设计。它将金融领域的专业工作流封装成标准化的 AI 能力单元，支持两种部署模式，覆盖投研、投行、PE、财富管理、基金运营等核心金融场景。

## 产品定位

Claude for Financial Services 不是一个通用 AI 工具，而是一个**金融行业垂直领域的专业 AI 工作流参考架构**，它解决的核心问题是：如何将 Claude 的通用 AI 能力快速适配到金融机构的复杂业务流程中，同时满足合规和人工审核要求。

| 设计目标 | 具体说明 |
|---------|---------|
| **端到端工作流** | 从数据摄入、分析建模到文档生成的完整流程自动化，而非零散的单点功能 |
| **双模式兼容** | 同一套 system prompt 和 skills 支持交互式插件模式和无头 API 模式 |
| **垂直领域专业化** | Skills 和 Commands 按金融子行业（IB/ER/PE/WM/fund-admin/ops）组织，符合实际业务分工 |
| **数据生态集成** | 内置 12 个主流金融数据提供商的 MCP 连接器，开箱即用接入专业数据 |
| **合规友好** | 明确的人工审核边界，所有输出需专业人员签核，不执行交易、不提供投资建议 |

## 双模式部署架构

Claude for Financial Services 的核心设计哲学是**一套源码、两种运行方式**——所有 agents 和 skills 共用相同的 system prompt 和业务逻辑，只是部署和交互方式不同：

### 模式一：Claude Cowork 插件模式

在 claude.com 产品中作为插件安装，用户通过 Claude 的 Web 界面交互式使用。适合分析师、经理等需要人机协作的场景，用户可以在对话中引导 agent、中途调整参数、审核中间结果。

### 模式二：Claude Managed Agents API 模式

通过 `/v1/agents` API 进行无头（headless）部署，使用 `managed-agent-cookbooks/` 中的 `agent.yaml` 模板配置。适合系统集成、批量处理、自动化流水线场景，agent 作为后端服务运行，由业务系统通过 API 触发。

```
┌─────────────────────────────────────────────────────────────┐
│                    共用的 System Prompt + Skills            │
│              （plugins/agent-plugins/ + vertical-plugins/） │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
┌───────────▼───────────┐      ┌────────────▼────────────┐
│  Claude Cowork 插件   │      │  Managed Agents API     │
│  （交互式 Web 界面）  │      │  （无头 /v1/agents）    │
│  - 人工对话引导       │      │  - 系统集成触发         │
│  - 中途调整参数       │      │  - 批量自动化处理       │
│  - 实时审核中间结果   │      │  - agent.yaml 配置      │
└───────────────────────┘      └─────────────────────────┘
```

> 🔗 Managed Agents API 详见 [/python-sdk/concepts/08-beta-agents.md](../../python-sdk/concepts/08-beta-agents.md)

## 四大功能域

10 个 End-to-End Agents 按业务职能分为四大功能域，覆盖金融机构前中后台的核心工作流：

### 1. 覆盖与顾问（Coverage & Advisory）

面向前台客户-facing 团队，支持客户 pitch 和会议准备：
- **Pitch Agent**：从可比公司分析（Comps）、先例交易（precedents）、杠杆收购模型（LBO, Leveraged Buyout）到品牌化 pitch deck 的端到端生成
- **Meeting Prep Agent**：每次客户会议前自动生成简报包，包含客户背景、持仓分析、近期动态、谈话要点

### 2. 研究与建模（Research & Modeling）

面向研究和分析师团队，支持行业研究、财报分析和财务建模：
- **Market Researcher**：从行业/主题输入生成行业概览、竞争格局、可比公司分析（peer comps）、投资机会短名单（ideas shortlist）
- **Earnings Reviewer**：摄入财报电话会记录和公告，自动更新财务模型，生成研报草稿
- **Model Builder**：构建 DCF（现金流折现）、LBO、三表模型（Three-Statement Model）、可比公司分析（Comps）等实时 Excel 模型

### 3. 基金管理与财务运营（Fund Management & Financial Operations）

面向中后台基金运营和财务团队：
- **Valuation Reviewer**：摄入 GP（普通合伙人）数据包，运行估值模板，准备 LP（有限合伙人）报告
- **GL Reconciler**：查找总账差异、追踪根本原因、路由审批流程
- **Month-End Closer**：处理应计项目（accruals）、滚动结转（roll-forwards）、差异分析（variance analysis）
- **Statement Auditor**：LP 报表分发前的审计检查

### 4. 运营与开户（Operations & Onboarding）

面向运营团队，支持客户开户和合规审核：
- **KYC Screener**：解析开户文档（KYC, Know Your Customer），运行规则引擎，标记缺失项和风险点

## 9个 Vertical Plugins 垂直插件

Skills 和 Commands 按金融垂直领域组织为 9 个 vertical plugins（7个官方 + 2个合作方），每个 vertical 是一组相关技能的集合：

| 类型 | Vertical Plugin | 覆盖领域 |
|------|----------------|---------|
| **核心** | `financial-analysis` | 财务分析核心：Comps/DCF/LBO/三表模型/Deck QC/Excel审计 + 全部12个数据连接器 |
| **官方** | `investment-banking` | 投行：CIM（保密信息备忘录）/teaser/process letter/buyer list/merger model/deal tracking |
| **官方** | `equity-research` | 股票研究：Earnings notes/initiations/model updates/thesis & catalyst tracking |
| **官方** | `private-equity` | 私募股权：Sourcing/screening/diligence checklists/IC memos/portfolio monitoring |
| **官方** | `wealth-management` | 财富管理：Client reviews/financial plans/rebalancing/reporting/TLH（税损收割） |
| **官方** | `fund-admin` | 基金行政：GL recon/break tracing/accruals/roll-forwards/variance commentary/NAV tie-out |
| **官方** | `operations` | 运营：KYC文档解析和规则网格评估 |
| **合作方** | `lseg` | 伦敦证券交易所集团：债券RV/swap曲线/FX carry/期权波动率/宏观利率监控 |
| **合作方** | `sp-global` | S&P Global：Capital IQ tear sheets/earnings previews/funding digests |

> 🔗 每个 vertical 的 skills 和 commands 详见 [垂直行业Skills与Commands](02-vertical-skills.md)

## 12个 MCP 数据连接器

为支持实时金融数据接入，`financial-analysis` 核心插件内置了 12 个 MCP（Model Context Protocol）数据连接器，覆盖主流金融数据提供商：

Daloopa、Morningstar、S&P Global、FactSet、Moody's、MT Newswires、Aiera、LSEG、PitchBook、Chronograph、Egnyte、Box

> 🔗 连接器完整清单和部署方式详见 [数据连接器与部署](03-connectors-deployment.md)

## 重要免责声明与人工审核要求

Claude for Financial Services 的所有 agents 和 skills 都设计为**人机协作工具**，而非全自动决策系统。使用时必须遵守以下边界：

| ❌ Agents 不做什么 | ✅ Agents 做什么 |
|-------------------|-----------------|
| 不提供投资建议（investment advice） | 生成分析框架、整理数据、草拟文档供审核 |
| 不执行交易（execute trades） | 计算交易指标、生成交易分析报告 |
| 不绑定风险（take risk） | 进行风险指标计算和敏感性分析 |
| 不记账（bookkeeping） | 生成记账分录草稿、进行对账匹配 |
| 不审批开户（approve accounts） | 标记KYC缺失项、运行规则引擎预审核 |

> ⚠️ **所有输出必须经合格的专业人员（持牌分析师、会计师、合规官等）审核签核后才能用于正式业务。** 本仓库内容不构成投资、法律、税务或会计建议。

## 适用场景

| 机构类型 | 典型使用场景 | 推荐 Agents/Verticals |
|---------|-------------|----------------------|
| **投资银行** | Pitch deck制作、CIM撰写、并购建模、买方清单筛选 | Pitch Agent、investment-banking vertical |
| **券商研究所** | 财报季快速更新模型、撰写财报点评、行业深度研究 | Earnings Reviewer、Market Researcher、equity-research vertical |
| **私募股权基金** | 项目 sourcing、尽职调查清单、IC备忘录、投后监控 | private-equity vertical、Valuation Reviewer |
| **财富管理** | 客户组合评审、财务规划、投资建议草拟、税损收割 | wealth-management vertical、Meeting Prep Agent |
| **基金行政/外包** | 月末结账、GL对账、NAV核对、LP报表审计 | GL Reconciler、Month-End Closer、fund-admin vertical |
| **银行/券商运营** | 客户开户KYC审核、文档解析、合规预检 | KYC Screener、operations vertical |

## 仓库结构

```
claude-for-financial-services/
├── plugins/
│   ├── agent-plugins/         # 10个命名agents，每个是自包含插件
│   ├── vertical-plugins/      # 7个vertical skill/command bundles
│   └── partner-built/         # 合作方插件（lseg, sp-global）
├── managed-agent-cookbooks/   # Managed Agent部署cookbooks（每个agent一个目录）
├── claude-for-msft-365-install/  # Microsoft 365插件部署管理工具
└── scripts/                   # 部署和工具脚本
    ├── deploy-managed-agent.sh
    ├── check.py
    ├── validate.py
    ├── orchestrate.py
    └── sync-agent-skills.py
```

## 与 Anthropic 其他产品的关系

| 产品/技术 | 关系 |
|----------|------|
| **Anthropic Skills 机制** | Financial Services 的 Skills 基于官方 Skills 规范构建，是通用 Skills 在金融垂直领域的专业化封装 |
| **Claude Code 插件体系** | Claude Cowork 和 Claude Code CLI 安装遵循 Claude Code 插件标准，vertical-plugins 和 agent-plugins 本质上是预配置的插件包 |
| **Managed Agents API** | 无头部署模式通过 Claude API 的 `/v1/agents` Beta 端点实现，支持 agent.yaml 配置和 subagent delegation |
| **MCP 协议** | 数据连接器基于 Model Context Protocol 构建，与 Claude 生态的 MCP 工具链兼容 |

> 🔗 相关交叉阅读：
> - [/official-skills/concepts/00-overview.md](../../official-skills/concepts/00-overview.md) — Skills 机制详解
> - [/claude-code/concepts/01-plugin-system.md](../../claude-code/concepts/01-plugin-system.md) — 插件安装体系
> - [/python-sdk/concepts/08-beta-agents.md](../../python-sdk/concepts/08-beta-agents.md) — Managed Agents API

## 相关概念

- [10个金融Agents详解](01-agents.md) — 深入了解每个 End-to-End Agent 的功能、输入输出和包含的 skills
- [垂直行业Skills与Commands](02-vertical-skills.md) — 7个官方 vertical plugins 的 skills 和 slash commands 完整说明
- [数据连接器与部署](03-connectors-deployment.md) — 12个MCP数据连接器清单和三种部署方式详解
- [Agents与Skills完整索引](../references/agents-skills-index.md) — 所有Agents、Skills、Commands、连接器的快速查询索引
