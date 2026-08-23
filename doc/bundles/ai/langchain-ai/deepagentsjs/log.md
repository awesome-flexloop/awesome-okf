# deepagentsjs Bundle 构建日志

## 2026-08-23 v1.13.1

### 构建信息

- **OKF 版本**：0.2
- **Bundle 范围**：deepagentsjs（TypeScript 实现）
- **源码版本**：1.13.1
- **源码路径**：`external/libs/ai/langchain-ai/deepagentsjs/libs/deepagents/`
- **深度**：中等（3 concepts + 1 reference + 1 example）

### 源码分析范围

阅读的核心模块：

- `src/index.ts` — 公共 API 导出
- `src/agent.ts` — createDeepAgent 主函数、中间件组装
- `src/types.ts` — 类型系统（DeepAgentTypeConfig、CreateDeepAgentParams 等）
- `src/values.ts` — filesValue 共享状态值
- `src/compat.ts` — 已废弃的 prompt 兼容导出
- `src/middleware/subagents.ts` — 子代理系统、task 工具
- `src/middleware/fs.ts` — 文件系统中间件
- `src/middleware/summarization.ts` — 摘要中间件
- `src/middleware/memory.ts` — AGENTS.md 记忆中间件
- `src/middleware/skills.ts` — 技能系统
- `src/middleware/async_subagents.ts` — 异步远程子代理
- `src/middleware/agent-memory.ts` — 已废弃的旧记忆中间件
- `src/middleware/index.ts` — 中间件桶导出
- `src/backends/state.ts` — StateBackend 实现
- `src/backends/protocol.ts` — 后端协议定义
- `src/backends/index.ts` — 后端桶导出
- `src/permissions/types.ts` — 权限类型
- `src/profiles/harness/types.ts` — Harness Profile 类型
- `src/profiles/harness/builtins/openai-codex.ts` — Codex profile
- `src/profiles/harness/builtins/anthropic-sonnet-4-6.ts` — Sonnet profile
- `package.json` — 包元信息和依赖
- `README.md` — 项目文档

### 产出文件

| 文件 | 类型 | 说明 |
|---|---|---|
| `index.md` | bundle | 根索引，含 okf_version: "0.2" |
| `spec/facts.md` | spec | 83条编号源码事实，含文件路径和行号 |
| `spec/insights.md` | spec | 3篇架构洞察 |
| `concepts/index.md` | concept index | 概念导航 |
| `concepts/overview.md` | concept | 总览 |
| `concepts/subagent-planning.md` | concept | 子代理与规划 |
| `concepts/context-todo.md` | concept | 上下文与 Todo 管理 |
| `references/index.md` | reference index | API导航 |
| `references/api.md` | reference | 完整 API 参考 |
| `examples/index.md` | example index | 示例导航 |
| `examples/basic-agent.md` | example | 基础 Agent 示例 |

### 关键发现

1. **Todo/planning 不是 deepagentsjs 核心实现**：`write_todos` 工具由 langchain 内置的 `todoListMiddleware` 提供，deepagentsjs 仅在 Codex harness profile 中自动启用它，其他模型需手动添加。
2. **默认模型为 `anthropic:claude-sonnet-4-6`**（agent.ts:175），与 README 中提到的 sonnet-4-5 略有差异。
3. **StateBackend 通过 LangGraph 内部 Pregel 通道**（`__pregel_send`/`__pregel_read`）实现零 Command 返回值的状态更新，镜像了 Python 版的 CONFIG_KEY_SEND。
4. **子代理状态过滤精确排除7个键**，包括 `todos`，意味着父子代理的任务列表完全独立。
