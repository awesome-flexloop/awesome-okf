---
type: Reference
title: "Claude 模型选型官方核验报告"
description: "核验模型阵容、四档价格、effort 默认值、别名解析与基准口径，并记录勘误与单源边界。"
tags: [claude, verification, pricing, effort, benchmark]
generated: { by: "lobsterai/main", at: "2026-11-10T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T13:30:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    resource: https://claude.dev/blog/which-claude-model-should-you-build-with/
  - id: fable-page
    resource: https://www.anthropic.com/claude/fable
  - id: opus-page
    resource: https://www.anthropic.com/claude/opus
  - id: sonnet-page
    resource: https://www.anthropic.com/claude/sonnet
  - id: haiku-page
    resource: https://www.anthropic.com/claude/haiku
  - id: fable-launch
    resource: https://www.anthropic.com/claude-fable-and-mythos-5-2
  - id: cc-model-config
    resource: https://code.claude.com/docs/en/model-config
---

# Claude 模型选型官方核验报告

## 核验结论

| 核验项 | 结果 | 事实编号 |
|---|---|---|
| 四模型阵容与 GA 状态 | ✅ 四个模型页均在线，Fable 5.2 于 2026-11-09 发布 | F-003 |
| Mythos 5.2 定位与获取方式 | ✅ 发布文确认 Fable 与 Mythos 同源，Mythos 经验证计划提供 | F-004 |
| Haiku 5.5 分档价格 | ✅ Haiku 页逐项列出 `$0.10/$0.50` 与 `$0.50/$2.50` | F-026 |
| Sonnet 5.5 价格 | ✅ Sonnet 页确认 `$2/$10` | F-027 |
| Opus 5.5 价格与缓存价 | ✅ Opus 页确认 `$4/$20`、缓存读 `$0.20` | F-028、F-030 |
| Fable 5.2 价格与缓存价 | ✅ Fable 页与发布文确认 `$8/$40`、缓存读 `$0.20` | F-029、F-030 |
| Fast mode 归属与溢价 | ✅ Opus `$8/$40`、Fable `$16/$80`，均最高 2.5x | F-035、F-044 |
| Fable 5.2 在 FrontierCode 2.0 `high` 约等于 Opus 5.5 `max` | ✅ 发布文原文 45.3% vs 45.5%，成本约一半 | F-037 |
| Fable 5.2 比 5.1 快 30% | ✅ 发布文确认 | F-040 |
| Claude Code 默认 effort 为 `medium` | ✅ model-config 文档：四模型均默认 `medium` | F-034 |
| `haiku` 别名在 API 解析为 5.5、其他平台为 4.5 | ✅ model-config 文档逐平台列出 | F-058 |
| 1M 上下文 | ✅ 四个模型页均标注 1M | F-031 |
| 最大输出 128K | ⚠️ 博文单源，模型页未逐项列出 | F-032 |
| API 默认 effort：Sonnet/Fable 为 `high` | ⚠️ 博文单源；可访问文档只确认 Claude Code 侧为 `medium` | F-034 |
| Sonnet 5.5 缓存读取 `$0.10` | ⚠️ 与官方“最多 90% 缓存节省”口径冲突，详见勘误 E-1 | F-030 |
| Opus 5.5 为各计划默认模型 | ⚠️ 文档仅确认“Fable 不是任何计划的账户默认”，未逐计划点名 Opus | F-006、F-023 |
| SWE-bench Pro / Terminal-Bench / 内部基准数字 | ⚠️ 厂商自述，未独立复算 | F-036、F-039、F-041、F-043、F-063、F-064 |
| preserved thinking 400 规则、advisor 细节、`computer_toolset_20260801` | ⚠️ 单源；platform.claude.com 在核验环境返回区域限制页 | F-060—F-072 |

## 勘误与口径

### E-1 Sonnet 5.5 缓存读取单价

博文对照表写 Sonnet 5.5 缓存读取为 `$0.10`/百万 token。官方 Sonnet 页只写“prompt caching 最多节省 90%”，按输入价 `$2` 的 10% 推算应为 `$0.20`，与博文数字不一致；Opus/Fable 页则明确列出 `$0.20`。

处理：正文保留博文数字并同列官方口径与推算值，提示以实时价目表为准；该差异不影响“缓存读取远低于输入价”的结论。

### E-2 API 默认 effort 与 Claude Code 默认 effort 不是同一口径

博文表格把 Sonnet 与 Fable 的 API 默认 effort 标为 `high`，同时注明 Claude Code 中为 `medium`。可访问的 model-config 文档确认 Claude Code 侧四模型均为 `medium`，但 API 侧默认值位于区域受限的 platform 文档，未能逐字核验。正文分栏呈现，避免把两个口径混为一个。

### E-3 “默认模型”表述

博文称 Claude Code 在 Pro/Max/Ultra/Team/Enterprise 与 Anthropic API 上默认使用 Opus 5.5。model-config 文档只确认“没有任何 Fable 模型是任何计划或供应商的账户默认”，未点名具体默认模型。正文采用“博文口径”，并标注官方文档未逐计划列出。

### E-4 基准与内部实验的数字层级

FrontierCode 2.0 的 45.3%/45.5% 与 49.1% 已由 Fable 5.2 发布文确认；Terminal-Bench 3.0、SWE-bench Pro 的分数差、43% 开销集中度、90.1%/$2.92、97%/$0.17 等均为厂商自述或同站文章转述，未独立复算。正文以“厂商自述”标注，不作为跨厂商横比依据。

## 未获独立核验项

1. platform.claude.com 全部页面在核验环境返回 “App unavailable in region”，API 侧 thinking、effort、advisor、preserved thinking、computer use 工具集只能单源登记。
2. 博文中的四段演示视频与图像质量评价属于作者演示样本，不代表总体能力上限。
3. 价格与版本为 2026-11-10 快照；`stale_after` 设为 2026-12-31。

## 审查记录

- G1：事实、方法论建议、作者观点、厂商自述四层已分开登记；方法论建议不写成官方结论。
- G2：洞察按“价格—任务成本—上下文—编排”四元组组织，每条结论附适用边界。
- G3：选型矩阵、升级顺序、自测闭环可迁移到其他模型家族与供应商。
- G4：两篇 examples 各自单一目标、可独立验证，并写明预期输出。
- 双份 F 编号：`F-001` 至 `F-077` 集合一致、连续无跳号。
