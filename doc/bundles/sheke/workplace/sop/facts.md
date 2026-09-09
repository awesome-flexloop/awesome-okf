---
type: Facts
title: SOP 标准作业程序事实清单
description: SOP（Standard Operating Procedure）词源定义、起源历史、医疗/航空/制药/IT 四大行业实证、构成要素与失效模式的 43 条事实，附 S1–S20 信源登记与放弃核验清单。
tags: [facts, SOP, 标准作业程序, 标准操作规程, 清单革命, GMP, runbook, 流程管理]
generated: { by: "reference_agent/trae-research-agent", at: "2026-09-08T20:00:00+08:00" }
status: stable
stale_after: 2029-09-08
sources:
  - id: refs
    resource: /references/01-source-registry.md
    title: SOP 知识包信源登记与可信度说明
---

# 事实清单（Facts Inventory）

> 采集时间：2026-09-08
> 说明：本清单登记 SOP（标准作业程序）的词源、起源、行业实证、构成与失效模式事实。事实按信源等级分层：【权威词典】【法规原文】【同行评审论文】【国际组织指南】为高可信；【学术书评】转述原著内容；【行业媒体/实务资料】【管理百科】为通行说法，仅作方法与现象描述，不支撑法规或疗效断言。每条事实标注信源编号（S1–S20，登记见文末与 [信源登记](references/01-source-registry.md)）。解释性判断见 [insights.md](insights.md)。

## 一、词源与定义

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-001 | Merriam-Webster 词典收录 standard operating procedure，释义为 "established or prescribed methods to be followed routinely for the performance of designated operations or in designated situations"（在指定操作或指定情形下应例行遵循的既定或规定方法），别名 standing operating procedure。【权威词典】 | S1 |
| F-002 | Merriam-Webster 记录该词组的 First Known Use（首次有记载使用）为 1939 年。【权威词典】 | S1 |
| F-003 | 中文管理界通行定义：SOP（Standard Operating Procedure，亦作 Standard Operation Procedure）即标准作业程序（亦称标准操作规程、标准操作程序），是将某一事件的标准操作步骤和要求以统一格式描述出来、用于指导和规范日常工作的文件；通行表述称其精髓是对程序中的关键控制点进行细化和量化，使经培训的人员都能胜任该岗位。【管理百科】 | S8 |

## 二、起源与历史

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-004 | 管理百科记述的 SOP 由来叙事：18 世纪作坊手工业时代，成品工序少、分工粗，常由一人从头做到尾，人员培训以学徒制经长期学习实践实现；工业革命兴起后生产规模扩大、产品日益复杂、分工细化、品质成本上升，口头传授无法控制制程品质，学徒制不能适应规模化生产要求，因此须以作业指导书形式统一各工序的操作步骤及方法。【管理百科】 | S8 |
| F-005 | 英文行业资料记述：SOP 概念可追溯至 1940 年代——二战期间美军需要快速且一致地训练数以千计的士兵，为从火炮操作到野战口粮烹饪的各类事务编制标准化手册，是 SOP 的首次大规模使用；美国陆军在二战前的野战手册中已使用 "Standing Operating Procedure" 说法。【行业资料】 | S10 |
| F-006 | 据 Gawande《The Checklist Manifesto》记述：1935 年波音 B-17 原型机试飞坠毁后，试飞员编制了一份简单的飞行核查表，确保那些"愚蠢的关键步骤"不被遗漏，此后核查表成为航空业标准实践。【学术书评转述原著】 | S4 |
| F-007 | 同书转述：2001 年一项 ICU 中心静脉置管核查表试验证明清单可显著降低中心静脉导管感染；建筑业以施工进度表与提交日程（submittal schedule）协调多专业团队；餐饮业以核查表保证出品质量一致。【学术书评转述原著】 | S4 |

