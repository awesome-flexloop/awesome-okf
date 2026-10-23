---
type: Log
title: DeepSeek Harness 0.2 教程更新日志
description: deepseek-harness-0-2 知识包的创建与变更记录
tags: [deepseek-harness, dsh, 更新日志]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
---

# 更新日志

## 2026-10-22

### 创建
- 新建 `deepseek-harness-0-2` bundle，基于 DeepSeek Harness 官方仓库 **0.2.1-rc.2** 本地源码镜像 + 仓库内 `docs/` 中文文档集精读生成
- 创建 11 篇概念文档、5 篇示例文档、2 篇参考文档
- 独立成束而非复用既有 `deepseek-harness` 束：后者基于 **0.1.0-rc.5**（ReactLoopAgent + Phase 队列架构），与 0.2 的 profile/组合包分层、能力 seam、session 事件日志已换代，混写会产生事实错误
- 旧束保留作历史对照，两束在新束首页互链

### 结构
- `concepts/`：00-getting-started、01-architecture-overview、02-cordis-plugin-model、03-profile-and-bundle、04-agent-loop、05-session-and-persistence、06-tool-system、07-llm-abstraction、08-capability-seams、09-security-model、10-application-forms
- `examples/`：00-headless-task、01-mcp-integration、02-custom-tool、03-custom-plugin-bundle、04-python-sdk-embedding
- `references/`：source-map（源码路径与包清单登记）、facts（F-001~F-048 事实登记，区分源码事实 / 文档主张）
- `log.md`：本文件
- 三级目录各配 `index.md` 导航页（concepts/examples/references），与 kylin-agent-runtime 等既有束一致

### 事实校订
- `SessionEventMap` 核心变体数由 13 更正为 **14**（复核 `packages/core/session/src/types.ts`，含 `request/context` 与 `session/end-seed`）

### 信源口径
- 一手信源为官方源码与仓库内官方中文文档；未采用二手解读内容
- 知乎侧 CLI 因本机执行策略受限未能初始化，故本次未纳入知乎内容（不影响信源完整性）

### 索引对账
- `jishu/ai/frameworks/ai-agent/index.md`：束数 56 → 57，导航表与 toctree 同步新增，正文内容统计 405 → 423 文档
- `jishu/ai/frameworks/index.md`：束数 86 → 87（+ vllm 并入后 88）
- `jishu/ai/index.md`：束数 261 → 262（+ vllm 并入后 263）
- `jishu/index.md` 与 `doc/bundles/index.md`：ai 域束数同步，总索引对账通过
- 质量门：`check-bundles-index.py` 通过（9 域 / 63 组 / 667 束，五面一致）；`check-utf8.py` 通过（12158 文件）；`check-toctrees.py` 中本束 **0 问题**
