---
type: Facts
okf_version: "0.2"
title: "JupyterHub 源码事实清单"
tags: [jupyter, jupyterhub, multi-user, spawner, authenticator, proxy]
generated: "2026-08-22"
sources:
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\app.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\spawner.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\user.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\orm.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\auth.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\proxy.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\handlers\\base.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\apihandlers\\base.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\services\\service.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\oauth\\provider.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\objects.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\scopes.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\roles.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\traitlets.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\dbutil.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\jupyterhub\\singleuser\\app.py"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\pyproject.toml"
  - "d:\\spaces\\SpecWeave\\external\\libs\\jupyter\\jupyterhub\\requirements.txt"
---

# JupyterHub 源码事实清单

## 项目元数据

- F-001: pyproject.toml:9 — 项目名称为 `jupyterhub`，当前版本为 `6.0.0b2`（beta 版本）。
- F-002: pyproject.toml:19 — 要求 Python 版本 `>=3.10`。
- F-003: pyproject.toml:17 — 项目采用 BSD-3-Clause 许可证。
- F-004: pyproject.toml:3-4 — 构建系统使用 setuptools>=77 和 setuptools-scm，build-backend 为 `setuptools.build_meta`。
- F-005: pyproject.toml:62-64 — 定义两个 CLI 入口点：`jupyterhub` → `jupyterhub.app:main`，`jupyterhub-singleuser` → `jupyterhub.singleuser:main`。
- F-006: pyproject.toml:66-71 — Authenticator 插件入口点组 `jupyterhub.authenticators` 注册了 default/pam（PAMAuthenticator）、dummy（DummyAuthenticator）、shared-password、null（NullAuthenticator）。
- F-007: pyproject.toml:73-76 — Proxy 插件入口点组 `jupyterhub.proxies` 注册了 default/configurable-http-proxy（ConfigurableHTTPProxy）。
- F-008: pyproject.toml:77-80 — Spawner 插件入口点组 `jupyterhub.spawners` 注册了 default/localprocess（LocalProcessSpawner）、simple（SimpleLocalProcessSpawner）。
- F-009: requirements.txt:1-18 — 核心运行依赖包括：aiodns、aiohttp、alembic>=1.4、certipy>=0.1.2、idna、jinja2>=2.11.0、jupyter_events>=0.11.0、oauthlib>=3.0、packaging、pamela>=1.1.0（非Windows）、prometheus_client>=0.5.0、psutil>=5.6.5（Windows）、pydantic>=2、python-dateutil、requests、SQLAlchemy>=1.4.1、tornado>=6.5、traitlets>=5.4。
- F-010: _version.py:72 — 版本信息通过元组 `(major, minor, patch, "pre", "dev")` 管理，当前为 6.0.0b2。

## 目录结构

- F-011: jupyterhub/ — 核心 Python 包目录，包含 app.py、spawner.py、user.py、orm.py、auth.py、proxy.py 等核心模块。
- F-012: jupyterhub/handlers/ — HTTP 页面处理器目录，包含 base.py（基类）、login.py（登录）、pages.py（页面）、metrics.py（指标）、static.py（静态文件）。
- F-013: jupyterhub/apihandlers/ — REST API 处理器目录，包含 base.py（API基类）、auth.py、users.py、groups.py、services.py、proxy.py、hub.py、shares.py。
- F-014: jupyterhub/services/ — Hub 管理的外部服务模块，包含 service.py（Service 类）、auth.py（服务认证）。
- F-015: jupyterhub/oauth/ — OAuth 提供者实现，包含 provider.py（JupyterHubRequestValidator、JupyterHubOAuthServer）。
- F-016: jupyterhub/singleuser/ — 单用户服务器包装器，包含 app.py（入口）、mixins.py（认证混合类）、extension.py（Jupyter 扩展）。
- F-017: jupyterhub/alembic/ — 数据库迁移目录，使用 Alembic 管理 schema 版本，包含 env.py 和 versions/ 下的迁移脚本（共 18 个迁移版本）。
- F-018: jupyterhub/alembic/versions/ — 数据库迁移脚本从 `19c0846f6344_base_revision_for_0_5`（0.5 版本基线）到 `afd65840b69e_pkce`（PKCE 支持）。
- F-019: jupyterhub/authenticators/ — 内置认证器实现目录，包含 shared.py（SharedPasswordAuthenticator）。
- F-020: jupyterhub/tests/ — 测试套件目录，包含 test_api.py、test_app.py、test_auth.py、test_spawner.py、test_orm.py 等 30+ 测试文件。

## HubApp 主应用

