---
okf_version: "0.2"
type: bundle
title: "TokenEconomizer：经验驱动的黑盒成本控制"
description: "微软研究院博客 + arXiv:2610.22732v1 + 项目页 + 开源仓库四信源转化的中文教程——三类可回收成本、三条元策略、结果与消融、插件与论文参数分账、可逆节流模式"
tags: [TokenEconomizer, 编码Agent, 成本控制, 黑盒控制, 微技能, 工具剪枝, 失败循环干预, OKF教程]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-cmd", at: "2026-11-17T12:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:50:00+08:00" }
sources:
  - id: blog
    resource: https://www.microsoft.com/en-us/research/blog/tokeneconomizer-learning-from-experience-to-make-ai-coding-agents-more-efficient/
    title: "TokenEconomizer: Learning from Experience to Make AI Coding Agents More Efficient（Microsoft Research Blog，2026-11-16）"
  - id: paper
    resource: https://arxiv.org/abs/2610.22732
    title: "TokenEconomizer: Experience-Driven Black-Box Cost Control for Coding Agents（arXiv:2610.22732v1，2026-10-15，CC BY 4.0）"
  - id: project
    resource: https://tokeneconomizer.github.io
    title: "项目页：交互图表、逐仓库数字、九个标注运行与逐步参数说明"
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
    title: "开源插件 README：安装、支持矩阵、默认设置与复现说明"
  - id: pub
    resource: https://www.microsoft.com/en-us/research/publication/tokeneconomizer-experience-driven-black-box-cost-control-for-coding-agents/
    title: "Microsoft Research 论文出版页"
  - id: facts
    resource: ./references/article-source.md
    title: "本束事实清单 F-001 ~ F-110"
---

# TokenEconomizer：经验驱动的黑盒成本控制

> **⚠️ 性质声明**：本 bundle 是**机制解读 + 官方文档转述型中文教程**，不是源码精读，也不是实测报告。本环境未安装插件、未运行 `experiments/` harness。所有结果数字均表述为「论文报告」，安装与配置步骤均标注「官方文档转述，未实测」。

> **⚠️ 先读这一条**：论文里的控制器是三条元策略全开的实验配置；开源插件默认关闭 micro-skills，且从不自行停止卡住的 turn。**装上插件沿用默认值 ≠ 复现 18.4–30.9%**。逐项差异见 [参数分账台账](references/parameter-ledger.md) 与 [核验报告 D-3](references/verification.md)。

## 一句话结论

TokenEconomizer 把降本对象从「单个任务」改成「同一仓库的任务流」：读已完成会话的轨迹，更新三套策略（注入哪些事实、加载哪些工具、何时打断卡住的 turn），只通过 agent 已暴露的指令前缀、工具集、事件流三个接口施加控制，不改模型、不改 agent 代码（F-041、F-042、F-045）。

## 信源说明

| 信源 | 类型 | 作用 |
|---|---|---|
| 微软研究院博客（2026-11-16） | 作者团队成果介绍 | 问题陈述、三类浪费、机制概述 |
| arXiv:2610.22732v1（2026-10-15） | 一手论文 | 表 1–7、附录 A–J、形式化与局限 |
| 项目页 tokeneconomizer.github.io | 一手交互材料 | 逐步参数、逐组合数字、九个标注运行 |
| `microsoft/TokenEconomizer` README | 一手工程文档 | 安装、支持矩阵、默认设置、复现路径 |
| 微软研究院出版页 | 作者团队发布页 | 出版日期与署名（含一处差异） |

四信源由同一作者团队发布，**本次采集未取得独立第三方复现**（F-109）。关键声明一律回查论文表格；博客的合并区间不替代逐基准数字。完整核验见 [核验报告](references/verification.md)。

## 知识结构总览

```
tokeneconomizer-experience-cost-control/
├── concepts/      # 10 篇概念教程（速览→剖析→控制器→三策略→结果→分账→模式→边界）
├── examples/      # 2 篇检查清单式示例（安装验证 / 状态观测，均未实测）
├── references/    # 4 篇信源层 + 子目录索引（事实清单 / 核验 / 参数台账 / 术语表）
├── index.md       # 本文件
└── log.md         # 生成日志与机械门禁记录
```

本束**设 `examples/`**：本项目有官方安装命令、状态命令与可复现 harness，操作可复现性两问中至少一问成立。这与同域纯资讯解读束（不设 examples）的处理不同，理由记在 [examples/index.md](examples/index.md)。

