---
type: bundle
okf_version: "0.2"
scope: langsmith-cli
name: langsmith-cli
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli——LangChain AI 开发的 Agent-First Go 命令行工具，用于查询和管理 LangSmith 平台的 traces、runs、datasets、evaluators、experiments 等资源，支持 v1/v2 API 透明切换、OAuth 认证和双模式输出
---

# langsmith-cli

**langsmith-cli** 是 LangChain AI 团队开发的开源命令行工具，用于查询和管理 [LangSmith](https://smith.langchain.com) 平台资源。它使用 Go 语言编写，基于 Cobra CLI 框架和自动生成的 `langsmith-go` SDK，专为 AI 编码代理（deepagents、Claude Code、Cursor 等）和需要快速、可脚本化访问 observability 数据的开发者设计。

- **语言**：Go 1.25.0
- **模块路径**：`github.com/langchain-ai/langsmith-cli`
- **核心依赖**：Cobra v1.8.1、langsmith-go v0.25.6、tablewriter、treeprint、gojq
- **许可证**：MIT

## 核心特性

- **19 个命令组**：覆盖 project、trace、run、thread、dataset、example、evaluator、experiment、sandbox、hub、apps、prompt、auth、profile、workspace、api 等全平台资源。
- **v1/v2 API 透明切换**：运行时自动探测 LangSmith 部署版本（Cloud/自托管），在传统查询 API 和 SmithDB v2 之间无缝切换，命令代码无需感知后端差异。
- **双模式输出**：`--format pretty`（表格/树形，人类可读）和 `--format json`（机器可读），所有写操作输出 JSON 状态，便于脚本和 AI 代理消费。
- **统一过滤器系统**：15+ 通用过滤 flag，自动翻译为 LangSmith filter DSL，同时支持原生 DSL 透传（`--filter`）。
- **多认证方式**：API Key、OAuth 2.0 设备码流、多 profile 配置，token 自动刷新，配置文件 0600 权限。
- **通用 API 逃生舱**：`langsmith api` 命令提供类似 `gh api` 的认证 HTTP 客户端，可直接调用任意 LangSmith 端点。
- **Agent-First 设计**：`SilenceUsage`/`SilenceErrors` 保持输出干净，JSON 状态行写入 stderr，stdout 保持纯净。

## 快速开始

```bash
# 安装
curl -fsSL https://cli.langsmith.com/install.sh | sh

# 认证
export LANGSMITH_API_KEY="lsv2_pt_..."
# 或 OAuth 登录
langsmith auth login

# 查询 traces
langsmith trace list --project my-app --limit 5

# 查询 LLM calls（JSON 输出）
langsmith --format json run list --project my-app --run-type llm --limit 10

# 管理评估器
langsmith evaluator upload evals.py --name accuracy --function check_accuracy --dataset my-eval-set
```

## 文档导航

### 核心概念

- [总览](/langchain-ai/langsmith-cli/concepts/overview) — 项目定位、解决的问题、核心机制与架构概览
- [CLI 命令体系](/langchain-ai/langsmith-cli/concepts/cli-commands) — Cobra 命令树、通用过滤器、DSL 构建、分页与双模式输出
- [API 客户端架构](/langchain-ai/langsmith-cli/concepts/api-client) — langsmith-go SDK 封装、v1/v2 透明切换、OAuth 认证与原始 HTTP

### 参考文档

- [命令参考](/langchain-ai/langsmith-cli/references/commands) — 全部命令、子命令、标志、过滤器与输出格式详解
- [核心数据结构](/langchain-ai/langsmith-cli/references/data-structures) — Client、Options、FilterFlags、Config/Profile/OAuth 等关键类型

### 使用示例

- [基础使用示例](/langchain-ai/langsmith-cli/examples/basic-usage) — 认证、查询 traces/runs、过滤器 DSL、数据集与评估器管理、JSON 输出、OAuth、通用 API 调用

## 目录结构

```
langsmith-cli/
├── spec/
│   ├── facts.md           # 源码事实验证清单（57 条编号事实）
│   └── insights.md        # 架构洞察（3 个深度分析）
├── concepts/              # 核心概念（3 篇）
│   ├── overview.md
│   ├── cli-commands.md
│   └── api-client.md
├── references/            # API/技术参考（2 篇）
│   ├── commands.md
│   └── data-structures.md
├── examples/              # 使用示例（1 篇）
│   └── basic-usage.md
├── log.md                 # 构建日志
└── index.md               # 本文件
```
