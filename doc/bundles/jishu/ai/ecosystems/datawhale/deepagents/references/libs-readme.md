---
title: libs/README.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/README.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/README.md
---

# libs/README.md 引用

Monorepo 包清单与各包描述。

## 核心内容

- **入门推荐**：从 `deepagents-code`（dcode）开始体验，或使用 `deepagents` SDK 构建自定义 Agent
- **包清单表**：

| 包 | PyPI | 描述 |
|----|------|------|
| `deepagents` | `deepagents` | 核心 SDK——create_deep_agent、中间件、可插拔后端 |
| `code` | `deepagents-code` | 预构建终端编码 Agent（dcode），Textual TUI、远程沙箱、记忆、技能、headless 模式 |
| `cli` | `deepagents-cli` | 部署 CLI——init、deploy、agents、mcp-servers 子命令 |
| `acp` | — | Agent Client Protocol 集成，在 Zed 等编辑器中运行 Deep Agent |
| `evals` | — | 评估套件和 Harbor 集成，用于基准测试 Agent 行为 |
| `talon` | — | 实验性本地运行时宿主，用于长运行 Agent（通道适配器、cron 调度器） |
| `partners` | — | 提供商集成（Daytona、Modal、Runloop、Vercel、QuickJS） |

## 相关概念

- Monorepo 架构
