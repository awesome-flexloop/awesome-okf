# 知识束构建日志

## 2026-08-23 — 初始构建

### R 阶段（调研）
- 探索项目根目录与 `libs/` 子目录结构，确认七个包：deepagents、code、cli、acp、evals、talon、partners。
- 阅读根 `AGENTS.md`、`README.md`、`libs/README.md`、`libs/ARCHITECTURE.md`、`libs/DEVELOPMENT.md`、`libs/Makefile`。
- 阅读各模块 README：acp、cli、code、evals、talon、deepagents。
- 阅读 code 模块的 `AGENTS.md` 和 `ARCHITECTURE.md`、evals 模块的 `AGENTS.md`。
- 检查 OpenWiki 生成文档（index.md、architecture/overview.md、quickstart.md）。
- 检查 `.mcp.json`、`ACTION.md`、各包 `pyproject.toml` 关键元数据。
- 在 `spec/facts.md` 中记录 81 条编号事实，覆盖 14 个主题域。

### I 阶段（洞察）
- 提炼 5 个核心洞察到 `spec/insights.md`：
  1. 三层栈架构——"框架而非运行时"的定位哲学
  2. Monorepo 的独立版本化与清晰模块边界
  3. Code 模块的客户端/服务器分离与 Textual TUI 工程
  4. ACP 协议——将 Agent 嵌入编辑器的标准化桥接
  5. 评估驱动的工程文化与 Harbor 沙箱基准

### E 阶段（工程化）
- 创建 `index.md`（含完整 frontmatter：title/type/bundle/description/concepts/references/examples）。
- 创建 `log.md`。
- 创建 7 个概念文档：monorepo架构、核心SDK与三层架构、ACP协议集成、CLI部署工具、Code终端编码Agent、Evals评估套件、Talon运行时宿主。
- 创建 6 个示例文档。
- 创建 13 个引用文档，登记各模块 README 和 AGENTS.md。
- 全部使用中文，交叉链接以 `/datawhale/deepagents/` 开头。

### V 阶段（验证）
- 通过 Grep 验证文档中引用的模块名、文件名、配置项在源码中确实存在。
- 验证关键符号：`create_deep_agent`、`AgentServerACP`、`deepagents-evals`、`deepagents-talon`、`dcode`、`DeepAgentState` 等。
- 验证包名与版本：deepagents 0.7.8、deepagents-code 0.1.59、deepagents-acp 0.0.10、deepagents-talon 0.0.3。

### C 阶段（收尾）
- 最终校验目录结构和 frontmatter 格式。
