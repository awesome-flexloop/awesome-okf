---
type: Example
title: 基础任务定义与执行
description: 从安装到定义第一个 @task 任务、执行任务、传递参数的完整示例
tags: [pyinvoke, task, "@task", getting-started, basic, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-src
    resource: /references/pyinvoke-source.md
    title: "PyInvoke 源码"
---

# 基础任务定义与执行

本示例展示使用 Invoke 的完整入门流程：从安装开始，创建第一个 `tasks.py` 文件，定义多个带参数的任务，并通过命令行执行。[^pyinvoke-src]

## 1. 安装 Invoke

使用 pip 安装 invoke 包：

```bash
pip install invoke
```

安装完成后，可以使用 `inv` 或 `invoke` 命令调用任务。

## 2. 创建 tasks.py

在项目根目录下创建 `tasks.py` 文件。Invoke 默认从当前目录加载名为 `tasks.py` 的模块作为任务集合：

```python
# tasks.py
from invoke import task


@task
def build(c):
    """构建项目——编译源代码并生成产物。"""
    print("正在构建项目...")
    c.run("echo '编译源代码'")
    c.run("echo '打包产物'")
    print("构建完成！")


@task(help={'verbose': '输出详细日志信息'})
def test(c, verbose=False):
    """运行测试套件。"""
    cmd = "echo '运行单元测试'"
    if verbose:
        cmd += " && echo '详细模式：显示所有测试用例输出'"
    c.run(cmd)
    print("测试完成！")


@task
def clean(c):
    """清理构建产物和临时文件。"""
    c.run("echo '清理 build/ 目录'")
    c.run("echo '清理 __pycache__/ 目录'")
    print("清理完成！")


@task(pre=[clean], post=[build])
def rebuild(c):
    """清理后重新构建（pre=clean, post=build）。"""
    print("重新构建流程：clean → rebuild 本体 → build")
```

代码要点说明：

- `@task` 装饰器将普通 Python 函数标记为 Invoke 任务；装饰器既可以不带括号使用（如 `@task`），也可以带括号传入配置参数（如 `@task(help={...})`）。
- 每个任务函数的**第一个参数必须是 `c`**（Context 对象），通过 `c.run()` 执行 shell 命令。
- `help` 参数为任务参数提供帮助文本，会在 `--help` 输出中显示。
- `pre` 和 `post` 参数指定前置/后置任务，在当前任务执行前/后自动运行。
- `verbose=False` 定义了一个布尔型可选参数，命令行中使用 `--verbose` 或 `-v` 传递。

## 3. 列出可用任务

使用 `inv --list`（或简写 `inv -l`）查看所有可用任务：

```bash
$ inv --list

Available tasks:

  build     构建项目——编译源代码并生成产物。
  clean     清理构建产物和临时文件。
  rebuild   清理后重新构建（pre=clean, post=build）。
  test      运行测试套件。
```

## 4. 执行任务

直接在命令行输入 `inv <任务名>` 来执行任务：

```bash
# 执行 build 任务
$ inv build
正在构建项目...
编译源代码
打包产物
构建完成！
```

### 带参数执行

布尔参数通过 `--flag` 形式传递：

```bash
# 执行 test 任务并开启详细模式
$ inv test --verbose
运行单元测试
详细模式：显示所有测试用例输出
测试完成！
```

也可以使用自动生成的短标志（取参数名首字母）：

```bash
$ inv test -v
```

### 查看任务帮助

使用 `inv --help <任务名>` 查看特定任务的详细帮助信息：

```bash
$ inv --help build

Usage: inv [--core-opts] build [--options] [other tasks here ...]

Docstring:
  构建项目——编译源代码并生成产物。

Options:
  no commands available


$ inv --help test

Usage: inv [--core-opts] test [--options] [other tasks here ...]

Docstring:
  运行测试套件。

Options:
  -v, --verbose  输出详细日志信息
```

### 执行带 pre/post 钩子的任务

执行 `rebuild` 任务时，会自动先执行 `clean`（pre），然后执行 `rebuild` 本体，最后执行 `build`（post）：

```bash
$ inv rebuild
清理 build/ 目录
清理 __pycache__/ 目录
清理完成！
重新构建流程：clean → rebuild 本体 → build
正在构建项目...
编译源代码
打包产物
构建完成！
```

## 5. 定义带位置参数和可选值参数的任务

除了简单的布尔标志，Invoke 还支持位置参数和带值的可选参数：

```python
# tasks.py（追加内容）
@task(help={
    'name': '要部署的环境名称',
    'components': '要部署的组件列表（可多次指定）',
})
def deploy(c, name, components=None):
    """部署到指定环境。"""
    print(f"部署到环境: {name}")
    if components:
        for comp in components:
            c.run(f"echo '部署组件: {comp}'")
    else:
        c.run("echo '部署全部组件'")


@task(positional=['message'])
def commit(c, message, amend=False):
    """提交代码（message 为位置参数）。"""
    cmd = f"git commit -m '{message}'"
    if amend:
        cmd += " --amend"
    c.run(cmd, echo=True)
```

执行示例：

```bash
# 位置参数直接跟在任务名后面
$ inv commit "修复登录 bug"
git commit -m '修复登录 bug'

# 使用 --amend 标志
$ inv commit "更新文档" --amend
git commit -m '更新文档' --amend

# 可迭代参数（iterable）——多次指定
$ inv deploy --name production --components api --components worker
部署到环境: production
部署组件: api
部署组件: worker
```

> 注意：对于需要多次指定的列表参数（如 `components`），需要在 `@task` 中使用 `iterable=['components']` 声明，使其正确解析为列表。

## 相关概念

* [入门指南（§1）](../concepts/01-getting-started.md)
* [Task 基础（§2）](../concepts/02-task-basics.md)
* [Context 对象（§3）](../concepts/03-context-object.md)
* [执行模型（§8）](../concepts/08-execution-model.md)

[^pyinvoke-src]: PyInvoke 源码，见本 bundle 信源登记 [references/pyinvoke-source.md](../references/pyinvoke-source.md)。
