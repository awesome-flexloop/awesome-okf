---
okf_version: "0.2"
type: bundle
title: "TRAE 训练营第二期 01 课：手机 Agent 助理从零到可用"
description: "以 TRAE 官方训练营第二期第一课为信源、并经小满源码核验的手机 Agent 教程——Chatbot 与 Agent 之别、七件事与 ReAct 循环、安装与方舟双模型配置、记忆与提醒、任务四要素、用 TRAE 只读读项目、人类在环的七个卡点（源码轮 7✅/3⚠️/0❌）"
tags:
  - trae
  - agent
  - mobile-agent
  - react
  - volcengine-ark
  - memory
  - prompt-design
  - android
  - course
generated: 2026-11-15
verified: process:seven-concepts-v
status: stable
stale_after: 2027-05-31
sources:
  - id: course-doc
    resource: "TRAE 训练营第二期 01 课课程文档（飞书托管，需课程权限；按课程方口径不在公开仓库引用其 URL）"
    title: "TRAE 训练营第二期｜01 课：从零到可用，让 Agent 助手帮你完成第一个任务"
  - id: xiaoman-source
    resource: "本地 xiaoman 仓库（main commit 580fdf7 与远端分支 origin/camp/xiaoman，2026-11-17 只读核验）"
    title: "小满/PhonePal 源码"
  - id: ark-model-list
    url: https://ark.volcengine.com/region:cn-beijing/docs/model-list
    title: "火山方舟：模型列表"
  - id: ark-quickstart
    url: https://ark.volcengine.com/region:cn-beijing/docs/quick-start-code
    title: "火山方舟：快速入门（代码）"
  - id: ark-product
    url: https://www.volcengine.com/product/ark/
    title: "火山方舟产品页"
  - id: gmw-doubao
    url: http://economy.gmw.cn/2026-09/14/content_38999844.htm
    title: "光明网：豆包手机助手发布消费者版本"
  - id: trae-camp-news
    url: https://www.sina.cn/news/detail/5362227060412987.html
    title: "新浪新闻：TRAE 训练营第二期开课信息"
  - id: trae-forum
    url: https://forum.trae.cn/c/44-category/44
    title: "TRAE 官方中文社区：官方训练营"
  - id: react-paper
    url: https://arxiv.org/abs/2210.03629
    title: "ReAct: Synergizing Reasoning and Acting in Language Models"
---

# TRAE 训练营第二期 01 课：手机 Agent 助理从零到可用

> **内容性质**：厂商官方培训材料的系统化转写与核验（**教程**，非源码解读、非产品评测）。主信源为 TRAE 官方训练营第二期第一课课程文档（2026-11-12 开课；采集于 2026-11-15，revision_id 1236），交叉核验小满源码、火山方舟官方文档、光明网与 TRAE 官方社区。
>
> **核验结果**：初轮 P0 10 项 → 5 ✅ / 5 ⚠️；2026-11-17 源码核验后 → **7 ✅ / 3 ⚠️ / 0 ❌**。源码已确认：仓库与版本（0.1.0）、记忆路径与 Basic Memory 格式、提醒调度（非精确定时、重启清空）、Sentinel 规则与许可证（MIT）。剩余 ⚠️ 为免费额度口径、设备边界表述与费用估算，故本包取 `status: stable`。
>
> **敏感度处理**：主信源托管于企业内部飞书域，本包按用户指定目录落盘。正文与信源层**不引用课程文档 URL**，不转载课堂体验额度的领取流程、令牌与个人登记信息（该额度已于 2026-11-13 21:00 过期），附件与视频的一次性令牌不收录。

## 一句话结论

这一课交付的不是「一个更聪明的聊天机器人」，而是**一副能读屏、能点击、会在该停下时停下的身体**：模型去火山方舟开通，身体用课程版 App，行为靠技能说明书与记忆塑造，安全靠「不可逆动作必须人来做」的闸门守住。

## 你会读到什么

| 你现在的状态 | 建议路径 |
|--------------|----------|
| 只想把它用起来 | [03 安装与模型配置](concepts/03-install-and-model-config.md) → [04 记忆与提醒](concepts/04-memory-and-reminders.md) → [05 任务设计](concepts/05-task-prompt-design.md) |
| 想改成自己的助手 | [02 Agent 解剖](concepts/02-agent-anatomy-react.md) → [06 用 TRAE 读项目](concepts/06-trae-read-project.md) → [05](concepts/05-task-prompt-design.md) |
| 装上了但不动 / 报错 | [07 安全与权限](concepts/07-safety-and-permissions.md) → [03](concepts/03-install-and-model-config.md) 自检与排障 → [05](concepts/05-task-prompt-design.md) 求助模板 |
| 想带走方法论 | [五条洞察](insights.md) → [五个可迁移模式](patterns.md) |

