---
type: concept
title: "10个金融Agents详解"
tags: [financial-services, agents, pitch, market-research, earnings, model-builder, kyc, fund-admin]
sources:
  - id: anthropic-financial-services-agents
    title: Claude for Financial Services Agent Plugins
---

# 10个金融Agents详解

在 Claude for Financial Services 中，**Agents（智能代理）** 是端到端工作流的自包含插件，每个 agent 自动绑定完成特定业务流程所需的全部 skills、commands 和数据连接器。用户只需提供顶层输入，agent 就能自主编排工作流、调用相关技能、生成最终产出物。

## Agent 概念

Agents 与孤立的 Skills/Commands 的关键区别在于：Agents 封装了**完整的业务工作流**，包含多步骤的任务编排、子代理委托（subagent delegation）、上下文管理和输出生成。

| 特性 | Agents | Skills/Commands |
|------|--------|----------------|
| **封装粒度** | 端到端工作流（如"生成pitch deck"） | 单点能力（如"做DCF模型"、"生成teaser"） |
| **使用方式** | 用户触发顶层任务，agent 自主编排 | 用户显式调用或按场景自动触发 |
| **包含资源** | 自动绑定所需全部skills + commands + 连接器 | 单个技能包或单个斜杠命令 |
| **部署方式** | Cowork插件 + Managed Agent API双模式 | 随vertical插件分发 |

每个 agent 在 `plugins/agent-plugins/` 下是一个自包含目录，同时在 `managed-agent-cookbooks/` 下有对应的 `agent.yaml` 配置用于 API 部署。

## 四大功能域 Agents 详解

---

### 功能域一：覆盖与顾问（Coverage & Advisory）

#### 1. Pitch Agent

**功能描述**：从可比公司分析（Comps, Comparable Company Analysis）、先例交易（precedent transactions）、杠杆收购模型（LBO, Leveraged Buyout）到品牌化 pitch deck 的端到端生成流水线。

**典型输入**：目标公司名称、交易类型（并购/融资/IPO）、行业分类、品牌模板偏好
**典型输出**：完整的品牌化 pitch deck（PowerPoint格式），包含Comps表格、估值分析、交易结构、卖点叙述
**包含的核心 Skills/Commands**：
- `pitch-deck`（投影片生成）
- `comps-analysis`（可比公司分析）
- `datapack-builder`（数据包构建）
- `pptx-author`（PowerPoint创作）
- `ib-check-deck`（投行deck质量检查）
- `strip-profile`（公司简介提取）
- `merger-model`（并购模型，如适用）

**主要依赖 Verticals**：`investment-banking`、`financial-analysis`

**Managed Agent 部署**：使用 `managed-agent-cookbooks/pitch-agent/agent.yaml`，支持 API 触发批量生成 pitch 材料。

---

#### 2. Meeting Prep Agent

**功能描述**：每次客户会议前自动生成定制化的简报包（briefing book），帮助客户覆盖团队快速准备会议。

**典型输入**：客户/公司名称、会议日期、会议类型（初次拜访/季度评审/项目跟进）、参会人员
**典型输出**：会议简报包，包含客户背景、持仓/敞口分析、近期新闻和公告、财报摘要、关键谈话要点、准备好的问题清单
**包含的核心 Skills/Commands**：
- `client-review`（客户评审，财富管理场景）
- `morning-note`（晨会纪要风格摘要）
- `competitive-analysis`（竞争分析）
- `pptx-author`/`xlsx-author`（文档生成）

**主要依赖 Verticals**：`wealth-management`、`equity-research`、`financial-analysis`

**Managed Agent 部署**：可与日历系统集成，在会议前自动触发。

---

### 功能域二：研究与建模（Research & Modeling）

#### 3. Market Researcher

**功能描述**：针对特定行业或投资主题，生成完整的行业研究概览，包括市场格局、竞争态势、可比公司分析和投资机会筛选。

**典型输入**：行业名称/主题（如"AI基础设施"、"欧洲可再生能源"、"美国地区银行"）、研究范围、关注维度
**典型输出**：
- 行业概览报告（市场规模、增长驱动因素、监管环境）
- 竞争格局分析（主要玩家、市场份额、竞争优势）
- Peer comps（可比公司）表格和估值比较
- Ideas shortlist（投资机会短名单）
**包含的核心 Skills/Commands**：
- `sector-overview`（板块概览）
- `competitive-analysis`（竞争分析）
- `comps-analysis`（可比分析）
- `idea-generation`（投资机会筛选）
- `pptx-author`/`xlsx-author`

**主要依赖 Verticals**：`equity-research`、`financial-analysis`

**数据连接器使用**：通过 MCP 连接器从 Morningstar、S&P Global、FactSet、PitchBook 获取行业和公司数据。

---

#### 4. Earnings Reviewer

**功能描述**：财报季专用 agent，摄入财报电话会议（earnings call）记录和公司公告，自动更新财务模型并生成研报草稿。

