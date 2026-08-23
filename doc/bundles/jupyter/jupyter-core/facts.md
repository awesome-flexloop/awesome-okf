---
type: Facts
title: jupyter-core 源码事实清单
description: R阶段产出：从零推测事实，每条事实指向具体源码位置
tags:
- facts
- source-code
- evidence
- verification
- jupyter-core
- paths
- configuration
- traitlets
generated:
  by: agent:source-code-to-okf-wiki
  at: '2026-08-22T00:00:00+08:00'
status: stable
stale_after: 2027-08-22
sources:
- ../../../../../external/libs/jupyter/jupyter_core/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter_core/README.md
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/__init__.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/__main__.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/application.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/command.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/migrate.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/paths.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/troubleshoot.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/utils/__init__.py
- ../../../../../external/libs/jupyter/jupyter_core/jupyter_core/version.py
okf_version: '0.2'
---

# Jupyter Core 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 包名 `jupyter_core`，描述 "Jupyter core package. A base package on which Jupyter projects rely."（pyproject.toml L6-7）
- F-002: License 为 BSD-3-Clause，作者 Jupyter Development Team，邮箱 jupyter@googlegroups.org（pyproject.toml L8, L25-27）
- F-003: 版本 `5.9.1`，通过正则 `r"(?P<major>\d+).(?P<minor>\d+).(?P<patch>\d+)(?P<rest>.*)"` 解析为 `version_info` 元组 `(5, 9, 1)`（version.py L10-19）
- F-004: 构建系统使用 `hatchling>=1.4`，build-backend 为 `hatchling.build`（pyproject.toml L1-3）
- F-005: Python 版本要求 `>=3.10`（pyproject.toml L18）
- F-006: 运行时依赖：`platformdirs>=2.5`、`traitlets>=5.3`（pyproject.toml L19-22）
- F-007: 命令行入口：`jupyter = "jupyter_core.command:main"`、`jupyter-migrate = "jupyter_core.migrate:main"`、`jupyter-troubleshoot = "jupyter_core.troubleshoot:main"`（pyproject.toml L56-59）
- F-008: 项目 URLs：Homepage https://jupyter.org、Documentation https://jupyter-core.readthedocs.io/、Source https://github.com/jupyter/jupyter_core、Tracker https://github.com/jupyter/jupyter_core/issues（pyproject.toml L33-37）
- F-009: 包 `__init__.py` 仅从 `.version` 导入 `__version__` 和 `version_info`，无其他导出（__init__.py L1-3）
- F-010: 版本源文件路径配置为 `jupyter_core/version.py`（pyproject.toml L61-62）
- F-011: hatch build 配置强制包含根目录 `./jupyter.py` 到 wheel 包内的 `jupyter.py`（pyproject.toml L64-65）

## 目录结构

- F-020: 包目录 `jupyter_core/` 包含以下顶层模块：`__init__.py`、`__main__.py`、`application.py`、`command.py`、`migrate.py`、`paths.py`、`troubleshoot.py`、`version.py`、`py.typed`
- F-021: 包子目录 `utils/` 包含 `__init__.py`（即 `jupyter_core.utils` 包）
- F-022: `scripts/` 目录包含 shell 脚本：`jupyter`、`jupyter-migrate`
- F-023: `examples/` 目录包含 shell 补全示例：`completions-zsh`、`jupyter-completion.bash`
- F-024: `tests/` 目录包含测试文件：`test_application.py`、`test_command.py`、`test_migrate.py`、`test_paths.py`、`test_troubleshoot.py`、`test_utils.py`
- F-025: 根目录包含 `jupyter.py` 文件（被 hatch force-include 到包内，提供 `jupyter` 命令的 setuptools 兼容 shim）

## 路径系统（paths.py）

