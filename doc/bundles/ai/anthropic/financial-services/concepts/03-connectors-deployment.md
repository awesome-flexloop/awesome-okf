---
type: concept
title: "数据连接器与部署"
tags: [financial-services, mcp, connectors, deployment, cowok, managed-agents, claude-code, microsoft-365]
sources:
  - id: anthropic-financial-services-deployment
    title: Claude for Financial Services Deployment Cookbooks
---

# 数据连接器与部署

本文档介绍 Claude for Financial Services 的 MCP 数据连接器生态，以及三种主要部署方式：Claude Cowork 插件、Claude Code CLI、Managed Agents API，同时涵盖 Microsoft 365 插件部署工具和自定义扩展方法。

## MCP 数据连接器概念

**MCP（Model Context Protocol）数据连接器**是 Claude for Financial Services 接入外部金融数据源的标准接口。所有 12 个连接器集中在 `financial-analysis` 核心插件中，通过 MCP 协议为 agents 和 skills 提供实时金融数据，无需用户手动下载和整理数据。

### MCP 连接器的价值

| 优势 | 说明 |
|------|------|
| **实时数据接入** | 直接从数据提供商获取最新市场数据、财报、新闻，无需手动导出导入 |
| **统一接口** | 所有数据源使用相同的 MCP 调用方式，agents 无需为不同提供商写适配代码 |
| **按需查询** | agent 根据分析需要主动查询所需数据，而非预加载全部数据 |
| **可替换** | 企业可以替换为内部数据源或自定义连接器，保持工作流不变 |

### 12个 MCP 连接器清单

| 提供商 | 类型 | 主要用途 |
|--------|------|---------|
| **Daloopa** | 财务模型数据 | 自动更新的公司财务模型数据、一致预期数据，服务于财报更新和建模 |
| **Morningstar** | 投资研究数据 | 基金数据、股票研究、基本面数据、ESG评级 |
| **S&P Global** | 综合金融数据 | Capital IQ 公司数据、信用评级、市场情报、行业研究 |
| **FactSet** | 投资组合分析 | 多资产类别数据、组合分析、实时行情、研究管理 |
| **Moody's** | 信用评级 | 信用评级、风险评估、违约概率、固定收益研究 |
| **MT Newswires** | 新闻快讯 | 实时金融新闻、公司公告、市场动态、原创电讯稿 |
| **Aiera** | 财报情报 | 财报电话会转录、管理层问答、事件监控、财报日历 |
| **LSEG** | 市场数据 | 伦敦证交所/Refinitiv数据、固定收益、外汇、宏观数据 |
| **PitchBook** | 私募市场数据 | VC/PE交易数据、私募公司估值、基金业绩、LP/GP信息 |
| **Chronograph** | 基金运营数据 | PE/VC基金数据、资本账户、NAV、LP报告自动化 |
| **Egnyte** | 文档管理 | 云存储和文档管理、投资资料归档、文件协作 |
| **Box** | 内容管理 | 企业内容管理、文档共享、工作流自动化、安全存储 |

> 🔗 MCP 协议基础详见 Claude Code 插件体系文档。

### 连接器配置

每个 MCP 连接器需要配置对应的 API 密钥和访问权限，通常在插件的配置文件中设置：
- API endpoints
- Authentication credentials
- Rate limiting 参数
- 数据访问范围

企业部署时，可以将现有数据提供商订阅直接接入，无需额外采购。

## 部署方式一：Claude Cowork 插件安装

Claude Cowork 是 claude.com 产品中的插件功能，适合交互式使用场景。分析师通过 Web 界面与 agent 对话，实时引导工作流。

### 安装步骤

1. 进入 claude.com 的插件/扩展市场
2. 搜索需要安装的 agent 或 vertical 插件
3. 点击"安装"，插件会自动下载并注册
4. 配置 MCP 连接器的 API 密钥（如果需要数据访问）
5. 开始对话，插件会在相关场景自动激活

### Cowork 模式特点

| 特点 | 说明 |
|------|------|
| **交互友好** | 适合需要人工判断、中途调整、审核中间结果的场景 |
| **无需编码** | 业务用户直接通过界面使用，不需要开发支持 |
| **实时反馈** | 可以看到 agent 的思考过程、数据来源、中间步骤 |
| **文件上传下载** | 支持直接上传 Excel/PDF 文档，下载生成的模型和报告 |

### 典型用户

- 投行分析师、研究员撰写 pitch 和研报
- 财富顾问准备客户会议
- 需要人机协作的分析工作

## 部署方式二：Claude Code CLI 安装

对于开发者和高级用户，也可以通过 Claude Code CLI 直接安装插件到本地环境。

### 安装步骤

```bash
# 方式1：从本地目录安装
claude plugin install /path/to/claude-for-financial-services/plugins/agent-plugins/pitch-agent

# 方式2：从Git仓库安装
claude plugin install https://github.com/anthropics/claude-for-financial-services --path plugins/agent-plugins/pitch-agent

# 方式3：安装整个vertical plugins
claude plugin install /path/to/claude-for-financial-services/plugins/vertical-plugins/financial-analysis
```

