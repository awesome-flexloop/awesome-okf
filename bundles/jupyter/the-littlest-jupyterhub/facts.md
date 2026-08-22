---
type: Facts
title: The Littlest JupyterHub 源码事实清单
description: R阶段产出：从零推测事实，每条事实指向具体源码位置
tags: [facts, source-code, evidence, verification, jupyterhub, tljh, jupyter, devops]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tljh-readme
    title: README.md
  - id: tljh-setup
    title: setup.py
  - id: tljh-pyproject
    title: pyproject.toml
  - id: tljh-installer
    title: tljh/installer.py
  - id: tljh-config
    title: tljh/config.py
  - id: tljh-config-schema
    title: tljh/config_schema.py
  - id: tljh-configurer
    title: tljh/configurer.py
  - id: tljh-hooks
    title: tljh/hooks.py
  - id: tljh-conda
    title: tljh/conda.py
  - id: tljh-user
    title: tljh/user.py
  - id: tljh-traefik
    title: tljh/traefik.py
  - id: tljh-systemd
    title: tljh/systemd.py
  - id: tljh-jupyterhub-config
    title: tljh/jupyterhub_config.py
  - id: tljh-yaml
    title: tljh/yaml.py
  - id: tljh-utils
    title: tljh/utils.py
  - id: tljh-log
    title: tljh/log.py
  - id: tljh-migrator
    title: tljh/migrator.py
  - id: tljh-normalize
    title: tljh/normalize.py
  - id: tljh-apt
    title: tljh/apt.py
  - id: tljh-user-creating-spawner
    title: tljh/user_creating_spawner.py
  - id: tljh-bootstrap
    title: bootstrap/bootstrap.py
---

# The Littlest JupyterHub 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 包名 `the-littlest-jupyterhub`，版本 `2.0.1.dev`，描述 "A small JupyterHub distribution"（setup.py L4-6）
- F-002: URL 为 https://github.com/jupyterhub/the-littlest-jupyterhub，作者 Jupyter Development Team，License 为 3 Clause BSD（setup.py L7-10）
- F-003: Python 版本要求 `>=3.9`（setup.py L13）
- F-004: 运行时依赖：`ruamel.yaml==0.18.*`、`jinja2`、`pluggy==1.*`、`backoff`、`filelock`、`requests`、`bcrypt`、`jupyterhub-traefik-proxy==2.*`（setup.py L14-23）
- F-005: 控制台入口点：`tljh-config = tljh.config:main`（setup.py L24-28）
- F-006: README 描述为 "The Littlest JupyterHub (TLJH) distribution helps you provide Jupyter Notebooks to 1-100 users on a single server"（README.md L11-12）
- F-007: 目标受众为 "people who do not consider themselves 'system administrators'"（README.md L14-15）
- F-008: 支持平台为 Debian 和 Ubuntu LTS 版本，amd64 或 arm64 架构（README.md L32）
- F-009: 使用 setuptools 构建系统，`find_packages()` 发现包，`include_package_data=True`（setup.py L3, L11-12）
- F-010: pyproject.toml 配置了 autoflake、isort（profile=black）、black（target py39-py313）、pytest 工具（pyproject.toml L5-46）

## 目录结构

- F-020: Python 包位于 `tljh/` 目录
- F-021: `tljh/` 包含文件：`__init__.py`（空文件）、`apt.py`、`conda.py`、`config.py`、`config_schema.py`、`configurer.py`、`hooks.py`、`installer.py`、`jupyterhub_config.py`、`log.py`、`migrator.py`、`normalize.py`、`systemd.py`、`traefik.py`、`traefik-dynamic.toml.tpl`、`traefik.toml.tpl`、`user.py`、`user_creating_spawner.py`、`utils.py`、`yaml.py`
- F-022: `tljh/systemd-units/` 包含：`jupyterhub.service`、`traefik.service`
- F-023: `tljh/requirements-hub-env.txt` 列出 Hub 环境依赖
- F-024: `tljh/requirements-user-env-extras.txt` 列出用户环境额外包
- F-025: `bootstrap/` 目录包含 `bootstrap.py`
- F-026: `tests/` 目录包含单元测试
- F-027: `integration-tests/` 目录包含集成测试和 Dockerfile

