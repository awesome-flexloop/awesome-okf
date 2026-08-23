---
type: Concept
title: 配置系统
description: 9层配置优先级、配置文件格式（yaml/json/python）、环境变量加载、运行时覆盖、DataProxy双模式访问
tags: [pyinvoke, config, configuration, DataProxy, yaml, json, environment-variables, merge_dicts]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# 配置系统

Invoke 的配置系统是其灵活性的核心支柱之一。它通过一个多层级合并机制，将来自不同来源的配置值按优先级顺序叠加，最终形成任务执行时使用的统一配置视图。`Config` 类继承自 `DataProxy`，同时支持字典风格（`config['key']`）和属性风格（`config.key`）的双重访问模式。

## DataProxy：双模式访问代理

`DataProxy` 是 `Config` 的基类，实现了嵌套字典的属性/字典双访问模式。当你通过属性方式访问一个字典类型的值时，DataProxy 会自动将其包装为子 DataProxy，实现递归的属性访问：

```python
from invoke import Config

c = Config()
# 字典风格访问
print(c['run']['echo'])      # False
# 属性风格访问（等效）
print(c.run.echo)            # False
# 混合嵌套访问
print(c['run'].echo)         # False
print(c.run['echo'])         # False
```

DataProxy 会自动代理所有标准字典方法（`keys()`、`values()`、`items()`、`get()`、`pop()`、`update()`、`clear()` 等），因此可以像操作普通字典一样操作 Config 对象。需要注意的是，如果配置键名与 DataProxy/Config 的方法名冲突，必须使用字典语法访问。

## 9 层配置优先级

Config 内部维护 9 个配置层级，按从低到高的优先级依次合并。高优先级的值会覆盖低优先级的同名键值，但字典类型的值会递归合并而非整体替换。

| 优先级 | 层级 | 属性名 | 来源说明 |
|--------|------|--------|----------|
| 1（最低） | 默认值 | `_defaults` | `Config.global_defaults()` 提供的内置默认值 |
| 2 | 集合配置 | `_collection` | 通过 `ns.configure()` 或 Collection 树加载的配置 |
| 3 | 系统级 | `_system` | 系统级配置文件（Unix: `/etc/invoke.yaml`） |
| 4 | 用户级 | `_user` | 用户级配置文件（`~/.invoke.yaml`） |
| 5 | 项目级 | `_project` | 项目目录下的配置文件（`./invoke.yaml`） |
| 6 | 环境变量 | `_env` | `INVOKE_` 前缀的环境变量 |
| 7 | 运行时文件 | `_runtime` | 通过 `--config`/`-f` 指定的运行时配置文件 |
| 8 | CLI 覆盖 | `_overrides` | 命令行标志解析结果（如 `--echo`、`--warn-only`） |
| 9 | 运行时修改 | `_modifications` | 代码中直接对 Config 对象的修改 |
| — | 删除记录 | `_deletions` | 通过 `pop()`/`del`/`clear()` 删除的键路径 |

合并顺序在 `Config.merge()` 方法中严格定义：先合并默认值，再逐层叠加，最后应用删除记录。

## global_defaults()：内置默认值

`Config.global_defaults()` 是一个静态方法，定义了 Invoke 的所有内置默认配置。子类可以覆盖此方法来添加或修改默认值。核心默认值包括：

```python
{
    "run": {
        "asynchronous": False,
        "disown": False,
        "dry": False,
        "echo": False,          # 是否打印执行的命令
        "echo_stdin": None,     # 是否回显 stdin
        "encoding": None,       # 输出编码（None = 自动检测）
        "env": {},              # 子进程环境变量更新
        "err_stream": None,     # stderr 目标流
        "fallback": True,       # pty 不可用时是否回退
        "hide": None,           # 隐藏输出级别
        "in_stream": None,      # stdin 来源流
        "out_stream": None,     # stdout 目标流
        "echo_format": "\033[1;37m{command}\033[0m",  # echo 格式
        "pty": False,           # 是否使用伪终端
        "replace_env": False,   # 是否替换整个环境
        "shell": "bash",        # Unix 默认 shell；Windows 使用 COMSPEC 或 cmd.exe
        "warn": False,          # 命令失败时是否仅警告
        "watchers": [],         # StreamWatcher 列表
    },
    "runners": {"local": Local},  # 本地运行器类
    "sudo": {
        "password": None,
        "prompt": "[sudo] password: ",
        "user": None,
    },
    "tasks": {
        "auto_dash_names": True,      # 自动将下划线转为短横线
        "collection_name": "tasks",    # 默认任务模块名
        "dedupe": True,                # 是否去重任务
        "executor_class": None,        # 自定义执行器类路径
        "ignore_unknown_help": False,  # 是否忽略未知 help 参数
        "search_root": None,           # 任务搜索根目录
    },
    "timeouts": {"command": None},     # 命令超时
}
```

Windows 平台下，`run.shell` 默认值会从环境变量 `COMSPEC` 获取，回退到 `cmd.exe`。

## 配置文件格式与搜索顺序

Invoke 支持三种配置文件格式，按以下后缀优先级搜索：

1. **YAML**：`.yaml`（首选）
2. **YAML**：`.yml`
3. **JSON**：`.json`
4. **Python**：`.py`

对于每一级配置文件位置（system/user/project/runtime），Invoke 会按上述后缀顺序依次尝试加载，找到第一个存在的文件即停止。例如系统级配置会依次尝试 `/etc/invoke.yaml` → `/etc/invoke.yml` → `/etc/invoke.json` → `/etc/invoke.py`。

