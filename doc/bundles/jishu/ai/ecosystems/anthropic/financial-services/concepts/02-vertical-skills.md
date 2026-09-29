---
type: concept
title: "垂直行业Skills与Commands"
tags: [financial-services, vertical-plugins, skills, commands, slashes, financial-analysis, investment-banking]
sources:
  - id: anthropic-financial-services-verticals
    title: Claude for Financial Services Vertical Plugins
---

# 垂直行业Skills与Commands

在 Claude for Financial Services 中，**Vertical Plugins（垂直插件）** 是按金融行业子领域组织的技能包，每个 vertical 包含一组相关的 **Skills**（自动触发能力包）和 **Commands**（斜杠命令，用户显式调用）。Vertical plugins 位于 `plugins/vertical-plugins/` 和 `plugins/partner-built/` 目录下，是 10 个 End-to-End Agents 的能力基础。

## Vertical 插件概念

与通用 purpose 的 Skills 不同，Financial Services 的 Skills 和 Commands 按金融业务条线（vertical）组织，这种设计符合金融机构的实际分工——投行分析师、股票研究员、PE投资经理、财富顾问、基金会计使用不同的工具集和术语体系。

| 设计特点 | 说明 |
|---------|------|
| **按业务条线打包** | 每个 vertical 对应一个金融子行业，包含该领域所需的全部技能 |
| **Skills + Commands 混合** | 既有自动触发的 Skills（语义匹配），也有显式斜杠命令（用户主动调用） |
| **核心依赖关系** | `financial-analysis` 是核心基础，其他 6 个官方 vertical 都依赖它 |
| **合作方扩展** | LSEG 和 S&P Global 作为合作方提供数据驱动的垂直插件 |
| **同步机制** | 通过 `sync-agent-skills.py` 脚本从 vertical 源同步 skills 到各个 agent bundles |

> 🔗 Skills 机制基础详见 [/official-skills/concepts/00-overview.md](../../official-skills/concepts/00-overview.md)

## 7个官方Vertical详解

按依赖顺序排列（核心先行）：

---

### 1. financial-analysis（核心基础插件）

这是所有其他 vertical 的基础，包含金融建模和分析的核心技能，以及**全部 12 个 MCP 数据连接器**。任何需要财务模型、Excel 处理、数据分析的场景都会自动加载此插件。

#### 核心 Skills

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| comps-analysis | `/comps` | 可比公司分析（Comparable Company Analysis）——选择可比公司、计算交易倍数、生成估值区间 |
| dcf-model | `/dcf` | DCF（现金流折现模型）——WACC计算、自由现金流预测、终值计算、敏感性分析表格 |
| lbo-model | `/lbo` | LBO（杠杆收购模型）——收购价格、债务结构、退出回报（IRR/MOIC）、信用比率分析 |
| 3-statement-model | `/3-statement-model` | 三表联动模型——利润表、资产负债表、现金流量表完整链接预测 |
| audit-xls | `/debug-model` | Excel模型审计——公式检查、链接错误检测、逻辑验证、#REF!修复 |
| clean-data-xls | - | Excel数据清洗——格式标准化、缺失值处理、数据类型转换 |
| deck-refresh | - | 投影片数据刷新——将最新数据更新到已有deck模板中 |
| competitive-analysis | `/competitive-analysis` | 竞争格局分析——竞争对手对比、SWOT、市场份额分析 |
| ib-check-deck | - | 投行Deck质量检查——格式、数据一致性、逻辑漏洞审查 |
| pptx-author | - | PowerPoint专业创作——品牌模板应用、图表生成、格式标准化 |
| xlsx-author | - | Excel专业创作——格式、公式、命名范围、保护设置 |
| ppt-template-creator | `/ppt-template` | PPT模板创建——生成符合品牌规范的可复用deck模板 |
| skill-creator | - | 元技能——创建和修改自定义skills（继承自官方skill-creator） |

#### 包含的 MCP 连接器

全部 12 个金融数据连接器均集中在此插件中：Daloopa、Morningstar、S&P Global、FactSet、Moody's、MT Newswires、Aiera、LSEG、PitchBook、Chronograph、Egnyte、Box。

---

### 2. investment-banking（投资银行）

面向投资银行分析师和经理，覆盖 pitch 到执行的全流程投行业务。

#### 核心 Skills/Commands

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| strip-profile | `/one-pager` | 公司简介提取（strip profile）——从公开信息生成一页纸公司概要 |
| pitch-deck | - | Pitch Deck生成——从分析材料生成完整的推介材料 |
| datapack-builder | - | 数据包构建——整理模型、Comps、研究等原始材料成结构化数据包 |
| cim-builder | `/cim` | CIM（保密信息备忘录，Confidential Information Memorandum）撰写 |
| teaser | `/teaser` | Teaser（投资概要）生成——匿名项目推介文档 |
| buyer-list | `/buyer-list` | 买方清单构建——潜在收购方/投资者筛选和列表 |
| merger-model | `/merger-model` | 合并模型——增厚/摊薄分析、协同效应计算、合并后财务预测 |
| process-letter | `/process-letter` | 流程信函——拍卖流程各阶段标准信函模板 |
| deal-tracker | `/deal-tracker` | 交易跟踪——项目进度管理、关键时间点、任务清单 |

