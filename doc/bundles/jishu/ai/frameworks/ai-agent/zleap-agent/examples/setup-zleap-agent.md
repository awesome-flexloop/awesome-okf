---
okf_version: "0.2"
type: example
title: 安装配置 Zleap Agent
description: 使用 pnpm 安装 Zleap Agent，配置 PostgreSQL+pgvector 数据库，初始化 LLM 模型连接，启动 CLI 对话和 Web 服务
tags: [zleap-agent, example, setup, install, pnpm, postgres, configuration, cli]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/workspace-pipeline.md
  - /concepts/gateway-multi-platform.md
  - /concepts/pg-boss-task-queue.md
sources:
  - id: zleap-agent-self
    resource: /references/zleap-agent-sources.md
    title: Zleap-Agent 源码参考
---

# 安装配置 Zleap Agent

## 场景说明

本示例演示如何从零开始安装和配置 Zleap Agent，包括：使用 pnpm 安装依赖、启动 PostgreSQL+pgvector 数据库、配置 LLM 模型连接参数、初始化运行时环境，以及通过 CLI 和 Web 界面启动对话。这是使用 Zleap Agent 的第一步。

**前置条件**：
- Node.js ≥ 22（Zleap 使用 `node:22-bookworm` 作为 Docker 基础镜像）
- pnpm ≥ 9.15.0（项目通过 `packageManager` 字段锁定版本）
- Docker 和 Docker Compose（用于本地 PostgreSQL+pgvector 数据库）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务（OpenAI、DeepSeek、本地 Ollama 等）

## 完整代码示例

### 步骤 1：克隆项目并安装依赖

```bash
# 克隆仓库
git clone https://github.com/zleap-ai/Zleap-Agent.git
cd Zleap-Agent

# 启用 corepack（pnpm 版本管理器）
corepack enable

# 安装所有依赖
pnpm install

# 构建所有包
pnpm build
```

### 步骤 2：启动 PostgreSQL + pgvector 数据库

Zleap Agent 使用 PostgreSQL 配合 pgvector 扩展来存储对话记忆、任务队列和向量嵌入。项目根目录提供了 `docker-compose.yml`：

```bash
# 启动 PostgreSQL 数据库（端口 5433）
docker compose up -d postgres

# 等待数据库就绪（healthcheck 通过后继续）
docker compose ps postgres
# 预期输出: zleap-postgres   Up (healthy)
```

数据库默认连接信息：
- 主机：`127.0.0.1`
- 端口：`5433`（宿主机映射，容器内为 5432）
- 用户名：`zleap`
- 密码：`zleap`
- 数据库：`zleap`
- 连接字符串：`postgres://zleap:zleap@127.0.0.1:5433/zleap`

### 步骤 3：配置环境变量

复制 `.env.example` 到 `.env.local` 并编辑：

```bash
# 复制环境变量模板
cp .env.example .env.local
```

编辑 `.env.local`，填写 LLM 模型配置：

```bash
# .env.local — Zleap Agent 本地配置

# --- LLM（必须配置，否则无法对话）---
ZLEAP_MODEL_BASE_URL=https://api.deepseek.com/v1
ZLEAP_MODEL_API_KEY=sk-your-api-key-here
ZLEAP_MODEL_NAME=deepseek-chat

# --- 数据库（可选 — 使用 docker-compose 时默认即可）---
ZLEAP_DATABASE_URL=postgres://zleap:zleap@127.0.0.1:5433/zleap

# --- Embeddings（可选 — 未配置时使用 faux embedding）---
# ZLEAP_EMBED_MODEL=text-embedding-3-small
# ZLEAP_EMBED_BASE_URL=https://api.openai.com/v1
# ZLEAP_EMBED_API_KEY=sk-your-key
# ZLEAP_EMBED_DIM=1536

# --- 本地服务配置 ---
ZLEAP_WEB_PORT=3000
ZLEAP_SERVE_MODE=production
```

### 步骤 4：运行初始化向导

```bash
# 从环境变量导入配置并完成初始化
pnpm cli init --fromEnv
```

初始化向导会自动完成：
1. 检测数据库连接（从 `ZLEAP_DATABASE_URL` 读取）
2. 检测模型配置（从 `ZLEAP_MODEL_*` 读取）
3. 写入配置文件到 `~/.zleap/config.json`
4. 运行环境健康检查（`zleap doctor`）