- F-021: app.py:245-256 — JupyterHub 主类继承自 `traitlets.config.Application`，是整个 Hub 的入口类，描述为 "An Application for starting a Multi-User Jupyter Notebook server"。
- F-022: app.py:274-280 — JupyterHub 定义两个子命令：`token`（NewToken，生成 API token）、`upgrade-db`（UpgradeDB，升级数据库 schema）。
- F-023: app.py:102-124 — 定义命令行别名（aliases）：--log-level、-f/--config、--db、--base-url、-y、--ssl-key、--ssl-cert、--url、--ip、--port、--pid-file、--log-file。
- F-024: app.py:129-159 — 定义命令行标志（flags）：--debug、--generate-config、--generate-certs、--no-db（内存数据库）、--upgrade-db。
- F-025: app.py:161-163 — Cookie 密钥长度固定为 32 字节（COOKIE_SECRET_BYTES = 32）。
- F-026: app.py:963-975 — `proxy_class` 使用 EntryPointType trait，默认值为 ConfigurableHTTPProxy，基类为 Proxy，入口点组为 `"jupyterhub.proxies"`。
- F-027: app.py:1334-1354 — `authenticator_class` 使用 EntryPointType trait，默认值为 PAMAuthenticator，基类为 Authenticator，入口点组为 `"jupyterhub.authenticators"`。
- F-028: app.py:1459-1471 — `spawner_class` 使用 EntryPointType trait，默认值为 LocalProcessSpawner，基类为 Spawner，入口点组为 `"jupyterhub.spawners"`。
- F-029: app.py:1034-1044 — Hub 内部监听端口 `hub_port` 默认 8081，绑定 IP `hub_ip` 默认 `127.0.0.1`。
- F-030: app.py:443-448 — Cookie 默认有效期 `cookie_max_age_days` 为 14 天（两周）。
- F-031: app.py:462-495 — OAuth access token 默认过期时间 `oauth_token_expires_in` 与 cookie_max_age_days 一致（默认 14 天），影响浏览器中存储的服务/单用户服务器 token。
- F-032: app.py:520-531 — 用户活动记录分辨率 `activity_resolution` 为 30 秒，避免频繁数据库写入。
- F-033: app.py:1473-1479 — 并发 spawn 限制 `concurrent_spawn_limit` 默认 100，防止同时启动过多服务器导致性能问题。
- F-034: app.py:3470-3546 — `initialize()` 方法按固定顺序初始化组件：load_config_file → init_logging → init_eventlog → init_pycurl → init_secrets → init_internal_ssl → init_db → init_hub → init_proxy → init_oauth → init_role_creation → init_users → init_groups → init_services → init_api_tokens → init_role_assignment → init_blocked_users → init_tornado_settings → init_handlers → init_tornado_application。
- F-035: app.py:3556-3581 — `init_spawners()` 异步执行，可配置超时（默认负值即永不超时，内部设为 86400 秒），超时后允许后台完成。
- F-036: app.py:3604-3652 — `cleanup()` 方法按顺序清理：停止托管服务 → 停止单用户服务器（可选）→ 停止代理（可选）→ 提交数据库 → 删除 PID 文件 → 关闭 HTTP 客户端。
- F-037: app.py:1815 — `init_handlers()` 方法注册 Tornado 路由（URL → Handler 映射）。
- F-038: app.py:2033 — `init_db()` 创建 SQLAlchemy 引擎和会话工厂。
- F-039: app.py:2094 — `init_hub()` 初始化 Hub Server 对象（Hub 的自身网络端点表示）。
- F-040: app.py:3192 — `init_oauth()` 创建 OAuth 提供者（调用 oauth.provider.make_provider）。
- F-041: app.py:3226-3229 — `init_proxy()` 实例化 proxy_class 并传入 app、hub、public_url、ssl 等配置。
- F-042: app.py:3241-3364 — `init_tornado_settings()` 配置 Tornado 应用设置，包括 db、users、services、hub、proxy、authenticator、oauth_provider、spawner_class 等。
- F-043: app.py:597-605 — `internal_ssl` 选项（默认 False）启用 JupyterHub 各组件间端到端加密通信，自动创建 CA 证书。
- F-044: app.py:306-330 — `load_groups` 配置允许启动时预加载用户组，格式为 `{groupname: {users: [...], properties: {...}}}`。
- F-045: app.py:332-355 — `load_roles` 配置允许启动时预加载自定义角色定义（name、description、scopes、users、services、groups）。
- F-046: app.py:357-372 — `extra_user_scopes` 配置（v6.0 新增）向默认 `user` 角色添加额外 scope。
- F-047: app.py:374-395 — `custom_scopes` 配置允许自定义 scope，必须以 `custom:` 前缀开头。
- F-048: app.py:1381-1407 — `allow_named_servers`（默认 False）允许每个用户创建多个命名服务器；`named_server_limit_per_user` 限制每用户并发命名服务器数。

