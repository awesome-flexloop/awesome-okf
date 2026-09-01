---
title: 基础安装与第一个用户
description: 在新服务器上安装 TLJH 并添加第一个管理员用户的完整步骤
type: Example
tags: [example, install, setup, admin, getting-started, jupyterhub, tljh, devops]
sources:
  - id: tljh-bootstrap
    title: bootstrap/bootstrap.py
  - id: tljh-installer
    title: tljh/installer.py
---

# 基础安装与第一个用户

本文档演示在一台全新的 Ubuntu 22.04 服务器上安装 TLJH 并配置第一个管理员用户的完整流程。

## 前置条件

- 一台运行 Ubuntu 22.04 LTS（或 Debian 11+）的服务器
- 具有 root 或 sudo 权限
- 服务器可以访问互联网
- 至少 1GB RAM、10GB 磁盘空间

## 步骤1：更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

## 步骤2：运行安装脚本

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --admin myadmin
```

将 `myadmin` 替换为你想要的管理员用户名。

安装过程通常需要5-15分钟，取决于网络速度。脚本会：
1. 检查系统兼容性
2. 安装 Python、venv、git 等基础工具
3. 创建 hub 虚拟环境
4. 下载并安装 Miniforge（User 环境）
5. 安装 JupyterHub 及所有依赖
6. 下载 Traefik 二进制
7. 配置并启动 systemd 服务

安装期间可以添加 `--show-progress-page` 参数在浏览器中查看进度：

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --show-progress-page --admin myadmin
```

然后访问 `http://<服务器IP>` 查看安装进度。

## 步骤3：验证安装

安装完成后，检查服务状态：

```bash
sudo systemctl status jupyterhub
sudo systemctl status traefik
```

两个服务都应显示 `active (running)`。

## 步骤4：访问 JupyterHub

在浏览器中访问服务器的 IP 地址（或域名）：

```
http://<服务器IP>
```

使用安装时指定的管理员用户名（如 `myadmin`）登录。首次登录时，FirstUseAuthenticator 会要求设置密码。

## 步骤5：确认管理员权限

登录后，打开 JupyterHub 的 Terminal（New → Terminal），验证 sudo 权限：

```bash
sudo whoami
# 输出: root
```

管理员用户有 NOPASSWD sudo 权限。

## 步骤6：在用户环境安装常用包

管理员可以在 User 环境中安装包，所有用户立即可用：

```bash
# 安装数据科学常用包
sudo -E conda install -y numpy pandas matplotlib scikit-learn

# 或使用 pip
sudo -E pip install seaborn plotly
```

## 步骤7：添加更多用户

### 方式一：开放注册（默认）

默认配置下，任何人访问服务器地址都可以创建账户。适合团队内部可信环境。

### 方式二：白名单模式

限制只有指定用户可登录：

```bash
sudo tljh-config add-item users.allowed alice
sudo tljh-config add-item users.allowed bob
sudo tljh-config add-item users.allowed charlie
sudo tljh-config reload hub
```

### 方式三：添加管理员

```bash
sudo tljh-config add-item users.admin alice
sudo tljh-config reload hub
```

## 步骤8：查看配置

```bash
sudo tljh-config show
```

输出类似：

```yaml
base_url: /
http:
  address: ''
  port: 80
https:
  enabled: false
  port: 443
services:
  cull:
    enabled: true
    timeout: 600
    ...
users:
  admin:
  - myadmin
  allowed: []
  banned: []
  ...
```

## 常见问题排查

### 无法访问服务器

检查防火墙：

```bash
sudo ufw status
# 如未开放80端口：
sudo ufw allow 80
sudo ufw allow 443
```

### 服务启动失败

查看日志：

```bash
sudo journalctl -u jupyterhub -n 50
sudo journalctl -u traefik -n 50
```

### 安装中断

重新运行 bootstrap 脚本即可，安装过程是幂等的：

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --admin myadmin
```

## 下一步

- [配置基础操作](02-config-basics.md)：常用 tljh-config 命令
- [配置 HTTPS](04-https-letsencrypt.md)：启用 HTTPS 安全访问
- [设置资源限制](06-resource-limits.md)：限制用户内存和 CPU 使用
