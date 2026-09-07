---
type: Example
title: "CentOS/RHEL 系 Rootless Podman 生产部署"
description: "生产级 Rootless Podman 从零部署：cgroup v2、subuid、fuse-overlayfs、普通用户跑 Nginx、systemd --user、防火墙、资源限制完整验证。"
tags: [podman, rootless, centos-stream9, rhel9, production-deployment, systemd, nginx, firewall]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T10:00:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 与 docs/README 文档工程
  - id: cli-domain
    resource: /references/cli-domain-source.md
    title: CLI 层与 Domain 层架构源码
---

# CentOS/RHEL 系 Rootless Podman 生产部署

本示例演示在 CentOS Stream 9（或 RHEL 9 等价）上从零部署生产级 Rootless Podman，覆盖：内核前置检查 → 软件包安装 → subordinate ID 配置 → cgroup v2 delegation → 普通用户创建运行 Nginx → systemd --user 自启动 → firewalld 端口 → 资源限制 → 回归验证，共 9 个步骤。

## 环境信息

| 项目 | 值 |
|------|---|
| 发行版 | CentOS Stream 9 x86_64 |
| 内核版本 | ≥ 5.14（EL9 默认满足） |
| 目标用户 | `deploy` （uid=1100，普通用户，无 sudo 日常） |
| 业务容器 | Nginx 1.27 Alpine，对外 0.0.0.0:8080 → 容器 80 |
| 资源限制 | CPU 2 核软约束 / 内存 1GB 上限 / PIDs 1024 |

---

## Step 1：前置检查内核与发行版

```bash
# 1.1 内核版本（必须 ≥ 5.14）
uname -r
# 输出示例：5.14.0-500.el9.x86_64 ✅

# 1.2 必须是 cgroup v2（EL9 默认）
stat -c '%T' /sys/fs/cgroup
# 输出：cgroup2fs ✅ ；若是 tmpfs 说明 v1，必须在 GRUB 切 v2

# 1.3 SELinux Enforcing（生产建议保留）
getenforce
# 输出：Enforcing ✅
```

**如 cgroup 仍是 v1 必须切换（需重启）：**
```bash
sudo grubby --update-kernel=ALL --args="systemd.unified_cgroup_hierarchy=1"
sudo reboot
```

## Step 2：安装 Podman 与 Rootless 工具链

```bash
sudo dnf install -y \
    podman crun fuse-overlayfs slirp4netns \
    shadow-utils nftables policycoreutils-python-utils \
    uidmap iptables-nft
```

验证二进制版本：
```bash
podman --version      # podman version 5.x+
crun --version        # crun 1.11+
fuse-overlayfs --version  # 1.12+
```

## Step 3：创建部署用户与 subordinate ID

```bash
# 3.1 创建 deploy 用户（已存在则跳过）
sudo useradd -u 1100 -m -s /bin/bash deploy

# 3.2 分配 subordinate UID/GID 区间（65536 连续）
sudo usermod --add-subuids 200000-265535 --add-subgids 200000-265535 deploy

# 3.3 验证
grep deploy /etc/subuid /etc/subgid
# 应看到：
# deploy:200000:65536
# deploy:200000:65536
```

> ⚠️ 必须重新登录一次 deploy 用户（ssh 退出再进），新 subordinate ID 才生效；直接 su - deploy 无效。

## Step 4：配置 cgroup v2 delegation（允许普通用户限流）

```bash
# 4.1 创建 systemd user 服务委托配置
sudo mkdir -p /etc/systemd/system/user@.service.d
sudo tee /etc/systemd/system/user@.service.d/delegate.conf > /dev/null <<'EOF'
[Service]
Delegate=cpu cpuset memory hugetlb pids io
MaxTasksMax=infinity
EOF

# 4.2 放宽资源限制（防止 OOM 或 memlock 被拒）
sudo tee /etc/security/limits.d/99-podman-deploy.conf > /dev/null <<'EOF'
deploy        hard    memlock        unlimited
deploy        soft    memlock        67108864
deploy        hard    nofile         65536
deploy        soft    nofile         32768
@users        hard    nproc          65536
EOF

# 4.3 可选：允许非特权用户绑定低端口（如需 <1024）
echo "net.ipv4.ip_unprivileged_port_start = 80" | \
  sudo tee /etc/sysctl.d/99-unprivileged-ports.conf
sudo sysctl -p /etc/sysctl.d/99-unprivileged-ports.conf

# 4.4 重启生效（稳妥做法，生产窗口执行）
sudo reboot
```

## Step 5：部署用户首次启动与存储初始化

**切换到 deploy 用户（ssh 直接登录 deploy，不要用 su - deploy）：**

```bash
# 5.1 让 systemd --user 会话常驻（退出 ssh 也不杀容器）
export XDG_RUNTIME_DIR="/run/user/$UID"
systemctl --user enable --now podman.socket
sudo loginctl enable-linger deploy   # 持久化：用户登出后服务仍存活

# 5.2 验证 rootless 生效
podman info --format '{{.Host.Security.Rootless}}'
# 输出：true ✅

# 5.3 验证存储驱动 fuse-overlayfs
podman info --format '{{.Store.GraphDriverName}} overlay: {{index .Store.GraphStatus "Native Overlay Diff"}}'
# 输出：overlay false （false 即走 fuse-overlayfs ✅）

# 5.4 验证 cgroup controllers 被委托
cat /sys/fs/cgroup/user.slice/user-$UID.slice/cgroup.controllers
# 输出应包含：cpuset cpu memory hugetlb pids io （顺序不重要，都在就行）
```

