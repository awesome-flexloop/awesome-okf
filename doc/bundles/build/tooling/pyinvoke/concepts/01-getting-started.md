---
type: Concept
title: 5分钟快速上手
description: 创建第一个 tasks.py、使用 @task 装饰器、通过 inv 命令执行任务
tags: [pyinvoke, getting-started, tutorial, tasks.py]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# 5分钟快速上手

本教程将带你从零开始创建第一个 Invoke 项目，体验任务定义、列表查看和执行的完整流程。

## 步骤 1：安装 Invoke

首先确保已安装 Python 3.6+，然后通过 pip 安装：

```bash
pip install invoke
```

验证安装成功：

```bash
inv --version
```

## 步骤 2：创建 tasks.py

Invoke 默认从当前目录的 `tasks.py` 文件加载任务。在项目根目录创建该文件：

```python
from invoke import task

@task
def hello(c):
    """打印问候语。"""
    print("Hello, Invoke!")

@task
def greet(c, name="World"):
    """向指定的人打招呼。
    
    参数：
        name: 要问候的人名，默认为 World
    """
    print(f"Hello, {name}!")
```

说明：
- `from invoke import task` 导入 `@task` 装饰器
- `@task` 装饰器将普通 Python 函数标记为 Invoke 任务
- 每个任务函数的**第一个参数必须是 `c`**（即 Context 对象），即使你暂时用不到它
- 函数的 docstring（文档字符串）会自动成为任务的帮助文本

## 步骤 3：查看任务列表

在 `tasks.py` 所在目录运行：

```bash
inv --list
```

输出类似：

```
Available tasks:

  greet   向指定的人打招呼。
  hello   打印问候语。
```

你也可以使用简写 `-l`：

```bash
inv -l
```

## 步骤 4：执行任务

### 执行无参数任务

```bash
inv hello
```

输出：

```
Hello, Invoke!
```

### 执行带参数任务

```bash
inv greet --name Alice
```

输出：

```
Hello, Alice!
```

Invoke 自动将函数参数中的下划线（`_`）转换为命令行中的短横线（`-`）。如果参数名是 `user_name`，则命令行选项是 `--user-name`。

### 查看任务帮助

```bash
inv greet --help
```

输出类似：

```
Usage: inv[oke] [--core-opts] greet [--options] [other tasks here ...]

Docstring:
  向指定的人打招呼。

    参数：
        name: 要问候的人名，默认为 World

Options:
  -n STRING, --name=STRING   向指定的人打招呼。
```

## 步骤 5：执行 Shell 命令

任务的真正威力在于执行 shell 命令。这需要使用 Context 对象的 `c.run()` 方法：

```python
from invoke import task

@task
def build(c):
    """构建项目。"""
    c.run("mkdir -p dist")
    c.run("echo 'Building...'")
    # 这里可以放实际的构建命令，如 c.run("python setup.py sdist")

@task
def clean(c):
    """清理构建产物。"""
    c.run("rm -rf dist build *.egg-info")
    print("清理完成！")

@task
def deploy(c, env="staging"):
    """部署到指定环境。"""
    print(f"正在部署到 {env} 环境...")
    c.run(f"echo 'Deploying to {env}'")
```

执行：

```bash
inv build
inv clean
inv deploy --env production
```

## 步骤 6：组合任务（前置任务）

使用 `pre` 参数指定前置任务，确保在执行当前任务前先执行其他任务：

```python
from invoke import task

@task
def clean(c):
    """清理构建产物。"""
    c.run("rm -rf dist")
    print("已清理")

@task(pre=[clean])
def build(c):
    """构建项目（构建前自动清理）。"""
    c.run("mkdir -p dist")
    print("构建完成")
```

执行 `inv build` 时，会先自动执行 `clean`，再执行 `build`。

## 完整示例

以下是一个更完整的 `tasks.py`，展示了常见用法：

```python
from invoke import task

@task
def install(c):
    """安装项目依赖。"""
    c.run("pip install -r requirements.txt")
    print("依赖安装完成")

@task
def test(c, verbose=False):
    """运行测试套件。"""
    cmd = "pytest"
    if verbose:
        cmd += " -v"
    c.run(cmd)

@task(pre=[install])
def dev(c):
    """启动开发服务器（先安装依赖）。"""
    c.run("python -m http.server 8000")

@task
def lint(c):
    """代码风格检查。"""
    c.run("flake8 src/")

@task(pre=[lint, test])
def ci(c):
    """CI 流水线：lint + test。"""
    print("CI 检查通过！")
```

常用命令：

```bash
inv --list          # 列出所有任务
inv install         # 安装依赖
inv test            # 运行测试
inv test --verbose  # 运行测试（详细输出）
inv ci              # 运行完整 CI 流程（自动先 lint 再 test）
inv dev             # 启动开发服务器（自动先安装依赖）
```

## 关键要点总结

1. **文件名约定**：默认从 `tasks.py` 加载任务文件
2. **装饰器**：使用 `@task` 标记任务函数
3. **Context 参数**：每个任务的第一个参数必须是 `c`（Context），通过 `c.run()` 执行 shell 命令
4. **自动帮助**：函数 docstring 和参数自动出现在 `--help` 中
5. **下划线转短横线**：Python 参数名 `my_param` 映射为 CLI 选项 `--my-param`
6. **前置任务**：通过 `@task(pre=[other_task])` 指定执行顺序

## 相关概念

- [PyInvoke 简介](00-introduction.md)
- [Task 基础](02-task-basics.md)
- [Context 对象](03-context-object.md)
- [Collection 与命名空间](04-collection-namespace.md)
- [PyInvoke 源码信源登记](../references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](../references/pyinvoke-source.md)。
