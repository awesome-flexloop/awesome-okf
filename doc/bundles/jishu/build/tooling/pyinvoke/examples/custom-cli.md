---
type: Example
title: 使用 Program 构建自定义 CLI
description: 通过 Program 类将 invoke 任务集合打包为独立 CLI 工具
tags: [pyinvoke, program, cli, console_scripts, entry_points, standalone, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-src
    resource: /references/pyinvoke-source.md
    title: "PyInvoke 源码"
---

# 使用 Program 构建自定义 CLI

Invoke 不仅可以作为 `inv` 命令使用，还可以通过 `Program` 类将任务集合打包为独立的命令行工具。这使得你可以将任务分发给不熟悉 Invoke 的用户，以自定义品牌（自定义名称、版本号）提供 CLI 体验。[^pyinvoke-src]

## 1. 创建 CLI 模块

假设我们要构建一个名为 `mytool` 的项目管理 CLI 工具，包含构建、测试、部署等命令。

首先创建 CLI 模块文件 `mytool/cli.py`：

```python
# mytool/cli.py
from invoke import Collection, Program, task


# ===== 任务定义 =====

@task(help={'clean': '构建前清理产物目录'})
def build(c, clean=False):
    """构建项目产物。"""
    if clean:
        c.run("echo '清理 dist/ 目录'")
    c.run("echo '编译源代码...'")
    c.run("echo '打包到 dist/'")
    print("✅ 构建完成")


@task(help={
    'coverage': '生成代码覆盖率报告',
    'verbose': '输出详细测试日志',
})
def test(c, coverage=False, verbose=False):
    """运行测试套件。"""
    cmd = "echo '运行测试...'"
    if verbose:
        cmd += " && echo '详细模式启用'"
    if coverage:
        cmd += " && echo '生成覆盖率报告 → coverage.xml'"
    c.run(cmd)
    print("✅ 所有测试通过")


@task(help={
    'env': '目标部署环境 (staging/production)',
    'dry-run': '仅模拟执行，不实际部署',
})
def deploy(c, env="staging", dry_run=False):
    """部署到指定环境。"""
    if dry_run:
        print(f"🔍 [DRY RUN] 模拟部署到 {env} 环境")
        return
    c.run(f"echo '连接到 {env} 服务器...'")
    c.run(f"echo '上传产物...'")
    c.run(f"echo '重启服务...'")
    print(f"✅ 已部署到 {env} 环境")


@task
def version(c):
    """显示当前版本信息。"""
    c.run("echo 'mytool version 1.0.0'")


# ===== 组装命名空间 =====

ns = Collection()
ns.add_task(build)
ns.add_task(test)
ns.add_task(deploy)
ns.add_task(version)

# 命名空间级配置
ns.configure({
    'run': {
        'echo': True,
    },
})


# ===== 创建 Program 实例 =====

program = Program(
    namespace=ns,
    name="MyTool",
    version="1.0.0",
    binary="mytool",
)


def main():
    """CLI 入口函数，由 setuptools console_scripts 调用。"""
    program.run()
```

关键参数说明：

| 参数 | 说明 |
|------|------|
| `namespace=ns` | 传入静态的 Collection 对象作为子命令集合。传入后，Program 不再从文件系统搜索 `tasks.py`，而是直接使用这个固定集合。 |
| `name="MyTool"` | 程序的显示名称（首字母大写），用于 `--version` 和帮助输出。 |
| `version="1.0.0"` | 版本号字符串，通过 `mytool --version` 显示。 |
| `binary="mytool"` | 二进制文件名，用于帮助文本中显示用法（如 `Usage: mytool [--core-opts]`）。 |

## 2. 配置 setup.py / pyproject.toml

在项目的包配置中，通过 `console_scripts` 入口点将 CLI 注册为可执行命令。

### 使用 setup.py（传统方式）

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="mytool",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "invoke>=2.0",
    ],
    entry_points={
        'console_scripts': [
            'mytool = mytool.cli:main',
        ],
    },
)
```

### 使用 pyproject.toml（现代方式）

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "mytool"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = [
    "invoke>=2.0",
]

[project.scripts]
mytool = "mytool.cli:main"
```

## 3. 安装并使用

以可编辑模式安装项目（开发阶段推荐）：

```bash
pip install -e .
```

安装完成后，`mytool` 命令就可以在任意目录使用了。

### 查看帮助

