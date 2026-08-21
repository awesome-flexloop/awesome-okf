---
type: Concept
title: CLI 与 Program 类
description: 构建自定义 CLI 工具、Program 参数、核心选项、任务参数、Parser 机制、tab 补全
tags: [pyinvoke, program, cli, CLI, parser, Argument, tab-completion, FilesystemLoader, console_scripts]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# CLI 与 Program 类

`Program` 类是 Invoke 命令行接口的顶层管理器。它不仅支撑着 `inv`/`invoke` 命令本身，也是将任务集合打包为独立 CLI 工具的核心机制。通过 Program，你可以构建具有自定义名称、版本号、内置命名空间的命令行程序，并通过 `setup.py`/`pyproject.toml` 的 `console_scripts` 入口分发给用户。

## Program 的两种运行模式

Program 支持两种运行模式：

### 任务运行器模式（默认）

当构造 Program 时不传入 `namespace` 参数（或传入 `None`），Program 行为类似 `invoke` 命令本身：从文件系统动态搜索并加载任务集合，暴露 `--collection`、`--search-root`、`--list` 等任务相关选项。

```python
from invoke import Program

# 默认模式：等价于 invoke 命令
program = Program()
program.run()
```

### 捆绑命名空间模式

当构造时传入一个 `Collection` 对象作为 `namespace`，Program 将其作为固定的子命令集合，不再暴露动态加载相关的选项。适合将 Invoke 任务集合打包为独立 CLI 工具：

```python
from invoke import Collection, Program, task

@task
def build(c):
    """构建项目。"""
    c.run("echo building...")

@task
def test(c):
    """运行测试。"""
    c.run("echo testing...")

ns = Collection(build, test)
program = Program(namespace=ns, version="1.0.0")
program.run()
```

在此模式下，`--help` 输出中不会出现 `-c/--collection` 和 `-r/--search-root` 选项，子命令直接列在帮助信息中。

## Program 构造参数

`Program.__init__()` 接受以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `version` | `str` | `"unknown"` | 程序版本号，显示在 `--version` 输出中 |
| `namespace` | `Collection` | `None` | 捆绑的任务集合；None 表示任务运行器模式 |
| `name` | `str` | 自动推导 | 程序显示名称（如 `"Foobar"`），默认从 argv[0] 首字母大写推导 |
| `binary` | `str` | 自动推导 | 帮助文本中的二进制名（如 `"foobar"`），默认取 argv[0] |
| `binary_names` | `list[str]` | 自动推导 | 补全脚本使用的二进制名列表（如 `["fb", "foobar"]`） |
| `loader_class` | `type` | `FilesystemLoader` | 任务加载器类 |
| `executor_class` | `type` | `Executor` | 任务执行器类 |
| `config_class` | `type` | `Config` | 配置类 |

名称推导逻辑：
- `name`：argv[0] 的 basename 首字母大写（如 `"inv"` → `"Inv"`）
- `binary`：argv[0] 的 basename 原样（如 `"inv"`）
- Invoke 自身将 `binary` 设为 `"inv[oke]"`，`binary_names` 设为 `["inv", "invoke"]`

## 核心选项（core_args）

`Program.core_args()` 定义了 18 个始终可用的核心命令行标志：

| 标志 | 短标志 | 类型 | 默认 | 说明 |
|------|--------|------|------|------|
| `--command-timeout` | `-T` | int | — | 全局命令执行超时秒数 |
| `--complete` | — | bool | False | 打印 tab 补全候选 |
| `--config` | `-f` | str | — | 指定运行时配置文件路径 |
| `--debug` | `-d` | bool | False | 启用调试输出 |
| `--dry` | `-R` | bool | False | 试运行模式（仅打印不执行） |
| `--echo` | `-e` | bool | False | 执行前打印命令 |
| `--help` | `-h` | 可选 | — | 显示帮助（可接任务名显示任务帮助） |
| `--hide` | — | str | — | 设置 run() 的 hide 默认值 |
| `--list` | `-l` | 可选 | — | 列出可用任务（可接命名空间名） |
| `--list-depth` | `-D` | int | 0 | 列表深度限制（0=无限制） |
| `--list-format` | `-F` | str | `flat` | 列表格式：flat/nested/json |
| `--print-completion-script` | — | str | `""` | 打印指定 shell 的补全脚本（bash/zsh/fish） |
| `--prompt-for-sudo-password` | — | bool | False | 启动时提示输入 sudo 密码 |
| `--pty` | `-p` | bool | False | 使用伪终端执行命令 |
| `--version` | `-V` | bool | False | 显示版本并退出 |
| `--warn-only` | `-w` | bool | False | 命令失败时仅警告 |
| `--write-pyc` | — | bool | False | 允许创建 .pyc 文件 |