安装后可以通过斜杠命令查看已安装的金融技能：
```bash
# 查看可用命令
/comps    # 启动可比公司分析
/dcf      # 构建DCF模型
/lbo      # 构建LBO模型
/earnings # 财报分析
```

### CLI 模式特点

| 特点 | 说明 |
|------|------|
| **本地文件访问** | 可以直接读写本地文件系统的 Excel/PPT/PDF，适合处理批量文件 |
| **脚本集成** | 可以与 Shell 脚本、Makefile、CI/CD 流水线集成 |
| **自定义扩展** | 方便开发者修改和测试自定义 skills 和 agents |
| **版本控制** | 插件配置可以纳入 Git 版本管理 |

> 🔗 Claude Code 插件安装和CLI使用详见 [/claude-code/concepts/01-plugin-system.md](/claude-code/concepts/01-plugin-system.md)

## 部署方式三：Managed Agents API 部署

对于系统集成和自动化场景，可以通过 Claude Managed Agents API 进行无头（headless）部署。这种模式下，agents 作为后端服务运行，由业务系统通过 API 调用触发。

### 核心部署文件

| 文件 | 位置 | 用途 |
|------|------|------|
| `agent.yaml` | `managed-agent-cookbooks/<agent-name>/` | Agent 配置：system prompt、绑定 skills、工具权限、子代理 |
| `deploy-managed-agent.sh` | `scripts/` | 一键部署脚本，验证配置并部署到 API |
| `orchestrate.py` | `scripts/` | 事件循环脚本：处理多轮对话、工具调用、子代理委托 |
| `check.py` / `validate.py` | `scripts/` | 配置验证脚本：部署前检查 agent.yaml 合法性 |

### agent.yaml 示例结构

```yaml
name: pitch-agent
description: End-to-end pitch deck generation agent
system_prompt: |
  You are an expert investment banking analyst...
  Follow these steps:
  1. Gather company information
  2. Run comps analysis
  3. Build valuation
  4. Generate branded pitch deck
skills:
  - financial-analysis/comps-analysis
  - financial-analysis/dcf-model
  - financial-analysis/pptx-author
  - investment-banking/pitch-deck
  - investment-banking/cim-builder
tools:
  mcp_connectors:
    - factset
    - sp-global
    - pitchbook
subagents:
  - valuation-specialist
  - deck-formatter
```

### 部署流程

1. **配置 agent.yaml**：根据业务需求调整 system prompt、绑定的 skills、工具权限
2. **配置 MCP 连接器**：设置数据提供商 API 密钥
3. **验证配置**：运行 `validate.py` 检查配置合法性
4. **部署**：运行 `deploy-managed-agent.sh` 一键部署到 Claude API
5. **API 调用**：业务系统通过 `/v1/agents` 端点调用

```bash
# 部署示例
cd scripts/
./deploy-managed-agent.sh ../managed-agent-cookbooks/pitch-agent/
```

### orchestrate.py 事件循环

`orchestrate.py` 实现了 agent 运行时的事件循环：
1. 接收用户输入/API请求
2. 加载 agent 配置和 system prompt
3. 执行 agent 推理循环
4. 处理工具调用（MCP数据查询、Excel操作、PPT生成等）
5. 处理子代理委托（subagent delegation）——复杂任务调用专门子代理
6. 返回最终结果

### Subagent Delegation（子代理委托）

复杂任务中，主 agent 可以将专门子任务委托给子代理：
- **Valuation Specialist**：专门处理复杂估值建模
- **Model Auditor**：专门审计Excel模型错误
- **Deck Formatter**：专门处理PPT格式和品牌化
- **Data Researcher**：专门通过MCP连接器收集数据

子代理有自己的 system prompt 和工具集，专注于特定任务，完成后将结果返回给主 agent。

### API 调用示例（伪代码）

```python
from anthropic import Anthropic

client = Anthropic()

# 同步调用
response = client.beta.agents.run(
    agent_id="pitch-agent",
    input={
        "company": "TechTarget Inc",
        "deal_type": "strategic-sale",
        "industry": "enterprise-software",
        "brand_template": "goldman-sachs"
    }
)

# 获取生成的文件
deck = response.get_artifact("pitch-deck.pptx")
model = response.get_artifact("valuation-model.xlsx")
```

> 🔗 Managed Agents API 完整文档详见 [/python-sdk/concepts/08-beta-agents.md](/python-sdk/concepts/08-beta-agents.md)

### Managed API 模式特点

