---
title: TLJH 安装流程深度解析
description: 深入解析 TLJH 的两阶段安装流程：bootstrap 引导和 installer 完整安装
type: Explanation
tags: [concept, installation, bootstrap, installer, conda, miniforge, systemd, jupyterhub, tljh, devops]
sources:
  - id: tljh-bootstrap
    title: bootstrap/bootstrap.py
  - id: tljh-installer
    title: tljh/installer.py
  - id: tljh-conda
    title: tljh/conda.py
  - id: tljh-apt
    title: tljh/apt.py
---

# TLJH 安装流程深度解析

TLJH 的安装采用经典的**两阶段引导**设计：第一阶段 bootstrap.py 零依赖引导环境，第二阶段 installer.py 在已建立的环境中完成完整安装。

## 两阶段设计原理

bootstrap.py 和 installer.py 中各有一份 `run_subprocess` 函数副本，源码注释明确说明：

> "Copied into bootstrap/bootstrap.py. Make sure these two copies are exactly the same!"

这是因为 bootstrap 阶段**不能依赖 tljh 包**（包尚未安装），必须完全自包含，仅使用 Python 标准库。这是引导程序的经典约束。

## 阶段1：Bootstrap 引导

bootstrap.py 是安装入口，设计为仅依赖 Python 标准库。

### 1.1 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TLJH_INSTALL_PREFIX` | 安装根目录 | `/opt/tljh` |
| `TLJH_BOOTSTRAP_PIP_SPEC` | TLJH 包的 pip 安装路径 | PyPI 上的 the-littlest-jupyterhub |
| `TLJH_BOOTSTRAP_DEV` | 是否为开发模式（yes/no） | no |

### 1.2 系统兼容性检查

`ensure_host_system_can_install_tljh()` 执行以下检查：

1. **发行版检查**：读取 `/etc/os-release`，确认是 `ubuntu` 或 `debian`
2. **版本检查**：Ubuntu ≥22.04，Debian ≥11（通过 `_check_os_version_greater_or_equal`）
3. **Python 版本**：≥3.9（Ubuntu 22.04/Debian 11 默认 Python3 满足）
4. **systemd 检查**：`which systemctl` 必须存在
5. **架构检查**：通过 Miniforge URL 函数验证架构支持

不满足任何检查则打印错误信息并 `sys.exit(1)`。

### 1.3 Python 3.8 兼容处理

如果检测到 Python 3.8（某些旧系统），会打印清晰的错误信息：

```
The Littlest JupyterHub requires Python >= 3.9 but {version_str} was found.
Please upgrade to Python 3.9 or newer to install TLJH.
```

### 1.4 参数解析

bootstrap 支持的 CLI 参数：

| 参数 | 说明 |
|------|------|
| `--show-progress-page` | 启动 HTTP 服务器在端口80显示安装进度 |
| `--version <ver>` | 指定安装版本（latest/分支/commit/部分版本号） |
| `--admin <user>` | 管理员用户名（可多次指定） |
| `--user-requirements-txt-url <url>` | 用户环境额外 requirements URL |
| `--plugin <plugin>` | 要安装的插件（可多次指定） |
| `--progress-page-server-pid <pid>` | 进度页服务器 PID（installer 用） |

其余参数透传给 `tljh.installer:main`。

### 1.5 进度页服务器

指定 `--show-progress-page` 时，bootstrap 在端口80启动一个 HTTP 服务器：

- `GET /logs`：读取 installer.log 日志文件
- `GET /` → 302 重定向到 `/index.html`
- `GET /index.html`：安装进度 HTML 页面
- `GET /favicon.ico`：favicon

### 1.6 版本解析

`_resolve_git_version(version)` 通过 `git ls-remote --tags` 解析版本：

- `latest` → 最新 tag（排除含 `-` 的预发布版）
- 部分版本号（如 `1.0`）→ 匹配 `v1.0.*` 中最新的 tag
- 分支名/commit hash → 原样返回

### 1.7 基础环境准备

新安装时（INSTALL_PREFIX 不存在）：

1. **apt 安装基础工具**：`python3`、`python3-venv`、`python3-pip`、`git`、`sudo`
   - 设置 `DEBIAN_FRONTEND=noninteractive`
