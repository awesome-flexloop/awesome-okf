---
okf_version: "0.2"
type: reference
title: "环境诊断工具源码（troubleshoot.py）"
description: "jupyter_core/troubleshoot.py 中环境信息收集的简洁实现：外部命令调用、环境数据字典和主输出函数"
tags: [troubleshoot, diagnostic, debug, environment, jupyter-troubleshoot, subs, get_data]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: troubleshoot-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/troubleshoot.py"
    title: "jupyter_core/troubleshoot.py"
---

# 环境诊断工具源码（troubleshoot.py）

本信源登记 `jupyter_core/troubleshoot.py`（约111行）的所有函数与行为细节。troubleshoot.py 是一个简洁的环境诊断工具，仅包含3个函数，通过调用外部命令收集系统信息用于故障排查。

## 公开函数

### subs(cmd: list[str] | str) -> str | None

运行外部命令并捕获 stdout 输出：

1. 使用 `subprocess.check_output(cmd)` 执行命令
2. stdout 解码为 UTF-8（`decode("utf-8", "replace")`）并 strip 空白
3. 命令不存在或执行失败（OSError/CalledProcessError）时返回 `None`
4. 注意：`cmd` 参数通过 `S603 noqa` 标记（bandit 安全检查豁免），因命令列表是硬编码的

### get_data() -> dict[str, Any]

收集环境信息字典，返回以下键值：

| 键 | 类型 | 内容 |
|----|------|------|
| `path` | str | `os.environ["PATH"]`（系统PATH环境变量） |
| `sys_path` | list[str] | `sys.path`（Python模块搜索路径） |
| `sys_exe` | str | `sys.executable`（Python解释器路径） |
| `sys_version` | str | `sys.version`（Python版本信息） |
| `platform` | str | `platform.platform()`（操作系统平台描述） |
| `which` | str | None(Linux/macOS上运行`which -a jupyter`的结果)或None(Windows) |
| `where` | str | None(Windows上运行`where jupyter`的结果)或None(Linux/macOS) |
| `pip` | str | `{sys.executable} -m pip list` 输出（已安装包列表） |
| `conda` | str | `conda list` 输出（若conda可用）或None |
| `conda-env` | str | `conda env export` 输出（若conda可用）或None |

[F-220]

### main() -> None

命令行诊断入口，按以下顺序打印信息：

1. **argcomplete 早退**：若设置了 `_ARGCOMPLETE` 环境变量（tab补全模式），直接返回（避免缓慢的外部命令调用）
2. 调用 `get_data()` 获取环境数据
3. **$PATH**：逐目录打印 PATH 中的每个路径
4. **sys.path**：打印 Python 模块搜索路径
5. **sys.executable**：打印 Python 解释器路径
6. **sys.version**：打印 Python 版本（多行时逐行打印）
7. **platform.platform()**：打印操作系统平台描述
8. **which -a jupyter**（Linux/macOS）：打印所有 jupyter 命令位置
9. **where jupyter**（Windows）：打印 jupyter 命令位置
10. **pip list**：打印已安装的 Python 包列表
11. **conda list**（若可用）：打印 conda 包列表
12. **conda env export**（若可用）：打印 conda 环境导出

[F-221]

## 入口脚本

### scripts/jupyter-troubleshoot

```python
#!/usr/bin/env python
from jupyter_core.troubleshoot import main

if __name__ == "__main__":
    main()
```

## 设计特点

1. **简洁性**：整个模块仅111行，3个函数，无复杂逻辑
2. **外部命令优先**：通过 `subprocess.check_output` 调用 `pip list`、`conda list`、`which/where` 等外部命令获取信息，而非通过 Python API（确保获取的是实际执行环境的信息）
3. **容错处理**：外部命令失败时返回 None，不中断整体输出
4. **argcomplete 优化**：tab补全时提前退出，避免用户体验延迟
5. **平台感知**：Windows 使用 `where`，Unix 使用 `which -a`
6. **无包版本查询API**：不提供编程式的包版本查询函数（`pkg_info`、`package_table` 等不存在于此版本），包版本信息通过 `pip list` 外部命令获取

[F-222]