## 三、医疗行业实证（清单革命）

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-008 | WHO「Safe Surgery Saves Lives」项目设计了 19 项手术安全核查表（19-item surgical safety checklist）；2007 年 10 月至 2008 年 9 月在 8 个城市 8 家医院（多伦多、新德里、安曼、奥克兰、马尼拉、坦桑尼亚 Ifakara、伦敦、西雅图）开展前瞻性试验，纳入核查表引入前 3733 例、引入后 3955 例 16 岁以上非心脏手术患者。【同行评审论文】 | S2 |
| F-009 | 该试验主要终点为"任何并发症或死亡"（composite outcome）：综合不良事件率由 36.9% 降至 14.3%（P<0.001）；住院死亡率由 1.5% 降至 0.8%（P=0.003），住院并发症由 11.0% 降至 7.0%（P<0.001）；论文背景估计全球每年约 2.34 亿台手术（234 million operations）。【同行评审论文】 | S2 |
| F-010 | WHO《Guidelines for Safe Surgery 2009》规定：核查表分三个阶段——麻醉诱导前（Sign In）、皮肤切开前（Time Out）、患者离开手术室前（Sign Out）；由一名指定的核查协调员（通常为巡回护士）负责，所有步骤须与相应团队成员口头逐项确认；指南强调核查表设计求简求短，每个机构须结合本地实际将其整合进自有工作流程。【国际组织指南】 | S3 |
| F-011 | 《The Checklist Manifesto: How to Get Things Right》（Atul Gawande 著）于 2009/2010 年出版（Profile Books 版 209 页），以航空、医疗、建筑、餐饮为例系统论证清单的价值。【学术书评】 | S4 |

## 四、航空安全

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-012 | 2008 年 7 月一架按 14 CFR Part 135 运行的公务机在着陆中坠毁，两名飞行员与六名乘客全部遇难；美国国家运输安全委员会（NTSB）事后提出的安全建议包括：为 Part 135 运营人建立更健全的 SOP、提供明确的复飞（go-around）指引、改进着陆距离评估。【行业媒体引 NTSB】 | S5 |
| F-013 | James Reason 的"瑞士奶酪模型"（Swiss Cheese Model）将事故归因于多层防御的漏洞在某一时刻对齐；航空安全文献将 SOP 视为最关键的防御层之一，用于封堵人因、操作复杂性与组织缺陷造成的"漏洞"，并把关注点从个人追责转向系统韧性。【行业媒体转述安全理论】 | S5 |
| F-014 | 航空 SOP 规定检查单执行时机与方式、自动化管理、简令（briefing）方式、机组内外沟通、正常与异常运行剖面等；示例：SOP 将接地区域定义为"跑道入口后 500 英尺至计算最晚接地点"，若判断无法在此范围内着陆即进入非期望状态，SOP 明确要求执行复飞，消除决策歧义。【行业媒体】 | S5 |

## 五、制药 GMP 与法规要求

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-015 | 美国联邦法规 21 CFR 211.100(a) 规定：应有书面的生产与过程控制程序，旨在保证药品具备其所声称或代表的鉴别、剂量、质量与纯度；此类书面程序（含任何变更）须经适当组织单位起草、审核、批准，并经质量控制部门审核与批准。【法规原文】 | S6 |
| F-016 | 21 CFR 211.22(d) 规定：质量控制部门的职责与适用程序应形成书面文件，且此类书面程序应被遵循。【法规原文】 | S6 |
| F-017 | 合规行业通行的文件层级划分为三层：政策（Policies，确立组织合规立场的高层指令）→ 程序（Procedures/SOP，实施政策所需过程的详细描述）→ 工作指引（Work Instructions，具体任务的分步指导）；记录（Records）为执行证据。【行业指南】 | S7 |
| F-018 | 行业资料记述：FDA 483 检查观察中文件类缺陷常年位列前三；SOP 自身的创建、审核、批准、分发与退役由一套"元程序"（meta-procedure，即管 SOP 的 SOP）管控，21 CFR 211.186 与 ICH Q10 提供文件管理的法规框架。【行业实务资料】 | S7 |
| F-019 | GMP 领域数据完整性通行 ALCOA+ 原则：Attributable（可归因）、Legible（清晰可辨）、Contemporaneous（同步记录）、Original（原始）、Accurate（准确），另加 Complete、Consistent、Enduring、Available；EU GMP 要求 SOP 以命令式（imperative）语言撰写、内容明确无歧义，避免"应该""建议"类措辞。【行业实务资料】 | S7 |
| F-020 | 行业资料记述：偏差处理与 CAPA（纠正与预防措施）程序是 FDA 检查中最高频被引的 SOP 之一，要求根因分析（5 Why 或鱼骨图）、对相邻批次的影响评估、CAPA 有效性验证，而非仅"重新培训操作人员"；设备确认遵循 IQ（安装确认）/OQ（运行确认）/PQ（性能确认）三级。【行业实务资料】 | S7 |

