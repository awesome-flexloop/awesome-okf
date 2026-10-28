---
okf_version: "0.2"
type: Reference
title: "智谱清言 AgentMore × 清华 OpenMAIC 公告 P0 权威核验报告"
description: "对公告 13 项 P0/P1 声明的官方交叉核验：✅ 7/⚠️ 6/❌ 0，含勘误四张清单（日期版本/成效溯源/口径对照/引文逐字）"
tags: [openmaic, agentmore, verification, p0-check, fact-check, errata]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-10-28T14:20:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: announcement
    url: https://agentmore.chatglm.cn/shareFile/m/6ad704d27f8c85cf468aac82
  - id: openmaic-repo
    url: https://github.com/THU-MAIC/OpenMAIC
  - id: openmaic-demo
    url: https://open.maic.chat
  - id: third-party
    url: https://m-ai.36kr.com/note-detail/3568010593721452
---

# P0 权威核验报告

> 核验时间：2026-10-28。信源：官方仓库 **github.com/THU-MAIC/OpenMAIC**（README/News/LICENSE/`skills/` 目录树/GitHub API）、官方 Live Demo **open.maic.chat**、第三方测评（36氪）与 App Store 开发者信息。
> 公告信源距离：**厂商自述**（智谱清言 AgentMore 官方公告），能力宣称与可核验事实交织；被点名项目 OpenMAIC 的事实以官方仓库为准，厂商自述（S）与观点宣传语（V）分层登记、不参与"事实正误"判定。

## 核验总览

| 级别 | 数量 | 结论分布 |
|------|------|---------|
| P0（项目存在/归属/版本/能力/License/Star） | 8 | ✅ 5 / ⚠️ 3 / ❌ 0 |
| P1（技术栈/平台机制/Skill 命名映射/多源旁证） | 5 | ✅ 2 / ⚠️ 3 |
| 合计 | 13 | **✅ 7 / ⚠️ 6 / ❌ 0** |

> 注：spec.md 第 5 节按"声明项"口径计为 13 项（✅7/⚠️6/❌0）；本表按"F 编号核验行"计为 **✅ 14 / ⚠️ 6 / ❌ 0**（✅ 行：F-025~F-029、F-032~F-034、F-037~F-043、F-046；⚠️ 行：F-030、F-031、F-035、F-036、F-044、F-045）。两者为同一结论的不同切分，无冲突。

**总体评估**：公告的**可核验骨架全部成立**——OpenMAIC 项目真实存在且归属清华 THU-MAIC、Live Demo 在线、版本 v0.2.1（2026-03 起开源）、具备课程生成能力、官方提供引导式 SOP Skill，8 个上新 Skill 中 6 个能与官方目录名一一对应。⚠️ 项集中于三类：① **动态数字口径**（Star 数多源互斥）；② **合规口径冲突**（LICENSE 正文 MIT vs 徽章/API AGPL-3.0）；③ **厂商自述范围**（"学习搭子两项新技能""8 Skill 已上新"及"Skill 广场"安装机制无官方仓库/智谱文档逐字佐证，另有 2 个 Skill 名未在仓库命中）。无一项构成核心声明造假，故 bundle 状态 **stable**；⚠️ 项在正文保留公告口径并明确标注。

## 勘误四张清单

### ① 日期/版本表

| 公告声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 未声明具体发布日期（F-001） | 分享页无日期；采集时点 2026-10-28 可访问 | ➖ 本束只陈述采集时点，不臆测发布日期 |
| 「清华 Github万星项目」（F-002/F-003） | README News：v0.1.0 **2026-03-26** 起开源；最新 v0.2.1（**2026-04-26**）（F-028） | ✅ 开源时间线可核；Star 数见 ② |
| 「后续持续升级课程生成与修改能力」（F-023） | 官方已有 two-stage pipeline（Outline→Scenes）（F-043）；"持续升级"为**规划性表述**，未核 | ⚠️ 正文按"厂商规划"呈现，不当作已上线能力 |

### ② 成效数字溯源表

| 公告声明（F） | 官方/第三方核验 | 结论 |
|--------------|----------------|------|
| 「Github万星项目」（未给具体数，F-003） | GitHub API **18,538**（2026-10-28）；GitHubDaily 报道 **33,000+**（2026-08-28）；某第三方站点自宣 **41.5k**；过期 HTML 缓存 **16.3k**（F-030） | ⚠️ **多口径互斥**——本束按"带时点观测"分层登记：18,538（2026-10-28 实测）/ 33,000+（2026-08-28 媒体）/ 其余为无时点或不一致缓存值，不采信单一权威值 |
| （无其他成效数字） | 公告未给出课程数/用户数等成效数字 | ➖ 本表仅验证 Star 口径 |

