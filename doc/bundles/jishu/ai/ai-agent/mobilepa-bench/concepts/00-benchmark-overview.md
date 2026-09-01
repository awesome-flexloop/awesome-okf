---
type: Concept
title: "基准概览：页面即仓库的有状态工具规划基准"
description: "MobilePA-Bench 仓库性质声明（项目页资产、零评测代码）、基准一句话定义、五大亮点、News 时间线、建模与评测方式、私有评测通道及差异化定位。"
tags: [MobilePA-Bench, 基准评测, 规划智能体, 私有评测, arXiv]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobilepa-facts
    resource: /references/facts.md
    title: MobilePA-Bench 与网站事实台账
  - id: mobilepa-sources
    resource: /references/source-registry.md
    title: 信源登记
---

# 基准概览：页面即仓库的有状态工具规划基准

> **事实基础**：本文所有数据与引文均标注 F 编号，完整事实清单见本束 `references/facts.md` A 部分（frontmatter sources 已登记），信源文件清单见 `references/source-registry.md`。

MobilePA-Bench 是一个面向**移动规划智能体（mobile planner agents）**的交互式、有状态、以工具为中心的基准。本篇首先声明一个最容易被忽视的事实：它的 GitHub 仓库**不是实现代码仓**，而是"README + 静态项目页 + CI 脚本"的论文资产仓——基准本体以 arXiv 论文发布，评测经托管私有通道进行（F-001）。理解这一点后再读定义、亮点、私有评测与差异化定位，才不会在仓库里寻找不存在的"run 脚本"。

## 1. 仓库性质：页面即仓库，零评测代码

仓库根目录经全量核查仅含 `README.md`、`LICENSE`、`.gitignore`、`github-pages/`（纯静态站点）与 `.github/`（CI 脚本与 workflow），**不存在任何基准任务数据、评测 harness、模型或智能体实现代码目录**（F-001）。README「News」原文记载：

```text
2026-08-25: The project repository was opened with an interactive project page,
leaderboard, and a private-evaluation link
```

这意味着：**"open repository" 不等于 "open benchmark"**——ground truth 与 judge 凭据被有意隔离（F-009），社区唯一参与方式是提交 endpoint（见 §5）。与 MobileWorld 那类"开源 harness + Docker 环境 + 本地跑分"的基准形成完全相反的工程形态。

## 2. 基准一句话定义

README 原文定义（F-002）：

```text
MobilePA-Bench is an interactive, stateful, and tool-centric benchmark for
evaluating the tool-calling and planning capabilities of mobile planner agents.
It moves beyond static function matching by executing agent actions in a
mutable mobile environment and checking both the action trace and the
resulting state.
```

三个关键词：**interactive**（可交互）、**stateful**（有状态）、**tool-centric**（以工具为中心）。判分不只看"调用了哪个函数"，而是**在可变移动环境中实际执行每个动作，同时核对动作轨迹与结果状态**。

## 3. 五大 Highlights 与规模

README 列出五条字面要点（F-003），其中规模数字为 1,705 任务、212 工具、13 域、89 子类（F-004）：

| # | Highlight | 要点 |
|---|---|---|
| ① | Executable and stateful | 应用数据、权限与设备状态随每次动作演化 |
| ② | Broad mobile coverage | 1,705 任务、212 工具、13 个域、89 个子类（F-004） |
| ③ | Four capability dimensions | Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration |
| ④ | Evidence-based evaluation | 固定策略验证工具选择、落地参数、执行顺序、最终环境状态与智能体行为 |
| ⑤ | Realistic failure modes | 工具依赖、权限边界、冲突请求、运行时错误、不完整用户上下文 |

## 4. 建模与评测方式

README Overview 描述（F-007）：移动规划智能体被建模为通过 **structured tools、reusable skills、persistent memory 和 specialized sub-agents** 进行操作的决策器；环境执行每个动作、更新状态并返回观察或运行时错误。评测器为**每个任务分配固定验证策略（fixed verification policy）**，成功可要求以下四种形态之一：

