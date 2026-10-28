---
okf_version: "0.2"
type: Reference
title: "智谱清言 AgentMore × 清华 OpenMAIC 公告事实清单（信源登记）"
description: "智谱清言 AgentMore 官方公告《清言 × 清华 OpenMAIC，打造你的专属AI老师》的 F 编号事实双份登记与官方核验状态（F-001~F-046）"
tags: [openmaic, agentmore, zhipu, article-source, fact-registry, ai-education, blog-article]
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-10-28T14:05:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: announcement
    url: https://agentmore.chatglm.cn/shareFile/m/6ad704d27f8c85cf468aac82
  - id: openmaic-repo
    url: https://github.com/THU-MAIC/OpenMAIC
  - id: openmaic-demo
    url: https://open.maic.chat
---

# 博文事实清单（article-source）

> 本文件是 F 编号事实的双份登记之一（另一份在 spec `facts.md`，两集合正则比对一致：F-001~F-046 连续无跳号）。
> 类型：O=客观事实，V=作者观点/体验，S=厂商自述。核验：✅ 官方一致 ｜ ⚠️ 口径/时效/单源差异（详见 [verification.md](verification.md)）｜ ➖ 无需外部核验。
> 公告：智谱清言 AgentMore 官方分享页，2026-10（采集时点 2026-10-28），约 700 字。F-001~F-024 出自公告，F-025~F-046 为 2026-10-28 官方仓库（README/API/目录树/LICENSE）+ Live Demo + 第三方核验补充。
> 本文为**厂商产品能力上新公告**，厂商自述（S）与可核验事实（O）分层登记；被点名项目 OpenMAIC 的事实以官方仓库为准。

## A. 公告元信息（F-001 ~ F-003）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 公告标题《清言 × 清华 OpenMAIC，打造你的专属AI老师》，副标题「你的学习搭子，又升级了！」，发布页位于 `agentmore.chatglm.cn`（智谱清言 AgentMore 官方域） | ➖ |
| F-002 | S | 公告称：智谱清言携手清华「Github万星项目」OpenMAIC，为 **AgentMore 学习搭子**带来两项新技能——**费曼学习、习题带练** | ⚠️ F-044（公告单源） |
| F-003 | O | 公告未给出 OpenMAIC 的具体 Star 数，"Github万星项目"为模糊表述 | ⚠️ F-030 |

## B. 费曼学习（技能一，F-004 ~ F-007）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-004 | O | 费曼学习通过**主动讲解、反馈修正、换情境检验**，帮用户发现"以为懂了"的地方；面向学生复习与职场人自学 | ➖ |
| F-005 | O | 第一轮「先讲理解」示例 prompt：「用费曼学习法检查我对机会成本的理解，我先讲一遍。每次只帮我找一个理解缺口。」 | ➖ |
| F-006 | O | 第二轮「再讲一遍」：根据搭子的追问，用自己的话修正解释，让它检查误区是否消除 | ➖ |
| F-007 | O | 第三轮「换情境检验」示例：「换个新情境，先别给答案，让我自己判断机会成本。」 | ➖ |

## C. 习题带练（技能二，F-008 ~ F-011）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-008 | O | 习题带练通过**逐步提示、自主推理、总结方法**，帮用户彻底搞定一类题；面向备考人群 | ➖ |
| F-009 | O | 第一轮「找到卡点」示例 prompt：「这道题我选 B，但其实是蒙的。先别公布答案，先问我为什么排除一个选项。」 | ➖ |
| F-010 | O | 第二轮「说出依据」：解释自己的排除理由，让搭子检查逻辑，再引导比较其他选项 | ➖ |
| F-011 | O | 第三轮「总结方法」：说出最终答案与理由，请搭子核对，并一起总结同类题的判断步骤 | ➖ |

## D. 八个 OpenMAIC Skill（F-012 ~ F-021）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-012 | S | 教师、培训者也能用 Skill 辅助备课、设计课程；**8 个 OpenMAIC Skill 已同步上新**，前往「Skill 广场」搜索名称即可安装 | ⚠️ F-045（公告单源） |
| F-013 | O | Skill「费曼学习」：概念自查或知识理解 | ✅ F-034 |
| F-014 | O | Skill「习题带练」：题型练习或解题思路梳理 | ⚠️ F-036（仓库未见逐字同义目录名） |
| F-015 | O | Skill「学会学习」：调整学习方法或优化复习策略 | ✅ F-034 |
| F-016 | O | Skill「互动工作坊」：互动教学培训或实践活动设计 | ✅ F-034 |
| F-017 | O | Skill「系列课规划」：系列课程规划或多课时教学安排 | ✅ F-034 |
| F-018 | O | Skill「逆向教学设计」：围绕学习目标设计评价与教学活动 | ⚠️ F-035（疑对应 `understanding-by-design`） |
| F-019 | O | Skill「核心素养备课」：将素养目标转化为具体教学任务 | ✅ F-034 |
| F-020 | O | Skill「螺旋式课程设计」：同一概念的多轮学习与逐步深化 | ✅ F-034 |
| F-021 | O | Skill 面向教师/培训者，用于辅助备课与设计课程，让"学习者主动思考、教学者因材施教" | ➖ |