**典型输入**：公司名称/股票代码、财报季度、电话会议转录/链接、公告文件
**典型输出**：
- 更新后的 Excel 财务模型（三表 + 关键指标）
- 财报点评研报草稿（earnings note）
- 实际vs预期对比分析（actual vs consensus）
- 管理层指引变化摘要
- 电话会议关键Q&A摘录
**包含的核心 Skills/Commands**：
- `earnings-analysis`（财报分析）
- `model-update`（模型更新）
- `morning-note`（财报点评风格）
- `clean-data-xls`（Excel数据清洗）
- `audit-xls`（模型审计检查）
- `xlsx-author`

**主要依赖 Verticals**：`equity-research`、`financial-analysis`

**数据连接器使用**：Aiera（财报电话会）、MT Newswires（新闻）、Morningstar/FactSet（预期数据）。

---

#### 5. Model Builder

**功能描述**：构建和维护各类标准金融模型的 Excel 实时建模 agent，支持 DCF、LBO、三表模型、可比公司分析等。

**典型输入**：公司名称、模型类型（DCF/LBO/三表/Comps/合并模型）、历史财务数据、关键假设
**典型输出**：
- 完整格式化的 Excel 模型文件（.xlsx）
- 公式链接正确、格式专业、含敏感性分析
- DCF：WACC计算、自由现金流预测、终值计算、敏感性表格
- LBO：收购价格、债务结构、退出回报、信用比率
- 三表：利润表、资产负债表、现金流量表完整链接
- Comps：可比公司交易倍数、估值区间
**包含的核心 Skills/Commands**：
- `dcf-model`（DCF模型，`/dcf`）
- `lbo-model`（LBO模型，`/lbo`）
- `3-statement-model`（三表模型，`/3-statement-model`）
- `comps-analysis`（可比分析，`/comps`）
- `merger-model`（合并模型，`/merger-model`）
- `audit-xls`（模型调试审计，`/debug-model`）
- `clean-data-xls`（数据清洗）
- `xlsx-author`（Excel创作）

**主要依赖 Verticals**：`financial-analysis`（核心）、`investment-banking`、`private-equity`

**Managed Agent 部署**：可作为API服务接收模型构建请求，批量生成标准化模型模板。

---

### 功能域三：基金管理与财务运营（Fund Management & Financial Operations）

#### 6. Valuation Reviewer

**功能描述**：面向私募股权和基金运营团队，摄入 GP（普通合伙人）提供的估值数据包，运行估值模板，准备 LP（有限合伙人）报告。

**典型输入**：GP估值数据包（PDF/Excel）、基金结构、估值政策、报告期
**典型输出**：
- 标准化估值复核工作底稿
- 估值结果对比（GP报告值vs复核值）
- LP报告草稿（投资组合估值、业绩指标）
- 估值差异说明和建议调整项
**包含的核心 Skills/Commands**：
- `dcf-model`（底层资产估值）
- `comps-analysis`（可比估值）
- `portfolio-monitoring`（投后监控，PE场景）
- `xlsx-author`/`pptx-author`
- `clean-data-xls`

**主要依赖 Verticals**：`private-equity`、`fund-admin`、`financial-analysis`

**数据连接器使用**：Chronograph（LP/GP报告数据）、S&P Global/FactSet（市场数据）、Egnyte/Box（文档管理）。

---

#### 7. GL Reconciler

**功能描述**：总账（GL, General Ledger）对账 agent，自动查找账目差异、追踪根本原因、路由到对应审批人。

**典型输入**：GL数据文件、对账单（银行/经纪人/托管人）、对账规则、历史对账记录
**典型输出**：
- 对账匹配结果表（已匹配/未匹配项目）
- 差异项目清单（break items），标注可能原因
- 拟议调整分录建议
- 审批路由清单（按差异类型分配）
- 对账状态跟踪表
**包含的核心 Skills/Commands**：
- GL recon（总账对账核心流程）
- break tracing（差异追踪）
- `clean-data-xls`
- `audit-xls`
- `xlsx-author`

**主要依赖 Verticals**：`fund-admin`、`financial-analysis`

---

#### 8. Month-End Closer

**功能描述**：月末结账 agent，处理应计项目、滚动结转、差异分析等月末关账流程任务。

**典型输入**：当月GL数据、上月结转数据、应计计划、摊销/折旧表
**典型输出**：
- 应计项目计算表（accruals）
- 资产负债表滚动结转（roll-forwards）
- 差异分析报告（variance commentary）：实际vs预算、当月vs上月
- 月末调整分录建议
- 关账检查清单
**包含的核心 Skills/Commands**：
- accruals（应计处理）
- roll-forwards（滚动结转）
- variance commentary（差异说明）
- `clean-data-xls`
- `xlsx-author`

**主要依赖 Verticals**：`fund-admin`、`financial-analysis`

---

#### 9. Statement Auditor

