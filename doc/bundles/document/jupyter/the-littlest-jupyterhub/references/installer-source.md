---
type: Reference
title: installer.py 源码信源
description: tljh/installer.py 模块公共 API 信源文档
tags: [reference, source, installer, installation, api]
sources:
  - id: tljh-installer
    title: tljh/installer.py
---

# installer.py 源码信源

> TLJH 安装逻辑核心模块。负责协调所有安装步骤：插件设置、配置初始化、用户组创建、Conda 环境安装、Traefik 二进制下载、Systemd 服务安装等。

## 模块常量

```python
MINIFORGE_VERSION = "24.7.1-2"
MINIFORGE_CHECKSUMS = {
    "aarch64": "7bf60bce50f57af7ea4500b45eeb401d9350011ab34c9c45f736647d8dba9021",
    "x86_64": "636f7faca2d51ee42b4640ce160c751a46d57621ef4bf14378704c87c5db4fe3",
}
MINIMUM_VERSIONS = {
    "mamba": "0.16.0",
    "conda": "4.10",
    "pip": "23.1.2",
    "python": "3.9",
}
```

## 公共函数

### `remove_chp()`

停止、禁用、卸载 configurable-http-proxy.service。从旧版本迁移时调用。

### `ensure_jupyterhub_service(prefix)`

确保 JupyterHub 相关 systemd 服务正确安装和运行：
1. 调用 `remove_chp()` 移除旧代理
2. `systemd.reload_daemon()`
3. 如果 traefik-api.secret 不存在，生成 32 字节 hex 密钥
4. 调用 `traefik.ensure_traefik_config(STATE_DIR)` 渲染 Traefik 配置
5. 渲染并安装 jupyterhub.service 和 traefik.service 单元
6. 重启并 enable 两个服务

### `ensure_jupyterhub_package(prefix)`

在 Hub 环境安装 JupyterHub 包：
1. apt 安装 libssl-dev、libcurl4-openssl-dev、build-essential
2. pip install requirements-hub-env.txt（含 upgrade）

### `ensure_usergroups()`

设置用户组和 sudo 规则：
1. 创建 jupyterhub-admins 和 jupyterhub-users 组
2. 写入 `/etc/sudoers.d/jupyterhub-admins`：
   - `%jupyterhub-admins ALL = (ALL) NOPASSWD: ALL`
   - `Defaults exempt_group = jupyterhub-admins`

### `_miniforge_url(version=MINIFORGE_VERSION, arch=None) → (url, checksum)`

返回 Miniforge 下载 URL 和 SHA256 校验和。arch 默认为 `os.uname().machine`，不支持的架构抛 ValueError。

### `ensure_user_environment(user_requirements_txt_file)`

设置 User Conda 环境：
1. 检查 Linux 系统
2. 检测现有环境状态（新安装/已有环境）
3. 新安装时下载并安装 Miniforge（SHA256 校验）
4. 检查 Python ≥3.9
5. 升级 conda/mamba/pip 到最低版本
6. 非新安装时强制重装 conda/mamba（修复依赖一致性）
7. 安装 jupyterhub 到 user 环境
8. 新安装时安装 requirements-user-env-extras.txt
9. 安装用户自定义 requirements URL

### `ensure_admins(admin_password_list)`

设置管理员账户：
1. 创建 STATE_DIR（0o700）
2. 解析 `username:password` 对，bcrypt hash 密码存入 passwords.dbm（0o600）
3. 无密码的管理员仅添加用户名到列表
4. 将 admin 列表写入 config.yaml users.admin

### `ensure_jupyterhub_running(times=20)`

等待 JupyterHub 就绪：最多 times 次循环，每秒 HTTP GET http://127.0.0.1，忽略 SSL 警告。404/502/503 视为临时状态继续等待，其他异常立即抛出。超时抛 Exception。

### `ensure_symlinks(prefix)`

创建符号链接：
- `/usr/bin/tljh-config → prefix/bin/tljh-config`
- 如果目标存在且不是正确的链接，抛 FileExistsError

### `setup_plugins(plugins=None) → pm`

设置插件基础设施：
1. 如果指定 plugins 参数，pip install 到 Hub 环境
2. 创建 `pluggy.PluginManager("tljh")`
3. `pm.add_hookspecs(hooks)`
4. `pm.load_setuptools_entrypoints("tljh")`
5. 返回 PluginManager 实例

### `run_plugin_actions(plugin_manager)`

按顺序执行插件安装钩子：
1. tljh_extra_apt_packages → apt.install_packages
2. tljh_extra_hub_pip_packages → conda.ensure_pip_packages（Hub 环境）
3. tljh_extra_user_conda_channels/packa ges → conda.ensure_conda_packages（User 环境，默认 conda-forge）
4. tljh_extra_user_pip_packages → conda.ensure_pip_packages（User 环境）
5. tljh_post_install()

### `ensure_config_yaml(plugin_manager)`

确保 config.yaml 存在：
1. 创建 CONFIG_DIR 和 jupyterhub_config.d（0o700）
2. `migrator.migrate_config_files()`
3. 读取现有 config（或空 dict）
4. 调用 `tljh_config_post_install(config=config)` 插件钩子
5. 写回 config.yaml

### `main()`

CLI 入口，执行完整安装流程：
1. `init_logging()`
2. 解析参数：--admin、--user-requirements-txt-url、--plugin、--progress-page-server-pid
3. `setup_plugins(args.plugin)`
4. `ensure_config_yaml(pm)`
5. `ensure_admins(args.admin)`
6. `ensure_usergroups()`
7. `ensure_user_environment(args.user_requirements_txt_url)`
8. `ensure_jupyterhub_package(HUB_ENV_PREFIX)`
9. `traefik.ensure_traefik_binary(HUB_ENV_PREFIX)`
10. 停止进度页服务器（如果有 PID）
11. `ensure_jupyterhub_service(HUB_ENV_PREFIX)`
12. `ensure_jupyterhub_running()`
13. `ensure_symlinks(HUB_ENV_PREFIX)`
14. `run_plugin_actions(pm)`
15. 输出 "Done!"

## 模块依赖

- `tljh.apt`：APT 包管理
- `tljh.conda`：Conda 环境管理
- `tljh.hooks`：插件钩子规范
- `tljh.migrator`：配置迁移
- `tljh.systemd`：Systemd 服务管理
- `tljh.traefik`：Traefik 代理配置
- `tljh.user`：系统用户管理
- `tljh.config`：路径常量（CONFIG_DIR 等）
- `tljh.utils.parse_version`：版本号比较
- `tljh.yaml.yaml`：YAML 读写
- 第三方：`bcrypt`、`pluggy`、`requests`
