---
okf_version: "0.2"
type: bundle
title: "WeChatBridge（微信流）：把微信合并转发送进 AI 与 Obsidian"
description: "本地优先的 macOS 转发工具——十二个内置入口、场景提示词与 SKILL.md、100 条分批收集、Share Extension 沙盒与权限模型，含官方核验的四条时点差异与可照做流程"
tags: [wechatbridge, 微信流, share-extension, macos, obsidian, ai-agent, local-first, 博文转化, 时点差异]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-11-06T12:08:16+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-06T12:08:16+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/QdCiRiwjjc5uOvBW0nBZxw
  - id: official-readme
    url: https://github.com/freestylefly/WeChatBridge
  - id: official-usage
    url: https://github.com/freestylefly/WeChatBridge/blob/main/USAGE.zh-CN.md
  - id: official-capabilities
    url: https://github.com/freestylefly/WeChatBridge/blob/main/PRODUCT_CAPABILITIES.zh-CN.md
---

# WeChatBridge（微信流）：把微信合并转发送进 AI 与 Obsidian

> **类型**：技术教程/选型（含 examples/，操作可复现性两问皆「是」；但 examples 来自官方 README 文档化流程，**非实机验证**）
> **信源**：微信公众号「虾说AI实验室 / 虾哥」推介文（2026-09-24）→ 2026-11-06 经项目官方 GitHub README 逐项核验
> **核验结论**：18 项 P0 **14✅ / 4⚠️ / 0❌**，无源文硬错误；F-001~F-107 双份登记连续无跳号
> **状态**：`status: stable`（按 Skill §6 步骤 6.4，0❌ 不设 flagged）；四项 ⚠️ 由下方口径差异块 + 短 `stale_after` 兜住

## ⚠️ 阅读前必知的四条口径差异

本知识包由一篇 **2026-09-24 的第三方推介文**转化而来，项目在约 6 周内发生了可见演进。
以下四项**不要按源文数字引用**：

1. **入口数量**：源文写「九个原生入口」（F-018、F-041）；官方 2026-11-06 为「**十二个内置入口**」（F-067、F-068），
   `make-app.sh` 亦组装十二个 Share Extension（F-096）。本教程以十二个为主表，源文值只作时点标注。
2. **平台范围**：源文定位「完全本地的 **macOS 工具**」（F-011）；官方当前 macOS 14+ 与 Windows 均提供下载、
   iOS 开发中（F-078、F-079、F-095）。本教程的 examples 一律以 macOS 为准。
3. **「已签名公证」**：源文完成态表述（F-015）；官方 README 仅在路线图列「签名与公证流程」、
   开发者章节说明本地构建签名策略，**未逐字确认完成态**（F-100、F-103）。本教程不复述该断言。
4. **「不调微信接口」**：源文概括（F-026、F-051）；官方逐字为「不读取微信数据库，不解密、不注入、不修改微信进程」
   「聊天内容只来自微信主动导出的文件」（F-082）。引用官方立场请用官方六条，勿把推介文措辞加引号。

> 另有两项身份差异：源文作者「虾哥 / 虾说AI实验室」不是项目方，官方署名为「向明 / 苍何」（F-098）；
> 官方致谢说明项目「基于 Dukou（渡口）二次开发」（F-099），源文未提。详见 [concepts/00](concepts/00-project-facts-and-positioning.md) 与 [concepts/05](concepts/05-boundaries-selection-and-patterns.md)。

## 本文概要