## Spawner 体系

- F-049: spawner.py:149-163 — Spawner 基类继承自 `LoggingConfigurable`，子类必须实现 `load_state`、`get_state`、`start`、`stop`、`poll` 五个方法。
- F-050: spawner.py:166-174 — Spawner 内部维护多个 pending 状态标志：`_spawn_pending`、`_start_pending`、`_stop_pending`、`_proxy_pending`、`_check_pending`、`_rename_pending`、`_waiting_for_response`。
- F-051: spawner.py:203-216 — `pending` 属性返回当前待处理事件类型：'spawn'/'stop'/'check'/'rename' 或 None（无待处理）。
- F-052: spawner.py:219-228 — `ready` 属性在无 pending 事件且 server 存在时返回 True，表示服务器可用。
- F-053: spawner.py:231-236 — `active` 属性在服务器 pending 或 ready 时返回 True（包含启动中、运行中、停止中状态）。
- F-054: spawner.py:273-287 — `__init_subclass__` 类初始化钩子强制检查子类是否重写了 `start`/`stop`/`poll` 方法，缺失则抛出 NotImplementedError。
- F-055: spawner.py:359 — 每个 Spawner 实例拥有唯一 `api_token`，用于单用户服务器与 Hub API 通信。
- F-056: spawner.py:360 — `oauth_client_id` 标识该服务器的 OAuth 客户端。
- F-057: spawner.py:376-383 — `oauth_access_scopes` 默认包含 `access:servers!server={user}/{name}` 和 `access:servers!user={user}`，控制 API token 的权限范围。
- F-058: spawner.py:449-510 — `oauth_client_allowed_scopes` 配置 OAuth 浏览器 token 的最大权限，默认包含访问当前服务器。
- F-059: spawner.py:542-585 — Spawner 配置 `ip`（默认空，由 JupyterHub 版本决定行为）和 `port`（默认 0 即随机端口）控制单用户服务器监听地址。
- F-060: spawner.py:1032-1058 — `cmd` trait（Command 类型）指定启动单用户服务器的命令，默认为 `["jupyterhub-singleuser"]`。
- F-061: spawner.py:1059-1072 — `notebook_dir` 配置单用户服务器的根目录。
- F-062: spawner.py:1073-1086 — `default_url` 配置用户登录后默认跳转 URL（如 `/lab` 或 `/tree`）。
- F-063: spawner.py:1262-1273 — `load_state(state)` 从数据库恢复 Spawner 状态（state 为 dict）；`get_state()` 序列化当前状态供持久化。
- F-064: spawner.py:1300-1410 — `get_env()` 构建传递给单用户服务器的环境变量，包括 JUPYTERHUB_API_TOKEN、JUPYTERHUB_API_URL、JUPYTERHUB_BASE_URL、JUPYTERHUB_ROOT_DIR、JUPYTERHUB_DEFAULT_URL 等。
- F-065: spawner.py:1322 — 环境变量 `JUPYTERHUB_API_TOKEN` 被设置为 spawner 的 api_token 值。
- F-066: spawner.py:1358 — 环境变量 `JUPYTERHUB_API_URL` 指向 Hub 的 API 端点。
- F-067: spawner.py:1366 — 环境变量 `JUPYTERHUB_BASE_URL` 设置为 hub.base_url 去除末尾 `/hub/` 后的值。
- F-068: spawner.py:1688-1712 — Spawner 基类定义 `async def start()`、`async def stop(now=False)`、`async def poll()` 接口契约。
- F-069: spawner.py:1757-1784 — Spawner 支持轮询（polling）机制：`start_polling()` 启动定期 poll，`stop_polling()` 停止，`add_poll_callback()` 注册服务器停止回调。
- F-070: spawner.py:1920 — LocalProcessSpawner 继承自 Spawner，是默认的本地进程 Spawner 实现。
- F-071: spawner.py:1969-1978 — LocalProcessSpawner 使用 `shell_cmd` trait（默认依赖平台）包装命令执行，Linux 默认 `['bash', '-l', '-c']`。
- F-072: spawner.py:2118-2158 — LocalProcessSpawner.start() 在 port=0 时自动选择随机端口，通过 Popen 启动子进程，支持 setuid 切换用户。
- F-073: spawner.py:2158 — LocalProcessSpawner.poll() 通过检查进程返回码判断服务器状态。
- F-074: spawner.py:2208 — LocalProcessSpawner.stop() 通过向进程组发送信号终止服务器。

## Authenticator

