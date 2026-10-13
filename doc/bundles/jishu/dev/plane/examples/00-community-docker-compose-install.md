---
okf_version: "0.2"
type: Example
title: "演练：社区版 Docker Compose 一键安装"
description: "从零到可登录的社区版自托管演练——拉取 setup.sh、安装、改四个环境键、启动与验收，含每一步的预期输出与排障点"
sources:
  - id: official-docker
    resource: https://developers.plane.so/self-hosting/methods/docker-compose
---

# 00 · 演练：社区版 Docker Compose 一键安装

> ⚠️ **来源性质**：以下步骤来自 **官方 Docker Compose 部署文档（2026-10 版，已逐条核验）**，**不是作者实测，也不是本包实测**。首次上生产请先在测试机跑通。
> 参考事实：F-033、F-034、F-035、F-036、F-038、F-040；核验：V17、V18、V19、V20。

## 前置条件

| 项 | 官方要求 |
|----|---------|
| CPU | 2 核（x64/AMD64 或 ARM64） |
| 内存 | 4 GB（**生产推荐 8 GB**） |
| 系统 | Ubuntu / Debian / CentOS / Amazon Linux 2 或 2023（Windows 走 WSL2 + gitbash） |
| 软件 | 最新版 Docker 与 Docker Compose |
| 权限 | root 或有 sudo 权限，且该用户能访问 docker 服务 |

## 步骤 1：建目录并拉脚本

```bash
mkdir plane-selfhost
cd plane-selfhost
curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh
chmod +x setup.sh
```

> 目录名任意（博文示例用 `plane-deploy`，官方用 `plane-selfhost`）。这个目录同时承载数据与配置，**不要放在会被清理的临时路径**。

## 步骤 2：安装

```bash
./setup.sh
```

预期看到菜单：

```text
Select a Action you want to perform:
   1) Install (arm64)
   2) Start
   3) Stop
   4) Restart
   5) Upgrade
   6) View Logs
   7) Backup Data
   8) Exit
Action [2]: 1
```

输入 `1` → 生成 `plane-app/`（预览部署为 `plane-app-preview/`）目录，内含 `docker-compose.yaml` 与 `plane.env`。随后输入 `8` 退出。

## 步骤 3：改四个关键环境键（先别启动）

编辑 `plane-app/plane.env`：

| 键 | 默认 | 改成 |
|----|------|------|
| `LISTEN_HTTP_PORT` | `80` | 未被占用的端口，如 `8080` |
| `LISTEN_HTTPS_PORT` | `443` | 未被占用的端口，如 `4430` |
| `WEB_URL` | `http://localhost` | `https://plane.example.com:8080` 或 `http://[IP]:8080` |
| `CORS_ALLOWED_ORIGINS` | `http://localhost` | **与 `WEB_URL` 完全一致** |

```bash
# 示例（按实际情况替换）
sed -i 's|^LISTEN_HTTP_PORT=.*|LISTEN_HTTP_PORT=8080|' plane-app/plane.env
sed -i 's|^WEB_URL=.*|WEB_URL="http://192.168.1.100:8080"|' plane-app/plane.env
sed -i 's|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS="http://192.168.1.100:8080"|' plane-app/plane.env
```

> ⚠️ 官方硬要求：`WEB_URL` 与 `CORS_ALLOWED_ORIGINS` 必须**逐字符一致**（含 http/https 与端口）。不一致会导致登录与 API 调用失败——这是自托管最常见的「装起来了但用不了」原因。

顺手一起改的安全项（生产必做）：`SECRET_KEY`、`POSTGRES_PASSWORD`、`RABBITMQ_PASSWORD`、MinIO 的 `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`。

## 步骤 4：启动

```bash
./setup.sh
# 输入 2 (Start)
```

首次启动会拉取镜像，耗时取决于带宽。官方页面给出两个验收信号：镜像下载完成、服务全部 up。

## 步骤 5：验收

```bash
# 服务状态（worker / beat-worker 不应处于 Restarting）
docker compose -f plane-app/docker-compose.yaml ps

# 端口只应暴露 80/443（或你改的端口），不应暴露 5432/6379/5672/9000
ss -lntp | grep -E ':(8080|4430)\b'

# 应用可达
curl -I http://192.168.1.100:8080
```

浏览器打开 `WEB_URL` → 注册第一个账号 → 创建工作区。

## 排障速查

| 现象 | 常见原因 |
|------|---------|
| worker / beat 反复 `Restarting` | RabbitMQ 或 Postgres 不可达（多为 `.env` 主机名写错）——注意 **RabbitMQ 也在依赖链里**（F-056） |
| 能打开但登录/接口报错 | `WEB_URL` 与 `CORS_ALLOWED_ORIGINS` 不一致 |
| 80 端口起不来 | 端口被占用，改 `LISTEN_HTTP_PORT` |
| 上传失败 | 检查 `FILE_SIZE_LIMIT`（默认 5242880 = 5 MB）与对象存储配置 |
| migrator 容器 exited | 属正常（官方设计为跑完迁移即退出，`restart: no`） |

## 已知边界

- 本演练对应**社区版**；Commercial 版走另一条线：`curl -fsSL https://prime.plane.so/install/ | sh -`，再用 `prime-cli` 配置（F-037）
- 容器内置组件仅适合体验：生产应把数据库与对象存储挪到外部（F-040），见 [01 生产加固清单](01-production-hardening-checklist.md)
