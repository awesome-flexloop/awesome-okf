---
type: OKF
title: 分支选择决策指南
description: 用想解决什么、偏好什么表达形态、是否需要临床资质、中文语境四个问题逐层分流，把读者导向六个束中最适合的一个及对应入口文档。
tags: [art-therapy, 艺术疗愈, 决策指南, 分支选择]
version: "1.0.0"
sources:
  - id: facts
    resource: facts.md
    title: 事实登记与信源表（OV-01 ~ OV-11）
generated: { by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }
status: stable
stale_after: 2027-09-01
---

# 分支选择决策指南

“我对艺术疗愈感兴趣，该从哪里入手？”——这个问题无法直接回答，因为六个束对应六种不同的需求场景。本指南把选择过程拆成四个问题，按序作答即可定位目标束。每个问题只做一次分流，做完四问最多进入两个束；不需要读完全部六束。

下图把四个问题画成决策树——按序作答，每个出口直接指向一个目标束或一项资质核对动作；本图为阅读导航，不构成治疗建议。

```mermaid
flowchart TD
  Q1 {"问题一：你想解决什么？"}
  Q1 -->|"确诊或在治的心理健康问题，想寻求治疗"| Q3 {"问题三：是否处于需要临床资质的场景？"}
  Q1 -->|"压力调适、兴趣培养、自我成长"| Q2 {"问题二：你偏好哪种表达形态？"}
  Q1 -->|"文化研究、写作、报道，想弄清概念与史实"| RD ["研究层：阅读路径与方法论，以 facts 层为引用底座"]
  Q2 -->|"绘画、雕塑等视觉艺术"| ATB ["art-therapy 束"]
  Q2 -->|"唱歌、演奏、聆听"| MTB ["music-therapy 束"]
  Q2 -->|"身体动作、舞蹈"| DDB ["dance-drama-therapy 束"]
  Q2 -->|"角色扮演、剧场"| DDB
  Q2 -->|"写作读诗，或不愿限定单一模态"| EXB ["expressive-arts 束"]
  Q3 -->|"是：患者、医疗机构、标准化治疗关系"| CERT ["核对资质缩写与发证机构：ATR-BC、MT-BC、R-DMT、RDT；否决速成班拿证即可治疗的宣称"]
  Q3 -->|"否：社区、文旅、自我使用场景"| AIHB ["arts in health 语域：引用时保留证据限定语"]
  Q4 {"问题四：中文语境有哪些专属判据？"}
  CERT -.->|"涉中文材料时"| Q4
  EXB -.->|"涉中文材料时"| Q4
  Q4 -->|"艺术治疗与艺术疗愈混用"| TERM ["按服务人群、执业场域、从业背书三判据核对"]
  Q4 -->|"五音疗疾式溯源叙事"| CN ["china-art-therapy 束：两套话语体系分层处理"]
```

## 问题一：你想解决什么？

这是最重要的分流，决定你在三层术语结构（[定义辨析与术语分层](../concepts/00-overview.md)，洞察 2）中处于哪一层。

- **确诊或在治的心理健康问题，想寻求治疗** → 你处于临床职业层。直接跳到问题三（资质核验是硬门槛），分支形态后定。提醒：本知识组是文献资料不是医疗建议（束根免责声明），就诊请找持证专业人士。
- **一般压力调适、兴趣培养、自我成长** → 你处于广义关怀层（arts in health 语域，facts OV-06）。可优先看 [expressive-arts 束](../../expressive-arts/index.md)与本束[循证证据概貌](../concepts/02-evidence.md)，并在对外宣传材料上使用问题四的判据。
- **文化研究、写作、报道，想弄清概念与史实** → 你处于研究层。以 [阅读路径与方法论](../concepts/04-reading-paths.md) 的学术研究向路径为主干，facts 层是你的引用底座。

## 问题二：你偏好哪种表达形态？

