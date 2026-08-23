---
type: bundle
okf_version: "0.2"
scope: openwiki
name: openwiki
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki——LangChain AI 开源的基于 DeepAgents 的代码库文档生成与维护 CLI，支持多 LLM provider、OAuth 连接器认证、ngrok 内网穿透、增量 wiki 更新与多语言翻译
---

# OpenWiki

**OpenWiki** 是 LangChain AI 开发的开源 CLI 工具，使用 DeepAgents 文档代理为代码库自动生成和维护 wiki 文档。它通过 LLM 代理读取源码、生成结构化文档，支持增量更新、多语言翻译、证据 Claims 验证，并内置 Slack/Gmail/X/Notion 等数据源的 OAuth 连接器认证。

- **版本**：0.3.3
- **许可证**：MIT
- **运行时**：Node.js >= 22，ESM 模块
- **核心依赖**：DeepAgents 1.12.0、LangChain 1.5、LangGraph、Ink 5（React TUI）、React 18
- **CLI 入口**：`openwiki`（`dist/cli/cli.js`）

## 核心特性

- **DeepAgents 文档代理**：基于 LangGraph 的代理图，组合文件系统后端、工具、中间件（翻译/Claims/index）、skills 和 review subagents，自动生成结构化 wiki。
- **三种命令模式**：`chat`（交互式对话，持久化 checkpoint）、`init`（首次生成）、`update`（增量更新，git head no-op 检测）。
- **13 种 LLM Provider**：OpenAI、Anthropic、Gemini（AI Studio + Vertex AI）、AWS Bedrock、OpenRouter、ChatGPT OAuth、OpenAI 兼容端点（Baseten/Fireworks/NVIDIA/Copilot/Nebius）。
- **OAuth 2.0 PKCE 连接器认证**：Slack、Gmail、X/Twitter、Notion，支持 RFC 7591 动态客户端注册和 RFC 9728 受保护资源元数据发现。
- **ngrok 内网穿透**：为 Slack 等要求 HTTPS 回调的 provider 自动桥接本地开发环境，支持预留域名和随机域名发现。
- **原子化环境变量管理**：`~/.openwiki/.env` 原子写入（临时文件 + rename），0o600 权限，shell 导出优先，凭证诊断脱敏。
- **双模式渲染**：TTY 环境使用 Ink React TUI，非 TTY/`--print` 使用纯文本输出，均通过同一 agent 入口。
- **Wiki 替换事务**：repository init 时备份旧 wiki，成功 commit、失败自动 rollback。
- **多语言支持**：翻译中间件在语言切换时重翻译所有页面，update 时重试待翻译页面。

## 支持的 LLM Provider

| Provider | 模型类 | 认证方式 |
|---|---|---|
| OpenAI | ChatOpenAI | API key |
| Anthropic | ChatAnthropic | API key |
| Gemini (AI Studio) | ChatGoogle | API key |
| Gemini Enterprise (Vertex) | ChatGoogle/AnthropicVertex/ChatOpenAI | ADC + GCP project |
| AWS Bedrock | ChatBedrockConverse | AWS SDK 凭证链 |
| ChatGPT | ChatOpenAI (Codex Responses API) | OAuth（浏览器登录） |
| OpenRouter | ChatOpenRouter | API key |
| OpenAI 兼容 | ChatOpenAI | API key + base URL |
| Baseten/Fireworks/NVIDIA/Copilot/Nebius | ChatOpenAI | API key + base URL |

## 快速开始

