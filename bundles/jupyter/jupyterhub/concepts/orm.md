---
type: Concept
title: JupyterHub ORM 数据模型
description: JupyterHub 基于 SQLAlchemy 的 ORM 持久化层——自定义列类型、核心实体模型（Server/User/Group/Role/Spawner/Service/APIToken/OAuth/Share）、表关系与实用方法
tags: [jupyterhub, orm, sqlalchemy, database, rbac, user-model]
sources:
  - id: orm-source
    resource: ../references/orm-source.md
    title: JupyterHub ORM 源码参考
generated: { by: reference_agent/source-code-to-okf-wiki, at: "2026-08-22" }
status: stable
stale_after: "2027-08-22"
---

# JupyterHub ORM 数据模型

> 源码位置：`jupyterhub/orm.py`（v6.0.0b2）

## ORM 层概述

JupyterHub 的 ORM（Object-Relational Mapping）层基于 **SQLAlchemy** 构建，是整个 Hub 进程星座（constellation of processes）的状态持久化核心。所有运行时状态——用户、服务器、Token、角色权限、OAuth 授权、笔记本共享——均通过 ORM 模型映射到关系数据库（默认 SQLite，生产环境推荐 PostgreSQL/MySQL）。

### 技术栈

| 组件 | 说明 |
|------|------|
| SQLAlchemy ORM | 声明式基类 + 关系映射，使用 `declarative_base` |
| Alembic | 数据库迁移管理 |
| 自定义 TypeDecorator | JSONDict/JSONList 实现 JSON 列透明序列化 |

### 基类与元数据

所有模型继承自声明基类 `Base`，该基类配置了 SQLAlchemy **约束命名约定**（naming convention），确保 Alembic 迁移的确定性：

- `ix_%(column_0_label)s` — 索引命名
- `uq_%(table_name)s_%(column_0_name)s` — 唯一约束
- `ck_%(table_name)s_%(constraint_name)s` — 检查约束
- `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s` — 外键约束
- `pk_%(table_name)s` — 主键约束

---

## 自定义列类型

### JSONDict

继承 `sqlalchemy.types.TypeDecorator`，底层使用 `Text` 列存储 JSON 字符串。提供 Python 字典与数据库 JSON 字符串之间的透明双向转换，额外支持 **bytes 类型**的编解码：

- 写入时（`process_bind_param`）：调用 `json.dumps()`，bytes 编码为 `{"__jupyterhub_bytes__": true, "data": "<base64>"}`
- 读取时（`process_result_value`）：调用 `json.loads()`，检测 `__jupyterhub_bytes__` 标记还原 bytes

### JSONList

继承 `JSONDict`，专用于列表类型列：

- 写入接受 `list`/`tuple`/`set`，set 自动排序后序列化为有序列表
- 读取始终返回 `list` 类型，`None` 返回空列表 `[]`

---

## 核心实体模型

### Server — 单用户服务器记录

**表名**：`servers`

记录单个用户服务器的连接信息和 Cookie 状态，是 Spawner 和 Service 的底层连接载体。

| 列 | 类型 | 默认值 | 说明 |
|----|------|--------|------|
| `id` | Integer | — | 主键 |
| `proto` | Unicode(15) | `'http'` | 协议（http/https） |
| `ip` | Unicode(255) | `''` | IP 地址或 DNS 名称 |
| `port` | Integer | 随机端口 | 端口号 |
| `base_url` | Unicode(255) | `'/'` | 基础 URL 路径 |
| `cookie_name` | Unicode(255) | `'cookie'` | Cookie 名称 |

**关系**：与 Spawner、Service 各为一对一（`uselist=False`）。

---

### User — 用户实体

**表名**：`users`

JupyterHub 的核心实体，代表一个认证用户。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `name` | Unicode(255) | 用户名（唯一） |
| `user_info` | JSONDict | Authenticator 提供的用户信息 |
| `admin` | Boolean | 是否管理员（v2.0+ 推荐使用 RBAC roles） |
| `created` | DateTime | 创建时间（默认 utcnow） |
| `last_activity` | DateTime | 最后活动时间 |
| `cookie_id` | Unicode(255) | Cookie 标识（唯一），重置可强制重新登录 |
| `state` | JSONDict | Spawner 状态字典 |
| `encrypted_auth_state` | LargeBinary | Authenticator 加密认证状态 |

**关系映射**：

