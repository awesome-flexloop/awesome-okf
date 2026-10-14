---
okf_version: "0.2"
type: bundle
title: "企业微信 5.0.10 版本新功能：CLI/MCP 开放与大圆 AI 报告"
description: "企业微信官方 5.0.10 版本介绍页经七概念链路转化：CLI/MCP 双通道开放办公模块（7/10/11 模块时点口径）、Skill 安装命令核验、智能表格大圆 AI 分析报告、智能文档导出增强；含 33 条登记事实，版本资讯非操作教程"
tags: [企业微信, WeCom, 5.0.10, CLI, MCP, Agent, Skill, 智能表格, 大圆, 智能文档, 版本发布]
generated: { by: "process:seven-concepts-e", at: "2026-10-14" }
verified: { by: "process:seven-concepts-v", at: "2026-10-14" }
status: stable
stale_after: "2027-01-31"
sources:
  - { id: W, resource: "https://work.weixin.qq.com/nl/act/p/b40dacdc68ee4589?ver=5.0.10&type=new&lang=zh" }
  - { id: O1, resource: "https://work.weixin.qq.com/nl/index/aicli?from=new_intro" }
  - { id: O2, resource: "http://m.toutiao.com/group/7675264433509138998/" }
  - { id: O3, resource: "https://www.npmjs.com/package/@wecom/cli" }
  - { id: O4, resource: "https://work.weixin.qq.com/" }
  - { id: O5, resource: "https://developer.work.weixin.qq.com/document/path/101805" }
  - { id: O6, resource: "http://www.cnstock.com/commonDetail/802000" }
  - { id: O7, resource: "https://juejin.cn/post/7622655641333596196" }
  - { id: O8, resource: "https://open.work.weixin.qq.com/help/wap/detail?docid=21657" }
---

# 企业微信 5.0.10 版本新功能：CLI/MCP 开放与大圆 AI 报告

> **内容性质：版本发布资讯/技术综述，非操作教程。** 原文是官方版本新功能介绍页，没有可照做且经实测的安装配置链路（仅一句 Skill 安装提示词），按「操作可复现性两问」判定不设 `examples/`。
>
> **可信度状态：`stable`（含 3 类口径提示，无核心声明证伪）。** 信源为企业微信官方发布页，核心声明经官方 AI 能力页、官网、开发者中心与 npm 注册表交叉核验；模块数 7/10/11、安装命令大小写等差异为时点演进与写法口径，已分层呈现，详见[核验报告](references/verification.md)。

## 这束知识包讲什么

2026 年 8 月 18 日，企业微信 5.0.10 版本面向所有规模企业开放 CLI 与 MCP 能力（IT之家发布日锚点），主打「让 AI Agent 直接调用企业微信底层办公能力」；同期智能表格上线智能助理「大圆」的 AI 分析报告（灰度中），智能文档补齐多格式导出。本束按七概念知识沉淀链路（R→I→E→V）把官方版本介绍页重构为**事实—机制—功能**三层：

| 顺序 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| 1 | [5.0.10 版本更新总览](concepts/00-wecom-5-0-10-release-overview.md) | 这个版本何时发布、开放给谁、更新了什么？现在是否仍是最新版？ |
| 2 | [AI 开放能力：CLI 与 MCP](concepts/01-ai-open-capability-cli-mcp.md) | CLI/MCP 是什么？开放哪些模块？两条安装路径的命令和包有何区别？安全边界？兼容哪些 Agent？ |
| 3 | [智能表格大圆与智能文档](concepts/02-smart-sheet-dayuan-and-smart-doc.md) | 大圆分析报告能做什么（灰度状态如何）？智能文档能导出哪些格式？ |
| 查证 | [文章事实登记](references/article-source.md)（F-001～F-033）与[核验报告](references/verification.md) | 每条说法的出处、信源距离与核验结论 |

## 已知边界

- **灰度功能**：智能表格 AI 分析报告在 5.0.10 发布时标注「功能灰度中」，并非所有租户可见；灰度范围与转正时间以官方公告为准（[F-013](references/article-source.md)）。
- **版本快照与官方页演进**：发布页枚举 7 个开放模块；核验时（2026-10-14）官方 AI 能力页已扩展到 11 个模块（文档系拆分 + 通讯录）。本束保留 5.0.10 时点口径，不以现状倒写历史；查最新能力以[官方 AI 开放能力页](https://work.weixin.qq.com/nl/index/aicli?from=new_intro)为准（F-021、F-027）。
- **5.0.10 已被接替**：2026-10-14 腾讯已发布企业微信 5.0.12（WorkBuddy 以可对话机器人进入企业联系人列表，WorkBuddy 5.8.0 支持企微账号登录）（F-031）。
- **命令大小写口径**：发布页写 `wecomTeam/wecom-unified`，官方 AI 页写 `WecomTeam/wecom-unified` 与 `WeComTeam/wecom-cli`，npm 仓库 canonical 为 `WecomTeam`；GitHub org 大小写不敏感但应按 canonical 引用，且 `wecom-unified` 与 `wecom-cli` 是两个不同的包（F-023、F-025）。
- **信源强弱分层**：「报告随数据实时更新」仅发布页单源（F-016）；安全四机制为 IT之家媒体转述、未取得开发者文档逐字页（F-026）；发布页与官方页均无提效倍数等成效数字，本束不含厂商成效叙事。

## 主题关联

- [腾讯会议 CLI（tencent-meeting-cli）](../tencent-meeting-cli/index.md)——同属「腾讯办公 + 官方 CLI/Agent」主题：腾讯会议官方 CLI 的完整使用与源码机制教程（含 OAuth、命令域、事件总线），可与本束的企微开放能力对照。
- [LightVela 与 Personal Agent 赛道观察](../lightvela-personal-agent/index.md)——同分组博文核验束：腾讯轻量云 Agent 与微信/企微等五通道接入的赛道分析。
- [WorkBuddy 一句话做 MVP](../workbuddy-one-sentence-mvp/index.md)——WorkBuddy 软文核验束；5.0.12 中 WorkBuddy 与企微深度互通，是本束版本时效线的后续（F-031）。
- [腾讯 WeKnora 技术综述](../weknora/index.md)——腾讯系知识库/Agent 能力的技术综述（同分组资讯核验束）。
- [企业微信 5.0.12 版本更新](../wecom-5-0-12-release/index.md)——本束的下一版本快照：WorkBuddy 深度融合、机器人双领用入口、频道与知识库、对外管理与智能幻灯片前瞻口径（51 条事实）。

## 一句话结论

5.0.10 标志着企业微信从「应用内加 AI 功能」（大圆报告）走向「把办公底座整体暴露给 Agent」（CLI/MCP + 权限审批护栏）；至 2026-10-14 的 5.0.12，路线已推进到第三方 Agent（WorkBuddy）直接进入企业通讯录——开放模块从 7 个增至 11 个的演进速度，比任何单条功能都更值得追踪。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
