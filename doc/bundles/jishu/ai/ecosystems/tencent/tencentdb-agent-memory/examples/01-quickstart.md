---
type: Example
title: "一键部署最小闭环：start-all.sh 拉起 core/hub/proxy 三件套"
description: "在单机用公开 Docker 镜像与 .env 两组 LLM 参数一键拉起 MemoryCore、MemoryHub、MemoryProxy，读取 admin key 并验证 Claude Code 接入地址。"
tags: [tencentdb-agent-memory, example, deploy, docker, quickstart]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 安装与部署信源
---

# 一键部署最小闭环

> 本示例基于 commit 8b86874 截面的文档与源码整理，未在真实环境运行验证；命令中的 env/端点均带（F-xxx）溯源，落地前请先实测。

## 1. 前置条件

1. 已安装 Docker。三个发布镜像 `agentmemory/memory-core:latest`、`agentmemory/memory-hub:latest`、`agentmemory/memory-proxy:latest` 在 Docker Hub 公开可拉，多架构 linux/amd64 + linux/arm64（F-033/F-281）。
2. 运行环境 Node.js ≥ 22.16（README 口径，F-020）。
3. 准备好两组 LLM 参数（F-278/F-170）：
   - `MEMORY_LLM_*`：core/hub 内部使用，协议变量 `MEMORY_LLM_PROTOCOL` 取值 `openai|anthropic`（F-170/F-279）。
   - `PROXY_UPSTREAM_*`：proxy 的代理上游（F-170）。
4. 管理员默认用户名 `admin`（F-277）；`MEMORY_CORE_GATEWAY_API_KEY` 留空等于关闭 Bearer 鉴权，即本地零配置形态（F-167）。

## 2. 获取部署脚本并填写 .env

```bash
# 实际 remote 组织为 TencentCloud；CHANGELOG 克隆命令写作 Tencent/，以实际 remote 为准（F-018/F-001）
git clone https://github.com/TencentCloud/TencentDB-Agent-Memory.git
cd TencentDB-Agent-Memory/deploy/global-images
cp .env.example .env
```

编辑 `.env`，填入两组 LLM 参数（F-035）。`require_vars` 会校验必填变量：缺失或值仍为 `REPLACE_ME` 时列出变量名并退出（F-264/F-266）。

`.env.example` 的默认端口与卷（F-272/F-273）：

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `MEMORY_CORE_PORT` | 8420 | MemoryCore 宿主端口，容器内监听 8420（F-269） |
| `PANEL_PORT` | 8125 | Hub 面板宿主端口，容器内监听 8125（F-255/F-024） |
| `KNOWLEDGE_PORT` | 8424 | Knowledge 宿主端口，容器内监听 8421（F-255/F-023） |
| `PROXY_PORT` | 8096 | MemoryProxy 宿主端口，容器内监听 8096（F-271/F-218） |
| `MEMORY_CORE_VOLUME` | tdai-memory-core-data | core 卷，挂载到容器 `/data/tdai-memory`（F-269） |
| `PANEL_VOLUME` | tdai-panel-data | hub 卷，挂载到容器 `/data/knowledge`（F-255） |

## 3. 执行一键启动

```bash
./start-all.sh
```

脚本行为按以下顺序发生（F-263/F-264）：

1. 启动前做端口占用检查（F-282）。
2. 启动顺序固定为 memory-core → memory-hub → proxy，每个组件等待 healthy 后才继续下一个（F-263）。
3. `wait_healthy` 依据 Docker inspect 的 `State.Health.Status` 判断 healthy/unhealthy/none，支持超时与日志输出（F-267）。
4. 首次启动自动执行 init-admin：随机生成 `sk-mem-` 前缀的 admin key 并落盘 `.admin-key`（F-035/F-166/F-275）。
5. core 经 `/v3/meta/auth/verify` 自检通过后，脚本读取 `.admin-key` 并打印可复制的 Claude Code 接入命令（F-035/F-265）。
6. proxy 默认以 `PROXY_FULL_STACK=1` 启动（F-264）。

## 4. 读取 admin key 并验证闭环

```bash
cat .admin-key
```

最小闭环验证以脚本结束时打印的两个接入参数为准（F-274）：

```text
ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default
ANTHROPIC_AUTH_TOKEN=<.admin-key 中的 sk-mem-*>
```

补充验证：proxy 路由含 `/health`（F-221），core 网关 `/health` 豁免鉴权（F-156），二者均可直接探测。hub 容器内同时包含 Panel 与 Knowledge Service，并被注入 `REMOTE_INSTANCE_URL=http://memory-core:8420`（F-254/F-256）。

## 5. 失败处置

| 现象 | 依据 | 处置 |
|------|------|------|
| `require_vars` 报错并列出变量名 | 必填项缺失或仍为 `REPLACE_ME`（F-266） | 补齐两组 LLM 参数后重跑（F-278） |
| 启动前提示端口被占用 | `check_ports` 预检（F-282） | 修改 `.env` 中冲突端口（F-272）或释放端口 |
| 某组件长时间 unhealthy | `wait_healthy` 超时并输出日志（F-267） | 按输出查看该容器日志；core/hub/proxy 均可单独重启（F-280） |
| `.admin-key` 文件不存在 | init-admin 未成功完成（F-035/F-166） | 检查 core 日志后重置环境再启动 |
| 拉取镜像失败 | 镜像公开无需登录（F-281/F-033） | 检查网络；腾讯内网可改用内网镜像源（F-034） |
| 想换 MongoDB 后端 | 属 2.0.2-beta.1 试验特性（F-009/F-010） | 不在本最小闭环范围，改用 `start-all-mongo.sh`（F-283） |

## 6. 重置环境

```bash
./stop-all.sh --purge
```

`--purge` 会清除 volume 与 admin key，用于从零重置（F-036）。重置后再次执行 `./start-all.sh` 会重新 init-admin 并生成新的 `sk-mem-` key（F-035/F-275），旧的 `ANTHROPIC_AUTH_TOKEN` 随即失效。

## 相关概念

- [部署拓扑与脚本](../concepts/11-deploy-topology.md)
- [产品总览与四件架构](../concepts/00-overview.md)
- 信源：[安装与部署信源](../references/04-deploy-install.md)
