---
title: TLJH 用户管理与 SystemdSpawner
description: 理解用户创建流程、系统用户映射、权限管理和资源限制
type: Explanation
tags: [concept, users, systemdspawner, authentication, permissions, jupyterhub, tljh]
sources:
  - id: tljh-user-creating-spawner
    title: tljh/user_creating_spawner.py
  - id: tljh-user
    title: tljh/user.py
  - id: tljh-normalize
    title: tljh/normalize.py
  - id: tljh-configurer
    title: tljh/configurer.py
  - id: tljh-installer
    title: tljh/installer.py
---

# TLJH 用户管理与 SystemdSpawner

TLJH 通过自定义的 `UserCreatingSpawner` 扩展了 systemdspawner，实现了用户首次登录时自动创建系统用户、分配用户组和设置 sudo 权限。

## 用户创建流程

当用户首次登录 JupyterHub 时，`UserCreatingSpawner.start()` 方法被调用：

```
用户登录
  → UserCreatingSpawner.start()
    → generate_system_username() 生成系统用户名
    → user.ensure_user() 创建系统用户
    → 加入 jupyterhub-users 组
    → 管理员 → 加入 jupyterhub-admins 组（sudo 权限）
    → 普通用户 → 确保不在 jupyterhub-admins 组（无 sudo）
    → 加入配置的 extra_user_groups
    → super().start() 启动用户 Notebook 服务器
```

### 系统用户名生成

JupyterHub 用户名可能很长（如 OAuth 返回的邮箱地址），Linux 系统用户名限制为 32 字符。TLJH 使用 `generate_system_username` 函数规范化：

- 用户名长度 < 26：直接返回
- 用户名长度 ≥ 26：取前26字符 + `-` + SHA256 哈希前5字符
- 最终用户名格式为 `jupyter-{normalized_username}`（由 SystemdSpawner.username_template 控制）

示例：
- JupyterHub 用户名 `alice` → 系统用户名 `jupyter-alice`
- JupyterHub 用户名 `verylongemail@example.com` → `jupyter-verylongemail@exampl-abc12`

### 系统用户创建

`user.ensure_user(username)` 执行：

1. 通过 `pwd.getpwnam()` 检查用户是否已存在
2. 不存在则执行 `useradd --create-home` 创建用户及主目录
3. `chmod o-rwx` 保护用户主目录（其他用户无法读取）
4. 调用 `tljh_new_user_create` 插件钩子（允许插件对新用户做自定义操作）

## 用户组与权限

TLJH 使用两个核心用户组：

### jupyterhub-users 组

所有 JupyterHub 用户自动加入此组。

### jupyterhub-admins 组

管理员用户加入此组，通过 sudoers 配置获得完整 sudo 权限：

```
%jupyterhub-admins ALL=(ALL) NOPASSWD:ALL
```

这意味着管理员用户可以执行任何 sudo 命令而无需输入密码。这是 TLJH 的设计决策——管理员需要能安装系统包和 Python 包。

### Sudoers 配置

安装时写入 `/etc/sudoers.d/jupyterhub-admins`：

- `jupyterhub-admins` 组：`NOPASSWD:ALL`
- 所有 jupyter-* 用户被加入 exempt_group（密码过期豁免）

### 额外用户组

通过 `users.extra_user_groups` 配置可将用户加入额外的系统组：

```yaml
users:
  extra_user_groups:
    docker:
      - alice
      - bob
    staff:
      - alice
```

这在需要让特定用户访问 Docker、GPU 等资源时很有用。

## 用户管理命令

### 添加管理员

安装时指定：

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --admin alice
```

安装后通过 tljh-config：

```bash
sudo tljh-config add-item users.admin alice
sudo tljh-config reload hub
```

### 管理员密码

管理员密码使用 bcrypt 哈希存储在 `/opt/tljh/state/passwords.dbm`（dbm 格式，权限 0o600）。首次登录时通过 FirstUseAuthenticator 设置。

### 允许/禁止用户

```bash
# 设置白名单（只有这些用户可登录）
sudo tljh-config add-item users.allowed alice
sudo tljh-config add-item users.allowed bob

