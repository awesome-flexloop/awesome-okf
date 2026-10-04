---
type: Example
title: "Docker Compose 部署：单机、Postgres 与云手机三套环境"
description: "用仓库 docker/ 下三套 compose 文件部署 Octop：两阶段镜像构建链、基础单机卷与环境变量、pgvector 后端切换，以及 Redroid 云手机叠加层与升级备份。"
tags: [octop, docker, compose, postgres, pgvector, redroid, deployment]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: deploy
    resource: /concepts/21-packaging-deployment.md
    title: 打包与部署
  - id: lifecycle
    resource: /concepts/01-server-lifecycle.md
    title: 服务器生命周期
  - id: mobile
    resource: /concepts/18-mobile-desktop-proactive.md
    title: 移动端与桌面端
---

# Docker Compose 部署：单机、Postgres 与云手机三套环境

本示例基于仓库 `docker/` 目录下逐字核实的三套文件：`docker-compose.yml`（单机）、`docker-compose.postgres.yml`（数据库）、`docker-compose.mobile.yml`（云手机）。

## 镜像构建链（docker/Dockerfile）

两阶段构建（F-586）：

1. **前端** `FROM node:20-slim AS frontend-builder`：`npm ci` 后执行 `npm run build:docker`；构建参数 `NODE_MAX_OLD_SPACE_SIZE` 默认 2048（低内存机构建主机可调 1024）
2. **运行时** `FROM python:3.12-slim AS runtime`：uv 逐字来自 `COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/`；两次 `uv sync --frozen --no-dev --extra browser`（第一次 `--no-install-project` 利用层缓存）
3. 环境默认 `OCTOP_BIND_HOST=0.0.0.0`、`OCTOP_PORT=8088`、`HOME=/data`、`PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright`；`EXPOSE 8088`
4. 健康检查逐字：`HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 CMD ["sh","-c","curl -f http://localhost:${OCTOP_PORT:-8088}/api/health || exit 1"]`；镜像内无 USER 指令（root 运行）

入口脚本 `docker-entrypoint.sh`：首启（`~/.octop/octop.db` 不存在时）执行 `octop init --yes`，默认管理员 `admin`；未给 `OCTOP_DEFAULT_PASSWORD` 则随机生成 16 位密码（首字母、末位数字，被密码策略拒绝会换一个重试），凭据写入 `/data/.octop/credential.txt` 并 chmod 600（F-587）。最终 `exec octop run --host 0.0.0.0 --port "$PORT"`。

## 方案一：单机 docker-compose.yml

关键片段逐字：

```yaml
services:
  octop:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    image: octop:latest
    container_name: octop
    restart: unless-stopped
    ports:
      - "${OCTOP_PORT:-8088}:${OCTOP_PORT:-8088}"
    volumes:
      - ${OCTOP_DATA:-~/.octop}:/data/.octop
    environment:
      - HOME=/data
      - OCTOP_BIND_HOST=0.0.0.0
      - OCTOP_PORT=${OCTOP_PORT:-8088}
      - OCTOP_DEFAULT_PASSWORD=${OCTOP_DEFAULT_PASSWORD:-}
      - OCTOP_DATABASE_URL=${OCTOP_DATABASE_URL:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY:-}
      - LANGFUSE_TRACING_ENABLED=${LANGFUSE_TRACING_ENABLED:-true}
```

启动（注释要求在仓库根目录执行）：

```bash
docker compose -f docker/docker-compose.yml up -d --build
# 自定义端口/首启密码
OCTOP_PORT=9090 OCTOP_DEFAULT_PASSWORD='abc12345' \
  docker compose -f docker/docker-compose.yml up -d
```

注意：`docker/.env` 仅用于 Compose 插值，变量必须出现在 `environment` 清单里才会进容器；密码须 ≥8 位且同时含字母与数字。

## 方案二：docker-compose.postgres.yml（pgvector）

数据库服务逐字要点（F-589）：

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: octop-postgres
    restart: unless-stopped
    ports:
      - "${OCTOP_PG_PORT:-5432}:5432"
    environment:
      POSTGRES_USER: ${OCTOP_PG_USER:-octop}
      POSTGRES_PASSWORD: ${OCTOP_PG_PASSWORD:-octop}
      POSTGRES_DB: ${OCTOP_PG_DB:-octop}
    volumes:
      - octop_pgdata:/var/lib/postgresql/data
      - ./postgres/init-vector.sql:/docker-entrypoint-initdb.d/01-vector.sql:ro
```

`docker/postgres/init-vector.sql` 仅一条有效语句：`CREATE EXTENSION IF NOT EXISTS vector;`——只负责 pgvector 扩展，不属于 Octop 控制面迁移（注释标注 ADR 002；控制面 schema 由 Octop 启动时跑 `NNN_*.pg.sql` 迁移）。

启动数据库后，让 Octop 容器切到 Postgres（连接串即配置键 `OCTOP_DATABASE_URL`，与自托管文档一致）：

```bash
docker compose -f docker/docker-compose.postgres.yml up -d