- F-030: 常量 `APPNAME` 根据平台取值：Windows 或非 Homebrew macOS 为 `"Jupyter"`（大写），Linux 和 Apple Silicon Homebrew 为 `"jupyter"`（小写）（paths.py L28-32）
- F-031: `_is_apple_silicon_homebrew` 判断条件：`sys.platform == "darwin" and sys.prefix.startswith("/opt/homebrew")`（paths.py L28）
- F-032: 常量 `UF_HIDDEN` 通过 `getattr(stat, "UF_HIDDEN", 32768)` 获取，BSD 隐藏文件标志，默认值 32768（paths.py L36）
- F-033: `pjoin = os.path.join` 为路径拼接快捷别名（paths.py L25）
- F-034: `envset(name, default)` 函数读取布尔环境变量，将 `"no"/"n"/"false"/"off"/"0"/"0.0"`（不区分大小写）视为 False，其他非空值视为 True，未设置时返回 default（paths.py L47-58）
- F-035: `use_platform_dirs()` 返回 `envset("JUPYTER_PLATFORM_DIRS", False)`，控制是否使用 platformdirs 库确定平台标准路径，默认 False（paths.py L61-66）
- F-036: `get_home_dir()` 通过 `Path("~").expanduser().resolve()` 获取用户主目录的真实路径，处理符号链接（paths.py L69-74）
- F-037: `_dtemps` 字典缓存临时目录，`_mkdtemp_once(name)` 为同一 name 在同一进程中复用同一临时目录（paths.py L77, L129-139）
- F-038: `_do_i_own(path)` 检查当前用户是否拥有指定路径：先尝试 `Path.owner() == os.getlogin()`，再尝试 `os.geteuid() == st.st_uid`，都失败则退化为 `os.access(p, os.W_OK)` 写权限检查（paths.py L80-104）
- F-039: `prefer_environment_over_user()` 判断环境级别路径是否优先于用户级别路径：若 `JUPYTER_PREFER_ENV_PATH` 环境变量设置则使用其值；否则若在 venv 中且拥有 sys.prefix 返回 True；若在非 base conda 环境中且拥有 sys.prefix 返回 True；其他情况返回 False（paths.py L107-126）
- F-040: `jupyter_config_dir()` 返回 Jupyter 配置目录优先级：`JUPYTER_NO_CONFIG` 设置时返回临时目录 `_mkdtemp_once("jupyter-clean-cfg")`；`JUPYTER_CONFIG_DIR` 设置时返回其值；`use_platform_dirs()` 为 True 时返回 `platformdirs.user_config_dir(APPNAME, appauthor=False)`；否则返回 `~/.jupyter`（paths.py L142-160）
- F-041: `jupyter_data_dir()` 返回 Jupyter 数据目录优先级：`JUPYTER_DATA_DIR` > platformdirs > 平台默认路径（macOS: `~/Library/Jupyter`，Windows: `%APPDATA%\jupyter`，Linux: `$XDG_DATA_HOME/jupyter` 或 `~/.local/share/jupyter`）（paths.py L163-193）
- F-042: `jupyter_runtime_dir()` 返回运行时目录：`JUPYTER_RUNTIME_DIR` > `jupyter_data_dir()/runtime`（不再使用 XDG_RUNTIME_DIR）（paths.py L196-209）
- F-043: `SYSTEM_JUPYTER_PATH` 在非 platformdirs 模式下：Windows 无 PROGRAMDATA 时为 `[sys.prefix/share/jupyter]`，有 PROGRAMDATA 时为 `[%PROGRAMDATA%/jupyter]`；非 Windows 为 `["/usr/local/share/jupyter", "/usr/share/jupyter"]`；Apple Silicon Homebrew 额外插入 `"/opt/homebrew/share/jupyter"` 到最前（paths.py L228-243）
- F-044: `SYSTEM_JUPYTER_PATH` 在 platformdirs 模式下：Windows 无 PROGRAMDATA 时为 `[sys.prefix/share/jupyter]`，否则为 `platformdirs.site_data_dir(APPNAME, appauthor=False, multipath=True).split(os.pathsep)`（paths.py L220-227）
- F-045: `ENV_JUPYTER_PATH = [str(Path(sys.prefix, "share", "jupyter"))]` 固定为当前 Python 环境的 share/jupyter 目录（paths.py L245）
- F-046: `jupyter_path(*subdirs)` 返回数据文件搜索路径列表，按优先级：`$JUPYTER_PATH` 环境变量（最高）→ 用户目录或环境目录（由 `prefer_environment_over_user()` 决定顺序）→ 系统目录（最后），支持传入 subdirs 自动追加子目录（paths.py L248-333）
- F-047: `ENV_CONFIG_PATH = [str(Path(sys.prefix, "etc", "jupyter"))]`（paths.py L336）
- F-048: `SYSTEM_CONFIG_PATH` 在非 platformdirs 模式下：非 Windows 为 `["/usr/local/etc/jupyter", "/etc/jupyter"]`（Apple Silicon Homebrew 插入 `"/opt/homebrew/etc/jupyter"`）；Windows 有 PROGRAMDATA 时为 `[%PROGRAMDATA%/jupyter]`，否则为 ENV_CONFIG_PATH 副本（paths.py L347-360）
- F-049: `jupyter_config_path()` 返回配置文件搜索路径，逻辑同 `jupyter_path()` 但使用配置目录（jupyter_config_dir + ENV_CONFIG_PATH + SYSTEM_CONFIG_PATH），支持 `JUPYTER_CONFIG_PATH` 和 `JUPYTER_NO_CONFIG`（paths.py L363-429）
- F-050: `exists(path)` 使用 `os.lstat(path)` 替代 `os.path.exists()`，以支持 Windows 容器上的主机映射卷（paths.py L432-440）
- F-051: 平台隐藏文件检测在模块加载时通过 `sys.platform == "win32"` 条件选择：Windows 用 `is_file_hidden_win`，POSIX 用 `is_file_hidden_posix`（paths.py L530-533）
- F-052: `is_file_hidden_win` 判断隐藏：文件名以 `.` 开头或 `stat.FILE_ATTRIBUTE_HIDDEN` 属性置位（paths.py L443-486）
- F-053: `is_file_hidden_posix` 判断隐藏：文件名以 `.` 开头、目录无 R+X 访问权限、或 `st_flags & UF_HIDDEN` 置位（paths.py L489-527）
- F-054: `is_hidden(abs_path, abs_root)` 递归检查路径及其所有父目录是否隐藏：文件名以 `.` 开头或父目录设置 UF_HIDDEN 标志，根目录本身不视为隐藏（paths.py L536-601）
- F-055: `secure_write(fname, binary=False)` 上下文管理器：以最严格权限（`0o0600`）打开文件写入，Windows 上通过 `win32_restrict_file_to_user` 设置 DACL，POSIX 上验证文件 mode 为 `0o0600`，不匹配且未设置 `JUPYTER_ALLOW_INSECURE_WRITES` 时抛出 RuntimeError（paths.py L1048-1099）
- F-056: `win32_restrict_file_to_user(fname)` 优先使用 pywin32（`win32api`/`win32security`/`ntsecuritycon`），ImportError 时降级到 ctypes 直接调用 advapi32/secur32 DLL 设置文件 DACL，仅授予当前用户 R/W/D 和管理员 FULL 权限（paths.py L604-1023）
- F-057: `get_file_mode(fname)` 返回 `stat.S_IMODE(stat().st_mode) & 0o6677`，屏蔽 CIFS 自动设置的执行位和 sticky bit（paths.py L1026-1042）
- F-058: `allow_insecure_writes` 由环境变量 `JUPYTER_ALLOW_INSECURE_WRITES` 控制，值为 `"true"` 或 `"1"` 时为 True（paths.py L1045）
- F-059: Windows 系统路径默认不使用 `%PROGRAMDATA%`，需设置 `JUPYTER_USE_PROGRAMDATA` 环境变量启用（paths.py L213-217）

