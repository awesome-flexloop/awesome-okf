---
type: concept
title: "沟通与写作类 Skills 详解"
description: "internal-comms/academy-guide/discernment-nudge 三个沟通类 Skill 的用途、结构、编写规范与可复用模式，含薄壳路由、正向推荐规则与反触发清单三种典型写法。"
tags: [skills, writing, communication, internal-comms, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# 沟通与写作类 Skills 详解

覆盖 3 个 skill：`internal-comms`、`academy-guide`、`discernment-nudge`。

三个都是**纯指令型**（零脚本、零资源目录或近零），但示范了三种截然不同的写法策略：

| skill | 策略 | 核心机制 |
|-------|------|---------|
| internal-comms | **薄壳路由** | 32 行 SKILL.md 分派到 4 篇文风模板 |
| academy-guide | **正向推荐规则** | 先立"只在强匹配时推荐"再给目录 |
| discernment-nudge | **反触发清单** | 明确枚举 9 类不该追问的场景 |

---

## 一、internal-comms —— 薄壳路由器

| 维度 | 内容 |
|------|------|
| **用途** | 写各类内部沟通：状态报告、领导层更新、3P 更新、公司通讯、FAQ、事故报告、项目更新 |
| **SKILL.md** | **32 行**（19 个中最短，F-043） |
| **资源** | `examples/` 4 篇（**无 `templates/` 目录**，F-078） |

### 完整正文结构（F-079）

```markdown
## When to use this skill
   （7 类沟通类型清单）

## How to use this skill
1. Identify the communication type from the request
2. Load the appropriate guideline file from the `examples/` directory
3. Follow the specific instructions in that file

## Keywords
   （8 个关键词）
```

SKILL.md 本身**不含任何写作规范**——它只做一件事：**识别类型 → 加载对应文件**。

### 4 篇模板的结构

| 文件 | 用途 |
|------|------|
| `examples/3p-updates.md` | Progress/Plans/Problems 团队更新 |
| `examples/company-newsletter.md` | 全公司通讯 |
| `examples/faq-answers.md` | 常见问题答复 |
| `examples/general-comms.md` | **兜底**——其余一切 |

### 模板的两段式结构（F-080）

以 `3p-updates.md` 为例：

```markdown
## Instructions
（受众是谁、读多久、粒度规则、三段式定义）

## Tools Available
（到哪里取信息：Slack / Google Drive / Email / Calendar，及时间窗口）
```

第一段讲**怎么写**，第二段讲**从哪拿数据**。第二段尤其值得学——它把"内容收集"当成写作任务的一部分来规定，并给出各来源的时间窗（Progress 与 Problems 看过去一周，Plans 看未来一周）。

### 编写规范要点

1. **兜底文件必须存在**——`general-comms.md` 承接所有未明确匹配的类型。这保证 skill 永远有路可走，不会因"没匹配上"而空转。
2. **匹配不上时先问**——"If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format."
3. **关键词表放在正文末尾**——作为兜底的语义匹配线索（description 只有一句话概括）。

> 🟢 **可复用模式（模板路由器）**：当"一种能力"下有多种**明显不同的输出形态**时，不要把全部规范塞进 SKILL.md——写成**薄壳 SKILL.md + 每形态一个 guideline 文件**。SKILL.md 只负责路由，形态规范各自独立、按需加载。
>
> 关键设计是**兜底文件 + 匹配不上就问**这两条：前者保证不空转，后者避免硬套。

---

## 二、academy-guide —— 正向推荐规则

| 维度 | 内容 |
|------|------|
| **用途** | 推荐匹配的 Claude Academy 课程、教程、use case |
| **SKILL.md** | 147 行 |
| **资源** | 无（纯指令） |

### 三段结构（F-081）

```
# Claude Academy guide
## Purpose
## Rules
## The catalog
```

### description 是强度 A（场景枚举型）的代表

```
Stop and check this skill before finishing any reply to a question about how
to use Claude or a Claude product ... Trigger on: "how do I", "how can I",
"getting started with", "what can Claude do", "teach me", "learn to use";
questions about artifacts, projects, skills, plugins, connectors, MCP;
requests about rolling Claude out to a team, class, or organization; and any
ask for training materials, onboarding content, or learning resources.

Use it when the user is learning how to use a feature or product — not when
they are mid-task and just want the task done.

This skill composes with other skills: after consulting product documentation
to answer how a Claude feature works, also check here for a matching course
or tutorial ...

Only recommend on a strong match; never invent Academy content.
```

四个可抄的设计：

| 设计 | 作用 |
|------|------|
| **Stop and check this skill before finishing any reply** | 明确是"回复前"动作，不是"任务中"动作 |
| **Trigger on: "..." 引号枚举** | 字面问法可直接匹配 |
| **not when they are mid-task and just want the task done** | 反触发（F-082） |
| **composes with other skills** | 显式声明与其他 skill 的协作顺序 |
| **Only recommend on a strong match; never invent Academy content** | 内容真实性约束 |

### 🔴 "never invent" 类约束是推荐型 skill 的生命线

F-082：它的 Rules 段定义了**不触发**的边界——与 `claude-api` 的 SKIP 块同构。

> 🟢 **可复用模式（推荐型 skill）**：推荐类 skill 必须写死两条——**何时可以推荐**（强匹配条件）+ **何时绝不推荐**（编造禁令）。只写前者，模型在无匹配时会"尽力推荐一个"，输出幻觉。
>
> 附带一条：推荐型 skill 通常还应声明**与其他 skill 的组合关系**（先查文档 → 再查课程），这让多个 skill 能串成完整的学习链路。

---

## 三、discernment-nudge —— 反触发清单

| 维度 | 内容 |
|------|------|
| **用途** | 给出实质性回答后追加 2-3 个针对性追问，帮用户校验事实、检验推理、发现缺失上下文 |
| **SKILL.md** | 209 行 |
| **资源** | 无（纯指令） |

### 五段结构（F-083）

```
# Discernment nudge
## Why this exists
## When to offer the nudge
## When not to
## Writing the prompts
## Output format
```

### 触发条件（description 层）

在给出**实质性回答或草稿之后**触发——具体列举：建议/推荐、草拟产物（目标、计划、提案、邮件）、估算或预测、数据分析或解读、用户可能依赖的事实主张、多步论证。

并明确 **"Do this at most once per conversation"**（每次对话最多一次）。

### 🔴 9 类应跳过的场景（F-084）

"When not to" 段逐条列出：

1. **Creative writing** —— 诗、故事、头脑风暴、起草
2. **Casual conversation** —— 寒暄、闲聊、交换看法
3. **Code the user will execute** —— 用户自己会运行的代码（运行即验证）
4. **Simple lookups** —— 单位换算、定义、"哪一年…"
5. **Purely educational explanations** —— "X 怎么工作"、"解释…"
6. **The user asked you to verify, cite, or flag uncertainty** —— 用户已要求过复核/引用/标注不确定性
7. **The user asked for the quick version** —— 或说他们自己来做
8. **The user asked you to check something of theirs** —— "帮我看看我这个…"
9. **The user gave you the material** —— 只做摘要、重排、格式化

### 编写规范要点

1. **先讲"为什么存在"**——`## Why this exists` 置于最前。存在理由讲清了，边界才推得出来。
2. **跳过场景写得比触发场景还细**——反触发清单是这类 skill 的主要工作量所在。
3. **输出格式独立成段**——`## Output format` 明确"追加 2-3 个短追问，每个都锚定在刚才产出的具体内容上"，而非泛泛追问。

> 🟢 **可复用模式（干预型 skill）**：这类 skill 的风险不是"不触发"，而是"过度触发"——每次回答都追加追问会变成噪音。三个防线：
> ① **频率上限**（每次对话最多一次）
> ② **详尽的跳过清单**（枚举不该触发的情况）
> ③ **输出锚定要求**（每个追问必须指向刚才产出中的具体点，禁止泛问）
>
> 这三条可以照搬到任何"给建议/加提示"型的扩展能力。

---

## 四、三者横向对比

| skill | SKILL.md 行数 | 资源 | 写作策略 | 最值得抄的一点 |
|-------|------------|------|---------|--------------|
| internal-comms | 32 | 4 篇 examples | 薄壳路由 | 兜底文件 + 匹配不上就问 |
| academy-guide | 147 | 无 | 正向推荐规则 | "Only recommend on a strong match; never invent" |
| discernment-nudge | 209 | 无 | 反触发清单 | 频率上限 + 跳过清单 + 输出锚定 |

### 共同的观察

三个 skill 都是**纯指令、零脚本**，但正文字数从 32 到 209 行不等——**篇幅由任务复杂度决定，不由"是不是纯指令"决定**：

- `internal-comms` 只有 32 行，因为真正的规范在 4 个外部文件里
- `discernment-nudge` 209 行，因为它要精细划边界（边界本身就是它的产品）
- `academy-guide` 147 行，因为推荐规则本身就是它的产品

> 🟢 **可复用模式**：判断一个 skill 该写多长，先问"**真正的规范放在哪**"。如果规范可以外置，SKILL.md 就该薄；如果边界判断本身就是产品（如"什么时候该追问"），SKILL.md 就必须厚。

---

## 相关文档

- [全部Skills索引](../references/skills-index.md) — 19 个 skill 速查
- [事实登记表](../references/facts.md) — F-078~F-086 实测
- [Skill 编写规范与可复用模式](04-authoring-patterns.md) — 跨 skill 通用模式
