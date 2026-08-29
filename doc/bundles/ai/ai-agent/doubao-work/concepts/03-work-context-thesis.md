---
type: Concept
title: 工作现场论点：模型vs组织上下文
description: 博文核心战略分析——AI办公真正难的是进入工作现场而非技能不足，Sam Altman引语，CLI/MCP接入工具vs接入工作，组织上下文四要素（归属/时效/有效性/权限），金句"模型决定AI有多聪明，组织上下文决定它能不能成为同事"
tags: [工作现场, 组织上下文, Sam Altman, Codex, 工作流, AI办公, 战略分析, 同事]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:55:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: appso-article
    resource: https://mp.weixin.qq.com/s/dqvRKQoH45cXL2F8z0ZHYw
    title: APPSO 豆包工作实测
  - id: altman-podcast
    resource: https://www.ababnews.com/opinions/fdc5f1bb-32dd-4d87-97bb-fcebb58ce676
    title: Sam Altman David Senra播客访谈整理
---

# 工作现场论点：模型vs组织上下文

> **事实基础**：本文为博文作者的战略分析，F-035~F-042 为作者观点（📝标注），非客观事实。Sam Altman引语（F-039）已经核验。完整事实清单见 [references/article-source.md](../references/article-source.md)，核验报告见 [references/verification.md](../references/verification.md)。

## 1. 核心论点

📝 博文结尾给出核心判断（F-035）：

> **AI办公真正难的，是进入工作现场。**

这不是技术能力问题——AI已经能写文档、做PPT、生成网页和视频。难的是让AI理解"我正在做什么工作、和谁一起做、事情推进到了哪一步"。

## 2. 工具接入 vs 工作接入

📝 博文区分了两种Agent接入方式（F-036）：

| 维度 | 多数Agent | 豆包工作+飞书 |
|------|----------|--------------|
| 接入方式 | CLI、MCP或连接器调用办公软件 | 飞书账号登录继承工作上下文 |
| 接入对象 | 某个工具、某份文件、某种能力 | 一个人在飞书里的**整个工作** |
| 数据范围 | 指定的文件夹/文档 | 聊天记录、文档、会议纪要、任务、组织关系（在权限范围内） |

### 真实工作的形态

📝 博文指出（F-037）：现实中的工作不会像使用办公Agent那样——"先给它指定一个文件夹，然后把需要的文档都放在里面"。

更真实的场景是：
- 冗长的聊天记录要复制
- 各式各样的文档散落各处
- 会议纪要、日历、项目表来自不同应用、不同数据格式
- 这些都是工作的一部分

## 3. "上下文"难题

📝 博文认为，要让AI真正进入工作场景，难的是把很难整理好的"上下文"交给AI，让它知道（F-038）：

1. **知识属于谁**（归属）
2. **发生在什么时候**（时效）
3. **现在是否还有效**（有效性）
4. **自己能不能使用**（权限）

这四个维度正是飞书这样的协作平台天然承载的信息——组织架构定义归属、时间戳定义时效、任务状态定义有效性、权限体系定义可用性。

## 4. Sam Altman 引语

博文引用OpenAI CEO Sam Altman在2026年8月23日David Senra播客访谈中的发言（F-039）：

> 今天明明已经有Codex，他却还是会在消息应用之间复制粘贴、翻邮件、维护待办。

Altman将原因归结为长期形成的心理习惯——人们倾向于将某种低效方式认定为"工作"本身。

> ✅ **核验通过**：原始访谈中Altman表示"He invented Codex many years ago but still works with a computer workflow from 20 years ago: copying and pasting between different messaging apps, picking the easiest email to reply to, and maintaining a to-do list"。博文引语义准确，措辞为中文意译。

博文借此论证（F-040）：
- 技术已经走到前面
- 人和产品的使用方式还没完全跟上
- 问题从"AI能不能做"变成了"怎么让AI自己走进人们原来的工作流"

## 5. 豆包+飞书的分工

📝 博文对豆包工作的战略定位（F-041）：

| 组件 | 提供什么 |
|------|---------|
| **豆包** | 完成任务的能力（生成、操作、推理） |
| **飞书** | 已经存在的工作环境 |

飞书提供的工作环境包含五个维度：

```
组织架构 → 告诉AI"谁是谁"
聊天/文档 → 记录"公司过去发生了什么"
任务/多维表格 → 保存"项目当前状态"
账号/权限 → 决定"能进入哪些地方"
结果写回 → 成为"下一次任务的上下文"
```

这形成了一个闭环：AI从飞书获取上下文 → 完成任务 → 结果写回飞书 → 成为未来任务的上下文。

## 6. 金句

📝 博文最后给出被广泛引用的判断（F-042）：

> **模型决定AI有多聪明，组织上下文决定它能不能成为同事。**

博文进一步阐释（F-035、F-040）：
- AI已经开始帮人跨出专业边界
- 组织上下文决定它能不能继续跨进一家公司的真实边界
- 真正改变办公方式的那一刻，不是AI又学会一项新技能，而是它不再等着我们把工作搬给它，开始自己走进工作发生的地方

## 7. 论点逻辑链

```
AI技能已足够（写文档/做PPT/生成视频）
  ↓
但多数Agent只接入"工具"，没接入"工作"
  ↓
真实工作是散落的聊天/文档/会议/日历/项目表
  ↓
难的是交给AI"上下文"：归属/时效/有效性/权限
  ↓
飞书天然承载这四维度（组织/时间戳/任务状态/权限）
  ↓
豆包提供能力 + 飞书提供环境 = AI走进工作现场
  ↓
模型决定聪明程度，组织上下文决定能否成为同事
```

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- Sam Altman访谈整理：https://www.ababnews.com/opinions/fdc5f1bb-32dd-4d87-97bb-fcebb58ce676
- 飞书深度集成：[02-feishu-integration.md](02-feishu-integration.md)
