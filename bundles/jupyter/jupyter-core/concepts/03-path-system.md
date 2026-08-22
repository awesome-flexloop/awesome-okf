---
okf_version: "0.2"
type: concept
title: "路径系统详解"
description: "深入理解 jupyter_core 的三类核心目录、跨平台默认位置、四级搜索优先级、原子写入机制与环境变量。"
tags: [jupyter, core, paths, platformdirs, secure-write, cross-platform]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paths-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/paths.py"
    title: "jupyter_core/paths.py"
---

# 路径系统详解

路径系统是 jupyter_core 最基础也是最核心的子系统。它负责在不同操作系统上正确定位 Jupyter 的配置文件、数据文件和运行时文件，并提供安全的文件写入机制。

## 三类核心目录

jupyter_core 管理三类目录，分别承担不同用途：

| 目录类型 | 获取函数 | 用途 | 生命周期 |
|---------|---------|------|---------|
| **配置目录** | `jupyter_config_dir()` | 存放 `.py`/`.json` 配置文件 | 持久化 |
| **数据目录** | `jupyter_data_dir()` | 存放内核规格、扩展、nbextensions 等非 transient 数据 | 持久化 |
| **运行时目录** | `jupyter_runtime_dir()` | 存放内核连接文件、PID 文件等 transient 文件 | 临时，可删除 |

### 跨平台默认位置（传统模式）

| 平台 | 配置目录 | 数据目录 | 运行时目录 |
|------|---------|---------|-----------|
| **Linux** | `~/.jupyter` | `~/.local/share/jupyter` | `~/.local/share/jupyter/runtime` |
| **macOS** | `~/.jupyter` | `~/Library/Jupyter` | `~/Library/Jupyter/runtime` |
| **Windows** | `%APPDATA%\jupyter`（通常为 `%USERPROFILE%\AppData\Roaming\jupyter`） | 同配置目录下的 `data` 子目录 | 数据目录下的 `runtime` 子目录 |

> **注意**：macOS 上的 Apple Silicon Homebrew（`/opt/homebrew`）是一个特例，此时使用小写目录名 `jupyter` 而非大写 `Jupyter`。

### 使用 platformdirs 标准路径

设置环境变量 `JUPYTER_PLATFORM_DIRS=1` 后，将使用 `platformdirs` 库提供的平台标准路径，这更符合各操作系统的目录规范（如 XDG、AppData 等）。

```python
import os
os.environ["JUPYTER_PLATFORM_DIRS"] = "1"

from jupyter_core.paths import jupyter_config_dir, jupyter_data_dir
print(jupyter_config_dir())  # Linux: ~/.config/jupyter (XDG_CONFIG_HOME)
print(jupyter_data_dir())    # Linux: ~/.local/share/jupyter (XDG_DATA_HOME)
```

## 四级搜索优先级

`jupyter_path()` 和 `jupyter_config_path()` 返回目录搜索列表，按优先级从高到低排列。优先级由四级路径源决定：

```
优先级高 ───────────────────────────────────────────── 优先级低

┌────────────┐  ┌──────────┐  ┌────────────┐  ┌────────────┐
│ 环境变量    │→│ 用户目录  │→│ 环境目录    │→│ 系统目录    │
│ JUPYTER_   │  │ ~/.jupyter│  │ {sys.prefix}│  │/usr/local/ │
│ PATH /     │  │ ~/.local/ │  │ /share/jupyter│ │share/jupyter│
│ CONFIG_PATH│  │ share/... │  │ /etc/jupyter │  │/etc/jupyter │
└────────────┘  └──────────┘  └────────────┘  └────────────┘
```

### 用户目录 vs 环境目录的顺序

用户目录和环境目录（`sys.prefix` 下的路径）的顺序由 `prefer_environment_over_user()` 决定：

- **虚拟环境中**（`sys.prefix != sys.base_prefix` 且用户拥有该 prefix）：环境目录优先
- **非 base 的 conda 环境中**：环境目录优先
- **设置了 `JUPYTER_PREFER_ENV_PATH` 环境变量**：按其值决定
- **其他情况**：用户目录优先

这意味着在虚拟环境或 conda 环境中安装 Jupyter 包时，环境内的配置和数据会优先于用户目录，实现环境隔离。

### jupyter_path() 返回值示例

```python
from jupyter_core.paths import jupyter_path, jupyter_config_path

# 数据搜索路径（按优先级排列）
print("数据搜索路径:")
for p in jupyter_path():
    print(f"  {p}")
# 可能的输出（非虚拟环境）：
#   ~/.local/share/jupyter          ← 用户级
#   ~/.local/share/jupyter (site)   ← Python user site
#   {sys.prefix}/share/jupyter      ← 环境级
#   /usr/local/share/jupyter        ← 系统级
#   /usr/share/jupyter              ← 系统级

# 配置搜索路径
print("\n配置搜索路径:")
for p in jupyter_config_path():
    print(f"  {p}")
```

