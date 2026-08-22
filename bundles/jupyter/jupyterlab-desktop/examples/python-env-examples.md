---
type: Example
title: Python 环境配置示例
description: 在 JupyterLab Desktop 中配置和管理 Python 环境的实际操作示例，包括捆绑环境使用、Conda 环境集成、venv 配置、环境切换
tags: [python-environment, conda, venv, configuration, examples]
prerequisites:
  - /concepts/05-python-env-management.md
  - /concepts/06-settings-config.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: env-source
    resource: /references/env-source.md
    title: Python环境工具源码信源
  - id: registry-source
    resource: /references/registry-source.md
    title: 环境注册表源码信源
---

# Python 环境配置示例

## 使用捆绑环境（开箱即用）

安装 JupyterLab Desktop 后，首次启动即可使用内置的捆绑 Python 环境，无需额外安装：

1. 启动 JupyterLab Desktop
2. 欢迎页中点击"Start a new session"
3. 自动使用捆绑环境启动 JupyterLab

捆绑环境包含 JupyterLab、Python kernel 和常用包。

## 配置现有 Conda 环境

### 方式1：通过 GUI 设置

1. 打开 JupyterLab Desktop
2. 点击标题栏的环境选择器
3. 选择"Select Python path"
4. 浏览到 Conda 环境的 Python 可执行文件：
   - Windows: `C:\Users\you\miniconda3\envs\myenv\python.exe`
   - macOS: `/Users/you/miniconda3/envs/myenv/bin/python`
   - Linux: `/home/you/miniconda3/envs/myenv/bin/python`
5. 确认选择，环境将被验证并设为默认

### 方式2：通过 CLI 设置

```bash
# 设置默认 Python 路径
jlab config set pythonPath ~/miniconda3/envs/myenv/bin/python

# 或使用 env 子命令
jlab env set-default-python-path ~/miniconda3/envs/myenv/bin/python
```

### 设置 Conda 路径

如果自动发现失败，手动设置 Conda 路径：

```bash
jlab env set-conda-path ~/miniconda3/bin/conda
```

## 配置 venv 虚拟环境

### 创建并使用 venv

```bash
# 1. 创建 venv 环境
python3 -m venv ~/venvs/myproject

# 2. 安装 jupyterlab
~/venvs/myproject/bin/pip install jupyterlab

# 3. 在 JupyterLab Desktop 中使用
jlab --python-path ~/venvs/myproject/bin/python
```

### 为项目设置 venv（工作区设置）

```bash
cd ~/projects/myproject

# 在项目目录创建 venv
python3 -m venv .venv
.venv/bin/pip install jupyterlab numpy pandas

# 设置工作区 Python 路径
jlab config set pythonPath .venv/bin/python --project

# 启动时自动使用项目的 venv
jlab .
```

这会在 `~/projects/myproject/.jupyter/desktop-settings.json` 中创建配置。

## 创建新环境（通过 CLI）

### 创建 Conda 环境

```bash
# 创建名为 "datascience" 的 conda 环境，包含 jupyterlab
jlab env create --name datascience -c conda-forge

# 创建并安装额外包（创建后手动 pip/conda install）
jlab env create --name minimal --add-jupyterlab-package=false
conda activate minimal
conda install numpy pandas
```

### 创建 venv 环境

```bash
jlab env create --name myvenv --env-type venv
```

## 切换 Python 环境

### GUI 方式

1. 在 JupyterLab 窗口中，点击标题栏的环境选择器
2. 从下拉列表中选择已发现的环境
3. 或选择"Select Python path"浏览到其他 Python
4. 环境切换会重启 Jupyter 服务器

### 每个窗口独立环境

可以同时打开多个窗口，每个窗口使用不同的 Python 环境：

1. 打开窗口1，使用环境A工作在项目A
2. 打开窗口2（File → New Window），切换到环境B工作在项目B
3. 两个窗口互不干扰，各自有独立的 Jupyter Server

## 验证环境有效性

### 路径验证

```bash
# 验证 Python 路径是否有效
# （通过 IPC 或在设置对话框中自动验证）
```

环境验证检查：
1. Python 可执行文件存在
2. 可以执行 `python --version`
3. jupyterlab 版本 >= 3.0.0

### 环境不满足要求时

如果环境缺少 jupyterlab 或版本过低，错误日志中会显示安装命令：

```
Required Python packages not found in the environment.
You can install missing packages using:
'conda install -c conda-forge -y "jupyterlab>=3.0.0"'
```

## 常见 Conda Channels 配置

```bash
# 使用 conda-forge（推荐）
jlab env set-conda-channels conda-forge

# 使用多个 channels
jlab env set-conda-channels conda-forge defaults bioconda
```

## 工作区设置文件示例

`~/projects/myproject/.jupyter/desktop-settings.json`：

```json
{
  "pythonPath": "/home/user/venvs/myproject/bin/python",
  "serverArgs": "--ServerApp.root_dir=/data",
  "serverEnvVars": {
    "MY_VAR": "my_value"
  }
}
```

这个文件确保在该目录启动 JupyterLab Desktop 时自动使用指定配置。

## 相关概念

- [Python 环境管理](/concepts/05-python-env-management.md) — 环境发现、验证、创建与激活的完整机制
- [设置与配置系统](/concepts/06-settings-config.md) — 全局/项目级配置层级与 desktop-settings.json 持久化
- [CLI 命令系统](/concepts/07-cli-system.md) — jlab env/config 子命令的完整参数与用法参考
- [Jupyter 服务器管理](/concepts/04-server-management.md) — 环境切换时服务器重启与会话管理机制
