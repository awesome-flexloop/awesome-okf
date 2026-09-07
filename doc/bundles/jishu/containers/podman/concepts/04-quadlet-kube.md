---
type: Concept
title: "Quadlet 与 Kubernetes YAML 系统集成"
description: "Quadlet .container/.volume/.network/.kube 单元文件、systemd socket 激活、podman kube play/apply/down/generate 循环与 auto-update 协同。"
tags: [podman, quadlet, kubernetes, systemd, container-unit, kube-play, auto-update, integration]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T09:50:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T09:50:00+08:00 }
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

# Quadlet 与 Kubernetes YAML 系统集成

Podman 区别于 Docker 的最大亮点是**对 Linux 系统管理原生工作流的深度集成**：用 Quadlet 把容器写成声明式的 systemd 单元；或者用 K8s YAML 直接作为容器/ Pod 的唯一来源——两种方式共享同一套 systemd 生命周期管理与自动更新能力。

## 一、Quadlet：声明式容器 systemd 单元

Quadlet 是 Podman 4.4+ 引入的**系统级容器管理方式**：你不用手写 `podman run` 再套一层 `systemd service`（`podman generate systemd` 那种方式），而是写一个极简的 `.container` 单元文件，由 Quadlet 在 systemd 启动时自动翻译成完整的 Podman 调用。

### 四种单元文件类型

| 后缀 | 作用 | 等价 Podman 操作 |
|------|------|-----------------|
| `.container` | 单个容器（90% 场景用它） | `podman run/create` + 健康检查 + 重启策略 |
| `.volume` | 持久化卷 | `podman volume create` |
| `.network` | 用户自定义网络 | `podman network create` |
| `.kube` | 整个 K8s YAML（Pod/Deployment） | `podman kube play` |

### Quadlet 放置目录（systemd 加载顺序）

| 路径 | 权限 | 说明 |
|------|------|------|
| `/etc/containers/systemd/*.container` | root 全局 | rootful 容器、开机启动关键服务 |
| `~/.config/containers/systemd/*.container` | 用户级 | rootless 容器、普通用户自启动服务（配合 `systemctl --user`） |

### 最小化示例：Nginx Web 服务

```ini
# /etc/containers/systemd/nginx.container
[Unit]
Description=Nginx Reverse Proxy
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/library/nginx:1.27-alpine
ContainerName=nginx-proxy
PublishPort=80:80
PublishPort=443:443
Volume=/srv/nginx/html:/usr/share/nginx/html:Z
Volume=/srv/nginx/conf.d:/etc/nginx/conf.d:Z
Volume=/srv/nginx/ssl:/etc/nginx/ssl:ro,Z
Environment=TZ=Asia/Shanghai
HostName=web-01
MemoryMax=512M
CPUShares=1024
HealthCmd=/usr/bin/curl -fsS http://127.0.0.1/ || exit 1
HealthInterval=30s
HealthStartPeriod=10s
HealthRetries=3
AutoUpdate=registry
Restart=on-failure
SecurityLabelDisable=true   # 或 SecurityLabelFileType=container_file_t
ReadOnly=true
Tmpfs=/tmp
Tmpfs=/run

[Service]
Restart=always
RestartSec=5
TimeoutStartSec=900

[Install]
WantedBy=multi-user.target
```

### [Container] 组常用字段速查（与 podman run flags 对应）

| Quadlet 字段 | 等价 podman run |
|-------------|----------------|
| `Image=` | 位置参数最后一个镜像名 |
| `ContainerName=` | `--name` |
| `PublishPort=80:80` | `-p 80:80` |
| `Volume=src:dst:opts` | `-v src:dst:opts` |
| `Environment=KEY=val` | `-e KEY=val` |
| `HostName=` | `-h/--hostname` |
| `User=` / `Group=` | `-u user:group` |
| `AddCapability=NET_ADMIN` | `--cap-add NET_ADMIN` |
| `DropCapability=ALL` | `--cap-drop ALL` |
| `NoNewPrivileges=true` | `--security-opt no-new-privileges` |
| `ReadOnly=true` | `--read-only` |
| `Tmpfs=/tmp:size=64m` | `--tmpfs /tmp:size=64m` |
| `Exec=` | 覆盖 CMD（`podman run -- ...` 的 `...` 部分） |
| `Network=host` / `Network=internal-net` | `--net host` / `--network internal-net` |
| `Pod=backend.pod` | 加入另一个 `.pod` 单元的 Pod |
| `MemoryMax=1G` | `--memory=1g` |
| `CPUShares=512` | `--cpu-shares=512` |
| `AutoUpdate=registry` | `--label io.containers.autoupdate=registry` |
| `HealthCmd=` / `HealthInterval=` | `--health-cmd` / `--health-interval` |

### 加载、启停、查看

```bash
# 1. 让 systemd 重新扫描 Quadlet 单元（写/改 .container 之后必跑）
sudo systemctl daemon-reload

# 2. 此时 nginx.service 被自动生成！查看一下：
sudo systemctl cat nginx.service

# 3. 启动 + 开机自启
sudo systemctl enable --now nginx.service

# 4. 查看状态（底层就是 podman container）
podman container inspect nginx-proxy | jq '.[0].State.Health'
systemctl status nginx.service -l
journalctl -u nginx.service -f    # 日志
```

### .volume 和 .network 组合示例

```ini
# /etc/containers/systemd/pgdata.volume
[Volume]
VolumeName=pgdata-16
User=999
Group=999
Label=app=postgres
```