## 安装路径常量 `tljh/config.py`

- F-030: `INSTALL_PREFIX = os.environ.get("TLJH_INSTALL_PREFIX", "/opt/tljh")`（config.py L29）
- F-031: `HUB_ENV_PREFIX = os.path.join(INSTALL_PREFIX, "hub")`（config.py L30）
- F-032: `USER_ENV_PREFIX = os.path.join(INSTALL_PREFIX, "user")`（config.py L31）
- F-033: `STATE_DIR = os.path.join(INSTALL_PREFIX, "state")`（config.py L32）
- F-034: `CONFIG_DIR = os.path.join(INSTALL_PREFIX, "config")`（config.py L33）
- F-035: `CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")`（config.py L34）

## 配置系统 `tljh/config.py`

- F-040: `config_file_lock(config_path, timeout=1)` 是上下文管理器，使用 FileLock 获取配置文件锁，锁文件为 `{config_path}.lock`，超时1秒（config.py L37-50）
- F-041: `set_item_in_config(config, property_path, value)` 对点分路径设值，使用 deepcopy 不修改原 config，非叶节点不存在时创建 dict，设值是破坏性的（会替换已有子树）（config.py L53-78）
- F-042: `unset_item_from_config(config, property_path)` 删除点分路径的键，deepcopy 不修改原 config，删除后递归清理空 dict（config.py L81-123）
- F-043: `add_item_to_config(config, property_path, value)` 向点分路径的列表追加值，目标不存在或不是列表时初始化为空列表（config.py L126-149）
- F-044: `remove_item_from_config(config, property_path, value)` 从点分路径的列表中移除值，目标不是列表时抛 ValueError（config.py L152-172）
- F-045: `validate_config(config, validate)` 使用 jsonschema 对 config 做校验，schema 来自 config_schema.py；validate=True 时校验失败 sys.exit(1)，可用 --no-validate 跳过（config.py L175-193）
- F-046: `show_config(config_path)` 读取配置并 yaml.dump 到 stdout（config.py L196-201）
- F-047: `set_config_value`/`unset_config_value`/`add_config_value`/`remove_config_value` 四个函数均在 config_file_lock 内执行：读取当前配置→调用对应操作→validate_config→写回文件（config.py L204-253）
- F-048: `get_current_config(config_path)` 读取 YAML 文件返回 dict，FileNotFoundError 时返回空 dict（config.py L256-264）
- F-049: `check_hub_ready()` 通过 HTTP GET 请求 `http://{address}:{port}{base_url}/hub/api` 检查 Hub 是否就绪，返回 status_code==200（config.py L267-290）
- F-050: `reload_component(component)` 支持 'hub' 和 'proxy' 两种组件：hub 重启 jupyterhub 服务并等待就绪；proxy 重新生成 traefik 配置并重启 traefik 服务（config.py L293-315）
- F-051: `parse_value(value_str)` 解析字符串值：`"none"`→None、纯数字→int、浮点数字→float、`"true"/"false"`→bool、其余返回原字符串（config.py L318-332）
- F-052: `main(argv=None)` 是 tljh-config CLI 入口，先检查 os.geteuid()!=0 则报错退出；支持子命令：show、unset、set、add-item、remove-item、reload（config.py L343-446）
- F-053: CLI 支持 `--config-path`（默认 CONFIG_FILE）、`--validate`/`--no-validate`（默认 validate=True）参数（config.py L363-377）

## 配置 Schema `tljh/config_schema.py`

