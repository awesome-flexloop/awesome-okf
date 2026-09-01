---
type: Concept
title: 配置体系
description: Config 层级合并、SSH config 文件集成、环境变量、fab 命令行选项与配置优先级
tags: [fabric, configuration, config, ssh-config]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 配置体系

## 双层配置架构

fabric 的配置系统由两个独立但协作的体系组成：

1. **invoke 风格配置**：继承自 `invoke.Config` 的六层合并体系，承载所有运行时行为配置
2. **SSH config 文件体系**：独立的 `paramiko.config.SSHConfig` 对象，专门承载 OpenSSH 配置文件数据

两者不合并，在 Connection 初始化时各取所需。

```
┌─────────────────────────────────────────────┐
│           invoke 六层配置体系                │
│  (dict 树，通过 merge_dicts 合并)            │
├─────────────────────────────────────────────┤
│ defaults ← collection ← system ← user       │
│       ← runtime ← overrides(CLI)            │
├─────────────────────────────────────────────┤
│  数据：port, user, run, sudo, connect_kwargs │
│       gateway, forward_agent, runners...     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│        SSH config 文件体系（独立）            │
│  (paramiko.config.SSHConfig 对象)            │
├─────────────────────────────────────────────┤
│  /etc/ssh/ssh_config (system)               │
│  ~/.ssh/config (user)                       │
│  runtime path (-S/--ssh-config)             │
├─────────────────────────────────────────────┤
│  数据：Hostname, User, Port, ProxyJump,     │
│       IdentityFile, ForwardAgent...         │
└─────────────────────────────────────────────┘
```

## Config 类

`fabric.Config` 继承 `invoke.config.Config`，主要扩展：

- 设置 `prefix = "fabric"`（环境变量前缀为 `FABRIC_`）
- 扩展 `global_defaults()` 添加 SSH 相关默认值
- 增加 SSH config 文件加载机制
- 增加 `from_v1()` 迁移构造器

### 默认值

`Config.global_defaults()` 在 invoke 默认值基础上添加/修改：

| 配置键 | 默认值 | 说明 |
|--------|--------|------|
| `port` | `22` | SSH 默认端口 |
| `user` | `get_local_user()` | 当前系统用户名 |
| `forward_agent` | `False` | 是否转发 SSH agent |
| `gateway` | `None` | 默认跳板机 |
| `inline_ssh_env` | `True` | 环境变量以内联 export 方式传递 |
| `load_ssh_configs` | `True` | 是否自动加载 SSH config 文件 |
| `ssh_config_path` | `None` | 运行时 SSH config 路径 |
| `connect_kwargs` | `{}` | 透传给 paramiko 的参数 |
| `tasks.collection_name` | `"fabfile"` | 任务模块名 |
| `timeouts.connect` | `None` | 连接超时 |
| `runners.remote` | `Remote` | 远程命令 Runner 类 |
| `runners.remote_shell` | `RemoteShell` | 交互式 Shell Runner 类 |
| `authentication.identities` | `[]` | 认证身份列表 |
| `authentication.strategy_class` | `None` | 认证策略类 |

### invoke 六层优先级

从低到高：

1. **defaults**：`global_defaults()` 静态方法返回值
2. **collection**：任务集合自带配置（fabfile 中的 `ns.configure()`）
3. **system**：系统级配置文件（`/etc/fabric.yml`）
4. **user**：用户级配置文件（`~/.fabric.yml`）
5. **runtime**：运行时配置文件（项目目录下的 `fabric.yml`）
6. **overrides**：CLI 参数和程序化覆盖（最高优先级）

### 配置文件格式

fabric 使用 invoke 的配置文件加载机制，支持 YAML、JSON、Python 等格式。文件名前缀为 `fabric`：

- `/etc/fabric.yml`（系统级）
- `~/.fabric.json`（用户级）
- `./fabric.yaml`（项目/运行时级）

示例 `fabric.yml`：

```yaml
user: deploy
port: 22
forward_agent: true
connect_kwargs:
  key_filename: /home/user/.ssh/id_ed25519
run:
  hide: true
  warn: true
```

### 环境变量

前缀为 `FABRIC_`，使用双下划线表示嵌套：

```bash
export FABRIC_USER=deploy
export FABRIC_PORT=2222
export FABRIC_CONNECT_KWARGS__KEY_FILENAME=/path/to/key
export FABRIC_RUN__HIDE=true
```

## SSH config 文件体系

### 三级路径

Config 在初始化时建立 SSH config 路径：

| 级别 | 参数 | 默认值 | 行为 |
|------|------|--------|------|
| system | `system_ssh_path` | `/etc/ssh/ssh_config` | 自动加载，文件不存在静默跳过 |
| user | `user_ssh_path` | `~/.ssh/config` | 自动加载，文件不存在静默跳过 |
| runtime | `runtime_ssh_path` | `None` | 若设置则**只加载**此文件，跳过 system/user；文件不存在抛 FileNotFoundError |

