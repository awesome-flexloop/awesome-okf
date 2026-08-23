---
okf_version: "0.2"
type: concept
title: "环境变量参考"
description: "jupyter_core 支持的所有环境变量的完整参考：变量名、类型、作用、默认值、使用示例。"
tags: [jupyter, core, environment-variables, configuration, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paths-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/paths.py"
    title: "jupyter_core/paths.py"
  - id: command-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/command.py"
    title: "jupyter_core/command.py"
  - id: migrate-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/migrate.py"
    title: "jupyter_core/migrate.py"
  - id: troubleshoot-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/troubleshoot.py"
    title: "jupyter_core/troubleshoot.py"
---

# 环境变量参考

jupyter_core 通过环境变量提供灵活的配置选项，允许用户自定义目录位置、路径搜索行为、安全设置等。本文档列出所有支持的环境变量及其用法。

## 布尔值解析规则

布尔类型的环境变量通过 `envset()` 函数解析。以下值（不区分大小写）被视为 `False`：

- `no`, `n`, `false`, `off`, `0`, `0.0`

其他非空值被视为 `True`。如果环境变量未设置，返回指定的默认值。

## 完整环境变量列表

### JUPYTER_CONFIG_DIR

| 属性 | 值 |
|------|-----|
| **类型** | 路径字符串 |
| **作用** | 覆盖 Jupyter 配置目录的位置 |
| **默认值** | 平台相关：Linux/macOS 为 `~/.jupyter`；Windows 为 `%APPDATA%\jupyter`。设置 `JUPYTER_PLATFORM_DIRS=1` 时使用 platformdirs 的 user_config_dir |
| **影响模块** | `paths.py` |

**使用示例（Bash/Zsh）：**

```bash
# 使用自定义配置目录
export JUPYTER_CONFIG_DIR="$HOME/.my-jupyter-config"
jupyter notebook
```

**使用示例（Python）：**

```python
import os
os.environ["JUPYTER_CONFIG_DIR"] = "/custom/config/path"

from jupyter_core.paths import jupyter_config_dir
print(jupyter_config_dir())  # /custom/config/path
```

---

### JUPYTER_DATA_DIR

| 属性 | 值 |
|------|-----|
| **类型** | 路径字符串 |
| **作用** | 覆盖 Jupyter 数据目录的位置（存放 kernels、nbextensions 等） |
| **默认值** | 平台相关：Linux 为 `~/.local/share/jupyter`；macOS 为 `~/Library/Jupyter`；Windows 为 `%APPDATA%\jupyter\data`。设置 `JUPYTER_PLATFORM_DIRS=1` 时使用 platformdirs 的 user_data_dir |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
export JUPYTER_DATA_DIR="/opt/jupyter-data"
```

---

### JUPYTER_RUNTIME_DIR

| 属性 | 值 |
|------|-----|
| **类型** | 路径字符串 |
| **作用** | 覆盖 Jupyter 运行时目录的位置（存放内核连接文件、PID 等临时文件） |
| **默认值** | `{jupyter_data_dir}/runtime` |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
# 将运行时文件放到 tmpfs 以提升性能
export JUPYTER_RUNTIME_DIR="/tmp/jupyter-runtime"
```

---

### JUPYTER_PATH

| 属性 | 值 |
|------|-----|
| **类型** | 路径列表（使用 `os.pathsep` 分隔，Linux/macOS 用 `:`，Windows 用 `;`） |
| **作用** | 附加到数据搜索路径的最前面（最高优先级），用于添加额外的数据文件搜索位置 |
| **默认值** | 空（不附加） |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
# 添加多个数据搜索路径
export JUPYTER_PATH="/opt/jupyter-extras:$HOME/.local/jupyter-extras"
```

```python
from jupyter_core.paths import jupyter_path
# JUPYTER_PATH 中的路径会出现在返回列表的最前面
for p in jupyter_path():
    print(p)
```

---

### JUPYTER_CONFIG_PATH

| 属性 | 值 |
|------|-----|
| **类型** | 路径列表（`os.pathsep` 分隔） |
| **作用** | 附加到配置搜索路径的最前面（最高优先级），用于添加额外的配置文件搜索位置 |
| **默认值** | 空（不附加） |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
export JUPYTER_CONFIG_PATH="/etc/jupyter-custom:/opt/jupyter-config"
```

---

### JUPYTER_NO_CONFIG

| 属性 | 值 |
|------|-----|
| **类型** | 布尔值 |
| **作用** | 启用"无配置"隔离模式。配置目录使用临时空目录，忽略用户配置和系统配置。适用于测试、CI 环境或需要干净环境的场景。 |
| **默认值** | `False` |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
# 在 CI 中使用干净环境
export JUPYTER_NO_CONFIG=1
pytest tests/
```

设置后，`jupyter_config_dir()` 返回一个通过 `tempfile.mkdtemp` 创建的临时目录（同一进程内复用），`jupyter_config_path()` 仅返回该临时目录。

---

### JUPYTER_PLATFORM_DIRS

| 属性 | 值 |
|------|-----|
| **类型** | 布尔值 |
| **作用** | 启用 platformdirs 标准路径模式。使用各操作系统的标准目录规范（如 XDG、AppData 等），而非 Jupyter 传统路径。 |
| **默认值** | `False`（使用传统路径） |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
# 使用 XDG 标准路径（Linux）
export JUPYTER_PLATFORM_DIRS=1
jupyter --config-dir  # ~/.config/jupyter
jupyter --data-dir    # ~/.local/share/jupyter
```

> **注意**：启用后系统级路径也会变化。Linux 下系统配置路径变为 `/etc/xdg/jupyter` 等 platformdirs 的 site_config_dir。

---

### JUPYTER_PREFER_ENV_PATH

| 属性 | 值 |
|------|-----|
| **类型** | 布尔值 |
| **作用** | 控制环境目录（`{sys.prefix}/share/jupyter` 和 `{sys.prefix}/etc/jupyter`）是否优先于用户目录。未设置时自动检测：虚拟环境和非 base conda 环境下默认为 `True`。 |
| **默认值** | 自动检测 |
| **影响模块** | `paths.py` |

**使用示例：**

```bash
# 显式要求用户目录优先（即使在虚拟环境中）
export JUPYTER_PREFER_ENV_PATH=0

# 显式要求环境目录优先
export JUPYTER_PREFER_ENV_PATH=1
```

---

### JUPYTER_USE_PROGRAMDATA

| 属性 | 值 |
|------|-----|
| **类型** | 布尔值 |
| **作用** | **Windows 专用**。启用后使用 `%PROGRAMDATA%\jupyter` 作为系统级路径。出于安全考虑，默认不启用（`%PROGRAMDATA%` 对所有用户可写）。 |
| **默认值** | `False` |
| **影响模块** | `paths.py` |

**使用示例：**

```powershell
# Windows: 启用 PROGRAMDATA 系统路径
set JUPYTER_USE_PROGRAMDATA=1
```

---

### JUPYTER_ALLOW_INSECURE_WRITES

| 属性 | 值 |
|------|-----|
| **类型** | 布尔值 |
| **作用** | 允许跳过 `secure_write()` 的文件权限检查。适用于不支持 POSIX 权限的文件系统（如 CIFS/SMB 挂载）。启用会发出警告。 |
| **默认值** | `False` |
| **影响模块** | `paths.py`, `application.py` |

**使用示例：**

```bash
# 在网络文件系统上使用
export JUPYTER_ALLOW_INSECURE_WRITES=1
```

---

### IPYTHONDIR

| 属性 | 值 |
|------|-----|
| **类型** | 路径字符串 |
| **作用** | 指定 IPython 配置目录位置。`jupyter-migrate` 使用此变量定位旧版 IPython 配置。 |
| **默认值** | `~/.ipython` |
| **影响模块** | `migrate.py` |

**使用示例：**

```bash
export IPYTHONDIR="$HOME/.my-ipython"
jupyter-migrate
```

---

### _ARGCOMPLETE

| 属性 | 值 |
|------|-----|
| **类型** | 由 argcomplete 库自动设置 |
| **作用** | Tab 补全标记。argcomplete 库在触发补全时设置此环境变量。`jupyter` 命令检测到此变量时进入补全模式；`jupyter-troubleshoot` 检测到此变量时立即退出以避免卡顿。 |
| **默认值** | 未设置（用户不需要手动设置） |
| **影响模块** | `command.py`, `troubleshoot.py` |

用户通常不需要手动设置此变量。它由 argcomplete 的 shell 激活脚本自动处理。

## 环境变量速查表

| 变量名 | 类型 | 核心作用 | 默认值 |
|--------|------|---------|--------|
| `JUPYTER_CONFIG_DIR` | 路径 | 配置目录 | `~/.jupyter` |
| `JUPYTER_DATA_DIR` | 路径 | 数据目录 | 平台相关 |
| `JUPYTER_RUNTIME_DIR` | 路径 | 运行时目录 | `{data_dir}/runtime` |
| `JUPYTER_PATH` | 路径列表 | 附加数据搜索路径 | 空 |
| `JUPYTER_CONFIG_PATH` | 路径列表 | 附加配置搜索路径 | 空 |
| `JUPYTER_NO_CONFIG` | 布尔 | 临时空配置模式 | False |
| `JUPYTER_PLATFORM_DIRS` | 布尔 | 使用 platformdirs 标准路径 | False |
| `JUPYTER_PREFER_ENV_PATH` | 布尔 | 环境目录优先 | 自动检测 |
| `JUPYTER_USE_PROGRAMDATA` | 布尔 | Windows 系统路径 | False |
| `JUPYTER_ALLOW_INSECURE_WRITES` | 布尔 | 跳过权限检查 | False |
| `IPYTHONDIR` | 路径 | IPython 目录 | `~/.ipython` |
| `_ARGCOMPLETE` | 标记 | Tab 补全 | 未设置 |

## 典型使用场景

### 多环境隔离

```bash
# 项目 A 使用独立配置
export JUPYTER_CONFIG_DIR="$PROJECT_A/.jupyter"
export JUPYTER_DATA_DIR="$PROJECT_A/.jupyter-data"
jupyter lab

# 项目 B 使用不同配置
export JUPYTER_CONFIG_DIR="$PROJECT_B/.jupyter"
export JUPYTER_DATA_DIR="$PROJECT_B/.jupyter-data"
jupyter notebook
```

### CI/测试环境

```bash
# 在 CI 中使用干净环境，避免用户配置干扰
export JUPYTER_NO_CONFIG=1
python -m pytest
```

### 虚拟环境自动隔离

当检测到虚拟环境或非 base conda 环境时，`JUPYTER_PREFER_ENV_PATH` 默认为 `True`，环境内的包和配置优先于用户目录，实现自动隔离。用户无需手动设置。

---

**下一步阅读：**
- [路径定制与环境变量示例](../examples/03-path-customization.md) — 通过环境变量定制路径的实战示例
- [源码信源索引](../references/index.md) — 直接查阅源码信源