2. **创建 Hub 虚拟环境**：`python3 -m venv /opt/tljh/hub`
3. **升级 pip**：`hub/bin/python -m pip install --upgrade pip`
4. **安装 TLJH 包**：`hub/bin/pip install the-littlest-jupyterhub`（或 PIP_SPEC）

### 1.8 切换到 Installer

最后一步通过 `os.execv` 替换当前进程：

```python
os.execv(hub_env_python, [hub_env_python, "-m", "tljh.installer"] + flags)
```

这是关键的阶段切换点——进程替换为 hub 环境中的 Python 执行 installer 模块。

## 阶段2：Installer 完整安装

installer.main() 在 hub 环境中执行完整安装。

### 2.1 插件设置

`setup_plugins(plugins)`：
1. 如果指定了 `--plugin` 参数，先 pip 安装插件包
2. 创建 `pluggy.PluginManager("tljh")`
3. 注册 hookspecs（`tljh.hooks`）
4. 通过 `load_setuptools_entrypoints("tljh")` 自动发现所有插件

### 2.2 配置目录初始化

`ensure_config_yaml(plugin_manager)`：
1. 创建 CONFIG_DIR（/opt/tljh/config），权限 0o700
2. 创建 jupyterhub_config.d 子目录，权限 0o700
3. 执行 `migrator.migrate_config_files()` 迁移旧配置
4. 调用 `tljh_config_post_install` 插件钩子修改 config dict
5. 将配置写回 config.yaml

### 2.3 管理员账户设置

`ensure_admins(admin_password_list)`：
1. 创建 STATE_DIR（/opt/tljh/state），权限 0o700
2. 解析 `username:password` 格式的参数
3. 未指定密码的管理员使用空密码
4. 使用 **bcrypt** hash 密码
5. 存储到 STATE_DIR/passwords.dbm（dbm 格式），权限 0o600
6. 将管理员用户名写入 config.yaml 的 users.admin 列表

### 2.4 用户组创建

`ensure_usergroups()`：
1. 创建 `jupyterhub-admins` 组
2. 创建 `jupyterhub-users` 组
3. 写入 `/etc/sudoers.d/jupyterhub-admins`：
   - `%jupyterhub-admins ALL=(ALL) NOPASSWD:ALL`
   - 将所有 jupyter-* 用户加入 exempt_group（密码过期豁免）

### 2.5 用户 Conda 环境设置

`ensure_user_environment(user_requirements_txt_file)`：

1. **架构检测**：通过 `os.uname().machine` 获取架构
2. **新环境检测**：USER_ENV_PREFIX 不存在则为新安装
3. **下载 Miniforge**：
   - 版本：Miniforge3-24.7.1-2
   - URL 格式：`https://github.com/conda-forge/miniforge/releases/download/{ver}/Miniforge3-{ver}-Linux-{arch}.sh`
   - 支持 aarch64 和 x86_64 架构，其他架构抛 ValueError
   - SHA256 校验（MINIFORGE_CHECKSUMS 字典）
4. **安装 Miniforge**：执行 `/bin/bash installer -u -b -p /opt/tljh/user`
   - `-u`：接受用户协议
   - `-b`：batch 模式（无交互）
   - `-p`：安装前缀
5. **版本检查**：确认 conda ≥4.10、mamba ≥0.16.0、pip ≥23.1.2、python ≥3.9
   - 版本解析使用 `parse_version`（提取数字元组比较）
6. **升级工具**：conda、mamba、pip 升级到最低要求版本
7. **安装 JupyterHub**（user 环境中也需要）
8. **安装用户额外包**：requirements-user-env-extras.txt（notebook、jupyterlab、nbgitpuller 等）
9. **安装用户自定义 requirements**（如果指定了 URL）

包安装优先级：apt 包 → hub pip 包 → user conda 包 → user pip 包。

### 2.6 Hub 环境安装

`ensure_jupyterhub_package(prefix)`：
1. **apt 依赖**：libssl-dev、libcurl4-openssl-dev、build-essential
2. **pip 安装 requirements-hub-env.txt**：JupyterHub、各种认证器、traefik-proxy、pycurl 等

### 2.7 Traefik 二进制下载

`traefik.ensure_traefik_binary(prefix)`：
1. 使用 `@backoff.on_exception(backoff.expo, max_tries=2)` 重试装饰
2. 检查已存在二进制的版本（`traefik version`），匹配则跳过
3. 不匹配则删除旧版本
4. 从 GitHub releases 下载 `traefik_v3.6.5_linux_{arch}.tar.gz`
5. SHA256 校验验证
6. 解压 traefik 二进制到 hub/bin/
7. chmod 0o755

