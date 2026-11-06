---
okf_version: "0.2"
type: bundle
title: "WeChatBridge iOS 版与「别聊需求，定验收」"
description: "从 2026-10-27 微信博文提炼 iOS 中转站能力与验收驱动 Agent 编码方法论——两段提示词、S/R/T 编号控制面、出口闸门与勘误四张清单；含官方仓库一手件核验出的 4 项核心口径冲突，status: flagged"
tags: [wechatbridge, 微信流, ios, agent-coding, acceptance-driven, 验收闸门, 博文转化, flagged, 时点差异]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-11-06T12:20:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-06T12:20:00+08:00"
status: flagged
stale_after: "2027-01-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/94FP4Cl7JIQbxU5-i3B6og
  - id: official-repo
    url: https://github.com/freestylefly/WeChatBridge
  - id: official-readme
    url: https://github.com/freestylefly/WeChatBridge/blob/main/README.md
  - id: official-dev-spec
    url: https://github.com/freestylefly/WeChatBridge/blob/main/docs/design/ios-dev-spec.zh-CN.md
  - id: official-schedule
    url: https://github.com/freestylefly/WeChatBridge/blob/main/docs/design/ios-schedule.zh-CN.md
  - id: official-acceptance
    url: https://github.com/freestylefly/WeChatBridge/blob/main/docs/design/ios-验收记录.zh-CN.md
---

# WeChatBridge iOS 版与「别聊需求，定验收」

> **类型**：技术教程 / 方法论（含 `examples/`，操作可复现性两问皆「是」；但示例均为**非官方模板、本知识包未实机验证**）
> **信源**：微信公众号「苍何」产品方自述文（2026-10-27）→ 2026-11-06 经项目官方 GitHub 一手件逐项核验
> **核验结论**：24 项 P0/P1 **12✅ / 8⚠️ / 4❌**；F-001~F-084 双份登记连续无跳号
> **状态**：⚠️ `status: flagged` —— 4 项 ❌ 中 **V-21、V-22 为博文核心声明**，按 `blog-article-to-okf-wiki` §6 步骤 6.4 强制标记

## ⚠️ 阅读前必知：四项不要照抄的源文口径

本知识包由一篇 **产品方作者自述文**（F-008）转化而来。以下四项已被官方仓库一手件证伪或收窄，
**正文一律采用「博文口径 / 官方口径 / 结论」并列写法**：

1. **iOS「开发完成 / 正在提审、还没上架」**（F-009/F-010）→ 官方 README 写「iOS 版**正在开发中**」、
   路线图 `- [ ] iOS 版` 未勾选、验收记录 R3–R6「**待真机**」、§10 交付定义未全打勾（F-065/F-066/F-077/F-080）。
   **❌ V-21**：截至核验时点无官方证据支持「已提审」，本束按「开发中 / 内部体验阶段」处理。
2. **「灵动岛小入口 / 复制提示词」**（F-019）→ 官方 dev-spec §12「不在 v1」逐字列有「灵动岛」（F-077），
   官方仅记录通知横幅「快速投递」且 R7「模拟器通过，待真机」（F-080）。**❌ V-22**：v1 无此入口。
3. **「一次发完，哪家都能吃」**（F-022）→ 官方 R2「部分通过」：豆包 / 千问只发聊天记录 TXT、
   「视频和压缩包仍发不了」（F-080）。**❌ V-23**：只能写「部分目标默认格式为图文合一 PDF」。
4. **10-27 称「国产开源模型 / 开源第一梯队」**（F-037/F-040）→ 完整权重 11-02 上传、**11-04 才正式公开**（F-081）。
   **❌ V-24**：博文时点应写「开源权重待发布」。

> **厂商 / 作者自述数据提示**：源文含成效与热度数字（1.7 k star、6 个多小时、18 个工作日、55 分、
> 「有点贵」等，F-006/F-039/F-050/F-040/F-061）。按信源距离规则，**这些数字默认 P0 必核验**，
> 结论见 [verification.md](references/verification.md) 的「成效数字溯源表」；未标 ✅ 的一律不得当作可复现结论引用。

## 本文概要

