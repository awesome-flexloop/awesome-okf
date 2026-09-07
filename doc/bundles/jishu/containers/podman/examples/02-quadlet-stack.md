---
type: Example
title: "Quadlet 部署三服务生产级容器栈"
description: "Postgres 持久化 + Redis 缓存 + Web 应用三服务 Quadlet 部署：.volume/.network/.container 互联、systemd 自启、auto-update、健康检查、重启策略完整配置。"
tags: [podman, quadlet, postgres, redis, web-app, production, systemd, volumes, networks, healthcheck, auto-update]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T10:05:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T10:05:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: cli-domain
    resource: /references/cli-domain-source.md
    title: CLI 层与 Domain 层架构源码
  - id: libpod
    resource: /references/libpod-source.md
    title: libpod 核心与外部协同库源码
---

# Quadlet 部署三服务生产级容器栈

本示例演示用 4 个 Quadlet 单元文件（1 个网络 + 1 个卷 + 3 个容器）搭建完整的三层 Web 服务：Postgres 16（持久化卷）→ Redis 7（内存缓存）→ 内部 Web 应用（Node.js 连接上述两层）。含 systemd 自启顺序、健康检查、资源上限、auto-update 滚动、SELinux 标签、日志驱动完整配置。

## 目标架构

```text
  internet ──► host:3000 ──┐
                            ▼
                    ┌─────────────────┐
                    │   web-app.container   │───► Pod/容器内 Node.js 20
                    │  (PublishPort=3000)  │     │         │
                    └─────────┬───────────┘     │查询     │缓存读写
                              │ backend.network  │         │
                ┌─────────────┴──────────────┐  │         │
                ▼                            ▼  ▼         ▼
        ┌───────────────┐           ┌───────────────┐
        │ postgres.container │     │ redis.container  │
        │  Port 不对外发布    │     │  Port 不对外发布   │
        │  + pgdata.volume  │     │  + tmpfs 数据卷   │
        └───────────────┘           └───────────────┘
                  ▲                               ▲
              持久化：                         纯内存，
            /var/lib/containers/...            重启丢数据
             storage/pgdata-16
```

## 目录结构

```
/etc/containers/systemd/
├── backend.network          ① 隔离网络 172.21.x.x/24
├── pgdata-16.volume         ② Postgres 持久化卷
├── postgres.container       ③ Postgres 16 数据库
├── redis.container          ④ Redis 7 缓存
└── web-app.container        ⑤ Node.js Web 前端应用
```

> 下面所有单元都是 **rootful**（/etc/... 目录），对应系统级 systemd。若想 rootless 就全部改放在 `~/.config/containers/systemd/`，命令用 `systemctl --user`。

---

## ① backend.network：内部隔离网络

```ini
# /etc/containers/systemd/backend.network
[Network]
NetworkName=backend-net
Driver=bridge
Subnet=172.21.0.0/16
Gateway=172.21.0.1
IPRange=172.21.1.0/24
DNS=true
Label=env=production
Label=app=triple-stack
```

## ② pgdata-16.volume：Postgres 持久化卷

```ini
# /etc/containers/systemd/pgdata-16.volume
[Volume]
VolumeName=pgdata-16
# 固定 owner 让 postgres uid=999 可写；或不加就由第一次容器启动时的进程调整
Label=app=postgres
Label=version=16
Copy=false          # Copy=true 会把容器初始 /var/lib/postgresql/data 复制出来；首次初始化用 true 更稳
```

## ③ postgres.container：PostgreSQL 16