### 配置文件位置

| 层级 | 默认路径前缀 | 示例路径 |
|------|-------------|----------|
| 系统级 | `/etc/`（Unix 独有） | `/etc/invoke.yaml` |
| 用户级 | `~/.` | `~/.invoke.yaml` |
| 项目级 | 任务集合所在目录 | `./invoke.yaml` |
| 运行时 | 由 `--config`/`-f` 指定 | 任意完整路径 |

### YAML 配置示例

```yaml
# invoke.yaml
run:
  echo: true
  warn: true
  shell: /bin/zsh

tasks:
  auto_dash_names: false

sudo:
  password: "mysecret"
```

### JSON 配置示例

```json
{
  "run": {
    "echo": true,
    "pty": true
  }
}
```

### Python 配置示例

```python
# invoke.py
# Python 配置文件中所有非 __ 开头的顶层变量都会被加载
debug = True
run = {"echo": True, "warn": False}
```

Python 配置文件中不能包含模块对象（会抛出 `UnpicklableConfigMember` 异常）。

## 环境变量加载

以 `INVOKE_` 前缀（大写）命名的环境变量会被自动加载为配置值。环境变量名通过以下规则映射到配置键路径：

1. 去除 `INVOKE_` 前缀
2. 按下划线 `_` 分割为嵌套键路径
3. 转为全大写匹配已有配置键

例如：

| 环境变量 | 映射到配置键 |
|----------|-------------|
| `INVOKE_RUN_ECHO=1` | `run.echo = True` |
| `INVOKE_RUN_WARN=1` | `run.warn = True` |
| `INVOKE_RUN_HIDE=both` | `run.hide = "both"` |
| `INVOKE_TASKS_DEDUPE=0` | `tasks.dedupe = False` |

`Environment` 类负责环境变量的递归扫描与类型转换，其类型转换规则如下：

- **布尔值**：已有值为 `bool` 类型时，`"0"` 和空字符串 `""` 转为 `False`，其他值转为 `True`
- **字符串**：已有值为 `str` 类型时，直接使用环境变量字符串值
- **None**：已有值为 `None` 时，直接使用字符串值
- **数值类型**：已有值为 `int`/`float` 时，调用对应类型构造函数转换
- **列表/元组**：不支持，抛出 `UncastableEnvVar` 异常
- **歧义键**：如果多个路径映射到同一个环境变量名，抛出 `AmbiguousEnvVar` 异常

环境变量加载必须在其他所有配置层加载完成后执行（`Config.load_shell_env()`），因为它依赖已有配置结构来确定有效的键路径和类型。

## merge_dicts：递归合并

`merge_dicts(base, updates)` 是配置合并的核心函数，它将 `updates` 字典递归合并到 `base` 字典中（修改 `base`）：

- 两个值都是字典时，递归进入合并
- 一个是字典另一个不是时，抛出 `AmbiguousMergeError`
- 非字典叶子值通过 `copy.copy()` 复制，避免状态共享
- 有 `fileno()` 属性的对象（真实文件）按引用传递

```python
from invoke.config import merge_dicts

base = {"run": {"echo": False, "warn": False}, "tasks": {"dedupe": True}}
overrides = {"run": {"echo": True}, "sudo": {"password": "secret"}}
merge_dicts(base, overrides)
# base 变为:
# {"run": {"echo": True, "warn": False}, "tasks": {"dedupe": True}, "sudo": {"password": "secret"}}
```

## Config.clone()：配置副本

`Config.clone(into=None)` 创建当前配置对象的独立副本。新对象在配置源和已加载数据上与原对象相同，但拥有独立的可变状态。关键特性：

- 所有字典值递归重建，非字典叶子值使用 `copy.copy()`（而非 `deepcopy`，避免编译正则、线程锁等对象的复制问题）
- `into` 参数允许克隆到 Config 子类，并合并子类的 `global_defaults()`
- 克隆后系统/用户配置文件会重新加载，runtime/overrides 等数据通过复制传递

```python
from invoke import Config

original = Config(overrides={"run": {"echo": True}})
cloned = original.clone()
cloned.run.warn = True
# original.run.warn 仍为 False（独立副本）
```

## 配置生命周期

Config 的加载遵循特定的生命周期顺序：

1. **`__init__`**：创建各层级数据结构，自动加载系统级和用户级配置文件（可通过 `lazy=True` 跳过），执行首次 `merge()`
2. **`load_overrides()`**：加载 CLI 解析结果到 overrides 层
3. **`set_project_location()` + `load_project()`**：设置项目目录并加载项目级配置
4. **`set_runtime_path()` + `load_runtime()`**：加载运行时指定的配置文件
5. **`load_collection()`**：执行每个任务前，加载对应 Collection 的配置
6. **`load_shell_env()`**：最后加载环境变量（依赖前面所有层级确定有效键路径）
7. **运行时修改**：代码中对 Config 的直接赋值存储在 `_modifications` 层，`del`/`pop`/`clear()` 记录在 `_deletions` 层

这种设计使得配置来源可以被清晰追踪——任何最终值都可以追溯到具体的配置层级。

## 相关概念

- [Context 对象](/concepts/03-context-object.md)
- [Collection 与命名空间](/concepts/04-collection-namespace.md)
- [Runner 系统](/concepts/06-runners.md)
- [CLI 与 Program 类](/concepts/07-cli-program.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Config 类与 DataProxy 定义于 `invoke/config.py`，Environment 类定义于 `invoke/env.py`。
