---
type: Concept
title: CLI 命令系统
description: jlab 命令的完整用法，包括全局选项、env/config/appdata/logs 子命令、环境创建与激活、设置管理、命令参数解析流程
tags: [cli, jlab-command, yargs, environment-management, config-management, command-line]
prerequisites:
  - /concepts/05-python-env-management.md
  - /concepts/06-settings-config.md
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

# CLI 命令系统

## 概述

JupyterLab Desktop 提供 `jlab` 命令行工具，支持从终端启动应用、管理 Python 环境、管理配置、查看日志等操作。CLI 使用 yargs 库解析参数。

## 基本用法

```bash
jlab [options] [files-or-urls...]
```

不带参数直接运行 `jlab` 启动 GUI 应用。

## 全局选项

| 选项 | 缩写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--python-path` | - | string | - | 指定 Python 解释器路径 |
| `--working-dir` | - | string | - | 指定工作目录 |
| `--persist-session-data` | - | boolean | `true` | 持久化远程服务器会话数据 |
| `--log-level` | - | error/warn/info/verbose/debug | `warn` | 设置日志级别 |
| `--help` | `-h` | - | - | 显示帮助信息 |
| `--version` | - | - | - | 显示版本号 |

## 启动应用

### 打开文件或目录

```bash
# 打开当前目录
jlab .

# 打开指定目录
jlab /path/to/project

# 打开 Notebook 文件
jlab notebook.ipynb

# 打开多个文件
jlab file1.ipynb file2.ipynb

# 指定工作目录和文件
jlab --working-dir /path/to/project analysis.ipynb
```

文件打开逻辑：
- 文件：以第一个文件所在目录为工作目录，打开对应文件
- 目录：以该目录为工作目录启动新会话
- 多个文件/目录：混合处理，文件取其所在目录

### 打开远程服务器

```bash
# 连接到远程 Jupyter Server
jlab http://localhost:8888/lab?token=abc123

# 不持久化远程会话数据
jlab --persist-session-data=false http://remote-server:8888/lab?token=xyz
```

远程 URL 通过正则 `^https?:\/\/` 检测。

### 指定 Python 环境

```bash
# 使用指定 Python 环境启动
jlab --python-path /path/to/python

# 指定工作目录 + Python 路径
jlab --working-dir /my/project --python-path /my/venv/bin/python
```

## env 子命令 - Python 环境管理

```bash
jlab env <action> [options]
```

### env info - 显示环境信息

```bash
jlab env info
```

输出：
- 默认 Python 路径
- 捆绑环境路径
- Conda 路径
- 系统 Python 路径
- 环境安装目录

### env list - 列出所有环境

```bash
jlab env list
```

列出所有发现的和用户设置的 Python 环境。

### env create - 创建新环境

```bash
# 创建 conda 环境（自动命名）
jlab env create

# 指定名称创建
jlab env create --name myenv

# 指定路径创建
jlab env create --prefix /path/to/env

# 使用 venv 创建
jlab env create --env-type venv

# 指定 conda channels
jlab env create -c conda-forge -c defaults

# 从 conda-pack 文件创建
jlab env create --source /path/to/env.tar.gz --source-type conda-pack

# 强制覆盖已有环境
jlab env create --name myenv --force

# 不自动安装 jupyterlab
jlab env create --add-jupyterlab-package=false
```

创建选项：

| 选项 | 缩写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--name` | `-n` | string | 自动分配 | 环境名称（env_1, env_2...） |
| `--prefix` | `-p` | string | - | 环境安装路径 |
| `--source` | - | string | - | 环境来源路径/URL |
| `--source-type` | - | registry/conda-pack/conda-lock-file/conda-env-file | `registry` | 来源类型 |
| `--channel` | `-c` | string[] | `[]` | conda channels |
| `--env-type` | - | auto/conda/venv | `auto` | 环境类型 |
| `--add-jupyterlab-package` | - | boolean | `true` | 自动安装 jupyterlab |
| `--force` | - | boolean | `false` | 覆盖已有环境 |

### env activate - 激活环境

```bash
jlab env activate
```

在新的终端窗口中激活默认 Python 环境。

### env set-python-envs-path - 设置环境安装目录

```bash
jlab env set-python-envs-path /path/to/envs
```

### env set-conda-path - 设置 Conda 路径

```bash
jlab env set-conda-path /path/to/conda
```

### env set-conda-channels - 设置 Conda channels

```bash
jlab env set-conda-channels conda-forge defaults
```

