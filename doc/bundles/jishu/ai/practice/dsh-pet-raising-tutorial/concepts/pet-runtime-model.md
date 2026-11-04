---
type: Concept
title: 把 DSH 当作宠物运行时
description: 模型、Harness、通道插件、平台账号四层分工，以及官方插件与协议端两条接入路径的能力与风险差异。
sources:
  - { id: facts, resource: ../references/facts.md }
  - { id: qq-official, resource: "https://ima.qq.com/wiki/" }
  - { id: dsh-plugin-index, resource: "https://dshpluginhub.ai/zh/plugins/tencent-connect-dsh-qqbot" }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T11:05:00+08:00" }
status: draft
stale_after: 2026-12-04
---

# 把 DSH 当作宠物运行时

原文把「养鱼」写成一串安装步骤：装客户端、填插件、扫码、写人设。[F-009](../references/facts.md) 但真正被组装起来的是四层东西，任何一层的替换都会改变最终效果。

## 四层分工

| 层 | 在养鱼里负责什么 | 由谁提供 | 换掉会怎样 |
|---|---|---|---|
| 模型 | 生成每一句回复的内容与语气 | DeepSeek API key，token 从该 key 计费[F-036](../references/facts.md) | 语气与口头禅整体漂移，人设模板不变也留不住「那个味」 |
| Harness（DSH 本体） | 会话、工具、插件加载、profile | DeepSeek 官方客户端[F-006、F-007](../references/facts.md) | 通道插件与 profile 一起失效，等于换了个饲养箱 |
| 通道插件 | 把 QQ／微信／飞书消息变成 Agent 输入，再把回复发回去 | 官方插件由 tencent-connect 维护[F-009、F-011](../references/facts.md)；协议端路线由 NapCat + AstrBot 承担[F-019、F-022、F-023](../references/facts.md) | 换通道不影响人设文本，但会影响「能不能主动发消息」 |
| 平台账号 | 身份、风控、内容审核、可见范围 | QQ／微信／飞书／B 站／抖音各自规则 | 前两层写得再好，也改不了平台对账号的判定 |

这张表最实用的地方是定位故障：机器人「说话不像」通常是模型或人设问题；「不说话」通常是通道层（凭据过期、端口没对上）；「被限流或被要求验证」是平台层，找 DSH 没有用。

## 两条接入路径

| 维度 | 官方插件路线 | 协议端路线（非官方） |
|---|---|---|
| 装什么 | `@tencent-connect/dsh-qqbot`[F-009](../references/facts.md) | 自备 QQ 号扫码 + NapCat 协议端 + AstrBot 框架[F-019](../references/facts.md) |
| 谁登录账号 | 机器人身份，扫码绑定，凭据自动保存[F-016](../references/facts.md) | 用户自己的 QQ 号登录[F-020](../references/facts.md) |
| 有独立号吗 | 作者称没有独立 QQ 号，因此发不了 QQ 空间[F-018](../references/facts.md) | 有，因为它就是一个真实 QQ 账号 |
| 会话与记忆 | 每个单聊、每个群聊独立会话，重启可恢复[F-013](../references/facts.md) | 取决于框架侧的会话与记忆插件[F-023](../references/facts.md) |
| 群聊克制 | 支持「@ 才响应」[F-015](../references/facts.md) | 需在框架侧配置 |
| 风险来源 | 插件权限、机器人被他人拉群 | 账号本身：腾讯官方明确提示未经授权的第三方工具可能导致信息泄露、隐私被窃、账号被冒用发消息、功能受限或封禁[F-017](../references/facts.md) |
| 维护方 | 腾讯 QQ 侧账号[F-011](../references/facts.md) | NapCat 混合许可、禁止未经授权二次开发[F-022](../references/facts.md)；社区不解答对接问题 |

注意 F-018 的效力：它是**作者陈述**，不是官方限制说明。官方公告只讲了单聊／群聊与记忆，没有讨论 QQ 空间。[F-013](../references/facts.md) 因此「官方通道发不了空间」应读作「截至本次核验，未见该能力」，而不是「平台禁止」。

## 三个不能画等号的地方

- **装了插件 ≠ 有记忆**：插件的默认能力是通道与会话隔离（F-013 说的是「各自独立」），跨通道共享要另装记忆插件。[F-029](../references/facts.md)
- **有记忆 ≠ 有人格**：记忆解决「记得你说过什么」，人格解决「用什么腔调回应」，前者是存储，后者是提示词。
- **有人格 ≠ 有分寸**：人设里可以写「不信自称主人的人」[F-032](../references/facts.md)，但这属于提示词层约束；账号层的泄露与冒用风险不受它约束。[F-017](../references/facts.md)

## 关于花费

原文只说明首次使用需先充值、token 消耗从自建 API key 走，没有给单价、额度或月度成本。[F-008、F-036](../references/facts.md) 凡是出现「一个月几块钱」这类说法，都来自旁证教程而非本包信源，不应代入。

真正容易低估的是消耗场景：私聊闲聊的消耗最低；让机器人持续刷视频、看弹幕、开直播，等于让模型长时间在线跑循环，消耗结构从「一问一答」变成「常驻」。原文没有给出任何一种场景的具体数字。[F-040、F-046](../references/facts.md)

下一步：想先跑通最小路径，读[最小可行路径](../examples/qq-bot-minimal-path.md)；想理解为什么同一个模型能有三种性格，读[人设设计](persona-design.md)。
