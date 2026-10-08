---
okf_version: "0.2"
type: bundle
title: "show-me-skill——让 Coding Agent 用视觉结构说话的 HumanLayer Skill"
description: "开源工具教程：HumanLayer 2026-08-12 开源的 show-me Skill 不教模型新能力，只用几行规则让 Agent 用 Mermaid/树/表/HTML 等紧凑视觉替代小作文。含官方 9 类可视化词汇、程序设计与大 diff 两大用法、作者三轮实测、安装调用实操与减法 Skill 模式。39 条事实，7 项 P0 核验全部✅，0 硬错误。"
author: OKF Wiki Bot
date: 2026-09-16
source: "https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ"
article_author: "胖啊（公众号：阿胖 AI 手记）"
article_date: "2026-09-06"
repo: "https://github.com/humanlayer/skills"
status: verified
stale_after: "2026-12-31"
tags: ["HumanLayer", "show-me", "Agent Skill", "Coding Agent", "Mermaid", "HTML explainer", "可视化沟通", "WorkBuddy", "减法Skill", "开源工具"]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ
  - id: official-blog
    url: https://www.humanlayer.dev/blog/show-me-skill
  - id: hn
    url: https://www.libhunt.com/posts/1530852-show-hn-show-me-agent-skill-for-compact-visual-representations
  - id: workbuddy-docs
    url: https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project
---

# show-me-skill

> **来源**：微信公众号「阿胖 AI 手记」（作者：胖啊），2026-09-06，原创
> **原文**：[《我发现一个神仙 Skill，就几行规则，没教AI任何新本事，却让我的WorkBuddy像换了个脑子！》](https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ)
> **官方发布**：[HumanLayer 官方博客《show-me: a coding agent skill for compact visual representations》](https://www.humanlayer.dev/blog/show-me-skill)（Dex Horthy，2026-08-12）
> **P0 核验**：7 项关键声明全部 ✅ 通过，0 ❌ 硬错误；2 项非错误性精度处理，详见 [verification.md](references/verification.md)

> **📌 内容性质**：开源 Skill 的个人一手实测体验文转化。技能机制/命令以 HumanLayer 官方博客为裁决依据；"做减法的 Skill"等论点与适用场景为博文作者观点，正文已逐条分层标注。

## 一句话定位

`show-me` 是 HumanLayer 开源的 Coding Agent Skill：**不向模型提供任何新能力，只用一份简短规则要求 Agent 把"写小作文"的默认输出换成"画结构"**——Mermaid 图、组件树、调用栈、文件布局、伪代码、类型签名、diff、HTML 原型与讲解页共 9 类视觉表达（F-010/F-031/F-034）。

## 快速安装与调用

```bash
npx skills add humanlayer/skills --skill show-me
```

```text
/show-me                              # 用紧凑视觉重新表达
/show-me as an html explainer         # 复杂内容生成 HTML 讲解页
```

完整路径（含 WorkBuddy 两种装法与自测步骤）：[examples/00-install-and-invocation.md](examples/00-install-and-invocation.md)。

## 知识结构

```
show-me-skill/
├── index.md
├── concepts/
│   ├── index.md
│   ├── 00-show-me-what-and-why.md       ← 发布事实：是什么、解决什么问题
│   ├── 01-visual-vocabulary.md          ← 机制：9 类视觉词汇 + 三轮实测
│   └── 02-subtraction-skills-pattern.md ← 模式：减法 Skill / 白板 vs 质询
├── examples/
│   ├── index.md
│   └── 00-install-and-invocation.md     ← 安装、三种调用、WorkBuddy 路径
├── references/
│   ├── index.md
│   ├── article-source.md                ← F-001~F-039 事实登记
│   └── verification.md                  ← 7 项 P0 全✅核验报告
└── log.md
```

## 分层导航

### 概念层（3 篇）

1. [show-me 是什么](concepts/00-show-me-what-and-why.md) — HumanLayer 发布事实、"小作文墙"问题、不增加新能力的 Skill 形态、设计论据
2. [可视化词汇表](concepts/01-visual-vocabulary.md) — 官方 9 类视觉表达、diff 四形态、两大用法、博文三轮实测映射
3. [做减法的 Skill](concepts/02-subtraction-skills-pattern.md) — show-me 白板模式 vs Matt Pocock Grill Me 质询模式、适用边界（观点分层）

### 实战层（1 篇）

1. [安装与调用实操](examples/00-install-and-invocation.md) — npx 安装、三种调用、WorkBuddy 极简/GitHub 连接器路径、自测与避坑

### 信源层（2 篇）

- [事实登记](references/article-source.md) — F-001~F-039（博文 30 + 核验补充 9）
- [核验报告](references/verification.md) — 7✅ 0❌、勘误四张清单、信源清单

## 信任与生命周期

- **事实基数**：39 条（F-001~F-039）
- **P0 核验**：7✅ 0⚠️（失败口径）0❌；另有 2 项非错误性精度处理（F-037 防误归因、F-039 路径单源）
- **status**：verified
- **stale_after**：2026-12-31（Skills 分发生态迭代活跃，年末复核命令与仓库结构）

## 已知边界

1. 博文为单一作者在 WorkBuddy（腾讯桌面 Agent，F-038）中的个人实测，"换了个脑子"等效果描述是主观体验而非对照实验结论；
2. 实测生成的五步流水线（听/懂/剪/配/出）与 9 分 12 秒字幕时间戳图（F-019/F-020）是作者环境的生成结果，不是官方固定模板；
3. 仓库内 SKILL.md 的具体路径本次未直取（F-039），"就几行规则"为作者阅读后概括（F-010）；安装命令与技能行为以官方博客为准；
4. HTML 内嵌渲染是 HumanLayer 自家产品能力，其他编码 Agent 需将 HTML 在浏览器打开（F-036）；
5. 与 show-me 对比的 Grill Me（`/grill-me`）为 **Matt Pocock** 出品，非 HumanLayer 同门（F-037）；
6. "做减法的 Skill"趋势判断与适用/不适用场景（F-021/F-023/F-024/F-025）均为博文作者观点，非行业共识。

## 主题关联

- 同分组 [anthropics-skills](../anthropics-skills/index.md) / [agent-skills-spec](../agent-skills-spec/index.md)：Agent Skills 的格式规范与官方技能参考——show-me 是"极简规则型 Skill"的一个实证样本；
- 同分组 [claude-vision-skill](../claude-vision-skill/index.md)：同为"博文转化的 Coding Agent Skill 工具教程"，可对照 Skill 的能力增强型（装眼睛）与表达约束型（换白板）两种设计取向。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
