---
type: Example
title: 无root部署Nginx与systemd集成
description: 实战Podman rootless容器模式，非root用户运行Nginx，生成systemd用户服务实现开机自启与linger常驻。
tags: [podman, rootless, systemd, nginx, 非root, linger]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## Rootless模式前提检查

Podman默认支持rootless模式（普通用户无需sudo即可运行容器），首先验证当前环境是否正常启用：

```bash
# 检查是否运行在rootless模式
podman info | grep rootless

# 输出应显示：rootless: true
```

如果显示 `rootless: false`，需要检查：
- `/etc/subuid` 和 `/etc/subgid` 是否为当前用户配置了从属ID范围
- 是否安装了 `slirp4netns` 或 `pasta` 网络栈
- 用户是否有足够的 `/dev/fuse` 访问权限

## 运行无root Nginx容器

以普通用户身份（不使用sudo）启动Nginx容器：

```bash
# 拉取镜像（普通用户权限即可）
podman pull nginx:alpine

# 后台运行nginx，映射8080端口（rootless模式端口>1024无需特权）
podman run -d --name nginx-rootless -p 8080:80 nginx:alpine

# 验证容器运行
podman ps
curl http://localhost:8080
```

Rootless模式下：
- 容器进程以当前用户UID运行，而非root
- 端口映射只能使用1024以上的端口
- 存储位于用户目录 `~/.local/share/containers/storage/`

## 验证非root运行

确认容器进程没有root权限：

```bash
# 查看Podman相关进程的所有者
ps aux | grep podman | grep -v grep

# 查看容器内进程的UID映射
podman top nginx-rootless huser user

# 输出应显示容器内root（UID 0）映射到主机普通用户
```

可以看到容器内的进程在主机上是以当前普通用户身份运行的，这就是rootless容器的用户命名空间映射机制——容器内的root在主机上只是普通用户，无法越权访问主机资源。

## 生成systemd用户服务单元

使用 `podman generate systemd` 自动生成systemd服务配置，实现容器开机自启：

```bash
# 先停止并删除现有容器（generate systemd --new需要容器存在但可以是停止状态）
podman stop nginx-rootless
podman rm nginx-rootless

# 确保systemd用户目录存在
mkdir -p ~/.config/systemd/user

# 生成systemd服务单元文件
# --new: 每次启动创建新容器（停止后自动删除）
# --name: 使用容器名作为服务名前缀
podman generate systemd --new --name nginx-rootless > ~/.config/systemd/user/nginx-rootless.service

# 查看生成的服务文件内容
cat ~/.config/systemd/user/nginx-rootless.service
```

生成的服务文件包含标准的systemd单元配置：
- `[Unit]`：服务描述与依赖（After=network.target）
- `[Service]`：启动/停止命令、重启策略、PID文件
- `[Install]`：WantedBy=default.target（用户默认目标）

## 启用并启动服务

加载systemd配置并启动服务：

```bash
# 重新加载systemd用户配置
systemctl --user daemon-reload

# 启用服务（开机自启）并立即启动
systemctl --user enable --now nginx-rootless.service

# 查看服务状态
systemctl --user status nginx-rootless.service

# 验证容器运行
podman ps
curl http://localhost:8080
```

`systemctl --user` 操作用户级systemd实例，不需要root权限。

## 配置Linger实现用户退出后常驻

默认情况下，用户注销后systemd用户实例会停止，容器也会随之退出。使用 `loginctl enable-linger` 让用户服务在用户未登录时也保持运行：

```bash
# 启用linger（需要root权限执行一次）
sudo loginctl enable-linger $USER

# 验证linger状态
loginctl show-user $USER | grep Linger
# 输出应显示：Linger=yes
```

启用linger后：
- 用户注销或服务器重启后，用户级systemd服务会自动启动
- 容器无需用户登录即可常驻运行
- 这是生产环境rootless容器部署的标准配置

## 服务管理与日志

日常管理systemd托管的容器：

```bash
# 停止服务
systemctl --user stop nginx-rootless.service

# 启动服务
systemctl --user start nginx-rootless.service

# 重启服务
systemctl --user restart nginx-rootless.service

# 查看服务日志（journald）
journalctl --user -u nginx-rootless.service -f

# 禁用开机自启
systemctl --user disable nginx-rootless.service
```

也可以直接使用 `podman` 命令管理容器，但推荐通过systemctl管理以保持状态一致。

## 清理服务与容器

如需彻底移除：

```bash
# 停止并禁用服务
systemctl --user stop nginx-rootless.service
systemctl --user disable nginx-rootless.service

# 删除服务文件
rm ~/.config/systemd/user/nginx-rootless.service

# 重新加载配置
systemctl --user daemon-reload

# 删除容器和镜像
podman rm -f nginx-rootless
podman rmi nginx:alpine
```

## 完整部署流程速查

```bash
# 1. 验证rootless模式
podman info | grep rootless

# 2. 准备容器
podman pull nginx:alpine
podman run -d --name nginx-rootless -p 8080:80 nginx:alpine
podman stop nginx-rootless
podman rm nginx-rootless

# 3. 生成并安装systemd服务
mkdir -p ~/.config/systemd/user
podman generate systemd --new --name nginx-rootless > ~/.config/systemd/user/nginx-rootless.service
systemctl --user daemon-reload
systemctl --user enable --now nginx-rootless.service

# 4. 配置linger（可选，服务器部署推荐）
sudo loginctl enable-linger $USER

# 5. 验证
systemctl --user status nginx-rootless.service
curl http://localhost:8080
```

## 相关概念

- [Rootless容器](/concepts/10-rootless.md)
- [systemd与Quadlet](/concepts/12-systemd-quadlet.md)
- [容器基础](/concepts/04-container-basics.md)
- [入门指南](/concepts/01-getting-started.md)
