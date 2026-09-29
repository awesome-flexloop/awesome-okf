---
type: Changelog
scope: deepcode-cli
name: log
version: "0.1.0"
source: https://github.com/lessweb/deepcode-cli
description: deepcode-cli OKF wiki bundle 变更日志
---

# 变更日志

## 2026-08-23

### 新增

- 初始化 OKF v0.2 wiki bundle
- **R 阶段（事实）**：创建 `spec/facts.md`，包含 59 条编号事实（F-001 至 F-059），每条引用确切文件路径与行号，覆盖项目元信息、TypeScript 配置、三包结构、权限系统、设置配置、MCP 集成、CLI 命令、会话管理、Core 库导出和 VSCode 扩展
- **I 阶段（洞察）**：创建 `spec/insights.md`，包含 4 条核心洞察：
  1. 三层设置合并模型中环境变量的最高优先级
  2. MCP 工具命名的哈希消歧机制
  3. 权限系统的 allowAll 默认模式与 Plan Mode 强制询问
  4. 三包 monorepo 中 core 包的无 UI 依赖设计
- **E 阶段（文档）**：
  - 创建 `references/source.md`：源码信源索引，列出 14 个关键源文件及支持的事实 ID
  - 创建 5 篇概念文档：
    - `concepts/00-introduction.md`：项目简介、功能特性、安装
    - `concepts/01-architecture.md`：三包 monorepo 架构与依赖关系
    - `concepts/02-permission-system.md`：10 种权限作用域与合并策略
    - `concepts/03-mcp-integration.md`：MCP 客户端管理、命名空间与协议
    - `concepts/04-cli-commands.md`：CLI 参数、斜杠命令、会话管理
  - 创建 `examples/01-basic-usage.md`：从安装到 MCP 配置的完整上手示例
  - 创建 4 个导航索引文件：`concepts/index.md`、`examples/index.md`、`references/index.md`、根 `index.md`
- 所有概念文档和示例文档均包含标准 frontmatter（type、title、description、tags、generated、verified、status、stale_after、sources）
- 所有内部链接使用 bundle 根相对路径（`/` 前缀）
