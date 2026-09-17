---
okf_version: "0.2"
type: Example
title: "实战：接入 Coding Agent、MCP 配置与 ov CLI"
description: "把自部署 OpenViking 接给 Claude Code/Codex/Cursor/TRAE（安装脚本+Hooks）、手动配置 MCP 端点，以及用 ov CLI/SDK 操作 viking:// 的完整方法"
tags: [OpenViking, Claude Code, Codex, Cursor, TRAE, MCP, Hooks, ov CLI, SDK]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/OFS4DzgTEcEgzNHyvRVD0g
  - id: docs-mcp
    url: https://docs.openviking.ai/en/guides/06-mcp-integration
  - id: docs-trae
    url: https://docs.openviking.ai/en/agent-integrations/13-trae/llms.txt
  - id: docs-deploy
    url: https://docs.openviking.ai/en/guides/03-deployment
---

# 实战：接入 Coding Agent、MCP 配置与 ov CLI

> 前置：已有一台运行中的 OpenViking Server（[实战 00](00-docker-server-deployment.md)），并拿到某用户的 **用户 API 密钥**。本篇对应博文"AI Agent 支持"段（F-029/F-030）并补齐官方完整接线方式。下文示例地址 `192.168.3.101` 沿用实战 00 的博文示例机 IP，照做时替换为你自己的服务器地址。

## 接入方式总览

| 方式 | 适合谁 | 是否自动记忆 |
|------|--------|-------------|
| 官方安装脚本（Hooks + MCP） | Claude Code / Codex / Cursor / TRAE 等日常 Coding Agent | ✅ 会话自动召回 + 自动捕获提交 |
| 手动 MCP 配置 | 任意标准 MCP 客户端（Manus、自写客户端等） | ❌ 需显式调用工具 |
| OpenClaw / Hermes 专用集成 | 对应用户 | Context engine / 内置 |
| SDK / HTTP API | 自研应用 | 自行控制 |

## 方式一：安装脚本（推荐，博文"三步法"的完整版）

博文口径：启动 Server → 跑一条安装脚本 → 重启客户端（F-030）。官方统一脚本（F-041）：

```bash
# 交互式（询问要接哪个 harness）
bash <(curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/memory-plugin-shared/install.sh)

# 直接指定 harness
bash <(curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/memory-plugin-shared/install.sh) \
  --harness claude-code
```

国内网络可用火山 TOS 镜像：

```bash
bash <(curl -fsSL https://ovrelease.tos-cn-beijing.volces.com/memory-plugin-shared/install.sh) \
  --harness claude-code --dist tos
```

`--harness` 支持 `claude-code`、`codex`、`cursor`、`trae`、`trae-cn`、`trae-cli`（TraeCode CLI 2.0，走 Codex 兼容插件格式）等，可逗号分隔同时安装多个（F-041）。

**前置条件**（官方，博文未展开）：macOS 或 Linux、Node.js 18+；安装向导会引导填写 OpenViking 连接信息（自部署选 Self-hosted / local，填服务器 URL 与用户 API Key）。

**装完必须完全退出并重启客户端**，然后验证（以 TRAE 为例，其他客户端同理）：

1. 在客户端 MCP 设置里确认 `openviking` 已连接
2. 问一个旧会话里存过的偏好，确认答案来自记忆
3. 告诉 Agent 一个临时偏好，等回复完成后新开会话再问，验证捕获→提交→跨会话召回

脚本安装的四个 Hook（F-041）：

| Hook | 作用 |
|------|------|
| SessionStart | 加载 profile 与当前项目记忆 |
| UserPromptSubmit | 为当前请求召回并注入上下文 |
| PreToolUse | 误访本地 `viking://` 路径时重定向到 MCP 工具 |
| Stop | 捕获并立即提交当轮对话用于记忆抽取 |

卸载/升级均重跑同一脚本（`--uninstall --yes`）。

## 方式二：手动配置 MCP

OpenViking Server 内置 MCP 端点，**与 REST 同进程同端口**：`http://<server>:1933/mcp`（F-039）。

通用客户端（Trae、Manus、Cursor 等标准 mcpServers 格式）：

```json
{
  "mcpServers": {
    "openviking": {
      "url": "http://192.168.3.101:1933/mcp",
      "headers": {
        "Authorization": "Bearer <你的用户API密钥>"
      }
    }
  }
}
```

