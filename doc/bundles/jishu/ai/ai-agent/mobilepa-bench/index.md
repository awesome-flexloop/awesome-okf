---
okf_version: "0.2"
type: bundle
title: "MobilePA-Bench：移动规划智能体基准精读"
description: "MobilePA-Bench 规划智能体基准精读——页面即仓库（零评测代码）、1,705 任务/212 工具四维加权（Tool 50%）、六类 checker 固定验证策略、v1.5 榜单 13 模型与 Cost 口径，并入 Qwen-UI-Agent 网站技术栈简析"
tags: [MobilePA-Bench, 规划智能体, 基准评测, 私有评测, Qwen-UI-Agent, Next.js, Tongyi-MAI, arXiv]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: arxiv-2608-23035
    resource: https://arxiv.org/abs/2608.23035
    title: arXiv 2608.23035（MobilePA-Bench 论文，基准本体）
  - id: github-mobilepa-bench
    resource: https://github.com/Tongyi-MAI/MobilePA-Bench
    title: GitHub 仓库 Tongyi-MAI/MobilePA-Bench（项目页/论文资产仓，非实现代码仓）
  - id: private-eval-portal
    resource: https://116.62.42.171/login?next=/submit
    title: MobilePA-Bench 私有评测入口（secure submission portal，F-008）
  - id: github-qwen-ui-agent-website
    resource: https://github.com/Tongyi-MAI/Qwen-UI-Agent
    title: GitHub 仓库 Tongyi-MAI/Qwen-UI-Agent（网站源码仓，非实现代码仓）
  - id: qwen-ui-agent-website
    resource: https://tongyi-mai.github.io/Qwen-UI-Agent/
    title: Qwen-UI-Agent 官方技术报告网站
---

# MobilePA-Bench：移动规划智能体基准精读

> **⚠️ 性质声明**：本束覆盖**两个网站型子项目**——MobilePA-Bench（项目页/论文资产仓）与 Qwen-UI-Agent（技术报告网站源码仓）。两仓均为**网站/论文资产，非实现代码仓**：MobilePA-Bench 仓库根不存在任何基准任务数据、评测 harness 或实现代码，基准本体以 arXiv 论文（arXiv:2608.23035）发布（F-001）；Qwen-UI-Agent 仓 README 原文 "Website source only — this is not the Qwen-UI-Agent implementation repository."，实现代码指向 Tongyi-MAI/MAI-UI（WEB-A-01、WEB-A-02）。因此本束不含"本地运行评测"的指引，也不设 examples/ 目录（理由见 [log.md](log.md)）。

MobilePA-Bench 是面向移动规划智能体的**交互式、有状态、以工具为中心**的基准：在可变移动环境中实际执行智能体的每个动作，同时核对动作轨迹与结果状态（F-002）。规模为 **1,705 任务、212 工具、13 个功能域、89 个子类**（F-004），按 Tool Use / Memory / Skills / Sub-agent 四维组织，总分公式 `Overall = 0.5*Tool + 0.2*Memory + 0.2*Skills + 0.1*SubAgent`（F-011）。社区参与方式是提交 HTTPS、OpenAI-compatible、支持 tool-calling 的 endpoint 参与托管私有评测（F-008、F-009）。

本束同时并入一篇 Qwen-UI-Agent 网站技术栈简析（04 篇），记录该技术报告网站的 Next.js 16 双构建轨道、双语 LocalizedText 机制与无数据库架构（WEB-A-04 ~ WEB-A-20）。

---

## 📚 知识结构总览

