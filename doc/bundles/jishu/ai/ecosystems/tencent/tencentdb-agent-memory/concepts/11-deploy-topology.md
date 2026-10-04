---
type: Concept
title: "部署拓扑：三容器、卷、端口与一键启动"
description: "start-all.sh 按 core → hub → proxy 顺序拉起三个容器，配合变量预检、健康等待与两组 LLM 参数完成单机一键部署。"
tags: [tencentdb-agent-memory, concept, deployment, docker, topology]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 部署形态与一键安装
---

# 部署拓扑：三容器、卷、端口与一键启动

## 本篇看点

- 单机 Docker 形态是三个容器：`tdai-memory-core`、`tdai-memory-hub`（Panel+Knowledge 一体）、`tdai-proxy`，Proxy 与 Hub 相互独立（F-263、F-254）。
- `start-all.sh` 严格按 core → hub → proxy 顺序启动，每步等待 healthy；变量缺失或仍为 `REPLACE_ME` 直接退出（F-263、F-266、F-267）。
- 默认端口 8420 / 8125 / 8424 / 8096，默认卷 `tdai-memory-core-data`、`tdai-panel-data`（F-272、F-273）。
- 必填配置只有两组 LLM 参数 `MEMORY_LLM_*` 与 `PROXY_UPSTREAM_*`（F-278）。本篇覆盖 F-263 ~ F-286，并以 F-030 ~ F-036 说明形态选择。

## 1. 三容器拓扑

```text
                 单机 Docker（deploy/global-images）
┌────────────────────────────────────────────────────────────────┐
│ coding agent ──HTTP/SSE──▶ tdai-proxy :8096                    │
│                            (context-proxy，PROXY_FULL_STACK=1) │
│                                  │ 回源                         │
│                                  ▼                              │
│ 浏览器 ──▶ tdai-memory-hub  ──▶ tdai-memory-core :8420          │
│            PANEL 8125            (MemoryCore + 数据卷)          │
│            KNOWLEDGE 8424                                      │
│            卷 → /data/knowledge     卷 → /data/tdai-memory      │
└────────────────────────────────────────────────────────────────┘
宿主端口：8420(core) 8125(panel) 8424(knowledge) 8096(proxy)（F-272）
```

Hub 容器名 `tdai-memory-hub`，端口 `PANEL_PORT:8125` 与 `KNOWLEDGE_PORT:8424`，卷 `PANEL_VOLUME:/data/knowledge`（F-255）；它注入 `REMOTE_INSTANCE_URL=http://memory-core:8420` 回源 Core（F-256）。

## 2. start-all.sh：顺序、校验与收尾

| 步骤 | 机制 | 事实 |
|---|---|---|
| 启动顺序 | memory-core → memory-hub → proxy，各组件等待 healthy 后继续 | F-263 |
| 变量校验 | 调用 `require_vars` 校验必填环境变量 | F-264 |
| Proxy 模式 | 默认以 `PROXY_FULL_STACK=1` 启动 | F-264 |
| 收尾 | 读取 `.admin-key`，打印可复制的 Claude Code 接入命令 | F-265 |

```text
cp .env.example .env → 填两组 LLM 参数 → ./start-all.sh
   │ require_vars：缺变量 / REPLACE_ME → 列清单并退出（F-266）
   ├─ 1. start-memory-core.sh → wait_healthy（F-267）
   ├─ 2. start-memory-hub.sh   → wait_healthy（F-263）
   ├─ 3. start-proxy.sh        → wait_healthy（F-263）
   └─ 读 .admin-key → 打印接入命令（F-265、F-274）
```

`require_vars`（`_lib.sh:33-49`）检查变量缺失或仍为 `REPLACE_ME`，缺失则列出并退出（F-266）；`wait_healthy`（`_lib.sh:99-135`）依据 Docker inspect 的 `State.Health.Status` 判断 healthy / unhealthy / none，支持超时与日志输出（F-267）。

## 3. 三组件单独脚本：容器名、端口与卷

| 组件 | 启动脚本 | 容器名 | 端口映射 | 卷 / 挂载 | 事实 |
|---|---|---|---|---|---|
| Core | `start-memory-core.sh` | `tdai-memory-core` | `${MEMORY_CORE_PORT}:8420` | `${MEMORY_CORE_VOLUME}:/data/tdai-memory`，配置只读挂载 | F-268、F-269 |
| Hub | `start-memory-hub.sh` | `tdai-memory-hub` | `${PANEL_PORT}:8125`、`${KNOWLEDGE_PORT}:8424` | `${PANEL_VOLUME}:/data/knowledge` | F-255 |
| Proxy | `start-proxy.sh` | `tdai-proxy` | `${PROXY_PORT}:8096` | 配置只读挂载 | F-271 |

Core 容器启动要求 `MEMORY_CORE_IMAGE`、`MEMORY_CORE_PORT`、`MEMORY_CORE_VOLUME` 三个变量（F-268）。`start-proxy.sh` 中 `PROXY_FULL_STACK=1` 同时启用 auth、tdai、sessionInit 三个开关，否则各自默认关闭（F-270）。