- F-060: config_schema 使用 JSON Schema draft-07（config_schema.py L8）
- F-061: 顶级 properties 包括：base_url（string）、user_environment、users、limits、https、http、traefik_api、services；additionalProperties=False（config_schema.py L119-129）
- F-062: Users 定义包含：extra_user_groups（object）、allowed（string array）、banned（string array）、admin（string array）（config_schema.py L14-22）
- F-063: HTTP 定义包含：address（ipv4 string）、port（integer）（config_schema.py L42-48）
- F-064: HTTPS 定义包含：enabled（boolean）、address（ipv4）、port（integer）、tls（TLS对象）、letsencrypt（LetsEncrypt对象）（config_schema.py L50-59）
- F-065: LetsEncrypt 定义包含：email（email格式）、domains（hostname array）、staging（boolean）（config_schema.py L61-72）
- F-066: TLS 定义包含：key（string）、cert（string）（config_schema.py L73-77）
- F-067: Limits 定义包含：memory（string|null）、cpu（number>=0|null）（config_schema.py L78-96）
- F-068: UserEnvironment 定义包含：default_app（enum: jupyterlab/classic，默认 jupyterlab）（config_schema.py L97-107）
- F-069: TraefikAPI 定义包含：ip（ipv4）、port（integer）、username（string）、password（string）（config_schema.py L108-117）
- F-070: Services.cull 定义包含：enabled（boolean）、timeout（integer）、every（integer）、concurrency（integer）、users（boolean）、max_age（integer）、remove_named_servers（boolean）（config_schema.py L24-40）

## 配置器 `tljh/configurer.py`

- F-080: `default` 字典定义默认配置：base_url="/"、auth.type="firstuseauthenticator.FirstUseAuthenticator"、users.allowed/banned/admin=[]、limits.memory/cpu=None、http.address="" port=80、https.enabled=False port=443、traefik_api.ip="127.0.0.1" port=8099 username="api_admin"、user_environment.default_app="jupyterlab"、services.cull.enabled=True timeout=600 every=60 concurrency=5（configurer.py L18-67）
- F-081: `load_config(config_file)` 读取 config.yaml 合并 default 配置和 secrets（traefik-api.secret），使用 `_merge_dictionaries` 递归合并（configurer.py L70-84）
- F-082: `apply_config(config_overrides, c)` 合并默认配置后依次调用：update_base_url、update_auth、update_userlists、update_usergroups、update_limits、update_user_environment、update_user_account_config、update_traefik_api、update_services（configurer.py L87-101）
- F-083: `set_if_not_none(parent, key, value)` 当 value 不为 None 时 setattr（configurer.py L104-109）
- F-084: `load_traefik_api_credentials()` 从 STATE_DIR/traefik-api.secret 读取密码（configurer.py L112-123）
- F-085: `update_auth(c, config)` 设置 c.JupyterHub.authenticator_class，遍历 auth 配置中大写字母开头的 dict 项作为类配置项，set_if_not_none 设置到 c[class_name]（configurer.py L143-192）
- F-086: `update_userlists(c, config)` 设置 c.Authenticator.allowed_users/blocked_users/admin_users；默认认证器且无 allowed 用户时设置 c.FirstUseAuthenticator.allow_all=True（configurer.py L195-211）
- F-087: `update_usergroups(c, config)` 设置 c.UserCreatingSpawner.user_groups（configurer.py L214-219）
- F-088: `update_limits(c, config)` 设置 c.Spawner.mem_limit 和 c.Spawner.cpu_limit（configurer.py L222-229）
- F-089: `update_user_environment(c, config)` 根据 default_app 设置 c.Spawner.default_url：jupyterlab→"/lab"，classic→"/tree"（configurer.py L232-242）
- F-090: `update_user_account_config(c, config)` 设置 c.SystemdSpawner.username_template = "jupyter-{USERNAME}"（configurer.py L245-246）
- F-091: `update_traefik_api(c, config)` 设置 TraefikProxy 凭证和入口点（http/https）（configurer.py L249-259）
- F-092: `set_cull_idle_service(config)` 构造 jupyterhub_idle_culler 服务命令，包含 --timeout/--cull-every/--concurrency/--max-age/--cull-users/--remove-named-servers 参数（configurer.py L262-285）
- F-093: `update_services(c, config)` 清空 c.JupyterHub.services，若 cull enabled 则追加 cull 服务（configurer.py L288-292）
- F-094: `_merge_dictionaries(a, b, path=None, update=True)` 递归合并字典，dict 类型递归合并，其他类型 b 覆盖 a（configurer.py L295-315）

