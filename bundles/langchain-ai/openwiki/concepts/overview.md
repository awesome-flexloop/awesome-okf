---
type: concept
scope: openwiki
name: overview
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki 总览——基于 DeepAgents 的代码库文档生成与维护 CLI
---

# OpenWiki 总览

## 什么是 OpenWiki

OpenWiki 是 LangChain AI 开发的开源 CLI 工具，使用 DeepAgents 文档代理为代码库自动生成和维护 wiki 文档。它通过 LLM 代理读取源码、生成结构化文档，并支持增量更新、多语言翻译、证据 Claims 验证等能力。

- **版本**：0.3.3
- **许可证**：MIT
- **运行时**：Node.js >= 22，ESM 模块
- **CLI 入口**：`openwiki`（`dist/cli/cli.js`）
- **核心框架**：DeepAgents 1.12.0、LangChain 1.5、LangGraph、Ink（React TUI）

## 解决的问题

大型代码库的文档维护面临三个核心挑战：

1. **文档滞后**：代码频繁变更，人工文档难以同步，wiki 逐渐过时。
2. **上下文丢失**：新开发者难以从代码 alone 理解架构意图和领域概念。
3. **多源证据**：文档中的断言需要可追溯到代码证据，避免 LLM 幻觉。

OpenWiki 通过 AI 代理自动化文档生成与更新流程，并以 git head 为基准做增量 no-op 检测，避免不必要的 LLM 调用。

## 三种命令模式

OpenWiki 支持三种命令（见 [Agent 系统](/langchain-ai/openwiki/concepts/agent-system)）：

| 命令 | 用途 | Checkpoint | 输出模式 |
|---|---|---|---|
| `chat` | 交互式对话，不修改 wiki | SQLite 持久化 | local-wiki / repository |
| `init` | 首次生成完整 wiki | 内存 | local-wiki / repository |
| `update` | 增量更新已有 wiki | 内存 | local-wiki / repository |

两种输出模式：
- **local-wiki**：文档输出到当前工作目录，元数据存 `.last-update.json`。
- **repository**：文档输出到 `openwiki/` 子目录，元数据存 `openwiki/.last-update.json`，支持 git head 追踪。

## 核心架构

```
用户 CLI 命令 (cli.tsx)
        │
        ▼
┌─────────────────────────┐
│  Startup Guards         │ ← TTY 检查、凭证检查、消息校验
│  (startup.ts)           │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  Runner (runners.ts)    │ ← TUI (Ink) / Print / Auth / Ngrok
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  runOpenWikiAgent       │ ← 环境加载、no-op 检测、provider 解析
│  (agent/index.ts)       │   wiki 替换事务、元数据持久化
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  createOpenWikiAgent    │ ← DeepAgent 图工厂
│  (agent/index.ts)       │   tools + backend + middleware + skills
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  LangChain Chat Model   │ ← 13 种 provider（OpenAI/Anthropic/
│  (createModel)          │   Gemini/Bedrock/OpenRouter/...）
└─────────────────────────┘
```

## 多 Provider 支持

OpenWiki 通过 `createModel` 工厂支持 13 种 LLM provider（详见 [API 参考](/langchain-ai/openwiki/references/api)）：

- **API key 类**：OpenAI、Anthropic、Gemini（AI Studio）、OpenRouter、Baseten、Fireworks、NVIDIA、Copilot、Nebius、OpenAI 兼容端点
- **OAuth 类**：ChatGPT（Codex Responses API，浏览器登录）
- **云 SDK 类**：AWS Bedrock（SDK 凭证链）、Gemini Enterprise（Vertex AI ADC）

Vertex AI 进一步根据模型 ID 路由到三种 surface：原生 Gemini（ChatGoogle gcp）、Anthropic on Vertex（AnthropicVertex SDK 桥接）、OpenAI 兼容 MaaS（fetch wrapper 注入 ADC token）。

## 认证与连接器

除 LLM provider 认证外，OpenWiki 还为数据源连接器实现了独立的 OAuth 体系（详见 [Auth 与 CLI 认证体系](/langchain-ai/openwiki/concepts/auth-cli)）：

- **OAuth 连接器**：Slack、Gmail、X/Twitter、Notion（支持 PKCE 和动态客户端注册）
- **ngrok 内网穿透**：为 Slack 等要求 HTTPS 回调的 provider 桥接本地开发环境
- **外部 CLI 认证**：支持通过云厂商 CLI 获取临时凭证

## 环境与配置

所有配置通过 `~/.openwiki/.env` 文件管理（见 [配置与环境变量](/langchain-ai/openwiki/references/env-config)）：

- `loadOpenWikiEnv()` 加载时 shell 环境变量优先于文件值。
- `saveOpenWikiEnv()` 使用原子写入（临时文件 + rename），文件权限 0o600。
- `MANAGED_ENV_KEYS` 是所有受管环境变量的唯一真相源（60+ 键）。
- 凭证诊断面板对密钥做脱敏（前6后4），对 URL 去除认证信息。

## 文档导航

### 核心概念

- [总览](/langchain-ai/openwiki/concepts/overview) — 本页
- [Agent 系统](/langchain-ai/openwiki/concepts/agent-system) — DeepAgent 图构建、命令模式、checkpoint、中间件
- [Auth 与 CLI 认证体系](/langchain-ai/openwiki/concepts/auth-cli) — OAuth PKCE、token 刷新、ngrok 穿透

### API 参考

- [Agent API](/langchain-ai/openwiki/references/api) — runOpenWikiAgent、createModel、createAgentBackend 等
- [配置与环境变量](/langchain-ai/openwiki/references/env-config) — .env 管理、凭证诊断、provider 配置

### 使用示例

- [OAuth 认证与 ngrok 隧道](/langchain-ai/openwiki/examples/oauth-ngrok) — 配置 Slack OAuth、启动 ngrok、运行认证流程

## 目录结构

```
openwiki/
├── spec/
│   ├── facts.md           # 源码事实验证清单（76 条）
│   └── insights.md        # 3 个架构深度洞察
├── concepts/              # 核心概念（3 篇）
├── references/            # API/技术参考（2 篇）
├── examples/              # 使用示例（1 篇）
└── index.md               # 本文件
```

## 进一步阅读

- [Agent 系统](/langchain-ai/openwiki/concepts/agent-system)
- [Auth 与 CLI 认证体系](/langchain-ai/openwiki/concepts/auth-cli)
- [API 参考](/langchain-ai/openwiki/references/api)
