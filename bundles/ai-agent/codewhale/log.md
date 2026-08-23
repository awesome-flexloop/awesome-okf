---
type: Changelog
scope: codewhale
name: log
version: "0.1.0"
---

# Changelog

## 0.1.0 — 2026-08-23

### 新增

- 初始 OKF v0.2 wiki 包生成
- **spec/facts.md**：110 条编号事实（F-001 ~ F-110），覆盖工作区结构、21 个 crate、核心运行时、MCP、工具系统、Hooks、执行策略、Workflow、Fleet、模型 Provider、状态持久化、TUI、Skills/Plugins、缓存/记忆、安装分发
- **spec/insights.md**：5 条核心洞察，每条包含陈述/证据/反常识/行动：
  1. Crate 模块化设计——21 个 crate 的严格分层与进行中的 core 迁移
  2. Fleet 多 Agent 编排——持久化 worker 与权限 clamp 模型
  3. Workflow 引擎——声明式 IR + 命令式 JS 双轨设计与确定性回放
  4. MCP 集成——防重放、名称折叠安全与调用时过滤
  5. Skill 系统——四层架构与所有权边界
- **references/source.md**：按 crate 组织的关键源文件索引，标注事实 ID
- **8 个概念文档**：
  - 00-introduction.md（简介与安装）
  - 01-workspace-architecture.md（工作区架构与依赖图）
  - 02-agent-core.md（Runtime、Thread/Session、Engine、JobManager）
  - 03-mcp-protocol.md（MCP 管理器、限定名、JSON-RPC）
  - 04-tool-system.md（ToolRegistry、Handler、并发控制）
  - 05-fleet-subagents.md（Fleet 控制平面、角色、权限 clamp）
  - 06-skills-hooks.md（Skills 四层架构、Hooks 事件、插件）
  - 07-sandbox-execpolicy.md（执行策略、Shell 安全、Seatbelt/bwrap）
- **2 个示例文档**：
  - 01-basic-usage.md（安装、配置、对话、模式切换）
  - 02-fleet-workflow.md（Fleet profile、TOML/JS Workflow、agent 委派）
- **索引文件**：concepts/index.md、examples/index.md、references/index.md
- **根 index.md**：bundle 元数据、功能导航表、3 条学习路径、目录结构

### 数据来源

- CodeWhale v0.9.10 源码（`Cargo.toml`、21 个 crate 的 `Cargo.toml` 和 `src/`）
- 官方文档（`docs/GUIDE.md`、`docs/MCP.md`、`docs/FLEET.md`、`docs/MODES.md`、`docs/HOOKS.md`、`docs/SKILLS.md`、`docs/SUBAGENTS.md`、`docs/SANDBOX.md`、`docs/PLUGINS.md`、`docs/PROVIDERS.md`、`docs/WEB.md`、`docs/CACHE.md`、`docs/MEMORY.md`、`docs/INSTALL.md`、`docs/DOCKER.md`、`docs/RECEIPTS.md`）
- 项目根文件（`README.md`、`AGENTS.md`）

### 生成方式

- R Phase：通过 Glob 和 Read 工具发现并读取源码和文档，提取 110 条带文件路径和行号引用的事实
- I Phase：基于事实综合分析，形成 5 条核心洞察
- E Phase：创建目录结构，编写参考索引、8 个概念文档、2 个示例文档和完整导航索引