```text
an exact tool call            精确工具调用
a target state transition     目标状态迁移
a prescribed action order     规定动作顺序
a valid collaboration pattern 有效协作模式
```

验证策略的六类 checker 谱系在 [02-verification-policy.md](02-verification-policy.md) 展开。

## 5. 私有评测通道

面向 hosted mobile planner agents 的保密评测：提交 **HTTPS、OpenAI-compatible、支持 tool-calling 的 endpoint**，将在 Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration 四维评测；入口为 secure submission portal（`116.62.42.171/login?next=/submit`）（F-008）。四条特性（F-009）：

1. **Confidential by design**——提交直达专用评测服务器，API 凭据不经 GitHub Pages；
2. **Hidden-test integrity**——基准查询、ground truth、judge 凭据与被测模型隔离；
3. **Reviewed results**——每次运行在发布前经人工检查；
4. **Expected turnaround**——通常 **3 个工作日**内返回报告，**每账户每 7 天允许 1 次请求**。

站点侧的评测入口 URL 由 `site_config.js` 统一注入：`evaluationServiceUrl = "https://116.62.42.171"` 挂载到 `window.MobilePABenchConfig`，脚本遍历所有带 `data-evaluation-path` 属性的链接改写 href（F-010）。注意入口指向裸 IP 而非域名——这是保密设计的一部分，而非工程疏漏。

## 6. 差异化定位：补空档而非替代

站点 Introduction 的原文论述（F-031）：

```text
static function-calling benchmarks rarely execute predicted calls against a
persistent environment, while GUI-centric benchmarks underrepresent efficient
structured APIs, personalized context, reusable procedures, and coordination
with specialized agents
```

即现有评测存在两层缺口：静态函数调用基准**不在持久环境中执行**预测调用；GUI 中心基准**低估**了高效结构化 API、个性化上下文、可复用流程与专才智能体协作。MobilePA-Bench 以 interactive、stateful、tool-centric 的 sandbox 补足这一空档（F-031），并重申 1,705 tasks / 212 tools / 13 domains 的规模（F-004）。

它与同生态的 MobileWorld 是**互补层级而非竞品**：MobileWorld 考"端到端在真实 GUI 里做对"，MobilePA-Bench 考"规划器对结构化工具的调度与状态推理"。两套分数不可互相替代，选基准应按"被测能力层"判断。环境侧详见同生态在线评测环境束：[../mobile-world/index.md](../../mobile-world/index.md)。

## 7. News 时间线、论文与许可

- **2026-08-24**：论文上 arXiv（arxiv.org/abs/2608.23035）；**2026-08-25**：项目仓库开放（F-006）。
- README BibTeX：citation key `zhu2026mobilepabench`，标题 "MobilePA-Bench: Benchmarking Mobile Planner Agents on Complex Real-World Tasks"，作者 Zhu, Yi; Wu, Xiongwei; Wang, Qiyi; Qu, Tingyu; Liu, Jiajun; Cao, Sihan; Chen, Long; Sun, Weigao; Zhu, Feida; Zhong, Yiran; Hoi, Steven，arXiv preprint arXiv:2608.23035，2026，primaryClass cs.AI（F-028）。页面 #citation 章节另有简化版（key `mobilepabench2026`，author "MAI Team, Alibaba Token Hub, Alibaba Group"），footer 注明页面模板灵感来自 Video-MME（F-029）。
- 许可证：README 声明 "Unless otherwise noted, this repository is licensed under the Apache License 2.0"，根目录存在 LICENSE 文件（F-030）。

## 相关概念

- [01-capability-dimensions.md](01-capability-dimensions.md)——四能力维度定义、任务分布与代表案例
- [02-verification-policy.md](02-verification-policy.md)——固定验证策略与六类 checker
- [03-leaderboard-analysis.md](03-leaderboard-analysis.md)——v1.5 榜单权重公式与 13 模型解读
- [04-qwenuiagent-website.md](04-qwenuiagent-website.md)——并入的 Qwen-UI-Agent 网站技术栈简析
- [../mobile-world/index.md](../../mobile-world/index.md)——同生态在线评测环境（互补层级）