```ini
# /etc/containers/systemd/backend.network
[Network]
NetworkName=backend-net
Subnet=172.20.0.0/16
Gateway=172.20.0.1
IPRange=172.20.1.0/24
Driver=bridge
```

然后在 postgres.container 里直接引用：
```ini
Volume=pgdata.volume:/var/lib/postgresql/data:Z
Network=backend.network
```

### auto-update：镜像滚动更新 + systemd 重启

Quadlet 设置 `AutoUpdate=registry` 后，Podman 自动更新服务会定期检查 registry 上镜像是否有新 digest，并把新镜像拉下来、然后优雅重启对应的 systemd 单元——零停机配置即得：

```bash
# 开启自动更新定时服务（root）
sudo systemctl enable --now podman-auto-update.timer
# 或 rootless 用户：
systemctl --user enable --now podman-auto-update.timer
```

策略对比：
- `AutoUpdate=registry`：digest 变就更（生产推荐）
- `AutoUpdate=local`：本地同名镜像变就更（开发场景）

更高级的滚动策略（蓝绿）由结合 `podman auto-update --rollback=healthcheck` 实现：健康检查不过就自动回滚到上一版镜像。

## 二、Kubernetes YAML 原生驱动（podman kube）

Podman 可以把 Kubernetes Pod / Deployment / PersistentVolumeClaim 等 YAML 当"本地容器编排规范"直接用，不需要 K8s 集群。这是 Podman 独有的能力。

### K8s ↔ Podman 双向工作流

```text
  手动容器 ──podman generate kube──▶ K8s YAML（唯一可信源）
                                      │
                                      │ podman kube play/apply/down
                                      ▼
                                 Podman 本地 Pod/容器
```

### play（=首次运行） vs apply（=幂等更新） vs down（=清理）

| 命令 | 语义 | 幂等 |
|------|------|------|
| `podman kube play web-pod.yaml` | 读 YAML，创建 Pod/容器/卷/网络 | 否，重跑会报错（对象已存在） |
| `podman kube apply -f web-pod.yaml` | 存在则更新配置重启，不存在则创建 | ✅ 幂等，CI/CD 首选 |
| `podman kube down web-pod.yaml` | 按 YAML 内容删除对应 Pod/卷/网络 | ✅ 幂等 |

### 最小 K8s Pod YAML 示例

```yaml
# web-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web
spec:
  restartPolicy: Always
  containers:
    - name: nginx
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
          hostPort: 8080
      volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html
      env:
        - name: TZ
          value: Asia/Shanghai
      livenessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 5
        periodSeconds: 10
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 500m
          memory: 512Mi
  volumes:
    - name: html
      hostPath:
        path: /srv/web/html
        type: Directory
```

```bash
# 应用
podman kube apply -f web-pod.yaml
# 查看生成的 Pod（带 infra 容器）
podman pod ps
podman ps --pod web-pod
# 一键停机清理
podman kube down web-pod.yaml
```

### .kube Quadlet：把 K8s YAML 交给 systemd

如果 K8s YAML 是生产规范，那么 `.kube` Quadlet 直接让它由 systemd 托管，连 apply 都不用手敲：

```ini
# /etc/containers/systemd/backend-stack.kube
[Unit]
Description=Backend full stack (K8s YAML)
After=network-online.target

[Kube]
Yaml=/opt/manifests/backend-full.yaml
ConfigMap=/opt/manifests/config.yaml:/etc/config
AutoUpdate=registry

[Install]
WantedBy=multi-user.target
```

然后：
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backend-stack.service
```

启动流程：systemd → 调 `podman kube play` → 创建所有 Pod/容器/卷 → 健康检查 OK 即进入 running。

## 三、auto-update 与 healthcheck 的闭环

把 Quadlet/Kube + auto-update + healthcheck 合在一起，就得到零运维的生产级自愈系统：

```text
   ┌──────────────────────────────────────────────────────┐
   │ podman-auto-update.timer（每日 00:00 触发）           │
   └──────────┬───────────────────────────────────────────┘
              ▼
   拉 registry:2 更新 digest 比对 ──相同──▶ 退出
              │不同
              ▼
   拉新镜像到本地存储 ──失败──▶ 退出 + 告警
              │成功
              ▼
   systemctl restart <unit>  ──新容器启动──▶ 跑 HealthCmd
              │                           │
         失败←返回非0                      │通过 200 OK
              │                           │
              ▼                           ▼
         自动回滚到老镜像            ← 成功 ── 标记 OK，写 journal 更新记录
```

## 四、systemd socket 激活（更省资源）

对于低流量的 Web/API 服务，用 Quadlet 的 socket 激活让容器**第一个请求进来时才启动**，空闲则卸载：

```ini
# /etc/containers/systemd/api.socket
[Unit]
Description=Internal API socket

[Socket]
ListenStream=0.0.0.0:3000
Accept=no

[Install]
WantedBy=sockets.target
```

```ini
# api.container（同名关联自动生效）
[Container]
Image=registry.internal/myapi:v1
...
```

```bash
sudo systemctl enable --now api.socket
# 此时 3000 端口被 systemd 监听；第一个 curl 进来，Podman 才创建并启动 api 容器
```

## 相关概念
- [/concepts/01-commands.md](01-commands.md) — 容器/Pod 基础命令
- [/concepts/02-rootless.md](02-rootless.md) — 用户级 Quadlet 运行前提
- [/examples/02-quadlet-stack.md](../examples/02-quadlet-stack.md) — 完整三服务 Quadlet 栈
