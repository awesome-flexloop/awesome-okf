---
type: Concept
title: "04 · 验收记录、自修 bug 与勘误落实"
description: "官方验收记录 S/R 结果、9 项自修问题、两次复跑数字，以及 4 项 ❌ 在本束正文中的逐项落实"
tags: [acceptance-record, bugfix, regression, 勘误, flagged]
sources:
  - id: official-acceptance
    url: "https://raw.githubusercontent.com/freestylefly/WeChatBridge/main/docs/design/ios-验收记录.zh-CN.md"
  - id: official-dev-spec
    url: "https://raw.githubusercontent.com/freestylefly/WeChatBridge/main/docs/design/ios-dev-spec.zh-CN.md"
  - id: blog
    url: "https://mp.weixin.qq.com/s/94FP4Cl7JIQbxU5-i3B6og"
---

# 04 · 验收记录、自修 bug 与勘误落实

## 1. 官方验收记录的全貌

`docs/design/ios-验收记录.zh-CN.md` 记录 App `0.1.0 (1)`、iPhone 17 Simulator / iOS 26.5，模拟器上没有微信，用「文件」App 代替分享（F-079）。

| 类别 | 结果 | 出处 |
|---|---|---|
| 模拟器 S1–S11 | 全部「通过」；其中 S4、S7、S8、S9 为「通过（修复后）」 | F-079 |
| 真机 R1 | 部分通过（单人样本通过，多人群样本未测） | F-080 |
| 真机 R2 | 部分通过（豆包/千问附件行为反复调整） | F-080 |
| 真机 R3–R6 | **待真机** | F-080 |
| 真机 R7 | 模拟器通过、待真机；长按无法在模拟器触发，仅单测覆盖 | F-080 |
| 环境 | iPhone 16 Pro / iOS 26.5，免费 Personal Team 签名，7 天过期需重装 | F-080 |

两次 `verify.sh` 复跑（F-079）：

| 日期 | Mac `swift test` | iOS 单元测试 | 退出码 |
|---|---|---|---|
| 2026-10-23 | 186 个测试（1 跳过）0 失败 | 28 个 0 失败 | 0 |
| 2026-10-24（加入快速投递后） | 186 个测试（1 跳过）0 失败 | 40 个 0 失败 | 0 |

> **口径提示**：博文「6 个多小时 / 一个下午加一个晚上」（F-039、F-055）与官方记录跨 10-23、10-24 两日并不相容为一个自然日；本束按 V-14 标「作者自述、未独立核验」，且不用于任何提效倍数计算。

## 2. 博文 5 个 bug → 官方 9 项问题

博文列举 Agent 自验收时揪出并自修的 5 个问题（F-056）：空文件被存进中转站；点卡片进不去详情只会高亮；发完按钮还显示「继续发送第 2/1 组」；编辑模式下底部「合并投递」被标签栏挡住；刚点完的目标图标当场跳到别的位置。

官方「验收中发现并修复的问题」表共 **9 项**（F-079/F-080），博文 5 项全部命中，另多出 4 项（引导页按钮压住页码点、场景开关打不开、设置页输入框无标签、真机单条消息导出「解析失败」）。相关提交：`cfbced3`、`0d48b3f`、`767fedd`、`34e2d5a` 等。

**结论**：这是核验中「✅ 且信息量增加」的一类——博文不是错的，是省略了 4 项。正文应采用官方的 9 项口径，并把「每个问题记进验收记录：现象 / 原因 / 哪次提交修的」（F-057）作为该方法论的可验证证据。

## 3. 4 项 ❌ 在正文中的落实（对照检查）

| 核验项 | 博文错误口径 | 本束呈现的正确口径 | 落地位置 |
|---|---|---|---|
| V-21 | iOS「开发完成」「正在提审、还没上架」（F-009/F-010） | 截至 2026-11-06 官方为「iOS 版正在开发中」、路线图 `[ ] iOS 版`、R3–R6 待真机、§10 未全打勾（F-065/F-066/F-077/F-080） | [00 §5](00-identity-source-distance-and-status.md)、[01 §2 第 14 行](01-ios-relay-capabilities.md)、[examples/02](../examples/02-ios-usage-walkthrough.md) |
| V-22 | 灵动岛留小入口、可复制提示词（F-019） | §12「不在 v1」明列灵动岛；官方仅记录通知横幅「快速投递」，R7 待真机（F-077/F-080） | 00 §5、01 §2 第 6 行、examples/02 |
| V-23 | 「一次发完，哪家都能吃」（F-022） | 「图文合一 PDF」只是部分目标的默认格式；豆包/千问只发 TXT、视频与压缩包仍发不了（F-080） | 01 §2 第 9 行、01 §3 |
| V-24 | 10-27 称「国产开源模型 / 开源第一梯队」（F-037/F-040） | 10-24 发布为预览、承诺开源；完整权重 11-02 上传 / **11-04 正式公开**（F-081） | 00 §3、[verification.md ①](../references/verification.md) |

8 项 ⚠️ 全部在 [00 §3/§5](00-identity-source-distance-and-status.md)、[01 §2/§3](01-ios-relay-capabilities.md)、[02 §4](02-acceptance-driven-agent-coding.md) 与 [verification.md](../references/verification.md) 中有对应表述，未出现「只登记不落实」。

## 4. 「待真机」是一条纪律，不是一个缺陷

官方 §0 规则 5 与博文 F-053 一致：「真机步骤无法自动完成时…标『待真机』，不要标通过」（F-073）。验收记录里 R3–R6 长期挂「待真机」，R7 明说长按只有单元测试覆盖（F-080）——这不是交付失败，而是**证据状态被诚实登记**。作者把这一点列为「体贴」的例子之一（F-060，作者观点）。

对本知识包的启示（洞察，非官方结论）：把「未验证」写成一等状态，能让下游读者区分「已证实」「仅在模拟器证实」「尚未证实」三种证据强度。本束对 iOS 功能全部采用三档标注，正是沿用这条纪律。

## 5. 复跑数字与回归基线

`swift test` 186 个测试（含 1 个跳过）0 失败是 Mac 侧回归基线，dev-spec §0 规定「任何改到 `macos/` 的提交，提交前都必须跑」（F-073）；§10 交付定义进一步要求「测试数 ≥ 186」（F-077）。验收记录两次复跑均满足（F-079）。

README 另给出可直接照做的开发者命令（F-070）：`swift test`、`swift Scripts/check-localizations.swift`、`Scripts/check-release-config.sh`、`Scripts/dev-preview.sh`、`CONFIG=release Scripts/make-app.sh`、`Scripts/install-dev-build.sh`、Windows 侧 `dotnet test windows/WeChatBridge.Windows.sln -c Release`。

> **本束未实机验证任何命令**。以上仅为官方 README 的路径说明，读者须自行核对 Xcode/Swift 版本与平台要求（dev-spec §1：Xcode 26.6、iOS 26.5 平台、XcodeGen 2.x、真机需付费团队签名，F-074）。
