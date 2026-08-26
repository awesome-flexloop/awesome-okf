---
type: bundle
okf_version: "0.2"
scope: codebuddy
name: codebuddy
version: "0.1.0"
source: web
description: "CodeBuddy 产品矩阵 OKF 知识包，覆盖 IDE、插件、CLI 三态一体的 AI 编程工具，以及 NPC 云端 AI 员工、WorkBuddy 在线助手、Security 安全审计三大延伸产品。"
---

# CodeBuddy 产品矩阵知识库

CodeBuddy 是腾讯推出的 AI 编程产品矩阵，以"AI 驱动全栈研发"为核心，从本地开发工具延伸到云端自主 Agent、在线办公助手与代码安全审计。本知识包基于 CodeBuddy 六个官方公开页面的事实，系统梳理其产品形态、核心能力与实战流程。

CodeBuddy 的核心差异化在于"三态一体"——IDE（产设研一体桌面端）、插件（嵌入主流 IDE）、CLI（终端命令行）共享同一套 AI 引擎与高级能力（Plan 模式、Subagents、Skills、Hooks、MCP、记忆、规则），并在此基础上延伸出 NPC（云端自主 AI 员工）、WorkBuddy（在线办公助手）与 Security（AI 安全审计）三大场景化产品。

## 产品矩阵篇

| 文档 | 说明 |
|------|------|
| [产品矩阵总览](/concepts/00-product-matrix.md) | IDE/插件/CLI 三态一体与 NPC、WorkBuddy、Security 三大延伸产品的定位、关系与适用场景 |
| [CodeBuddy IDE](/concepts/01-ide.md) | 基于 VSCode 架构的产设研一体桌面端，自然语言驱动 PRD→设计→代码→部署全流程 |
| [CLI](/concepts/02-cli.md) | 终端原生 AI 编程工具，全仓百万级代码感知、MCP 双端、分层记忆与 Sub-agents |
| [NPC 云端 AI 员工](/concepts/03-npc.md) | 基于 CodeBuddy 的云端自主 Agent，目标驱动从需求到 PR 全流程，支持多 NPC 协同 |
| [WorkBuddy 在线助手](/concepts/04-workbuddy.md) | 覆盖日常办公与代码开发双场景的对话式在线 AI 助手，公测阶段 |
| [Security 安全审计](/concepts/05-security.md) | 基于 TCA-Xcheck 与 AI 安全 Agent 的六步安全闭环，对抗性审查与 PoC 动态验证 |

## 核心能力篇

CodeBuddy 三态共享的高级能力（详见各概念文档）：

| 能力 | 说明 |
|------|------|
| Plan 模式 | 规划优先的执行模式，适合复杂任务 |
| Subagents | 子 Agent 委派，独立上下文与工具权限 |
| Skills | 可复用技能包，NPC 与 WorkBuddy 均支持 |
| Hooks | 生命周期钩子，自动化扩展 |
| MCP | Model Context Protocol，CLI 同时支持客户端与服务器 |
| 分层记忆 | CodeBuddy.md 项目/用户/企业三级继承 |
| 规则与智能提交 | 自定义行为规则与 AI 辅助提交 |

## 实战示例

| 示例 | 说明 |
|------|------|
| [CLI 快速入门](/examples/quick-start-cli.md) | 环境准备、全局安装、/init 初始化项目手册、/doctor 诊断、Sub-agents 与 MCP 配置 |
| [IDE 产设研工作流](/examples/ide-workflow.md) | 从自然语言需求到 PRD、Figma 转码、前后端实现、CloudBase/Supabase 部署与代码审查的全流程 |

## 信源登记簿

| 信源 | 文件 | 对应事实 |
|------|------|----------|
| CodeBuddy IDE 官网 | [ide.md](/references/ide.md) | F-001 ~ F-008 |
| CodeBuddy IDE 文档介绍 | [docs-intro.md](/references/docs-intro.md) | F-009 ~ F-025 |
| CodeBuddy CLI 官网 | [cli.md](/references/cli.md) | F-026 ~ F-038 |
| CodeBuddy NPC 官网 | [npc.md](/references/npc.md) | F-039 ~ F-051 |
| WorkBuddy 官网 | [workbuddy.md](/references/workbuddy.md) | F-052 ~ F-060 |
| CodeBuddy Security 官网 | [security.md](/references/security.md) | F-061 ~ F-079 |

完整编号事实清单见 [spec/facts.md](/spec/facts.md)，架构洞察见 [spec/insights.md](/spec/insights.md)。

## 规格说明

| 文件 | 说明 |
|------|------|
| [事实清单 (F-001~F-079)](/spec/facts.md) | 79 条带信源标注的编号事实 |
| [核心洞察](/spec/insights.md) | 5 条架构洞察（陈述/证据/反常识/行动） |
| [变更日志](/log.md) | 版本变更记录 |

## 学习路径建议

1. **了解全貌**：[产品矩阵总览](/concepts/00-product-matrix.md) → 选择感兴趣的产品
2. **本地开发**：[CodeBuddy IDE](/concepts/01-ide.md) → [IDE 工作流示例](/examples/ide-workflow.md) → [CLI](/concepts/02-cli.md) → [CLI 快速入门](/examples/quick-start-cli.md)
3. **云端交付**：[NPC 云端 AI 员工](/concepts/03-npc.md)
4. **安全审计**：[Security 安全审计](/concepts/05-security.md)
5. **办公协同**：[WorkBuddy 在线助手](/concepts/04-workbuddy.md)

## 目录结构

```
codebuddy/
├── index.md                    # 本文件（知识包根索引）
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # R 阶段：79 条编号事实
│   └── insights.md             # I 阶段：5 条架构洞察
├── concepts/
│   ├── index.md
│   ├── 00-product-matrix.md
│   ├── 01-ide.md
│   ├── 02-cli.md
│   ├── 03-npc.md
│   ├── 04-workbuddy.md
│   └── 05-security.md
├── examples/
│   ├── index.md
│   ├── quick-start-cli.md
│   └── ide-workflow.md
└── references/
    ├── index.md
    ├── ide.md
    ├── docs-intro.md
    ├── cli.md
    ├── npc.md
    ├── workbuddy.md
    └── security.md
```

## 信任与生命周期说明

- **事实来源**：本知识包全部 79 条事实均来自 CodeBuddy 六个官方公开页面（IDE 官网、IDE 文档、CLI 官网、NPC 官网、WorkBuddy 官网、Security 官网），抓取日期为 2026-08-23，未引入外部推测或演绎。
- **status 判定**：所有内容文档（6 概念 + 2 示例 + 6 信源）均标记为 `stable`，表示基于已抓取信源可直接消费。
- **stale_after 解释**：统一设置为 `2027-02-23`（生成日后 6 个月）。CodeBuddy 产品矩阵处于快速迭代期（WorkBuddy 仍在公测，产品能力可能频繁更新），6 个月后应重新抓取官方页面核验事实时效性。
- **核验链路**：`generated.at` 与 `verified.at` 均为 2026-08-23T00:00:00Z，由 `reference_agent/trae-solo` 生成、`process:seven-concepts-v` 过程核验。所有产品名称、版本号、URL 均直接引自官方页面。
- **覆盖范围**：覆盖 CodeBuddy IDE、CLI、NPC、WorkBuddy、Security 五个产品及插件形态；不含定价细则、API 文档细节、未公开功能与第三方对比评测。
- **内容敏感度**：本束内容全部来自公开发布的官方网页，属公开内容（Public），存放于 `bundles/` 公共规划区域。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
