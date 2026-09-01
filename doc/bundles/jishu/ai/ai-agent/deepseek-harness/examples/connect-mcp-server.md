---
type: Example
title: 连接 MCP 服务器
description: 学习如何在 DeepSeek Harness 中配置和使用 MCP（Model Context Protocol）客户端，通过 stdio 或 HTTP 连接外部 MCP 服务器并使用其提供的工具。
tags:
  - mcp
  - mcp-client
  - stdio
  - streamable-http
  - tool-discovery
  - namespace
related:
  - create-cordis-plugin
  - define-custom-tool
  - build-agent-loop
sources:
  - packages/mcp/mcp-client/src/index.ts
  - packages/mcp/mcp-client/src/tools.ts
  - packages/mcp/mcp-client/src/connection.ts
  - examples/acp-agent/cordis.yml
---

# 连接 MCP 服务器

## 场景说明

MCP（Model Context Protocol）是一个开放协议，允许 AI 模型通过标准化接口访问外部工具和资源。DeepSeek Harness 通过 `@deepseek-ai/dsh-mcp-client` 插件提供 MCP 客户端能力，可以连接本地（stdio）或远程（Streamable HTTP/SSE）MCP 服务器，并自动将服务器提供的工具注册到工具注册表中，模型可以像使用内置工具一样调用远程 MCP 工具。本示例演示：

- MCP 客户端插件的两种传输方式：stdio 和 streamable-http
- `cordis.yml` 中的 MCP 配置方法
- 工具命名空间（`mcp__<serverName>__<toolName>`）
- 连接生命周期管理、自动重连和启动失败处理
- 同时连接多个 MCP 服务器
- 编程方式（TypeScript）连接 MCP 服务器

## 完整代码示例

### 方式一：通过 cordis.yml 配置（推荐）

在 `cordis.yml` 中添加 MCP 客户端插件条目。以下配置演示连接三个不同的 MCP 服务器：