```ini
# /etc/containers/systemd/postgres.container
[Unit]
Description=PostgreSQL 16 Database (Triple-Stack)
Requires=backend.network pgdata-16.volume
After=backend.network pgdata-16.volume
Before=web-app.container redis.container
Wants=network-online.target
After=network-online.target

[Container]
Image=docker.io/library/postgres:16-alpine
ContainerName=postgres-db
# 卷：持久化数据 + 初始化脚本（第一次建库）
Volume=pgdata-16.volume:/var/lib/postgresql/data:Z
Volume=/opt/initdb:/docker-entrypoint-initdb.d:Z,ro
# 网络（同 backend.network 就可用容器名 DNS 互联）
Network=backend.network
HostName=postgres
# 端口：不对外 PublishPort，只允许同网络的 web 连
# 环境变量
Environment=POSTGRES_DB=appdb
Environment=POSTGRES_USER=app
Environment=POSTGRES_PASSWORD_FILE=/run/secrets/postgres-passwd
Environment=TZ=Asia/Shanghai
Environment=PGDATA=/var/lib/postgresql/data/pgdata
# 秘密（文件注入）
Secret=postgres-passwd,type=file,source=/etc/podman-secrets/postgres-passwd,target=/run/secrets/postgres-passwd,mode=0400,uid=70,gid=70
# 健康检查：真正的 SQL 连通性
HealthCmd=/usr/bin/pg_isready -U app -d appdb || exit 1
HealthInterval=15s
HealthStartPeriod=30s
HealthRetries=5
# 资源上限
MemoryMax=2G
MemorySwapMax=4G
CPUShares=2048
PidsLimit=4096
# 安全
ReadOnly=true
Tmpfs=/tmp:size=128m,mode=1777
Tmpfs=/var/run/postgresql:size=16m,mode=0775,uid=70,gid=70
User=postgres
NoNewPrivileges=true
SecurityLabelDisable=true
# 自动更新
AutoUpdate=registry
# 日志
LogDriver=journald
LogTag=postgres-db

[Service]
Restart=on-failure
RestartSec=10
TimeoutStartSec=600
TimeoutStopSec=120

[Install]
WantedBy=multi-user.target
```

## ④ redis.container：Redis 7（无持久化）

```ini
# /etc/containers/systemd/redis.container
[Unit]
Description=Redis 7 In-Memory Cache (Triple-Stack)
Requires=backend.network
After=backend.network
Before=web-app.container
Wants=network-online.target
After=network-online.target

[Container]
Image=docker.io/library/redis:7-alpine
ContainerName=redis-cache
# 网络
Network=backend.network
HostName=redis
# 不对外端口；同网络访问 redis:6379
# 配置 + 数据都在 tmpfs（可容忍丢）
Tmpfs=/data:size=1g,mode=0755
# 自定义 redis.conf 挂进去
Volume=/opt/redis/redis.conf:/usr/local/etc/redis/redis.conf:Z,ro
Exec=/usr/local/etc/redis/redis.conf
# 健康：真 PING/PONG
HealthCmd=/usr/local/bin/redis-cli -h 127.0.0.1 ping | grep -q PONG || exit 1
HealthInterval=10s
HealthStartPeriod=5s
HealthRetries=3
# 资源
MemoryMax=512M
CPUShares=1024
PidsLimit=512
# 安全
ReadOnly=true
User=redis
NoNewPrivileges=true
# 自动更新
AutoUpdate=registry
LogDriver=journald
LogTag=redis-cache

[Service]
Restart=always
RestartSec=3
TimeoutStartSec=120
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

## ⑤ web-app.container：Node.js 三层服务前端

```ini
# /etc/containers/systemd/web-app.container
[Unit]
Description=Node.js Web App (Triple-Stack)
BindsTo=postgres.container redis.container
After=postgres.container redis.container backend.network
Wants=network-online.target
After=network-online.target

[Container]
Image=registry.example.com/internal/web-app:v2
ContainerName=web-app
# 网络 + 对外端口
Network=backend.network
PublishPort=0.0.0.0:3000:3000
HostName=web
# 卷：静态资源 + 配置文件（ro）
Volume=/opt/web-app/public:/app/public:Z,ro
Volume=/opt/web-app/config.yml:/app/config.yml:Z,ro
Secret=web-app-env,type=env,source=/etc/podman-secrets/web-app.env
# 环境变量：用容器名 DNS 连 Postgres/Redis
Environment=NODE_ENV=production
Environment=DATABASE_URL=postgres://app@postgres:5432/appdb
Environment=REDIS_URL=redis://redis:6379/0
Environment=TZ=Asia/Shanghai
# 健康：/healthz 端点
HealthCmd=/usr/bin/wget -qO- http://127.0.0.1:3000/healthz 2>/dev/null | grep -q OK || exit 1
HealthInterval=15s
HealthStartPeriod=20s
HealthRetries=3
# 资源
MemoryMax=1G
CPUShares=1024
PidsLimit=1024
# 安全
ReadOnly=true
Tmpfs=/tmp:size=128m,mode=1777
Tmpfs=/app/tmp:size=512m,mode=0755
User=node
NoNewPrivileges=true
DropCapability=ALL
AddCapability=NET_BIND_SERVICE
# 自动更新：拉新镜像后健康检查失败自动回滚
AutoUpdate=registry
# 日志
LogDriver=journald
LogTag=web-app

