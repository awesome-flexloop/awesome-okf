---
type: reference
title: "Agents与Skills完整索引"
tags: [financial-services, index, agents, skills, commands, connectors, reference]
sources:
  - id: anthropic-financial-services-index
    title: Claude for Financial Services Complete Index
---

# Agents与Skills完整索引

本页是 Claude for Financial Services 的完整快速查询索引，包含全部 10 个 End-to-End Agents、7 个官方 Vertical Plugins 的所有 Skills/Commands，以及 12 个 MCP 数据连接器。

---

## 一、10个 End-to-End Agents 索引

按四大功能域分组：

| 功能分组 | Agent名称 | 一句话描述 | 主要依赖 Verticals |
|---------|----------|-----------|-------------------|
| **覆盖与顾问** | Pitch Agent | Comps/precedents/LBO→品牌化pitch deck端到端生成 | investment-banking, financial-analysis |
| **覆盖与顾问** | Meeting Prep Agent | 每次客户会议前自动生成简报包 | wealth-management, equity-research, financial-analysis |
| **研究与建模** | Market Researcher | 行业/主题→行业概览、竞争格局、peer comps、ideas shortlist | equity-research, financial-analysis |
| **研究与建模** | Earnings Reviewer | 财报电话会+公告→模型更新→研报草稿 | equity-research, financial-analysis |
| **研究与建模** | Model Builder | DCF/LBO/三表模型/Comps——Excel实时模型构建 | financial-analysis（核心）, investment-banking, private-equity |
| **基金管理与财务运营** | Valuation Reviewer | 摄入GP包、运行估值模板、准备LP报告 | private-equity, fund-admin, financial-analysis |
| **基金管理与财务运营** | GL Reconciler | 找差异、追踪根因、路由审批 | fund-admin, financial-analysis |
| **基金管理与财务运营** | Month-End Closer | 应计、滚动、差异分析 | fund-admin, financial-analysis |
| **基金管理与财务运营** | Statement Auditor | 分发前审计LP报表 | fund-admin, financial-analysis |
| **运营与开户** | KYC Screener | 解析开户文档、运行规则引擎、标记缺失项 | operations, financial-analysis |

> 🔗 Agents 详细说明见 [10个金融Agents详解](../concepts/01-agents.md)

---

## 二、7个官方 Vertical Plugins Skills/Commands 对照表

### 1. financial-analysis（核心基础插件）

包含全部 12 个 MCP 数据连接器。

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| comps-analysis | `/comps` | Skill + Command | 可比公司分析（Comparable Company Analysis）：选择可比公司、计算交易倍数、生成估值区间 |
| dcf-model | `/dcf` | Skill + Command | DCF（现金流折现模型）：WACC计算、自由现金流预测、终值计算、敏感性分析 |
| lbo-model | `/lbo` | Skill + Command | LBO（杠杆收购模型）：收购价格、债务结构、退出回报IRR/MOIC、信用比率 |
| 3-statement-model | `/3-statement-model` | Skill + Command | 三表联动模型：利润表、资产负债表、现金流量表完整链接预测 |
| audit-xls | `/debug-model` | Skill + Command | Excel模型审计：公式检查、链接错误检测、逻辑验证、#REF!修复 |
| clean-data-xls | - | Skill | Excel数据清洗：格式标准化、缺失值处理、数据类型转换 |
| deck-refresh | - | Skill | 投影片数据刷新：将最新数据更新到已有deck模板中 |
| competitive-analysis | `/competitive-analysis` | Skill + Command | 竞争格局分析：竞争对手对比、SWOT、市场份额分析 |
| ib-check-deck | - | Skill | 投行Deck质量检查：格式、数据一致性、逻辑漏洞审查 |
| pptx-author | - | Skill | PowerPoint专业创作：品牌模板应用、图表生成、格式标准化 |
| xlsx-author | - | Skill | Excel专业创作：格式、公式、命名范围、保护设置 |
| ppt-template-creator | `/ppt-template` | Skill + Command | PPT模板创建：生成符合品牌规范的可复用deck模板 |
| skill-creator | - | Skill | 元技能：创建和修改自定义skills |

---

### 2. investment-banking（投资银行）

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| strip-profile | `/one-pager` | Skill + Command | 公司简介提取：从公开信息生成一页纸公司概要 |
| pitch-deck | - | Skill | Pitch Deck生成：从分析材料生成完整的推介材料 |
| datapack-builder | - | Skill | 数据包构建：整理模型、Comps、研究等原始材料成结构化数据包 |
| cim-builder | `/cim` | Skill + Command | CIM（保密信息备忘录）撰写 |
| teaser | `/teaser` | Skill + Command | Teaser（投资概要）生成：匿名项目推介文档 |
| buyer-list | `/buyer-list` | Skill + Command | 买方清单构建：潜在收购方/投资者筛选和列表 |
| merger-model | `/merger-model` | Skill + Command | 合并模型：增厚/摊薄分析、协同效应计算、合并后预测 |
| process-letter | `/process-letter` | Skill + Command | 流程信函：拍卖流程各阶段标准信函模板 |
| deal-tracker | `/deal-tracker` | Skill + Command | 交易跟踪：项目进度管理、关键时间点、任务清单 |

