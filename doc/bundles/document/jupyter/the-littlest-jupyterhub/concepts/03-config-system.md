---
title: TLJH 配置系统与 tljh-config
description: 掌握 tljh-config 命令行工具、YAML 配置结构和配置生效机制
type: How-To
tags: [concept, config, tljh-config, yaml, jupyterhub, tljh, devops]
sources:
  - id: tljh-config
    title: tljh/config.py
  - id: tljh-config-schema
    title: tljh/config_schema.py
  - id: tljh-configurer
    title: tljh/configurer.py
  - id: tljh-yaml
    title: tljh/yaml.py
---

# TLJH 配置系统与 tljh-config

TLJH 使用声明式 YAML 配置文件管理所有设置，通过 `tljh-config` 命令行工具进行读写。配置变更后需要 reload 服务才能生效。

## 配置文件位置

主配置文件位于 `/opt/tljh/config/config.yaml`，使用 YAML 格式。所有配置操作都通过 `tljh-config` 命令完成，也可以直接编辑该文件。

> ⚠️ 配置目录权限为 0o700，需要 sudo 才能访问。

## tljh-config 命令

tljh-config 是 TLJH 的配置管理 CLI，入口点为 `tljh-config = tljh.config:main`。

### 查看配置

```bash
sudo tljh-config show
```

读取 config.yaml 并以 YAML 格式输出到 stdout。如果文件不存在则输出空配置。

### 设置值

```bash
sudo tljh-config set <property-path> <value>
```

使用**点分路径**语法设置配置项。值会被自动解析：

- `"none"` → `None`
- 纯数字 → 整数
- 含小数点的数字 → 浮点数
- `"true"`/`"false"` → 布尔值
- 其他 → 字符串

示例：

```bash
sudo tljh-config set https.enabled true
sudo tljh-config set http.port 8080
sudo tljh-config set https.letsencrypt.email admin@example.com
```

### 删除值

```bash
sudo tljh-config unset <property-path>
```

删除配置项，递归清理空的父节点。

### 列表操作

向列表追加值：

```bash
sudo tljh-config add-item <property-path> <value>
sudo tljh-config add-item users.admin alice
```

从列表移除值：

```bash
sudo tljh-config remove-item <property-path> <value>
sudo tljh-config remove-item users.admin alice
```

### 重载服务

配置修改后必须 reload 才能生效：

```bash
# 重载 Hub（重启 jupyterhub 服务）
sudo tljh-config reload hub

# 重载代理（重新生成 Traefik 配置并重启 traefik 服务）
sudo tljh-config reload proxy

# 重载所有（hub + proxy）
sudo tljh-config reload
```

Hub reload 会：重启 jupyterhub systemd 服务 → 等待 HTTP 健康检查通过（最多等待 20 秒，每秒检查一次）。

Proxy reload 会：重新渲染 Traefik TOML 配置 → 重启 traefik 服务。

### 全局参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config-path <path>` | 指定配置文件路径 | `/opt/tljh/config/config.yaml` |
| `--validate` / `--no-validate` | 是否使用 JSON Schema 校验配置 | `--validate` |

## 配置 Schema

配置使用 JSON Schema Draft-07 校验，顶层允许的键：

| 键 | 类型 | 说明 |
|----|------|------|
| `base_url` | string | JupyterHub 基础 URL 路径，默认 `/` |
| `auth` | object | 认证配置（动态，按类名配置） |
| `users` | object | 用户列表配置 |
| `limits` | object | 资源限制（内存/CPU） |
| `http` | object | HTTP 监听配置 |
| `https` | object | HTTPS/TLS 配置 |
| `traefik_api` | object | Traefik API 凭证 |
| `services` | object | JupyterHub 服务配置（如 idle culler） |
| `user_environment` | object | 用户环境配置（默认应用） |

Schema 中设置了 `additionalProperties: false`，不允许未定义的顶层键。

### users 配置

```yaml
users:
  admin:          # 管理员用户名列表
    - alice
  allowed:        # 允许登录的用户列表（空表示允许所有）
    []
  banned:         # 禁止登录的用户列表
    []
  extra_user_groups:  # 额外用户组映射
    groupname:
      - username
```

### http/https 配置

```yaml
http:
  address: ""     # 监听地址，空字符串表示所有接口
  port: 80

https:
  enabled: false
  address: ""
  port: 443
  letsencrypt:
    email: ""     # Let's Encrypt 通知邮箱
    domains: []   # 域名列表
    staging: false
  tls:
    key: ""       # TLS 私钥路径
    cert: ""      # TLS 证书路径
```