```yaml
# cordis.yml

# ---- 基础插件（LLM、沙箱等）----
- id: llm-deepseek
  name: '@deepseek-ai/dsh-llm-deepseek'
  config:
    thinking: enabled
    reasoningEffort: medium
    models:
      - id: deepseek-v4-flash

- id: sandbox
  name: '@deepseek-ai/dsh-sandbox-local'
- id: sandbox-policy
  name: '@deepseek-ai/dsh-sandbox-policy'
  config:
    mode: workspace-write
    workspaceRoot: !!js process.cwd()

- id: subprocess
  name: '@deepseek-ai/dsh-subprocess-local'
- id: bash
  name: '@deepseek-ai/dsh-bash-sandbox'
  config:
    timeoutMs: 60000

- id: fs-sandbox
  name: '@deepseek-ai/dsh-fs-sandbox'
  config:
    cwd: !!js process.cwd()
- id: tool-fs
  name: '@deepseek-ai/dsh-tool-fs'

# ---- MCP 服务器 1：通过 stdio 连接本地文件系统 MCP 服务器 ----
- id: mcp-filesystem
  name: '@deepseek-ai/dsh-mcp-client'
  config:
    # 使用 stdio 传输：启动一个子进程通过标准输入输出通信
    transport: stdio
    # serverName 是本地命名空间，用于隔离不同 MCP 服务器的工具名
    # 必须匹配 [A-Za-z0-9_-]{1,32}，同一应用中唯一
    serverName: filesystem
    # 要执行的命令（通常是 npx、uvx 或本地可执行文件路径）
    command: npx
    # 命令行参数，直接传递不经过 shell 解析
    args:
      - '-y'
      - '@modelcontextprotocol/server-filesystem'
      - !!js process.cwd()  # 允许访问当前工作目录
    # 额外环境变量，合并到清理后的环境变量之上
    env: {}
    # 子进程工作目录
    cwd: !!js process.cwd()
    # 单次工具调用超时（毫秒）
    toolCallTimeoutMs: 60000
    # 启动时连接/工具同步失败是否导致插件激活失败
    failOnStartupError: true
    # 自动重连策略（省略则使用默认值）
    reconnect:
      enabled: true
      initialDelayMs: 1000
      maxDelayMs: 30000
      maxAttempts: 10

# ---- MCP 服务器 2：通过 stdio 连接 GitHub MCP 服务器 ----
- id: mcp-github
  name: '@deepseek-ai/dsh-mcp-client'
  config:
    transport: stdio
    serverName: github
    command: npx
    args:
      - '-y'
      - '@modelcontextprotocol/server-github'
    env:
      # 通过环境变量传递 GitHub Token（从 .env 文件加载）
      GITHUB_PERSONAL_ACCESS_TOKEN: !!js "process.env.GITHUB_TOKEN ?? ''"
    cwd: !!js process.cwd()
    toolCallTimeoutMs: 30000
    failOnStartupError: false  # GitHub 服务器可选，启动失败不影响主应用
    reconnect:
      enabled: true
      initialDelayMs: 2000
      maxDelayMs: 60000
      maxAttempts: 5

# ---- MCP 服务器 3：通过 Streamable HTTP 连接远程 MCP 服务器 ----
- id: mcp-remote
  name: '@deepseek-ai/dsh-mcp-client'
  config:
    # 使用 HTTP/SSE 传输：连接到远程 MCP 端点
    transport: streamable-http
    serverName: remote-search
    # MCP 端点 URL
    url: 'https://mcp.example.com/search'
    # 附加到 MCP 请求的 HTTP 头（用于认证等）
    headers:
      Authorization: !!js "`Bearer ${process.env.MCP_API_KEY ?? ''}`"
    toolCallTimeoutMs: 30000
    failOnStartupError: false
    reconnect:
      enabled: true
      initialDelayMs: 1000
      maxDelayMs: 15000
      maxAttempts: 20

# ---- Agent 核心 ----
- id: acp-agent
  name: '@deepseek-ai/dsh-acp-demo'
  config:
    provider: deepseek-official
    model: deepseek-v4-flash
    persistenceRoot: './.sessions'
    persona: |
      You are a helpful coding assistant. You have access to filesystem tools via MCP,
      GitHub tools via MCP, and built-in bash/fs tools. Use the appropriate tool for each task.
```

确保 `.env` 文件包含所需的认证信息：

```env
# .env（不要提交到版本控制！）
GITHUB_TOKEN=ghp_your_github_personal_access_token_here
MCP_API_KEY=your_remote_mcp_api_key_here
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
```

### 方式二：编程方式连接（TypeScript 插件内）

```typescript
/**
 * 在自定义 Cordis 插件中编程式连接 MCP 服务器。
 * @module my-mcp-bridge
 */

import type { Context } from '@deepseek-ai/cordis'
import { apply as applyMcpClient } from '@deepseek-ai/dsh-mcp-client'
import type { Config as McpConfig } from '@deepseek-ai/dsh-mcp-client'

export const name = 'my-mcp-bridge'
export const inject = ['tools']  // mcp-client 依赖 tools 服务

export function apply(ctx: Context): void {
  // 动态连接一个 stdio MCP 服务器
  // 注意：applyMcpClient 是异步的，在 effect 中处理
  ctx.effect(() => {
    let disposed = false
    const cleanupFns: Array<() => void | Promise<void>> = []

    const config: McpConfig = {
      transport: 'stdio',
      serverName: 'dynamic-math',
      command: 'python',
      args: ['-m', 'mcp_server_math'],
      env: {},
      cwd: process.cwd(),
      toolCallTimeoutMs: 30000,
      failOnStartupError: false,
      reconnect: {
        enabled: true,
        initialDelayMs: 1000,
        maxDelayMs: 30000,
        maxAttempts: 5,
      },
    }

    // 异步应用 MCP 客户端插件
    // 注意：直接调用 apply 函数而非通过 Loader，适合动态场景
    applyMcpClient(ctx, config).then(() => {
      if (disposed) return
      ctx.logger.info('my-mcp-bridge: dynamic math MCP server connected')
    }).catch((error: Error) => {
      ctx.logger.warn(`my-mcp-bridge: math MCP connection failed: ${error.message}`)
    })

    // 清理函数
    return () => {
      disposed = true
      for (const fn of cleanupFns) {
        void fn()
      }
    }
  }, 'my-mcp-bridge.dynamic')
}
```

