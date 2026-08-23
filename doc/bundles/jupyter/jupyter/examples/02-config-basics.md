---
type: example
title: Jupyter 配置基础操作
description: 生成配置文件、修改常用配置项、使用命令行覆盖配置、配置密码认证，掌握 Jupyter 配置系统的实战操作
tags: [example, config, jupyter-config, password, customization]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T11:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# Jupyter 配置基础操作

本示例将演示 Jupyter 配置系统的常用操作：生成配置文件、修改关键配置项、设置密码、通过命令行覆盖配置。

## 前置条件

- 已安装 JupyterLab 或 Notebook
- 了解 [Jupyter 通用配置系统](../concepts/04-config-system.md) 基本概念
- 了解 [目录结构与文件位置](../concepts/05-directories.md)

## 步骤 1：查看当前配置目录

首先确认 Jupyter 使用的配置目录：

```bash
jupyter --config-dir
```

典型输出：
- Linux/macOS: `/home/user/.jupyter`
- Windows: `C:\Users\user\.jupyter`

```bash
# 同时查看所有目录（配置/数据/运行时）
jupyter --paths
```

## 步骤 2：生成配置文件

为 Jupyter Server 生成默认配置文件：

```bash
jupyter server --generate-config
```

如果你使用经典 Notebook：

```bash
jupyter notebook --generate-config
```

> **注意**：JupyterLab 和 Notebook v7+ 使用 Jupyter Server 作为后端，配置文件名为 `jupyter_server_config.py`。经典 Notebook v6 使用 `jupyter_notebook_config.py`。

你会看到类似提示：

```
Writing default config to: /home/user/.jupyter/jupyter_server_config.py
```

如果文件已存在，会询问是否覆盖（输入 `y` 确认覆盖，`N` 保留现有配置）。

## 步骤 3：编辑配置文件

打开生成的配置文件（用你喜欢的编辑器）：

```bash
# Linux/macOS
nano ~/.jupyter/jupyter_server_config.py

# Windows
notepad %USERPROFILE%\.jupyter\jupyter_server_config.py
```

配置文件是 Python 脚本，所有配置项都被注释掉（以 `#` 开头），显示默认值。以下是一些常用配置的修改示例：

### 3.1 修改端口和网络监听

找到以下行，取消注释并修改：

```python
# 监听所有网络接口（允许远程访问，默认只监听 localhost）
c.ServerApp.ip = '0.0.0.0'

# 修改端口（默认 8888）
c.ServerApp.port = 9999

# 端口被占用时不尝试其他端口
c.ServerApp.port_retries = 0
```

### 3.2 控制浏览器行为

```python
# 启动时不自动打开浏览器（服务器环境常用）
c.ServerApp.open_browser = False
```

### 3.3 设置工作目录

```python
# 设置 Notebook 的根目录
c.ServerApp.root_dir = '/home/user/notebooks'
```

### 3.4 配置默认 Kernel

```python
# 设置默认启动的 Kernel
c.MappingKernelManager.default_kernel_name = 'python3'

# 关闭空闲 Kernel（单位：秒）
c.MappingKernelManager.cull_idle_timeout = 3600  # 1小时无活动后关闭
c.MappingKernelManager.cull_interval = 300        # 每5分钟检查一次
```

### 3.5 禁用 Token（仅限开发环境！）

```python
# 禁用 token 认证（⚠️ 仅在可信的本地/私有网络中使用）
c.ServerApp.token = ''

# 或者设置固定的 token
c.ServerApp.token = 'my-secret-token-123'
c.ServerApp.password = ''
```

> **警告**：禁用 token 并监听 0.0.0.0 会让任何人都能访问你的 Jupyter Server。生产环境务必设置密码。

### 完整配置示例

一个常用的开发环境配置：

```python
# jupyter_server_config.py - 开发环境配置
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '/home/user/projects'

# Kernel 管理
c.MappingKernelManager.default_kernel_name = 'python3'
c.MappingKernelManager.cull_idle_timeout = 7200

# 不关闭时显示设置
c.ServerApp.shutdown_no_activity_timeout = 0
```