- F-075: auth.py:31-32 — Authenticator 基类继承自 `LoggingConfigurable`，是所有认证器的抽象基类。
- F-076: auth.py:51-70 — `enable_auth_state`（默认 False）启用认证状态持久化，auth_state 加密存储在数据库中，需要 cryptography 包和 JUPYTERHUB_CRYPT_KEY 环境变量。
- F-077: auth.py:72-89 — `auth_refresh_age`（默认 300 秒/5分钟）控制认证信息刷新间隔，设置为 0 禁用定时刷新。
- F-078: auth.py:91-105 — `refresh_pre_spawn`（默认 False）在 spawn 前强制刷新用户认证信息，确保 auth_state（如 token）不过期。
- F-079: auth.py:126-162 — `admin_users` 集合配置管理员用户名集合，但仅授予权限不撤销（v2.0 后推荐使用 roles 管理）。
- F-080: auth.py:218-232 — `allowed_users` 集合限制可登录用户，空集合表示不限制（需 allow_all=True 或其他 allow 配置）。
- F-081: auth.py:234-250 — `allow_all`（默认 False 自 v5.0）允许任何成功认证的用户登录，False 时需要显式配置 allowed_users 等。
- F-082: auth.py:579-597 — `run_post_auth_hook()` 支持在认证成功后执行自定义钩子函数，可修改 auth_model。
- F-083: auth.py:599-609 — `normalize_username()` 默认将用户名转为小写并应用 username_map 映射，子类可重写。
- F-084: auth.py:611-640 — `check_allowed(username, authentication)` 检查用户是否在允许列表中，allow_all=True 时直接返回 True。
- F-085: auth.py:675-744 — `get_authenticated_user(handler, data)` 是认证的外层 API（子类不应重写），流程为：调用 authenticate → 规范化用户名 → 检查 blocked_users → 检查 allowed → 判断 admin → 执行 post_auth_hook。
- F-086: auth.py:746-774 — `refresh_user(user, handler)` 支持刷新用户认证数据，返回 True（无需更新）、False（需重新登录）或 dict（更新数据）。
- F-087: auth.py:791 — `authenticate(handler, data)` 是子类必须实现的核心认证方法，返回用户名/dict（成功）或 None（失败）。
- F-088: auth.py:864 — `add_user(user)` 在用户首次创建时调用，子类可执行自定义初始化逻辑。
- F-089: auth.py:906-917 — `manage_groups`（默认 False）允许 Authenticator 管理用户组成员关系，启用后 authenticate 返回值必须包含 groups 字段。
- F-090: auth.py:918 — `manage_roles`（默认 False）允许 Authenticator 管理用户角色分配。
- F-091: auth.py:959-982 — `auto_login`（默认 False）跳过登录页直接使用认证器登录；`auto_login_oauth2_authorize` 控制 OAuth 自动跳转。
- F-092: auth.py:1072 — LocalAuthenticator 是 Authenticator 的中间子类，添加了本地用户管理功能（添加/删除系统用户、检查 group 成员）。
- F-093: auth.py:1238 — PAMAuthenticator 继承自 LocalAuthenticator，使用 pamela 库通过 PAM（Pluggable Authentication Modules）进行系统用户认证。
- F-094: auth.py:1482 — DummyAuthenticator 是测试用认证器，允许任意用户名/密码登录。
- F-095: auth.py:1535 — NullAuthenticator 禁止所有登录（完全不允许认证），用于 API-only 部署。

## Proxy