这些选项通过 `Argument` 类定义，由 Parser 系统解析。解析后的值映射到配置 overrides 层，影响所有任务的执行行为。

## 任务相关选项（task_args）

`Program.task_args()` 定义了仅在任务运行器模式（无内置 namespace）下添加的 3 个选项：

| 标志 | 短标志 | 说明 |
|------|--------|------|
| `--collection` | `-c` | 指定要加载的任务集合名称 |
| `--no-dedupe` | — | 禁用任务去重 |
| `--search-root` | `-r` | 指定查找任务模块的根目录 |

这些选项在捆绑命名空间模式下不会出现，因为任务集合已经固定。

## run() 方法与执行流程

`Program.run(argv=None, exit=True)` 是 CLI 的主入口方法，执行以下流程：

```
create_config() → parse_core() → parse_collection() → parse_tasks()
→ parse_cleanup() → update_config() → execute()
```

### 1. create_config()

实例化 Config 对象（默认加载系统级和用户级配置文件）。

### 2. parse_core(argv)

- 规范化 argv（None→sys.argv，字符串→split）
- 创建 Parser（以核心选项作为 initial context）
- 解析 argv，得到 core ParseResult
- 处理 `--version`、`--print-completion-script` 等即时退出选项
- 根据 `--debug` 启用日志
- 根据 `--write-pyc` 设置 `sys.dont_write_bytecode`

### 3. parse_collection()

- 如果有捆绑 namespace，直接使用
- 否则：如果裸 `--help`（无任务名），打印核心帮助并退出；否则通过 `FilesystemLoader` 加载任务集合
- 加载项目级配置文件（`invoke.yaml` 等）

### 4. parse_tasks()

- 创建包含所有任务 ParserContext 的 Parser
- 解析剩余 argv，得到任务列表（`self.tasks`）和任务中的核心标志（`core_via_tasks`）
- 将任务中出现的核心标志合并回 core 解析结果

### 5. parse_cleanup()

- 处理 `--help`（核心帮助/任务帮助）
- 处理 `--list`（列出任务）
- 处理 `--complete`（tab 补全）
- 如果没有指定任务且无默认任务，打印全局帮助

### 6. update_config()

将解析结果映射到 Config overrides 层：
- `--echo` → `run.echo`
- `--warn-only` → `run.warn`
- `--pty` → `run.pty`
- `--hide` → `run.hide`
- `--dry` → `run.dry`
- `--no-dedupe` → `tasks.dedupe = False`
- `-T/--command-timeout` → `timeouts.command`
- `--prompt-for-sudo-password` → `sudo.password`（通过 getpass 输入）
- `-f/--config` → 运行时配置文件路径

同时加载运行时配置文件和环境变量 `INVOKE_RUNTIME_CONFIG`。

### 7. execute()

- 确定 Executor 类（构造参数、配置项 `tasks.executor_class`、或默认 `Executor`）
- 创建 Executor 实例，传入 collection、config、core 解析结果
- 调用 `executor.execute(*self.tasks)` 执行任务

exit 参数控制异常处理：`exit=True`（默认）时，`UnexpectedExit`/`Exit`/`ParseError` 会触发 `sys.exit()`；`exit=False` 时异常向上传播（主要用于测试）。

## FilesystemLoader：任务发现

`FilesystemLoader` 负责从文件系统发现和加载任务模块。搜索逻辑：