| 关系 | 目标实体 | 说明 |
|------|----------|------|
| `spawners` (via `_orm_spawners`) | Spawner | 用户的所有 Spawner 实例（支持命名服务器） |
| `servers` | — | 通过 Spawner 关联的 Server |
| `api_tokens` | APIToken | 用户的 API 令牌 |
| `oauth_codes` | OAuthCode | OAuth 授权码 |
| `roles` | Role | RBAC 角色（多对多，通过 `user_role_map`） |
| `groups` | Group | 所属用户组（多对多，通过 `user_group_map`） |
| `shares` | Share | 用户发起的共享 |
| `share_codes` | ShareCode | 用户创建的共享码 |
| `shared_with_me` | Share | 直接共享给此用户的资源 |

**关键属性**：
- `orm_spawners`：`{name: Spawner}` 字典，按服务器名称索引
- `all_shared_with_me`：合并直接共享和通过组共享的所有 Share 列表
- `kind`：类属性，值为 `"user"`，用于实体类型区分

**实用方法**：
- `new_api_token(token=None, **kwargs)`：创建新的 API Token；若传入 `token` 参数则加载已有令牌
- `find(cls, db, name)` **classmethod**：按用户名查找用户，返回 None 或 User 实例

---

### Group — 用户组

**表名**：`groups`

用户组用于批量管理权限和共享。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `name` | Unicode(255) | 组名（唯一） |
| `properties` | JSONDict | 组扩展属性 |

| 关系 | 目标 | 说明 |
|------|------|------|
| `users` | User | 组成员（多对多） |
| `roles` | Role | 组角色（多对多，通过 `group_role_map`） |
| `shared_with_me` | Share | 共享给此组的资源 |

**类属性**：`kind = "group"`

**实用方法**：`find(cls, db, name)` 按名称查找组。

---

### Role — RBAC 角色

**表名**：`roles`

RBAC（Role-Based Access Control）权限模型核心，定义角色及其拥有的权限范围（scopes）。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `name` | Unicode(255) | 角色名称（唯一） |
| `description` | Unicode(1023) | 角色描述 |
| `scopes` | JSONList | 角色拥有的权限范围列表 |
| `managed_by_auth` | Boolean | 是否由认证系统自动管理 |

| 关系 | 目标 | 说明 |
|------|------|------|
| `users` | User | 拥有此角色的用户（多对多） |
| `services` | Service | 拥有此角色的服务（多对多） |
| `groups` | Group | 拥有此角色的用户组（多对多） |

角色与实体的多对多关联通过动态生成的映射表实现：`user_role_map`、`group_role_map`、`service_role_map`，均包含 `managed_by_auth` 标记。

**实用方法**：`find(cls, db, name)` 按名称查找角色。

---

### Spawner ORM — Spawner 状态持久化

**表名**：`spawners`

记录单个 Spawner 实例的持久化状态，支持每个用户拥有多个命名服务器（named servers）。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `user_id` | Integer (FK→users.id) | 所属用户（CASCADE 删除） |
| `server_id` | Integer (FK→servers.id) | 关联服务器（SET NULL） |
| `name` | Unicode(255) | 服务器名称（空字符串为默认服务器） |
| `display_name` | Unicode(255) | 显示名称 |
| `state` | JSONDict | Spawner 状态字典 |
| `started` | DateTime | 启动时间 |
| `last_activity` | DateTime | 最后活动时间 |
| `user_options` | JSONDict | 用户选项（表单输入等） |
| `oauth_client_id` | Unicode(255) | OAuth 客户端标识（SET NULL，v2.0+） |

**状态属性**（ORM 层默认值，运行时被 Spawner 包装器覆盖）：

| 属性 | 默认值 | 含义 |
|------|--------|------|
| `active` | `False` | Spawner 是否活跃 |
| `running` | `False` | 服务器是否运行中 |
| `ready` | `False` | 服务器是否就绪（可接受请求） |
| `pending` | `None` | 待处理状态（`'spawn'`/`'stop'` 等） |

---

### Service — 服务实体

**表名**：`services`

JupyterHub 托管服务。Service 类似没有 Spawner 的 User，可以拥有 API Token 访问 Hub API，可选配代理 HTTP 端点。