对想要实践或学习的人而言，模态偏好是最自然的入口。六分支对应关系如下（谱系细节见[历史脉络与分支谱系](../concepts/01-history.md)）：

| 你的偏好 | 对应分支 | 目标束 |
|---|---|---|
| 绘画、雕塑等视觉艺术 | 美术治疗（art therapy） | [art-therapy 束](../../art-therapy/index.md) |
| 唱歌、演奏、聆听 | 音乐治疗（music therapy） | [music-therapy 束](../../music-therapy/index.md) |
| 身体动作、舞蹈 | 舞动治疗（dance/movement therapy） | [dance-drama-therapy 束](../../dance-drama-therapy/index.md) |
| 角色扮演、剧场 | 戏剧治疗（drama therapy，根系为心理剧） | [dance-drama-therapy 束](../../dance-drama-therapy/index.md) |
| 写作、读诗 | 诗歌治疗（poetry/bibliotherapy；现阶段暂并于表达性艺术束叙述） | [expressive-arts 束](../../expressive-arts/index.md) |
| 不想限定单一模态，愿在多模态间流动 | 表达性艺术治疗（expressive arts therapy，intermodal 模型，facts OV-05） | [expressive-arts 束](../../expressive-arts/index.md) |

注意：模态偏好决定的是**学习与体验入口**，不决定治疗适配性——临床层面的模态选择应由持证治疗师评估，本文不提供该建议。

## 问题三：你是否处于需要临床资质的场景？

判断依据：服务对象是否为心理疾病患者、场景是否为专业医疗机构或心理咨询室、是否建立标准化治疗关系（facts OV-06 的三要素）。任一为“是”，即进入临床资质场景。

- **是** → 核对三件事：从业者的资质缩写对应的发证机构是否存在且可查（ATR-BC/MT-BC/R-DMT/RDT 对照表见[职业体系与资源地图](../concepts/03-professional-orgs.md)）；所在地区的职业化处于五步路径的哪一步（洞察 6）——例如中国正处于“高校专业已设、国家职业资格目录缺位”的第四至五步之间（facts CN-09、CN-10）；对“速成班几天拿证书即可治疗心理疾病”类宣称直接否决（facts CN-10）。
- **否**（社区、文旅、自我使用场景） → 仍建议核对宣称者背景，但门槛要求不同：此场景对应 arts in health 语域，其证据强度低于临床层，引用时保留限定语（[循证证据概貌](../concepts/02-evidence.md)，洞察 3）。

## 问题四：中文语境中有哪些专属判据？

中文材料有两类高频陷阱，需要专属检查：

1. **“艺术治疗”与“艺术疗愈”混用**：按判据表核对（服务人群/执业场域/从业背书，facts OV-06）；首次出现术语处应有英文原词。
2. **“五音疗疾”式溯源叙事**：把中医五音情志话语与 20 世纪循证 music therapy 直接接续是叙事错误——两套体系范式与验证标准不同，现代音乐治疗进入中国的锚点是 1988 年中国音乐学院音乐治疗大专班（facts CN-05、CN-06、洞察 4）。涉及此类材料，进入 [china-art-therapy 束](../../china-art-therapy/index.md)。

## 决策结果对照表

| 你的四问答案组合 | 目标束 | 建议入口 |
|---|---|---|
| 寻求治疗＋偏好视觉/音乐/身体戏剧 | art-therapy / music-therapy / dance-drama-therapy | 各束 concepts/00 总览＋本束概念 03 核资质 |
| 自我成长＋多模态或写作 | expressive-arts 束 | concepts/00＋本束概念 02 |
| 研究写作＋中文材料辨析 | china-art-therapy 束 | facts 层＋洞察 4 |
| 只是弄懂术语 | 本束（liaoyu-overview） | 概念 00→02，够了 |

四问走完仍拿不准时，回到束根[快速开始](../../index.md)：先概念 00 分层，再示例 02 判资料，最后按路径表选束。