1. 从 `start` 目录（由 `--search-root` 指定或默认为当前目录）开始
2. 查找名为 `tasks.py` 的文件或 `tasks/` 包目录
3. 如果未找到，向上递归搜索父目录
4. 找到后加载模块，返回 `(module, parent_directory)` 元组

通过 `-c/--collection` 可以指定其他模块名替代默认的 `tasks`。配置项 `tasks.collection_name` 和 `tasks.search_root` 可设置默认值。

## 任务列表输出

`--list`/`-l` 标志列出可用任务，支持三种格式：

### flat（默认）

所有任务以完整点号路径显示，按字母排序：

```
$ inv --list
Available tasks:

  build        构建项目。
  db.migrate   执行数据库迁移。
  db.reset     重置数据库。
  test         运行测试。
```

### nested

以缩进树状结构显示命名空间嵌套，默认任务用 `*` 标记：

```
$ inv --list --format=nested
Available tasks ('*' denotes collection defaults):

  build        构建项目。
  db
    migrate    执行数据库迁移。
    reset      重置数据库。
  test         运行测试。
```

`--list-depth/-D` 可限制显示深度，超过深度的子集合显示任务/子集合数量摘要。

### json

以 JSON 格式输出完整的集合树结构（通过 `Collection.serialized()`），适合脚本消费。不支持 `--list-depth`。

### 作用域列表

`--list <namespace>` 仅列出指定命名空间下的任务：

```bash
$ inv --list db
Available tasks 'db':

  db.migrate   执行数据库迁移。
  db.reset     重置数据库。
```

## Tab 补全

Invoke 支持 Bash、Zsh、Fish 三种 shell 的 tab 补全：

### 安装补全脚本

```bash
# Bash
inv --print-completion-script bash > /etc/bash_completion.d/inv
# Zsh
inv --print-completion-script zsh > ~/.zsh/completions/_inv
# Fish
inv --print-completion-script fish > ~/.config/fish/completions/inv.fish
```

### 动态补全

`--complete` 标志在 shell 补全时被调用，根据当前命令行状态输出候选列表。补全逻辑由 `invoke.completion.complete` 模块实现。

补全脚本中使用 `binary_names` 列表来确定哪些命令名应触发该补全。对于自定义 Program，应正确设置 `binary_names` 参数。

## 构建独立 CLI 工具

通过 Program 的捆绑命名空间模式，可以将任务集合打包为独立命令行工具。典型的项目结构：

```
mytool/
├── mytool/
│   ├── __init__.py
│   └── tasks.py       # 任务定义
├── pyproject.toml
└── setup.py
```

**mytool/\_\_init\_\_.py：**

```python
from invoke import Collection, Program, task

@task
def build(c, clean=False):
    """构建项目。"""
    if clean:
        c.run("rm -rf dist/")
    c.run("python -m build")

@task
def deploy(c, env="staging"):
    """部署到指定环境。"""
    c.run(f"fab deploy:{env}")

ns = Collection(build, deploy)
program = Program(
    namespace=ns,
    version="1.0.0",
    name="MyTool",
    binary="mytool",
    binary_names=["mytool"],
)

def main():
    program.run()
```

**pyproject.toml 或 setup.py 入口：**

```python
# setup.py
from setuptools import setup
setup(
    name="mytool",
    version="1.0.0",
    packages=["mytool"],
    install_requires=["invoke"],
    entry_points={
        "console_scripts": [
            "mytool = mytool:main",
        ],
    },
)
```

安装后用户即可直接使用 `mytool` 命令：

```bash
mytool --help
mytool build --clean
mytool deploy --env=production
mytool --list
```

## 相关概念

- [Collection 与命名空间](/concepts/04-collection-namespace.md)
- [配置系统](/concepts/05-configuration.md)
- [执行模型](/concepts/08-execution-model.md)
- [高级模式](/concepts/11-advanced-patterns.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Program 类定义于 `invoke/program.py`，FilesystemLoader 定义于 `invoke/loader.py`，Parser/Argument 定义于 `invoke/parser/`。