[WeChatBridge（微信流）](https://github.com/freestylefly/WeChatBridge) 是一个 MIT 许可的工具（F-066）：
macOS 微信 4.1.13 起，「多选聊天记录 → 合并转发」会生成一份含 TXT、图片和视频的 ZIP（F-013、F-081）；
系统的「转发到其他应用」列表只显示带 Share Extension 的应用，多数 AI 工具不在其中（F-080），
微信流用 **Share Extension 补上这层入口**，让一次转发直接抵达 Agent、Obsidian/文件夹、剪贴板或自定义应用。

全程只接管你主动转发的归档：不读微信数据库、不解密、不注入、不修改微信进程，
Share Extension 在 macOS 沙盒中运行且没有网络权限（F-082）。三大能力是**一键转发、AI 处理、本地沉淀**（F-017）。

## 阅读路径

**先建立概念（约 15 分钟）**

1. [项目身份与双时点发布事实](concepts/00-project-facts-and-positioning.md)——许可证、能力、信源距离、哪些数字已漂移
2. [转发链路与权限模型](concepts/01-forwarding-pipeline-and-permissions.md)——ZIP → Share Extension → 目标；隐私六条；两项系统权限逐字用途
3. [十二个内置入口矩阵](concepts/02-entry-matrix.md)——逐行行为、用途分组、「九个→十二个」如何并列
4. [场景提示词、SKILL.md 与本地沉淀](concepts/03-scenes-skills-and-deposition.md)——Agent 路径与笔记路径是并列分支
5. [100 条限制与分批收集](concepts/04-batch-collection-and-records.md)——官方补齐、源文完全没写的一块
6. [边界、选型与三条可迁移模式](concepts/05-boundaries-selection-and-patterns.md)——四条前提与显式标注的编者洞察

**再动手实操（未实机验证）**

7. [安装与首次转发](examples/00-install-and-first-forward.md)——官方三步上手 + 四个检查点
8. [从源码构建与开发验证](examples/01-build-from-source.md)——命令逐字引用
9. [场景/技能配置与分批收集工作流](examples/02-scenes-skills-and-batch-workflow.md)——文字可证实的动作顺序

## 核心事实速查

| 项 | 值 | F 编号 |
|----|----|--------|
| 仓库 / 许可证 | `freestylefly/WeChatBridge` / MIT | F-007、F-066 |
| 系统要求 | macOS 14+；macOS 微信 4.1.13+ | F-052、F-053、F-078 |
| 构建前置 | Xcode 16 或兼容 Swift 6 的 Command Line Tools | F-088 |
| 归档格式 | 合并转发生成含 TXT、图片、视频的 ZIP | F-013、F-081 |
| 内置入口 | **十二个**（源文 2026-09-24 时为「九个」） | F-067、F-068 / F-018 |
| 单次转发上限 | 微信侧 100 条；用「分批收集到微信流」绕过 | F-085、F-086 |
| 隐私边界 | 不读数据库、不注入；Share Extension 沙盒且无网络权限 | F-082 |
| 权限用途 | 屏幕录制=识别聊天名；辅助功能=激活目标应用与粘贴 | F-083、F-084 |
| 失败兜底 | 目标未装/权限不足时文件仍留在剪贴板 | F-035、F-075 |
| 当前平台 | macOS + Windows 已提供下载；iOS 开发中 | F-078、F-079 |
| 项目方署名 | 向明 / 苍何；基于 Dukou（渡口）二次开发 | F-098、F-099 |

## 采用提示与已知边界

- **不是全量归档工具**：核心场景是「主动转发你选中的聊天」（F-054），每批都要人在微信里手动选取（F-086）。
  需要无人值守同步/备份的方案请另选。
- **入口数量与平台状态漂移快**：约 6 周内从九个增至十二个、从 macOS-only 扩展到 Windows。`stale_after: 2026-12-31`，
  复核优先查 [concepts/05 §6](concepts/05-boundaries-selection-and-patterns.md) 的六项清单。
- **examples 未实机验证**：源文无任何操作序列（F-039），三篇 examples 全部来自官方 README 文档化流程；
  「场景管理页」「技能中心」等 UI 只见截图，图片内文字不可补全（F-038）。以官方使用指南为准（F-101）。
- **README 无版本锁定**：核验抓取的是默认分支渲染页，未返回 commit SHA / 最后更新日期（F-105），
  故无法回溯 2026-09-24 时点的入口数（F-102）——「九个」判 ⚠️ 时点差异而非 ❌ 失实。
- **无成效数字污染**：源文与官方 README 均未提供提效倍数/工时/用户量（F-063、F-107），
  「成效数字溯源表」为空风险表；请勿从「一键」这类修辞推导效率结论。
- **「不怕封号」类承诺不存在**：官方 README 无此类表述（F-107）；源文关于读数据库「有封号和数据泄露风险」
  是作者断言、无独立出处（F-049），本教程只作为观点登记。

## 信源与可信度

- 事实清单（F-001~F-107 双份登记）：[references/article-source.md](references/article-source.md)
- P0 核验报告 + 勘误四张清单：[references/verification.md](references/verification.md)
- 信源距离：第三方公众号推介 → 项目一手 README 交叉核验；四项 ⚠️ 均为时点/口径漂移，已并列呈现
- 状态决策与机械门禁记录：[log.md](log.md)

## 主题关联

- [WeChat Intelligence Hub](../wechat-intelligence-hub/index.md)：同为「微信聊天内容 → 本地知识库」主题，
  但走只读 Reader + 日报/情报路线；本束走「合并转发 + Share Extension」的投递路线，二者输入通道不同。
- [wigolo](../wigolo/index.md)：同为本地优先的 Agent 情报层，且同属「微信博文经 OKF v0.2 七阶段转化」先例束；
  wigolo 处理 Web 公开情报，本束处理用户主动导出的私聊/群聊归档。
- [Agent Reach](../agent-reach/index.md)：同属「给 Agent 补一层能力入口」的产品族，可对照「不抓取只选型/路由」
  与本束「不读库只接管导出物」的边界设计。
- [Knocket](../knocket/index.md)：同分组内微信公众号博文经官方核验转化的先例，可对照事实登记与勘误清单格式。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
