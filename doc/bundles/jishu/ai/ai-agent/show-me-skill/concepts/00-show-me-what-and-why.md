---
okf_version: "0.2"
type: Concept
title: "show-me 是什么：让 Coding Agent 用视觉结构说话的 Skill"
date: 2026-09-16
tags: ["Agent Skill", "HumanLayer", "show-me", "Coding Agent", "可视化沟通"]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ
  - id: official-blog
    url: https://www.humanlayer.dev/blog/show-me-skill
---

# show-me 是什么：让 Coding Agent 用视觉结构说话的 Skill

## 一句话定位

`show-me` 是 HumanLayer 于 2026-08-12 开源发布的 Coding Agent Skill：它不向模型提供任何新工具或新能力，只通过一份简短的 SKILL.md 规则，要求 Agent **用紧凑的视觉表达（Mermaid 图、树、表格、HTML 等）替代大段文字（walls of prose）来解释正在发生的事**（F-031/F-032）。

> 官方原话（tl;dr）："make your agent converse visually instead of in walls of prose."（F-032）

## 发布事实

| 项 | 内容 |
|----|------|
| 名称 | `show-me`（调用形态 `/show-me`） |
| 发布方 | HumanLayer（官方博客，作者 Dex Horthy，@dexhorthy） |
| 发布时间 | 2026-08-12，同日以 "Show HN: /show-me" 发布到 Hacker News（F-031） |
| 分发方式 | `npx skills add humanlayer/skills --skill show-me`；HumanLayer 自家产品内已内置（F-026/F-031） |
| 适用对象 | 任意支持 Agent Skills 的编码 Agent（官方说法："if you want it in any other coding agent"）；博文作者在腾讯 WorkBuddy 中完成实测（F-009/F-029/F-038） |

## 它解决的问题：Coding Agent "越来越聪明，却越来越难读"

HumanLayer 在发布文中直接用 "Coding agents are pretty much unreadable" 作为章节标题，并引用了 Reddit 前 CEO、pi 作者 Mario Zechner 等人对 Agent 长篇输出的吐槽（F-032）。其核心判断是：

> "agents got more intelligent on paper, but the experience of using them got noticeably worse along this dimension."
> （Agent 在纸面上越来越聪明，但沿"能不能让人快速读懂"这个维度，使用体验反而明显变差。）

博文作者的遭遇是这一判断的具体样本：他向 WorkBuddy 询问一个 AI 剪视频工作流（20 分钟口播 → 找高光、删废话、加字幕、插 B-roll → 3 条短视频，F-005）中各环节的先后顺序，得到的是"每个字都看得懂、组合在一起看不懂"的长篇专业内容（F-006）。**信息没有缺失，缺失的是结构**。

## "不增加新能力"的 Skill 形态

博文作者读完 SKILL.md 后的第一反应是"这也算 Skill？"——文件不大、就几行规则，核心被他概括为一句话（F-010，作者概括口径）：

> 别一上来给用户写小作文，能画出来，就尽量画出来。

他据此提出一个关键观察（**作者观点**，F-011）：

- WorkBuddy 本来就会画 Mermaid、本来就会写 HTML——Skill 没有赋予模型任何新能力；
- 它改变的是**表达方式**：把"默认写文字"切换成"默认画结构"，"没让 AI 变聪明，但让 AI 换了个脑子"。

这与官方对技能行为的描述一致：`/show-me` prompts the agent to use concise visuals... instead of walls of prose（F-032）。

## 设计论据：为什么"画"比"写"有效

官方将设计灵感归于 Coda Hale 的演讲《Intuition vs. Attention in Infrastructure Systems》（F-033）：

1. 分析信息是困难且耗神的（analyzing information is hard and exhausting）；
2. 人的视觉皮层经数百万年进化，能够毫不费力地处理丰富的视觉信息；
3. 因此工具应顺应这一特性来设计——"正如斧子必须合手才有用，软件必须契合人的心智才有用"。

博文作者用两个日常类比表达了同一层意思（**作者观点/类比**，F-013）：没人会写八千字描述地铁从人民广场到虹桥火车站经过的每一站——"画条线就完了"；公司组织架构也不会用五千字讲汇报关系——"一张组织架构图就搞定"。但面对 AI，人们却开始容忍它一天写几十篇小作文。

## 与本包其他篇目的关系

- [01-visual-vocabulary.md](01-visual-vocabulary.md)：show-me 具体让 Agent "画什么、怎么画"——官方 9 类可视化词汇与两轮官方用法。
- [02-subtraction-skills-pattern.md](02-subtraction-skills-pattern.md)：从这个 Skill 抽象出的"做减法的 Skill"模式，以及与 Grill Me 的对比、适用边界（作者观点层）。
- [../examples/00-install-and-invocation.md](../examples/00-install-and-invocation.md)：安装命令、三种调用方式与 WorkBuddy 路径实操。
