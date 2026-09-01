---
type: Concept
title: 目录结构与文件位置
description: Jupyter 三类文件分离（config/data/runtime）、各平台默认路径、环境变量覆盖、搜索路径机制
tags: [jupyter, directories, paths, config, data, runtime, jupyter-path]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T10:35:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# 目录结构与文件位置

Jupyter 将文件严格分为三类：**配置文件（config）**、**数据文件（data）**和**运行时文件（runtime）**，每类有独立的存储位置和搜索路径。理解这三类文件的分离是排查 Jupyter 问题、配置环境和管理扩展的基础。

## 三类文件概述

| 文件类型 | 内容 | 生命周期 | 典型示例 |
|---------|------|---------|---------|
| **Config（配置）** | 配置文件 | 长期持久，手动编辑 | `jupyter_notebook_config.py`、`custom.js` |
| **Data（数据）** | 非临时非配置的数据文件 | 长期持久 | kernelspecs、nbextensions、Voilà 模板 |
| **Runtime（运行时）** | 进程相关的临时文件 | 仅在进程运行期间有效 | 连接文件、PID 文件、日志文件 |

这三类文件的分离原则：

- 配置文件可备份、可版本控制
- 数据文件可由包安装、用户安装
- 运行时文件可安全删除，重启后自动重建

## 配置文件目录

### 默认位置

| 平台 | 默认配置目录 |
|------|------------|
| Linux/FreeBSD | `~/.jupyter/` |
| macOS | `~/.jupyter/` |
| Windows | `%USERPROFILE%\.jupyter\` |

### 环境变量

| 环境变量 | 作用 |
|---------|------|
| `JUPYTER_CONFIG_DIR` | 覆盖默认配置目录 |
| `JUPYTER_CONFIG_PATH` | 追加额外的配置搜索目录（用 `os.pathsep` 分隔：Unix `:`，Windows `;`） |

### 搜索路径优先级

Jupyter 加载配置时按以下顺序搜索，后加载的覆盖先加载的：

```
1. JUPYTER_CONFIG_DIR（用户级，优先级最高）
2. JUPYTER_CONFIG_PATH 中的每个目录
3. {sys.prefix}/etc/jupyter/（环境级，conda/venv）
4. 系统级目录：
   - Unix: /usr/local/etc/jupyter/、/etc/jupyter/
   - Windows: %PROGRAMDATA%\jupyter\
```

这种多层搜索路径设计使得：

- **用户配置**覆盖环境和系统配置
- **conda/venv 环境**可以有独立的 Jupyter 配置
- **系统管理员**可以在 `/etc/jupyter/` 设置全局默认配置

### 查询命令

```bash
# 查看当前配置目录
jupyter --config-dir

# 查看所有搜索路径
jupyter --paths
```

## 数据文件目录

数据文件是 Jupyter 安装和运行过程中产生的非配置、非临时文件，包括：

- **Kernelspecs**（内核规范）：JSON 文件描述内核的启动命令和显示信息
- **NBExtensions**（Notebook 扩展）：前端 JS/CSS 扩展
- **Voilà 模板**等

### 默认位置

| 平台 | 默认数据目录 |
|------|------------|
| Linux | `~/.local/share/jupyter/`（遵循 XDG_DATA_HOME） |
| macOS | `~/Library/Application Support/Jupyter/` |
| Windows | `%APPDATA%\jupyter\` |

### 环境变量

| 环境变量 | 作用 |
|---------|------|
| `JUPYTER_DATA_DIR` | 覆盖用户数据目录 |
| `JUPYTER_PATH` | 追加额外的数据搜索目录（用 `os.pathsep` 分隔） |

`JUPYTER_PATH` 中指定的目录在所有其他数据目录**之前**搜索。

### 搜索路径优先级

```
1. JUPYTER_PATH 中的每个目录
2. JUPYTER_DATA_DIR / 平台默认用户数据目录
3. {sys.prefix}/share/jupyter/（环境级）
4. 系统级目录：
   - Unix: /usr/local/share/jupyter/、/usr/share/jupyter/
   - Windows: %PROGRAMDATA%\jupyter\
