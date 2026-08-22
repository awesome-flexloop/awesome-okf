---
type: Reference
title: JupyterHub ORM 源码参考
description: JupyterHub SQLAlchemy ORM 层核心参考——自定义类型、元数据配置、Server/Role/Group/User/Spawner/Service 等数据表定义及关系映射
tags: [orm, sqlalchemy, database, schema, jupyterhub, role, user, spawner, service, server]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:static-analysis", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: orm-source
    resource: https://github.com/jupyterhub/jupyterhub/blob/6.0.0b2/jupyterhub/orm.py
    title: jupyterhub/orm.py (v6.0.0b2)
---

# JupyterHub ORM 源码参考

> 源码位置：`jupyterhub/orm.py`（前 500 行）

## 模块概览

ORM 模块基于 SQLAlchemy 定义 JupyterHub 进程星座（constellation of processes）的持久化状态。包含自定义列类型（JSONDict/JSONList）、声明式基类 `Base`，以及核心数据表模型。使用 Alembic 进行数据库迁移管理。

### 依赖导入

| 来源 | 导入项 |
|------|--------|
| `sqlalchemy` | `Boolean`, `Column`, `DateTime`, `ForeignKey`, `Integer`, `MetaData`, `Table`, `Unicode`, `create_engine`, `event`, `exc`, `inspect`, `or_`, `select`, `text` |
| `sqlalchemy.orm` | `Session`, `declarative_base`, `declared_attr`, `interfaces`, `joinedload`, `object_session`, `relationship`, `sessionmaker` |
| `sqlalchemy.pool` | `StaticPool` |
| `sqlalchemy.types` | `LargeBinary`, `Text`, `TypeDecorator` |
| `alembic` | `command`, `config` |
| `alembic.script` | `ScriptDirectory` |
| `tornado.log` | `app_log` |

### 模块级变量

