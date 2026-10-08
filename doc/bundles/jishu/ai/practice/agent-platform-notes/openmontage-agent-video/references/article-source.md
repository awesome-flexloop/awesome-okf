---
type: Reference
title: "文章事实与官方信源"
description: "登记微信文章关于 OpenMontage 的主张，并与官方仓库机制文档分层"
tags: [OpenMontage, Agent, 视频制作, 事实核验]
generated: { by: "process:seven-concepts-r", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/Icq2rjqPi7gfVb-x7cCz8Q" }
  - { id: repo, resource: "https://github.com/calesthio/OpenMontage" }
  - { id: guide, resource: "https://raw.githubusercontent.com/calesthio/OpenMontage/main/AGENT_GUIDE.md" }
---

# 文章事实与官方信源

微信文章发表于2026-07-31，主题是 OpenMontage 的 Agent 视频生产流水线。以下内容为原创转述，不复制文章全文。W 表示微信文章，O 表示 OpenMontage 官方仓库。

| 编号 | 声明 | 来源 | 状态 |
| --- | --- | --- | --- |
| F-001 | 文章标题为《离谱！4.3 万 Star OpenMontage，厉害到让你怀疑自己！！！哈哈哈》。 | W | 热度未独立核实 |
| F-002 | OpenMontage 是开源 Agent 视频制作系统，目标覆盖研究、脚本、素材、剪辑和渲染。 | W、O1 | 官方 README 支持定位 |
| F-003 | 官方 README 声称许可证为 AGPLv3。 | O1、O3 | 已核对 |
| F-004 | 快速开始需要 Python 3.10+、FFmpeg、Node.js 18+ 与 AI 编程助手。 | O1 | 已核对 |
| F-005 | 快速开始命令为 `git clone`、进入目录、`make setup`。 | O1 | 已核对 |
| F-006 | 生产阶段包含 research、proposal、script、scene_plan、assets、edit、compose。 | O1 | 已核对 |
| F-007 | AGENT_GUIDE 要求先读规则与技能，再选择流水线和工具。 | O2 | 已核对 |
| F-008 | README 支持真实素材与开放档案路径，而不只是图像动画。 | O1 | 已核对 |
| F-009 | 文章列举多种任务流水线，包括科普、纪录片、电影感、切片、屏幕演示、播客再利用和本地化配音。 | W、O1 | 列表可能随版本变化 |
| F-010 | 渲染/后期链路包含 Remotion、HyperFrames 与 FFmpeg。 | O1 | 已核对 |
| F-011 | 文章时点称约4.36万 Star、5.2k Fork、12条流水线、100+工具和700+技能/知识文件。 | W | 时点快照，不作为当前计数 |
| F-012 | 官方示例提示词包含60秒动画科普和75秒真实素材纪录片。 | O1 | 已核对 |
| F-013 | Piper TTS、开放素材、本地渲染可支持低密钥路径，但高级模型和服务可能收费。 | O1 | 成本取决于配置 |
| F-014 | AGPLv3 的自由软件许可不等于零成本或免除网络服务场景的合规义务。 | O3 | 许可证原文 |
| F-015 | 文章的“省时50%”与热度数字没有给出完整统计口径或独立评测。 | W | 证据缺口 |
| F-016 | 文章中的热度和规模数字应视为2026-07-31附近的读取日快照，不应当作当前仓库计数。 | W、O1 | 时效边界 |