## 应用基类（application.py）

- F-060: `JupyterApp` 继承自 `traitlets.config.application.Application`，是所有 Jupyter 应用的基类（application.py L70）
- F-061: `JupyterApp.name = "jupyter"`、`description = "A Jupyter Application"`（application.py L73-74）
- F-062: `JupyterApp.aliases` 和 `flags` 在 traitlets Application 基础上扩展 Jupyter 特有选项：`--log-level`、`--config`、`--debug`、`--generate-config`、`-y`（application.py L38-63）
- F-063: `NoStart` 异常类用于表示应用不应启动（application.py L66-67）
- F-064: `JupyterApp._log_level_default()` 返回 `logging.INFO`（application.py L79-80）
- F-065: `JupyterApp.jupyter_path` 为 List(Unicode()) trait，默认值为 `jupyter_path()` 函数返回的路径列表（application.py L82-85）
- F-066: `JupyterApp.config_dir` 为 Unicode trait，默认值为 `jupyter_config_dir()`（application.py L87-90）
- F-067: `JupyterApp.config_file_paths` 属性返回 `jupyter_config_path()` 并将 `self.config_dir` 插入到列表最前（application.py L92-98）
- F-068: `JupyterApp` 导入 `ensure_dir_exists` 和 `ensure_event_loop` 工具函数（application.py L32）
- F-069: `base_aliases` 和 `base_flags` 是模块级字典，先从 traitlets Application 复制默认值再追加 Jupyter 特有选项，兼容 traitlets 5（application.py L38-63）

## 命令调度（command.py）

- F-080: `JupyterParser` 继承 `argparse.ArgumentParser`，重写 `epilog` 属性动态生成子命令列表（command.py L27-41）
- F-081: `JupyterParser.epilog` getter 调用 `list_subcommands()` 获取 PATH 中所有 `jupyter-*` 可执行文件，格式化 "Available subcommands: ..."（command.py L31-37）
- F-082: `JupyterParser.argcomplete()` 尝试导入 `argcomplete` 并启用自动补全，ImportError 时静默跳过（command.py L43-50）
- F-083: `jupyter_parser()` 创建参数解析器，支持互斥参数组：`--version`、`subcommand`（位置参数）、`--config-dir`、`--data-dir`、`--runtime-dir`、`--paths`；以及 `--json`、`--debug` 选项（command.py L53-79）
- F-084: `--version` 标志显示核心 Jupyter 包版本（command.py L60-62）
- F-085: `--paths` 标志显示所有 Jupyter 路径，`--json` 控制 JSON 格式输出（command.py L72-77）
- F-086: 文件首行 `# PYTHON_ARGCOMPLETE_OK` 标记支持 argcomplete（command.py L1）

## 迁移与故障排除（migrate.py / troubleshoot.py）

- F-090: `migrate.py` 提供 `jupyter-migrate` 命令，用于从旧版 Jupyter 路径（~/.jupyter）迁移到 platformdirs 标准路径
- F-091: `troubleshoot.py` 提供 `jupyter-troubleshoot` 命令，输出环境诊断信息
- F-092: `__main__.py` 支持 `python -m jupyter_core` 执行

## 工具模块（utils/）

- F-100: `jupyter_core.utils` 包提供 `ensure_dir_exists`（确保目录存在）和 `ensure_event_loop`（确保 asyncio 事件循环）等工具函数