```
mobilepa-bench/
├── concepts/                        # 核心概念文档（5篇）
│   ├── 00-benchmark-overview.md          # 基准概览：页面即仓库、定义、亮点、私有评测
│   ├── 01-capability-dimensions.md       # 四能力维度、任务分布、13 工具域、代表案例
│   ├── 02-verification-policy.md         # 固定验证策略、六类 checker、replay 双场景
│   ├── 03-leaderboard-analysis.md        # v1.5 权重公式、13 模型分数、Cost/1K 口径
│   └── 04-qwenuiagent-website.md         # Qwen-UI-Agent 网站技术栈简析（独立可跳读）
├── references/                      # 信源登记簿（2篇）
│   ├── facts.md                     # 事实台账 F-001~F-032 + WEB-A-01~WEB-A-24
│   └── source-registry.md           # 信源登记（文件清单/URL/覆盖范围/性质声明）
├── index.md                         # 本文件
└── log.md                           # 生成日志
```

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [基准概览](concepts/00-benchmark-overview.md) | 页面即仓库（零评测代码，F-001）、一句话定义（F-002）、五大 Highlights 与规模（F-003/F-004）、私有评测通道（F-008~F-010）、与 GUI 中心基准的差异化定位（F-031） |
| [四能力维度与任务分布](concepts/01-capability-dimensions.md) | 四维字面定义（F-005）、任务分布 1,040/376/200/89（F-018）、六项统计 N=15/T=15（F-017）、13 工具域（F-019）、代表案例 BTU-204/BTU-622/MEM-0043 等（F-022/F-032） |
| [固定验证策略与六类 checker](concepts/02-verification-policy.md) | 四种成功形态（F-007）、六类 checker 与维度分布（F-021/F-032）、replay demo 的 tool_acc/task_db_acc（F-023）、hidden tasks 保密边界 |
| [榜单解读](concepts/03-leaderboard-analysis.md) | v1.5 数据出处 paper_v5 Table 1（F-011）、权重公式 50/20/20/10（F-011/F-013）、13 模型分数（F-012）、Cost/1K 仅可见输出 token（F-014）、解读纪律 |
| [Qwen-UI-Agent 网站技术栈简析](concepts/04-qwenuiagent-website.md) | 网站源码仓声明（WEB-A-01/02）、Next.js 16 + vinext/wrangler 与 next build 双轨道（WEB-A-04~07）、双语 LocalizedText（WEB-A-11）、无数据库（WEB-A-17）、Pages 部署自检（WEB-A-19/20） |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [事实台账](references/facts.md) | A 部分 F-001~F-032（沿用原编号）+ B 部分 WEB-A-01~WEB-A-24（改编号并标注 facts-websites.md 原编号），全部 concepts 引用的唯一事实依据 |
| [信源登记](references/source-registry.md) | 两信源根的文件清单、相对路径/URL、覆盖事实范围、"两仓均为网站/论文资产非实现代码仓"声明与未覆盖项 |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## 🔗 跨束互链（Tongyi-MAI 生态）

| 互链束 | 关系 | 说明 |
|--------|------|------|
| [mai-ui](../mai-ui/index.md) | 同生态 Agent 基座模型 | MAI-UI 模型家族与 Agent 实现仓；Qwen-UI-Agent 网站 README 明确指向 Tongyi-MAI/MAI-UI 为官方实现仓库（WEB-A-02） |
| [mobile-world](../mobile-world/index.md) | 同生态在线评测环境 | 互补层级而非竞品（F-031）：MobileWorld 考"端到端在真实 GUI 里做对"，MobilePA-Bench 考"规划器对结构化工具的调度与状态推理"，两套分数不可互相替代 |
| [qwen-ui-agent](../qwen-ui-agent/index.md) | Qwen-UI-Agent 技术评测束 | 与本束 04 篇互补：既有束为网站**内容评测**视角（能力/基准成绩/实测），本束 04 篇为网站**工程**视角（构建轨道/双语机制/数据结构） |

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2026-08-29 完成的 R（事实采集）→ I（洞察提炼）→ E（信源先行成文）链路生成，V（核验）由 seven-concepts 流程执行
- **覆盖事实**：共 56 条——MobilePA-Bench F-001 ~ F-032 + Qwen-UI-Agent 网站仓 WEB-A-01 ~ WEB-A-24
- **status**：stable — 仓库结构、站点数据、论文信息为已登记事实
- **stale_after**：2026-12-31 — 榜单数据为 v1.5 快照（from paper_v5 Table 1，F-011），后续版本更新可能改变分数与收录范围；Qwen-UI-Agent 网站多处资源卡为 "Coming soon" 占位、数值待技术报告冻结（WEB-A-24）
- **方法论链路**：R（事实采集）→ I（洞察提炼）→ E（信源先行成文）→ V（核验），详见 [log.md](log.md)

### 已知边界

1. **非实现代码仓**：两仓均为网站/论文资产（F-001、WEB-A-01），本束不提供任何"本地复现评测"的操作；唯一参与方式为私有评测 endpoint 提交（F-008/F-009，每账户每 7 天 1 次）。
2. **榜单为快照数据**：13 模型分数出自 `leaderboard_data.js` v1.5（from paper_v5 Table 1）（F-011/F-012），引用须注明出处文件与版本，禁止跨信源混拼表格。
3. **hidden 任务保密**：站点案例与 replay 演示仅为公开样例，hidden evaluation tasks and ground truth remain private（F-023），与 F-009 的 Hidden-test integrity 一致。
4. **Cost 口径**：Cost/1K Tasks 仅按可见输出 token 估算，input/cached/hidden reasoning tokens 被排除（F-014）；Overall 仅对四维覆盖完整的模型报告。
5. **Qwen-UI-Agent 网站数据未冻结**：sourceNote 声明数值来自当前 LaTeX 草稿、发布前可能调整（WEB-A-12），冲突数字被有意省略（WEB-A-24）。

---

**本知识包共收录 11 个文件（5 个概念 + 2 个信源 + 2 个子目录索引 + 根索引 + 生成日志），无 examples/（依据 F-001 的仓库性质，理由见 log.md）。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
