---
okf_version: "0.2"
type: bundle
title: "TRAE 训练营第二期 02 课：用 TRAE 改造你的 Agent 助手"
description: "以 TRAE 官方训练营第二课为信源、并经小满源码核验的改造教程——记忆/技能/程序三层改造面、3-2-1 个人档案与 adb 推送、四问写成 SKILL.md、五场景试改验循环、程序层自建技能、多 Agent 总管技能与证据链排障（源码复读 9✅/2⚠️/0❌）"
tags:
  - trae
  - agent
  - skills
  - memory
  - adb
  - multi-agent
  - prompt-design
  - android
  - course
generated: 2026-11-16
verified: process:seven-concepts-v
status: stable
stale_after: 2027-05-31
sources:
  - id: course-doc
    resource: "TRAE 训练营第二期 02 课课程文档（飞书托管，需课程权限；按课程方口径不在公开仓库引用其 URL）"
    title: "TRAE 训练营第二期｜02 课：从能用到懂你，用 TRAE 改造你的 Agent 助手"
  - id: xiaoman-source
    resource: "本地 xiaoman 仓库（main commit 580fdf7 与远端分支 origin/camp/xiaoman，2026-11-17 只读核验）"
    title: "小满/PhonePal 源码"
  - id: xiaoman-repo
    url: https://github.com/aduoge/xiaoman
    title: "小满（xiaoman）课程版源码仓库"
  - id: xiaoman-branch
    url: https://github.com/aduoge/xiaoman/tree/camp/02-skill-builder
    title: "小满 02 课分支：手机上自建技能"
  - id: superagent-lead
    url: https://github.com/aduoge/superagent-lead
    title: "superagent-lead（总管）技能仓库"
  - id: ark-model-list
    url: https://ark.volcengine.com/region:cn-beijing/docs/model-list
    title: "火山方舟：模型列表"
  - id: trae-forum
    url: https://forum.trae.cn/c/44-category/44
    title: "TRAE 官方中文社区：官方训练营"
---

# TRAE 训练营第二期 02 课：用 TRAE 改造你的 Agent 助手

> **内容性质**：厂商官方培训材料的系统化转写与核验（**改造教程**，非源码解读、非产品评测）。主信源为 TRAE 官方训练营第二课课程文档（课程于 2026-11-13 晚间结课；初采 2026-11-16 revision 1074，2026-11-18 复读 revision 1076），交叉核对源码仓库、方舟官方模型文档与 TRAE 官方社区。
>
> **核验结果**：初轮 P0 11 项 → 4 ✅ / 7 ⚠️；2026-11-17 源码核验后 → 8 ✅ / 3 ⚠️；2026-11-18 源码复读后 → **9 ✅ / 2 ⚠️ / 0 ❌**。五个场景技能、`chat` channel、`camp/02-skill-builder` 与 0.2.0 均已由公开仓库确认；剩余 ⚠️ 为 superagent-lead 仓库可达性与 401/404 归因。
>
> **敏感度处理**：主信源托管于企业内部飞书域，本包按用户指定目录落盘。正文与信源层**不引用课程文档 URL**；不转载课堂体验额度的领取入口、IP 形式服务地址、令牌与个人登记信息（该额度已于 2026-11-13 过期）；附件与视频的一次性令牌不收录。

## 一句话结论

第一课让助理「能用」，这一课让它「像你」：**记忆**把你的习惯变成档案，**技能**把重复流程变成四问齐备的 SKILL.md，**程序**把「手机上一句话自己写技能」变成能力。三层的生效成本依次升高，所以改造顺序应当是记忆 → 技能 → 程序。

## 你会读到什么

| 你现在的状态 | 建议路径 |
|--------------|----------|
| 第一课还没跑通 | [01 回顾与高频问题](concepts/01-recap-and-faq.md) → [示例一](examples/01-profile-to-memory.md) |
| 只想让它更懂我 | [02 个人档案](concepts/02-personal-profile.md) → [示例一](examples/01-profile-to-memory.md) |
| 想让它多会一件事 | [03 工作流与技能](concepts/03-workflow-and-skill.md) → [04 试改验循环](concepts/04-skill-edit-loop.md) → 六篇示例挑一个 |
| 想改程序 / 做多助理 | [05 程序层改造](concepts/05-program-layer.md) → [06 多 Agent](concepts/06-multi-agent-superagent.md) → [07 证据链排障](concepts/07-evidence-debugging.md) |
| 想带走方法论 | [五条洞察](insights.md) → [六个可迁移模式](patterns.md) |

## 信源说明

