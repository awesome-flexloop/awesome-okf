---
type: Example
title: CLI 命令使用示例
description: jlab 命令行工具的常见使用场景示例，包括打开文件/目录、管理环境、配置设置、连接远程服务器
tags: [cli, jlab, command-line, examples, usage]
prerequisites:
  - /concepts/07-cli-system.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cli-source
    resource: /references/cli-source.md
    title: CLI命令源码信源
  - id: main-source
    resource: /references/main-source.md
    title: 应用入口源码信源
---

# CLI 命令使用示例

## 启动应用

### 基本启动

```bash
# 启动应用（显示欢迎页或按启动模式设置）
jlab
```

### 打开当前目录

```bash
# 以当前目录为工作目录启动 JupyterLab
jlab .
```

### 打开 Notebook 文件

```bash
# 打开单个 Notebook
jlab my_notebook.ipynb

# 打开多个 Notebook（同一工作目录下）
jlab analysis.ipynb visualization.ipynb
```

### 指定工作目录

```bash
# 打开指定目录作为工作目录
jlab --working-dir ~/projects/data-science

# 在指定目录中打开文件
jlab --working-dir ~/projects/data-science notebook.ipynb
```

### 指定 Python 环境

```bash
# 使用指定 Python 环境启动
jlab --python-path ~/miniconda3/envs/myenv/bin/python

# 指定工作目录 + Python 环境
jlab --working-dir ~/projects/myproject --python-path ~/venvs/myproject/bin/python
```

### 连接远程服务器

```bash
# 连接到本地运行的 Jupyter Server
jlab http://localhost:8888/lab?token=abc123def456

# 连接到远程服务器
jlab http://192.168.1.100:8888/lab?token=mytoken

# 不持久化远程会话（关闭窗口后清除登录状态）
jlab --persist-session-data=false http://remote-server:8888/lab?token=xyz
```

### 设置日志级别

```bash
# 调试模式启动（显示详细日志）
jlab --log-level debug

# 仅显示错误
jlab --log-level error
```

## 环境管理（jlab env）

### 查看环境信息

```bash
# 显示当前环境配置信息
jlab env info
```

输出示例：
```
Default Python path: /home/user/miniconda3/bin/python
Bundled env path: /opt/JupyterLab/resources/env
Conda path: /home/user/miniconda3/bin/conda
System Python path: /usr/bin/python3
Envs directory: /home/user/.jupyter/jupyterlab-desktop/envs
```

### 列出所有环境

```bash
# 列出系统中发现的所有 Python 环境
jlab env list
```

### 创建新环境

```bash
# 创建新的 conda 环境（自动命名 env_1, env_2...）
jlab env create

# 指定名称创建
jlab env create --name datascience

# 指定路径创建
jlab env create --prefix ~/envs/myproject

# 创建 venv 虚拟环境
jlab env create --name myvenv --env-type venv

# 使用 conda-forge 和 defaults 两个 channel
jlab env create --name myenv -c conda-forge -c defaults

# 强制覆盖已有环境
jlab env create --name myenv --force

# 创建环境但不安装 jupyterlab（手动安装）
jlab env create --name minimal --add-jupyterlab-package=false
```

### 激活环境

```bash
# 在新终端中激活默认 Python 环境
jlab env activate
```

### 设置环境相关路径

```bash
# 设置 Conda 路径
jlab env set-conda-path ~/miniconda3/bin/conda

# 设置 conda channels
jlab env set-conda-channels conda-forge defaults bioconda

# 设置系统 Python 路径
jlab env set-system-python-path /usr/bin/python3

# 设置环境安装目录
jlab env set-python-envs-path ~/jupyter-envs

# 更新环境注册表（重新扫描系统）
jlab env update-registry
```

## 配置管理（jlab config）

### 查看配置

```bash
# 列出所有全局设置
jlab config list

# 列出当前目录的项目设置
jlab config list --project

# 列出指定目录的项目设置
jlab config list --project-path ~/projects/myproject
```

### 修改设置

```bash
# 设置暗色主题
jlab config set theme dark

# 设置启动模式为恢复上次会话
jlab config set startupMode restore-sessions

# 关闭自动检查更新
jlab config set checkForUpdatesAutomatically false

# 设置默认工作目录
jlab config set defaultWorkingDirectory ~/notebooks

# 设置 Ctrl+W 关闭标签页而非窗口
jlab config set ctrlWBehavior close-tab

# 设置环境变量（JSON 格式）
jlab config set serverEnvVars '{"CUDA_VISIBLE_DEVICES":"0"}'

# 为当前项目设置 Python 路径
jlab config set pythonPath ./venv/bin/python --project
```

### 重置设置

```bash
# 重置主题为默认值
jlab config unset theme

# 重置项目级 Python 路径
jlab config unset pythonPath --project
```

### 打开配置文件

```bash
# 在默认编辑器中打开全局设置文件
jlab config open-file

# 打开项目设置文件
jlab config open-file --project
```

## 查看应用数据和日志

```bash
# 查看应用数据
jlab appdata list

# 打开应用数据文件
jlab appdata open-file

# 显示日志
jlab logs show

# 打开日志文件
jlab logs open-file
```

## 查看帮助和版本

```bash
# 显示帮助
jlab --help
jlab -h

# 显示版本
jlab --version
```

## 典型工作流示例

### 场景1：为项目创建独立环境

```bash
# 1. 为项目创建 conda 环境
jlab env create --name myproject -c conda-forge

# 2. 进入项目目录
cd ~/projects/myproject

# 3. 使用项目环境启动 JupyterLab
jlab --python-path ~/.jupyter/jupyterlab-desktop/envs/myproject/bin/python .
```

### 场景2：连接远程服务器

```bash
# 在远程服务器上启动 Jupyter（在服务器上执行）
# jupyter lab --no-browser --port=8888

# 在本地桌面应用中连接
jlab http://remote-server:8888/lab?token=your_token_here
```

### 场景3：每个项目使用独立配置

```bash
# 进入项目目录
cd ~/projects/project-a

# 为项目设置独立 Python 环境
jlab config set pythonPath /path/to/project-a-venv/bin/python --project

# 设置项目级服务器参数
jlab config set serverArgs "--ServerApp.root_dir=/data" --project

# 启动时自动使用项目配置
jlab .
```

## 相关概念

- [CLI 命令系统](../concepts/07-cli-system.md) — jlab 命令完整用法与子命令参考
- [Python 环境管理](../concepts/05-python-env-management.md) — jlab env 子命令底层环境发现与管理机制
- [设置与配置系统](../concepts/06-settings-config.md) — jlab config 子命令读写的配置层级与持久化机制