`.env.example` 默认值（F-272、F-273）：

| 类别 | 默认值 |
|---|---|
| 端口 | `MEMORY_CORE_PORT=8420`、`PANEL_PORT=8125`、`KNOWLEDGE_PORT=8424`、`PROXY_PORT=8096` |
| 卷 | `MEMORY_CORE_VOLUME=tdai-memory-core-data`、`PANEL_VOLUME=tdai-panel-data` |

## 4. 接入地址与三类密钥/用户名

部署结束打印的接入地址为 `ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default` 与 `ANTHROPIC_AUTH_TOKEN`（即 admin key）（F-274）。

| 凭据 | 规则 | 事实 |
|---|---|---|
| admin key | 存于 `.admin-key` 文件，`sk-mem-` 前缀自动生成；首次启动经 init-admin 与 auth/verify 双接口校验 | F-275、F-035 |
| Knowledge service key | `KNOWLEDGE_SERVICE_KEY` 留空时自动生成 `ks-svc-*` | F-276 |
| 管理员用户名 | `MEMORY_CORE_ADMIN_USERNAME` 默认 `admin` | F-277 |

一键部署流程为 `cp .env.example .env`、填两组 LLM 参数、执行 `./start-all.sh`；start-all 首次启动自动 init-admin 并落盘 `.admin-key`，自检 `/v3/meta/auth/verify` 后打印接入命令（F-035）。重置可执行 `stop-all.sh --purge`，清除 volume 与 admin key（F-036）。

## 5. 两组 LLM 参数

| 变量组 | 用途 | 事实 |
|---|---|---|
| `MEMORY_LLM_*` | core / hub 内部使用，含 `MEMORY_LLM_PROTOCOL=openai\|anthropic` | F-170、F-279 |
| `PROXY_UPSTREAM_*` | Proxy 代理上游 | F-170、F-278 |

两组 LLM 参数是核心必填变量（F-278）；`MEMORY_LLM_PROTOCOL` 取值为 `openai` 或 `anthropic`（F-279）。

## 6. 脚本清单、预检与多架构

| 项 | 内容 | 事实 |
|---|---|---|
| 单独脚本 | `start-memory-hub.sh`、`start-memory-core.sh`、`start-proxy.sh` | F-280 |
| 镜像架构 | 多架构 amd64 / arm64，公开无需登录 | F-281、F-033 |
| 端口预检 | `check_ports` 在启动前做端口占用检查 | F-282 |
| 交互配置 | 启动脚本支持交互式配置，自动预检 LLM 通路与端口占用 | F-017 |
| Mongo 入口 | `start-all-mongo.sh`；未配置 `MONGODB_ENDPOINT` 时拉起 `mongodb-atlas-local` 容器 | F-283、F-009 |
| Mongo 配套 | `docker-compose.local-mongo.yaml`、`tdai-gateway.local-mongo.yaml` | F-284 |
| Knowledge 容器脚本 | `MemoryKnowledge/docker/` 含 `run.sh`、`smoke-test.sh`、`env.example` | F-285 |
| 镜像说明 | 仓库根 `README.docker.md` | F-286 |

三个发布镜像为 `agentmemory/memory-core:latest`、`agentmemory/memory-hub:latest`、`agentmemory/memory-proxy:latest`，linux/amd64 + linux/arm64 双架构，发布在 Docker Hub 公开可拉（F-033）；部署脚本另存在腾讯内网镜像源 `mirrors.tencent.com/memory-team-control/*`（F-034）。

## 7. 形态选择：Standalone 与 Service

| 形态 | 存储与状态 | 面向 | 事实 |
|---|---|---|---|
| Standalone | SQLite / 本地文件 / 进程内状态 | 单机部署 | F-030 |
| Service | TCVDB / COS / Redis | K8s 多副本、多租户 | F-030 |

Service 形态的 K8s 要点为 ConfigMap/Secret 注入环境变量、Deployment 设置 `TDAI_DEPLOY_MODE=service`、Service 暴露 3100 端口（F-031）。Standalone Docker 示例以 `docker run` 注入 LLM 参数、映射 `8420:8420`、挂载 tdai-data 卷，镜像名为 `agentmemory/hermes-memory:latest`（F-032）。存储后端可用 `MEMORY_CORE_STORE_MODE=mongodb` 切换到试验性 MongoDB（需 Mongo 7.0+ mongot，不静默回退 sqlite，切换不迁移数据）（F-010）。

## 延伸阅读

- [TencentDB Agent Memory 事实清单 F-263~F-286](../spec/facts.md)
- [部署形态与一键安装](../references/04-deploy-install.md)
- [TencentDB-Agent-Memory 源码地图](../references/01-source-code-map.md)
- [09 · MemoryProxy 代理与注入层](09-memory-proxy.md)
- [10 · MemoryPanel/Hub 团队操作台与 ACL](10-panel-acl.md)