| 列 | 类型 | 默认值 | 说明 |
|----|------|--------|------|
| `id` | Integer | — | 主键（自增） |
| `name` | Unicode(255) | — | 服务名（唯一） |
| `admin` | Boolean | `False` | 是否管理员权限 |
| `url` | Unicode(2047) | — | 服务 HTTP 端点 URL（nullable） |
| `pid` | Integer | — | 进程 ID（Hub 托管时） |
| `command` | JSONList | — | 启动命令（Hub 托管服务） |
| `cwd` | Unicode(4095) | — | 工作目录 |
| `environment` | JSONDict | — | 环境变量 |
| `info` | JSONDict | — | 服务扩展信息 |
| `oauth_client_allowed_scopes` | JSONList | — | OAuth 客户端允许的权限范围 |
| `display` | Boolean | — | 是否在 UI 中显示 |
| `oauth_no_confirm` | Boolean | — | OAuth 授权时是否跳过确认页 |
| `user` | Unicode(255) | — | 运行服务的系统用户 |
| `timeout` | Integer | `30` | 启动/停止超时（秒） |
| `from_config` | Boolean | `True` | 是否来自配置文件 |

**关系**：`roles`（多对多）、`api_tokens`、`server`（一对一）、`oauth_client`。

---

### APIToken — API 令牌

**表名**：`api_tokens`

API 访问令牌，支持用户和服务两种所有者类型。采用哈希存储（`hashed` 列），不明文保存令牌值。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键 |
| `hashed` | Unicode(255) | 令牌哈希值（唯一） |
| `prefix` | Unicode(16) | 令牌前缀（索引，用于快速查找） |
| `user_id` | Integer (FK→users.id) | 关联用户（nullable，CASCADE） |
| `service_id` | Integer (FK→services.id) | 关联服务（nullable，CASCADE） |
| `client_id` | Unicode(255) (FK→oauth_clients.identifier) | OAuth 客户端（CASCADE，v2.0+） |
| `session_id` | Unicode(255) | 浏览器会话 ID（OAuth cookie 场景） |
| `created` | DateTime | 创建时间 |
| `expires_at` | DateTime | 过期时间（nullable） |
| `last_activity` | DateTime | 最后使用时间 |
| `note` | Unicode(1023) | 令牌备注 |
| `scopes` | JSONList | 令牌权限范围 |

**关键属性/方法**：
- `owner`：返回 `self.user or self.service`，即令牌持有者
- `api_id`：返回 `"a{id}"` 格式的 API 标识
- `find(cls, db, token, *, kind=None)` **classmethod**：按令牌值查找；`kind` 可过滤为 `'user'` 或 `'service'`

---

### OAuthCode / OAuthClient — OAuth 2.0 支持

**OAuthClient**（`oauth_clients` 表）：OAuth 客户端注册信息。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `identifier` | Unicode(255) | 客户端标识（唯一），即 client_id |
| `description` | Unicode(1023) | 客户端描述 |
| `secret` | Unicode(255) | 客户端密钥 |
| `redirect_uri` | Unicode(1023) | 重定向 URI |

**关系**：`spawner`（一对一）、`service`（一对一）、`access_tokens`（APIToken 集合）、`codes`（OAuthCode 集合）。

**OAuthCode**（`oauth_codes` 表）：OAuth 授权码（短生命周期）。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `client_id` | Unicode(255) (FK→oauth_clients.identifier) | 客户端标识 |
| `code` | Unicode(36) | 授权码值 |
| `expires_at` | Integer | 过期时间戳 |
| `redirect_uri` | Unicode(1023) | 请求时的重定向 URI |
| `session_id` | Unicode(255) | 会话 ID |
| `user_id` | Integer (FK→users.id) | 授权用户（CASCADE） |
| `scopes` | JSONList | 授权范围 |
| `code_challenge` | Unicode(255) | PKCE code challenge（v5.3+） |
| `code_challenge_method` | Unicode(64) | PKCE challenge 方法 |

**实用方法**：`find(cls, db, code)` 按授权码查找（自动过滤过期码，预加载用户）。

---

### Share / ShareCode — 笔记本共享

**Share**（`shares` 表）：用户将自己的笔记本服务器共享给其他用户或组的权限记录。共享被限制在单个服务器范围内。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `owner_id` | Integer (FK→users.id) | 共享发起者（服务器所有者） |
| `spawner_id` | Integer (FK→spawners.id) | 目标 Spawner/服务器 |
| `user_id` | Integer (FK→users.id, nullable) | 共享给的用户 |
| `group_id` | Integer (FK→groups.id, nullable) | 共享给的组 |
| `scopes` | JSONList | 授予的权限范围（自动附加 `!server=owner/server` 过滤器） |
| `expires_at` | DateTime | 过期时间（nullable） |
| `created_at` | DateTime | 创建时间 |

**实用方法**：`find(cls, db, spawner, share_with)` 查找指定 (spawner, user/group) 的已有共享。

