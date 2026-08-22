---
title: TLJH 架构概览与双环境模型
description: 理解 TLJH 的双 Conda 环境架构、systemd 服务模型和进程隔离机制
type: Explanation
tags: [concept, architecture, dual-env, conda, systemd, jupyterhub, tljh, devops]
sources:
  - id: tljh-installer
    title: tljh/installer.py
  - id: tljh-config
    title: tljh/config.py
  - id: tljh-jupyterhub-config
    title: tljh/jupyterhub_config.py
  - id: tljh-conda
    title: tljh/conda.py
---

# TLJH 架构概览与双环境模型

TLJH 的核心架构设计是**双环境分离**：Hub 环境运行管理组件，User 环境为所有用户提供 Notebook 计算。两者物理隔离，通过 PATH 机制桥接。

## 整体架构

```
                    ┌─────────────────────────────────────────────┐
                    │               Traefik (反向代理)             │
                    │         端口 80/443 / systemd 服务           │
                    └─────────────────┬───────────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────────┐
                    │           JupyterHub (Hub 环境)              │
                    │     /opt/tljh/hub/  ·  systemd 服务          │
                    │         端口 15001  ·  以 root 运行           │
                    └─────────────────┬───────────────────────────┘
                                      │ spawn (systemd)
                    ┌─────────────────┴───────────────────────────┐
                    │     每个用户独立 systemd 服务                  │
                    │   jupyter-{username} · 用户权限运行           │
                    │     使用 /opt/tljh/user/ Conda 环境          │
                    └─────────────────────────────────────────────┘
```

## 双环境详解

### Hub 环境（/opt/tljh/hub）

Hub 环境是一个 Python venv（虚拟环境），运行 JupyterHub 核心和管理组件。

- **路径常量**：`HUB_ENV_PREFIX = os.path.join(INSTALL_PREFIX, "hub")`，即 `/opt/tljh/hub`
- **运行身份**：以 root 用户运行（jupyterhub.service 中 `User=root`）
- **核心组件**：
  - JupyterHub 5.x（多用户管理核心）
  - jupyterhub-systemdspawner（systemd 进程管理）
  - jupyterhub-traefik-proxy（文件代理模式）
  - 各种认证器（FirstUse/Native/LDAP/OAuth/Tmp）
  - jupyterhub-idle-culler（空闲服务清理）
- **安装方式**：先通过 apt 安装 libssl-dev/libcurl4-openssl-dev/build-essential，然后 pip 安装 `requirements-hub-env.txt`

### User 环境（/opt/tljh/user）

User 环境是一个 Miniforge（Conda）环境，所有 Jupyter Notebook/Lab 实例均在此环境中运行。

- **路径常量**：`USER_ENV_PREFIX = os.path.join(INSTALL_PREFIX, "user")`，即 `/opt/tljh/user`
- **核心包**：
  - Notebook ≥7.2, <8
  - JupyterLab ≥4.2, <5
  - nbgitpuller（Git 内容拉取）
  - jupyter-resource-usage（资源使用显示）
  - ipywidgets
- **共享特性**：所有用户共享同一个 Conda 环境——管理员安装一次包，所有用户立即可用
- **安装方式**：下载 Miniforge 24.7.1-2（含 SHA256 校验），创建独立 Conda 环境

### 环境桥接机制

两个环境通过 SystemdSpawner 的 `extra_paths` 配置桥接：

```python
c.SystemdSpawner.extra_paths = ["/opt/tljh/user/bin"]
c.SystemdSpawner.default_shell = "/bin/bash"
```

这意味着用户的 Notebook 服务器进程（在用户权限下运行）的 PATH 中包含 `/opt/tljh/user/bin`，从而使用 User 环境的 Python 和包，但 Hub 进程本身不使用 User 环境。

## 为什么不是每人一个环境？

TLJH 面向1-100用户的小规模场景。在这种规模下：

1. **简化管理**：管理员只需 `sudo -E conda install` 或 `sudo -E pip install` 一次
2. **节省磁盘**：避免每个用户重复安装相同的包
3. **快速启动**：用户启动服务器时无需创建新环境
4. **一致性**：所有用户使用相同版本的包，减少兼容性问题

对于需要隔离环境的高级场景，可使用 Conda 内核或 DockerSpawner 插件扩展。

## Systemd 服务模型

TLJH 完全依赖 systemd 管理进程生命周期。

### jupyterhub.service

- **依赖**：Requires=traefik.service, After=traefik.service
- **安全沙箱**：PrivateTmp=yes, PrivateDevices=yes, ProtectKernelTunables=yes, ProtectKernelModules=yes
- **自动重启**：Restart=always
- **工作目录**：`/opt/tljh/state`
- **启动命令**：`/opt/tljh/hub/bin/python -m jupyterhub -f /opt/tljh/config/jupyterhub_config.py --upgrade-db`

### traefik.service

- **依赖**：After=network.target
- **安全沙箱**：ProtectHome=yes, ProtectSystem=strict, ReadWritePaths=state/rules 和 state/acme.json
- **自动重启**：Restart=always
- **启动命令**：`/opt/tljh/hub/bin/traefik -c /opt/tljh/state/traefik.toml`

### 用户服务（jupyter-{USERNAME}）

- **命名模板**：`c.SystemdSpawner.unit_name_template = "jupyter-{USERNAME}"`
- **用户名映射**：`c.SystemdSpawner.username_template = "jupyter-{USERNAME}"`（系统用户名）
- **创建时机**：用户首次登录时由 UserCreatingSpawner 动态创建

## 用户进程创建流程

1. 用户通过浏览器访问 Traefik（端口80/443）
2. Traefik 将请求路由到 JupyterHub（端口15001）
3. 用户认证成功后，JupyterHub 通过 SystemdSpawner spawn 用户服务器
4. UserCreatingSpawner.start()：
   - 生成系统用户名（规范化长用户名）
   - 确保系统用户存在（`useradd --create-home`）
   - 将用户加入 jupyterhub-users 组
   - 管理员额外加入 jupyterhub-admins 组（获得 sudo 权限）
   - 启动 systemd 服务运行 Notebook 服务器
5. JupyterHub 将路由信息写入 rules.toml
6. Traefik 监听到文件变化，自动更新路由
7. 用户请求通过 Traefik 路由到用户的 Notebook 服务器

## 配置与状态分离

```
/opt/tljh/
├── config/           # 配置（持久化，用户编辑）
│   ├── config.yaml
│   └── jupyterhub_config.d/
└── state/            # 状态（运行时生成，不手动编辑）
    ├── traefik.toml
    ├── rules/
    ├── acme.json
    └── passwords.dbm
```

配置目录权限为 0o700（仅 root 可访问），因为其中可能包含密钥等敏感信息。

## 下一步

- [配置系统](03-config-system.md)：学习如何使用 tljh-config 管理配置
- [用户管理](04-user-management.md)：理解用户创建和权限管理
- [Traefik 代理](05-traefik-proxy.md)：深入了解反向代理和 HTTPS 配置
- [插件系统](06-plugin-system.md)：通过插件扩展 TLJH 功能