Claude Code 需显式 `type: http`，也可用 CLI：

```bash
claude mcp add --transport http openviking \
  http://192.168.3.101:1933/mcp \
  --header "Authorization: Bearer <你的用户API密钥>"
```

鉴权支持 `X-Api-Key` 或 `Authorization: Bearer` 两种 Header；仅绑定 localhost 的本地开发模式可免鉴权（F-039）。Claude.ai/Claude Desktop 只接受 OAuth 2.1，需走服务端内置的 OAuth 授权流程，不能直接填 API Key。

接好后 Agent 即可调用 **15 个 MCP 工具**：

```text
find  search  read  list  tree  remember  write  edit
add_resource  list_watches  cancel_watch
grep  glob  forget  health
```

最常用四个：`search`（带会话上下文深检索，`mode="context"` 直接给注入级上下文）、`find`（快速直查）、`remember`（主动固化记忆）、`add_resource`（导入外部资料）。

> 博文提到的 `openviking_search`/`openviking_memory_commit` 是 VikingBot 界面化/早期叫法，MCP 开发以这 15 个工具名为准（F-039，详见[核验报告](../references/verification.md)）。

## 方式三：ov CLI

CLI 的连接配置在 `~/.openviking/ovcli.conf`（F-047）：

```json
{
  "url": "http://192.168.3.101:1933",
  "api_key": "<你的用户API密钥>"
}
```

常用命令：

```bash
ov status                                        # 服务与连接状态
ov add-resource https://github.com/volcengine/OpenViking   # 导入仓库（异步任务）
ov task status <TASK_ID>                         # 轮询处理进度直到 completed
ov ls viking://resources/                        # 列目录
ov tree viking://resources/volcengine -L 2       # 目录树
ov find "what is openviking"                     # 语义检索，返回带 URI 的结果
ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs/en
```

VikingBot 终端里的 `/search`（博文实测命令，F-027）与会话命令 `ov chat` 属于 bot 交互层；脚本化场景用上面的 ov CLI。

## 方式四：Python SDK / HTTP

Python（F-047）：

```python
import openviking as ov

client = ov.SyncHTTPClient(url="http://192.168.3.101:1933", api_key="<用户API密钥>")
client.initialize()
results = client.find(query="how to use openviking")
client.close()
```

curl 直接打 REST：

```bash
curl "http://192.168.3.101:1933/api/v1/fs/ls?uri=viking://" \
  -H "X-API-Key: <用户API密钥>"
```

另有 **Go、TypeScript SDK** 与完整 HTTP API（F-040），LangChain 生态提供 Tools + store 集成。

## 集成矩阵速查

| 客户端 | 方式 |
|--------|------|
| Claude Code / Codex / Cursor / TRAE（含 TRAE CN、TraeCode CLI 2.0） | Hooks + MCP（同一安装脚本，选 harness） |
| OpenClaw | Context engine |
| Hermes | 内置 |
| OpenCode / DeerFlow / DSH | Plugin + MCP |
| pi | 原生扩展 |
| 豆包工作（Doubao Work） | Connector |
| LangChain | Tools + store |
| Manus 等通用 MCP 客户端 | 标准 MCP JSON 配置 |

（F-040；博文列举的 Claude Code、Codex、OpenClaw、TRAE、Cursor、Python、LangChain 全部在列）

## 生产部署补充

不只想用 Docker 单机时（F-048）：

- **systemd**：官方推荐的生产进程托管方式（Environment 指向 `/etc/openviking/ov.conf`）
- **docker compose**：仓库根目录提供 `docker-compose.yml`，`docker compose up -d`
- **Kubernetes**：`examples/k8s-helm` 有 Helm chart，安装时传 embedding/vlm api_key
- **多实例**：开 `temp_upload.default_mode=shared`；仅多实例共享同一 workspace 时才设 `storage.skip_process_lock=true`，QueueFS/审计 SQLite 路径按实例独立

## 验证清单

- [ ] 客户端重启后 MCP 显示 openviking 已连接
- [ ] 新会话能召回旧偏好（跨会话）
- [ ] `ov find` 能检索到导入的资源
- [ ] 对外暴露时已改强密钥，未使用示例值 abc123456efg
