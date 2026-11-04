---
type: Reference
title: Super-agent 编号事实表
sources:
  - id: guide
    resource: https://mp.weixin.qq.com/s/gYZGu2qndS6dgCYqQHi03Q
  - id: news-pd
    resource: https://peoplesdaily.pdnews.cn/china/er/30053466920
  - id: news-pandaily
    resource: https://pandaily.com/deepseek-harness-super-agent-prototype-router-worker-event-driven-watchdog-open-source-mit
status: flagged
stale_after: 2026-12-04
generated: { by: "agent/okf-wiki", at: "2026-11-04" }
---

# Super-agent 编号事实表

下表登记的是“页面说了什么”，不是对设计效果的认可。`author_claim` 包括来源作者的解释、能力描述与媒体转述；执行者推论仅放入概念页。共 30 项，连续 F-001 至 F-030。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 导读标题为 DeepSeek 团队谈 Super-agent：AI 越来越能干，人为什么还这么忙？ | page_fact | guide | 页面标题 | page-verified |
| F-002 | 页面账号为小枫coding，作者为小枫，并标记原创 | page_fact | guide | js_name/meta_content | page-verified |
| F-003 | 页面发布时间为 2026-11-01 20:05 | page_fact | guide | publish_time | page-verified |
| F-004 | 导读描述用户在多任务间切换窗口、补背景、追问进度 | author_claim | guide | 开头“用 AI 同时推进几件事” | single-source |
| F-005 | 导读将人的注意力视为多任务协作瓶颈 | author_claim | guide | 开头后续段落 | single-source |
| F-006 | 导读列出跨会话上下文、并行任务、主动响应环境、长期在线等设计目标 | author_claim | guide | “团队提出的 Super-agent” | secondary-supported |
| F-007 | 导读将核心设计概括为 Router 与多个 Worker 两层 | author_claim | guide | “核心设计可以先理解成两层” | secondary-supported |
| F-008 | 导读称 Router 统一交互和任务分派；Global Times 还描述维持共享上下文 | author_claim | guide, news-pd | 双层分工段；报道“two-layer structure” | secondary-supported |
| F-009 | 导读称多个 Worker 使用独立上下文执行任务 | author_claim | guide | 双层分工段 | secondary-supported |
| F-010 | 导读称订阅机制把相关消息送到对应 Worker | author_claim | guide | “用户面对的是同一个协作者” | secondary-supported |
| F-011 | 导读讨论事件驱动与异步交互 | author_claim | guide | 配图后的机制段 | secondary-supported |
| F-012 | 导读讨论计算、状态和执行环境分离；Pandaily 描述云端保持在线并接触用户设备 | author_claim | guide, news-pandaily | 配图后的机制段；报道“event-driven” | secondary-supported |
| F-013 | 导读讨论 Watchdog 检查异常和进度；Global Times 描述外部监控机制 | author_claim | guide, news-pd | 配图后的机制段；报道“external monitoring” | secondary-supported |
| F-014 | 导读推荐上游第2节双层架构、第3节事件驱动、第4节面向人的交互 | author_claim | guide | “如果时间有限” | single-source |
| F-015 | 导读提到上游第7节初步实验、第8节开放问题 | author_claim | guide | 推荐阅读段 | single-source |
| F-016 | 导读称这是工程架构探索，非现有产品功能介绍，并提到研究原型 | author_claim | guide | 文末“原文说明” | secondary-supported |
| F-017 | People's Daily 页面署名 Global Times，时间为 2026-11-01 09:01 | page_fact | news-pd | 标题下署名时间 | page-verified |
| F-018 | Global Times 报道把方案归于 DeepSeek Harness 团队 | author_claim | news-pd | “In an article published on Saturday” | secondary-only |
| F-019 | 报道列出 continuity、efficiency、proactivity、persistence 四项目标 | author_claim | news-pd | “four major features” | secondary-only |
| F-020 | 报道称内部系统参与复现软件问题、修复和代码审查 | author_claim | news-pd | “internal Super-agent system” | secondary-only |
| F-021 | 报道称公开研究原型非官方产品或生产就绪软件，且不同于内部系统 | author_claim | news-pd | “research prototype” | secondary-only |
| F-022 | 报道列出扩展性、长期记忆、Agent 间通信及云端访问本地设备的安全隐私问题 | author_claim | news-pd | 文末“challenges remain” | secondary-supported |
| F-023 | Pandaily 报道发布日期为 2026-11-01 | page_fact | news-pandaily | Published | page-verified |
| F-024 | Pandaily 称研究原型名为 dsh-superagent-prototype，并称采用 MIT 许可 | author_claim | news-pandaily | 首段及 repository 段 | unverified/flagged |
| F-025 | Pandaily 称该原型针对单个 GitHub 仓库，监听 GitHub 与可选 Feishu | author_claim | news-pandaily | repository 段 | secondary-only |
| F-026 | Pandaily 称 Router 只派工，可无 Bash 工具；Worker 向 Router 汇报而非直接面向用户 | author_claim | news-pandaily | “core idea” | secondary-only |
| F-027 | Pandaily 称消息、邮件、审查评论、CI 结果先经确定性代码过滤，再经模型处理 | author_claim | news-pandaily | “event-driven” | secondary-only |
| F-028 | Pandaily 转述合成负载约300条消息、约20个请求，半数任务12.4分钟内、95%任务15.7分钟内完成，缓存 token 更多 | author_claim | news-pandaily | “preliminary tests” | unverified/flagged |
| F-029 | Pandaily 转述取消后续消息直达 Worker 后 Router 决策约增加30%；负载下批处理每次决策推理时间6.4秒降至1.6秒 | author_claim | news-pandaily | “preliminary tests” | unverified/flagged |
| F-030 | Global Times 转述一人可跟踪3至5个活跃会话 | author_claim | news-pd | “three to five active sessions” | unverified/flagged |

F-028 至 F-030 不进入教程的性能结论；实验原文、任务定义、样本分布、模型和硬件未核读。F-024 不构成使用许可证的依据。