### 加载流程

1. `Config.__init__` 中若 `lazy=False`，调用 `load_ssh_config()`
2. `load_ssh_config()` 先检查 invoke 配置中的 `ssh_config_path` 值更新 runtime 路径
3. 若未给定显式 SSHConfig 对象，调用 `_load_ssh_files()`
4. `_load_ssh_files()` 按优先级加载：
   - 若 `_runtime_ssh_path` 不为 None：只加载该路径（不存在则抛异常）
   - 否则：若 `load_ssh_configs=True`，依次加载 user 和 system 路径（不存在则跳过）

### 显式 SSHConfig 对象

可以传入预构建的 `paramiko.config.SSHConfig` 对象，阻止文件加载：

```python
from paramiko.config import SSHConfig

ssh_config = SSHConfig()
with open("~/.ssh/custom_config") as f:
    ssh_config.parse(f)

config = Config(ssh_config=ssh_config)
```

### set_runtime_ssh_path()

程序运行时动态指定 SSH config 路径：

```python
config.set_runtime_ssh_path("/path/to/ssh_config")
config.load_ssh_config()
```

设置后重新加载只读取该文件。

### clone() 行为

`Config.clone()` 复制 SSH config 路径属性，并通过深拷贝 `base_ssh_config._config` 内部字典来传递已解析的数据，避免重复读取文件。

## CLI 参数与配置映射

`fab` 命令的参数会写入 overrides 层级：

| CLI 参数 | 配置路径 | 说明 |
|----------|---------|------|
| `-H`, `--hosts` | core args（非配置树） | 主机列表，由 Executor 处理 |
| `-i`, `--identity` | `connect_kwargs.key_filename` + `authentication.identities` | 私钥路径列表 |
| `-S`, `--ssh-config` | 设置 runtime_ssh_path | SSH config 文件路径 |
| `-t`, `--connect-timeout` | `connect_kwargs.timeout` | 连接超时 |
| `--prompt-for-login-password` | `connect_kwargs.password` | 提示输入密码 |
| `--prompt-for-passphrase` | `connect_kwargs.passphrase` | 提示输入密钥密码短语 |
| `--list-agent-keys` | （特殊行为） | 列出 agent 密钥后退出 |

## 配置解析示例

以下几种方式均可达到"以 admin 用户连接 myhost"的效果：

```python
# 1. 直接参数
Connection("myhost", user="admin")

# 2. 简写
Connection("admin@myhost")

# 3. fabric 配置文件
# ~/.fabric.yml: user: admin
Connection("myhost")

# 4. SSH config 文件
# ~/.ssh/config:
#   Host myhost
#       User admin
Connection("myhost")
```

优先级：SSH config 值 < fabric Config 值 < 构造函数显式参数。

## 认证配置

### authentication 配置节

fabric 3.1+ 支持新的认证策略框架：

```yaml
authentication:
  identities:
    - /path/to/key1
    - /path/to/key2
  strategy_class: fabric.auth.OpenSSHAuthStrategy
```

当 `authentication.strategy_class` 被设置时，`Connection.open()` 会：
1. 从 connect_kwargs 中移除 `allow_agent`、`key_filename`、`look_for_keys`、`passphrase`、`password`、`pkey`、`username`
2. 创建认证策略实例，传入 ssh_config、fabric_config、username
3. 通过 `auth_strategy` 参数传给 `SSHClient.connect()`

### OpenSSHAuthStrategy

`fabric.auth.OpenSSHAuthStrategy` 模拟 OpenSSH 客户端的认证顺序：
1. 配置文件中的证书
2. CLI 指定的证书
3. ssh-agent 中的密钥（配置文件中提及的优先）
4. CLI 指定的普通密钥
5. 配置文件中的普通密钥
6. 密码提示

详见 [高级模式](08-advanced-patterns.md)。

## from_v1() 迁移

`Config.from_v1(env)` 从 Fabric 1.x 的 env 字典迁移配置：

```python
config = Config.from_v1(env)
connection = Connection.from_v1(env)
```

映射关系包括：`always_use_pty` → `run.pty`、`gateway`、`forward_agent`、`key_filename`、`no_agent` → `connect_kwargs.allow_agent`、`sudo_password`/`password`、`sudo_prompt`、`timeout` → `timeouts.connect`、`use_ssh_config` → `load_ssh_configs`、`warn_only` → `run.warn`。

## 相关概念

- [Connection 详解](02-connection.md)
- [命令执行](04-command-execution.md)
- [高级模式](08-advanced-patterns.md)
- [pyinvoke 配置](../../../../build/tooling/pyinvoke/index.md)