## Step 6：拉取镜像 + 首次运行 Nginx

```bash
# 6.1 首次拉取（默认从 docker.io）
podman pull docker.io/library/nginx:1.27-alpine
# 输出镜像大小与 digest；观察是否报 permission 错

# 6.2 试跑一次性容器验证
podman run --rm --memory=128m --cpus=0.5 \
  --publish 127.0.0.1:18080:80 \
  --name nginx-smoke \
  docker.io/library/nginx:1.27-alpine &
# 稍等 3 秒

# 6.3 HTTP 200 验证
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18080/
# 输出：200 ✅

# 6.4 清理烟雾容器
podman rm -f nginx-smoke
```

## Step 7：持久化卷 + systemd --user 自启动

```bash
# 7.1 准备宿主机持久化目录（deploy 用户下执行）
mkdir -p ~/nginx/{html,conf.d,ssl}
cat > ~/nginx/html/index.html <<'EOF'
<!doctype html>
<html><head><title>Deploy Rootless</title></head>
<body><h1>Podman Rootless Nginx is UP</h1></body>
</html>
EOF

# 7.2 创建 systemd --user 目录
mkdir -p ~/.config/systemd/user

# 7.3 生成 service 文件（也可用 podman generate systemd，但手写更清晰）
cat > ~/.config/systemd/user/nginx.service <<'EOF'
[Unit]
Description=Nginx Frontend (rootless)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
TimeoutStartSec=600
ExecStartPre=-/usr/bin/podman rm -f nginx-frontend
ExecStart=/usr/bin/podman run \
    --name=nginx-frontend \
    --cgroups=split \
    --memory=1g \
    --cpus=2 \
    --pids-limit=1024 \
    --read-only \
    --tmpfs=/tmp:size=64m,mode=1777 \
    --tmpfs=/run:size=16m,mode=0755 \
    --userns=auto \
    --security-opt label=type:container_t \
    --publish 0.0.0.0:8080:80/tcp \
    --volume %h/nginx/html:/usr/share/nginx/html:Z,ro \
    --volume %h/nginx/conf.d:/etc/nginx/conf.d:Z,ro \
    --volume %h/nginx/ssl:/etc/nginx/ssl:Z,ro \
    --health-cmd='/usr/bin/wget -qO- http://127.0.0.1:80/ >/dev/null 2>&1 || exit 1' \
    --health-interval=20s \
    --health-start-period=5s \
    --health-retries=3 \
    --label io.containers.autoupdate=registry \
    --log-driver journald \
    --hostname=frontend-%H \
    docker.io/library/nginx:1.27-alpine
ExecStop=/usr/bin/podman stop -t 30 nginx-frontend
ExecStopPost=-/usr/bin/podman rm -f nginx-frontend

[Install]
WantedBy=default.target
EOF

# 7.4 加载 + 开机自启（用户级）
systemctl --user daemon-reload
systemctl --user enable --now nginx.service

# 7.5 查看状态
systemctl --user status nginx.service -l
podman ps
podman healthcheck run nginx-frontend   # 健康检查手动触发，返回 0 即 OK
```

## Step 8：firewalld 放行端口 + 富规则

```bash
# 8.1 放行 8080/tcp（firewalld 默认开着）
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.0.0/8" port port="8080" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all

# 8.2 从外部客户端验证
curl -sS -o /dev/null -w '%{http_code}\n' http://<服务器IP>:8080/
# 输出：200 ✅
```

## Step 9：生产资源验证 + 自动更新服务

```bash
# 9.1 验证内存限制（压 1.5G 观察 cgroup 杀）
podman exec -it nginx-frontend sh -c '
dd if=/dev/zero of=/tmp/big bs=1M count=1500 2>&1 || echo "OOM OK"'
# 预期：分配到 1G 附近被拒绝（--memory=1g）；若 OOM 会触发 restart=on-failure

# 9.2 验证 CPU 限制
podman exec -it nginx-frontend sh -c "nproc"
# 预期看到容器内可用 CPU 数（取决于 cgroup，约 2）

# 9.3 开启 auto-update 定时（每日凌晨 0:00）
systemctl --user enable --now podman-auto-update.timer
systemctl --user list-timers podman-auto-update.timer
# 想手动试一次更新：
podman auto-update --dry-run

# 9.4 开启 journal 日志持久化（否则重启丢）
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
# 查看 nginx 日志：
journalctl --user -u nginx.service -n 200 -f
```

## 验收矩阵 Checklist

| # | 检查项 | 预期结果 | 状态 |
|---|--------|---------|------|
| 1 | `podman info Rootless` | true | ☐ |
| 2 | `podman info GraphDriver` | overlay + Native=false | ☐ |
| 3 | curl 本机 127.0.0.1:8080 | HTTP 200 | ☐ |
| 4 | curl 公网IP:8080 | HTTP 200 | ☐ |
| 5 | systemctl --user is-active nginx.service | active (running) | ☐ |
| 6 | 重启服务器后再检查 #5 | 仍 active | ☐ |
| 7 | podman healthcheck run nginx-frontend | exit 0 | ☐ |
| 8 | podman exec 触发 1.5G 内存分配 | 1G 后被拒/OOM 不影响宿主机 | ☐ |

## 相关概念
- [/concepts/02-rootless.md](../concepts/02-rootless.md) — Rootless 安全模型详解
- [/concepts/04-quadlet-kube.md](../concepts/04-quadlet-kube.md) — 用 Quadlet 替代手写 service（更简洁）
