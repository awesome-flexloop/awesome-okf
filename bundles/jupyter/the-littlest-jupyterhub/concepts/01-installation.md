---
title: TLJH 安装指南
description: 在 Debian/Ubuntu 服务器上安装 The Littlest JupyterHub
type: How-To
tags: [how-to, install, bootstrap, deployment, jupyterhub, tljh, devops]
sources:
  - id: tljh-bootstrap
    title: bootstrap/bootstrap.py
  - id: tljh-installer
    title: tljh/installer.py
  - id: tljh-readme
    title: README.md
---

# TLJH 安装指南

## 系统要求

- **操作系统**：Ubuntu ≥22.04 或 Debian ≥11
- **架构**：amd64（x86_64）或 arm64（aarch64）
- **Python**：≥3.9
- **systemd**：必须可用
- **网络**：需要能访问互联网（下载 Conda 包和 Traefik 二进制）

## 快速安装

在目标服务器上执行：

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --admin <admin-username>
```

安装完成后，在浏览器中访问服务器 IP 或域名即可使用。首次访问时，admin 用户需要设置密码。

## 安装命令选项

### 指定管理员用户

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --admin alice --admin bob
```

可以多次指定 `--admin` 来添加多个管理员。

### 指定版本

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --version 2.0.0
```

`--version` 接受：
- `latest`：最新发布版本（默认）
- 部分版本号（如 `1.0` 会匹配 1.0.x 最新版）
- Git 分支名
- Git commit hash

### 自定义安装前缀

通过环境变量指定安装目录：

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo env TLJH_INSTALL_PREFIX=/opt/tljh python3 -
```

默认安装前缀为 `/opt/tljh`。

### 开发模式安装

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo env TLJH_BOOTSTRAP_DEV=yes TLJH_BOOTSTRAP_PIP_SPEC=/path/to/tljh python3 -
```

### 显示安装进度页

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --show-progress-page --admin alice
```

安装期间在端口 80 提供 HTTP 进度页，可通过浏览器查看安装日志。

### 安装用户自定义 requirements

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --user-requirements-txt-url https://example.com/my-requirements.txt
```

在用户环境中安装额外的 pip 包。

## 安装流程

安装分为两个阶段：

### 阶段1：Bootstrap（bootstrap.py）

bootstrap.py 仅依赖 Python 标准库，执行以下操作：

1. **系统检查**：验证发行版版本、Python 版本、systemd 可用性
2. **基础工具安装**：通过 apt 安装 python3、python3-venv、python3-pip、git、sudo
3. **创建虚拟环境**：在 `/opt/tljh/hub` 创建 Python venv
4. **安装 TLJH**：pip 安装 `the-littlest-jupyterhub` 包
5. **切换到 Installer**：通过 `os.execv` 切换到 hub 环境的 Python 执行 installer

### 阶段2：Installer（installer.py）

installer.py 在 hub 环境中执行：

1. 设置插件（setuptools entry points 自动发现）
2. 创建配置目录和 config.yaml
3. 创建管理员账户（bcrypt 密码哈希存储）
4. 创建用户组（jupyterhub-admins、jupyterhub-users）
5. 设置用户 Conda 环境（安装 Miniforge + Notebook/JupyterLab）
6. 安装 Hub Python 依赖
7. 下载 Traefik 二进制文件（含 SHA256 校验）
8. 安装并启动 systemd 服务（jupyterhub.service、traefik.service）
9. 创建符号链接 `/usr/bin/tljh-config`
10. 执行插件 post_install 钩子

## 安装目录结构

```
/opt/tljh/
├── hub/              # Hub 虚拟环境（JupyterHub 运行环境）
│   ├── bin/
│   └── lib/
├── user/             # User Conda 环境（所有用户共享的 Notebook 环境）
│   ├── bin/
│   └── lib/
├── state/            # 运行时状态
│   ├── traefik.toml  # Traefik 静态配置
│   ├── rules/        # Traefik 动态路由
│   ├── acme.json     # Let's Encrypt 证书存储
│   ├── traefik-api.secret
│   └── passwords.dbm # 管理员密码哈希
└── config/           # 配置文件
    ├── config.yaml   # 主配置文件
    └── jupyterhub_config.d/  # 自定义 JupyterHub 配置
```

## 安装后的验证

安装完成后，可以通过以下方式验证：

```bash
# 检查服务状态
sudo systemctl status jupyterhub
sudo systemctl status traefik

# 查看配置
sudo tljh-config show

# 测试访问
curl -I http://localhost
```

## 常见问题

### 安装失败：架构不支持

TLJH 仅支持 amd64 和 arm64 架构。安装前确认：

```bash
uname -m
```

应输出 `x86_64` 或 `aarch64`。

### 安装后无法访问

检查防火墙是否放行 80/443 端口，以及 Traefik 服务是否正常运行。

### 重新安装

如需完全重新安装，先清理：

```bash
sudo systemctl stop jupyterhub traefik
sudo rm -rf /opt/tljh
sudo rm -f /etc/systemd/system/jupyterhub.service /etc/systemd/system/traefik.service
sudo systemctl daemon-reload
```

然后重新运行 bootstrap 脚本。

## 下一步

- [架构概览](02-architecture.md)：理解 TLJH 的内部架构
- [配置系统](03-config-system.md)：配置用户、认证、HTTPS 等
- [基础安装示例](../examples/01-basic-install.md)：从零到可用的完整示例