# 在 docker/.env 或启动环境中提供
OCTOP_DATABASE_DRIVER=postgresql
OCTOP_DATABASE_URL=postgresql://octop:octop@host.docker.internal:5432/octop
docker compose -f docker/docker-compose.yml up -d
```

Linux 上容器访问宿主机映射的 5432 需用 `host.docker.internal`（Docker 20.10+ 自动解析）或宿主网桥 IP；也可自行把两个服务合入同一 compose 网络后用服务名 `postgres:5432`。

## 方案三：docker-compose.mobile.yml（Redroid 云手机）

该文件是**独立** compose 而非叠加层——注释明确 `network_mode: host` 与基础文件的 `ports` 发布冲突（F-589）。关键配置：

```yaml
services:
  octop:
    privileged: true
    network_mode: host
    volumes:
      - ${OCTOP_DATA:-~/.octop}:/data/.octop
      - /var/run/docker.sock:/var/run/docker.sock
      - /dev/binderfs:/dev/binderfs
      - ${OCTOP_PLATFORM_TOOLS:-../.tools/platform-tools}:/opt/android-sdk/platform-tools:ro
    environment:
      - OCTOP_MOBILE_ADB_HOST=${OCTOP_MOBILE_ADB_HOST:-127.0.0.1:5555}
      - OCTOP_MOBILE_CONTAINER=${OCTOP_MOBILE_CONTAINER:-octop-mobile-android}
      - OCTOP_ENABLE_MOBILE=${OCTOP_ENABLE_MOBILE:-1}
      - ANDROID_HOME=/opt/android-sdk
      - ANDROID_SDK_ROOT=/opt/android-sdk
```

宿主要求：Docker socket 可用、存在 `/dev/binder` 或 `/dev/binderfs`。云机子容器由内置脚本创建，参数逐字含镜像 `redroid/redroid:13.0.0-latest`、ADB 端点 `127.0.0.1:5555`、容器名 `octop-mobile-android`、`--privileged --cgroupns=host --restart unless-stopped`、binderfs 挂载与 `--network host`（F-464）。启动：

```bash
docker compose -f docker/docker-compose.mobile.yml up -d --build
```

## 升级与备份

- **升级**：拉新代码后重新 `up -d --build`；入口脚本幂等，迁移在启动时自动执行。`seed_bundled` 只升级已安装的内置插件（版本更新才覆盖，启用状态保留）
- **备份卷**：单卷 `${OCTOP_DATA:-~/.octop}` 挂载到容器 `/data/.octop`，内含 SQLite 库、Agent 工作区、config.json 与知识库索引；可在容器内用 `octop backup create` 生成 `octop-backup-*.tar.gz`，备份内容目录含 config/db/workspaces/skill-packages/plugins/knowledge 六类
- Postgres 方案另需备份命名卷 `octop_pgdata`（或用 pg_dump）

## 排错

| 现象 | 原因与处理 |
|------|-----------|
| 容器一直 unhealthy | 健康检查 30s 间隔、10s 超时、90s 启动宽限、3 次重试才判失败；首启要初始化+迁移+（可选）下载 embedding 模型，先 `docker logs octop` 看初始化是否完成 |
| 端口起不来 | 8088（或 `OCTOP_PORT`）被占用；基础文件双侧端口都用同一变量，换用 `OCTOP_PORT=9090`；mobile 文件用 host 网络，端口冲突直接发生在宿主网络命名空间 |
| 忘记管理员密码 | 查宿主机 `${OCTOP_DATA}/credential.txt`（容器内 `/data/.octop/credential.txt`，首启生成，仅未显式给 `OCTOP_DEFAULT_PASSWORD` 时有） |
| 云手机探测为 none/no_binder | 宿主无 binder 也无 kvm：Linux 上有 `/dev/binder` 判 redroid、有 `/dev/kvm` 判 emulator，二者皆无返回 none（F-457）；需加载 binder_linux 或换支持的内核 |
| 容器连不上宿主机 Postgres | 不要用容器内 localhost；用 `host.docker.internal:5432` 或 compose 服务名，并确认 pgvector 扩展已由 init-vector.sql 创建（仅首启空卷执行） |
| 前端构建 OOM | 构建机内存不足，加 `--build-arg NODE_MAX_OLD_SPACE_SIZE=1024`，或用国内镜像 build-arg（PIP/NPM/APT）走 `docker/docker_build.sh` |
| mobile 与基础 compose 不能同时用 | 设计如此：host 网络与 ports 发布互斥；二选一启动，不要用 `-f base -f mobile` 叠加 |

## 相关概念

- [/concepts/21-packaging-deployment.md](../concepts/21-packaging-deployment.md)
- [/concepts/01-server-lifecycle.md](../concepts/01-server-lifecycle.md)
- [/concepts/18-mobile-desktop-proactive.md](../concepts/18-mobile-desktop-proactive.md)