## 插件系统 `tljh/hooks.py`

- F-100: 使用 pluggy 框架，`hookspec = pluggy.HookspecMarker("tljh")`，`hookimpl = pluggy.HookimplMarker("tljh")`（hooks.py L5-8）
- F-101: 定义 8 个 hookspec：`tljh_extra_user_conda_packages()`、`tljh_extra_user_conda_channels()`、`tljh_extra_user_pip_packages()`、`tljh_extra_hub_pip_packages()`、`tljh_extra_apt_packages()`、`tljh_custom_jupyterhub_config(c)`、`tljh_config_post_install(config)`、`tljh_post_install()`、`tljh_new_user_create(username)`（hooks.py L11-84）
- F-102: `tljh_extra_apt_packages` 返回的 apt 包在 pip/conda 包之前安装（hooks.py L40-45）
- F-103: `tljh_custom_jupyterhub_config(c)` 接收 JupyterHub 配置对象 c，可放置任意 jupyterhub_config.py 内容（hooks.py L48-55）
- F-104: `tljh_config_post_install(config)` 接收 dict-like config 对象，原地修改（hooks.py L58-67）
- F-105: `tljh_new_user_create(username)` 在新用户创建后执行（hooks.py L80-84）

## 安装器 `tljh/installer.py`

- F-110: MINIFORGE_VERSION = "24.7.1-2"（installer.py L140）
- F-111: MINIFORGE_CHECKSUMS 包含 aarch64 和 x86_64 两个架构的 sha256 值（installer.py L142-145）
- F-112: MINIMUM_VERSIONS = {"mamba": "0.16.0", "conda": "4.10", "pip": "23.1.2", "python": "3.9"}（installer.py L148-155）
- F-113: `remove_chp()` 停止、禁用、卸载 configurable-http-proxy.service（installer.py L38-56）
- F-114: `ensure_jupyterhub_service(prefix)` 移除 CHP、reload daemon、生成 traefik-api.secret（32字节hex）、渲染 traefik 配置、安装 jupyterhub.service 和 traefik.service systemd 单元、重启并 enable 两个服务（installer.py L59-96）
- F-115: `ensure_jupyterhub_package(prefix)` 安装 apt 依赖（libssl-dev/libcurl4-openssl-dev/build-essential），然后通过 conda.ensure_pip_requirements 安装 requirements-hub-env.txt（installer.py L99-117）
- F-116: `ensure_usergroups()` 创建 jupyterhub-admins 和 jupyterhub-users 组，写入 /etc/sudoers.d/jupyterhub-admins：admin 组 NOPASSWD:ALL，exempt_group（installer.py L120-135）
- F-117: `_miniforge_url(version, arch)` 构造 Miniforge 下载 URL，arch 从 os.uname().machine 获取，不支持的架构抛 ValueError（installer.py L158-175）
- F-118: `ensure_user_environment(user_requirements_txt_file)` 在 USER_ENV_PREFIX 设置 conda 环境：检测 Linux 系统→检测已有环境→新安装时下载 Miniforge→检查 Python 版本→升级 conda/mamba/pip→安装 jupyterhub→安装 requirements-user-env-extras.txt→安装用户自定义 requirements（installer.py L178-305）
- F-119: `ensure_admins(admin_password_list)` 创建 STATE_DIR（mode 0o700），解析 admin:password 对，bcrypt hash 密码存入 STATE_DIR/passwords.dbm（dbm 格式，0o600），将 admin 用户名写入 config.yaml users.admin（installer.py L308-343）
- F-120: `ensure_jupyterhub_running(times=20)` 循环最多 20 次（每次等1秒），HTTP GET http://127.0.0.1 检查 JupyterHub 是否启动（installer.py L346-377）
- F-121: `ensure_symlinks(prefix)` 创建符号链接 /usr/bin/tljh-config → prefix/bin/tljh-config；如果目标存在但不是正确链接则抛 FileExistsError（installer.py L380-405）
- F-122: `setup_plugins(plugins)` 安装插件 pip 包，创建 pluggy.PluginManager("tljh")，add_hookspecs(hooks)，load_setuptools_entrypoints("tljh")（installer.py L408-421）
- F-123: `run_plugin_actions(plugin_manager)` 按顺序执行：收集并安装 tljh_extra_apt_packages→tljh_extra_hub_pip_packages→tljh_extra_user_conda_packages（channels 默认 conda-forge）→tljh_extra_user_pip_packages→tljh_post_install（installer.py L424-483）
- F-124: `ensure_config_yaml(plugin_manager)` 创建 CONFIG_DIR 和 jupyterhub_config.d 目录（mode 0o700），执行 migrator.migrate_config_files()，调用 tljh_config_post_install hook，写回 config.yaml（installer.py L486-506）
- F-125: `main()` 解析 CLI 参数（--admin、--user-requirements-txt-url、--plugin、--progress-page-server-pid），执行顺序：setup_plugins→ensure_config_yaml→ensure_admins→ensure_usergroups→ensure_user_environment→ensure_jupyterhub_package→traefik.ensure_traefik_binary→停止进度页服务器→ensure_jupyterhub_service→ensure_jupyterhub_running→ensure_symlinks→run_plugin_actions（installer.py L509-560）

