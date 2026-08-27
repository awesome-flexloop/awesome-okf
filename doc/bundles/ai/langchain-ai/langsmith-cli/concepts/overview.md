---
type: concept
scope: langsmith-cli
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli 总览——Agent-First 的 LangSmith 命令行工具
---

# langsmith-cli 总览

## 什么是 langsmith-cli

**langsmith-cli** 是 LangChain AI 团队开发的开源命令行工具，用于查询和管理 [LangSmith](https://smith.langchain.com) 平台资源。它使用 Go 语言编写，基于 Cobra CLI 框架和自动生成的 `langsmith-go` SDK，面向 AI 编码代理（deepagents、Claude Code、Cursor 等）和需要快速、可脚本化访问 traces、runs、datasets、evaluators、experiments、threads 的开发者。

- **语言**：Go 1.25.0
- **模块路径**：`github.com/langchain-ai/langsmith-cli`
- **核心依赖**：Cobra v1.8.1、langsmith-go v0.25.6、tablewriter、treeprint、gojq
- **许可证**：MIT

## 解决的问题

在 LLM 应用开发中，LangSmith 平台收集了大量的 trace、run、评估数据。开发者和 AI 代理需要：

1. **快速查询**：在终端中快速查看 traces、runs、错误、延迟分布，无需打开浏览器。
2. **脚本化操作**：将数据查询、导出、evaluator 管理集成到 CI/CD 和自动化工作流中。
3. **Agent 集成**：让 AI 编码代理能够自主查询 observability 数据、管理评估规则、导出调试信息。

传统的 Web UI 无法满足这些场景，而直接调用 HTTP API 又需要处理认证、分页、版本兼容等复杂性。langsmith-cli 将这些能力封装为统一的命令行接口。

## 核心机制

### 命令树结构

CLI 以 `langsmith` 为根命令，下设 19 个功能命令组：

```
langsmith
├── project      # 追踪项目（session）列表与问题
├── trace        # Trace 查询、导出、层级树、setup
├── run          # 单个 Run 查询与导出
├── thread       # 多轮对话线程
├── dataset      # 评估数据集 CRUD
├── example      # 数据集示例管理
├── evaluator    # 在线/离线评估规则
├── experiment   # 评估实验结果
├── sandbox      # 沙箱管理（实验性）
├── insights     # 洞察分析
├── fleet         # Fleet 管理
├── hub          # Agent/Skill 仓库版本管理
├── apps         # 自定义应用
├── prompt       # Prompt Hub
├── auth         # 认证（login/info/token）
├── profile      # 多环境配置
├── workspace    # 工作区管理
├── update       # 自更新
└── api          # 通用 API 浏览器与请求工具
```

详见 CLI 命令体系。

### 双输出模式

每个命令都支持 `--format pretty`（默认，人类可读表格/树）和 `--format json`（机器可读 JSON），并统一通过 `-o/--output` 写入文件。写操作始终输出 JSON 状态对象，便于脚本和代理解析。

### 认证与配置

认证采用四级优先级链：flag → 环境变量 → profile 配置 → 默认值。支持 API Key 和 OAuth 2.0 设备码流两种方式，配置存储在 `~/.langsmith/config.json`（0600 权限）。详见 API 客户端架构。

### v1/v2 后端自动适配

CLI 在运行时自动检测 LangSmith 部署版本，透明地在 v1（传统查询 API）和 v2（SmithDB）之间切换，命令代码无需感知后端差异。

## 架构概览

```
langsmith-cli/
├── cmd/langsmith/main.go        # 入口，ldflags 注入版本信息
├── internal/
│   ├── cmd/                     # 所有 CLI 命令（Cobra）
│   │   ├── root.go              # 根命令、全局 flag、配置解析
│   │   ├── trace.go             # trace 命令组
│   │   ├── run.go               # run 命令组
│   │   ├── evaluator.go         # evaluator 命令组
│   │   ├── experiment.go        # experiment 命令组
│   │   ├── filters.go           # 通用过滤器与 DSL 构建
│   │   ├── helpers.go           # 查询、v1/v2 适配、数据提取
│   │   ├── auth.go / login.go   # OAuth 设备码认证
│   │   ├── api/                 # 通用 API 浏览与请求
│   │   └── ...                  # dataset/hub/sandbox/apps 等
│   ├── client/                  # LangSmith 客户端封装
│   │   ├── client.go            # SDK 包装、原始 HTTP、v2 探测
│   │   └── oauth.go             # OAuth 发现与元数据校验
│   ├── config/                  # 配置文件与 Profile 管理
│   ├── output/                  # JSON/JSONL/表格/树输出
│   ├── extract/                 # Run 数据归一化提取
│   ├── structured/              # 声明式命令框架
│   └── cmdutil/                 # 命令工具函数
└── scripts/                     # install.sh / install.ps1
```

## 快速开始

```bash
# 认证
export LANGSMITH_API_KEY="lsv2_pt_..."

# 列出项目
langsmith project list

# 查询最近 traces
langsmith trace list --project my-app --limit 5

# 查询 LLM calls
langsmith run list --project my-app --run-type llm --limit 10

# 列出数据集和实验
langsmith dataset list
langsmith experiment list --dataset my-eval-set

# JSON 输出供 jq/代理消费
langsmith --format json trace list --project my-app --limit 5
```

详见 基础使用示例 和 命令参考。

## 已知限制

1. 部分 v2 专属功能（trace messages、thread messages）在自托管 `< 0.16` 上不可用。
2. `--min-tokens` 过滤在客户端执行（服务端不支持 total_tokens 作为过滤属性）。
3. `trace setup` 仅支持 Claude Code 和 Codex 的配置写入。
4. Sandbox 功能标记为实验性。

## 进一步阅读

- CLI 命令体系 — 命令树结构、过滤器系统、输出模式
- API 客户端架构 — SDK 封装、v1/v2 适配、认证体系
- 命令参考 — 全部命令与标志详解
