---
type: Reference
title: 阅读地图与现有知识关联
sources:
  - {id: architecture, resource: ../concepts/00-architecture.md}
  - {id: vidbee, resource: ../../../products/vidbee/index.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 阅读地图与现有知识关联

## 按目标阅读

| 目标 | 路线 |
|---|---|
| 不写代码，把直播保存后整理 | [工具选型](../concepts/01-tool-selection.md) → [Windows 录制演练](../examples/windows-recording.md) |
| 已有音视频，交给 Agent 读取 | [确认音轨并提取 WAV](../concepts/02-capture.md) → [离线 JSONL 示例](../examples/offline-transcription.md) → [Agent 分析](../concepts/05-agent-analysis.md) |
| 边播边看字幕或主题 | [三种时间要求](../concepts/00-architecture.md) → [采集与分段](../concepts/02-capture.md) → [时间轴契约](../concepts/04-transcript-contract.md) |
| 验证分析是否可追溯 | [证据检查示例](../examples/agent-evidence-check.md) → [质量验收](../concepts/06-reliability-security.md) |
| 决定哪些能力值得自建 | [架构](../concepts/00-architecture.md) → [最小适配层](../concepts/05-agent-analysis.md) → [验证边界](verification.md) |

## 与已有知识包的边界

[VidBee 视频下载与本地转录](../../../products/vidbee/index.md)侧重单个产品的桌面使用、模型选择、AI 提示词和导出。本包侧重跨工具的直播采集、分段定稿、证据契约、故障恢复与只读 Agent，不将 VidBee 功能清单复制成新的产品手册。

“直播转录”横跨媒体采集、音频识别和知识工程，因此归入 `jishu/ai/practice`。不新增技术域或分组；一个独立知识包即可承载方案和示例。

## 七概念对应关系

| 概念 | 本包位置 | 使用边界 |
|---|---|---|
| R 事实采集 | [来源](source-manifest.md)与[事实表](facts.md) | 工具官方接口为主要证据，不冒充独立性能评测 |
| I 洞察 | 架构页三条洞察 | 区分事实、推论和建议 |
| F 第一性原理 | 五层分工与证据定位 | 从输入保全、时间映射和可回查需求推导适配层 |
| E 萃取 | 可靠性页“证据先行”模式 | L1 候选，迁移为设计推演，不虚构验证案例 |
| A 原子化 | concepts/examples/references | 按读者任务分篇，每篇保留完整语义 |
| V 对抗审查 | [验证记录](verification.md) | 分开记录内容审查、程序测试和未覆盖实机面 |
| C 原子提交 | [变更日志](../log.md) | 本次未获显式 Git 提交指令，不执行 commit/push |

## 缺口由谁验证

具体直播平台的可录制性由操作者用获授权频道验证；本地性能由部署者用目标硬件和真实样本验证；法务与发布权限由内容权利人或负责方确认；Agent 结论由阅读者回听关键证据。任何一项未完成，都不能由本包“结构校验通过”代替。