---

### 3. equity-research（股票研究）

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| earnings-analysis | `/earnings` | Skill + Command | 财报分析：财报电话会解析、实际vs预期对比、关键指标追踪 |
| earnings-preview | `/earnings-preview` | Skill + Command | 财报预览：业绩预期汇总、关键观察点、同行业对比 |
| initiating-coverage | `/initiate` | Skill + Command | 首次覆盖报告撰写：完整深度研究报告框架 |
| model-update | `/model-update` | Skill + Command | 模型更新：新财报发布后自动更新财务模型 |
| morning-note | `/morning-note` | Skill + Command | 晨报/晨会纪要：每日市场点评、个股新闻摘要 |
| sector-overview | `/sector` | Skill + Command | 行业/板块概览：行业深度分析、板块轮动观点 |
| thesis-tracker | `/thesis` | Skill + Command | 投资论点跟踪：核心论点变化、验证/证伪信号记录 |
| catalyst-calendar | `/catalysts` | Skill + Command | 催化剂日历：upcoming events（财报、产品发布、监管决定等） |
| idea-generation | `/screen` | Skill + Command | 投资机会筛选：基于量化/定性条件筛选股票池 |

---

### 4. private-equity（私募股权）

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| deal-sourcing | `/source` | Skill + Command | 项目源开发：行业扫描、潜在标的筛选、初步接触策略 |
| deal-screening | `/screen-deal` | Skill + Command | 项目筛选：投资标准匹配、快速初步评估、排除理由 |
| dd-checklist | `/dd-checklist` | Skill + Command | 尽职调查清单：商业/财务/法律/税务/IT/HR各模块DD清单 |
| dd-meeting-prep | `/dd-prep` | Skill + Command | 尽调会议准备：管理层访谈问题清单、资料请求列表 |
| unit-economics | `/unit-economics` | Skill + Command | 单位经济分析：单店/单用户/单产品层面盈利模型 |
| returns-analysis | `/returns` | Skill + Command | 回报分析：IRR/MOIC计算、敏感性分析、回报桥接 |
| ic-memo | `/ic-memo` | Skill + Command | IC备忘录（投资决策委员会备忘录）撰写 |
| portfolio-monitoring | `/portfolio` | Skill + Command | 投后监控：被投公司业绩跟踪、KPI仪表盘、价值创造进度 |
| value-creation-plan | `/value-creation` | Skill + Command | 价值创造计划：100天计划、运营改进举措、退出路径规划 |
| ai-readiness | `/ai-readiness` | Skill + Command | AI成熟度评估：被投企业AI应用现状和机会评估 |

---

### 5. wealth-management（财富管理）

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| client-review | `/client-review` | Skill + Command | 客户评审：组合表现回顾、市场展望、再平衡建议 |
| financial-plan | `/financial-plan` | Skill + Command | 财务规划：退休规划、教育金、遗产规划、现金流预测 |
| portfolio-rebalance | `/rebalance` | Skill + Command | 组合再平衡：偏离度分析、交易建议、税务影响评估 |
| client-report | `/client-report` | Skill + Command | 客户报告生成：个性化组合报告、业绩归因、持仓分析 |
| investment-proposal | `/proposal` | Skill + Command | 投资建议书：新客户/新资金的投资方案推荐 |
| tax-loss-harvesting | `/tlh` | Skill + Command | TLH（税损收割）：识别亏损仓位、优化税务效率 |

---

### 6. fund-admin（基金行政）

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| GL recon | - | Skill | 总账对账：账目匹配、差异识别 |
| break tracing | - | Skill | 差异追踪：定位对账差异的根本原因 |
| accruals | - | Skill | 应计项目处理：管理费、业绩报酬、费用应计计算 |
| roll-forwards | - | Skill | 滚动结转：资产负债表项目从上期结转到本期 |
| variance commentary | - | Skill | 差异分析说明：实际vs预算/预测的差异解释 |
| NAV tie-out | - | Skill | NAV（资产净值）核对：跨表NAV一致性验证 |

---

### 7. operations（运营）

| Skill/Command名 | 斜杠命令 | 类型 | 功能描述 |
|----------------|---------|------|---------|
| KYC文档解析 | - | Skill | KYC材料结构化解析：身份证/护照/地址证明/W-8表格等信息提取 |
| 规则网格评估 | - | Skill | 规则引擎评估：按KYC政策网格自动评估客户风险等级 |

---

## 三、2个合作方 Vertical Plugins 概览