[Service]
Restart=on-failure
RestartSec=5
TimeoutStartSec=600
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
```

---

## 加载与启动

```bash
# 前置：准备 secrets 目录与文件（root）
sudo mkdir -p /etc/podman-secrets
echo -n 'ChangeM3InProduction!!'     | sudo tee /etc/podman-secrets/postgres-passwd > /dev/null
sudo chmod 0400 /etc/podman-secrets/postgres-passwd

# web.env 内容（key=value 一行一个，Podman 会转成容器内的环境变量）
cat <<'EOF' | sudo tee /etc/podman-secrets/web-app.env > /dev/null
DATABASE_PASSWORD=ChangeM3InProduction!!
SESSION_SECRET=s3cr3t-r3place-m3
JWT_SIGNING_KEY=xxx-very-long-random-key
EOF
sudo chmod 0400 /etc/podman-secrets/web-app.env

# ① systemd 扫描 Quadlet 单元（每次改 .container/.network/.volume 之后必跑）
sudo systemctl daemon-reload

# ② 看看生成的 .service 是否长这样（调试）
sudo systemctl cat postgres.service | head -60
sudo systemctl cat redis.service    | head -40
sudo systemctl cat web-app.service  | head -80

# ③ 一键启动整栈（web-app 自动拉起前置 redis/postgres）
sudo systemctl enable --now web-app.service
```

## 观察与验收

```bash
# 容器状态
podman ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# 三容器健康状态（Healthy 列都得 healthy）
watch -n 2 podman ps --format 'table {{.Names}}\t{{.Status}}\t{{.Health}}'

# 日志（journalctl，rootful 直接看）
journalctl -u postgres.service --since "10 minutes ago" -f
journalctl -u redis.service --since today | grep -i 'warning\|error'
journalctl -u web-app.service | grep 'healthcheck\|started'

# 真网络：从 web-app 容器里 ping 其他服务
podman exec -it web-app sh -c "
  echo '--DNS resolve--'
  getent hosts postgres redis
  echo '--postgres pg_isready--'
  timeout 5 sh -c '</dev/tcp/postgres/5432' && echo 5432 open
  echo '--redis ping--'
  timeout 5 sh -c '</dev/tcp/redis/6379'    && echo 6379 open
"

# 外部 HTTP 健康端点
curl -sS http://127.0.0.1:3000/healthz
# 预期输出：OK
```

## auto-update 全栈镜像滚动

```bash
# 开启系统级 auto-update 定时器（每日 00:00 执行）
sudo systemctl enable --now podman-auto-update.timer
sudo systemctl list-timers podman-auto-update.timer

# 手动干跑一次，看看哪些有更新
sudo podman auto-update --dry-run

# 真正跑更新：先拉 → 健康检查 → 过了就重启对应 service → 不过就回滚
sudo podman auto-update
journalctl -u podman-auto-update.service -n 100
```

## 清理与卸载（非破坏性）

```bash
# 停 web → redis → postgres（按依赖反向）
sudo systemctl disable --now web-app.service redis.service postgres.service

# 卸载单元但保留数据
sudo rm /etc/containers/systemd/{web-app,redis,postgres}.container
sudo rm /etc/containers/systemd/pgdata-16.volume
sudo rm /etc/containers/systemd/backend.network
sudo systemctl daemon-reload

# 真要彻底清数据（小心！）：
# sudo podman volume rm pgdata-16
# sudo podman network rm backend-net
```

## 验收矩阵

| # | 检查项 | 命令 | 预期 | 状态 |
|---|--------|------|------|------|
| 1 | 三容器均 up 健康 | `podman ps | wc -l`（含表头 4 行） | 3 容器 + header | ☐ |
| 2 | 外部端点 200 | `curl -s -o /dev/null -w '%{http_code}' :3000/healthz` | 200 | ☐ |
| 3 | postgres 卷持久化 | `podman volume inspect pgdata-16 -l` | 存在且 Mountpoint 非空 | ☐ |
| 4 | web → postgres:5432 通 | 见上方 exec 脚本 | open | ☐ |
| 5 | web → redis:6379 通 | 见上方 exec 脚本 | open | ☐ |
| 6 | 重启 OS 后服务自启 | `sudo reboot` → `systemctl is-active web-app.service` | active | ☐ |
| 7 | auto-update.timer 激活 | `systemctl is-active podman-auto-update.timer` | active | ☐ |

## 相关概念
- [/concepts/04-quadlet-kube.md](../concepts/04-quadlet-kube.md) — Quadlet 单元完整字段说明
- [/concepts/01-commands.md](../concepts/01-commands.md) — Volume / Network / 健康检查命令