[WeChatBridge（微信流）](https://github.com/freestylefly/WeChatBridge) 是 MIT 许可的工具（F-062/F-070），
主线为把微信「合并转发」的聊天归档转给各家 Agent 或沉淀进 Obsidian（F-007）。
本束聚焦 **2026-10-27 博文中的 iOS 版发布线**，以及作者反复强调的那套做法：
「**先让它写计划，再让它自己跑**」（F-043，作者观点）与「**别跟它聊需求，跟它定验收**」（F-059，作者观点）。

真正可迁移的不是某个模型的表现，而是**把「什么叫做完」写成可验收的控制面**：
两段提示词（F-046/F-047）→ `docs/design/` 下两份编号化文档（F-071/F-072/F-078）→
S1–S11 模拟器验收 / R1–R7 真机验收 / T0.1–T9.2 任务清单 / §10 交付定义（F-077）→
每个任务单独提交并固定 7 行汇报（F-073/F-078）→ 验收记录留痕与复跑（F-079/F-080）。
官方记录把「不能验证的就写『待真机』，不许标通过」列为硬规矩（F-073），这也是本束处理证据状态的原则。

> **本束不做模型评测**。所有对 Kimi K3.1 Pro 的能力评价均为作者观点或媒体转述（F-037/F-038/F-040/F-041/F-060/F-082/F-084），
> 本束不据此对模型能力下结论；V-24 仅处理「开源」措辞的时点问题。

## 阅读路径

**先建立概念与证据边界（建议先读 00）**

1. [00 · 身份、时点与信源距离](concepts/00-identity-source-distance-and-status.md)——`flagged` 读前须知、四层信源距离、动态数字双时点
2. [01 · iOS 中转站能力](concepts/01-ios-relay-capabilities.md)——收 / 存 / 投 / Obsidian 逐项对照博文口径与官方口径，含 2 项核心 ❌
3. [02 · 别聊需求，定验收](concepts/02-acceptance-driven-agent-coding.md)——两段提示词 → 两份文档 → 按 T 编号执行的方法论链
4. [03 · 验收控制面](concepts/03-spec-schedule-and-acceptance-gates.md)——S/R/T 编号、交付定义、出口闸门、工作规则、「不在 v1」
5. [04 · 验收记录与勘误落实](concepts/04-verification-record-and-errata-implementation.md)——9 项自修 bug、两次复跑数字、4 项 ❌ 的正文落地
6. [05 · 可迁移模式与采用边界](concepts/05-transferable-patterns-and-boundaries.md)——洞察四元组、三个可搬走做法、复核清单

**再按证据状态动手（未实机验证）**

7. [两段提示词复现](examples/00-reproduce-the-two-prompts.md)
8. [自设计验收闸门模板](examples/01-design-your-own-acceptance-gates.md)
9. [iOS 五步使用流程（含证据状态标注）](examples/02-ios-usage-walkthrough.md)

**查出处**：[事实清单 F-001~F-084](references/article-source.md) · [P0 核验报告与勘误四张清单](references/verification.md)

## 核心事实速查

| 项 | 值 | F 编号 |
|----|----|--------|
| 博文 / 作者 / 时间 | 《开源微信流 APP…》；「苍何」原创；2026-10-27 16:28 湖北；第 613 篇原创 | F-001、F-002 |
| 仓库 / 许可 / 语言 | `freestylefly/WeChatBridge`；MIT；Swift；默认分支 `main`；创建于 2026-09-21 | F-062、F-063、F-070 |
| 官方平台状态 | macOS 14+ 与 Windows 提供下载；`ios/` 为「开发中」、路线图 `[ ] iOS 版` 未勾选 | F-065、F-066、F-067 |
| 星标（双时点） | 博文 2026-10-27「1.7 k」；GitHub API 2026-11-06 为 **2024** | F-006 / F-063 |
| iOS 设计文档 | `docs/design/` 下 6 份；dev-spec 与 schedule 均标注 2026-10-23 | F-071、F-072、F-078 |
| 编号体系 | S1–S11（模拟器）/ R1–R7（真机）/ T0.1–T9.2（21 任务）/ §10 交付定义 9 条 / §12「不在 v1」14 项 | F-077 |
| 档期 | 「开发和验收共 **18 个工作日**，另加 2 天缓冲」；计划交付 2026-11-18 / 最晚 11-20；M0–M6 | F-050、F-078 |
| 回归基线 | Mac `swift test` 186 个测试（含 1 跳过）0 失败；iOS 单测 28 → 40，两次复跑退出码 0 | F-053、F-073、F-079 |
| 自修问题 | 官方验收记录 9 项；博文列举 5 项，均在其中 | F-056、F-079 |
| 真机状态 | R1 / R2「部分通过」；R3–R6「待真机」；R7「模拟器通过，待真机」 | F-080 |
| 分批上限 | 微信一次最多转发 100 条；用「分批收集到微信流」分几批选 | F-024、F-069 |
| 隐私边界 | 官方六条：内容只来自微信主动导出的文件、不读库 / 不解密 / 不注入 / 不改进程、本机保存等 | F-068 |
| 6 小时 | 作者自述净运行时长，**无独立出处**，官方记录跨 10-23 / 10-24 两日 | F-039、F-055、F-079 |
| 模型 / 评分 / 补偿 | K3.1 Pro 2026-10-24 发布、权重 11-04 公开；AA 55 分；会员补偿月度总额 25%（均为媒体转述层级） | F-081、F-082、F-083 |

## 采用提示与已知边界

- **不是安装教程**：官方只提供 macOS 14+ 与 Windows 包（F-065），iOS 仍在开发中（V-21）。
  `examples/` 不含安装、签名、TestFlight 或 IPA 步骤；真机 App Group 还需付费 Apple Developer Program 团队（F-074）。
- **三类证据状态贯穿全文**：官方印证 ✅ / 仅博文单源或未真机 ⚠️ / 官方证伪 ❌。
  「待真机」是一等状态，不允许推测填补（F-073/F-080）。
- **8 项 ⚠️ 不得忽略**：星标时点、6 小时口径、通知长按换目标未真机、PDF 仅部分目标默认格式、
  「客户复盘」六项仅博文单源、Kimi 规格仅媒体转述、3D 能力作者未实测、「有点贵」与第三方「便宜约 80%」相反口径
  （V-13~V-20，见 [verification.md](references/verification.md)）。
- **6 小时 ≠ 18 工作日的 1/N**：前者是作者自述净运行时长，后者是含真机验收与 2 天缓冲的全职档期，
  统计口径不同，**禁止相除得「提效倍数」**（F-039/F-055/F-050/F-078）。
- **动态数字均带时点**：星标 1.7 k / 2024 并列，互不覆盖；模型「开源」措辞以权重公开日为准（V-24）。
- **作者观点不升级为事实**：F-037/F-038/F-040/F-043/F-058/F-059/F-060/F-061 为作者观点或转述，
  引用时保留标注；F-083 为「官方公告经媒体转述」，不得写成已取得官方原文。
- **tree API 曾截断**：`ios/` 条目只登记「约百余条 / 可见条目」，不得写成精确值（F-071）。
- **复核安排**：`stale_after: 2027-01-31`。到期前复核 ① iOS 上架与路线图状态 ② 灵动岛 / Live Activity 是否入版
  ③ R3–R6 真机结论是否补齐、R7 是否真机通过 ④ 权重开放后的「开源」措辞。清单详见 [concepts/05](concepts/05-transferable-patterns-and-boundaries.md)。

## 信源与可信度

- 事实清单（F-001~F-084 双份登记）：[references/article-source.md](references/article-source.md)
- P0 核验报告 + 勘误四张清单：[references/verification.md](references/verification.md)
- 信源距离：**官方仓库一手件**（README / dev-spec / schedule / 验收记录 / GitHub API）>
  官方公告经媒体转述 > 第三方评测 / 实测 > 产品方自述 / 作者观点。
- 状态决策与机械门禁记录：[log.md](log.md)

## 主题关联

- [WeChatBridge（微信流）](../wechatbridge/index.md)：**同一项目、不同博文、不同主线**。
  该束处理 2026-09-24 的 Mac/Windows 产品推介文（十二个入口、Share Extension、分批收集与安装构建）；
  本束处理 2026-10-27 的 iOS 版发布线与「定验收」Agent 编码方法论。两束互链但互不覆盖。
- [WeChat Intelligence Hub](../wechat-intelligence-hub/index.md)：同为「微信聊天内容 → 本地知识库」主题，
  该束走只读 Reader + 日报情报路线，本束走「合并转发 → 中转站 → 投递」路线。
- [Craft Anything](../craft-anything/index.md)：同分组内「自宣发布资讯经 P0 核验」先例，
  可对照勘误四张清单与 `flagged` / `stable` 状态判定的写法。
- [Agent Reach](../agent-reach/index.md)：同属「给 Agent 补一层能力入口」的产品族，
  可对照其边界设计与本束「分享扩展只收和存、投递须用户点分享面板」（F-033/F-076）的约束。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