### 步骤 5：环境健康检查

```bash
pnpm cli doctor
```

`doctor` 命令会检查以下关键项：
- Node.js 版本是否 ≥ 22
- pnpm 是否可用
- 数据库连接是否正常
- 模型 API 是否可达
- 配置文件是否有效

### 步骤 6：启动 CLI 对话

```bash
# 进入交互式 TUI 对话界面
pnpm cli
```

启动后可以直接在终端与 Agent 对话，支持：
- 多轮对话上下文
- 工具调用（文件读写、终端命令、Web 搜索等）
- Workspace 自动路由
- 命令面板（`Ctrl+K` 或 `/` 前缀触发）

### 步骤 7：启动 Web 服务

```bash
# 启动 Web UI 服务（开发模式）
pnpm dev:web

# 或启动生产模式服务
pnpm serve
```

Web UI 默认地址：`http://localhost:3000`（开发模式）或 `http://localhost:4789`（生产模式）。

### 步骤 8（可选）：一键 Docker Compose 完整启动

```bash
# 启动 PostgreSQL + Web 服务 + 任务 Worker + IM 网关
docker compose --profile worker --profile gateway up -d

# 仅启动数据库和 Web UI
docker compose up -d
pnpm dev:web
```

## 逐步解释

### 1. 项目结构与包管理

Zleap Agent 是一个 monorepo 项目，使用 pnpm workspaces 管理多个子包：

| 包名 | 路径 | 功能 |
|---|---|---|
| `@zleap/core` | `packages/core/` | 核心类型定义、Agent/Workspace/Tool 抽象 |
| `@zleap/ai` | `packages/ai/` | LLM Provider 抽象层（OpenAI/Anthropic/SSE） |
| `@zleap/agent` | `packages/agent/` | Agent 运行时引擎、对话循环、Workspace 执行 |
| `@zleap/host` | `packages/host/` | 运行时宿主环境、安装/布局/PostgreSQL 管理 |
| `@zleap/store` | `packages/store/` | PostgreSQL 持久化层、向量记忆、迁移 |
| `@zleap/gateway` | `packages/gateway/` | IM 网关（飞书/微信/飞书CLI） |
| `@zleap/tasks` | `packages/tasks/` | 定时任务调度（基于 pg-boss） |
| `@zleap/cli` | `packages/cli/` | 命令行界面（TUI 对话 + 管理命令） |
| `@zleap/web` | `packages/web/` | Next.js Web 管理界面 |
| `@zleap/avatar` | `packages/avatar/` | 入站运行组装（IM/定时/WebChat） |
| `@zleap/runtime` | `packages/runtime/` | 运行时组合层 |

`pnpm build` 命令会递归构建所有包（`pnpm -r --filter "./packages/*" build`）。

### 2. 数据库配置

默认数据库 URL 常量定义在 `@zleap/host` 包中：

```typescript
// packages/host/src/constants.ts
export const DEFAULT_DATABASE_URL = 'postgres://zleap:zleap@127.0.0.1:5433/zleap';
```

配置解析优先级（由高到低）：
1. 环境变量 `ZLEAP_DATABASE_URL`
2. 环境变量 `DATABASE_URL`
3. 配置文件 `~/.zleap/config.json` 中的 `database.url`
4. 默认值 `postgres://zleap:zleap@127.0.0.1:5433/zleap`

### 3. 模型配置

模型配置通过 `CustomModelConfig` 类型管理，支持任意 OpenAI 兼容 API：

```typescript
// packages/ai/src/types.ts 中的 CustomModelConfig 结构
type CustomModelConfig = {
  baseUrl: string;       // API 基础 URL，如 https://api.deepseek.com/v1
  apiKey: string;        // API 密钥
  model: string;         // 模型名称，如 deepseek-chat
  displayName?: string;  // 显示名称
  protocol?: string;     // 协议类型
};
```

模型向导 `runModelWizardReadline()` 会交互式引导用户配置：
- API Base URL
- API Key
- 模型名称
- 连接测试

### 4. CLI 命令

`pnpm cli` 实际上运行 `@zleap-ai/cli` 包的 `start` 命令，支持以下子命令：

