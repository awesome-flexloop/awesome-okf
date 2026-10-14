---
type: Reference
title: openKylin AISubsystem SIG（SIG 120）社区信源
description: openKylin 社区 AISubsystem 特别兴趣小组官方页面信源——使命、邮件列表、仓库生态与采集边界，作为 Kylin Agent Runtime 的社区归属背景。
tags: [openkylin, sig, aisubsystem, community]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: sig-page
    resource: https://www.openkylin.top/sig/sig_detail.html?sig_id=120
    title: openKylin SIG 120 - AISubsystem
---

# openKylin AISubsystem SIG（SIG 120）社区信源

## 信源元数据

| 项 | 值 |
|---|---|
| 页面 | https://www.openkylin.top/sig/sig_detail.html?sig_id=120 |
| SIG 名称 | AISubsystem（AI 子系统特别兴趣小组） |
| 邮件列表 | aisubsystem@lists.openkylin.top（订阅页：https://mailweb.openkylin.top/postorius/lists/aisubsystem.lists.openkylin.top） |
| 抓取日期 | 2026-10-14 |
| 页面形态 | 动态分页页面（仓库清单共 9 页，分页由 JavaScript 加载；静态抓取只能取第 1 页） |

## SIG 使命（页面原文要点）

AISubsystem SIG 小组致力于 openKylin AI 子系统的规划、维护和升级工作，具体三条：

1. 负责 AI 子系统相关软件包的规划、维护和升级；
2. 管理本地和云端大模型，屏蔽各个大模型和框架的差异，提供 AI 基础能力和特定场景相关的 SDK 接口；
3. 打造麒麟 OS Agent。

本束研究对象 `agent-runtime`（包名 `kylin-agent-runtime`，自述"基于 Hermes 改进的自进化智能体运行时"）对应第 3 条"打造麒麟 OS Agent"的运行时形态；其多模型传输层（anthropic_messages / bedrock_converse / chat_completions / codex_responses 四类传输，见 [05-model-providers](../concepts/05-model-providers.md)）与第 2 条"屏蔽大模型和框架差异"相互印证。

## 仓库生态（首屏可见部分）

SIG 项目仓库清单分页展示（9 页），第 1 页可见 10 个仓库（均位于 https://gitee.com/openkylin/ 组织下）：

`kylin-baidu-nlp-engine`、`kylin-baidu-vision-engine`、`kylin-ondevice-ai-engine-plugin`、`kylin-ondevice-speech-engine`、`kylin-baidu-speech-engine`、`kylin-ai-engine`、`kylin-ai-sdk`、`kylin-ai-runtime`、`kylin-ondevice-nlp-engine`、`kylin-baidu-ai-engine-plugin`。

这些仓库呈现"云端/端侧引擎（NLP/视觉/语音）+ 引擎插件 + kylin-ai-engine/sdk/runtime 基础层"的 AI 子系统分层结构；`agent-runtime` 仓库本身在第 1 页清单中未出现。

## 采集边界与可信度声明

- 页面中的 PR / Issues / Commits / 贡献排名为**动态时点数据**，随社区活动持续变化；本束不引用这些数字作为事实断言（在 [facts.md](../spec/facts.md) 中刻意排除）。
- 仓库列表共 9 页且分页为 JavaScript 动态加载，静态抓取无法翻页，因此**不臆测** agent-runtime 出现在第几页，也不断言其是否登记于该 SIG 仓库表；可确定的是仓库归属 openKylin Gitee 组织，且 SIG 使命第 3 条与该项目定位直接对应。
- 本信源仅作社区归属与生态背景；技术事实全部以固定 commit `ee0c170` 源码为准（见 [source-code-map](source-code-map.md)）。
