---
okf_version: "0.2"
type: Concept
title: "8 个 OpenMAIC Skill：清单、用途与官方目录名映射"
description: "公告上新的 8 个 OpenMAIC Skill（费曼学习/习题带练/学会学习/互动工作坊/系列课规划/逆向教学设计/核心素养备课/螺旋式课程设计）与官方 24 个教学 Skill 目录名的逐项映射及单源边界（清单层，声明带 F 编号）"
tags: [openmaic, agentmore, skills, skill-marketplace, teaching-design, ai-education]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-28T14:40:00+08:00" }
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

# 8 个 OpenMAIC Skill：清单、用途与官方目录名映射

> 清单层（What-List）。本文列出公告上新的 8 个 Skill 及其用途，并与 OpenMAIC 官方仓库 `skills/` 目录名逐项比对；无法逐字对应的项显式标注为单源/未命中。

## 公告口径：8 个 Skill 已同步上新

公告称：教师、培训者也能用 Skill 辅助备课、设计课程，**8 个 OpenMAIC Skill 已同步上新**，前往 **AgentMore「Skill 广场」搜索名称即可安装**（F-012）。

| # | Skill 名称（公告） | 公告用途 | 核验 |
|---|-------------------|---------|------|
| 1 | 费曼学习 | 概念自查或知识理解 | ✅ F-034（→ `feynman-learning`） |
| 2 | 习题带练 | 题型练习或解题思路梳理 | ⚠️ F-036 |
| 3 | 学会学习 | 调整学习方法或优化复习策略 | ✅ F-034（→ `learning-to-learn`） |
| 4 | 互动工作坊 | 互动教学培训或实践活动设计 | ✅ F-034（→ `workshop-style`） |
| 5 | 系列课规划 | 系列课程规划或多课时教学安排 | ✅ F-034（→ `curriculum-planner`） |
| 6 | 逆向教学设计 | 围绕学习目标设计评价与教学活动 | ⚠️ F-035（疑 → `understanding-by-design`） |
| 7 | 核心素养备课 | 将素养目标转化为具体教学任务 | ✅ F-034（→ `k12-core-literacy-planning`） |
| 8 | 螺旋式课程设计 | 同一概念的多轮学习与逐步深化 | ✅ F-034（→ `spiral-curriculum`） |

## 与官方仓库目录名的映射（核验）

官方 `skills/` 下有两个目录：`openmaic`（引导式 SOP Skill）与 `agent-runtime`（教学类 Skill 集）（F-032）。`skills/agent-runtime/` 共 **24 个** Skill 子目录（目录树 `truncated: false` 全文枚举，F-033）：

```
build-personal-skill      curriculum-planner        deep-interactive
deep-research             fact-check                feynman-learning
k12-core-literacy-planning learning-to-learn        lecture-style
page-clone                pptx-import                pro-editing
slide-craft               slide-dsl                  social-emotional-learning
spiral-curriculum         stage-design               stage-dsl
style-clone               teacher-style-clone        understanding-by-design
vocational                workshop-style             zone-of-proximal-development
```

**映射结论**：

- 8 项中 **6 项可与官方目录名一一对应**（F-034）：费曼学习→`feynman-learning`、学会学习→`learning-to-learn`、互动工作坊→`workshop-style`、系列课规划→`curriculum-planner`、核心素养备课→`k12-core-literacy-planning`、螺旋式课程设计→`spiral-curriculum`。
- 「**逆向教学设计**」疑对应官方 `understanding-by-design`（UbD 逆向设计），**未逐字绑定**（F-035）。
- 「**习题带练**」在官方 24 个目录名中**未见逐字同义项**（候选 `zone-of-proximal-development`，未确认，F-036）。

> 口径说明：官方 `agent-runtime` 有 24 个 Skill，公告只列 8 个；"8 个"是**公告侧清单**（面向备课/教学设计场景的子集），与官方总数不矛盾（见 [verification ③](../references/verification.md)）。

## OpenMAIC 官方 Skill 生态（补充核验）

- `skills/openmaic/SKILL.md` 为**引导式 SOP**：选择模式 → 克隆/复用 → 启动方式 → 配置 Provider Key → `GET {url}/api/health` 验活 → 生成课堂（`requirement`/`materialIds`）（F-037）。
- 官方支持 **OpenClaw 集成**：可从飞书/Slack/Telegram 等 **20+ 消息应用**生成课堂（`clawhub install openmaic`）（F-040）。
- 官方支持多 Provider（含 GLM/Zhipu 等 15+ 家及任意 OpenAI 兼容 API）（F-039），并提供站点级 `ACCESS_CODE` 访问口令（F-038）。

## ⚠️ 公告单源边界

- **「8 个 Skill 已上新」为厂商自述**（F-012），本束按"厂商公告披露"呈现；官方仓库并未声明哪些 Skill 已接入 AgentMore。
- **「Skill 广场搜索名称即可安装」**：AgentMore 侧该安装机制在公开资料中**未见官方文档说明**（F-045）；OpenMAIC 侧的安装路径为 `clawhub install openmaic` / OpenClaw skill（F-040），**两侧机制不同**，切勿混用（见 [verification ④](../references/verification.md)）。
- Skill 面向教师/培训者，用于辅助备课与设计课程，让"学习者主动思考、教学者因材施教"（F-021，公告表述）。

## 阅读提示

- 若关注**学习者侧**用法（费曼学习/习题带练三轮流程），见 [01-two-new-study-modes.md](01-two-new-study-modes.md)。
- 若关注**项目身份与版本/合规口径**，见 [00-what-is-openmaic-agentmore.md](00-what-is-openmaic-agentmore.md)。