**依赖**：`financial-analysis` 核心插件
**主要使用 Agent**：Pitch Agent

---

### 3. equity-research（股票研究）

面向卖方/买方股票研究分析师，覆盖财报季、首次覆盖、模型更新等研究工作流。

#### 核心 Skills/Commands

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| earnings-analysis | `/earnings` | 财报分析——财报电话会解析、实际vs预期对比、关键指标追踪 |
| earnings-preview | `/earnings-preview` | 财报预览——业绩预期汇总、关键观察点、同行业对比 |
| initiating-coverage | `/initiate` | 首次覆盖报告撰写——完整的深度研究报告框架 |
| model-update | `/model-update` | 模型更新——新财报数据发布后自动更新财务模型 |
| morning-note | `/morning-note` | 晨报/晨会纪要——每日市场点评、个股新闻摘要 |
| sector-overview | `/sector` | 行业/板块概览——行业深度分析、板块轮动观点 |
| thesis-tracker | `/thesis` | 投资论点跟踪——核心论点变化、验证/证伪信号记录 |
| catalyst-calendar | `/catalysts` | 催化剂日历—— upcoming events（财报、产品发布、监管决定等） |
| idea-generation | `/screen` | 投资机会筛选——基于量化/定性条件筛选股票池 |

**依赖**：`financial-analysis` 核心插件
**主要使用 Agent**：Market Researcher、Earnings Reviewer

---

### 4. private-equity（私募股权）

面向私募股权基金投资团队和投后管理团队，覆盖 sourcing 到退出的全 PE 生命周期。

#### 核心 Skills/Commands

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| deal-sourcing | `/source` | 项目源开发——行业扫描、潜在标的筛选、初步接触策略 |
| deal-screening | `/screen-deal` | 项目筛选——投资标准匹配、快速初步评估、排除理由 |
| dd-checklist | `/dd-checklist` | 尽职调查清单——商业/财务/法律/税务/IT/HR各模块DD清单生成 |
| dd-meeting-prep | `/dd-prep` | 尽调会议准备——管理层访谈问题清单、资料请求列表 |
| unit-economics | `/unit-economics` | 单位经济分析——单店/单用户/单产品层面的盈利模型 |
| returns-analysis | `/returns` | 回报分析——IRR/MOIC计算、敏感性分析、回报桥接 |
| ic-memo | `/ic-memo` | IC备忘录（投资决策委员会备忘录）撰写——投资推荐完整文档 |
| portfolio-monitoring | `/portfolio` | 投后监控——被投公司业绩跟踪、KPI仪表盘、价值创造进度 |
| value-creation-plan | `/value-creation` | 价值创造计划——100天计划、运营改进举措、退出路径规划 |
| ai-readiness | `/ai-readiness` | AI成熟度评估——被投企业AI应用现状和机会评估 |

**依赖**：`financial-analysis` 核心插件
**主要使用 Agent**：Valuation Reviewer

---

### 5. wealth-management（财富管理）

面向私人银行家和财富顾问，覆盖客户评审、财务规划、投资组合管理等财富管理场景。

#### 核心 Skills/Commands

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| client-review | `/client-review` | 客户评审——组合表现回顾、市场展望、再平衡建议 |
| financial-plan | `/financial-plan` | 财务规划——退休规划、教育金、遗产规划、现金流预测 |
| portfolio-rebalance | `/rebalance` | 组合再平衡——偏离度分析、交易建议、税务影响评估 |
| client-report | `/client-report` | 客户报告生成——个性化组合报告、业绩归因、持仓分析 |
| investment-proposal | `/proposal` | 投资建议书——新客户/新资金的投资方案推荐 |
| tax-loss-harvesting | `/tlh` | TLH（税损收割，Tax-Loss Harvesting）——识别亏损仓位、优化税务效率 |

**依赖**：`financial-analysis` 核心插件
**主要使用 Agent**：Meeting Prep Agent

---

### 6. fund-admin（基金行政）

面向基金行政、基金会计、中后台运营团队，覆盖 NAV 计算、对账、月末结账等基金运营流程。

#### 核心 Skills/Commands

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| GL recon | - | 总账对账（General Ledger Reconciliation）——账目匹配、差异识别 |
| break tracing | - | 差异追踪——定位对账差异的根本原因 |
| accruals | - | 应计项目处理——管理费、业绩报酬、费用应计计算 |
| roll-forwards | - | 滚动结转——资产负债表项目从上期结转到本期 |
| variance commentary | - | 差异分析说明——实际vs预算/预测的差异解释 |
| NAV tie-out | - | NAV（资产净值）核对——跨表NAV一致性验证 |

