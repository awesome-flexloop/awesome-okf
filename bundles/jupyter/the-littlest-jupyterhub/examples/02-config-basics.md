---
title: 配置基础操作
description: 使用 tljh-config 管理用户、默认应用、空闲超时等常用配置
type: Example
tags: [example, config, tljh-config, users, default-app, cull, jupyterhub, tljh, devops]
sources:
  - id: tljh-config
    title: tljh/config.py
  - id: tljh-configurer
    title: tljh/configurer.py
---

# 配置基础操作

本文档演示使用 `tljh-config` 命令进行日常配置管理的常见操作。

## 查看当前配置

```bash
sudo tljh-config show
```

## 用户管理

### 添加管理员

```bash
sudo tljh-config add-item users.admin alice
sudo tljh-config reload hub
```

### 移除管理员

```bash
sudo tljh-config remove-item users.admin alice
sudo tljh-config reload hub
```

### 设置用户白名单

```bash
# 只允许这些用户登录
sudo tljh-config add-item users.allowed alice
sudo tljh-config add-item users.allowed bob
sudo tljh-config add-item users.allowed charlie
sudo tljh-config reload hub
```

### 禁止用户

```bash
sudo tljh-config add-item users.banned troublemaker
sudo tljh-config reload hub
```

### 将用户加入额外系统组

例如让特定用户能使用 Docker：

```bash
sudo tljh-config set users.extra_user_groups.docker
# 注：extra_user_groups 是 dict 类型，需要直接编辑 config.yaml
```

直接编辑配置文件：

```bash
sudo nano /opt/tljh/config/config.yaml
```

添加：

```yaml
users:
  extra_user_groups:
    docker:
      - alice
    video:
      - bob
```

```bash
sudo tljh-config reload hub
```

## 默认应用设置

### 默认使用 JupyterLab

```bash
sudo tljh-config set user_environment.default_app jupyterlab
sudo tljh-config reload hub
```

### 默认使用经典 Notebook

```bash
sudo tljh-config set user_environment.default_app classic
sudo tljh-config reload hub
```

## 网络配置

### 修改 HTTP 端口

```bash
sudo tljh-config set http.port 8080
sudo tljh-config reload proxy
```

### 绑定特定地址

```bash
# 只监听本地回环（配合反向代理使用）
sudo tljh-config set http.address 127.0.0.1
sudo tljh-config reload proxy
```

## 空闲服务器清理（Idle Culler）

idle culler 自动停止长时间空闲的用户服务器，释放资源。

### 查看当前配置

```bash
sudo tljh-config show | grep -A 10 cull
```

### 修改空闲超时

```bash
# 空闲1小时后停止服务器（默认10分钟）
sudo tljh-config set services.cull.timeout 3600
sudo tljh-config reload hub
```

### 修改检查间隔

```bash
# 每5分钟检查一次（默认60秒）
sudo tljh-config set services.cull.every 300
sudo tljh-config reload hub
```

### 启用用户级清理

默认只清理命名服务器（named servers）。启用后，空闲用户（包括默认服务器）也会被停止：

```bash
sudo tljh-config set services.cull.users true
sudo tljh-config reload hub
```

### 设置最大存活时间

```bash
# 服务器最长运行12小时
sudo tljh-config set services.cull.max_age 43200
sudo tljh-config reload hub
```

### 禁用 idle culler

```bash
sudo tljh-config set services.cull.enabled false
sudo tljh-config reload hub
```

## 基础路径配置

如果 JupyterHub 不在域名根路径（如反向代理在 `/jupyter` 下）：

```bash
sudo tljh-config set base_url /jupyter
sudo tljh-config reload
```

## 配置验证

tljh-config 默认在写入前使用 JSON Schema 验证配置。如果配置有误，命令会失败并显示验证错误。

跳过验证（不推荐，除非你确定配置正确）：

```bash
sudo tljh-config --no-validate set some.custom.path value
```

## 配置备份

直接备份配置文件即可：

```bash
sudo cp /opt/tljh/config/config.yaml /opt/tljh/config/config.yaml.backup
```

恢复：

```bash
sudo cp /opt/tljh/config/config.yaml.backup /opt/tljh/config/config.yaml
sudo tljh-config reload
```

## 配置操作速查表

| 操作 | 命令 |
|------|------|
| 查看配置 | `sudo tljh-config show` |
| 设置值 | `sudo tljh-config set <path> <value>` |
| 删除值 | `sudo tljh-config unset <path>` |
| 追加列表 | `sudo tljh-config add-item <path> <value>` |
| 移除列表项 | `sudo tljh-config remove-item <path> <value>` |
| 重载 Hub | `sudo tljh-config reload hub` |
| 重载代理 | `sudo tljh-config reload proxy` |
| 重载全部 | `sudo tljh-config reload` |