### 2.8 进度页服务器停止

如果通过 bootstrap 启动了进度页 HTTP 服务器，向其 PID 发送 SIGINT 停止。

### 2.9 Systemd 服务安装

`ensure_jupyterhub_service(prefix)`：
1. `remove_chp()`：停止并卸载 configurable-http-proxy.service（从旧版本迁移）
2. `systemd.reload_daemon()`：systemctl daemon-reload
3. **生成 Traefik API 密码**：32字节 hex 随机字符串，写入 STATE_DIR/traefik-api.secret
4. **渲染 Traefik 配置**：调用 `traefik.ensure_traefik_config` 生成 TOML 文件
5. **安装 systemd 单元**：
   - 读取 `systemd-units/jupyterhub.service` Jinja2 模板
   - 渲染 install_prefix、python_interpreter_path、jupyterhub_config_path
   - 写入 /etc/systemd/system/jupyterhub.service
   - 同理安装 traefik.service
6. **启动并启用服务**：
   - `systemd.restart_service("jupyterhub")`
   - `systemd.restart_service("traefik")`
   - `systemd.enable_service("jupyterhub")`
   - `systemd.enable_service("traefik")`

### 2.10 等待 JupyterHub 启动

`ensure_jupyterhub_running(times=20)`：
- 最多等待 20×1 = 20 秒
- 每秒 HTTP GET `http://127.0.0.1`
- 收到 200 响应表示 JupyterHub 就绪
- 超时抛异常

### 2.11 符号链接创建

`ensure_symlinks(prefix)`：
- 创建 `/usr/bin/tljh-config → /opt/tljh/hub/bin/tljh-config`
- 如果目标已存在且不是正确的符号链接，抛 FileExistsError（需要手动处理冲突）

### 2.12 插件后置操作

`run_plugin_actions(plugin_manager)`：按顺序执行插件安装钩子：
1. 收集并安装 `tljh_extra_apt_packages`（apt 包）
2. 收集并安装 `tljh_extra_hub_pip_packages`（hub pip 包）
3. 收集 conda channels 和 packages，安装 user conda 包
4. 收集并安装 `tljh_extra_user_pip_packages`（user pip 包）
5. 执行 `tljh_post_install()` 钩子

## Conda 环境管理细节

### Miniforge vs Miniconda

TLJH 使用 Miniforge（conda-forge 社区维护的发行版）而非 Anaconda 的 Miniconda，默认 channel 为 conda-forge。

### Mamba 优先

`ensure_conda_packages` 优先使用 mamba（C++ 实现的更快 conda 替代），mamba 不存在时回退到 conda。

### 包版本检查

安装后通过 `conda list --json` 获取已安装包版本，使用 `parse_version`（提取数字元组）与 MINIMUM_VERSIONS 比较。

### 文件权限

`fix_permissions(prefix)` 在 conda 安装后执行：
- `chown -R` 当前用户:组
- `chmod -R o-w`（移除其他用户写权限）

## APT 包管理

### GPG 密钥和源添加

- `trust_gpg_key(key)`：通过 stdin 执行 apt-key add
- `add_source(name, source_url, section)`：解析 VERSION_CODENAME，写入 sources.list.d
- 重复添加源时检测避免重复

### 包安装

`install_packages(packages)`：
- 检查 `/var/lib/apt/lists` 是否为空（是否需要 apt update）
- 设置 `DEBIAN_FRONTEND=noninteractive`
- 执行 `apt-get install --yes`

## 安装日志

所有安装日志输出到 `/opt/tljh/installer.log`，同时输出到 stderr。日志配置在 `log.init_logging()` 中设置。

## 重新执行安装

installer 可以在已安装的系统上重复执行，是**幂等的**：
- 已存在的包不重复安装
- 配置不会被覆盖（除非插件修改）
- 服务会被重启
- 符号链接已正确存在时跳过

```bash
sudo /opt/tljh/hub/bin/python -m tljh.installer
```

## 下一步

- [安装指南](01-installation.md)：快速安装步骤
- [架构概览](02-architecture.md)：理解安装后的系统架构
- [基础安装示例](../examples/01-basic-install.md)：完整安装示例
