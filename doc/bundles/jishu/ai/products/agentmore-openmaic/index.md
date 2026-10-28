---
okf_version: "0.2"
type: bundle
title: "AgentMore × OpenMAIC：学习搭子两项新技能与 8 个教学 Skill"
description: "智谱清言 AgentMore「学习搭子」引入清华开源项目 OpenMAIC 的费曼学习与习题带练两项技能，并同步上新 8 个面向教师/培训者的教学 Skill（源自智谱清言官方公告，经 OpenMAIC 官方仓库交叉核验）"
tags: [openmaic, agentmore, zhipu, qingyan, thu-maic, feynman-learning, exercise-coaching, ai-education, skill-marketplace, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-10-28T14:45:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-28T15:00:00+08:00"
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

# AgentMore × OpenMAIC：学习搭子两项新技能与 8 个教学 Skill

> **类型**：厂商产品能力上新公告 / 能力解读（无 examples/——操作可复现性两问皆"否"）
> **信源**：智谱清言 AgentMore 官方分享页《清言 × 清华 OpenMAIC，打造你的专属AI老师》（约 700 字，采集时点 2026-10-28，分享页未标具体日期）→ 经 OpenMAIC 官方仓库 `THU-MAIC/OpenMAIC`、Live Demo `open.maic.chat` 与第三方测评（36氪）交叉核验
> **核验结论**：13 项 P0/P1 声明 **7✅ / 6⚠️ / 0❌**（F 编号行级口径 ✅ 14 / ⚠️ 6 / ❌ 0），无核心声明被证伪；⚠️ 集中在 Star 多口径、License 三源互斥与公告单源边界
> **数据时点**：OpenMAIC 事实为 2026-10-28 官方仓库口径（最新 release v0.2.1，2026-04-26）；AgentMore 侧能力为公告口径

## 本文概要

公告讲的是**智谱清言 AgentMore「学习搭子」与清华大学开源项目 [OpenMAIC](https://github.com/THU-MAIC/OpenMAIC) 的衔接**：为学习搭子带来两项新技能——**费曼学习**（先讲理解 → 再讲一遍 → 换情境检验）与**习题带练**（找到卡点 → 说出依据 → 总结方法），并把 **8 个面向教师/培训者的 OpenMAIC Skill** 同步上新到 AgentMore「Skill 广场」（费曼学习、习题带练、学会学习、互动工作坊、系列课规划、逆向教学设计、核心素养备课、螺旋式课程设计）。OpenMAIC 全称 **Open Multi-Agent Interactive Classroom**，由清华 THU-MAIC 团队开源，具备一键课程生成能力，官方 `skills/agent-runtime/` 含 24 个教学类 Skill。

## 阅读路径

**先建立概念（10 分钟）**

1. [OpenMAIC 与 AgentMore 学习搭子是什么](concepts/00-what-is-openmaic-agentmore.md)——项目身份、版本/技术栈、Star 与 License 口径、公告元信息（带 F 编号）
2. [两项新技能：费曼学习与习题带练](concepts/01-two-new-study-modes.md)——两套三轮学习法及公告示例 prompt
3. [8 个 OpenMAIC Skill 与官方目录名映射](concepts/02-eight-openmaic-skills.md)——Skill 清单、24 目录名比对与安装口径边界

**继续溯源核验**

- [公告事实清单](references/article-source.md)（F-001~F-046 双份登记）
- [P0 权威核验报告](references/verification.md)（勘误四张清单）

## 核心事实速查

| 项 | 值 |
|----|-----|
| 公告 | 《清言 × 清华 OpenMAIC，打造你的专属AI老师》，智谱清言 AgentMore 官方分享页 |
| 被点名项目 | **OpenMAIC**（Open Multi-Agent Interactive Classroom），清华大学 **THU-MAIC** 团队开源 |
| 官方入口 | https://github.com/THU-MAIC/OpenMAIC ｜ Live Demo https://open.maic.chat |
| 最新版本 | **v0.2.1（2026-04-26）**；2026-03-26 起开源（v0.1.0） |
| 两项新技能 | 费曼学习（概念自查/知识理解）｜习题带练（题型练习/解题思路梳理） |
| 上台 Skill 数 | 公告称 **8 个**（官方 `agent-runtime` 实为 24 个，其中 6 项可逐字对应） |
| 技术栈 | Next.js 16 / React 19 / TypeScript 5 / LangGraph 1.1 / Tailwind CSS 4 |

## ⚠️ 阅读前必知的六条口径/边界

1. **Star 数多口径互斥**：GitHub API 18,538（2026-10-28）/ GitHubDaily 33,000+（2026-08-28）/ 第三方自宣 41.5k / 过期缓存 16.3k；公告仅模糊称"Github万星项目"。本束按"带时点观测"分层登记，**不采信单一权威值**（F-003、F-030）。
2. **License 三源互斥**：`LICENSE` 正文 = **MIT** vs README 徽章与 GitHub API license = **AGPL-3.0**。本束并列登记，采用前须自行复核（F-031）。
3. **"两项新技能"为公告单源**：费曼学习/习题带练作为学习搭子技能的具体实现与命名，未在 OpenMAIC 仓库或智谱公开文档中逐字找到（F-044）。
4. **"Skill 广场安装"为公告单源**：AgentMore 侧该安装机制无公开文档；OpenMAIC 侧安装路径为 `clawhub install openmaic`，**两侧机制不同勿混用**（F-045、F-040）。
5. **2 个 Skill 名未逐字命中官方目录**：「逆向教学设计」疑对应 `understanding-by-design`（F-035）；「习题带练」在 24 目录名中未见逐字同义项（F-036）。
6. **无操作流程、无发布日期**：公告只含对话示例与 Skill 清单，无可复现的安装/配置/代码/调用流程（F-024）；分享页未标具体发布日期，只登记采集时点（F-001）。

## 采用提示与已知边界

- **无 examples/**：公告属"产品能力上新说明"而非操作教程（操作可复现性两问皆"否"），故本束只设 `concepts/` 与 `references/`。若需上手，请以 OpenMAIC 官方 README/`skills/openmaic/SKILL.md` 的 SOP 为准（F-037）。
- **分层阅读**：跳转公告宣传语（如"让学习者主动思考，让教学者因材施教"）为厂商观点（F-022）；"持续升级课程生成与修改能力"为规划性表述（F-023），均不当作已上线能力。
- **高时效**：Star/License/Skill 清单/版本号均为高时效字段，`stale_after: 2026-12-31` 前复核。

## 信源与可信度

- 事实清单与逐条核验状态：[references/article-source.md](references/article-source.md)（F-001~F-046）
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 信源距离：**厂商自述**（智谱清言 AgentMore 官方公告）→ 已用被点名项目 **OpenMAIC 官方仓库/API** 与第三方测评交叉核验；单源项显式标注

## 主题关联

- [skills-manager](../skills-manager/index.md)：Skill 管理与分发（本束"8 个 Skill 上新 + Skill 广场安装"同属 Skill 分发话题）
- [agent-reach](../agent-reach/index.md)：Skill-MD 与 Agent 分发范式（对照 AgentMore 与 OpenMAIC 两侧不同的 Skill 安装路径）
- [aitokenbus](../aitokenbus/index.md)：产品自述资讯型知识包（同为"厂商/产品自述、非操作教程"的先例）
- [knocket](../knocket/index.md)：腾讯系产品观察（同为国内大厂 AI 产品的能力上新类知识包）

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