**功能描述**：LP报表审计 agent，在报表分发给 LP 之前进行自动化审计检查，确保数据准确性和合规性。

**典型输入**：待分发的LP报表包、NAV（资产净值）对账表、资本账户表、业绩报表、审计规则
**典型输出**：
- 审计检查结果清单（通过/失败/警告）
- NAV tie-out（净值核对）验证
- 资本账户变动核对
- 数据一致性校验（跨表交叉引用）
- 异常项标记和修改建议
- 审计签核建议
**包含的核心 Skills/Commands**：
- NAV tie-out（净值核对）
- `audit-xls`（Excel审计）
- `clean-data-xls`
- `xlsx-author`

**主要依赖 Verticals**：`fund-admin`、`financial-analysis`

---

### 功能域四：运营与开户（Operations & Onboarding）

#### 10. KYC Screener

**功能描述**：KYC（Know Your Customer，了解你的客户）审核 agent，解析开户文档、运行规则引擎、标记缺失项和风险信号。

**典型输入**：客户开户申请材料（身份证明、地址证明、资金来源证明、W-8/W-9表格等）、KYC政策规则、风险评分矩阵
**典型输出**：
- 文档解析结果（结构化提取的客户信息）
- 完整性检查清单（缺失/过期/不清晰的文档标记）
- 规则引擎评估结果（通过/需要补充/拒绝）
- 风险信号标记（PEP（政治公众人物）、制裁名单、高风险司法辖区等）
- 开户决策建议（需人工审核的点明确标注）
**包含的核心 Skills/Commands**：
- KYC文档解析
- 规则网格评估（rules grid evaluation）
- `clean-data-xls`/`xlsx-author`
- PDF文档处理

**主要依赖 Verticals**：`operations`、`financial-analysis`

> ⚠️ **人工审核要求**：KYC Screener 仅做预处理和规则检查，**不自动审批开户**。所有"通过"建议需合规官人工复核签核。

---

## Agents 与 Verticals 的关系

Agents 是面向最终用户的**工作流入口**，而 Vertical Plugins 是面向能力组织的**技能仓库**。两者的关系是：

- 每个 agent 依赖一个或多个 vertical 中的 skills/commands
- `financial-analysis` 是核心基础 vertical，被几乎所有 agent 依赖
- Skills 通过 `sync-agent-skills.py` 脚本从 vertical 源同步到各个 agent bundle 中
- 用户可以单独使用某个 vertical 中的 skills，也可以直接使用 agent 完成端到端任务

```
用户/API调用
    │
    ▼
┌─────────────────┐
│  End-to-End     │  （自包含工作流，自动编排）
│  Agents         │
│  (10个)         │
└────────┬────────┘
         │ 自动绑定/调用
         ▼
┌─────────────────────────────────────────┐
│  Vertical Plugins (9个)                 │
│  financial-analysis (核心) + 6个业务    │
│  + 2个合作方                            │
│  ├── Skills（自动触发能力包）           │
│  └── Commands（斜杠命令）               │
└────────────────┬────────────────────────┘
                 │ 通过MCP协议
                 ▼
┌─────────────────────────────────────────┐
│  MCP Data Connectors (12个)             │
│  Daloopa/Morningstar/S&P/FactSet/...    │
└─────────────────────────────────────────┘
```

> 🔗 Vertical Plugins 和 Skills 详见 [垂直行业Skills与Commands](02-vertical-skills.md)
> 🔗 MCP 连接器和部署详见 [数据连接器与部署](03-connectors-deployment.md)

## Managed Agent API 部署方式

每个 agent 都可以通过 Managed Agents API 无头部署。部署的核心组件：

1. **agent.yaml**：位于 `managed-agent-cookbooks/<agent-name>/agent.yaml`，定义 agent 的 system prompt、绑定的 skills、工具权限、子代理配置
2. **deploy-managed-agent.sh**：部署脚本，一键部署配置到 Claude API
3. **orchestrate.py**：事件循环脚本，处理多轮对话、工具调用、子代理委托
4. **subagent delegation**：复杂任务中，主 agent 可以调用专门的子代理（如专门做估值的子代理、专门审计模型的子代理）

部署后，agent 可以通过 API 调用：
```python
# 伪代码示例
response = client.beta.agents.create(
    agent_id="pitch-agent",
    input={"company": "Target Corp", "deal_type": "M&A", "industry": "tech"}
)
```

> 🔗 Managed Agents API 完整文档详见 [/python-sdk/concepts/08-beta-agents.md](../../python-sdk/concepts/08-beta-agents.md)

## 相关概念

- [Claude for Financial Services概览](00-overview.md) — 产品定位、双模式架构、四大功能域总览
- [垂直行业Skills与Commands](02-vertical-skills.md) — Agents所依赖的vertical skills和commands详解
- [数据连接器与部署](03-connectors-deployment.md) — MCP连接器清单和三种部署方式
- [Agents与Skills完整索引](../references/agents-skills-index.md) — 10个Agents的快速查询索引表
