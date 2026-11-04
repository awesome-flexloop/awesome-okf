---
type: Example
title: 最小可行路径：用官方插件让它先会说话
description: 只走官方插件路线的最短步骤、验收点与三类常见故障的排查顺序。
sources:
  - { id: facts, resource: ../references/facts.md }
  - { id: qq-official, resource: "https://ima.qq.com/wiki/" }
  - { id: dsh-plugin-index, resource: "https://dshpluginhub.ai/zh/plugins/tencent-connect-dsh-qqbot" }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T11:05:00+08:00" }
status: draft
stale_after: 2026-12-04
---

# 最小可行路径：用官方插件让它先会说话

目标：在 QQ 里和一个人格稳定的机器人聊上十句，全程只用有官方文档兜底的通道。协议端路线、微信、飞书、B 站、抖音都不在本练习范围内。

## 准备清单

| 项 | 为什么需要 | 备注 |
|---|---|---|
| DSH 桌面客户端 | 宿主，插件与 profile 都挂在它下面 | 下载入口见原文 F-006；本包未逐页核验安装界面 |
| 可用的模型额度 | token 从自建 API key 计费[F-036](../references/facts.md) | 原文称未使用过的账号需先充值[F-008](../references/facts.md) |
| 手机 QQ | 扫码绑定用[F-010](../references/facts.md) | 绑定成功后凭据自动保存[F-016](../references/facts.md) |
| 一段人设文本 | 决定它像不像一个人 | 用[人设骨架](persona-prompt-skeleton.md)填，别现场编 |

## 步骤

1. **先确认宿主能对话**。打开 DSH，随便问一句，能正常回再往下走。宿主不通时排查插件只是浪费时间。
2. **装插件**。桌面路径：插件 → 添加插件 → 输入 `@tencent-connect/dsh-qqbot` → 安装并启用 → 重启应用，侧边栏出现 QQ 机器人。[F-009](../references/facts.md) CLI 路径：`npx @deepseek-ai/dsh plugin --profile qqbot add @tencent-connect/dsh-qqbot`，再 `npx @deepseek-ai/dsh --profile qqbot` 启动。[F-016](../references/facts.md)
3. **扫码绑定**。左下角头像 → 设置 → QQ 机器人 → 手机 QQ 扫码。[F-010](../references/facts.md) 绑定后凭据落盘，之后不必重复扫码。
4. **先写人设，再聊天**。把填好的骨架贴进会话，要求它按此扮演。**不要**边聊边补人设——前几句会变成风格样本，后面很难纠正。
5. **做三句校准**。发同一句「在吗」三次，观察是否稳定：是否一句一条、是否不用句号、有没有出现「有什么可以帮你」。三项都过，人设才算立住。[F-033](../references/facts.md)
6. **补两条群规则**。如果打算拉进群，先开「@ 才响应」，避免刷屏。[F-015](../references/facts.md)

## 验收

| 检查点 | 通过标准 | 对应事实 |
|---|---|---|
| 宿主 | 能对话，插件出现在侧边栏 | F-009 |
| 通道 | 手机 QQ 能收到机器人回复 | F-010、F-013 |
| 会话隔离 | 私聊与群聊各自记住各自的内容 | F-013 |
| 人格 | 三次「在吗」风格一致，无客服腔 | F-033 |
| 身份识别 | 换个号自称主人，套不出任何内部信息 | F-032 |
| 模型切换 | 换模型后上下文仍在 | F-014 |

## 故障排查顺序

按「宿主 → 凭据 → 插件 → 人设」四级走，不要跳级：

| 症状 | 先查什么 | 依据 |
|---|---|---|
| 侧边栏没有 QQ 机器人 | 插件是否真的启用、是否重启过 | F-009 |
| 扫码后仍不回消息 | 凭据是否保存成功；换 CLI 启动看是否进入扫码引导 | F-016 |
| 机器人在群里刷屏 | 是否开了「@ 才响应」 | F-015 |
| 回复正确但完全不像 | 人设是否进了系统提示，而不是只发在聊天里 | F-031、F-033 |
| 私聊记得、群里装失忆 | 这是默认行为，不是故障 | F-013 |

最后一行是新手最容易误判的：官方设计就是「每个单聊、每个群聊独立会话」。[F-013](../references/facts.md) 想让它们共享，需要额外的记忆组件，见[四通道拓扑](../concepts/channel-topology.md)。

## 做完之后

- 想让它有分寸：读[安全边界](../concepts/safety-boundaries.md)，把三条禁令落成配置。
- 想接第二个通道：先确认记忆方案，再动手，否则会得到三个互不相识的机器人。
- 想让它出去发内容：先做[彩排闸门](../concepts/social-ops-loop.md)，别直接从「能聊天」跳到「能直播」。

> 本练习是阅读后的原创步骤整理，不是原文复述。原文的安装顺序与界面描述取自单篇公众号文章，[F-009](../references/facts.md) 与官方三步一致[F-010](../references/facts.md)，但具体界面文案随版本变化，以现场为准。