## 信源说明

| 信源 | 类型 | 层级 | 用途 |
|------|------|------|------|
| TRAE 训练营 01 课课程文档（采集 2026-11-15，revision 1236） | 主信源 | 厂商官方培训材料（一手） | 课程目标、操作步骤、提示词、排障口径 |
| 小满源码（main 580fdf7 + 远端 camp/xiaoman） | 权威 | 第一方源码（只读核验） | 包名与版本、记忆/技能格式、提醒实现、Sentinel、CLI |
| 火山方舟官方文档（模型列表、快速入门） | 权威 | 官方文档 | Base URL、模型存在性、视觉/GUI 与工具调用能力 |
| 火山方舟产品页 | 权威 | 官方产品页 | 免费额度与协作奖励计划口径 |
| 光明网（2026-09-14） | 权威 | 媒体一手报道 | 豆包手机助手消费者版发布时间与开售节点 |
| 新浪新闻 / TRAE 官方社区 | 参考 | 公开资讯与社区 | 训练营开课信息、作业帖与「小满」名称旁证 |
| ReAct 论文（arXiv:2210.03629） | 权威 | 学术原始出处 | ReAct 范式的定义 |

## 知识结构

```
trae-agent-camp-01/
├── index.md                          ← 你在这里
├── insights.md                       五条洞察（四元组：陈述/证据/反常识/行动）
├── patterns.md                       五个可迁移模式（L1-draft）
├── concepts/
│   ├── 00-course-map.md              课程交付、设备边界、三条路径、第二课衔接
│   ├── 01-chatbot-vs-agent.md        三个案例、定义对照、二次开发边界
│   ├── 02-agent-anatomy-react.md     七件事与五部件、ReAct 循环、分链排障
│   ├── 03-install-and-model-config.md 四步法、方舟五步、双模型、自检
│   ├── 04-memory-and-reminders.md    偏好写入/覆盖/删除、提醒的真实边界
│   ├── 05-task-prompt-design.md      四要素、官方示例拆解、模板与反模式
│   ├── 06-trae-read-project.md       四个房间、三问勘察、改动落点顺序
│   ├── 07-safety-and-permissions.md  七个卡点、不可逆清单、截图出设备
│   └── 08-source-map.md              十一个模块、改动落点、源码阅读路径
├── examples/
│   ├── 01-self-check-two-models.md   两条指令自检与失败分诊
│   ├── 02-taobao-notebook-task.md    主线任务复现、结算页四项核对
│   └── 03-memory-and-reminder.md     偏好与提醒的完整验收
└── references/
    ├── course-source.md              F-001~F-095 事实登记
    ├── source-code.md                源码核验事实（S-001~S-059）
    └── verification.md               P0 核验、勘误四清单、缺口、四视角审查
```

## 分层导航

### 概念文档（9 篇）

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [课程地图](concepts/00-course-map.md) | 四项收获、设备边界（安卓与鸿蒙 5 以下）、TRAE 与学习者的分工、三条路径 |
| 01 | [Chatbot 与 Agent](concepts/01-chatbot-vs-agent.md) | 豆包跨 App 案例、真机购买录屏、需求墙；回答「为什么不从零写」 |
| 02 | [Agent 解剖](concepts/02-agent-anatomy-react.md) | 模型只会读写；记忆/技能/工具/闸门/运行时；ReAct 循环；两张模型的分工 |
| 03 | [安装与模型配置](concepts/03-install-and-model-config.md) | 四步四标志；方舟开通五步；两条自检；429 与「手机不动」分诊 |
| 04 | [记忆与提醒](concepts/04-memory-and-reminders.md) | 「记住/忘记」话术、Markdown 文件、当次优先、提醒可能晚约 1 分钟 |
| 05 | [任务设计](concepts/05-task-prompt-design.md) | 四要素、两个官方示例、可复制模板、五条反模式、求助模板 |
| 06 | [用 TRAE 读项目](concepts/06-trae-read-project.md) | app/core-memory/skills/hands 四个房间、三问勘察、只讲不改、四步闭环 |
| 07 | [安全与权限](concepts/07-safety-and-permissions.md) | 七个卡点、不可逆动作清单、Key 红线、截图出设备、最小权限建议 |
| 08 | [源码地图](concepts/08-source-map.md) | 十一个模块的职责、改动落点速查、用 TRAE 读源码的三问 |

### 实战示例（3 篇）

| 文档 | 内容 |
|------|------|
| [两条指令自检](examples/01-self-check-two-models.md) | 分别验证聊天链与操作链，附三条失败分诊 |
| [淘宝挑笔记本](examples/02-taobao-notebook-task.md) | 主线任务复现、执行中你只做两件事、结算页四项核对、停止条件 |
| [偏好与提醒](examples/03-memory-and-reminder.md) | 写入/覆盖/删除偏好，两分钟提醒与通知不弹排查 |

