---
okf_version: "0.2"
type: Reference
title: "P0 核验报告——show-me Skill 博文（7 项 P0：7✅ / 0❌）"
date: 2026-09-16
tags: ["P0核验", "勘误", "信源", "HumanLayer", "show-me"]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ
  - id: official-blog
    url: https://www.humanlayer.dev/blog/show-me-skill
  - id: hn
    url: https://news.ycombinator.com/item?id=49274489
  - id: workbuddy-docs
    url: https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project
  - id: grillme-source
    url: https://ziyang.io/blog/2026-the-ambiguity-tax
---

# P0 核验报告

- **核验日期**：2026-09-16
- **核验对象**：微信公众号"阿胖 AI 手记"博文（2026-09-06）中关于 HumanLayer `show-me` Skill 的全部关键声明
- **信源距离预判**：作者一手实测（独立公众号作者，与厂商无归属）+ 官方博客可交叉 → 历史上零硬性错误信源类型
- **核验结论**：**7 项 P0 全部 ✅，0 ❌ 硬错误；2 项非错误性精度处理（F-037 防误归因 / F-039 路径单源）**

## 一、P0 声明逐项核验

| # | P0 声明（博文口径） | 权威信源 | 结论 | 证据 |
|---|---------------------|----------|------|------|
| P0-1 | show-me 是 HumanLayer 开源的 Skill（F-009） | HumanLayer 官方博客 | ✅ | 官方博客 2026-08-12 发布，作者 Dex Horthy（@dexhorthy）；同日 "Show HN: /show-me"（F-031） |
| P0-2 | 安装命令 `npx skills add humanlayer/skills --skill show-me`（F-026） | 官方博客代码块（正文两处 + 结尾一处） | ✅ | 逐字一致，含空格与参数顺序（F-031） |
| P0-3 | 调用方式：`/show-me` 或要求 Agent 使用该 Skill（F-027） | 官方博客"go try it"节 | ✅ | 原文："invoke `/show-me` or ask the agent to use the `show-me` skill"（F-031） |
| P0-4 | 复杂内容用法 `/show-me as an html explainer`（F-017/F-028） | 官方博客"go try it"节代码块 | ✅ | 原文同款调用（F-031/F-036） |
| P0-5 | 官方吐槽口径：coding agent 纸面越来越聪明、可读懂性体验变差（F-012） | 官方博客"Coding agents are pretty much unreadable / i am so sick of this"节 | ✅ | 原文："agents got more intelligent on paper, but the experience of using them got noticeably worse along this dimension"；博文为非引号转述、语义一致（F-032） |
| P0-6 | 技能行为：用简洁视觉（Mermaid/HTML 等）替代大段文字，且形态不止流程图（含 HTML 讲解页） | 官方博客"What's inside"节 | ✅ | 9 类可视化词汇（F-034）；HTML 可内嵌回复或浏览器打开（F-036） |
| P0-7 | 作者所用环境：WorkBuddy 可安装第三方 Skill、支持斜杠命令与 GitHub 连接器（F-029） | WorkBuddy 官方文档 | ✅ | `.codebuddy/skills/`（SKILL.md）、`.codebuddy/commands/`、连接器清单含 GitHub（F-038） |

**P1/P2 处理**：

- P1（选核验）：作者"三轮实测"的具体输出（五步流水线、9 分 12 秒字幕时间戳）属作者环境生成结果，官方博客给出的同类用法（program design、大 diff 回顾、HTML explainer）可旁证其合理性 → 标注"作者实测输出"，不作为官方能力承诺。
- P2（单源即可）：作者身份、发布时间（F-002/F-003）取页面元数据；全部 📌 观点条目（F-007/F-011/F-013/F-016/F-021~F-025/F-030）在正文保留作者观点分层。

## 二、勘误四张清单过筛

### ① 日期/版本表

| 项 | 结果 |
|----|------|
| 官方发布日期 | ✅ 2026-08-12（官方博客 + Show HN 日期互证），博文 2026-09-06 发布，相隔 25 天，时序合理 |
| 版本号 | 不适用——博文与官方博客均无版本号声明；`npx skills` 取最新分发，不存在版本错配面 |
| 博文发布时间 | ⚠️ F-003 仅页面 #publish_time 单源，无外部交叉必要（元数据类） |

### ② 成效数字溯源表

| 项 | 结果 |
|----|------|
| 提效倍数/工时节省/成本下降 | ✅ 不适用——全文无任何成效数字（纯个人体验文） |
| 下载量/star 数 | ✅ 不适用——博文未引用任何仓库规模数字 |

### ③ 口径对照表

| 数字 | 性质 | 结果 |
|------|------|------|
| 20 分钟口播 / 3 条短视频 / 9 分 12 秒 / 剪掉 5 分多钟 / 60 秒成片 | 作者假设工作流中的叙述性数字（非市场/规模统计） | ✅ 无需外部核验，正文以"作者假设场景"口径呈现 |

### ④ 引文逐字核对表

| 项 | 结果 |
|----|------|
| 对官方吐槽的转述（F-012） | ✅ 博文未加引号、属意译，与官方原文语义一致，无拔高 |
| 安装命令（F-026） | ✅ 逐字核对完全一致 |
| Grill Me 归属（F-022） | ⚠️ 博文未归属（"我之前分享的"），但两个 Skill 在同段对比易致读者误认同门；F-037 补充：`/grill-me` 为 Matt Pocock 出品。概念篇对比表述显式区分 |
| SKILL.md"几行规则"（F-010） | ⚠️ 作者概括性描述，仓库文件路径未直取（F-039）；正文以"作者阅读后概括"口径呈现，不伪造逐字引用 |

## 三、失败项管理

- 无核心声明失败 → bundle `status: verified`（非 flagged），无需到期前专项复核。
- 两项 ⚠️ 均已在概念篇正文与 [index.md](../index.md) 已知边界中落地：
  - F-037 → [02-subtraction-skills-pattern.md](../concepts/02-subtraction-skills-pattern.md) 对比段标注各自出处；
  - F-039 → index 已知边界第 3 条（仓库内 SKILL.md 路径未逐字核验，命令与行为以官方博客为准）。

## 四、信源清单

| id | 信源 | 类型 |
|----|------|------|
| blog | https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ | 转化对象（一手实测博文，2026-09-06） |
| official-blog | https://www.humanlayer.dev/blog/show-me-skill | ① 官方发布（2026-08-12，Dex Horthy） |
| hn | https://www.libhunt.com/posts/1530852-show-hn-show-me-agent-skill-for-compact-visual-representations | Show HN 镜像（2026-08-12） |
| workbuddy-docs | https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project | ① WorkBuddy 官方文档（Skill/斜杠命令/连接器） |
| grillme-source | https://ziyang.io/blog/2026-the-ambiguity-tax | ③ /grill-me 身份与原文（Matt Pocock） |