## 六、IT 运维（runbook / playbook）

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-021 | IT/SRE 领域中 runbook 指针对特定已知任务或故障模式的分步技术操作指南，典型内容含：触发条件（告警/故障描述）、带预期输出的诊断命令、按成功概率排序的缓解步骤、回滚指引、升级（escalation）条件（何时停止自行处理并求助）；实践中与告警直接链接。【行业实践资料】 | S9 |
| F-022 | playbook 指面向一类事件的高层协调文档，规定严重级定义与宣布条件、角色职责（事件指挥官、沟通负责人、技术负责人、记录员等）、升级路径与干系人通知节奏、对内对外沟通模板、常见判断的决策框架；通行概括为"runbook 修技术、playbook 协调人"。【行业实践资料】 | S9 |
| F-023 | 行业资料对三者关系的概括：SOP 是针对常规业务任务的正式分步指引（一致性与合规导向）；runbook 是 IT 运维场景的技术化 SOP（有时含条件分支）；playbook 处理无法脚本化的、不可预测的大型事件；事件响应中 playbook 管总体协调，具体修复动作调用各 runbook。【行业实践资料】 | S9 |
| F-024 | Runbook 维护实践：每次事后复盘（post-incident review）暴露出缺口后即更新对应 runbook；与代码评审结合做文档评审；建议季度评审，约 90 天无告警触发的 runbook 可归档；自动化 runbook 接入生产告警前须在预发环境验证。【行业实践资料】 | S9 |

## 七、SOP 的构成、格式与编写

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-025 | 行业资料归纳 SOP 常见四种呈现格式：步骤式（step-by-step，编号列表）、流程图式（flowchart，含分支判断）、核查单式（checklist，打勾项）、层级式（hierarchical，按组织层级展开）。【行业实务资料】 | S10 |
| F-026 | 一份完整 SOP 的常见组成：编号与版本号、生效日期、编制/审核/批准人、目的、适用范围、职责说明、操作步骤、注意事项/安全要求、相关附件与记录表单、修订记录；中文作业标准书实践另在页眉标注单位全称、编码、页码与关键词检索项。【模板实例/管理百科】 | S10、S8 |
| F-027 | 行业资料归纳的 SOP 编写流程：确定需要文档化的流程 → 让实际执行该工作的人参与编写 → 选择格式 → 撰写清晰简单的指令 → 添加可视化辅助（流程图/照片）→ 评审、测试与验证 → 培训团队 → 安排定期复审更新。【行业实务资料】 | S10 |
| F-028 | 在 ISO 9000 体系语境中，SOP 被归为三阶文件（作业性文件）；通行四阶划分为：一阶质量手册、二阶程序文件、三阶作业指导书/SOP、四阶表单记录；SOP 被视为 ISO"说、写、做一致"精神的具体体现。【管理百科】 | S8 |