```

数据文件搜索机制与 Python 的 `import` 类似：从第一个目录开始查找，找到即停。这意味着用户安装的 kernelspecs 优先级高于系统安装的。

### 子目录约定

每个数据目录下，不同类型的资源放在不同子目录：

| 子目录 | 内容 |
|--------|------|
| `kernels/` | 内核规范（kernelspecs） |
| `nbextensions/` | Notebook 前端扩展 |
| `labextensions/` | JupyterLab 扩展 |
| `voila/templates/` | Voilà 模板 |

例如，查看所有已安装的内核：

```bash
jupyter kernelspec list
```

## 运行时文件目录

运行时文件是仅在特定 Jupyter 进程运行期间有意义的临时文件。

### 默认位置

默认存储在用户数据目录的 `runtime/` 子目录中：

| 平台 | 运行时目录 |
|------|----------|
| Linux | `~/.local/share/jupyter/runtime/` |
| macOS | `~/Library/Application Support/Jupyter/runtime/` |
| Windows | `%APPDATA%\jupyter\runtime\` |

### 环境变量

| 环境变量 | 作用 |
|---------|------|
| `JUPYTER_RUNTIME_DIR` | 覆盖运行时目录 |

### 典型文件

| 文件 | 说明 |
|------|------|
| `kernel-<pid>.json` | 内核连接文件（包含通信端口、签名密钥等） |
| `nbserver-<pid>.json` | Notebook Server 信息文件 |
| `jpserver-<pid>.json` | Jupyter Server 信息文件（v7+） |
| `jupyter-<pid>.log` | 服务器日志文件 |

连接文件（connection file）是 Kernel 启动时生成的 JSON 文件，包含前端连接 Kernel 所需的所有信息：

```json
{
  "shell_port": 56789,
  "iopub_port": 56790,
  "stdin_port": 56791,
  "control_port": 56792,
  "hb_port": 56793,
  "ip": "127.0.0.1",
  "key": "abc123...",
  "transport": "tcp",
  "signature_scheme": "hmac-sha256",
  "kernel_name": "python3"
}
```

前端通过读取这个文件知道连接哪个端口、使用什么密钥签名消息。

```bash
# 连接到已运行的内核
jupyter console --existing

# 或指定连接文件
jupyter console --existing kernel-12345.json
```

## 目录查询总结

```bash
# 分别查询各类目录
jupyter --config-dir     # 配置目录
jupyter --data-dir       # 数据目录
jupyter --runtime-dir    # 运行时目录

# 一次性查看所有目录和搜索路径
jupyter --paths

# JSON 格式（适合脚本解析）
jupyter --paths --json
```

`jupyter --paths` 的输出示例（Linux）：

```
Config:
    /home/user/.jupyter
    /home/user/miniconda3/envs/main/etc/jupyter
    /usr/local/etc/jupyter
    /etc/jupyter
Data:
    /home/user/.local/share/jupyter
    /home/user/miniconda3/envs/main/share/jupyter
    /usr/local/share/jupyter
    /usr/share/jupyter
Runtime:
    /home/user/.local/share/jupyter/runtime
```

## Python API

如果你需要在 Python 代码中查找这些目录，使用 `jupyter_core.paths` 模块：

```python
from jupyter_core.paths import (
    jupyter_config_dir,      # 配置目录
    jupyter_data_dir,        # 数据目录
    jupyter_runtime_dir,     # 运行时目录
    jupyter_config_path,     # 配置搜索路径列表
    jupyter_path,            # 数据搜索路径列表
)

# 用户目录
print(jupyter_config_dir())   # ~/.jupyter
print(jupyter_data_dir())     # ~/.local/share/jupyter
print(jupyter_runtime_dir())  # ~/.local/share/jupyter/runtime

# 搜索路径列表
for p in jupyter_config_path():
    print(p)
```

## 环境变量速查表

| 环境变量 | 影响文件类型 | 作用 |
|---------|------------|------|
| `JUPYTER_CONFIG_DIR` | Config | 用户配置目录 |
| `JUPYTER_CONFIG_PATH` | Config | 追加配置搜索路径 |
| `JUPYTER_DATA_DIR` | Data | 用户数据目录 |
| `JUPYTER_PATH` | Data | 追加数据搜索路径 |
| `JUPYTER_RUNTIME_DIR` | Runtime | 运行时目录 |

## 常见问题排查

### 问题1：安装的内核/扩展找不到

检查 `jupyter --paths` 的数据目录，确认文件放在了搜索路径中的某个目录下。不同 conda 环境的 `{sys.prefix}/share/jupyter/` 不同，在一个环境安装的内核在另一个环境可能看不到。

### 问题2：连接到已有 Kernel 失败

检查运行时目录中的连接文件是否存在，确认 Kernel 进程仍在运行。

### 问题3：自定义配置不生效

1. 检查配置文件拼写（拼写错误静默忽略）
2. 用 `jupyter --config-dir` 确认配置文件放在了正确目录
3. 确认配置类名正确（Notebook v7 用 `ServerApp` 而非 `NotebookApp`）
4. 检查命令行参数是否覆盖了配置文件设置

### 问题4：多环境冲突

如果同时有系统 Python、conda 环境、venv，每个环境有自己的 `{sys.prefix}/etc/jupyter/` 和 `{sys.prefix}/share/jupyter/`。确认激活了正确的环境，以及环境的 bin 目录在 PATH 最前面。

## 相关概念

- [通用配置系统](04-config-system.md) — 配置文件语法、配置类、命令行覆盖
- [jupyter 命令与子命令发现](03-jupyter-command.md) --paths/--config-dir 等命令选项
- [客户端-服务器架构详解](08-client-server.md) — 连接文件在 Kernel 通信中的作用
