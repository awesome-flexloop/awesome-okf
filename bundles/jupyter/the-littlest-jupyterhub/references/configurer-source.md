---
type: Reference
title: configurer.py 源码信源
description: tljh/configurer.py 模块公共 API 信源文档
tags: [reference, source, configurer, traitlets, jupyterhub-config, api]
sources:
  - id: tljh-configurer
    title: tljh/configurer.py
---

# configurer.py 源码信源

> 将 YAML 配置转换为 JupyterHub Traitlets 配置对象的桥接模块。JupyterHub 启动时加载 jupyterhub_config.py，此模块负责将 config.yaml 中的声明式配置应用到 `c` 对象。

## 默认配置

```python
default = {
    "base_url": "/",
    "auth": {"type": "firstuseauthenticator.FirstUseAuthenticator"},
    "users": {
        "allowed": [],
        "banned": [],
        "admin": [],
        "extra_user_groups": {},
    },
    "limits": {"memory": None, "cpu": None},
    "http": {"address": "", "port": 80},
    "https": {"enabled": False, "address": "", "port": 443, "tls": {"key": "", "cert": ""}, "letsencrypt": {"email": "", "domains": [], "staging": False}},
    "traefik_api": {"ip": "127.0.0.1", "port": 8099, "username": "api_admin", "password": ""},
    "user_environment": {"default_app": "jupyterlab"},
    "services": {
        "cull": {"enabled": True, "timeout": 600, "every": 60, "concurrency": 5, "users": False, "max_age": 0, "remove_named_servers": False}
    },
}
```

## 公共函数

### `load_config(config_file) → dict`

加载 YAML 配置文件，递归合并 default、secrets（traefik-api.secret 密码）和文件配置：
1. 从 STATE_DIR/traefik-api.secret 读取 Traefik API 密码
2. 使用 `_merge_dictionaries` 合并 default → secrets → file_config
3. 返回合并后的配置 dict

### `apply_config(config_overrides, c)`

将配置应用到 JupyterHub Traitlets 配置对象 `c`：
1. 调用 `_merge_dictionaries(default, config_overrides)` 得到完整配置
2. 按顺序调用各 update 函数：
   - `update_base_url`
   - `update_auth`
   - `update_userlists`
   - `update_usergroups`
   - `update_limits`
   - `update_user_environment`
   - `update_user_account_config`
   - `update_traefik_api`
   - `update_services`

### `set_if_not_none(parent, key, value)`

当 value 不为 None 时，执行 `setattr(parent, key, value)`。

### `load_traefik_api_credentials() → str`

从 STATE_DIR/traefik-api.secret 读取并返回密码。

### `update_base_url(c, config)`

设置 `c.JupyterHub.base_url` 和 `c.TraefikFileProviderProxy.traefik_api_url`。

### `update_auth(c, config)`

设置认证器：
1. `c.JupyterHub.authenticator_class = auth_type`
2. 遍历 `config["auth"]` 中以大写字母开头的键（类名），将其值的非 None 项通过 `set_if_not_none` 设置到 `c[class_name]`

### `update_userlists(c, config)`

设置用户列表：
- `c.Authenticator.allowed_users = set(users.allowed)`
- `c.Authenticator.blocked_users = set(users.banned)`
- `c.Authenticator.admin_users = set(users.admin)`
- 默认认证器（FirstUseAuthenticator）且无 allowed 用户时，设置 `c.FirstUseAuthenticator.allow_all = True`

### `update_usergroups(c, config)`

设置 `c.UserCreatingSpawner.user_groups = users.extra_user_groups`。

### `update_limits(c, config)`

设置资源限制：
- `c.Spawner.mem_limit = limits.memory`
- `c.Spawner.cpu_limit = limits.cpu`

### `update_user_environment(c, config)`

根据 default_app 设置默认 URL：
- `jupyterlab` → `c.Spawner.default_url = "/lab"`
- `classic` → `c.Spawner.default_url = "/tree"`

### `update_user_account_config(c, config)`

设置 `c.SystemdSpawner.username_template = "jupyter-{USERNAME}"`。

### `update_traefik_api(c, config)`

设置 Traefik 代理配置：
- `c.TraefikProxy.traefik_api_username/password/url`
- 配置 HTTP/HTTPS 入口点路由

### `set_cull_idle_service(config) → dict`

构造 jupyterhub_idle_culler 服务定义：
- 命令包含 `--timeout/--cull-every/--concurrency/--max-age/--cull-users/--remove-named-servers` 参数
- 从 config.services.cull 读取参数值

### `update_services(c, config)`

设置 JupyterHub 服务列表：
1. 清空 `c.JupyterHub.services`
2. 如果 cull.enabled，追加 cull 服务

### `_merge_dictionaries(a, b, path=None, update=True) → dict`

递归合并字典：dict 类型递归合并，其他类型 b 覆盖 a。
