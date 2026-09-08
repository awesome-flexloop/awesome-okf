---
type: concept
title: 行业实践——医疗·航空·制药·IT
description: 四大高可靠性行业的 SOP / 核查清单实践：WHO 手术安全核查表、航空瑞士奶酪模型、FDA GMP 的 21 CFR 211、IT SRE 的 runbook 维护。
tags: [concept, SOP, 行业实践, WHO, 航空安全, GMP, SRE]
generated: { by: "reference_agent/trae-research-agent", at: "2026-09-08T20:20:00+08:00" }
status: stable
stale_after: 2029-09-08
sources:
  - id: facts
    resource: ../facts.md
  - id: s2
    title: NEJM 外科安全清单试验（2009）
    url: https://flexiblelearning.auckland.ac.nz/hqsc-site/5/files/haynes_et_al_2009_a_ssc_to_reduce_morbidity_and_mortality_in_a_global_population.pdf
  - id: s3
    title: WHO Guidelines for Safe Surgery 2009
    url: https://www.ncbi.nlm.nih.gov/books/NBK143230/
  - id: s5
    title: FlightSafety International / global-aero（2026）
    url: https://sm4.global-aero.com/articles/the-case-for-better-standard-operating-procedures/
  - id: s6
    title: 21 CFR Part 211 原文
    url: https://ecfr.federalregister.gov/current/title-21/chapter-I/subchapter-C/part-211
  - id: s7
    title: Pharmaceutical GMP SOP Guide
    url: https://www.workprocedures.ai/blog/pharmaceutical-gmp-sop-explained
  - id: s9
    title: Runbook vs Playbook（Uptime Labs / Sonat）
    url: https://www.uptimelabs.io/learn/runbook-vs-playbook
---

# 行业实践：医疗 · 航空 · 制药 · IT

> 本概念整合四组行业实证（F-008～F-024），重点提取跨行业可迁移的共同原则。

## 一、医疗：WHO 手术安全核查表

### 关键事实（F-008～F-010）

- 试验设计：8 城 8 院，纳入前 3733 例 / 后 3955 例患者；
- 结果：死亡率 1.5% → 0.8%（P=0.003），并发症 11.0% → 7.0%（P<0.001）；
- 全球背景：每年约 2.34 亿台手术，即使 0.7% 的绝对降幅也意味数百万例挽救；
- 核查表结构：19 项，分三个阶段（Sign In → Time Out → Sign Out）；
- 执行方式：由巡回护士担任核查协调员，逐项口头与所有团队成员确认；
- WHO 原则：**设计求简求短**，每个机构须结合本地实际整合进自有流程（F-010）。

### 可迁移原则

1. **核查单只保留真正关键的少数**（本项目中 19 项 = 约 5% 的操作步骤），不是把所有步骤都列出来。
2. **必须口头逐项确认**，不是签字后收走；确认动作本身是安全机制。
3. **指定协调员角色**，避免"人人都管等于没人管"。

## 二、航空：瑞士奶酪模型与 SOP 防御层

### 关键事实（F-012～F-014）

- 2008 年 NTSB 公务机事故后提出建议：强化 Part 135 运营人的 SOP、复飞指引、着陆距离评估；
- James Reason 瑞士奶酪模型：事故是多层防御漏洞对齐的结果，SOP 是最关键的防御层之一；
- 航空 SOP 的典型内容：检查单执行时机、自动化管理、简令方式、机组沟通、正常/异常运行剖面；
- 数值化决策门：如"跑道入口后 500 英尺内未接地则进入非期望状态并复飞"，把判断转化为规则（F-014）。

### 可迁移原则

1. **用数值化边界代替主观判断**——在高压、疲劳场景下，"判断接不住地"比"500 英尺未到就复飞"容易出错。
2. **SOP 是系统性防御的一部分**，不是独立的"遵守就行"的东西——它与训练、设备、组织文化一起构成防御层（F-013）。
3. **事故经验是 SOP 演进的主要来源**——NTSB 建议推动 SOP 修改（F-012）。

## 三、制药 GMP：FDA 21 CFR 211 的硬性要求

### 关键事实（F-015～F-020）

- 21 CFR 211.100(a)：须有书面的生产与过程控制程序；程序及变更须经适当组织单位起草、审核、批准，质量部门审核与批准（F-015）。
- 21 CFR 211.22(d)：质量控制部门的职责与适用程序须形成书面文件，且须被遵循（F-016）。
- 文件层级：Policy → Procedure/SOP → Work Instruction → Record（F-017）。
- FDA 483 缺陷中文件类常年居前三；SOP 自身由 meta-SOP（管 SOP 的 SOP）管控（F-018）。
- ALCOA+ 原则：Attributable / Legible / Contemporaneous / Original / Accurate + Complete / Consistent / Enduring / Available（F-019）。
- 偏差/CAPA 须做根因分析与有效性验证，不可仅以"重新培训"收口（F-020）。

### 可迁移原则

1. **法规语境的 SOP 不是"建议""推荐"，而是"必须""应"**；命令式语言是合规底线（F-019）。
2. **SOP 的生命周期是法规的一部分**——评审、批准、版本管理本身受法规要求约束。
3. **记录与 SOP 同编号同版本**——没有同步记录的 SOP 在审计中等于不存在。

## 四、IT SRE：runbook 维护实践

### 关键事实（F-021～F-024）

- runbook 针对已知故障模式，含触发条件、诊断命令（带预期输出）、缓解步骤、回滚、升级条件（F-021）；
- playbook 处理不可预测的大型事件，规定角色、沟通节奏、决策框架（F-022）；
- 关系总结：SOP 管常规业务一致性，runbook 管技术修复，playbook 管协调（F-023）；
- 维护机制：每次 post-incident review 暴露缺口即更新、与代码评审同步、季度评审、90 天无触发归档（F-024）。

### 可迁移原则

1. **runbook 必须带预期输出**——只写命令不写预期结果等于不完整。
2. **runbook 更新必须绑定到复盘**——否则复盘结论停留在口头，runbook 仍然是旧版。
3. **自动化四级路径**：文档 → 脚本集 → 编排 → AI 可执行（F-023 引申）。

## 五、跨行业共同点

| 维度 | 医疗 | 航空 | 制药 | IT |
|------|------|------|------|----|
| 核心机制 | 核查单口头逐项确认 | 检查单 + 决策门 | 文件生命周期 + 元程序 | runbook 绑定复盘 |
| 失败主因 | 遗漏关键步骤 / 协调员缺位 | 偏差值 / 疲劳 / 非期望状态未触发复飞 | SOP debt / 过期版本 / 无记录 | 未复盘即更新 / 误用旧版 |
| 监管强度 | WHO 指南（国际） | NTSB 建议 + FAA 法规 | FDA 法规（强制） | 最佳实践（自愿） |
| 成效证据 | RCT 死亡率 -47% | 减少事故后 NTSB 建议 | 483 缺陷下降 | 故障恢复时间缩短 |

> **核心结论**：四个行业尽管监管强度和领域差异巨大，但 SOP/核查清单的共同成功因素高度一致——**关键少数 + 明确责任人 + 与复盘联动 + 记录留痕**。

## 参考

- [事实清单（F-008～F-024）](../facts.md)
- [洞察笔记：生命周期断裂才是失效主因](../insights.md)