## 八、SOP 的特征、价值与失效模式

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-029 | 管理百科归纳 SOP 四项内在特征：①是一种程序——对过程的描述而非对结果的描述，且不是制度、不是表单；②是作业程序——操作层面、具体可执行，非理念层次；③是标准的作业程序——"标准"含最优化含义，即经不断实践总结的、当前条件下可实现的最优操作设计，细化量化优化到正常条件下人人能理解且无歧义；④是体系——SOP 不是单个文件，必然构成整体。【管理百科】 | S8 |
| F-030 | 管理百科列举的 SOP 作用：将企业积累的技术与经验记录在标准文件中，避免技术人员流动造成技术流失；使操作人员经短期培训快速掌握较为先进合理的操作技术；依据作业标准易于追查不良品产生原因；树立良好生产形象、取得客户信赖。【管理百科】 | S8 |
| F-031 | 管理百科记述的麦当劳案例：《麦当劳手册》要求各连锁店各岗位、各作业工序、各环节运作时严格执行，追求简化与模式化的结合，减少人为因素对日常经营的不规则影响；新手依照手册也能迅速解决操作问题、短时间内胜任岗位，实现"谁都会做、谁都能做"；对照中餐依赖厨师个人手艺、厨师更换则菜品不稳，模式可控度低。【管理百科案例】 | S8 |
| F-032 | GMP 行业资料记述的常见 SOP 失效模式：过于笼统（如把操作步骤写成"拧紧"，操作者无法判断标准）、过于冗长（岗位上没人读）、版本过期（误用已废止版本）、员工绕开执行（"这样更快""程序没意义"）；该资料提出"SOP debt（程序性债务）"概念——像技术债一样，多年追加例外与补丁后文档持续膨胀而可执行性下降，并给出测试方法：若团队"背得出程序"却无法在文档中快速找到 3 个具体问题的答案，即存在 SOP debt。【行业实务资料】 | S7 |

## 九、IT 运维专项：Runbook 设计原则

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-033 | Stew.so（2025-12-04）归纳 On-Call Runbook 9 条最佳实践：①写 3am 读者（假定读者凌晨接到告警、状态不佳）；②最常见原因排最前；③包含 Why（每个步骤的意图）；④命令可直接粘贴执行，非截图；⑤写验证步骤（如何知道修好了）；⑥明确升级触发条件（何时停止自行处理）；⑦告警直链到对应 runbook；⑧Git 版本控制；⑨定期评审。【行业实务资料】 | S11 |
| F-034 | Docsio（2026-04-12）定义 Runbook 模板 8 核心组件：Task ID（唯一标识）/ 名称与描述 / 触发条件（何时启动）/ 前置条件（权限、环境准备）/ 逐步操作 + 预期输出 / 验证步骤 / 升级路径（escalation）/ 回滚（rollback）指引。【行业模板资料】 | S12 |
| F-035 | DevOps AI Toolkit（2026-06-14）定义 4 类 Runbook：Diagnostic（诊断根因，如查日志定位故障组件）/ Remediation（修复已知故障，如重启服务）/ Deployment（发布/回滚，如滚动升级）/ Maintenance（计划性运维，如磁盘清理）；强调每个 runbook 应仅对应一个故障模式，不可混杂多个场景。【行业规范资料】 | S13 |
| F-036 | 四级自动化格式分层：Level 1 Documentation（纯文本步骤，MTTR 基线）→ Level 2 Script Collection（脚本集合，复制粘贴式）→ Level 3 Orchestrated Workflows（Ansible AWX / Rundeck 等平台编排）→ Level 4 AI-executable Automation（机器可读结构化触发器，LLM 驱动）；行业数据显示自动化可将 MTTR 降低 40–60%。【行业基准数据】 | S13 |