| 命令 | 功能 |
|---|---|
| `zleap` (无参数) | 进入 TUI 对话界面 |
| `zleap init [--fromEnv] [--force]` | 初始化配置向导 |
| `zleap setup` | 浏览器引导式设置流程 |
| `zleap doctor` | 环境健康检查 |
| `zleap serve [--gateway]` | 启动服务（Web + 可选网关） |
| `zleap config [get/set/list]` | 管理配置 |
| `zleap channels [connect/disconnect/list]` | 管理 IM 渠道连接 |
| `zleap sessions [list/clear]` | 管理会话历史 |
| `zleap models [list/test]` | 管理模型配置 |
| `zleap stop` | 停止后台服务 |
| `zleap update` | 更新到最新版本 |

### 5. 配置文件

配置文件存储在 `~/.zleap/config.json`，结构为：

```json
{
  "model": {
    "baseUrl": "https://api.deepseek.com/v1",
    "apiKey": "sk-***",
    "model": "deepseek-chat",
    "displayName": "DeepSeek Chat"
  },
  "database": {
    "url": "postgres://zleap:zleap@127.0.0.1:5433/zleap"
  },
  "onboarded": true,
  "session": {
    "runMode": "interactive",
    "permissionMode": "request_approval"
  }
}
```

配置也可以通过环境变量覆盖，环境变量与配置路径的映射：

| 环境变量 | 配置路径 |
|---|---|
| `ZLEAP_DATABASE_URL` | `database.url` |
| `ZLEAP_MODEL_BASE_URL` | `model.baseUrl` |
| `ZLEAP_MODEL_API_KEY` | `model.apiKey` |
| `ZLEAP_MODEL_NAME` | `model.model` |
| `ZLEAP_EMBED_MODEL` | `embedding.model` |
| `ZLEAP_EMBED_DIM` | `embedding.dimension` |

## 输出结果

成功安装配置后，CLI 启动界面如下：

```
🦅 Zleap Agent v0.3.3

✓ 数据库已连接: postgres://zleap:***@127.0.0.1:5433/zleap
✓ 模型已配置: DeepSeek Chat (deepseek-chat)
✓ 运行时已就绪

输入消息开始对话，或按 Ctrl+K 打开命令面板。

> █
```

Web UI 启动后访问 `http://localhost:3000`，可以看到：
- 左侧对话历史列表
- 中央对话区域（支持 Markdown 渲染、工具调用卡片）
- 右侧设置面板（模型选择、Workspace 管理、IM 渠道配置）
- 顶部状态栏（连接状态、模型信息）

`pnpm cli doctor` 输出示例：

```
✓ Node.js v22.x.x
✓ pnpm 9.15.0
✓ 数据库连接正常 (pgvector 扩展已安装)
✓ 模型 API 可达
✓ 配置文件有效 (~/.zleap/config.json)
✓ 数据库迁移已完成

环境检查通过，Zleap Agent 可以正常使用。
```

## 注意事项

1. **数据库必须是 pgvector/pg16 镜像**：Zleap 的记忆功能依赖 pgvector 扩展进行向量相似度搜索，普通 PostgreSQL 镜像不包含此扩展。docker-compose.yml 中已指定 `pgvector/pgvector:pg16`。

2. **数据库端口映射**：宿主机端口为 5433（而非默认的 5432），这是为了避免与本地可能已有的 PostgreSQL 实例冲突。容器内端口仍为 5432。

3. **corepack enable**：首次使用 pnpm 前需运行 `corepack enable`，这会自动安装并激活 `packageManager` 字段指定的 pnpm 版本（9.15.0）。

4. **构建顺序**：`pnpm dev:web` 和 `pnpm serve` 等命令都依赖 `@zleap/agent` 和 `@zleap/host` 先构建完成。首次运行或代码变更后，需先执行 `pnpm build`。

5. **API Key 安全**：`~/.zleap/config.json` 中存储了 API Key，确保该文件权限正确（建议 `chmod 600 ~/.zleap/config.json`）。不要将 `.env.local` 或 `config.json` 提交到版本控制。

6. **faux embedding**：如果未配置 Embedding 模型，Zleap 会使用 faux（伪）embedding，这意味着记忆检索功能可能不准确。生产环境建议配置真实的 Embedding 模型。

7. **Windows/WSL2 支持**：Zleap Agent 的 Docker 镜像基于 Linux，Windows 用户需通过 WSL2 运行。数据库使用 Docker Desktop for Windows 即可。

8. **端口冲突**：如果 3000/4789 端口被占用，可以通过 `ZLEAP_WEB_PORT` 环境变量指定其他端口。