## E. 结语与边界（F-022 ~ F-024）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-022 | V | 公告结语：让学习者主动思考，让教学者因材施教，一起探索 AI 时代教育的新可能 | ➖ |
| F-023 | S | 公告称后续学习搭子还将持续升级**课程生成与修改能力** | ✅ F-043（能力方向一致；"持续升级"为规划，未核） |
| F-024 | O | 公告为产品能力上新说明，含对话示例 prompt 与 Skill 名称清单，但**无可复现的安装/配置/代码/调用流程** | ➖ |

## F. 官方核验补充（F-025 ~ F-046，2026-10-28）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-025 | O | OpenMAIC 官方仓库真实存在：`https://github.com/THU-MAIC/OpenMAIC`（2026-10-28 抓取可访问） | ✅ |
| F-026 | O | OpenMAIC 全称 **Open Multi-Agent Interactive Classroom**，清华大学 **THU-MAIC** 团队开源的多智能体互动课堂平台 | ✅ |
| F-027 | O | 官方 Live Demo `https://open.maic.chat` 可访问；README 确认可在该站获取访问码以使用托管模式 | ✅ |
| F-028 | O | README News 显示最新版本 **v0.2.1（2026-04-26）**；更早 v0.2.0（2026-04-20）、v0.1.1（2026-04-14）、**v0.1.0（2026-03-26）** | ✅ |
| F-029 | O | 技术栈（README 徽章）：Next.js 16 / React 19 / TypeScript 5 / LangGraph 1.1 / Tailwind CSS 4 | ✅ |
| F-030 | O | Star 数**多口径互斥**：GitHub API 18,538（2026-10-28）/ GitHubDaily 33,000+（2026-08-28）/ 站点自宣 41.5k / 过期 HTML 16.3k | ⚠️ 多口径 |
| F-031 | O | License **三源互斥**：`LICENSE` 正文 **MIT** vs README 徽章 **AGPL-3.0** vs GitHub API license **AGPL-3.0** | ⚠️ 三源互斥 |
| F-032 | O | 官方 `skills/` 含两个目录：`openmaic`（引导式 SOP Skill）与 `agent-runtime`（教学类 Skill 集） | ✅ |
| F-033 | O | `skills/agent-runtime/` 共 **24 个** Skill 子目录（目录树 `truncated: false`） | ✅ |
| F-034 | O | 8 个上新 Skill 中 **6 个**可与官方目录名一一对应：费曼学习→`feynman-learning`、学会学习→`learning-to-learn`、互动工作坊→`workshop-style`、系列课规划→`curriculum-planner`、核心素养备课→`k12-core-literacy-planning`、螺旋式课程设计→`spiral-curriculum` | ✅ |
| F-035 | O | 「逆向教学设计」疑对应官方 `understanding-by-design`（UbD 逆向设计），未逐字绑定 | ⚠️ 未逐字确认 |
| F-036 | O | 「习题带练」在官方 24 个目录名中未见逐字同义项（候选 `zone-of-proximal-development`，未确认） | ⚠️ 未命中 |
| F-037 | O | `skills/openmaic/SKILL.md` 为引导式 SOP：0 选择模式→克隆/复用→启动方式→配置 Provider Key→`GET {url}/api/health` 验活→生成课堂（`requirement`/`materialIds`） | ✅ |
| F-038 | O | 官方支持 `ACCESS_CODE` 站点级访问口令（v0.1.1 起），API 路由同样受保护 | ✅ |
| F-039 | O | 官方支持多 Provider：OpenAI/Anthropic/Google/DeepSeek/Qwen/Kimi/MiniMax/Grok/OpenRouter/Doubao/腾讯混元/Xiaomi MiMo/GLM/Ollama/Lemonade 及任意 OpenAI 兼容 API | ✅ |
| F-040 | O | 官方 README 确认 OpenClaw 集成：可从飞书/Slack/Telegram 等 20+ 消息应用生成课堂（`clawhub install openmaic`） | ✅ |
| F-041 | O | 第三方测评（36氪）证实智谱清言存在「学习搭子」与「Agentmore 模式」，作为公告可采信旁证 | ✅ |
| F-042 | O | 智谱清言由智谱（Beijing Knowledge Atlas Technology）开发（App Store 开发者信息） | ✅ |
| F-043 | O | 官方 README 确认课程生成能力：two-stage pipeline（Outline→Scenes，含 slides/quizzes/交互模块/PBL） | ✅ |
| F-044 | O | "费曼学习/习题带练作为 AgentMore 学习搭子技能"的官方侧具体实现与命名，未在 OpenMAIC 仓库或智谱公开文档中逐字找到 | ⚠️ 公告单源 |
| F-045 | O | AgentMore「Skill 广场」的安装机制在公开资料中未见官方文档说明 | ⚠️ 公告单源 |
| F-046 | O | 本次核对未发现公告存在硬性事实错误；争议集中于 Star 数、License 口径与厂商自述的 Skill 上新范围 | ✅ |

## 双份一致性核对

- 本文件 F 编号集合 = spec `facts.md` 集合 = {F-001 … F-046}，连续无跳号
- V 阶段补充事实：无（所有核验事实在 R 阶段一次性登记，双份回转完成）
