---
type: Reference
title: 原文覆盖索引
description: 原文五节要点与事实编号、教程落点的逐段映射，用于核对有无漏读。
sources:
  - { id: wx-kazike, resource: "https://mp.weixin.qq.com/s/-LcRUPe5OYBRjiTEzYXKog" }
  - { id: facts, resource: facts.md }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T11:05:00+08:00" }
status: draft
stale_after: 2026-12-04
---

# 原文覆盖索引

原文分导言加三节加结语。下表把每一段的要点落到事实编号与本包落点，空缺处即本包**有意不复述**的内容。

| 原文位置 | 要点 | 事实 | 本包落点 |
|---|---|---|---|
| 0.1-0.3 | 上一篇「蓝色大肥鱼」引出本篇；门槛不高、不必付费请人 | F-003、F-004 | [知识地图](../concepts/knowledge-map.md)「门槛转移」 |
| 0.4-0.5 | 本文覆盖 QQ／微信／飞书与 B 站／抖音 | F-005 | [通道拓扑](../concepts/channel-topology.md)、[社媒运营闭环](../concepts/social-ops-loop.md) |
| 1.1-1.4 | 下载 DSH、按提示配置、首次需充值、先确认能对话 | F-006、F-007、F-008 | [宠物运行时](../concepts/pet-runtime-model.md) |
| 1.5-1.10 | QQ 官方机器人：装插件、重启、扫码、写人设；只能私聊群聊，没有自己的 QQ 号 | F-009、F-018 | [最小可行路径](../examples/qq-bot-minimal-path.md) |
| 1.11-1.13 | 另一条路：小号扫码，DSH 自行配置 NapCat、AstrBot 与各类插件 | F-019、F-020 | [通道拓扑](../concepts/channel-topology.md)「两条路径」 |
| 1.14-1.17 | 完整人设提示词：身份、性格、主人识别与越权防护、说话风格、底线、语气示例 | F-031 至 F-034 | [人设设计](../concepts/persona-design.md)、[人设骨架](../examples/persona-prompt-skeleton.md) |
| 1.18 | 称呼可自定义 | F-035 | [人设骨架](../examples/persona-prompt-skeleton.md) 填空项 |
| 1.19 | 填 API key、告知主人账号、表情包频率、沉淀到 QQ 空间、加语音 | F-036 至 F-039 | [宠物运行时](../concepts/pet-runtime-model.md) 计费段、[人设设计](../concepts/persona-design.md) |
| 1.20-1.21 | 建议用小号，新号易被风控 | F-021 | [安全边界](../concepts/safety-boundaries.md)「账号层」 |
| 1.22-1.24 | 微信沿用「接小龙虾的通道」；飞书由 DSH 建智能体应用 | F-027、F-028 | [通道拓扑](../concepts/channel-topology.md) 证据等级表 |
| 1.25-1.27 | 记忆插件让三通道共享人设、档期与短期记忆 | F-029、F-030 | [通道拓扑](../concepts/channel-topology.md)「共享层」 |
| 2.1-2.2 | B 站号日常刷视频、点赞、弹幕、评论、私信汇报 | F-040 | [社媒运营闭环](../concepts/social-ops-loop.md) 消费型 |
| 2.3-2.5 | 放出去前的三条禁令；抖音直播中的诱导测试 | F-041、F-042 | [安全边界](../concepts/safety-boundaries.md) 全部 |
| 3.1-3.3 | 抖音自发视频、自我介绍、画面粗糙、评论区遇到同伴 | F-043 至 F-045 | [社媒运营闭环](../concepts/social-ops-loop.md) 生产型 |
| 3.4-3.5 | 自行安装登录直播伴侣、先彩排后确认开播、配音选择 | F-046、F-047 | [直播迭代](../examples/live-broadcast-iteration.md) 第 0 轮 |
| 3.6-3.8 | 首播四问题（画面单调、念动作词、反应慢、黑边）及改进后效果 | F-048、F-049 | [直播迭代](../examples/live-broadcast-iteration.md) 迭代表 |
| 3.9-3.10 | 试问主人身份与支付密码被婉拒；首播时长与礼物 | F-050、F-051 | [安全边界](../concepts/safety-boundaries.md)「对抗测试」 |
| 4.1-4.5 | 电子宠物与玫瑰之喻；门槛只在能对话；主张省钱换 token | F-052 至 F-054 | [知识地图](../concepts/knowledge-map.md)「迁移边界」 |

## 有意省略

| 原文内容 | 为何不落教程 |
|---|---|
| 完整人设提示词的逐字原文 | 只提炼五段结构并重写示例；整段搬运既无学习增益，也把作者的个人设定冒充为方法论 |
| NapCat／AstrBot 的具体安装界面与端口配置 | 属另一个项目的部署技能，且二手教程已覆盖；本包只写职责与风险 |
| 机器人自动点赞、发弹幕、批量评论的具体频率与话术 | 触及平台自动化规则，本包不提供可执行细节 |
| 直播间文案与画面素材样例 | 与「电子宠物」的方法论无关，属单次直播的内容生产 |