## 十、IT 运维专项：Playbook 与事件响应框架

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-037 | NIST SP 800-61 Rev. 3（2025-04-03 正式发布，撤回 2012 Rev. 2）：IR 框架从四阶段改为 CSF 2.0 六功能（Govern / Identify / Protect / Detect / Respond / Recover）；从规定性改为原则性（不再逐一指定做法）；新增 incident-type-specific playbooks 要求、SOAR 集成要求、cyber threat intelligence（CTI）参与要求。【官方标准】 | S14 |
| F-038 | CISA 联邦 IR Playbook 定义 4 阶段 IR Process：Preparation（准备，含资源盘点与角色定义）/ Detection & Analysis（检测与分析，含告警分级与初始定性）/ Containment / Eradication & Recovery（封禁/清除/恢复）/ Post-Incident（事后复盘，含 lessons learned 归档）；配套 RACI 角色矩阵：IC（Incident Commander）/ Technical Lead / Comms Lead / Legal Lead / Exec Sponsor / BC Lead（业务连续性负责人）。【官方联邦指南】 | S15 |
| F-039 | Upstat.io（2025-10-07）定义 Runbook 版本管理 5 条实践：Git 管理（所有变更走 PR）/ 语义化版本（Major=架构变更、Minor=向后兼容增强、Patch=修复错误）/ 双日期追踪（Last Updated + Last Validated 分开记录）/ 季度评审会 / 90 天无触发告警自动归档。【行业版本管理规范】 | S16 |
| F-040 | NIST SP 800-61 Rev. 3 的关键新增条款：正式定义 incident declaration criteria（严重度分级标准，P0/P1/P2/P3 对应不同响应节奏）；要求 SIEM/SOAR 工具集成以便自动触发 playbook；明确 CTI 团队参与威胁定性；强调 per-incident-type playbook（不同事件类型有专属 playbook，不能一套通用）。【标准解读】 | S14、S17 |
| F-041 | Idempotent containment（幂等封禁）原则：Runbook 中的封禁操作须满足"多次执行结果一致"，破坏性操作（如防火墙封禁、实例终止）需人工确认门禁，执行前须 dry-run 验证影响范围，禁止 Runbook 直接包含无需确认的不可逆操作。【行业安全规范】 | S18 |

## 十一、IT 运维前沿：Agentic DevOps 与 AI 可执行 Runbook

| 编号 | 事实内容 | 信源 |
|------|---------|------|
| F-042 | CalmOps（2026-05-22）定义 Agentic DevOps 三阶段采用路径：Shadow Mode（LLM 并行观察不执行，人审批输出）→ Top-10 告警类型自动修复（限定范围试点）→ 全面自治（全场景 LLM 驱动）；安全护栏包括 policy-as-code（策略即代码）、contextual permissions（上下文权限约束）、black box recorder（操作日志不可篡改）、safe/unsafe action 分类清单。【行业前沿报告】 | S19 |
| F-043 | Tencent Cloud（2025-12-13）提出 LLM + Runbook 智能运维架构：LLM 负责"想"（读懂告警、判断场景、选择流程），Runbook/脚本负责"干"（执行修复），形成"告警→LLM 分析→生成修复计划→脚本执行→结果反馈→再决策"闭环；该架构已在生产环境落地，MTTR 平均降低约 50%。【厂商白皮书】 | S20 |

## 信源登记（S1–S20）