- F-096: proxy.py:82-104 — Proxy 基类继承自 `LoggingConfigurable`，子类必须实现 `get_all_routes`、`add_route`、`delete_route` 方法，可选实现 `start`/`stop`/`get_route`。
- F-097: proxy.py:119-128 — `should_start`（默认 True）控制 Hub 是否启动代理进程；外部管理代理时设为 False。
- F-098: proxy.py:130-194 — `extra_routes` 字典配置额外的代理路由，Hub 启动时自动注册。
- F-099: proxy.py:214-238 — `validate_routespec()` 验证路由规范：检查 host-based routing 一致性、确保尾部斜杠。
- F-100: proxy.py:240-263 — `add_route(routespec, target, data)` 添加路由，routespec 格式为 [host]/path/，target 为完整 URL，data 为关联元数据。
- F-101: proxy.py:332-362 — `add_user(user, server_name)` 将用户的单用户服务器注册到代理，路由前缀为 `/user/:username[/:servername]/`。
- F-102: proxy.py:363-388 — `add_all_services(service_dict)` 批量注册所有服务路由，路由前缀为 `/services/:name/`。
- F-103: proxy.py:389-490 — `check_routes(user_dict, service_dict)` 对比 Hub 已知路由和代理实际路由，修复不一致（添加缺失路由、删除多余路由）。
- F-104: proxy.py:492 — ConfigurableHTTPProxy 继承自 Proxy，是默认代理实现，通过 REST API 管理 nodejs 的 configurable-http-proxy 进程。
- F-105: proxy.py:542-553 — `auth_token` 用于 Hub 与代理 API 间的认证，默认自动生成随机 token。
- F-106: proxy.py:561-574 — `api_url`（默认 http://127.0.0.1:port+1）为 configurable-http-proxy 的管理 API 端点。
- F-107: proxy.py:575-581 — `command` trait 指定启动 configurable-http-proxy 的命令。
- F-108: proxy.py:726-799 — ConfigurableHTTPProxy.start() 构建命令行参数、设置 CONFIGPROXY_AUTH_TOKEN 环境变量、通过 Popen 启动代理进程、等待 API 就绪。
- F-109: proxy.py:902 — ConfigurableHTTPProxy.stop() 终止代理子进程。
- F-110: proxy.py:999-1006 — ConfigurableHTTPProxy.add_route()/delete_route() 通过 HTTP DELETE/POST 请求代理 API 管理路由，Authorization 头使用 token 认证。

## User 模型

- F-111: user.py:62 — UserDict 继承自 dict，是 User 对象的容器，提供 `count_active_users()` 等统计方法。
- F-112: user.py:188-210 — UserDict.count_active_users() 统计活跃服务器数、spawn pending 数和 proxy pending 数。
- F-113: user.py:218 — User 类是 orm.User 的高级包装器，管理用户的 Spawner 实例、服务器生命周期和认证状态。
- F-114: user.py:240 — User.spawners 是 _SpawnerDict 实例，懒加载创建 Spawner 对象（键为服务器名，空字符串为默认服务器）。
- F-115: user.py:226 — User._auth_refreshed 记录上次认证刷新时间戳（monotonic time）。
- F-116: user.py:297 — User.sync_groups(group_names) 同步用户组成员关系，添加到新组、从旧组移除。
- F-117: user.py:333 — User.sync_roles(auth_roles) 同步 Authenticator 管理的角色分配。
- F-118: user.py:435-461 — User.save_auth_state(auth_state) 加密保存认证状态到数据库；User.get_auth_state() 解密获取。
- F-119: user.py:650-661 — User.running 属性在用户有任何活跃 Spawner 时返回 True。
- F-120: user.py:736 — User.url 属性返回用户默认服务器的 URL。
- F-121: user.py:771 — User.progress_url(server_name) 返回 spawn 进度事件流 URL（/hub/api/users/:name[/server]/server/progress）。
- F-122: user.py:831 — User.spawn() 异步启动用户服务器：创建 Spawner → 调用 Spawner.start() → 等待服务器响应 → 返回 Server 对象。
- F-123: user.py:1150-1221 — User.stop(server_name) 异步停止用户服务器：调用 Spawner.stop() → 删除代理路由 → 清理 Spawner 状态。

## ORM/数据库