## 逐步解释

### 1. 传输方式对比

| 特性 | stdio | streamable-http |
|------|-------|-----------------|
| 用途 | 本地子进程（npx/uvx/本地命令） | 远程 HTTP 端点 |
| 配置字段 | `command`, `args`, `env`, `cwd` | `url`, `headers` |
| 进程管理 | Harness 启动并管理子进程生命周期 | 无进程管理，纯 HTTP 通信 |
| 认证 | 通过 `env` 传递 Token | 通过 `headers` 传递 Authorization |
| 典型场景 | filesystem、github、brave-search 等官方 MCP 服务器 | 自部署的远程 MCP 服务 |

### 2. serverName 与工具命名空间

每个 MCP 客户端实例需要唯一的 `serverName`，用于：
- **工具名隔离**：MCP 服务器提供的工具注册为 `mcp__<serverName>__<rawToolName>`
  - 例如，`filesystem` 服务器的 `read_file` 工具注册为 `mcp__filesystem__read_file`
  - `github` 服务器的 `search_repositories` 注册为 `mcp__github__search_repositories`
- **重复检测**：同一 `serverName` 的第二个实例在加载时会立即报错
- **资源释放**：插件卸载时，`serverName` 命名空间自动释放

工具名模式 `/^[A-Za-z0-9_-]{1,32}$/` 确保名称在工具注册表中合法且可读。

### 3. 连接生命周期与重连策略

MCP 客户端插件在 `apply` 函数中执行以下步骤：

1. **重连策略解析**：验证 `reconnect` 配置（`initialDelayMs`、`maxDelayMs`、`maxAttempts`）
2. **命名空间预留**：通过 `ctx.effect()` 注册 `serverName`，重复则立即失败
3. **启动连接**：创建子进程或 HTTP 连接，执行 MCP 握手
4. **工具发现**：连接建立后调用 MCP `tools/list`，将所有工具注册到 `ctx.tools`
5. **等待就绪**：`await connection.ready` 确保初始工具同步完成
6. **激活决策**：
   - `failOnStartupError: true`：初始连接失败 → 插件激活失败（Cordis 回滚）
   - `failOnStartupError: false`：初始失败仅记录日志，进入后台重连循环

重连策略字段（`ReconnectConfig`）：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `enabled` | `true` | 是否启用自动重连 |
| `initialDelayMs` | `1000` | 首次重连等待时间（毫秒） |
| `maxDelayMs` | `30000` | 重连最大等待时间（指数退避上限） |
| `maxAttempts` | `Number.MAX_SAFE_INTEGER` | 最大重连次数 |

连接断开时，插件自动：
1. 注销当前连接的所有工具
2. 按指数退避等待后重连
3. 重连成功后重新发现并注册工具
4. 触发 `tools/change` 事件通知 Agent 刷新工具列表

### 4. 多服务器配置要点

配置多个 MCP 服务器时：
- **每个服务器一个插件条目**：每个 `- id: mcp-xxx` 条目都是独立的 mcp-client 实例
- **serverName 必须唯一**：不同服务器使用不同的 serverName（如 `filesystem`、`github`、`remote-search`）
- **id 仅用于 Cordis 条目标识**：YAML 中的 `id` 是本地条目标识，不影响工具名
- **按需设置 failOnStartupError**：核心服务（如 filesystem）设为 `true`（启动失败则不启动），可选服务设为 `false`（启动失败进入重连）

### 5. 工具调用超时

`toolCallTimeoutMs` 设置单次 MCP 工具调用的超时时间：
- 默认值：60000ms（60 秒）
- 超时通过 AbortSignal 传递给 MCP 传输层
- MCP 协议本身支持取消（`cancelled` 通知）
- 模型会收到超时错误，可以决定重试或换用其他方式