| 特点 | 说明 |
|------|------|
| **无头运行** | 不需要用户界面，适合后端服务和系统集成 |
| **批量处理** | 支持批量触发，如财报季自动更新100个公司的模型 |
| **工作流集成** | 可以嵌入到企业现有系统（CRM、PM、文档管理） |
| **权限控制** | 企业级API密钥管理、访问控制、审计日志 |
| **事件驱动** | 可以通过webhook/消息队列触发（如财报发布后自动运行） |

## Microsoft 365 插件部署工具

仓库提供 `claude-for-msft-365-install/` 工具，用于在 Microsoft 365 生态中部署和管理 Claude for Financial Services 插件。

### 功能
- 将插件打包为 Microsoft 365 Add-in
- 支持 Word/Excel/PowerPoint/Outlook 中直接使用
- 企业级部署和权限管理
- 与 SharePoint/OneDrive 文档集成

### 典型场景
- 在 Excel 中直接调用 Model Builder 构建模型
- 在 PowerPoint 中调用 Pitch Agent 生成 deck
- Outlook 会议邀请自动触发 Meeting Prep Agent

## 验证与检查脚本

仓库提供多个脚本确保部署质量：

| 脚本 | 功能 |
|------|------|
| `check.py` | 基础检查：目录结构、文件完整性、配置格式 |
| `validate.py` | 深度验证：agent.yaml schema、skills引用有效性、MCP配置 |
| `sync-agent-skills.py` | Skills同步：从vertical plugins同步skills到agent bundles |

```bash
# 验证所有agent配置
python scripts/validate.py --all

# 同步skills到所有agents
python scripts/sync-agent-skills.py
```

## 自定义扩展方法

Claude for Financial Services 设计为可扩展框架，企业可以根据自身需求定制。以下是常见的扩展方向：

### 1. 替换/添加数据连接器

将内置 MCP 连接器替换为企业内部数据源：
- 内部数据仓库（Snowflake/BigQuery）
- 专有数据源和订阅
- 内部研究管理系统（RMS）
- 客户主数据系统

方式：实现 MCP server 接口，替换或新增连接器配置，agents 无需修改即可使用新数据源。

### 2. 添加企业上下文

在 agent 的 system prompt 中注入企业特定上下文：
- 公司品牌模板和格式规范
- 内部合规政策和审核要求
- 估值方法论偏好
- 标准模板（pitch、IC memo、LP报告）
- 行业专注领域和术语

方式：修改对应 agent 的 `agent.yaml` 中的 `system_prompt` 部分，或创建企业专属的 system prompt overlay。

### 3. 调整 agent 范围

根据企业需求调整 agent 的工作流边界：
- 添加/删除特定步骤
- 调整人工审核节点位置
- 添加企业特有合规检查
- 定制输出格式和模板

方式：修改 agent.yaml 中的工作流指令，或添加自定义 skills 实现企业特有逻辑。

### 4. 自定义模板

添加企业品牌模板：
- Pitch deck 模板（公司配色、字体、logo、标准页布局）
- IC memo 模板
- LP报告模板
- KYC审核清单模板

方式：将模板文件放入 agent 的 templates/ 目录，在 skills 中引用。

### 5. 创建新的自定义 Agent/skill

如果内置 agents 不满足需求，可以创建新的：
- 使用 `skill-creator` 元技能创建新 skills
- 参考现有 agent 结构创建自定义 agent
- 在 `plugins/agent-plugins/` 添加新 agent 目录
- 创建对应的 `managed-agent-cookbooks/<new-agent>/agent.yaml`
- 运行 `sync-agent-skills.py` 同步依赖

> 🔗 创建自定义 Skills 详见 [/official-skills/concepts/02-skill-creator.md](/official-skills/concepts/02-skill-creator.md)

## 部署模式选择指南

| 场景 | 推荐部署方式 | 理由 |
|------|-------------|------|
| 分析师日常使用、需要交互调整 | Claude Cowork 插件 | 交互式界面、零代码、文件上传下载方便 |
| 本地批量处理、开发者自定义 | Claude Code CLI | 本地文件访问、脚本集成、版本控制 |
| 系统集成、自动化流水线、批量作业 | Managed Agents API | 无头运行、API触发、可嵌入业务系统 |
| Office 365生态内使用 | MSFT 365 Add-in | 直接在Word/Excel/PPT中使用 |
| 企业内部数据和定制需求 | Managed API + 自定义扩展 | 可接入内部数据、注入企业上下文 |

## 相关概念

- [Claude for Financial Services概览](00-overview.md) — 双模式架构总览
- [10个金融Agents详解](01-agents.md) — 每个agent的功能和部署配置
- [垂直行业Skills与Commands](02-vertical-skills.md) — Agents依赖的skills和commands
- [Agents与Skills完整索引](/financial-services/references/agents-skills-index.md) — 连接器完整清单
- [/claude-code/concepts/01-plugin-system.md](/claude-code/concepts/01-plugin-system.md) — Claude Code插件安装体系
- [/python-sdk/concepts/08-beta-agents.md](/python-sdk/concepts/08-beta-agents.md) — Managed Agents API参考