## Conda 环境管理 `tljh/conda.py`

- F-130: `sha256_file(fname)` 计算文件 SHA256 哈希，4096 字节分块读取（conda.py L19-29）
- F-131: `get_conda_package_versions(prefix)` 执行 `conda list --json` 返回包名→版本字典（conda.py L32-46）
- F-132: `download_miniconda_installer(installer_url, sha256sum)` 是上下文管理器，下载 Miniforge 安装脚本到临时文件，验证 SHA256（conda.py L49-75）
- F-133: `fix_permissions(prefix)` 执行 chown -R 当前用户:组 和 chmod -R o-w（conda.py L78-88）
- F-134: `install_miniconda(installer_path, prefix)` 执行 `/bin/bash installer -u -b -p prefix`，然后 fix_permissions（conda.py L91-99）
- F-135: `ensure_conda_packages(prefix, packages, channels=("conda-forge",), force_reinstall=False)` 优先使用 mamba，不存在则用 conda；执行 install --yes [-c channel...] --prefix abspath packages，可选 --force-reinstall（conda.py L102-137）
- F-136: `ensure_pip_packages(prefix, packages, upgrade=False)` 使用 prefix/bin/python -m pip install [--upgrade] packages（conda.py L140-150）
- F-137: `ensure_pip_requirements(prefix, requirements_path, upgrade=False)` 使用 pip install [--upgrade] --requirement requirements_path，requirements_path 可以是文件或 URL（conda.py L153-165）

## Traefik 代理 `tljh/traefik.py`

- F-140: traefik_version = "3.6.5"（traefik.py L32）
- F-141: 支持架构 aarch64→linux_arm64、x86_64→linux_amd64；checksums 字典包含两个架构的 sha256（traefik.py L23-39）
- F-142: `checksum_file(path_or_file)` 计算 SHA256，支持文件路径或文件对象（traefik.py L44-54）
- F-143: `check_traefik_version(traefik_bin)` 执行 `traefik version` 解析版本号，匹配则返回 True（traefik.py L62-89）
- F-144: `ensure_traefik_binary(prefix)` 使用 @backoff.on_exception(backoff.expo, max_tries=2) 装饰：检查已有二进制版本→不匹配则删除→从 GitHub 下载 tar.gz→验证 checksum→解压 traefik 二进制到 prefix/bin/→chmod 0o755（traefik.py L92-129）
- F-145: `load_extra_config(extra_config_dir)` glob 加载 *.toml 文件，toml.load 合并（traefik.py L132-136）
- F-146: `ensure_traefik_config(state_dir)` 渲染 traefik.toml（静态配置）和 rules/dynamic.toml（动态配置）Jinja2 模板，合并 extra_config_dir 中的 TOML 文件；创建 rules/rules.toml 和 acme.json（权限 0o600）；启用 HTTPS 时校验 tls.cert+key 或 letsencrypt.email+domains（traefik.py L139-202）

