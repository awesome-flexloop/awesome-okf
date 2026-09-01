---
type: reference
title: "C02 n8n 安装与配置"
bundle: /datawhale/handy-n8n
description: "官方 SaaS、本地 PC Docker、云主机 Docker Compose、HuggingFace Space 四种部署方式详解"
source: https://github.com/datawhalechina/handy-n8n/blob/main/c02/README.md
path: c02/
tags: [deployment, docker, saas, cloud, huggingface]
status: stable
---

# C02 n8n 安装与配置

## 信源信息

- **文件路径**：`c02/README.md`（含 4 个子文档）
- **GitHub**：https://github.com/datawhalechina/handy-n8n/blob/main/c02/
- **sidebar 标题**：C02 - n8n 安装与配置

## 内容概要

本章介绍 n8n 的四种使用方式，各有优缺点和限制：

| 使用方式 | 优点 | 限制 |
|---------|------|------|
| 官方 SaaS | 开箱即用 | 需订阅费，基础版 $20/月 |
| 本地 PC | 快速上手 | 网络限制、回调受限、需保持开机 |
| 云主机部署 | 灵活、数据掌控 | 需云主机和域名、技术能力要求 |
| HuggingFace Space | 免费、无需云主机 | 需科学上网、需外部数据库 |

## 子文档

### 官方 SaaS（`saas.md`）
14 天免费试用，注册 https://app.n8n.cloud/register ，邮箱验证后使用。

### 本地 PC 部署（`local-pc-deploy.md`）
- 安装 Docker Desktop
- `docker volume create n8n_data`
- `docker run` 启动 n8n（端口 5678，时区 Asia/Shanghai，SQLite 存储）
- 访问 http://127.0.0.1:5678/

### 云主机部署（`cloud-host-deploy.md`）
- 安装 Docker + Docker Compose（Ubuntu）
- 使用官方 `n8n-hosting` 仓库的 `withPostgresAndWorker` 配置（n8n + PostgreSQL + Redis + Worker）
- 配置 `.env`（数据库密码、ENCRYPTION_KEY、WEBHOOK_URL、时区）
- 队列模式：Redis 消息队列，主实例 + Worker 可水平扩展
- Caddy 反向代理自动管理 SSL 证书

### HuggingFace Space 部署（`hf-space-deploy.md`）
- 使用 Supabase 提供外部 PostgreSQL 数据库（Transaction pooler，端口 6543）
- Duplicate Space 模板（tomowang/n8n）
- 配置环境变量：DB_POSTGRESDB_*、N8N_ENCRYPTION_KEY、WEBHOOK_URL、N8N_EDITOR_BASE_URL、时区
- 免费 CPU Basic（2vCPU/16GB/50GB）
- Space 休眠后需外部数据库保持数据

## 对应概念

- [n8n 入门与核心概念](../concepts/getting-started.md)——四种部署方式对比与选择