**ShareCode**（`share_codes` 表）：可兑换的共享码。与 Share 类似，但面向未知用户——通过分享一个 code，对方兑换后创建实际 Share 记录。

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | Integer | 主键（自增） |
| `hashed` | Unicode(255) | 共享码哈希（唯一） |
| `prefix` | Unicode(16) | 共享码前缀（索引） |
| `owner_id` | Integer (FK→users.id) | 共享发起者 |
| `spawner_id` | Integer (FK→spawners.id) | 目标 Spawner |
| `scopes` | JSONList | 授予的权限范围 |
| `expires_at` | DateTime | 过期时间（默认 86400 秒 = 24 小时） |
| `exchange_count` | Integer | 已兑换次数 |
| `last_exchanged_at` | DateTime | 最后兑换时间 |
| `created_at` | DateTime | 创建时间 |

**实用方法**：
- `new(cls, db, spawner, *, scopes, expires_in=None, **kwargs)` **classmethod**：创建新共享码，返回 `(share_code, code_plaintext)` 元组
- `find(cls, db, code, *, spawner=None)` **classmethod**：按码值查找
- `exchange(self, share_with)`：兑换共享码，创建或更新实际 Share 记录

---

## Mixin 基类

| Mixin | 位置 | 功能 |
|-------|------|------|
| `Expiring` | L547 | 提供 `expires_at` 列和 `expired` 属性判断是否过期 |
| `Hashed` | L594 | 继承 Expiring，提供 `hashed`/`prefix` 列、token 哈希匹配（`match()`）、前缀查找（`find_prefix()`）等令牌安全存储能力 |

---

## 表命名约定与外键删除策略

### 命名约定

所有表名使用**复数小写蛇形命名**：`servers`、`users`、`groups`、`roles`、`spawners`、`services`、`api_tokens`、`oauth_clients`、`oauth_codes`、`shares`、`share_codes`。

关联表使用 `{entity}_role_map` 和 `user_group_map` 格式。

### 外键 ON DELETE 策略

| 外键场景 | 策略 | 说明 |
|----------|------|------|
| 角色映射（`*_role_map.*_id` / `role_id`） | `CASCADE` | 删除实体/角色时级联清理关联 |
| 组成员（`user_group_map`） | `CASCADE` | 删除用户/组时级联退出/移除成员 |
| `spawners.user_id` | `CASCADE` | 删除用户时级联删除其所有 Spawner |
| `spawners.server_id` | `SET NULL` | 删除 Server 时保留 Spawner 记录但置空引用 |
| `spawners.oauth_client_id` | `SET NULL` | 删除 OAuth 客户端时置空引用 |
| `api_tokens.user_id` / `service_id` | `CASCADE` | 删除用户/服务时级联删除其令牌 |
| `api_tokens.client_id` | `CASCADE` | 删除 OAuth 客户端时级联删除其令牌 |
| `oauth_codes.client_id` / `user_id` | `CASCADE` | 删除客户端/用户时级联删除授权码 |
| `shares` / `share_codes` 外键 | `CASCADE` | 删除相关实体时级联清理共享记录 |

---

## 实用方法汇总

| 方法 | 所属模型 | 签名 | 说明 |
|------|----------|------|------|
| `find` | Role | `find(cls, db, name)` | 按名称查找角色 |
| `find` | Group | `find(cls, db, name)` | 按名称查找用户组 |
| `find` | User | `find(cls, db, name)` | 按用户名查找用户 |
| `new_api_token` | User | `new_api_token(self, token=None, **kwargs)` | 为用户创建新 API Token |
| `new_api_token` | Service | `new_api_token(self, token=None, **kwargs)` | 为服务创建新 API Token |
| `find` | APIToken | `find(cls, db, token, *, kind=None)` | 按令牌值查找，可过滤用户/服务类型 |
| `find` | OAuthCode | `find(cls, db, code)` | 按授权码查找（自动过滤过期） |
| `find` | Share | `find(cls, db, spawner, share_with)` | 查找 (spawner, 共享目标) 的共享记录 |
| `new` | ShareCode | `new(cls, db, spawner, *, scopes, ...)` | 创建新共享码 |
| `find` | ShareCode | `find(cls, db, code, *, spawner=None)` | 按码值查找共享码 |
| `exchange` | ShareCode | `exchange(self, share_with)` | 兑换共享码为实际 Share |

---

## 源码溯源

- ORM 模块完整源码：[jupyterhub/orm.py](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py)（v6.0.0b2）
- 详细参考文档：[references/orm-source.md](../references/orm-source.md)
