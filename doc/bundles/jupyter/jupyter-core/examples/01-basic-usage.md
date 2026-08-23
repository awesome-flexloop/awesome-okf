---
okf_version: "0.2"
type: example
title: "基础使用示例"
description: "通过可运行的代码示例，学习查询 Jupyter 路径、安全写入文件、收集环境诊断信息和发现可用子命令。"
tags: [jupyter, core, example, basic, paths, secure-write, troubleshoot]
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
  - id: troubleshoot-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/troubleshoot.py"
    title: "jupyter_core/troubleshoot.py"
---

# 基础使用示例

本示例展示 jupyter_core 最常用的 API 和操作模式。

## 示例 1：查询 Jupyter 路径

使用 `jupyter_core.paths` 模块查询各类目录位置和搜索路径。

```python
"""查询 Jupyter 各类目录和搜索路径"""

from jupyter_core.paths import (
    jupyter_config_dir,
    jupyter_data_dir,
    jupyter_runtime_dir,
    jupyter_path,
    jupyter_config_path,
)

# --- 单例目录 ---
print("=" * 50)
print("Jupyter 单例目录")
print("=" * 50)
print(f"配置目录:  {jupyter_config_dir()}")
print(f"数据目录:  {jupyter_data_dir()}")
print(f"运行时目录: {jupyter_runtime_dir()}")

# --- 配置搜索路径 ---
print("\n" + "=" * 50)
print("配置搜索路径（按优先级排列）")
print("=" * 50)
for idx, path in enumerate(jupyter_config_path(), 1):
    print(f"  {idx}. {path}")

# --- 数据搜索路径 ---
print("\n" + "=" * 50)
print("数据搜索路径（按优先级排列）")
print("=" * 50)
for idx, path in enumerate(jupyter_path(), 1):
    print(f"  {idx}. {path}")

# --- 子目录搜索 ---
print("\n" + "=" * 50)
print("内核（kernels）搜索路径")
print("=" * 50)
for idx, path in enumerate(jupyter_path("kernels"), 1):
    print(f"  {idx}. {path}")
```

## 示例 2：安全写入文件

使用 `secure_write()` 上下文管理器原子性地写入文件，并自动设置严格的文件权限（0o600），适用于写入内核连接文件、密钥等敏感信息。

```python
"""使用 secure_write 安全写入文件"""

import json
import os
from pathlib import Path

from jupyter_core.paths import jupyter_runtime_dir, secure_write

# 构造一个模拟的内核连接信息
kernel_connection_info = {
    "shell_port": 55555,
    "iopub_port": 55556,
    "stdin_port": 55557,
    "control_port": 55558,
    "hb_port": 55559,
    "ip": "127.0.0.1",
    "key": "a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "transport": "tcp",
    "signature_scheme": "hmac-sha256",
    "kernel_name": "python3",
}

# 写入运行时目录
runtime_dir = jupyter_runtime_dir()
conn_file = str(Path(runtime_dir) / "kernel-example.json")

print(f"写入内核连接文件到: {conn_file}")

# secure_write 会：
# 1. 原子写入（先写临时文件，完成后替换）
# 2. 设置权限为 0o600（仅所有者可读写）
# 3. Windows 下通过 DACL 限制访问
with secure_write(conn_file) as f:
    json.dump(kernel_connection_info, f, indent=2)

# 验证文件权限（Unix 系统）
if os.name != "nt":
    import stat
    file_mode = stat.S_IMODE(os.stat(conn_file).st_mode)
    print(f"文件权限: {oct(file_mode)}")
    assert file_mode == 0o600, f"期望 0o600，实际 {oct(file_mode)}"
    print("✓ 文件权限正确（0o600）")

# 验证文件内容
with open(conn_file, encoding="utf-8") as f:
    loaded = json.load(f)
    assert loaded["shell_port"] == 55555
    print("✓ 文件内容正确")

# 清理
os.unlink(conn_file)
print("✓ 清理完成")
```

## 示例 3：运行环境诊断

使用 `get_data()` 和 `subs()` 收集环境诊断信息。这些函数设计为容错的，即使某些外部命令不可用也不会崩溃。

```python
"""收集并格式化环境诊断信息"""

import sys

from jupyter_core.troubleshoot import get_data, subs

# --- 获取完整环境数据 ---
env_data = get_data()

print("=" * 50)
print("Jupyter 环境诊断信息")
print("=" * 50)

# 基本信息
print(f"\nPython 可执行文件: {env_data['sys_exe']}")
print(f"Python 版本:")
for line in env_data["sys_version"].split("\n"):
    print(f"  {line}")
print(f"平台: {env_data['platform']}")

# PATH 中的关键目录
print(f"\nPATH 中包含 'jupyter' 的目录:")
if env_data["path"]:
    for directory in env_data["path"].split(os.pathsep):
        if "jupyter" in directory.lower() or "python" in directory.lower():
            print(f"  {directory}")

# sys.path 中的 site-packages
print(f"\nPython 搜索路径中的 site-packages:")
for directory in env_data["sys_path"]:
    if "site-packages" in directory:
        print(f"  {directory}")

# jupyter 命令位置
if env_data["which"]:
    print(f"\nwhich -a jupyter:")
    for line in env_data["which"].split("\n"):
        print(f"  {line}")
elif env_data["where"]:
    print(f"\nwhere jupyter:")
    for line in env_data["where"].split("\n"):
        print(f"  {line}")

# --- 使用 subs() 执行其他外部命令 ---
print("\n" + "=" * 50)
print("额外诊断信息")
print("=" * 50)

# 检查 Python 版本
python_version = subs([sys.executable, "--version"])
if python_version:
    print(f"Python 版本: {python_version}")

# 检查 pip 版本
pip_version = subs([sys.executable, "-m", "pip", "--version"])
if pip_version:
    print(f"pip 版本: {pip_version}")

# 检查是否安装了 jupyter_core
pip_show = subs([sys.executable, "-m", "pip", "show", "jupyter_core"])
if pip_show:
    print("\njupyter_core 包信息:")
    for line in pip_show.split("\n"):
        print(f"  {line}")
```

注意：上面代码中需要导入 `os` 模块：

```python
import os
```

（在实际运行时，请将两个代码块合并，在文件顶部导入 `os`。）

## 示例 4：发现可用子命令

编程式调用 `list_subcommands()` 发现当前环境中所有可用的 `jupyter-*` 子命令。

```python
"""发现当前环境中所有可用的 jupyter 子命令"""

from jupyter_core.command import list_subcommands

# 获取所有可用子命令
subcommands = list_subcommands()

print("=" * 50)
print(f"发现 {len(subcommands)} 个可用 jupyter 子命令:")
print("=" * 50)

for cmd in sorted(subcommands):
    print(f"  jupyter {cmd}")

# 检查特定子命令是否可用
wanted = ["notebook", "lab", "server", "kernelspec", "migrate", "troubleshoot"]
print("\n常用子命令可用性检查:")
for cmd in wanted:
    status = "✓ 可用" if cmd in subcommands else "✗ 未安装"
    print(f"  jupyter {cmd:15s} -> {status}")
```

---

**下一步阅读：**
- [自定义 JupyterApp 应用](02-custom-app.md) — 构建自己的 Jupyter 应用
- [路径定制与环境变量](03-path-customization.md) — 通过环境变量自定义路径行为
- [快速上手](../concepts/01-getting-started.md) — 回到概念文档复习基础
