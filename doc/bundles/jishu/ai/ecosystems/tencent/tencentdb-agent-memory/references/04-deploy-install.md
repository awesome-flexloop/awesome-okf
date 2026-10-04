---
type: Reference
title: "安装指南与一键部署脚本信源"
description: "INSTALL_CN 的八客户端接入清单与 Claude Code 配置样例、deploy/global-images 的启动顺序/端口卷/env 默认值/健康检查/admin key 机制，以及 Standalone 与 Service 两形态边界。"
tags: [tencentdb-agent-memory, reference, deploy, install, docker, k8s]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-install
    resource: INSTALL_CN.md
    title: 中文安装指南
  - id: s-deploy
    resource: deploy/global-images/**
    title: 一键部署脚本与 env 样例
  - id: s-deploy-doc
    resource: README.deployment.md、README.docker.md
    title: 部署形态说明
---

# 安装与部署信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 文件 | INSTALL_CN.md、deploy/global-images/{start-all,start-memory-core,start-memory-hub,start-proxy,_lib}.sh、.env.example、README.deployment.md、README.docker.md |
| 采集日期 | 2026-10-04（commit 8b86874） |
| 对应事实 | F-009~F-018、F-026~F-036、F-164~F-170、F-213~F-215、F-255~F-257、F-263~F-286 |

## 客户端接入（INSTALL_CN.md:334-349）

Proxy 支持 8 类 AI Agent 客户端（F-028）：Claude Code、CodeBuddy、WorkBuddy、Codex、DeepSeek Harness（dsh）、OpenCode、Hermes、OpenClaw，各自有独立接入章节。

Claude Code 配置样例（INSTALL_CN.md:211-226，F-029）：

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default
export ANTHROPIC_AUTH_TOKEN=<.admin-key 中的 sk-mem-*>
# 并配置 --model
```

## 一键部署流程

```bash
git clone https://github.com/Tencent/TencentDB-Agent-Memory.git   # 注意组织名口径，见 F-018
cd deploy/global-images
cp .env.example .env          # 填入两组 LLM 参数：MEMORY_LLM_* 与 PROXY_UPSTREAM_*
./start-all.sh
```

- 启动顺序 core → hub → proxy，逐组件 wait_healthy（F-263/F-267）。
- require_vars 拦截缺失或仍为 REPLACE_ME 的必填变量（F-266）。
- 首次自动 init-admin，生成 sk-mem-* 落盘 .admin-key，auth/verify 自检后打印可复制的 claude 命令（F-035/F-275）。
- PROXY_FULL_STACK=1 时 proxy 同时启用 auth + tdai + sessionInit（F-270）。
- `./stop-all.sh --purge` 清卷与 admin key（F-036）。

## 端口、卷与镜像默认值（.env.example）

| 变量 | 默认值 |
|------|--------|
| MEMORY_CORE_IMAGE / MEMORY_HUB_IMAGE / PROXY_IMAGE | agentmemory/memory-core:latest、agentmemory/memory-hub:latest、agentmemory/memory-proxy:latest（F-033） |
| MEMORY_CORE_PORT / PANEL_PORT / KNOWLEDGE_PORT / PROXY_PORT | 8420 / 8125 / 8424 / 8096（F-272） |
| MEMORY_CORE_VOLUME / PANEL_VOLUME | tdai-memory-core-data、tdai-panel-data（F-273） |
| MEMORY_CORE_STORE_MODE | sqlite（默认）/ mongodb（试验，需 Mongo 7.0+ mongot，不静默降级，F-010/F-168） |
| MEMORY_CORE_METADATA_BACKEND | auto / sqlite（F-168） |
| MEMORY_PROMPT_MODE | code（默认）/ chat（F-169） |
| MEMORY_CORE_GATEWAY_API_KEY | 留空=关闭 Bearer（本地零配置，F-167） |
| KNOWLEDGE_PUBLIC_BASE_URL | http://host.docker.internal:8424/v3（F-215） |
| KNOWLEDGE_SERVICE_KEY | 留空自动生成 ks-svc-*（F-276） |

容器侧事实：core 容器 tdai-memory-core 映射 ${MEMORY_CORE_PORT}:8420 与卷 :/data/tdai-memory（F-269）；hub 容器 tdai-memory-hub 映射 PANEL_PORT:8125、KNOWLEDGE_PORT:8424，注入 REMOTE_INSTANCE_URL=http://memory-core:8420（F-255/F-256）；proxy 容器 tdai-proxy 映射 ${PROXY_PORT}:8096（F-271）。

## 两形态边界（README.deployment.md:6-20）

| 维度 | Standalone | Service |
|------|-----------|---------|
| 存储 | SQLite / 本地文件 / 进程内状态 | TCVDB / COS / Redis |
| 适用 | 单机、个人或小团队 | K8s 多副本、多租户 |
| K8s 要点 | — | ConfigMap/Secret 注入、TDAI_DEPLOY_MODE=service、Service 端口 3100（F-031） |

## MongoDB 试验形态

一键入口 start-all-mongo.sh；未配置 MONGODB_ENDPOINT 时拉起 mongodb-atlas-local 容器；切换不迁移存量数据（F-009/F-010/F-283）。MemoryCore 根目录配套 docker-compose.local-mongo.yaml 与 tdai-gateway.local-mongo.yaml（F-284）。

## 注意事项

- MemoryKnowledge 容器内监听 8421、宿主默认映射 8424（F-023）；Panel 本地裸跑默认 8123、容器内 8125（F-024）。
- 部署文档 Standalone 示例镜像名写作 agentmemory/hermes-memory:latest（F-032），与脚本中的 memory-core:latest 并列，属口径差异。