| 信源 | 类型 | 层级 | 用途 |
|------|------|------|------|
| TRAE 训练营 02 课课程文档（初采 1074 / 复读 1076） | 主信源 | 厂商官方培训材料（一手） | 三层框架、四问、五场景、程序改造、多 Agent、排障模板 |
| 小满源码（main 580fdf7 + 远端 camp/xiaoman） | 权威 | 第一方源码（只读核验） | 包名与版本、技能七字段与 channel 枚举、校验规则、CLI 输出、轨迹、Sentinel、提醒 |
| 02 课分支与 0.2.0 安装包 | 课程提供 | 未取得 | 公开远端无该分支，相关能力仍为课程单源 |
| superagent-lead 仓库 | 课程提供 | 一手材料地址 | 总管技能的安装与用法（独立仓库，未核验） |
| 火山方舟官方模型文档 | 权威 | 官方文档 | Base URL、模型存在性与视觉/GUI 能力 |
| TRAE 官方社区 | 参考 | 公开社区 | 训练营作业与课程背景 |

## 知识结构

```
trae-agent-camp-02/
├── index.md                                ← 你在这里
├── insights.md                             五条洞察（陈述/证据/反常识/行动）
├── patterns.md                             六个可迁移模式（L1-draft）
├── concepts/
│   ├── 00-course-map.md                    五件事、三层改造面、改哪里决策表
│   ├── 01-recap-and-faq.md                 上节课回顾、六组高频问题、鸿蒙口径
│   ├── 02-personal-profile.md              3-2-1、档案、adb 桥、三句话验证
│   ├── 03-workflow-and-skill.md            工作流与技能、四问、SKILL.md
│   ├── 04-skill-edit-loop.md               试改验三步、lint/push、成功判据
│   ├── 05-program-layer.md                 程序层、三处改动、分支与安装包
│   ├── 06-multi-agent-superagent.md        两种形态、五条原则、公众号小队
│   ├── 07-evidence-debugging.md            证据三件套、logs/traces、最小修改
│   ├── 08-boundaries-and-safety.md         设备与能力边界、泄露面、双闸门
│   └── 09-module-internals.md              技能生命周期、循环参数、Sentinel、MCP、SKILL_SAVE
├── examples/
│   ├── 01-profile-to-memory.md             3-2-1 → 档案 → 推送 → 验证
│   ├── 02-today-plan.md                    今日开工卡
│   ├── 03-health-alarms.md                 健康闹钟
│   ├── 04-taobao-compare.md                淘宝比价
│   ├── 05-daily-quiz.md                    每日出题与错题本
│   └── 06-ai-news-brief.md                 资讯速览
└── references/
    ├── course-source.md                    F-001~F-124 事实登记
    ├── source-code.md                      源码核验事实（选录 S-001~S-059）
    └── verification.md                     P0 核验、勘误四清单、缺口、四视角审查
```

## 分层导航

### 概念文档（10 篇）

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [课程地图](concepts/00-course-map.md) | 五件事、三层改造面、改哪里的决策表、设备分工、三条路径 |
| 01 | [回顾与高频问题](concepts/01-recap-and-faq.md) | 源码与材料、体验额度、双模型、401/404、无障碍、模拟器 |
| 02 | [个人档案](concepts/02-personal-profile.md) | 3-2-1、TRAE 整理提示词、手动/自动两种存法、adb 三步与判读 |
| 03 | [工作流与技能](concepts/03-workflow-and-skill.md) | 工作流 vs 技能、四问细节、技能文件位置、chat 与 gui |
| 04 | [试改验循环](concepts/04-skill-edit-loop.md) | 三步法、lint 与 push、五场景对照、什么叫改成了 |
| 05 | [程序层改造](concepts/05-program-layer.md) | 三条路径、四件事、改三处、验收四点、分支与卸载风险 |
| 06 | [多 Agent](concepts/06-multi-agent-superagent.md) | 两种形态、五条原则、总管技能安装用法、拆分四规则与交接单 |
| 07 | [证据链排障](concepts/07-evidence-debugging.md) | 三件套、logs/traces、排错模板、先回退再取证 |
| 08 | [边界与安全](concepts/08-boundaries-and-safety.md) | 硬边界、记忆与技能泄露面、双闸门、不可逆清单、脱敏 |
| 09 | [模块内部](concepts/09-module-internals.md) | 技能生命周期、操作循环参数、Sentinel、MCP 路由、SKILL_SAVE 与三种运行形态 |

### 实战示例（6 篇）

| 文档 | 内容 |
|------|------|
| [个人档案推到手机](examples/01-profile-to-memory.md) | 六步完整流程 + 三句话验证 |
| [今日开工卡](examples/02-today-plan.md) | 排序规则、最多 3 件、提醒确认 |
| [健康闹钟](examples/03-health-alarms.md) | 内置链接、按作息挑空档、不动原有闹钟 |
| [淘宝比价](examples/04-taobao-compare.md) | 前 3 家、页面未显示、停在商品页 |
| [每日出题](examples/05-daily-quiz.md) | 答前不给答案、错题进记忆、复习错题 |
| [资讯速览](examples/06-ai-news-brief.md) | 按偏好筛、附来源、不编新闻 |

