# Open SWE Bundle 变更日志

## 2026-08-23 — v0.1.0（初始生成）

- 基于 `d:/spaces/SpecWeave/external/libs/ai/langchain-ai/open-swe/` 源码，按 OKF v0.2 R→I→E→V 工作流生成中等深度 bundle。
- **R 阶段**：阅读 `agent/` 核心模块（server.py、reviewer.py、analyzer.py、chat.py、scheduler.py、dispatch.py、reconcile.py、baby_sit.py、prompt.py、desktop.py、webapp.py、api/app.py）、`agent/graphs/`、`agent/runtime/`、`agent/review/`、`langgraph.json`、`pyproject.toml`，提取 70 条编号事实写入 `spec/facts.md`。
- **I 阶段**：提炼 4 个架构洞察写入 `spec/insights.md`：
  1. 五个 LangGraph 图工厂，每线程无状态 Agent + 有状态沙箱；
  2. Durable Dispatch 单一契约 + reconcile 安全网构成闭环；
  3. Reviewer 的 findings 单一演进模型 + diff-anchor 纪律 + GitHub thread 双向协调；
  4. 基于 LangGraph + Deep Agents 的洋葱圈中间件与沙箱后端组合。
- **E 阶段**：生成 references/architecture.md、4 篇 concepts（overview、agent-architecture、dispatch-review-cycle、scheduler-reconcile）、examples/triggering-agent-run.md、各级 index.md 与根 index.md。
- **V 阶段**：Grep 验证文档引用的类名/函数名在源码中存在，检查 frontmatter 字段与交叉链接。