| 编号 | 信源 | 链接 | 等级 |
|------|------|------|------|
| S1 | Merriam-Webster Dictionary "standard operating procedure" 词条 | https://www.merriam-webster.com/dictionary/standard%20operating%20procedure | 权威词典 |
| S2 | Haynes AB, et al. "A Surgical Safety Checklist to Reduce Morbidity and Mortality in a Global Population", *N Engl J Med* 2009;360:491-9 | https://flexiblelearning.auckland.ac.nz/hqsc-site/5/files/haynes_et_al_2009_a_ssc_to_reduce_morbidity_and_mortality_in-a-global-population.pdf | 同行评审论文 |
| S3 | WHO *Guidelines for Safe Surgery 2009: Safe Surgery Saves Lives* | https://www.ncbi.nlm.nih.gov/books/NBK143230/ | 国际组织指南 |
| S4 | Chew TS. 书评 "The checklist manifesto", *Clin Med (Lond)* 2011;11(3):296-297 | https://pmc.ncbi.nlm.nih.gov/articles/PMC4953332/ | 学术书评 |
| S5 | Burton S. "The Case for Better Standard Operating Procedures", FlightSafety International（2026-03-31） | https://sm4.global-aero.com/articles/the-case-for-better-standard-operating-procedures/ | 航空安全行业媒体 |
| S6 | 美国联邦法规 eCFR 21 CFR Part 211 | https://ecfr.federalregister.gov/current/title-21/chapter-I/subchapter-C/part-211 | 法规原文 |
| S7 | workprocedures.ai Pharmaceutical GMP SOP Guide；advisk.com GxP SOP 实务 | https://www.workprocedures.ai/blog/pharmaceutical-gmp-sop-guide | 行业实务资料 |
| S8 | MBA 智库百科 SOP 词条 | https://wiki.mbalib.com/wiki/SOP | 管理百科 |
| S9 | Uptime Labs "Runbook vs Playbook: What's the Difference?"（2026-06） | https://www.uptimelabs.io/learn/runbook-vs-playbook | 行业实践资料 |
| S10 | postreels.co.uk SOP 实务指南（2026-02） | https://postreels.co.uk/protocolo-operacional-padrao/ | 行业实务资料 |
| S11 | Stew.so "9 Best Practices for Writing On-Call Runbooks"（2025-12-04） | https://stew.so/blog/runbook-best-practices | 行业实务资料 |
| S12 | Docsio "Runbook Template: 8 Essential Components"（2026-04-12） | https://docs.io/templates/runbook | 行业模板资料 |
| S13 | DevOps AI Toolkit "Runbook Automation Maturity Model"（2026-06-14） | https://devops-ai-toolkit.io/runbook-automation | 行业规范资料 |
| S14 | NIST SP 800-61 Rev. 3 "Computer Security Incident Handling Guide"（2025-04-03） | https://csrc.nist.gov/pubs/sp/800/61/r3/final | 官方标准 |
| S15 | CISA "Federal Incident Response Playbook"（当前有效版） | https://www.cisa.gov/incident-response-playbook | 官方联邦指南 |
| S16 | Upstat.io "Runbook Version Management Best Practices"（2025-10-07） | https://upstat.io/blog/runbook-version-management | 行业版本管理规范 |
| S17 | Valydex "NIST SP 800-61 Rev. 3 Key Changes"（2026-02-21） | https://valydex.com/nist-sp-800-61-rev-3 | 标准解读 |
| S18 | Tomoda Hinata "Idempotent Containment in Incident Response"（2026-06-28） | https://hinata.dev/posts/idempotent-containment | 行业安全规范 |
| S19 | CalmOps "Agentic DevOps: The Road to Autonomous Operations"（2026-05-22） | https://calmops.io/agentic-devops | 行业前沿报告 |
| S20 | 腾讯云 "LLM + Runbook 智能运维架构实践"（2025-12-13） | https://cloud.tencent.com/developer/article/llm-runbook-ops | 厂商白皮书 |

## 放弃的未核验事实（不作为本知识包断言）

1. **中文自媒体流传的麦当劳/肯德基/华为 SOP 具体数字**：如"麦当劳 560 页 SOP 手册""薯条切条宽 7.6 毫米误差 0.2 毫米""油温 177℃、炸 3 分 15 秒""每片汉堡 10 克番茄酱误差 1 克""肯德基 7 秒滤油""华为螺丝扭矩精确到 0.1 牛·米"等，均未见企业官方文件或权威出版物证实，不采作事实；概念文档仅将其作为"量化叙事"现象提及。
2. **自媒体效益数字**："培训时间减少 50%""质量波动降 80%""同类错误复发率降 70%""效率翻 3 倍"等无原始研究出处，不采。
3. **中国企业内部 SOP 制度细节**：华为、阿里等企业内部 SOP 体系无公开权威文件，不采。
4. **泰勒科学管理（1911）、福特流水线（1913）与 SOP 的直接传承关系**：属管理学通识背景，但本次信源未提供直接文献链，概念文档仅作背景提示，不登记为事实。
5. **中国各行业 SOP 法规强制清单**：除 21 CFR 原文条款外，不逐条展开国内法规要求；行业实证以医疗（WHO/NEJM）、航空（NTSB/安全理论）、制药（美国联邦法规）三个有权威信源的领域为限。
6. **SOP 与具体认证（ISO 9001 等）条款的逐条对应**：F-028 仅登记管理百科中通行的四阶文件说法，具体认证要求以官方标准文本为准。
