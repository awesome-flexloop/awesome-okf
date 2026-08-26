---
type: Concept
title: rootless 模式下的网络与卷
description: podman-compose 在无根模式下的网络配置、卷管理与相关注意事项
tags: [podman, compose, rootless, networking, volumes, security]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# rootless 模式下的网络与卷

rootless（无根）模式是 podman-compose 的核心设计目标之一。在 rootless 模式下，所有容器和编排操作都在普通用户权限下执行，不需要 root 权限，大大提升了安全性。

## rootless 模式概述

rootless 模式意味着：

- 容器进程以当前用户 UID/GID 运行，而非 root
- 不需要 sudo 即可执行 `podman-compose up` 等命令
- 网络栈在用户网络命名空间内创建
- 卷存储在用户目录下，不需要系统级权限
- 即使容器逃逸，攻击者获得的也只是普通用户权限

Podman >= 3.4 版本对 rootless 模式有完整支持，这也是 podman-compose 1.x 分支的最低要求版本。

## 网络配置

### CNI 网络与 dnsname 插件

使用传统 CNI 网络栈时，容器间 DNS 解析需要安装 `podman dnsname` 插件：

```bash
# Debian/Ubuntu
sudo apt install podman-plugins

# Fedora
sudo dnf install podman-dnsname
```

dnsname 插件允许同一网络内的容器通过服务名相互解析。例如在 Compose 文件中定义了 `db` 服务，其他服务可以直接使用 `db:3306` 访问数据库。

### netavark 网络后端

较新版本的 Podman（4.0+）默认使用 netavark 作为网络后端，netavark 内置 DNS 解析功能，不需要单独安装 dnsname 插件。

使用 netavark 时，容器间域名解析开箱即用，无需额外配置。

### 网络模式

podman-compose 支持 Compose 规范中的标准网络配置：

```yaml
services:
  web:
    image: nginx
    network_mode: bridge  # 标准桥接网络
    ports:
      - "8080:80"

  app:
    image: myapp
    network_mode: host    # 主机网络模式
```

rootless 模式下的端口映射：
- 端口号 >= 1024 可直接绑定，无需 root
- 端口号 < 1024 需要配置 `sysctl net.ipv4.ip_unprivileged_port_start`
- 建议使用非特权端口（>= 8080）进行开发测试

### 自定义网络

支持定义自定义网络并指定子网等配置：

```yaml
networks:
  frontend:
    ipam:
      config:
        - subnet: 10.5.0.0/16
  backend:
    internal: true  # 内部网络，不连接外部

services:
  web:
    networks:
      - frontend
  db:
    networks:
      - backend
```

## 卷管理

### 命名卷

rootless 模式下的命名卷存储在用户目录中，路径通常为：

```
~/.local/share/containers/storage/volumes/
```

定义和使用命名卷：

```yaml
volumes:
  db_data:
  cache_data:

services:
  db:
    image: postgres
    volumes:
      - db_data:/var/lib/postgresql/data
  app:
    image: myapp
    volumes:
      - cache_data:/app/cache
```

### 绑定挂载

支持绑定挂载主机目录，rootless 模式下需要注意文件权限：

```yaml
services:
  web:
    image: nginx
    volumes:
      - ./html:/usr/share/nginx/html:ro
      - ./config:/etc/nginx/conf.d:ro
```

权限注意事项：
- 容器内进程的 UID/GID 会映射到主机用户
- 如果容器内以 root（UID 0）运行，实际映射到主机上的普通用户 UID
- 使用 `:Z` 或 `:z` 标记处理 SELinux 标签（Fedora/RHEL 系发行版）：

```yaml
volumes:
  - ./data:/app/data:Z
```

### 临时卷

使用 `tmpfs` 挂载临时文件系统：

```yaml
services:
  app:
    image: myapp
    tmpfs:
      - /tmp
      - /run
```

## rootless 模式的限制与解决方案

### 1. 低端口绑定

**问题**：默认无法绑定 1024 以下端口

**解决方案**：

```bash
# 方法1：使用非特权端口
ports:
  - "8080:80"

# 方法2：修改 sysctl 允许非特权端口（需要 root 一次配置）
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
```

### 2. 资源限制

部分资源限制（如 ulimit）在 rootless 模式下有约束，需要配置 `/etc/security/limits.conf` 或使用 `--ulimit` 参数。

### 3. ping 命令

默认 rootless 容器内无法使用 ping，需要调整：

```bash
# 允许普通用户创建 ICMP 套接字
sudo sysctl net.ipv4.ping_group_range="0 2147483647"
```

### 4. 跨主机网络

rootless 模式下的 macvlan/ipvlan 等高级网络配置可能需要额外的内核参数调整。

## 从 0.1.x 升级的注意事项

podman-compose 0.1.x 分支使用特殊的映射 workaround 来处理 rootless 限制，1.x 分支在现代 Podman 版本上不需要这些 workaround：

- 移除了全局 `-t` 映射类型选项
- `network_mode: host` 等配置直接在 YAML 中使用标准字段
- 不再需要特殊的卷映射参数

升级示例：

```yaml
# 旧方式（0.1.x，已废弃）
# podman-compose -t hostnet up

# 新方式（1.x，推荐）
services:
  app:
    network_mode: host
```

## 最佳实践

1. **优先使用命名卷**：而非绑定挂载，避免权限问题
2. **使用非特权端口**：>= 8080，避免 sysctl 配置
3. **验证 dnsname**：多容器应用启动前确认容器间能解析服务名
4. **用户命名空间**：不需要额外配置，Podman rootless 自动处理 UID 映射
5. **测试权限**：涉及文件写入的挂载，先验证容器内有读写权限

## 相关概念

- [快速上手与 Compose Spec 兼容](/concepts/00-introduction.md)
- [daemon-less 架构](/concepts/01-daemonless-arch.md)
- [Compose 文件常见模式](/concepts/03-compose-patterns.md)
- [WordPress 部署示例](/examples/01-wordpress.md)
- [多容器应用编排](/examples/02-multi-container.md)