```bash
# 安装
npm install -g openwiki

# 配置 provider
export OPENAI_API_KEY="sk-..."

# 在代码库中初始化 wiki
openwiki init

# 增量更新
openwiki update

# 交互式对话
openwiki chat

# 非交互模式
openwiki update --print

# OAuth 连接器认证（Slack 需要 ngrok）
openwiki ngrok --url your-domain.ngrok.app
openwiki auth slack
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/openwiki/concepts/overview) — OpenWiki 是什么、解决什么问题、核心架构
- [Agent 系统](/ai/langchain-ai/openwiki/concepts/agent-system) — DeepAgent 图构建、命令模式、checkpoint 策略、中间件管道
- [Auth 与 CLI 认证体系](/ai/langchain-ai/openwiki/concepts/auth-cli) — OAuth PKCE、动态客户端注册、token 刷新、ngrok 内网穿透

### API 参考

- [Agent API](/ai/langchain-ai/openwiki/references/api) — runOpenWikiAgent、createModel、createAgentBackend、CLI runners 等
- [配置与环境变量](/ai/langchain-ai/openwiki/references/env-config) — .env 管理、凭证诊断、OAuth 与 provider 配置

### 使用示例

- [OAuth 认证与 ngrok 隧道](/ai/langchain-ai/openwiki/examples/oauth-ngrok) — 为 Slack 连接器配置本地 HTTPS 回调并完成 OAuth 授权

### 规格文档

- [事实清单](/ai/langchain-ai/openwiki/spec/facts) — 从源码提取的 76 条编号事实
- [架构洞察](/ai/langchain-ai/openwiki/spec/insights) — Agent-CLI 分层架构、OAuth+Token 管理、ngrok 内网穿透

## 架构概览

```
cli/cli.tsx (Shebang 入口, installCrashGuard)
    │
    ├── cli/startup.ts    ─ TTY/凭证/消息守卫
    ├── cli/runners.ts    ─ TUI/Print/Auth/Ngrok/Cron/Ingest/Visualize
    ├── cli/guards.ts     ─ isRecord/isDiagnosticValue 类型守卫
    ├── cli/debug.ts      ─ OPENWIKI_DEBUG 开关
    └── cli/format.ts     ─ exit/count/cwd/model 格式化
          │
          ▼
agent/index.ts
    ├── runOpenWikiAgent()    ─ 高层运行边界（环境/凭证/no-op/事务/元数据）
    ├── createOpenWikiAgent() ─ 低层图工厂
    ├── createModel()         ─ 13 种 provider 模型工厂
    ├── createAgentBackend()  ─ CompositeBackend（wiki + skills + history）
    └── resolveCheckpointTarget() ─ chat: SQLite, init/update: 内存
          │
          ▼
auth/                        config/env.ts
    ├── oauth.ts   (PKCE)        ├── loadOpenWikiEnv()
    ├── tokens.ts  (刷新)        ├── saveOpenWikiEnv() (原子写入)
    ├── ngrok.ts   (穿透)        └── MANAGED_ENV_KEYS (60+ 键)
    └── types.ts
```

## 关键设计决策

1. **两级 Agent API**：`runOpenWikiAgent` 拥有所有副作用（环境、凭证、事务、元数据），`createOpenWikiAgent` 是纯图组装，使 TUI 和 `--print` 复用同一 agent。
2. **命令差异化 Checkpoint**：chat 持久化 SQLite 支持多轮恢复，init/update 使用内存 checkpoint 避免状态污染，每次运行后清理历史。
3. **OAuth 与 LLM 认证分离**：连接器 OAuth（auth/ 模块）和 ChatGPT OAuth（agent/openai-chatgpt-oauth.ts）独立实现但共用 `.env` 持久化。
4. **ngrok 环境变量桥接**：ngrok 启动后将 HTTPS redirect URI 写入 `.env`，OAuth 流程自动读取，无需手动配置。
5. **Shell 优先的环境加载**：shell 导出的变量永远不会被 `.env` 文件覆盖，防止 CLI 保存意外遮蔽开发者的显式配置。

## 目录结构

```
openwiki/
├── spec/
│   ├── facts.md           # 源码事实验证清单（76 条）
│   └── insights.md        # 3 个架构深度洞察
├── concepts/
│   ├── index.md           # 概念索引
│   ├── overview.md        # 总览
│   ├── agent-system.md    # Agent 系统
│   └── auth-cli.md        # Auth 与 CLI 认证
├── references/
│   ├── index.md           # 参考索引
│   ├── api.md             # Agent API
│   └── env-config.md      # 配置与环境变量
├── examples/
│   ├── index.md           # 示例索引
│   └── oauth-ngrok.md     # OAuth + ngrok 示例
├── log.md                 # 生成日志
└── index.md               # 本文件
```
