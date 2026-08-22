---
okf_version: "0.2"
type: reference
title: "路径管理源码（paths.py）"
description: "jupyter_core/paths.py 中跨平台路径发现、四级搜索层级、安全写入和权限控制的完整API"
tags: [paths, cross-platform, config, data, runtime, secure-write, hidden-files, platformdirs]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paths-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/paths.py"
    title: "jupyter_core/paths.py"
---

# 路径管理源码（paths.py）

本信源登记 `jupyter_core/paths.py`（约1114行）的核心函数与行为细节。paths.py 是 jupyter_core 最核心的模块，提供 Jupyter 生态中配置、数据、运行时文件的跨平台路径发现与管理能力。

## 核心路径函数

### jupyter_config_dir() -> str

返回 Jupyter 配置目录，优先级：
1. `JUPYTER_CONFIG_DIR` 环境变量
2. 平台用户配置目录（通过 `platformdirs.user_config_dir("jupyter")`）
   - Linux/macOS: `~/.jupyter/` 或 `$XDG_CONFIG_HOME/jupyter/`
   - Windows: `%APPDATA%\jupyter\`

### jupyter_data_dir() -> str

返回 Jupyter 用户数据目录，优先级：
1. `JUPYTER_DATA_DIR` 环境变量
2. 平台用户数据目录（通过 `platformdirs.user_data_dir("jupyter")`）
   - Linux: `~/.local/share/jupyter/` 或 `$XDG_DATA_HOME/jupyter/`
   - macOS: `~/Library/Jupyter/`
   - Windows: `%APPDATA%\jupyter\`

### jupyter_runtime_dir() -> str

返回 Jupyter 运行时文件目录（内核连接文件、运行状态等）：
1. `JUPYTER_RUNTIME_DIR` 环境变量
2. 默认：`{data_dir}/runtime/`
3. 目录权限设为 `0o700`（仅用户可读写执行）

### jupyter_path() -> list[str]

返回 Jupyter 数据搜索路径列表（按优先级排序）：
1. 用户数据目录（`jupyter_data_dir()`）
2. 系统级数据目录（`sys.prefix/share/jupyter/`、`sys.prefix/local/share/jupyter/`）
3. 环境变量 `JUPYTER_PATH`（多个路径以 os.pathsep 分隔）

### jupyter_config_path() -> list[str]

返回 Jupyter 配置搜索路径列表（按优先级排序）：
1. `JUPYTER_CONFIG_PATH` 环境变量路径
2. 用户配置目录（`jupyter_config_dir()`）
3. 系统级配置目录（`sys.prefix/etc/jupyter/`）

## 安全写入与权限控制

### secure_write(fname, binary=False) -> Iterator[file handle]

上下文管理器，原子安全写入文件：
1. 确保目标目录存在
2. 创建临时文件（同目录下，确保跨rename原子性）
3. 设置文件权限为 `0o600`（仅所有者可读写）
4. Windows 上调用 `win32_restrict_file_to_user()` 设置 DACL
5. yield 文件句柄供写入
6. 上下文退出时 `os.replace()` 原子替换目标文件
7. 写入失败时清理临时文件

[F-100]

### win32_restrict_file_to_user(fname) -> None

Windows 平台专属：使用 pywin32 设置文件 DACL，仅允许当前用户访问，模拟 Unix `0o600` 权限。

### is_hidden(file_path, path) -> bool

检测路径是否为隐藏文件/目录：
- Unix：以 `.` 开头
- Windows：检查文件属性中的 `FILE_ATTRIBUTE_HIDDEN` 标志

[F-101]

### prefer_environment_over_user() -> bool

判断是否优先使用环境目录而非用户目录（当 sys.prefix 在 conda/venv 虚拟环境中时返回 True）。

## 环境变量汇总

| 环境变量 | 作用 | 默认值 |
|---------|------|--------|
| `JUPYTER_CONFIG_DIR` | 配置目录路径 | 平台用户配置目录 |
| `JUPYTER_DATA_DIR` | 数据目录路径 | 平台用户数据目录 |
| `JUPYTER_RUNTIME_DIR` | 运行时目录路径 | `{data_dir}/runtime/` |
| `JUPYTER_PATH` | 额外数据搜索路径 | 空 |
| `JUPYTER_CONFIG_PATH` | 额外配置搜索路径 | 空 |
| `JUPYTER_NO_CONFIG` | 跳过用户配置（仅使用sys-prefix） | 未设置 |
| `JUPYTER_PLATFORM_DIRS` | 强制使用platformdirs（不自动回退~/.jupyter） | 未设置 |

[F-102]

## 设计要点

1. **四层搜索**：用户目录 → sys.prefix → 环境变量路径 → 历史兼容路径
2. **安全优先**：runtime 目录和所有写入操作均限制为 `0o700`/`0o600` 权限
3. **跨平台一致**：通过 platformdirs 库抽象平台差异
4. **原子写入**：secure_write 使用临时文件 + os.replace 防止写入中断导致文件损坏
5. **向后兼容**：对旧版 IPython/Jupyter 路径有迁移兼容逻辑
