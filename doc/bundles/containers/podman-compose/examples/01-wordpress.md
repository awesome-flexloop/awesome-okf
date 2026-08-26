---
type: Example
title: WordPress 部署示例
description: 使用 podman-compose 部署 WordPress + MariaDB 双服务应用的完整教程
tags: [podman, compose, example, wordpress, mariadb, cms]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# WordPress 部署示例

本示例展示如何使用 podman-compose 部署一个完整的 WordPress 站点，包含 WordPress 应用服务器和 MariaDB 数据库两个服务。

## 前置条件

- 已安装 podman（>= 3.4）
- 已安装 podman-compose
- （CNI 网络用户）已安装 podman-plugins/dnsname 插件

## 项目结构

```
wordpress/
└── compose.yaml
```

## 步骤 1：创建 Compose 文件

创建 `compose.yaml` 文件：

```yaml
---
volumes:
  db_data:
services:
  wordpress:
    image: docker.io/library/wordpress:latest
    ports:
      - 8080:80
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=password
      - WORDPRESS_DB_NAME=wordpress
  db:
    image: docker.io/library/mariadb:10.6.4-focal
    command: '--default-authentication-plugin=mysql_native_password'
    volumes:
      - db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=somewordpress
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=password
```

### 配置说明

**顶层 volumes**：
- `db_data`：声明一个命名卷用于持久化数据库数据，容器删除后数据不丢失

**wordpress 服务**：
- `image`：使用官方 WordPress 镜像
- `ports`：将主机 8080 端口映射到容器 80 端口
- `environment`：配置数据库连接信息
  - `WORDPRESS_DB_HOST=db`：数据库主机地址，这里直接使用服务名 `db`，因为容器间通过服务名自动解析
  - 数据库用户名、密码、库名需要与 db 服务配置一致

**db 服务**：
- `image`：使用 MariaDB 10.6.4 镜像（兼容 MySQL）
- `command`：覆盖默认命令，使用旧版认证插件以兼容 WordPress
- `volumes`：将命名卷 `db_data` 挂载到 `/var/lib/mysql`（MariaDB 数据目录）
- `environment`：
  - `MYSQL_ROOT_PASSWORD`：root 用户密码
  - `MYSQL_DATABASE`：初始化时创建的数据库
  - `MYSQL_USER`/`MYSQL_PASSWORD`：创建的应用用户

## 步骤 2：启动服务

在 `compose.yaml` 所在目录执行：

```bash
podman-compose up -d
```

参数说明：
- `up`：创建并启动所有服务
- `-d`：后台运行（detached mode）

首次运行会自动拉取镜像并创建容器、网络、卷。

## 步骤 3：验证服务状态

查看运行中的容器：

```bash
podman-compose ps
```

查看服务日志：

```bash
# 查看所有服务日志
podman-compose logs

# 只查看数据库日志
podman-compose logs db

# 实时跟踪日志
podman-compose logs -f wordpress
```

## 步骤 4：访问 WordPress

打开浏览器访问：

```
http://localhost:8080
```

首次访问会进入 WordPress 安装向导，按提示设置站点标题、管理员账号即可。

## 常用操作

### 停止服务

```bash
# 停止服务但保留容器
podman-compose stop

# 停止并删除容器、网络
podman-compose down
```

### 停止并删除数据卷

```bash
# 警告：这会删除所有数据库数据！
podman-compose down -v
```

### 重启服务

```bash
podman-compose restart
```

### 进入容器执行命令

```bash
# 进入 wordpress 容器 shell
podman-compose exec wordpress bash

# 进入数据库容器执行 mysql 命令
podman-compose exec db mysql -uwordpress -ppassword wordpress
```

### 备份数据库

```bash
podman-compose exec db mysqldump -uwordpress -ppassword wordpress > backup.sql
```

### 恢复数据库

```bash
cat backup.sql | podman-compose exec -T db mysql -uwordpress -ppassword wordpress
```

## rootless 模式注意事项

本示例完全兼容 rootless 模式：

1. **端口 8080**：使用 >= 1024 的非特权端口，无需 root 即可绑定
2. **命名卷**：`db_data` 存储在用户目录下，权限自动处理
3. **容器间通信**：通过服务名 `db` 解析，需要 dnsname 插件（CNI）或使用 netavark 后端

如果无法通过服务名连接数据库，检查：

```bash
# 检查是否安装 dnsname 插件（CNI 网络）
podman network inspect podman-default 2>/dev/null | grep -i dnsname

# 或确认网络后端
podman info | grep networkBackend
```

## 生产环境加固建议

1. **使用强密码**：示例中的 `password`/`somewordpress` 仅用于演示，生产环境务必使用强密码
2. **使用 secrets**：敏感信息通过 secrets 管理而非环境变量
3. **绑定到 127.0.0.1**：不对外暴露时只绑定本地回环：
   ```yaml
   ports:
     - "127.0.0.1:8080:80"
   ```
4. **定期备份**：设置定时任务备份数据库卷
5. **固定镜像版本**：使用具体版本号而非 `latest`
6. **启用 TLS**：前端加反向代理处理 HTTPS

## 故障排查

### WordPress 无法连接数据库

1. 确认 db 服务已启动：`podman-compose ps`
2. 查看 db 日志：`podman-compose logs db`
3. 确认 DNS 解析正常：`podman-compose exec wordpress getent hosts db`
4. 检查环境变量是否一致

### 端口被占用

如果 8080 已被使用，修改端口映射：

```yaml
ports:
  - "8888:80"
```

然后通过 `http://localhost:8888` 访问。

### 权限问题

rootless 模式下绑定挂载主机目录可能遇到权限问题，建议数据库使用命名卷而非绑定挂载。

## 相关概念

- [快速上手与 Compose Spec 兼容](/concepts/00-introduction.md)
- [rootless 模式下的网络与卷](/concepts/02-rootless.md)
- [Compose 文件常见模式](/concepts/03-compose-patterns.md)
- [多容器应用编排](/examples/02-multi-container.md)