- F-124: orm.py:141-157 — Server 模型（__tablename__='servers'）存储 HTTP 端点信息：proto、ip、port、base_url、cookie_name，与 Service 和 Spawner 一对一关系。
- F-125: orm.py:194-209 — Role 模型（__tablename__='roles'）存储角色定义：name（唯一）、description、scopes（JSONList），与 User/Service/Group 多对多关系。
- F-126: orm.py:231-243 — Group 模型（__tablename__='groups'）存储用户组：name（唯一）、properties（JSONDict）、users（多对多）、roles（多对多）。
- F-127: orm.py:264-365 — User 模型（__tablename__='users'）存储用户：name（唯一）、admin、created、last_activity、user_info（JSONDict）、cookie_id（唯一随机token）、state（JSONDict）、encrypted_auth_state（LargeBinary）、与 Spawner/APIToken/Group/Role/OAuthCode/Share 的关系。
- F-128: orm.py:359 — User.cookie_id 使用 new_token 函数生成随机值，用于安全 cookie 认证，是唯一且不可为空的列。
- F-129: orm.py:374 — User.new_api_token() 创建新的 API token 并关联到用户。
- F-130: orm.py:389-430 — Spawner 模型（__tablename__='spawners'）存储 Spawner 状态：user_id（外键→users）、server_id（外键→servers）、state（JSONDict）、name、display_name、started、last_activity、user_options（JSONDict）、oauth_client_id（外键→oauth_clients）。
- F-131: orm.py:449-530 — Service 模型（__tablename__='services'）存储服务信息：name、admin、url、pid、info、command、oauth_client_allowed_scopes 等，关联 Server 和 OAuthClient。
- F-132: orm.py:547-585 — Expiring mixin 为有过期时间的模型提供 expires_at 属性和类方法 `now()`、`purge_expired()`（清理过期记录）。
- F-133: orm.py:594-680 — Hashed mixin（继承 Expiring）为 token 类模型提供哈希存储：prefix（前4字符索引）、hashed（bcrypt/哈希值）、`match()` 验证方法、`find()` 前缀+哈希快速查找。
- F-134: orm.py:754-919 — Share 模型（__tablename__='shares'）存储服务器共享关系：spawner_id、user_id/group_id、scopes、expires_at，支持用户/组级别的服务器访问共享。
- F-135: orm.py:928-999 — ShareCode 模型（__tablename__='share_codes'，继承 _Share、Hashed）存储一次性共享码，支持生成和兑换。
- F-136: orm.py:1031-1250 — APIToken 模型（__tablename__='api_tokens'，继承 Hashed）存储 API token：user_id/service_id（二选一外键）、hashed、prefix、client_id、session_id、expires_at、note、scopes。
- F-137: orm.py:1253-1289 — OAuthCode 模型（__tablename__='oauth_codes'，继承 Expiring）存储 OAuth 授权码：client_id、code、redirect_uri、user_id、scopes、session_id、code_challenge、code_challenge_method（PKCE 支持），默认 5 分钟过期。
- F-138: orm.py:1304-1338 — OAuthClient 模型（__tablename__='oauth_clients'）存储 OAuth 客户端：identifier（唯一）、description、secret（哈希）、redirect_uri、allowed_scopes（JSONList）。
- F-139: orm.py:55 — JSONDict 是自定义 TypeDecorator，自动在 Python dict 和数据库 JSON 文本间序列化/反序列化。
- F-140: dbutil.py:25-48 — write_alembic_ini() 从模板生成 alembic.ini，db_url 中的 % 需转义为 %%（避免 ConfigParser 格式化冲突）。
- F-141: dbutil.py:76-85 — upgrade() 使用临时 alembic.ini 执行 alembic upgrade 命令升级数据库到指定 revision。
- F-142: dbutil.py:104-134 — upgrade_if_needed() 检查数据库版本，SQLite 数据库升级前自动备份（带时间戳后缀），密码字段在日志中脱敏。
- F-143: dbutil.py:88-101 — backup_db_file() 在数据库文件旁创建带时间戳的备份文件，最多尝试 10 个序号避免覆盖。

## Handler/API