### 洞察与模式

| 文档 | 内容 |
|------|------|
| [五条洞察](insights.md) | 改造面决定生效成本；技能是流程契约；可靠性靠证据；闸门下沉；先单后多 |
| [六个可迁移模式](patterns.md) | 三层改造面、四问成技、试改验循环、证据先行、单产出拆分、双闸门 |

### 信源参考（3 篇）

| 文档 | 内容 |
|------|------|
| [课程事实登记](references/course-source.md) | F-001~F-124，十类分组，课程原文与核验补充分开；含 2026-11-18 复读补充 |
| [源码核验事实登记](references/source-code.md) | 选录 S-001~S-059，技能格式、校验、CLI、轨迹、Sentinel、提醒、02 分支与新增模块 |
| [P0 核验与对抗审查](references/verification.md) | 11 项核验（源码复读后 9✅/2⚠️）、勘误四张清单、10 项缺口、四视角 8 条意见 |

## 信任与生命周期

- **P0 核验**：初轮 11 项中 4 项通过、7 项部分通过、0 项失败；2026-11-17 源码核验后为 8 项通过、3 项部分通过；2026-11-18 源码复读后为 **9 项通过、2 项部分通过、0 项失败**。
- **事实分级**：课程 F-001~F-124；源码核验另登记 43 条 S 事实（S-001~S-059 选录）；讲师个人实践（多助理小队、五条原则、公众号小队）均标【讲师口径】。
- **status: stable 的理由**：五个场景技能、`chat` channel、`camp/02-skill-builder`、0.2.0 版本与 `SKILL_SAVE` 均已由公开仓库确认；剩余 ⚠️ 为 superagent-lead 仓库可达性与 401/404 归因，不影响教程主线。
- **stale_after**：2027-05-31。到期或触发以下任一条件时复核：① 训练营开设新一期或发布新安装包；② 02 课分支合并回 main；③ superagent-lead 仓库变更可见性或安装方式。

## 已知边界

1. **版本已确认**：main 为 `0.1.0`（versionCode 1），`camp/02-skill-builder` 为 `0.2.0`（versionCode 2）；0.2.0 安装包 zip 不在仓库中，只有课程附件（G-01 关闭，S-004）。
2. **无校验信息**：课程安装包无校验和与签名信息（G-02）。
3. **仓库与分支已核验**：远端包含 `main`、`camp/xiaoman`、`camp/xiaoman-web`、`camp/02-skill-builder`、`ios/wda-hands`；`superagent-lead` 是独立仓库，未核验（G-03 关闭，S-001、S-002、S-052）。
4. **CLI 输出已核验**：`lint` 摘要为 `N skill(s) checked, N ok, N problem(s)`，`push` 输出 `pushed ...` 与 `skills reloaded`；`logs`、`traces pull/show` 行为与参数已确认（G-04 关闭，S-046~S-049）。
5. **目录与格式已核验**：记忆、技能、轨迹目录与 Basic Memory 结构已由源码确认（G-05 关闭，S-008~S-013）。
6. **多设备已核验**：CLI 原生支持 `--serial/-s`，可写在子命令前后（G-07 关闭，S-046）。
7. **体验额度已过期**：课堂体验服务随结课失效，相关操作细节不收录（F-011、G-09）。
8. **不做能力外推**：淘宝场景只比当天搜索结果，不承诺历史低价与跨平台；也不承诺能读微信/QQ 或控制电脑（F-100）。
9. **02 课专属能力已公开**：五个场景技能、`channel: chat` 与 0.2.0 分支均已进入公开仓库（G-10 关闭，S-035、S-038、S-058）。
10. **时点边界**：本包反映 2026-11-18 的课程与源码口径；新增的 MCP、网页版与 iOS 通道不在本课范围。

## 主题关联

| 关联束 | 关系 |
|--------|------|
| [TRAE Community 生态（分组首页）](../index.md) | 上级分组；本束归入「📚 学习资源」板块 |
| [第一课：手机 Agent 从零到可用](../trae-agent-camp-01/index.md) | 前置课程；本包承接其 App、源码与四要素任务书 |
| [trae-one-click-deploy](../trae-one-click-deploy/index.md) | 同为课程/公告类转化束，同样因单源密集取 `status: draft` |
| [trae-skills](../trae-skills/index.md) | 社区技能仓库的 SKILL.md 规范与模式，可与本包「四问成技」对照 |
| [trae-learning](../trae-learning/index.md) | 官方学习站源码；本包是面向学习者的课程内容 |
| [volcengine](../../volcengine/index.md) | 方舟模型与计费口径的上游产品分析 |

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
insights
patterns
log
```