**依赖**：`financial-analysis` 核心插件
**主要使用 Agent**：GL Reconciler、Month-End Closer、Statement Auditor、Valuation Reviewer

---

### 7. operations（运营）

面向券商/基金运营团队，目前专注于 KYC 和开户流程。

#### 核心 Skills/Commands

| Skill | 斜杠命令 | 功能描述 |
|-------|---------|---------|
| KYC文档解析 | - | KYC材料结构化解析——身份证/护照/地址证明/W-8表格等信息提取 |
| 规则网格评估 | - | 规则引擎评估——按KYC政策网格自动评估客户风险等级 |

**依赖**：`financial-analysis` 核心插件
**主要使用 Agent**：KYC Screener

---

## 2个合作方Vertical Plugins

### 8. lseg（London Stock Exchange Group，伦敦证券交易所集团）

LSEG 合作开发的垂直插件，基于 LSEG 数据提供固定收益和宏观分析能力。

| 功能 | 描述 |
|------|------|
| 债券 RV（相对价值）分析 | 基于LSEG固定收益数据的债券相对价值比较 |
| Swap 曲线构建 | 利率互换曲线构建和分析 |
| FX Carry（外汇利差交易） | 外汇利差交易策略分析 |
| 期权波动率 | 期权波动率曲面分析和监控 |
| 宏观利率监控 | 主要经济体利率、央行政策实时监控 |

### 9. sp-global（S&P Global，标普全球）

S&P Global 合作开发的垂直插件，基于 S&P Capital IQ 数据提供 tear sheet 和研究摘要能力。

| 功能 | 描述 |
|------|------|
| Tear sheets | 公司概要 tear sheet——一页纸公司核心数据、财务、估值、分析师预期 |
| Earnings previews | 财报预览——S&P Global 预期数据、同行业对比 |
| Funding digests | 融资摘要——债券/贷款/股权融资市场动态摘要 |

---

## Skills 同步机制

由于 End-to-End Agents 需要自包含（安装一个 agent 插件即可使用，不依赖额外安装其他 vertical），仓库提供了 `scripts/sync-agent-skills.py` 脚本用于技能同步：

```
┌────────────────────────────┐
│  vertical-plugins/         │  （source of truth）
│  ├── financial-analysis/   │
│  ├── investment-banking/   │
│  └── ...                   │
└─────────────┬──────────────┘
              │
              │  sync-agent-skills.py
              │  （按agent依赖关系复制）
              ▼
┌────────────────────────────┐
│  agent-plugins/            │  （自包含，可独立安装）
│  ├── pitch-agent/          │
│  │   └── skills/           │  ◄── 从IB + financial-analysis同步
│  ├── earnings-reviewer/    │
│  │   └── skills/           │  ◄── 从ER + financial-analysis同步
│  └── ...                   │
└────────────────────────────┘
```

同步规则：
1. 每个 agent 声明依赖的 verticals
2. 脚本从 vertical-plugins 源复制所需 skills/commands 到 agent 的 skills/ 目录
3. 确保 agent 插件是自包含的，用户安装单个 agent 即可运行
4. 当 vertical 更新时，重新运行同步脚本更新所有相关 agents

> 💡 **扩展提示**：如果自定义 vertical 或 agent，记得更新同步脚本的依赖映射，确保你的 agent 包含所有必要的 skills。

## Skills 与 Commands 的区别

在 vertical plugins 中，同时存在 Skills 和 Commands 两种扩展机制，它们的使用方式不同：

| 维度 | Skills | Commands（斜杠命令） |
|------|--------|-------------------|
| **触发方式** | 自动触发——AI根据用户请求语义判断是否加载 | 显式调用——用户输入 `/command-name` 触发 |
| **用户感知** | 用户不需要知道skill存在，AI自动应用 | 用户需要知道命令名称，主动调用 |
| **典型用途** | 通用领域知识注入、自动化流程、审计检查 | 具体工作流入口、模板生成、快速操作 |
| **例子** | Excel打开时自动审计模型（audit-xls） | 用户输入 `/comps` 开始可比公司分析 |
| **类比** | 自动激活的专业知识 | 工具栏上的快捷按钮 |

> 🔗 详细区别详见 [/official-skills/concepts/00-overview.md#skills-与其他扩展机制的关系](../../official-skills/concepts/00-overview.md#skills-与其他扩展机制的关系)

## 相关概念

- [Claude for Financial Services概览](00-overview.md) — 双模式架构、四大功能域总览
- [10个金融Agents详解](01-agents.md) — Agents如何编排调用这些vertical skills
- [数据连接器与部署](03-connectors-deployment.md) — financial-analysis插件中的12个MCP连接器
- [Agents与Skills完整索引](../references/agents-skills-index.md) — 所有skills/commands的完整对照表
- [/official-skills/concepts/00-overview.md](../../official-skills/concepts/00-overview.md) — Skills机制基础