| 合作方 | Vertical名称 | 核心功能 |
|--------|-------------|---------|
| **LSEG（伦敦证券交易所集团）** | `lseg` | 债券RV（相对价值）分析、Swap曲线构建、FX Carry（外汇利差）、期权波动率、宏观利率监控 |
| **S&P Global（标普全球）** | `sp-global` | Tear sheets（公司概要页）、Earnings previews（财报预览）、Funding digests（融资摘要） |

> 🔗 Vertical Plugins 详细说明见 [垂直行业Skills与Commands](../concepts/02-vertical-skills.md)

---

## 四、12个 MCP 数据连接器索引

所有连接器集中在 `financial-analysis` 核心插件。

| 序号 | 提供商 | 官方URL（参考） | 数据类型 | 主要用途 |
|------|--------|----------------|---------|---------|
| 1 | **Daloopa** | daloopa.com | 财务模型数据 | 自动更新公司财务模型数据、一致预期数据，服务于财报更新和建模 |
| 2 | **Morningstar** | morningstar.com | 投资研究数据 | 基金数据、股票研究、基本面数据、ESG评级 |
| 3 | **S&P Global** | spglobal.com | 综合金融数据 | Capital IQ公司数据、信用评级、市场情报、行业研究 |
| 4 | **FactSet** | factset.com | 投资组合分析 | 多资产类别数据、组合分析、实时行情、研究管理 |
| 5 | **Moody's** | moodys.com | 信用评级 | 信用评级、风险评估、违约概率、固定收益研究 |
| 6 | **MT Newswires** | mtnewswires.com | 新闻快讯 | 实时金融新闻、公司公告、市场动态、原创电讯稿 |
| 7 | **Aiera** | aiera.com | 财报情报 | 财报电话会转录、管理层问答、事件监控、财报日历 |
| 8 | **LSEG** | lseg.com | 市场数据 | 伦敦证交所/Refinitiv数据、固定收益、外汇、宏观数据 |
| 9 | **PitchBook** | pitchbook.com | 私募市场数据 | VC/PE交易数据、私募公司估值、基金业绩、LP/GP信息 |
| 10 | **Chronograph** | chronograph.pe | 基金运营数据 | PE/VC基金数据、资本账户、NAV、LP报告自动化 |
| 11 | **Egnyte** | egnyte.com | 文档管理 | 云存储和文档管理、投资资料归档、文件协作 |
| 12 | **Box** | box.com | 内容管理 | 企业内容管理、文档共享、工作流自动化、安全存储 |

> 🔗 连接器部署和配置详见 [数据连接器与部署](../concepts/03-connectors-deployment.md)

---

## 五、快速查询：斜杠命令一览

所有用户可直接调用的斜杠命令（Commands）汇总：

### financial-analysis（核心）
| 命令 | 功能 |
|------|------|
| `/comps` | 可比公司分析 |
| `/dcf` | DCF模型构建 |
| `/lbo` | LBO模型构建 |
| `/3-statement-model` | 三表模型构建 |
| `/debug-model` | Excel模型审计 |
| `/competitive-analysis` | 竞争格局分析 |
| `/ppt-template` | PPT模板创建 |

### investment-banking
| 命令 | 功能 |
|------|------|
| `/one-pager` | 公司一页纸简介 |
| `/cim` | CIM保密信息备忘录 |
| `/teaser` | 投资Teaser |
| `/buyer-list` | 买方清单 |
| `/merger-model` | 合并模型 |
| `/process-letter` | 流程信函 |
| `/deal-tracker` | 交易跟踪 |

### equity-research
| 命令 | 功能 |
|------|------|
| `/earnings` | 财报分析 |
| `/earnings-preview` | 财报预览 |
| `/initiate` | 首次覆盖 |
| `/model-update` | 模型更新 |
| `/morning-note` | 晨会纪要 |
| `/sector` | 板块概览 |
| `/thesis` | 论点跟踪 |
| `/catalysts` | 催化剂日历 |
| `/screen` | 股票筛选 |

### private-equity
| 命令 | 功能 |
|------|------|
| `/source` | 项目源开发 |
| `/screen-deal` | 项目筛选 |
| `/dd-checklist` | 尽调清单 |
| `/dd-prep` | 尽调会议准备 |
| `/unit-economics` | 单位经济分析 |
| `/returns` | 回报分析 |
| `/ic-memo` | IC备忘录 |
| `/portfolio` | 投后监控 |
| `/value-creation` | 价值创造计划 |
| `/ai-readiness` | AI成熟度评估 |

### wealth-management
| 命令 | 功能 |
|------|------|
| `/client-review` | 客户评审 |
| `/financial-plan` | 财务规划 |
| `/rebalance` | 组合再平衡 |
| `/client-report` | 客户报告 |
| `/proposal` | 投资建议书 |
| `/tlh` | 税损收割 |
