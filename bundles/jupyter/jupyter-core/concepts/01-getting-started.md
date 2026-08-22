---
okf_version: "0.2"
type: concept
title: "5分钟快速上手"
description: "安装 jupyter_core，掌握路径 API、命令行用法、环境诊断与配置迁移的基本操作。"
tags: [jupyter, core, getting-started, installation, cli]
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
  - id: migrate-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/migrate.py"
    title: "jupyter_core/migrate.py"
---

# 5分钟快速上手

## 安装

使用 pip 安装：

```bash
pip install jupyter_core
```

使用 conda 安装：

```bash
conda install jupyter_core
```

安装完成后，验证版本：

```bash
jupyter --version
```

## 路径 API 使用示例

jupyter_core 最常用的 API 集中在 `jupyter_core.paths` 模块，用于定位 Jupyter 的各类目录。

```python
from jupyter_core.paths import (
    jupyter_config_dir,
    jupyter_data_dir,
    jupyter_runtime_dir,
    jupyter_path,
    jupyter_config_path,
)

# 单例目录：返回当前用户的配置/数据/运行时目录
print("配置目录:", jupyter_config_dir())      # 例如 ~/.jupyter
print("数据目录:", jupyter_data_dir())        # 例如 ~/.local/share/jupyter (Linux)
print("运行时目录:", jupyter_runtime_dir())   # 例如 ~/.local/share/jupyter/runtime

# 搜索路径：返回按优先级排列的目录列表
print("配置搜索路径:")
for p in jupyter_config_path():
    print(" ", p)

print("数据搜索路径:")
for p in jupyter_path():
    print(" ", p)

# 也可以搜索子目录，例如查找所有 kernels 目录
print("内核搜索路径:")
for p in jupyter_path("kernels"):
    print(" ", p)
```

## jupyter 命令行用法

`jupyter` 命令提供了一系列选项来查询路径和版本信息：

```bash
# 查看版本（同时显示已安装的 Jupyter 相关包版本）
jupyter --version

# 查看所有路径（config/data/runtime）
jupyter --paths

# 以 JSON 格式输出路径（便于脚本解析）
jupyter --paths --json

# 单独查看各类目录
jupyter --config-dir
jupyter --data-dir
jupyter --runtime-dir

# 查看调试信息（显示环境变量对路径的影响）
jupyter --paths --debug

# 调度子命令（安装其他 Jupyter 包后自动可用）
jupyter notebook   # 需要安装 notebook 包
jupyter lab        # 需要安装 jupyterlab 包
```

## 环境诊断

当遇到安装或路径问题时，可以使用 `jupyter-troubleshoot` 收集诊断信息：

```bash
jupyter-troubleshoot
```

也可以在 Python 中编程式收集环境信息：

```python
from jupyter_core.troubleshoot import get_data, subs

# 获取完整的环境数据字典
env_data = get_data()
print("Python 可执行文件:", env_data["sys_exe"])
print("Python 版本:", env_data["sys_version"])
print("平台:", env_data["platform"])
print("PATH:", env_data["path"])

# 执行外部命令并获取输出（容错：失败返回 None）
jupyter_path = subs(["which", "-a", "jupyter"])  # Unix
# jupyter_path = subs(["where", "jupyter"])      # Windows
if jupyter_path:
    print("jupyter 位置:", jupyter_path)
```

## 配置文件

使用 `JupyterApp` 基类可以生成默认配置文件：

```python
from jupyter_core.application import JupyterApp

# 创建一个应用实例并生成默认配置
app = JupyterApp()
app.config_file_name = "myapp_config"
app.write_default_config()
# 默认写入到 jupyter_config_dir()/myapp_config.py
```

也可以通过命令行生成配置：

```bash
# 对于继承 JupyterApp 的应用，使用 --generate-config
# 例如（如果有自定义应用）：
# python -m myapp --generate-config
```

## 迁移旧配置

如果你是从 IPython 3.x 升级，可以使用 `jupyter-migrate` 将旧配置迁移到 Jupyter 目录结构：

```bash
jupyter-migrate
```

迁移操作是**复制**而非移动，不会删除原有文件。如果目标位置已有文件则跳过，保证幂等安全。迁移完成后会在配置目录写入 `migrated` 标记文件，避免重复执行。

在 Python 中也可以编程式触发迁移：

```python
from jupyter_core.migrate import migrate

# 执行迁移，返回是否有文件被迁移
was_migrated = migrate()
if was_migrated:
    print("配置已迁移")
else:
    print("无需迁移")
```

---

**下一步阅读：**
- [架构总览](02-architecture-overview.md) — 理解 jupyter_core 的分层设计
- [路径系统详解](03-path-system.md) — 深入跨平台路径机制与搜索优先级
- [命令行调度器](04-command-dispatcher.md) — 了解 jupyter 命令如何发现和调度子命令
