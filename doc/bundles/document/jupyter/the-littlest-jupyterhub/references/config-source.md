---
type: Reference
title: config.py 源码信源
description: tljh/config.py 模块公共 API 信源文档
tags: [reference, source, config, tljh-config, cli, api]
sources:
  - id: tljh-config
    title: tljh/config.py
---

# config.py 源码信源

> TLJH 配置管理核心模块。提供 YAML 配置文件的读写操作、tljh-config CLI 入口、配置验证、服务重载等功能。

## 路径常量

```python
INSTALL_PREFIX = os.environ.get("TLJH_INSTALL_PREFIX", "/opt/tljh")
HUB_ENV_PREFIX = os.path.join(INSTALL_PREFIX, "hub")
USER_ENV_PREFIX = os.path.join(INSTALL_PREFIX, "user")
STATE_DIR = os.path.join(INSTALL_PREFIX, "state")
CONFIG_DIR = os.path.join(INSTALL_PREFIX, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
```

## 公共函数

### `config_file_lock(config_path, timeout=1)`（上下文管理器）

使用 FileLock 对配置文件加互斥锁。锁文件为 `{config_path}.lock`，超时 1 秒。

### `set_item_in_config(config, property_path, value) → dict`

对点分路径（如 `https.enabled`）设置值。使用 deepcopy 不修改原 dict。非叶节点不存在时创建空 dict。设置是破坏性的（替换已有子树）。

### `unset_item_from_config(config, property_path) → dict`

删除点分路径的键。deepcopy 不修改原 dict。删除后递归清理空 dict 父节点。

### `add_item_to_config(config, property_path, value) → dict`

向点分路径的列表追加值。目标不存在或不是列表时初始化为空列表。

### `remove_item_from_config(config, property_path, value) → dict`

从点分路径的列表中移除值。目标不是列表时抛 ValueError。

### `validate_config(config, validate=True)`

使用 jsonschema 验证 config。schema 来自 `config_schema.py`。validate=False 时跳过校验；validate=True 时校验失败调用 sys.exit(1)。

### `show_config(config_path)`

读取配置文件并 yaml.dump 到 stdout。

### `set_config_value(config_path, property_path, value, validate=True)`

在 config_file_lock 内：读取配置 → set_item_in_config → validate_config → 写回文件。

### `unset_config_value(config_path, property_path, validate=True)`

在 config_file_lock 内：读取配置 → unset_item_from_config → validate_config → 写回文件。

### `add_config_value(config_path, property_path, value, validate=True)`

在 config_file_lock 内：读取配置 → add_item_to_config → validate_config → 写回文件。

### `remove_config_value(config_path, property_path, value, validate=True)`

在 config_file_lock 内：读取配置 → remove_item_from_config → validate_config → 写回文件。

### `get_current_config(config_path) → dict`

读取 YAML 配置文件返回 dict。文件不存在时返回空 dict。

### `check_hub_ready(address, port, base_url) → bool`

HTTP GET 请求 `http://{address}:{port}{base_url}/hub/api`，返回 status_code==200。从 config 读取 http/base_url 配置。

### `reload_component(component)`

重载指定组件：
- `hub`：重启 jupyterhub.service，循环等待 Hub 就绪（最多100次）
- `proxy`：重新生成 Traefik 配置（`traefik.ensure_traefik_config`），重启 traefik.service

### `parse_value(value_str) → value`

解析字符串值为 Python 类型：`"none"`→None、纯数字→int、浮点→float、`"true"/"false"`→bool、其余返回原字符串。

### `main(argv=None)`

tljh-config CLI 入口：
1. 检查 `os.geteuid()!=0` 则报错退出（必须 root）
2. 支持全局参数：`--config-path`（默认 CONFIG_FILE）、`--validate/--no-validate`（默认 validate=True）
3. 子命令：
   - `show`：显示配置
   - `set <path> <value>`：设置值（value 通过 parse_value 解析）
   - `unset <path>`：删除值
   - `add-item <path> <value>`：追加列表项
   - `remove-item <path> <value>`：移除列表项
   - `reload [hub|proxy]`：重载组件（无参数则重载全部）

## CLI 入口点

```
tljh-config = tljh.config:main
```