| 变量 | 位置 | 说明 |
|------|------|------|
| `utcnow` | [orm.py#L52](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L52) | `partial(utcnow, with_tz=False)` — 无时区 UTC 时间工厂，用于测试 mock |

---

## 自定义列类型

### JSONDict {#JSONDict}

**位置**：[orm.py#L55-L94](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L55-L94)

继承 `sqlalchemy.types.TypeDecorator`，将不可变 Python 结构序列化为 JSON 字符串存储（底层 `Text` 列）。支持 bytes 类型的透明编解码。

| 方法 | 签名 | 说明 |
|------|------|------|
| `_json_default` | `_json_default(self, obj)` | JSON 序列化默认处理：bytes 编码为 `{"__jupyterhub_bytes__": True, "data": base64_str}`；非 JSON 可序列化对象记录警告并返回 `None` |
| `_object_hook` | `_object_hook(self, dct)` | JSON 反序列化钩子：检测 `__jupyterhub_bytes__` 标记并还原为 bytes |
| `process_bind_param` | `process_bind_param(self, value, dialect)` | 写入时调用 `json.dumps(value, default=self._json_default)` |
| `process_result_value` | `process_result_value(self, value, dialect)` | 读取时调用 `json.loads(value, object_hook=self._object_hook)` |

**用法**：`Column(JSONDict)` 或 `Column(JSONDict(255))`

### JSONList {#JSONList}

**位置**：[orm.py#L97-L124](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L97-L124)

继承 `JSONDict`，专用于列表类型列。支持 list/tuple/set 赋值，set 序列化为有序列表（sorted）。

| 方法 | 签名 | 说明 |
|------|------|------|
| `process_bind_param` | `process_bind_param(self, value, dialect)` | list/tuple 直接 `json.dumps`；set 排序后 `json.dumps(sorted(value))` |
| `process_result_value` | `process_result_value(self, value, dialect)` | `None` 返回 `[]`，否则 `json.loads(value)` 返回列表 |

**用法**：`Column(JSONList)` — 读取始终为 list 类型，写入接受 list/tuple/set

---

## 元数据与基类

**位置**：[orm.py#L127-L138](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L127-L138)

```python
meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
Base = declarative_base(metadata=meta)
Base.log = app_log
```

- 使用 SQLAlchemy 约束命名约定，确保 Alembic 迁移的确定性
- `Base` 为所有 ORM 模型的声明基类，挂载 `app_log` 作为日志器

---

## 类层次与表关系

```
Base (declarative_base)
├── Server          # 服务器连接与 Cookie 状态 (L141)
├── Role            # 角色定义 (L194)
├── Group           # 用户组 (L231)
├── User            # 用户 (L264)
├── Spawner         # Spawner 状态 (L389)
└── Service         # 托管服务 (L449)

动态生成的关联表类（L166-L191）：
├── UserRoleMap     # user_role_map 表
├── GroupRoleMap    # group_role_map 表
└── ServiceRoleMap  # service_role_map 表
```

### 关联表（Table 对象）

| 表名 | 位置 | 列 | 说明 |
|------|------|-----|------|
| `user_role_map` | [L173-L187](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L173-L187) | `user_id` (FK→users.id, CASCADE, PK), `role_id` (FK→roles.id, CASCADE, PK), `managed_by_auth` (Boolean, default False) | 用户-角色多对多 |
| `group_role_map` | 同上 | `group_id` (FK→groups.id, CASCADE, PK), `role_id`, `managed_by_auth` | 用户组-角色多对多 |
| `service_role_map` | 同上 | `service_id` (FK→services.id, CASCADE, PK), `role_id`, `managed_by_auth` | 服务-角色多对多 |
| `user_group_map` | [L223-L228](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L223-L228) | `user_id` (FK→users.id, CASCADE, PK), `group_id` (FK→groups.id, CASCADE, PK) | 用户-用户组多对多 |

> 三个 `*_role_map` 表通过循环 `for entity in ('user', 'group', 'service')` 动态创建，对应的映射类通过 `type()` 动态生成并存入 `_role_associations` 字典。

---

## Server 模型

**位置**：[orm.py#L141-L160](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L141-L160)

表名：`servers`，记录服务器的基本连接和 Cookie 信息。

### 列定义

| 列名 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `id` | `Integer` | — | PK | 主键 |
| `proto` | `Unicode(15)` | `'http'` | — | 协议（http/https） |
| `ip` | `Unicode(255)` | `''` | — | IP 地址或 DNS 名称 |
| `port` | `Integer` | `random_port` | — | 端口号，默认随机 |
| `base_url` | `Unicode(255)` | `'/'` | — | 基础 URL 路径 |
| `cookie_name` | `Unicode(255)` | `'cookie'` | — | Cookie 名称 |

### 关系

| 关系 | 目标 | 选项 | 说明 |
|------|------|------|------|
| `service` | `Service` | `back_populates="server"`, `uselist=False` | 一对一反向引用 |
| `spawner` | `Spawner` | `back_populates="server"`, `uselist=False` | 一对一反向引用 |

### 方法

| 方法 | 说明 |
|------|------|
| `__repr__(self)` | 返回 `<Server(ip:port)>` 格式字符串 |

---

## Role 模型

**位置**：[orm.py#L194-L219](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L194-L219)

表名：`roles`，用户/服务/用户组的角色定义，RBAC 权限模型核心。

### 列定义

| 列名 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `id` | `Integer` | — | PK, autoincrement | 主键 |
| `name` | `Unicode(255)` | — | unique | 角色名称（唯一） |
| `description` | `Unicode(1023)` | — | — | 角色描述 |
| `scopes` | `JSONList` | `[]` | — | 角色拥有的权限范围列表 |
| `managed_by_auth` | `Boolean` | `False` | nullable=False | 是否由认证系统自动管理 |

### 关系

| 关系 | 目标 | 中间表 | 说明 |
|------|------|--------|------|
| `users` | `User` | `user_role_map` | 拥有此角色的用户 |
| `services` | `Service` | `service_role_map` | 拥有此角色的服务 |
| `groups` | `Group` | `group_role_map` | 拥有此角色的用户组 |

### 方法

| 方法 | 签名 | 位置 | 说明 |
|------|------|------|------|
| `__repr__` | `__repr__(self)` | [L211-L212](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L211-L212) | 返回 `<Role name (description) - scopes: [...]>` |
| `find` | `find(cls, db, name)` classmethod | [L214-L219](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L214-L219) | 按名称查找角色，返回 None 或 Role 实例 |

---

## Group 模型

**位置**：[orm.py#L231-L261](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L231-L261)

表名：`groups`，用户组定义。

### 列定义

| 列名 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `id` | `Integer` | — | PK, autoincrement | 主键 |
| `name` | `Unicode(255)` | — | unique | 组名（唯一） |
| `properties` | `JSONDict` | `{}` | — | 组属性（扩展字段） |

### 关系

| 关系 | 目标 | 选项 | 说明 |
|------|------|------|------|
| `users` | `User` | `secondary='user_group_map'`, `back_populates='groups'` | 组成员 |
| `roles` | `Role` | `secondary='group_role_map'`, `back_populates='groups'`, `lazy="selectin"` | 组角色 |
| `shared_with_me` | `Share` | `back_populates="group"`, `cascade="all, delete-orphan"`, `lazy="selectin"` | 共享给此组的资源 |

### 类属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `kind` | `"group"` | 实体类型标识，用于区分 owner/actor |

### 方法

| 方法 | 签名 | 位置 | 说明 |
|------|------|------|------|
| `__repr__` | `__repr__(self)` | [L253-L254](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L253-L254) | 返回 `<Group name>` |
| `find` | `find(cls, db, name)` classmethod | [L256-L261](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L256-L261) | 按名称查找组 |

---

## User 模型

**位置**：[orm.py#L264-L386](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L264-L386)

表名：`users`，核心用户表。每个用户可拥有多个单用户 notebook 服务器、API Token、Cookie 会话、OAuth 授权码等。

### 列定义

| 列名 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `id` | `Integer` | — | PK, autoincrement | 主键 |
| `name` | `Unicode(255)` | — | unique | 用户名（唯一） |
| `user_info` | `JSONDict` | — | — | 认证器提供的用户信息 |
| `admin` | `Boolean` | `False` | `create_constraint=False` | 是否管理员（已推荐使用 roles） |
| `created` | `DateTime` | `utcnow` | — | 创建时间 |
| `last_activity` | `DateTime` | — | nullable | 最后活动时间 |
| `cookie_id` | `Unicode(255)` | `new_token` | unique, nullable=False | Cookie 标识，重置可强制重新登录 |
| `state` | `JSONDict` | — | — | Spawner 状态（JSON 字典） |
| `encrypted_auth_state` | `LargeBinary` | — | — | 认证器加密状态 |

### 关系

| 关系 | 目标 | 选项 | 说明 |
|------|------|------|------|
| `roles` | `Role` | `secondary='user_role_map'`, `lazy="selectin"` | 用户角色 |
| `_orm_spawners` | `Spawner` | `back_populates="user"`, `cascade="all, delete-orphan"` | 用户的所有 Spawner（内部） |
| `api_tokens` | `APIToken` | `back_populates="user"`, `cascade="all, delete-orphan"` | API Token |
| `groups` | `Group` | `secondary='user_group_map'`, `lazy="selectin"` | 所属用户组 |
| `oauth_codes` | `OAuthCode` | `back_populates="user"`, `cascade="all, delete-orphan"` | OAuth 授权码 |
| `shares` | `Share` | `back_populates="owner"`, `cascade="all, delete-orphan"`, `foreign_keys="Share.owner_id"` | 用户发起的共享 |
| `share_codes` | `ShareCode` | `back_populates="owner"`, `cascade="all, delete-orphan"`, `foreign_keys="ShareCode.owner_id"` | 共享码 |
| `shared_with_me` | `Share` | `back_populates="user"`, `cascade="all, delete-orphan"`, `foreign_keys="Share.user_id"`, `lazy="selectin"` | 直接共享给用户的资源 |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `orm_spawners` | property → `dict` | `{s.name: s for s in self._orm_spawners}` 按名称索引的 Spawner 字典 |
| `all_shared_with_me` | property → `list` | 合并直接共享和通过组共享的所有 Share 对象（使用 `itertools.chain`） |
| `kind` | class attr → `"user"` | 实体类型标识 |

### 方法

| 方法 | 签名 | 位置 | 说明 |
|------|------|------|------|
| `__repr__` | `__repr__(self)` | [L371-L372](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L371-L372) | 返回 `<User(name running/total running)>` 格式，显示运行中/总 Spawner 数 |
| `new_api_token` | `new_api_token(self, token=None, **kwargs)` | [L374-L379](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L374-L379) | 创建新 API Token；`token` 参数给定则加载已有 token |
| `find` | `find(cls, db, name)` classmethod | [L381-L386](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L381-L386) | 按用户名查找用户 |

---

## Spawner 模型

**位置**：[orm.py#L389-L446](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L389-L446)

表名：`spawners`，记录单个 Spawner 实例的持久化状态。支持每个用户多个命名服务器。

### 列定义

| 列名 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `id` | `Integer` | — | PK, autoincrement | 主键 |
| `user_id` | `Integer` | — | FK→`users.id` (ONDELETE CASCADE) | 所属用户 |
| `server_id` | `Integer` | — | FK→`servers.id` (ONDELETE SET NULL) | 关联服务器 |
| `state` | `JSONDict` | — | — | Spawner 状态字典 |
| `name` | `Unicode(255)` | — | — | 服务器名称（空字符串为默认服务器） |
| `display_name` | `Unicode(255)` | — | — | 显示名称 |
| `started` | `DateTime` | — | — | 启动时间 |
| `last_activity` | `DateTime` | — | nullable | 最后活动时间 |
| `user_options` | `JSONDict` | — | — | 用户选项（表单输入等） |
| `oauth_client_id` | `Unicode(255)` | — | FK→`oauth_clients.identifier` (ONDELETE SET NULL) | OAuth 客户端标识（v2.0+） |

### 关系

| 关系 | 目标 | 选项 | 说明 |
|------|------|------|------|
| `user` | `User` | `back_populates="_orm_spawners"` | 所属用户 |
| `server` | `Server` | `back_populates="spawner"`, `lazy="joined"`, `single_parent=True`, `cascade="all, delete-orphan"` | 关联服务器（joined 预加载） |
| `shares` | `Share` | `back_populates="spawner"`, `cascade="all, delete-orphan"` | 关联的共享 |
| `share_codes` | `ShareCode` | `back_populates="spawner"`, `cascade="all, delete-orphan"` | 关联的共享码 |
| `oauth_client` | `OAuthClient` | `back_populates="spawner"`, `cascade="all, delete-orphan"`, `single_parent=True` | OAuth 客户端 |

### 包装器属性（ORM 层默认值，运行时被 Spawner 包装器覆盖）

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `active` | `False` | Spawner 是否活跃 |
| `running` | `False` | 是否运行中 |
| `ready` | `False` | 是否就绪 |
| `pending` | `None` | 待处理状态（`'spawn'`/`'stop'` 等） |
| `orm_spawner` | `self` | 返回自身（兼容包装器接口） |

---

## Service 模型

**位置**：[orm.py#L449-L500](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyterhub/jupyterhub/orm.py#L449-L500)（前 500 行范围内）

表名：`services`，JupyterHub 托管服务。Service 类似没有 Spawner 的 User，可以拥有 API Token 访问 Hub API，可选配代理 HTTP 端点。

### 列定义

| 列名 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `id` | `Integer` | — | PK, autoincrement | 主键 |
| `name` | `Unicode(255)` | — | unique | 服务名（唯一） |
| `admin` | `Boolean` | `False` | `create_constraint=False` | 是否管理员权限 |
| `url` | `Unicode(2047)` | — | nullable | 服务 URL（有 HTTP 端点时设置） |
| `oauth_client_allowed_scopes` | `JSONList` | — | nullable | OAuth 客户端允许的权限范围 |
| `info` | `JSONDict` | — | nullable | 服务信息（扩展字段） |
| `display` | `Boolean` | — | nullable | 是否在 UI 中显示 |
| `oauth_no_confirm` | `Boolean` | — | nullable | OAuth 授权时是否跳过确认页 |
| `command` | `JSONList` | — | nullable | 启动命令（Hub 托管服务） |
| `cwd` | `Unicode(4095)` | — | nullable | 工作目录 |
| `environment` | `JSONDict` | — | nullable | 环境变量 |
| `user` | `Unicode(255)` | — | nullable | 运行服务的用户 |
| `timeout` | `Integer` | `30` | nullable=False | 启动/停止超时（秒） |
| `from_config` | `Boolean` | `True` | — | 是否来自配置文件 |

### 关系（前 500 行已见部分）

| 关系 | 目标 | 选项 | 说明 |
|------|------|------|------|
| `roles` | `Role` | `secondary='service_role_map'`, `lazy="selectin"` | 服务角色 |
| `api_tokens` | `APIToken` | `back_populates="service"`, `cascade="all, delete-orphan"` | API Token（L499 起始） |
| `server` | `Server` | (通过 Server.service 反向引用) | 关联服务器（一对一） |

> 注：Service 的完整定义（包括 `server` 关系、`oauth_client` 等）超出前 500 行范围，需参阅源码后续部分。

---

## 外键删除策略汇总

| 外键 | ON DELETE 策略 | 说明 |
|------|---------------|------|
| `*_role_map.*_id` | `CASCADE` | 删除实体时级联删除角色关联 |
| `*_role_map.role_id` | `CASCADE` | 删除角色时级联删除关联 |
| `user_group_map.user_id` | `CASCADE` | 删除用户时级联退出组 |
| `user_group_map.group_id` | `CASCADE` | 删除组时级联移除成员 |
| `spawners.user_id` | `CASCADE` | 删除用户时级联删除其 Spawner |
| `spawners.server_id` | `SET NULL` | 删除服务器时置空 Spawner 引用 |
| `spawners.oauth_client_id` | `SET NULL` | 删除 OAuth 客户端时置空引用 |