### 6. 环境变量安全

stdio 模式下，子进程的环境变量是**清理后的**（scrubbed ambient env）加上 `config.env`：
- 敏感信息（API Key）通过 `env` 字段传入，不要硬编码在 YAML 中
- 使用 `!!js process.env.XXX` 从进程环境读取（由 `.env` 文件或 shell 环境设置）
- 子进程 `cwd` 默认为空字符串（继承父进程 cwd），建议显式设置

## 输出结果

启动应用后，观察 MCP 连接日志：

```
[mcp-client(filesystem)] connecting to stdio: npx -y @modelcontextprotocol/server-filesystem ...
[mcp-client(filesystem)] connected, discovered 8 tools
[mcp-client(github)] connecting to stdio: npx -y @modelcontextprotocol/server-github ...
[mcp-client(github)] connected, discovered 15 tools
[mcp-client(remote-search)] connecting to http: https://mcp.example.com/search ...
[mcp-client(remote-search)] connected, discovered 3 tools
[tools] registered mcp__filesystem__read_file
[tools] registered mcp__filesystem__write_file
[tools] registered mcp__filesystem__list_directory
[tools] registered mcp__github__search_repositories
[tools] registered mcp__github__create_issue
[tools] registered mcp__remote-search__web_search
# ... Agent 就绪
```

模型与 MCP 工具的交互示例：

```
[用户] List files in the current directory and check if there are any open issues on the repo
[模型] I'll list the directory and check GitHub issues.

       Call tool: mcp__filesystem__list_directory
       args: { path: "." }
       → [MCP filesystem] directory listing: ...

       Call tool: mcp__github__list_issues
       args: { repo: "owner/repo", state: "open" }
       → [MCP github] 3 open issues: ...
```

模型**无需知道**工具来自 MCP——它通过统一的工具注册表看到所有工具，MCP 工具和内置工具在模型视角完全一致。

## 注意事项

1. **serverName 唯一性**：同一进程中（同一 `ctx.root`）的 `serverName` 不能重复。重复会抛出明确错误：`mcp-client: serverName "xxx" is already in use`。多应用测试场景通过 WeakMap 按 `ctx.root` 隔离命名空间。

2. **npx/uvx 首次启动延迟**：使用 `npx -y` 或 `uvx` 启动 MCP 服务器时，首次运行需要下载包，可能较慢。建议提前全局安装或配置 `failOnStartupError: false` 以避免启动阻塞。

3. **环境变量清理**：stdio 子进程的环境变量不是完全继承父进程，而是经过清理（scrubbed）后只保留必要变量加上 `config.env`。不要假设所有父进程环境变量都可用。

4. **HMR 热更新**：MCP 客户端插件支持 HMR——配置变更时旧实例被 dispose（断开连接、注销工具、释放命名空间），新实例创建（重连、重新发现工具）。相同 `serverName` 的热更新会产生完全相同的公开工具名。

5. **工具数量上限**：每个 MCP 服务器暴露的工具数量理论上无上限，但过多工具会增加模型的 prompt 长度和选择难度。建议按需连接 MCP 服务器。

6. **资源（Resources）支持**：当前 dsh-mcp-client 主要支持工具（tools）发现和调用。MCP 资源（resources）和提示（prompts）功能请查阅最新版本文档确认支持状态。

7. **stdio 参数安全**：`args` 数组直接传递给子进程，**不经过 shell 解析**，因此不会有 shell 注入风险。但应避免在 args 中包含用户可控的未转义内容。

8. **HTTP 头安全**：`headers` 中的认证信息（如 API Key）会随每个 MCP 请求发送。仅连接可信的 MCP 端点，避免将认证信息发送到未知服务器。

9. **failOnStartupError 的选择**：
   - 核心依赖（如 filesystem）→ `true`：确保工具可用后再启动
   - 可选增强（如 github、search）→ `false`：服务不可用时降级运行
   - 开发调试 → `false`：避免临时网络问题阻塞开发