## 分层导航

### 概念层

| 文档 | 核心内容 |
|---|---|
| [速览](concepts/00-overview.md) | 前置警示、一句话结论、关键数字、三条洞察、学习路径 |
| [成本剖析](concepts/01-cost-profiling.md) | 30%/7%、23/16、17%/32% 三组数字与三种固定策略逐仓反转 |
| [黑盒控制器](concepts/02-black-box-controller.md) | 状态 Sᵢ、式 (1)、四条原则、cache-aware 成本与式 (6) 约束 |
| [微技能](concepts/03-micro-skills.md) | proposer / detectors / 三道门 / 式 (2) / 三态状态机 / 附录 H 活动计数 |
| [工具剪枝](concepts/04-tool-pruning.md) | 核心保护、评审屏蔽链接、每 5 任务复审、按 agent 写入位置 |
| [失败循环干预](concepts/05-failure-loop.md) | Bᵢ 预算、judge 0.7、redirect、backstop、headless 边界 |
| [结果与消融](concepts/06-results-and-ablations.md) | 表 1 / 表 2 逐格数字、证据等级、四组易混数字 |
| [插件与论文分账](concepts/07-plugin-vs-paper.md) | 支持矩阵、安装命令族、默认开关、复现路径 |
| [可迁移模式](concepts/08-transferable-pattern.md) | 「可逆节流」：五步、五个反模式、检验标准、两个跨领域迁移 |
| [局限与落地](concepts/09-limits-and-adoption.md) | 三类误判、什么时候不该上、落地检查表、复核触发 |

### 示例层

| 文档 | 核心内容 |
|---|---|
| [安装与验证](examples/01-install-and-verify.md) | 四种稳定 agent 命令族、Trust / hooks、status、refresh-catalog、常见坑 |
| [读状态与调参](examples/02-status-and-tuning.md) | 四条命令读法、六步全栈对齐、附录 H 计数口径、headless 检查 |

### 信源层

| 文档 | 核心内容 |
|---|---|
| [事实清单](references/article-source.md) | F-001 ~ F-110，110 条客观事实，逐条带信源定位与口径类型 |
| [核验报告](references/verification.md) | 14 组 P0 核验、4 处口径差异、四视角 7 条攻击与采纳修正 |
| [参数分账台账](references/parameter-ledger.md) | 论文表 4 与插件 Settings 逐项对照，标注同名异义与重大差异 |
| [术语表](references/glossary.md) | 18 个术语、三条元策略作用面、受测版本快照、易混数字 |

## 信任与生命周期

- **覆盖事实**：共 **110 条**（F-001 ~ F-110），单份登记于 `references/article-source.md`（未建 `.trae/specs/` 双份，理由见该文件顶部）。
- **核验情况**：14 组 P0 全部通过；登记 4 处信源口径差异（D-1 ~ D-4 分组）、1 处待核验署名差异、1 处许可证标注差异；0 处硬错误。
- **对抗审查**：四视角 7 条具体意见，采纳 7 条并落到文件（速览警示、证据等级、投入产出判据、版本快照、逐基准数字、参数台账、未实测声明）。
- **方法论链路**：R（事实采集，G1）→ I（三条四元组洞察，G2）→ E（可逆节流模式，G3）→ V（四视角攻击）→ A（原子化，G4 前置）→ C（索引与导航同步）。详见 [log.md](log.md)。
- **status**：stable — 论文与仓库 README 均为已发布事实。
- **stale_after**：2027-02-28 — 插件受测版本区间很窄，模型与 harness 迭代快，约 3 个月后应复核。

## 已知边界

1. **未实测**：未安装插件、未运行实验、未读取 `LICENSE` 文件内容。
2. **证据独立**：无独立第三方复现；18.4–30.9% 为作者团队自报、按 cache-aware 口径、3 seed。
3. **口径分账**：论文按 task 计、插件按 prompt/session 计；同名参数字母含义不同，本束并存登记不合并。
4. **署名未裁决**：出版页 "Chinmay Singh" 与其余信源 "Chandan Singh" 的差异只登记，不判定。
5. **非操作保证**：安装与调参步骤是检查清单，不构成「照做必定成功」的承诺；版本区间仅采集日有效。

---

**本知识包共 16 个内容文档（10 概念 + 2 示例 + 4 信源）、3 个子目录索引、根索引与生成日志，合计 21 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