### 洞察与模式

| 文档 | 内容 |
|------|------|
| [五条洞察](insights.md) | 分水岭在操作链；杠杆在规则/技能/记忆；截图即成本；人类在环是边界；只讲不改是纪律 |
| [五个可迁移模式](patterns.md) | 底座二次开发、只讲不改勘察、四要素任务书、分链排障、截图成本裁剪 |

### 信源参考（3 篇）

| 文档 | 内容 |
|------|------|
| [课程事实登记](references/course-source.md) | F-001~F-095，十二类分组，课程原文与核验补充分开登记；含 2026-11-18 复读补充 |
| [源码核验事实登记](references/source-code.md) | S-001~S-059，包名与版本、目录、记忆/技能格式、Agent 循环、Sentinel、提醒、模型客户端、轨迹、CLI 与新增 MCP/Web/iOS 模块 |
| [P0 核验与对抗审查](references/verification.md) | 10 项核验（源码轮后 7✅/3⚠️）、勘误四张清单、8 项缺口、四视角 7 条意见 |

## 信任与生命周期

- **P0 核验**：初轮 10 项中 5 项通过、5 项部分通过、0 项失败；2026-11-17 源码核验后为 7 项通过、3 项部分通过、0 项失败。
- **事实分级**：课程原文 80 条、核验补充 9 条、元信息 2 条；源码核验另登记 51 条 S 事实；讲师个人实践（90 多个技能、20 多个定时任务）与费用估算标【讲师口径】。
- **status: stable 的理由**：安装、双模型、记忆、提醒、闸门等核心机制均已由源码或官方文档确认；剩余 ⚠️ 为免费额度资格、鸿蒙边界表述与费用估算，不影响教程主线。与同分组 `trae-one-click-deploy`（draft）不同，本包已有第一方源码核验。
- **stale_after**：2027-05-31。到期或触发以下任一条件时复核：① 训练营开设新一期或发布新安装包；② 方舟调整模型上下架与免费额度；③ 小满仓库发布正式版本说明或许可证。

## 已知边界

1. **版本已确认，构建号仍缺**：main 为 `0.1.0`、versionCode 1；`camp/02-skill-builder` 为 `0.2.0`、versionCode 2；课程 APK 的具体构建号未提供（G-01 部分关闭，S-004）。
2. **无附件校验信息**：未提供 APK 校验和与签名，无法验证附件完整性（G-02）。
3. **仓库已核验**：本地 clone 与 `origin`（`aduoge/xiaoman`）均存在；02 课分支 `camp/02-skill-builder` 现已公开（G-03 关闭，S-001、S-002）。
4. **费用不可复核**：几毛到一块钱为讲师估计，无账单或用量截图（G-04）。
5. **内部实现已核验**：记忆路径与 Basic Memory 格式、提醒调度（`AlarmManager.setAndAllowWhileIdle`、非精确、重启清空）均已由源码确认（G-05、G-06 关闭，S-011~S-013、S-030~S-032）。
6. **许可证已确认**：MIT（G-07 关闭，S-005）。
7. **课程手机端覆盖有限**：课程只讲安卓与鸿蒙 4.x 及以下；iPhone 与鸿蒙 5 及以上不在课程手机端范围（F-005、F-092）。源码另提供网页版与 iOS WDA 通道，属课后扩展，本包不展开。
8. **课程运营内容已过期**：课堂体验额度有效期至 2026-11-13 21:00，本包不提供其操作细节（F-090）。
9. **不做能力外推**：淘宝案例只证明「能停在确认前」，不证明可自动完成支付（见示例二的「不要外推」）。
10. **新模块不在本课范围**：MCP、网页版、iOS 与技能自建分支是 2026-11 后新增能力，第一课只用到记忆、技能、手机操作与提醒（S-053~S-059）。

## 主题关联

| 关联束 | 关系 |
|--------|------|
| [TRAE Community 生态（分组首页）](../index.md) | 上级分组；本束归入「📚 学习资源」板块（课程教程） |
| [trae-one-click-deploy](../trae-one-click-deploy/index.md) | 同为课程/公告类转化束；同样因单源密集取 `status: draft` |
| [trae-learning](../trae-learning/index.md) | 官方学习站源码解读；本束是面向学习者的课程内容，二者互补 |
| [volcengine](../../volcengine/index.md) | 方舟与云端产品的产品分析；本束只用到方舟的模型服务与计费口径 |
| [volcengine-agent](../../volcengine-agent/index.md) | AgentKit 与 VEADK 的框架视角；本束是终端侧手机 Agent 的使用视角 |
| [miaowu](../../miaowu/index.md) | 同为 AI 应用平台的实操教程，可对照「平台教程」的写法 |

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