- F-144: handlers/base.py:81-89 — BaseHandler 继承自 tornado.web.RequestHandler，默认 `_accept_cookie_auth=True`、`_accept_token_auth=False`（页面仅 cookie 认证）。
- F-145: handlers/base.py:90-121 — prepare() 方法在所有请求前执行：异步获取 current_user → 解析 roles/scopes → 执行 XSRF 检查（GET/HEAD/OPTIONS 除外）。
- F-146: handlers/base.py:78 — SESSION_COOKIE_NAME 常量为 `'jupyterhub-session-id'`，session cookie 不加密，供同域服务读取。
- F-147: handlers/base.py:227-229 — 默认 Content-Security-Policy 为 `frame-ancestors 'none'; report-uri <csp_report_uri>`，禁止被嵌入 iframe。
- F-148: handlers/base.py:349-355 — get_auth_token() 从 Authorization header 解析 token，支持 `token <value>` 和 `bearer <value>` 两种格式（正则 `^(?:token|bearer)\s+([^\s]+)$`）。
- F-149: handlers/base.py:452-476 — get_current_user_token() 从 Authorization header 查找 APIToken，记录 token 和用户活动时间，token 认证时跳过 XSRF 检查。
- F-150: handlers/base.py:478-504 — _user_for_cookie() 通过安全 cookie 查找用户（cookie 存储 user.cookie_id），无效/过期 cookie 自动清除。
- F-151: handlers/base.py:521-538 — get_current_user() 认证优先级：token（如启用）→ cookie（如启用）→ 对 User 类型调用 refresh_auth()。
- F-152: handlers/base.py:540-548 — _resolve_roles_and_scopes() 在认证后解析当前请求的 expanded_scopes 和 parsed_scopes。
- F-153: handlers/base.py:551-566 — get_scope_filter(req_scope) 返回一个过滤函数，判断当前请求对特定资源是否有指定 scope 的访问权限。
- F-154: handlers/base.py:916-977 — auth_to_user() 将 authenticate() 返回的认证数据持久化到数据库：查找/创建用户 → 设置 admin → 分配默认角色 → 同步 groups/roles → 保存 auth_state。
- F-155: handlers/base.py:979-1003 — login_user(data) 执行完整登录流程：authenticate → auth_to_user → set_login_cookie → 记录登录指标。
- F-156: handlers/base.py:1028-1333 — spawn_single_user() 是 spawn 的核心逻辑：检查并发限制 → 调用 user.spawn() → 注册 finish_user_spawn 回调（添加代理路由、注册 poll 回调）→ 慢 spawn 超时处理 → 连续失败计数（达到限制时 Hub 退出）。
- F-157: handlers/base.py:1073-1107 — 并发 spawn 限流：达到 concurrent_spawn_limit 时返回 HTTP 429 + Retry-After header，retry 时间在配置范围内随机（避免惊群效应）。
- F-158: apihandlers/base.py:23-34 — APIHandler 继承自 BaseHandler，启用 `_accept_token_auth=True`，返回 JSON 响应和错误。
- F-159: apihandlers/base.py:37-38 — APIHandler 追加 CSP `default-src 'none'`，比页面更严格。
- F-160: apihandlers/base.py:81 — APIHandler 的 XSRF 安全方法仅包含 HEAD 和 OPTIONS（GET 也需 XSRF 检查），但 token 认证时跳过。
- F-161: apihandlers/base.py:173-228 — server_model() 生成 Spawner 的 JSON 表示，包含 name、display_name、full_name、last_activity、started、pending、ready、stopped、url、progress_url 等字段，admin:server_state scope 可见 state。
- F-162: apihandlers/base.py:284-385 — user_model() 生成 User 的 JSON 表示，通过 scope 过滤可见字段（read:users 可见基本信息、read:roles:users 可见 roles、read:servers 可见 servers 等）。
- F-163: apihandlers/base.py:404-434 — service_model() 生成 Service 的 JSON 表示，同样基于 scope 过滤字段。
- F-164: apihandlers/base.py:509-530 — API 分页支持 offset/limit 参数，默认 limit 由 api_page_default_limit 控制，最大不超过 api_page_max_limit。
- F-165: apihandlers/base.py:532-568 — paginated_model() 返回分页格式 `{items: [...], _pagination: {offset, limit, total, next}}`，Accept: application/jupyterhub-pagination+json 时启用。
- F-166: apihandlers/users.py:1252 — users.py 是最大的 API handler（1252 行），处理用户 CRUD、服务器启停、token 管理等操作。
- F-167: apihandlers/auth.py:433 — auth.py 处理 OAuth 授权端点（/hub/api/oauth2/authorize、/hub/api/oauth2/token）。

## Services

- F-168: services/service.py:1-40 — Service 分为 Managed（Hub 管理的子进程，自动重启）和 Unmanaged（外部管理，如 Docker/systemd）；公共路由固定为 `/services/service-name/`。
- F-169: services/service.py:100-157 — _ServiceSpawner 继承自 LocalProcessSpawner，用于启动托管服务子进程，移除了 notebook 特定逻辑。
- F-170: services/service.py:160-502 — Service 类继承自 LoggingConfigurable，属性包括 name、admin、url、command、cwd、environment、user、oauth_client_allowed_scopes、api_token、info、display、timeout（v6.0 新增）、oauth_no_confirm 等。
- F-171: services/service.py:272-283 — Service.managed 属性在 command 非空时返回 True；Service.kind 返回 'managed' 或 'external'。
- F-172: services/service.py:325-336 — Service.oauth_client_id 默认格式为 `service-<name>`，验证器强制要求以 `service-` 前缀开头。
- F-173: services/service.py:414-482 — Service.start() 启动托管服务：设置环境变量（JUPYTERHUB_SERVICE_NAME、JUPYTERHUB_SERVICE_URL 等）→ 创建 _ServiceSpawner → 可选创建 SSL 证书 → 启动进程 → 注册停止回调（自动重启）。
- F-174: services/service.py:484-490 — _proc_stopped() 回调在服务进程意外退出时调用，通过 asyncio.ensure_future 安排自动重启。
- F-175: services/auth.py:1673 — services/auth.py（1673行）实现服务的 OAuth 认证处理器和回调。

## 配置与 traitlets