### limits 配置

```yaml
limits:
  memory: null    # 内存限制，如 "4G"、"2G"
  cpu: null       # CPU 限制，如 2.0（表示2核）
```

### user_environment 配置

```yaml
user_environment:
  default_app: "jupyterlab"  # jupyterlab 或 classic
```

- `jupyterlab` → 默认 URL 为 `/lab`
- `classic` → 默认 URL 为 `/tree`

### services.cull 配置（空闲用户清理）

```yaml
services:
  cull:
    enabled: true
    timeout: 600       # 空闲超时（秒），默认600（10分钟）
    every: 60          # 检查间隔（秒）
    concurrency: 5     # 并发清理数
    users: false       # 是否清理空闲用户
    max_age: 0         # 最大存活时间（0=不限）
    remove_named_servers: false
```

## 配置应用机制

### 默认配置

`configurer.py` 中的 `default` 字典定义了所有配置项的默认值。用户配置通过 `_merge_dictionaries` 递归合并覆盖默认值。

### 配置应用流程

1. `load_config()` 读取 config.yaml，合并默认配置和 secrets（traefik-api.secret）
2. `apply_config()` 按顺序调用各模块 update 函数：
   - `update_base_url` → 设置 c.JupyterHub.base_url
   - `update_auth` → 设置认证器类和配置
   - `update_userlists` → 设置 allowed/blocked/admin 用户列表
   - `update_usergroups` → 设置额外用户组
   - `update_limits` → 设置内存/CPU 限制
   - `update_user_environment` → 设置默认应用（JupyterLab/Classic）
   - `update_user_account_config` → 设置 SystemdSpawner 用户名模板
   - `update_traefik_api` → 设置 Traefik API 凭证和入口点
   - `update_services` → 配置 idle culler 等服务
3. 调用插件钩子 `tljh_custom_jupyterhub_config(c)`
4. 加载 `jupyterhub_config.d/*.py` 额外配置文件

### 认证器配置约定

认证配置采用动态类名约定：`auth` 对象中以大写字母开头的键被视为认证器类名。

```yaml
auth:
  type: github
  GitHubOAuthenticator:
    client_id: "xxx"
    client_secret: "xxx"
    oauth_callback_url: "https://example.com/hub/oauth_callback"
```

`update_auth` 函数遍历 `auth` 配置中所有大写字母开头的键，将其值设置为 `c[ClassName]` 的属性。

### 并发安全

配置文件操作使用文件锁（FileLock），锁文件为 `config.yaml.lock`，超时 1 秒，防止并发写入导致数据损坏。

## 直接编辑配置文件

也可以直接编辑 `/opt/tljh/config/config.yaml`，但编辑后必须执行：

```bash
sudo tljh-config reload
```

直接编辑时注意：

- 使用正确的 YAML 缩进（2空格）
- 布尔值用 `true`/`false`（小写）
- 编辑后最好用 `sudo tljh-config show` 验证格式正确

## 逃生舱：自定义 jupyterhub_config.py

对于 tljh-config 无法覆盖的高级配置，可在 `/opt/tljh/config/jupyterhub_config.d/` 目录下创建 `.py` 文件：

```bash
sudo nano /opt/tljh/config/jupyterhub_config.d/my_custom.py
```

```python
# 可直接使用 JupyterHub traitlets 配置对象 c
c.Spawner.default_url = "/lab"
c.JupyterHub.active_server_limit = 20
```

这些文件在 JupyterHub 启动时被加载，优先级最高（最后执行），可覆盖任何配置。

## 配置迁移

TLJH 内置迁移机制（migrator.py），会自动将旧版本的配置文件路径迁移到新位置：

- 旧 config.yaml → 新 CONFIG_DIR/config.yaml
- 旧 jupyterhub_config.d/ → CONFIG_DIR/jupyterhub_config.d/

迁移时如果目标文件已存在，旧文件会被重命名为 `{path}.old.YYYY-MM-DD` 避免覆盖。

## 下一步

- [用户管理](04-user-management.md)：添加用户、设置管理员、配置认证
- [配置基础操作示例](../examples/02-config-basics.md)：常用配置操作示例
- [GitHub OAuth 认证示例](../examples/03-github-auth.md)：配置第三方认证
