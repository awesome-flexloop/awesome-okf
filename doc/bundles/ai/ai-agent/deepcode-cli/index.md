---
type: bundle
okf_version: "0.2"
scope: deepcode-cli
name: deepcode-cli
version: "0.1.0"
source: https://github.com/lessweb/deepcode-cli
description: deepcode-cli 是基于 DeepSeek V4 模型的终端 AI 编程助手，提供交互式 TUI、MCP 工具集成、会话持久化和细粒度权限控制。本 bundle 包含架构、权限、MCP 集成和 CLI 命令的完整文档。
---

# deepcode-cli Wiki Bundle

deepcode-cli（`@vegamo/deepcode-monorepo` v0.2.1）是一个终端 AI 编程助手，采用 npm workspaces monorepo 架构，包含 CLI 工具、核心库和 VSCode 扩展三个子包。项目默认使用 DeepSeek V4 模型，内置 MCP 客户端可连接外部工具服务器，支持会话持久化、Plan Mode、技能系统和细粒度权限控制。

## 核心特性

- **交互式 TUI**：基于 Ink（React for CLI）构建，支持多行输入、模型切换、斜杠命令、图片粘贴
- **非交互执行**：`--exec` 模式单次运行，支持管道输入，适用于脚本和 CI
- **MCP 集成**：内置 MCP 客户端，工具以 `mcp__server__tool` 命名空间暴露，支持动态工具更新
- **会话持久化**：自动保存会话，支持恢复（`--resume`）、分叉（`--fork`）、最近会话（`--last`）和撤销（`/undo`）
- **权限控制**：10 种权限作用域，区分工作目录内外，支持 allow/deny/ask 策略
- **Plan Mode**：计划模式下强制询问写操作和 Git 变更权限
- **技能系统**：支持用户级和项目级 SKILL.md 技能加载
- **多前端支持**：core 包无 UI 依赖，可被 CLI、VSCode 扩展或第三方前端复用

## 文档导航

| 分类 | 文档 | 说明 |
|------|------|------|
| 概念 | [项目简介](/concepts/00-introduction.md) | 概述、功能特性、安装配置 |
| 概念 | [三包 monorepo 架构](/concepts/01-architecture.md) | cli/core/vscode-ide-companion 包结构与依赖关系 |
| 概念 | [权限系统](/concepts/02-permission-system.md) | 10 种权限作用域、allow/deny/ask 策略、合并优先级 |
| 概念 | [MCP 集成](/concepts/03-mcp-integration.md) | MCP 客户端、工具命名空间、JSON-RPC 通信、状态管理 |
| 概念 | [CLI 命令与会话管理](/concepts/04-cli-commands.md) | 命令行参数、斜杠命令、TUI 快捷键、会话存储 |
| 示例 | [基本使用](/examples/01-basic-usage.md) | 从安装到 MCP 配置的完整上手流程 |
| 参考 | [源码信源索引](/references/source.md) | 关键源文件清单及支持的事实 ID |
| 规范 | [事实清单](/spec/facts.md) | R 阶段：59 条带行号引用的事实 |
| 规范 | [核心洞察](/spec/insights.md) | I 阶段：4 条架构洞察与反常识发现 |

## 目录结构

```
deepcode-cli/
├── index.md                    # 本文件（bundle 入口）
├── log.md                      # 变更日志
├── concepts/                   # 概念文档
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-architecture.md
│   ├── 02-permission-system.md
│   ├── 03-mcp-integration.md
│   └── 04-cli-commands.md
├── examples/                   # 示例文档
│   ├── index.md
│   └── 01-basic-usage.md
├── references/                 # 参考资料
│   ├── index.md
│   └── source.md
└── spec/                       # R-I-E 规范产物
    ├── facts.md
    └── insights.md
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | TypeScript 6.x（strict 模式，target ES2022） |
| CLI UI | Ink 7 + React 19 |
| 参数解析 | yargs 18 |
| LLM 客户端 | openai 6（兼容 DeepSeek API） |
| 模板渲染 | EJS 5 |
| 数据校验 | Zod 4 |
| MCP 协议 | JSON-RPC 2.0 over stdio（协议版本 2025-03-26） |
| 构建 | esbuild 0.28 |
| 包管理 | npm workspaces（packageManager npm@10.9.4） |
| Node 要求 | >= 22 |

## 上游信息

- **仓库**：https://github.com/lessweb/deepcode-cli
- **许可证**：MIT
- **版本**：0.2.1
- **主页**：https://deepcode.vegamo.cn

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
