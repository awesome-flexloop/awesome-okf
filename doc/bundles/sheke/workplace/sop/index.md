---
okf_version: "0.2"
type: OKF
title: SOP 标准作业程序
description: SOP（Standard Operating Procedure，标准作业程序/标准操作规程）的词源定义、起源历史、医疗/航空/制药/IT 四大行业实证、要素结构、失效模式与程序性债务，配套通用模板与 runbook/playbook 对照示例。
tags: [SOP, 标准作业程序, 标准操作规程, 清单革命, GMP, 程序性债务, runbook, playbook]
generated: { by: "reference_agent/trae-research-agent", at: "2026-09-08T20:00:00+08:00" }
status: stable
stale_after: 2027-09-08
sources:
  - id: s1
    title: Merriam-Webster 词典
    url: https://www.merriam-webster.com/dictionary/standard%20operating%20procedure
  - id: s2
    title: NEJM 手术安全清单 RCT（Haynes et al. 2009）
    url: https://flexiblelearning.auckland.ac.nz/hqsc-site/5/files/haynes_et_al_2009_a_ssc_to_reduce_morbidity_and_mortality_in-a-global-population.pdf
  - id: s3
    title: WHO Guidelines for Safe Surgery 2009
    url: https://www.ncbi.nlm.nih.gov/books/NBK143230/
  - id: s4
    title: The Checklist Manifesto 书评（Chew 2011）
    url: https://pmc.ncbi.nlm.nih.gov/articles/PMC4953332/
  - id: s5
    title: FlightSafety International - The Case for Better SOP（Burton 2026）
    url: https://sm4.global-aero.com/articles/the-case-for-better-standard-operating-procedures/
  - id: s6
    title: 21 CFR Part 211 原文（FDA）
    url: https://ecfr.federalregister.gov/current/title-21/chapter-I/subchapter-C/part-211
  - id: s7
    title: Pharmaceutical GMP SOP Guide（workprocedures.ai / advisk.com）
    url: https://www.workprocedures.ai/blog/pharmaceutical-gmp-sop-explained
  - id: s8
    title: MBA 智库百科 SOP 词条
    url: https://wiki.mbalib.com/wiki/SOP
  - id: s9
    title: Runbook vs Playbook（Uptime Labs / Sonat）
    url: https://www.uptimelabs.io/learn/runbook-vs-playbook
  - id: s10
    title: SOP 实务指南（postreels.co.uk / glitter.io / CSDN）
    url: https://postreels.co.uk/protocolo-operacional-padrao/
---

# SOP 标准作业程序

> **一句话摘要**：SOP（Standard Operating Procedure，标准作业程序/标准操作规程）是把关键控制点的操作步骤与要求以统一格式描述出来，使经培训的人员都能胜任该岗位的**组织级外部认知装置**。医学 RCT 证明核查清单可使手术死亡率降低约 47%（NEJM 2009）；合规行业用 meta-SOP 与 ALCOA+ 记录体系支撑可审计性；SOP debt（程序性债务）是最大隐性风险。

## 快速导航

| 模块 | 内容 | 建议阅读顺序 |
|------|------|------------|
| [事实清单](facts.md) | 32 条事实（F-001～F-032）+ 10 条信源（S1～S10）+ 放弃核验清单 | 🔍 第一读：建立事实锚点 |
| [洞察笔记](insights.md) | 5 条四元组洞察（本质 / 生命周期 / 粒度 / 歧义 / 审计单元） | 💡 第二读：理解规律 |
| [概念库](concepts/index.md) | 5 个核心概念（定义·结构·行业·辨析·误区） | 📖 第三读：掌握术语 |
| [示例库](examples/index.md) | 2 个可直接参考的示例（通用模板 + runbook/playbook 对照） | 🛠️ 实践时查 |
| [信源登记](references/01-source-registry.md) | 10 条信源的等级说明、访问状态、未来补充方向 | 🔎 核查时查 |
| [更新日志](log.md) | 创建记录与索引同步清单 | 📋 修订时查 |

## 核心要点速览

1. **SOP 解决的核心问题**：人类记忆与注意力在压力、疲劳下不可靠——SOP 把关键步骤外包到组织层面的外部核查装置（F-006、F-013、洞察 1）。
2. **SOP 不是单个文件，是体系**：政策→程序→作业指导书→记录四层，SOP 本身也受 meta-SOP 管控（F-017、F-018、F-029）。
3. **医疗实证最硬**：WHO 手术核查表 RCT 死亡率 1.5%→0.8%（P=0.003），全球每年约 2.34 亿台手术受益（F-008、F-009）。
4. **SOP / runbook / playbook 分工**：SOP 管常规业务一致性，runbook 管技术故障修复，playbook 管大型事件协调——选型取决于"可预测性 × 后果"（F-021～F-023、概念 04）。
5. **最大风险是 SOP debt**：多年补丁堆积使文档厚重、新人无从下手、老员工凭经验跳过；"写了但没人用"比没有更糟（F-032、洞察 2、概念 05）。

## 目录结构

```
sop/
├── index.md          ← 本文件（束根导航）
├── facts.md          ← 32 条事实（F-001～F-032）
├── insights.md       ← 5 条四元组洞察
├── log.md            ← 更新日志
├── concepts/         ← 5 个核心概念
│   ├── index.md
│   ├── 01-what-is-sop.md
│   ├── 02-elements-and-structure.md
│   ├── 03-industry-practices.md
│   ├── 04-runbook-playbook-sop.md
│   └── 05-anti-patterns.md
├── examples/         ← 2 个示例
│   ├── index.md
│   ├── 01-sop-template.md
│   └── 02-runbook-vs-playbook-example.md
└── references/       ← 信源登记
    ├── index.md
    └── 01-source-registry.md
```

```{toctree}
:maxdepth: 1
:hidden:

facts
insights
concepts/index
examples/index
references/index
log
```