- F-176: traitlets.py:14-21 — URLPrefix 自定义 trait（继承 Unicode）自动规范化 URL 前缀，确保以 `/` 开头和结尾。
- F-177: traitlets.py:24-42 — Command 自定义 trait（继承 List）允许命令以字符串或列表指定，自动转换为列表，minlen 默认 1。
- F-178: traitlets.py:45-89 — ByteSpecification 自定义 trait（继承 Integer）支持 K/M/G/T 后缀的字节规格（如 '2G' → 2*1024^3 字节），allow_none 默认为 True。
- F-179: traitlets.py:92-106 — Callable 自定义 trait 验证值是否可调用（函数、类、实现 __call__ 的实例）。
- F-180: traitlets.py:109-152 — EntryPointType 自定义 trait（继承 Type）支持通过 entry points 查找可配置类，在 help 文本中列出所有已安装选项，validate 时先在 entry point 注册表查找。
- F-181: scopes.py:39-190 — scope_definitions 字典定义了全部 RBAC scope，包含 (no_scope)、self、inherit、admin-ui、admin:users、admin:servers、users、servers、tokens、groups、admin:services、access:servers、access:services、shares、proxy、shutdown、read:metrics 等 40+ 个 scope，支持 subscopes 层级。
- F-182: roles.py:14-67 — 默认角色定义：user（scope: self）、admin（全部管理 scope）、server（users:activity!user + access:servers!server）、token（scope: inherit，与所有者同权限）。
- F-183: roles.py:167-176 — admin 角色不可被覆盖（尝试修改 description/scopes 抛出 RoleValueError）。

## OAuth 与 Single-User

- F-184: oauth/provider.py:36-40 — JupyterHubRequestValidator 继承 oauthlib 的 RequestValidator，实现 OAuth 2.0 授权码流程的服务端验证逻辑，支持可选 PKCE。
- F-185: oauth/provider.py:26-33 — 补丁 oauthlib 的 is_absolute_uri 检查，允许以 `/` 开头的相对 URI 重定向（内部服务使用）。
- F-186: oauth/provider.py:223-274 — save_authorization_code() 将 OAuth 授权码持久化到数据库，关联 client、user、scopes、redirect_uri、session_id、PKCE code_challenge，有效期 300 秒（5分钟）。
- F-187: oauth/provider.py:295-370 — save_bearer_token() 将 OAuth access token 保存为 APIToken 记录，不支持 refresh_token（FIXME 注释标记）。
- F-188: oauth/provider.py:436-472 — validate_code() 验证授权码：查找 code → 检查 client_id 匹配 → 设置 request.user/session_id/scopes/PKCE 属性。
- F-189: oauth/provider.py:551-566 — 仅支持 `authorization_code` grant type，不支持 password、client_credentials、refresh_token 等。
- F-190: oauth/provider.py:631-711 — validate_scopes() 验证客户端请求的 scopes：检查 scope 存在性 → 向后兼容 roles→scopes 转换 → 解析请求 scopes → 检查是否在 allowed_scopes 内，始终包含 identify 和 access:services 基础 scope。
- F-191: oauth/provider.py:714-754 — JupyterHubOAuthServer 继承 WebApplicationServer，提供 add_client() 方法创建/更新 OAuthClient（secret 哈希存储）、remove_client() 删除客户端。
- F-192: oauth/provider.py:775-786 — make_provider() 工厂函数创建 JupyterHubOAuthServer 实例。
- F-193: singleuser/app.py:1-18 — Single-user 服务器入口由环境变量 JUPYTERHUB_SINGLEUSER_APP 指定底层应用类，默认 jupyter_server.serverapp.ServerApp（支持 "notebook" 快捷方式指向 notebook.notebookapp.NotebookApp）。
- F-194: singleuser/app.py:73 — make_singleuser_app(App) 通过 mixin 模式将 JupyterHub 认证层包装到任意 Jupyter 应用类上。
- F-195: singleuser/mixins.py:969 — mixins.py（969行）定义 SingleUserNotebookAppMixin，实现 OAuth 客户端流程、token 认证、Hub API 通信等逻辑。
- F-196: objects.py:24-46 — Server 类（HasTraits）表示 HTTP 端点，属性包括 orm_server、ip、connect_ip、connect_port、proto、port、base_url、cookie_name、connect_url、bind_url、SSL 证书路径等，部分 Server 存在于数据库中，部分仅内存（Hub、Proxy）。

## CLI 入口点

- F-197: app.py:170-221 — NewToken 子命令类（jupyterhub token [username]）生成并打印用户 API token，流程为初始化 Hub → init_db → init_role_creation → init_users → 查找用户 → new_api_token。
- F-198: app.py:224-242 — UpgradeDB 子命令类（jupyterhub upgrade-db）执行数据库 schema 升级。
- F-199: dbutil.py:137-149 — dbutil.shell() 启动 IPython shell 连接到 JupyterHub 数据库，命名空间包含 db、db_url、orm。
- F-200: dbutil.py:163-177 — dbutil.main() 提供 CLI 子命令 shell 和 alembic，`jupyterhub dbutil shell` / `jupyterhub dbutil alembic <args>`。