```bash
$ mytool --help
Usage: mytool [--core-opts] <subcommand> [--subcommand-opts] ...

Core options:

  --command-timeout=INT, -T INT  Specify a global command execution timeout, in seconds.
  --config=PATH, -f PATH         Runtime configuration file to use.
  --debug, -d                    Enable debug output.
  --dry, -R                      Echo commands instead of running.
  --echo, -e                     Echo executed commands before running.
  --help[=STRING], -h[STRING]    Show core or per-task help and exit.
  --hide=STRING                  Set default value of run()'s 'hide' kwarg.
  --list[=STRING], -l[STRING]    List available tasks, optionally limited to a namespace.
  --list-depth=INT, -D INT       When listing tasks, only show the first INT levels.
  --list-format=STRING, -F STRING  Change the display format used when listing tasks. Should be one of: flat (default), nested, json.
  --print-completion-script=STRING  Print the tab-completion script for your preferred shell (bash|zsh|fish).
  --prompt-for-sudo-password     Prompt user at start of session for the sudo.password config value.
  --pty, -p                      Use a pty when executing shell commands.
  --version, -V                  Show version and exit.
  --warn-only, -w                Warn, instead of failing, when shell commands fail.
  --write-pyc                    Enable creation of .pyc files.

Subcommands:

  build    构建项目产物。
  deploy   部署到指定环境。
  test     运行测试套件。
  version  显示当前版本信息。
```

### 查看版本

```bash
$ mytool --version
MyTool 1.0.0
```

### 列出任务

```bash
$ mytool --list

Available tasks:

  build    构建项目产物。
  deploy   部署到指定环境。
  test     运行测试套件。
  version  显示当前版本信息。
```

### 执行子命令

```bash
# 构建
$ mytool build
echo '编译源代码...'
编译源代码...
echo '打包到 dist/'
打包到 dist/
✅ 构建完成

# 构建前清理
$ mytool build --clean
echo '清理 dist/ 目录'
清理 dist/ 目录
echo '编译源代码...'
编译源代码...
echo '打包到 dist/'
打包到 dist/
✅ 构建完成

# 运行测试 + 覆盖率
$ mytool test --coverage
echo '运行测试...'
运行测试...
echo '生成覆盖率报告 → coverage.xml'
生成覆盖率报告 → coverage.xml
✅ 所有测试通过

# 部署到预发布
$ mytool deploy --env staging
echo '连接到 staging 服务器...'
连接到 staging 服务器...
echo '上传产物...'
上传产物...
echo '重启服务...'
重启服务...
✅ 已部署到 staging 环境

# 模拟部署到生产
$ mytool deploy --env production --dry-run
🔍 [DRY RUN] 模拟部署到 production 环境
```

### 查看子命令帮助

```bash
$ mytool --help deploy
Usage: mytool [--core-opts] deploy [--options] [other tasks here ...]

Docstring:
  部署到指定环境。

Options:
  --dry-run                     仅模拟执行，不实际部署
  -e STRING, --env=STRING       目标部署环境 (staging/production)
```

## 4. 带嵌套命名空间的独立 CLI

对于更复杂的 CLI，可以使用嵌套 Collection 组织子命令组：

```python
# mytool/cli.py（带嵌套命名空间的版本）
from invoke import Collection, Program, task


# db 子命令组
@task
def migrate(c):
    """执行数据库迁移。"""
    c.run("echo '运行数据库迁移...'")

@task
def seed(c):
    """填充种子数据。"""
    c.run("echo '填充种子数据...'")

db_ns = Collection('db')
db_ns.add_task(migrate)
db_ns.add_task(seed)


# build 子命令组
@task
def compile_src(c):
    """编译源代码。"""
    c.run("echo '编译...'")

@task
def bundle(c):
    """打包产物。"""
    c.run("echo '打包...'")

build_ns = Collection('build')
build_ns.add_task(compile_src, name='compile')
build_ns.add_task(bundle)


# 根级别任务
@task
def version(c):
    """显示版本。"""
    print("mytool 2.0.0")


ns = Collection()
ns.add_task(version)
ns.add_collection(build_ns)
ns.add_collection(db_ns)


program = Program(
    namespace=ns,
    name="MyTool",
    version="2.0.0",
    binary="mytool",
)

def main():
    program.run()
```

使用嵌套命名空间后的 CLI 体验：

```bash
$ mytool --list

Available tasks:

  build.bundle      打包产物。
  build.compile     编译源代码。
  db.migrate        执行数据库迁移。
  db.seed           填充种子数据。
  version           显示版本。

$ mytool build.compile
echo '编译...'
编译...

$ mytool db.migrate
echo '运行数据库迁移...'
运行数据库迁移...
```

## 5. 直接运行 CLI 模块（无需安装）

在开发过程中，也可以直接在 `cli.py` 末尾添加以下代码，以便通过 `python -m mytool.cli` 直接运行而无需安装：

```python
# mytool/cli.py（追加到末尾）
if __name__ == "__main__":
    main()
```

然后就可以直接运行：

```bash
python -m mytool.cli --help
python -m mytool.cli build
python -m mytool.cli deploy --env production
```

## 相关概念

* [CLI 与 Program 类（§7）](../concepts/07-cli-program.md)
* [Collection 与命名空间（§4）](../concepts/04-collection-namespace.md)
* [Task 基础（§2）](../concepts/02-task-basics.md)
* [配置系统（§5）](../concepts/05-configuration.md)

[^pyinvoke-src]: PyInvoke 源码，见本 bundle 信源登记 [references/pyinvoke-source.md](../references/pyinvoke-source.md)。