## Systemd 管理 `tljh/systemd.py`

- F-150: `reload_daemon()` 执行 systemctl daemon-reload（systemd.py L11-16）
- F-151: `install_unit(name, unit, path)` 将 unit 内容写入 /etc/systemd/system/name（systemd.py L19-25）
- F-152: `uninstall_unit(name, path)` rm 删除 systemd 单元文件（systemd.py L28-32）
- F-153: start_service/stop_service/restart_service 分别执行 systemctl start/stop/restart（systemd.py L35-53）
- F-154: enable_service/disable_service 执行 systemctl enable/disable（systemd.py L56-71）
- F-155: `check_service_active(name)` 执行 systemctl is-active，成功返回 True，CalledProcessError 返回 False（systemd.py L74-82）
- F-156: `check_service_enabled(name)` 执行 systemctl is-enabled，成功返回 True（systemd.py L85-93）

## JupyterHub 配置 `tljh/jupyterhub_config.py`

- F-160: `c = get_config()`（JupyterHub traitlets 配置入口）（jupyterhub_config.py L13）
- F-161: `c.JupyterHub.spawner_class = UserCreatingSpawner`（jupyterhub_config.py L14）
- F-162: `c.JupyterHub.cleanup_servers = False`（Hub 重启时保留用户服务器）（jupyterhub_config.py L17）
- F-163: `c.JupyterHub.hub_port = 15001`（jupyterhub_config.py L20）
- F-164: `c.TraefikProxy.should_start = False`（不自动启动 Traefik）（jupyterhub_config.py L22）
- F-165: `c.TraefikFileProviderProxy.dynamic_config_file = STATE_DIR/rules/rules.toml`（jupyterhub_config.py L24-25）
- F-166: `c.JupyterHub.proxy_class = "traefik_file"`（jupyterhub_config.py L26）
- F-167: `c.SystemdSpawner.extra_paths = [USER_ENV_PREFIX/bin]`（jupyterhub_config.py L28）
- F-168: `c.SystemdSpawner.default_shell = "/bin/bash"`（jupyterhub_config.py L29）
- F-169: `c.SystemdSpawner.unit_name_template = "jupyter-{USERNAME}"`（jupyterhub_config.py L31）
- F-170: 加载 configurer.load_config() 并 apply_config 到 c（jupyterhub_config.py L33-34）
- F-171: 调用 pm.hook.tljh_custom_jupyterhub_config(c=c) 插件钩子（jupyterhub_config.py L39-40）
- F-172: glob 加载 CONFIG_DIR/jupyterhub_config.d/*.py 额外配置文件，通过 load_subconfig 加载（jupyterhub_config.py L44-46）

## YAML 工具 `tljh/yaml.py`

- F-180: 使用 ruamel.yaml YAML(typ="rt")（round-trip 模式）（yaml.py L32）
- F-181: 自定义 `_NoEmptyFlowComposer` 继承 Composer，重写 compose_mapping_node 和 compose_sequence_node，空容器设置 flow_style=False（修复 ruamel.yaml issue #255）（yaml.py L11-28）
- F-182: 全局 `yaml` 对象使用自定义 Composer（yaml.py L32-33）

## 工具函数 `tljh/utils.py`

- F-190: `run_subprocess(cmd, *args, **kwargs)` 执行 subprocess.run（stdout=PIPE, stderr=STDOUT），失败时 logger.error 输出命令和 stdout 并抛 CalledProcessError；成功时 logger.debug 输出（utils.py L18-52）
- F-191: `get_plugin_manager()` 每次调用创建新的 pluggy.PluginManager("tljh")，add_hookspecs(hooks)，load_setuptools_entrypoints("tljh")（utils.py L55-64）
- F-192: `parse_version(version_string)` 用正则 `\d+` 提取所有数字返回 int 元组（类似 distutils.version.LooseVersion）（utils.py L67-75）

## 日志 `tljh/log.py`

- F-200: `init_logging()` 配置 "tljh" logger：INSTALL_PREFIX 不存在则创建；已有 handlers 则直接返回；添加 FileHandler（INSTALL_PREFIX/installer.log，格式 "%(asctime)s %(message)s"）和 StreamHandler（stderr，格式 "%(message)s"），级别 INFO（log.py L9-27）

## 迁移 `tljh/migrator.py`

- F-210: `migrate_file(old_path, new_path)` 迁移单个文件：old 不存在跳过；new 存在时移动到 new_path.old.YYYY-MM-DD[.i] 避免覆盖（migrator.py L13-36）
- F-211: `migrate_directory(old_dir, new_dir)` 递归迁移目录：new 存在时逐文件迁移；不存在时整体 shutil.move（migrator.py L39-54）
- F-212: `migrate_config_files()` 迁移旧路径 config.yaml→CONFIG_FILE、jupyterhub_config.d→CONFIG_DIR/jupyterhub_config.d（migrator.py L57-64）

## 用户名规范化 `tljh/normalize.py`

- F-220: `generate_system_username(username)` 用户名长度<26直接返回；否则截断前26字符+'-'+sha256哈希前5字符，确保用户名不超过32字符（normalize.py L8-24）

## APT 包管理 `tljh/apt.py`

- F-230: `trust_gpg_key(key)` 通过 stdin 执行 apt-key add，缺少 gpg2 时先安装 gnupg2（apt.py L11-20）
- F-231: `add_source(name, source_url, section)` 解析 /etc/os-release 获取 VERSION_CODENAME，写入 /etc/apt/sources.list.d/name.list，重复不添加；添加后 apt-get update（apt.py L23-45）
- F-232: `install_packages(packages)` /var/lib/apt/lists 为空时先 apt-get update；设置 DEBIAN_FRONTEND=noninteractive 执行 apt-get install --yes（apt.py L48-58）

## 用户创建 Spawner `tljh/user_creating_spawner.py`

- F-240: `UserCreatingSpawner` 继承 `systemdspawner.SystemdSpawner`（user_creating_spawner.py L8）
- F-241: 定义 `user_groups = Dict(key_trait=Unicode(), value_trait=List(Unicode()), config=True)` traitlet（user_creating_spawner.py L15）
- F-242: `start()` 方法：generate_system_username("jupyter-"+self.user.name)→设置 username_template→user.ensure_user→加入 jupyterhub-users 组→admin 用户加入 jupyterhub-admins 组并 disable_user_sudo=False，普通用户移除 admin 组并 disable_user_sudo=True→遍历 user_groups 加入对应组→调用 super().start()（user_creating_spawner.py L17-38）

## 用户管理 `tljh/user.py`

- F-250: `ensure_user(username)` pwd.getpwnam 检查用户存在性，不存在则 `useradd --create-home`，然后 chmod o-rwx 用户主目录，最后调用 tljh_new_user_create 插件钩子（user.py L16-34）
- F-251: `remove_user(username)` 存在则 `deluser --quiet`（user.py L37-47）
- F-252: `ensure_group(groupname)` 执行 `groupadd --force`（user.py L50-54）
- F-253: `remove_group(groupname)` 存在则 `delgroup --quiet`（user.py L57-67）
- F-254: `ensure_user_group(username, groupname)` grp.getgrnam 检查成员关系，不在组中则 `gpasswd --add`（user.py L70-80）
- F-255: `remove_user_group(username, groupname)` 在组中则 `gpasswd --delete`（user.py L83-91）

## 启动脚本 `bootstrap/bootstrap.py`

- F-260: bootstrap.py 仅依赖 Python 标准库，兼容 Python 3.9+（Ubuntu 22.04/Debian 11 默认），能在 Python 3.8 解析打印错误（bootstrap.py L12-17）
- F-261: 支持环境变量：TLJH_INSTALL_PREFIX（默认/opt/tljh）、TLJH_BOOTSTRAP_PIP_SPEC、TLJH_BOOTSTRAP_DEV（yes/no）（bootstrap.py L21-27）
- F-262: CLI 参数：--show-progress-page（端口80显示安装进度）、--version（版本/分支/commit），其余参数透传给 tljh.installer（bootstrap.py L31-43, L349-376）
- F-263: `ensure_host_system_can_install_tljh()` 检查：发行版为 ubuntu/debian、Ubuntu>=22.04、Debian>=11、Python>=3.9、systemd 存在；不满足则 sys.exit(1)（bootstrap.py L208-244）
- F-264: ProgressPageRequestHandler 提供 /logs（读 installer.log）、/(302→/index.html)、/index.html、/favicon.ico（bootstrap.py L247-268）
- F-265: `_resolve_git_version(version)` 通过 git ls-remote --tags 解析版本：latest→最新tag、部分版本号→匹配最新tag、分支/commit hash→原样返回（bootstrap.py L289-335）
- F-266: main() 执行顺序：系统检查→参数解析→(可选)启动进度页HTTP服务器→配置日志→新安装时apt-get安装python3/python3-venv/python3-pip/git/sudo→创建venv→升级pip→pip install TLJH→os.execv 切换到 hub/bin/python -m tljh.installer（bootstrap.py L338-513）

## Hub 环境依赖 `requirements-hub-env.txt`

- F-270: jupyterhub>=5.2.0,<6（requirements-hub-env.txt L11）
- F-271: jupyterhub-systemdspawner>=1.0.2,<2（L12）
- F-272: jupyterhub-firstuseauthenticator>=1.1.0,<2（L13）
- F-273: jupyterhub-nativeauthenticator>=1.3.0,<2（L14）
- F-274: jupyterhub-ldapauthenticator>=2.0.0,<3（L15）
- F-275: jupyterhub-tmpauthenticator>=1.0.0,<2（L16）
- F-276: oauthenticator>=17.1.0,<18（L17）
- F-277: jupyterhub-idle-culler>=1.4.0,<2（L18）
- F-278: pycurl>=7.45.7,<8（L28）

## 用户环境额外依赖 `requirements-user-env-extras.txt`

- F-280: notebook>=7.2.2,<8（requirements-user-env-extras.txt L12）
- F-281: jupyterlab>=4.2.5,<5（L15）
- F-282: nbgitpuller>=1.2.1,<2（L19）
- F-283: jupyter-resource-usage>=1.1.0,<2（L23）
- F-284: ipywidgets>=8.1.5,<9（L27）

## Systemd 单元模板

- F-290: jupyterhub.service 模板变量：install_prefix、python_interpreter_path、jupyterhub_config_path；Requires=traefik.service After=traefik.service；User=root；Restart=always；WorkingDirectory=install_prefix/state；PrivateTmp/PrivateDevices/ProtectKernelTunables/ProtectKernelModules=yes；ExecStart=python -m jupyterhub -f config --upgrade-db（jupyterhub.service L1-24）
- F-291: traefik.service 模板变量：install_prefix；After=network.target；User=root；Restart=always；ProtectHome=yes ProtectSystem=strict；ReadWritePaths 为 state/rules 和 state/acme.json；ExecStart=hub/bin/traefik -c state/traefik.toml（traefik.service L1-25）

## Traefik 配置模板

- F-300: traefik.toml.tpl 使用 Jinja2 模板语法，启用 [api]、[log] level=INFO、[accessLog] JSON格式过滤5xx状态码、Authorization/Cookie/Set-Cookie/X-Xsrftoken redact（traefik.toml.tpl L1-22）
- F-301: entryPoints.http 监听 http.address:http.port，idleTimeout=10m；HTTPS 启用时 http 重定向到 https，https 入口点监听 https.address:https.port（traefik.toml.tpl L23-43）
- F-302: entryPoints.auth_api 监听 localhost:traefik_api.port（traefik.toml.tpl L45-46）
- F-303: Let's Encrypt 配置：email、storage=acme.json、staging 可选、tlsChallenge（traefik.toml.tpl L48-56）
- F-304: providers.file.directory 指向 traefik_dynamic_config_dir，watch=true（traefik.toml.tpl L58-63）
- F-305: traefik-dynamic.toml.tpl 渲染 TLS 配置：minVersion=TLS12、密码套件列表、可选静态证书或 Let's Encrypt 自动证书（traefik-dynamic.toml.tpl L1-32）
