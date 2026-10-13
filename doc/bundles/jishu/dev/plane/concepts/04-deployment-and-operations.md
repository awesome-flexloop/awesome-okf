---
okf_version: "0.2"
type: Concept
title: "部署架构与运维要点"
description: "两条官方部署路径、安装脚本菜单、关键环境变量、内置组件与版本勘误、生产外置依赖建议、Kubernetes 与实例管理 God mode"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/KCjLFr72qwngPyyI1b2ENg
  - id: official-docker
    resource: https://developers.plane.so/self-hosting/methods/docker-compose
---

# 04 · 部署架构与运维要点

> ⚠️ **时效提示**：本节组件版本与镜像为 **2026-10-13 核验值**。博文写于 2026-10-12，其「Postgres 15.5 / Redis 7.2.4」已被上游更新取代，详见 §4 勘误。

## 1. 两条官方路径

| 路径 | 适用 | 官方入口 |
|------|------|---------|
| **Docker Compose** | 单机、中小团队、快速起步 | developers.plane.so《Docker Compose》 |
| **Kubernetes（Helm）** | 规模化、需要编排与弹性 | developers.plane.so《Kubernetes》 |

另有**单容器版（All-in-One）**，十来分钟可起（F-039），官方明确**只适合体验，勿上生产**。

## 2. 社区版一键脚本（命令与菜单）

官方步骤（F-033 / V17）：

```bash
mkdir plane-selfhost      # 博文示例写作 plane-deploy，目录名可自由取
cd plane-selfhost
curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh
chmod +x setup.sh
./setup.sh
```

脚本弹出**八项菜单**，官方逐字列出（F-034 / V17）：

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
```

流程：先选 **1** 安装 → 生成 `plane-app/` 目录并拉下 `docker-compose.yaml` 与 `plane.env`（F-035）→ **改环境变量** → 再跑 `./setup.sh` 选 **2** 启动。日常运维（升级/停止/重启/看日志/备份）都在同一个菜单里，不必记 docker compose 子命令。

> 官方要求：改 `plane.env` **前先停服务**（选 3），改完再启动。

## 3. 四个必须先改的环境键

| 键（官方名） | 默认值 | 说明 |
|-------------|--------|------|
| `LISTEN_HTTP_PORT` | `80` | 被占用时改如 `8080` |
| `LISTEN_HTTPS_PORT` | `443` | 被占用时改如 `4430` |
| `WEB_URL` | `http://localhost` | 必须改成实际 FQDN 或 IP + 端口 |
| `CORS_ALLOWED_ORIGINS` | `http://localhost` | 同上 |

官方强调（V18）：**`WEB_URL` 与 `CORS_ALLOWED_ORIGINS` 必须完全一致**（含协议与端口），不一致会导致认证与 API 调用失败。

其他常用键：`FILE_SIZE_LIMIT`（单文件上限，默认 `5242880` = 5 MB，F-042 / V25）、`USE_MINIO`（1=用内置 MinIO，0=接外部 S3）、`SECRET_KEY`、`DATABASE_URL`、`REDIS_URL`、`AMQP_URL`。

## 4. 内置组件与版本勘误

| 组件 | 博文口径 | **核验值（2026-10-13）** | 判定 |
|------|---------|------------------------|------|
| 数据库 | Postgres **15.5** | `postgres:15.7-alpine` | ⚠️ 版本漂移 |
| 缓存 | Redis **7.2.4** | `valkey/valkey:7.2.x-alpine`，官方称「默认用 **Valkey 7.2**，Redis 兼容替代」 | ⚠️ 组件替换 |
| 对象存储 | MinIO | MinIO（2026-10-08 commit `bab49bb` 将镜像切至 `pgsty/silo`） | ⚠️ 镜像来源变更 |
| 消息队列 | **博文未提及** | `rabbitmq:3.13.6-management-alpine` | ➕ 源文遗漏（F-056） |

> **为什么 RabbitMQ 值得单独提**：它承担邮件、通知、导入等后台任务。官方 Compose 中 worker / beat-worker 依赖它——若 RabbitMQ 或 Postgres 不可达，worker 会反复重启，而这类故障在只看 web/api 时容易漏判。

## 5. 生产环境的三条硬建议

1. **数据库与对象存储挪到容器外**（F-040 / V20）。官方原文是 WARNING 级：「strongly recommended to configure external database and storage」——容器里那套机器一崩数据跟着没。
2. **内存按生产口径配**。官方最低 2 核 4G（F-038 / V19），但**生产推荐 8GB**；第三方另有 4 核 8G 的建议口径。
3. **外部对象存储只认 S3 兼容**（F-043）。博文补充的三条经验（地址不能填本机、密码勿含特殊字符否则预签名上传失败）**未核到官方原文**，标「仅博文单源」，照做前建议小范围验证。

## 6. Kubernetes 路径

- 官方提供 Helm Chart，用 `PLANE_VERSION` 指定版本（F-044）
- 官方**明说不要写 `stable`，必须写具体版本号**（F-045）
- 快速安装会把 Postgres、Redis、MinIO 起成有状态服务，配 longhorn 存储类与 nginx 入口（F-046）

> ⚠️ 上述三条**仅博文单源**（V27），本轮未取到官方 K8s 部署页原文。上生产前请以官方当期 Helm 文档为准。

## 7. 实例管理：God mode

一个实例可放**多个工作区**（F-047）。管理员有专门路径 **God mode**，官方 README 直接给出入口（V22），管辖项（F-048）：

- 实例名与 ID、匿名遥测开关
- **SMTP**（F-049：早点配，否则邀请邮件发不出去）
- SSO 与 OAuth
- 免邀请注册开关
- 普通用户能否创建工作区

## 8. 已知边界

- 本节操作参数源自官方部署文档，**非作者实测**（F-052），也非本包实测
- 组件版本与镜像来源会随上游发版变化，`stale_after: 2026-12-31` 前须复核

下一篇 → [05 选型矩阵与适用边界](05-selection-and-boundaries.md)