### ③ 口径对照表

| 公告声明（F） | 官方口径 | 结论 |
|--------------|---------|------|
| 「清华 OpenMAIC」（F-002） | README + 第三方站点一致：OpenMAIC = Open Multi-Agent Interactive Classroom，清华大学 THU-MAIC 团队开源（F-026） | ✅ 一致 |
| License（公告未提） | `LICENSE` 正文 = **MIT**（Copyright (c) 2026 THU-MAIC）；README 徽章与 GitHub API license 字段 = **AGPL-3.0**（F-031） | ⚠️ **三源互斥**；本束并列登记，**不单一断言**，采用前需以官方 LICENSE 文件与 releases 为准自行复核 |
| 「8 个 OpenMAIC Skill」（F-012） | 官方 `skills/agent-runtime/` 含 24 个教学类 Skill；其中 6 个与公告名称一一对应（F-033/F-034） | ⚠️ "8 个"为**公告侧清单**（含仅面向 agent-runtime 的部分项）；"习题带练"未命中（F-036）、"逆向教学设计"疑对应 `understanding-by-design`（F-035） |
| 「AgentMore 学习搭子」（F-002） | 第三方测评确认智谱清言有「学习搭子」与「Agentmore 模式」（F-041）；但"费曼学习/习题带练作为其技能"无官方仓库/文档逐字（F-044） | ⚠️ 学习搭子与 AgentMore **存在性** ✅；**本次两项技能上新**为公告单源 |
| 「前往 Skill 广场搜索名称即可安装」（F-012） | 公开资料未见 AgentMore「Skill 广场」安装机制官方文档（F-045） | ⚠️ 公告单源，正文标"仅公告披露" |

### ④ 引文逐字核对表

| 公告引用（F） | 官方原文核对 | 结论 |
|--------------|-------------|------|
| 「github.com/THU-MAIC/OpenMAIC」对应的项目名 OpenMAIC（F-025/F-026） | README 标题与 Overview 均为 **OpenMAIC（Open Multi-Agent Interactive Classroom）** | ✅ |
| 「专属 AI 老师 / 学习搭子」产品定位（F-001/F-002） | README 定位"AI teachers and AI classmates…interactive classroom"；智谱侧为"学习搭子"（F-041） | ✅ 名称口径不同但定位一致 |
| 「课程生成」能力（F-023） | README "One-click lesson generation""two-stage pipeline"（F-043） | ✅ |
| 「Skill 广场搜索名称即可安装」（F-012） | OpenMAIC 侧安装路径为 `clawhub install openmaic` / OpenClaw skill（F-040）；AgentMore 侧无公开文档 | ⚠️ 平台侧机制未逐字确认 |
| 访问码 / 托管使用（公告隐含"打开学习搭子即可用"） | README 确认 `open.maic.chat` 可获取访问码；自部署可设 `ACCESS_CODE`（F-027/F-038） | ✅ 官方侧机制一致 |

## 博文口径归属（非事实错误，正文标注处理）

- F-002/F-012/F-044/F-045：**厂商自述**——"携手清华 OpenMAIC""两项新技能""8 Skill 已上新""Skill 广场安装"。正文以"厂商公告披露"呈现，标注官方仓库/公开文档未逐字对应。
- F-004~F-011、F-021~F-022：**公告单源的产品交互细节与宣传语**——费曼学习/习题带练三轮流程与示例 prompt 为公告口径，无第三方实测复现；正文标"公告口径"。
- F-003/F-030：**动态数字**——Star 数按多口径分层登记，不写成单一权威值。

## 核验方法与局限

1. **方法**：① GitHub API 抓取仓库元数据（stars/license/pushed_at）与 `skills/`、`skills/agent-runtime/` 目录树（`truncated: false` 全文枚举）；② raw 抓取 `README.md` 与 `LICENSE` 原文逐字比对；③ 读取 `skills/openmaic/SKILL.md` 引导式 SOP；④ WebSearch 交叉核验第三方测评（36氪）与 App Store 开发者信息。
2. **局限**：① **未注册使用 AgentMore 学习搭子**，"费曼学习/习题带练"的实际交互与三轮流程以公告为准；② **未登录 open.maic.chat 实测生成课堂**，能力描述取自官方 README/仓库；③ Star 数与 License 均存在多源互斥，本束只做"带时点观测登记"，不做仲裁；④ AgentMore「Skill 广场」机制无公开文档，无法核验"8 个 Skill 可安装"的完整链路。
3. **复核安排**：`stale_after=2026-12-31` 前复核——Star 数与时点、License 口径（官方是否统一 LICENSE 与徽章）、AgentMore 学习搭子能力集与 Skill 清单、OpenMAIC 版本号（v0.2.1 → 后续 release）。