### env set-system-python-path - 设置系统 Python 路径

```bash
jlab env set-system-python-path /usr/bin/python3
```

### env update-registry - 更新环境注册表

```bash
jlab env update-registry
```

重新扫描系统发现 Python 环境。

## config 子命令 - 设置管理

```bash
jlab config <action> [options]
```

### config list - 列出设置

```bash
# 列出全局设置
jlab config list

# 列出当前目录的项目设置
jlab config list --project

# 列出指定目录的项目设置
jlab config list --project-path /path/to/project
```

### config set - 设置配置项

```bash
# 设置全局设置
jlab config set theme dark
jlab config set startupMode restore-sessions
jlab config set checkForUpdatesAutomatically false

# 设置 JSON 值
jlab config set serverEnvVars '{"MY_VAR":"value"}'

# 设置项目级配置
jlab config set pythonPath /venv/bin/python --project
```

值自动解析为 JSON（boolean、number、对象、数组），无法解析则作为字符串。

### config unset - 重置配置项

```bash
# 重置全局设置为默认值
jlab config unset theme

# 重置项目级设置
jlab config unset pythonPath --project
```

### config open-file - 打开设置文件

```bash
# 在默认编辑器中打开全局设置文件
jlab config open-file

# 打开项目设置文件
jlab config open-file --project
```

设置文件位置：
- 全局：`{userDataDir}/settings.json`
- 项目：`{workingDir}/.jupyter/desktop-settings.json`

## appdata 子命令 - 应用数据管理

```bash
jlab appdata <action>
```

### appdata list - 列出应用数据

显示 app-data.json 中的数据（跳过 newsList 和 `_` 开头的字段）。

### appdata open-file - 打开应用数据文件

在系统默认编辑器中打开 app-data.json。

应用数据文件位置：`{userDataDir}/app-data.json`

## logs 子命令 - 日志管理

```bash
jlab logs <action>
```

### logs show - 显示日志

在终端中输出日志文件内容。

### logs open-file - 打开日志文件

在系统默认编辑器中打开日志文件。

## 立即退出命令

以下命令执行后立即退出，不启动 GUI：

- `jlab --help` / `jlab -h`
- `jlab --version`
- `jlab env <action>` 所有 env 子命令
- `jlab config <action>` 所有 config 子命令
- `jlab appdata list` / `jlab appdata open-file`
- `jlab logs show` / `jlab logs open-file`

## macOS jlab 命令设置

在 macOS 上，应用启动时调用 `setupJLabCommand()` 在 `/usr/local/bin/jlab` 创建符号链接（需要权限时弹出认证对话框）。如果该位置不可写，会提示用户手动创建。

## CLI 参数解析流程（processArgs）

```
processArgs()
  ├─ 配置 yargs 解析器
  ├─ 注册全局选项
  ├─ 注册 env/config/appdata/logs 子命令
  ├─ yargs.parse() 解析参数
  ├─ 检查是否为立即退出命令
  │    ├─ 是 → 执行命令 → process.exit(0)
  │    └─ 否 → 继续启动 GUI
  └─ 返回解析后的 argv
```

参数解析结果存入全局 `argv: ICLIArguments` 变量，传递给 JupyterApplication 构造函数。

## SessionConfig.createFromArgs()

CLI 参数解析后，非退出命令会调用 `SessionConfig.createFromArgs(cliArgs)` 创建会话配置：

1. 遍历位置参数，检测是否有 `https?://` URL（远程会话）
2. 解析 `--working-dir` 为绝对路径，验证存在性
3. 解析文件路径为相对于 workingDir 或 cwd 的路径
4. 解析 `--python-path` 为绝对路径
5. 返回对应的 SessionConfig（远程或本地）

## 相关信源

- [CLI 信源](/references/cli-source.md)
- [Main 信源](/references/main-source.md)
- [Settings 信源](/references/settings-source.md)

## 下一篇

- [事件与IPC系统](/concepts/08-event-ipc-system.md)

## 相关概念

- [Python 环境管理](/concepts/05-python-env-management.md) — jlab env 子命令底层调用环境发现、创建和激活逻辑
- [设置与配置系统](/concepts/06-settings-config.md) — jlab config 子命令读写 UserSettings/WorkspaceSettings
- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md) — CLI 参数在启动序列的 processArgs 阶段解析
- [CLI 命令使用示例](/examples/cli-usage-examples.md) — 常见 CLI 操作场景的实际示例
