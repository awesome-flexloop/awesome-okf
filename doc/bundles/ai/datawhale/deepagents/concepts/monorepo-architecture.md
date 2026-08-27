---
title: Monorepo 架构
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/core-sdk
  - /datawhale/deepagents/concepts/code-module
  - /datawhale/deepagents/concepts/cli-toolchain
  - /datawhale/deepagents/concepts/acp-protocol
  - /datawhale/deepagents/concepts/evals-suite
  - /datawhale/deepagents/concepts/talon-runtime
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/DEVELOPMENT.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/Makefile
  - https://github.com/datawhalechina/deepagents/blob/main/AGENTS.md
---

# Monorepo 架构

Deep Agents 仓库采用 **monorepo 结构**，所有 Python 包位于 `libs/` 目录下，每个包独立版本化、独立发布。这种设计在统一开发体验的同时保持了各包的发布独立性。

## 包清单

| 目录 | PyPI 包名 | 版本 | 职责 |
|------|-----------|------|------|
| `libs/deepagents/` | `deepagents` | 0.7.8 | 核心 SDK：`create_deep_agent`、中间件、后端、配置文件 |
| `libs/code/` | `deepagents-code` | 0.1.59 | 终端编码 Agent（`dcode`），Textual TUI + LangGraph 服务器 |
| `libs/cli/` | `deepagents-cli` | — | 部署 CLI：`init`/`deploy`/`agents`/`mcp-servers` |
| `libs/acp/` | `deepagents-acp` | 0.0.10 | Agent Client Protocol 集成（Alpha） |
| `libs/evals/` | `deepagents-evals` | — | 端到端评估套件与 Harbor 集成 |
| `libs/talon/` | `deepagents-talon` | 0.0.3 | 长运行 Agent 本地运行时宿主（实验性） |
| `libs/partners/` | — | — | 沙箱/提供商集成：daytona、modal、quickjs、runloop、vercel |

## 关键设计特征

### 无根 pyproject.toml

仓库**没有根级 `pyproject.toml`**。每个包拥有自己的 `pyproject.toml`、`uv.lock`、`Makefile` 和 `README.md`。开发者在正在修改的包目录内工作，uv 创建和管理该包的虚拟环境。

### uv 依赖管理

使用 [uv](https://docs.astral.sh/uv/) 管理解释器、虚拟环境和依赖。明确禁止使用 pip、poetry 或 conda。本地包依赖是 editable 的，一个包的修改对依赖它的兄弟包立即可见。

### Python 版本

- ACP 包要求 Python 3.14
- 其余包要求 Python 3.12+
- 不固定全局 Python 版本，由各包 `pyproject.toml` 的 `requires-python` 决定

### Make 任务体系

每个包的 `Makefile` 是其命令的唯一来源。标准目标包括：

| 命令 | 作用 |
|------|------|
| `make test` | 运行单元测试（无网络） |
| `make integration_test` | 运行集成测试（允许网络） |
| `make lint` | ruff 检查 + ty 类型检查 |
| `make format` | 自动格式化和安全 ruff 修复 |
| `make type` | 仅运行 ty 类型检查器 |
| `make bench` | walltime 基准测试 |
| `make bench-memory` | 堆内存基准测试 |

### 跨包 Fan-out

`libs/Makefile` 提供跨包操作：

- `make lint` — lint 所有包
- `make format` — 格式化所有包
- `make lock` — 更新所有锁文件
- `make lock-check` — 验证所有锁文件最新
- `make lock-bump DEP=<pkg>` — 跨所有锁文件升级一个依赖
- `make bench-all` — 在 deepagents 和 code 包上运行基准测试

### 搜索卫生

根 `AGENTS.md` 引导开发者定向搜索特定路径，避免全仓库漫游：

- SDK 源码和测试：`libs/deepagents/deepagents`、`libs/deepagents/tests`
- 编码 Agent：`libs/code`
- 部署 CLI：`libs/cli`
- ACP：`libs/acp`
- Talon：`libs/talon`
- Evals：`libs/evals`
- Partner 包：`libs/partners/<partner>`

## 开发规范

- **Conventional Commits**：PR 标题必须包含 type(scope)，允许的类型和 scope 定义在 `.github/workflows/pr_lint.yml`。
- **分支命名**：`<github-username>/<scope>/<short-description>`。
- **测试分类**：无网络测试放 `tests/unit_tests/`，网络测试放 `tests/integration_tests/`。
- **警告即错误**：所有包将未接受的 pytest 警告视为错误。
- **pre-commit**：运行格式化、lint、锁文件检查和提交消息验证。

## 与其他概念的关系

- 核心SDK与三层架构 是 monorepo 中 `deepagents` 包的内部设计。
- Code终端编码Agent 精确钉住核心 SDK 版本，是最大的消费者。
- CLI部署工具 和 ACP协议集成 是横向扩展包。
- Evals评估套件 验证 SDK 和 Code 的行为质量。
- Talon运行时宿主 依赖 deepagents 和 deepagents-code。