保存文件后，启动 `jupyter lab`，配置即生效。

## 步骤 4：设置密码认证

推荐使用密码而非 token 进行认证。Jupyter 提供了内置的密码设置工具：

```bash
jupyter server password
```

按提示输入密码两次，密码的哈希值会自动写入配置文件：

```
Enter password: ********
Verify password: ********
[JupyterPasswordApp] Wrote hashed password to /home/user/.jupyter/jupyter_server_config.json
```

密码哈希存储在 `jupyter_server_config.json`（JSON 格式）而非 `.py` 文件中。设置密码后，启动 Jupyter 时访问页面会要求输入密码。

### 手动生成密码哈希

如果你想在配置文件中手动设置：

```python
# 在 Python 中生成密码哈希
from jupyter_server.auth import passwd
print(passwd('your-password-here'))
# 输出类似：'argon2:$argon2id$v=19$m=10240,t=10,p=8$...'
```

然后在配置文件中设置：

```python
c.ServerApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$...'
```

## 步骤 5：使用命令行覆盖配置

配置文件中的任何设置都可以通过命令行参数临时覆盖，无需修改文件：

```bash
# 临时使用不同端口
jupyter lab --ServerApp.port=9999

# 临时禁用浏览器打开
jupyter lab --no-browser

# 临时监听所有接口
jupyter lab --ip=0.0.0.0

# 常用选项有短别名
jupyter lab --port 9999 --no-browser --ip 0.0.0.0
```

命令行参数的优先级**高于**配置文件。

## 步骤 6：查看所有可配置项

查看完整的配置选项列表：

```bash
# 查看常用选项
jupyter lab --help

# 查看所有可配置项（非常详细，包括默认值和说明）
jupyter lab --help-all | less
```

`--help-all` 输出包含每个配置项的：
- 配置类名和属性名（如 `ServerApp.port`）
- 默认值
- 类型（Int、Unicode、Bool、List 等）
- 帮助文本

## 步骤 7：使用 nbconvert 配置

nbconvert 也有自己的配置文件：

```bash
jupyter nbconvert --generate-config
```

编辑 `jupyter_nbconvert_config.py`：

```python
# 默认导出格式
c.NbConvertApp.export_format = 'html'

# 自定义模板路径
c.TemplateExporter.template_path.append('./my-templates')

# 执行超时
c.ExecutePreprocessor.timeout = 120
```

## 验证配置生效

启动 JupyterLab 后，在浏览器中：

1. 访问 `http://localhost:8888/lab`（使用你配置的端口）
2. 如果设置了密码，确认需要输入密码
3. 在 Launcher 中确认默认 Kernel 正确
4. 左侧文件浏览器显示的是你配置的 `root_dir`

在终端中确认：

```bash
# 检查 Jupyter 是否在配置的端口上监听
# Linux/macOS:
lsof -i :8888
# Windows:
netstat -ano | findstr :8888
```

## 常见配置场景速查

| 场景 | 配置 |
|------|------|
| 远程服务器访问 | `ip='0.0.0.0'` + 设置密码 |
| Docker 容器中运行 | `ip='0.0.0.0'` + `allow_origin='*'` |
| 团队共享服务器 | 安装 JupyterHub |
| 自定义 CSS/JS | 创建 `~/.jupyter/custom/custom.css` 和 `custom.js` |
| 设置环境变量 | 在 Kernel 的 kernel.json 中设置 `env` |
| 禁用终端功能 | `c.ServerApp.terminals_enabled = False` |

## 相关概念

- [Jupyter 通用配置系统](../concepts/04-config-system.md) — 配置语法、集合类型、拼写陷阱
- [目录结构与文件位置](../concepts/05-directories.md) — 配置文件搜索路径
- [JupyterHub 多用户部署](../concepts/11-jupyterhub.md) — 多用户场景使用 JupyterHub 而非手动配置