## secure_write 原子写入机制

`secure_write()` 是一个上下文管理器，用于安全地写入敏感文件（如内核连接信息、cookie secret 等），保证写入的原子性和权限安全。

### 核心机制

```
┌─────────────────────────────────────────────────┐
│              secure_write(fname)                │
│                                                 │
│  1. 删除已存在的目标文件（如果存在）             │
│  2. 创建文件，权限设为 0o0600（仅所有者可读写） │
│  3. [Windows] 设置 DACL 限制访问                │
│  4. 验证文件权限是否正确（非 Windows）           │
│  5. yield 文件句柄供写入                        │
│  6. 关闭文件（完成原子写入）                    │
└─────────────────────────────────────────────────┘
```

关键特性：

- **原子写入**：使用 `os.open` + `O_TRUNC` 标志，确保写入过程中文件要么是完整的旧内容，要么是完整的新内容，不会出现半写状态
- **权限控制**：Unix 下通过 `os.open` 的 mode 参数设置 `0o600` 权限；Windows 下通过 `win32_restrict_file_to_user()` 设置 DACL（优先使用 pywin32，回退到 ctypes 直接调用 Win32 API）
- **权限验证**：非 Windows 平台写入前会验证文件权限确实为 `0o600`，否则抛出 `RuntimeError`
- **不安全写入**：设置 `JUPYTER_ALLOW_INSECURE_WRITES=1` 可以跳过权限检查（适用于 CIFS 等不支持 POSIX 权限的文件系统），但会发出警告

使用示例：

```python
from jupyter_core.paths import secure_write

# 安全写入内核连接文件
with secure_write("/path/to/kernel-connection.json") as f:
    f.write('{"shell_port": 12345, "iopub_port": 12346}')
```

## is_hidden 跨平台隐藏文件检测

`is_hidden(abs_path, abs_root)` 检测文件或其路径中是否包含隐藏目录，用于安全检查。

检测规则：
- **Unix**：文件名以 `.` 开头，或 BSD `UF_HIDDEN` 标志位被设置
- **Windows**：文件名以 `.` 开头，或 `FILE_ATTRIBUTE_HIDDEN` 属性被设置
- 向上遍历目录直到 `abs_root`，检查路径中每一级是否隐藏
- 如果 `abs_path == abs_root`，根目录本身永远不被视为隐藏

```python
from jupyter_core.paths import is_hidden

# 检查文件是否在隐藏目录中
is_hidden("/home/user/.jupyter/config.py", "/home/user")  # True
is_hidden("/home/user/jupyter/config.py", "/home/user")    # False
```

## 环境变量完整列表

| 环境变量 | 类型 | 作用 | 默认值 |
|---------|------|------|--------|
| `JUPYTER_CONFIG_DIR` | 路径 | 覆盖配置目录位置 | `~/.jupyter`（或 platformdirs 路径） |
| `JUPYTER_DATA_DIR` | 路径 | 覆盖数据目录位置 | 平台相关默认值 |
| `JUPYTER_RUNTIME_DIR` | 路径 | 覆盖运行时目录位置 | `{data_dir}/runtime` |
| `JUPYTER_PATH` | 路径列表（`os.pathsep` 分隔） | 附加到数据搜索路径最前面 | 空 |
| `JUPYTER_CONFIG_PATH` | 路径列表 | 附加到配置搜索路径最前面 | 空 |
| `JUPYTER_NO_CONFIG` | 布尔 | 使用临时空配置目录（隔离模式） | 未设置 |
| `JUPYTER_PLATFORM_DIRS` | 布尔 | 使用 platformdirs 标准路径 | 未设置（使用传统路径） |
| `JUPYTER_PREFER_ENV_PATH` | 布尔 | 环境目录优先于用户目录 | 自动检测（虚拟环境/conda） |
| `JUPYTER_USE_PROGRAMDATA` | 布尔 | Windows 下使用 `%PROGRAMDATA%` 作为系统路径 | 未设置 |
| `JUPYTER_ALLOW_INSECURE_WRITES` | 布尔 | 允许跳过文件权限检查 | 未设置 |

布尔类型环境变量使用 `envset()` 函数解析，`no`/`n`/`false`/`off`/`0`/`0.0`（不区分大小写）视为 `False`，其他非空值视为 `True`。

### Windows 系统路径的特殊处理

出于安全考虑，Windows 上默认不使用 `%PROGRAMDATA%` 作为系统级 Jupyter 路径（因为该目录对所有用户可写，存在安全风险）。只有显式设置 `JUPYTER_USE_PROGRAMDATA=1` 才会启用。默认情况下，Windows 系统路径使用 `{sys.prefix}/share/jupyter`。

---

**下一步阅读：**
- [命令行调度器](04-command-dispatcher.md) — 了解 jupyter CLI 如何基于 PATH 发现子命令
- [环境变量参考](08-environment-variables.md) — 所有环境变量的详细说明与使用示例