# 禁止特定用户
sudo tljh-config add-item users.banned baduser
sudo tljh-config reload hub
```

默认情况下（使用 FirstUseAuthenticator 且未设置 allowed 列表），任何人都可以登录并创建账户。设置 allowed 后，仅白名单用户可登录。

### 删除用户

```bash
# 从系统中删除用户
sudo deluser --remove-home jupyter-alice
# 从配置中移除
sudo tljh-config remove-item users.admin alice
sudo tljh-config reload hub
```

## 认证方式

TLJH 内置多种认证器，通过 `auth.type` 配置选择：

| 认证器 | auth.type | 说明 |
|--------|-----------|------|
| FirstUseAuthenticator | `firstuseauthenticator.FirstUseAuthenticator` | 默认，首次登录设置密码 |
| NativeAuthenticator | `nativeauthenticator.NativeAuthenticator` | 支持注册/邀请码 |
| LDAPAuthenticator | `ldapauthenticator.LDAPAuthenticator` | 企业 LDAP 认证 |
| OAuthenticator | `oauthenticator.*` | GitHub/Google/Globus 等 OAuth |
| TmpAuthenticator | `tmpauthenticator.TmpAuthenticator` | 临时匿名用户 |

### 认证器配置约定

认证器配置通过 `auth.{ClassName}.{property}` 点分路径设置。任何以大写字母开头的 auth 子键被视为认证器类名：

```yaml
auth:
  type: oauthenticator.github.GitHubOAuthenticator
  GitHubOAuthenticator:
    client_id: "xxx"
    client_secret: "xxx"
    oauth_callback_url: "https://example.com/hub/oauth_callback"
```

对应 tljh-config 命令：

```bash
sudo tljh-config set auth.type oauthenticator.github.GitHubOAuthenticator
sudo tljh-config set auth.GitHubOAuthenticator.client_id xxx
sudo tljh-config set auth.GitHubOAuthenticator.client_secret xxx
```

## 资源限制

通过 `limits` 配置限制每个用户服务器的资源：

```yaml
limits:
  memory: "4G"   # 内存限制，如 "512M", "2G", "4G"
  cpu: 2.0        # CPU 核心数限制
```

- `memory` 设置 c.Spawner.mem_limit（SystemdSpawner 映射到 cgroup MemoryMax）
- `cpu` 设置 c.Spawner.cpu_limit（映射到 cgroup CPUQuota）

设置为 `null` 表示不限制（默认）。

## 用户服务器管理

每个用户的 Notebook 服务器作为独立的 systemd 服务运行：

- 服务名模板：`jupyter-{username}`
- 运行身份：对应的系统用户（非 root）
- 环境：使用 User Conda 环境（`/opt/tljh/user/`）
- 默认 Shell：bash
- 自动重启：Hub 重启时不清理服务器（`c.JupyterHub.cleanup_servers = False`）

### 服务器启动/停止

- 用户首次访问 → 自动 spawn
- 用户在控制面板点击 "Stop My Server" → 停止 systemd 服务
- 空闲超时 → idle culler 自动停止（配置见配置系统文档）

## 默认应用配置

用户登录后默认打开 JupyterLab 还是经典 Notebook：

```bash
# 默认 JupyterLab（/lab）
sudo tljh-config set user_environment.default_app jupyterlab

# 使用经典 Notebook（/tree）
sudo tljh-config set user_environment.default_app classic
sudo tljh-config reload hub
```

## 在用户环境中安装包

管理员可在 User 环境中安装包，所有用户立即可用：

```bash
# conda 安装
sudo -E conda install -c conda-forge numpy pandas

# pip 安装
sudo -E pip install scikit-learn

# 从 requirements.txt 安装
sudo -E pip install -r requirements.txt
```

> ⚠️ 必须使用 `sudo -E`，-E 保留环境变量以确保使用正确的 conda/pip。

用户也可以在自己的目录下使用 `pip install --user` 安装个人包，但这些包只对该用户可见。

## 下一步

- [配置系统](03-config-system.md)：完整的配置选项参考
- [Traefik 代理](05-traefik-proxy.md)：HTTPS 和网络配置
- [配置基础操作示例](../examples/02-config-basics.md)：添加用户、修改配置
- [GitHub OAuth 示例](../examples/03-github-auth.md)：配置第三方认证
