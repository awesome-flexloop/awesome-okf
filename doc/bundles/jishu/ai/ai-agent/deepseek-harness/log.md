# 更新日志

## 2026-09-02

**Merge**: 从 SpecWeave docs/knowledge/learning/03-agent-platforms-tools/deepseek-harness-wiki/ 合并独有内容

- 新增 `concepts/usage-modes-and-embedding.md`：运行模式与嵌入式集成（四种运行模式能力对比与选型、Code 模式 PTC 机制、Minimal 评测模式、Creator 定制流程、Headless 无头模式与 CI 自动化、Python SDK 自带 Node 运行时、JSON-RPC 跨语言集成、ACP 服务端用途、嵌入应用典型场景、配置共享机制），源自 learning 侧 04-four-modes.md 与 12-headless-sdk.md（基于 v0.1.0-rc.6 实测）
- 更新根 `index.md` 概念导航与 toctree（10→11 概念）；补建本束 `log.md`（此前缺失）
- 重复确认：learning 侧 00 章核心概念速览（Cordis/Context/Plugin/事件分发/SessionLog 等）与既有 cordis-plugin-architecture/agent-runtime-loop/session-and-context 覆盖重叠，未重复迁入；其余章节（01-03、05-11、13-16）在源侧缺失，无内容可迁
