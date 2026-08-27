---
type: Concept
title: 代码检查与格式化
description: 使用 checks 模块进行 black 格式化、flake8 lint，以及配置自定义检查流程
tags: [invocations, checks, black, flake8, formatting, linting]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 代码检查与格式化

`invocations.checks` 模块提供 Python 项目常用的代码质量检查任务：black 格式化和 flake8 lint。

## 快速使用

```python
# tasks.py
from invoke import Collection
from invocations import checks

ns = Collection(checks)
```

```bash
inv --list  # 应看到 checks.blacken, checks.lint, checks.all
```

## blacken：Black 格式化

`blacken` 任务使用 [Black](https://black.readthedocs.io/) 格式化所有 `.py` 文件：

```bash
# 格式化所有 Python 文件
inv checks.blacken

# 只检查不修改（CI 中常用）
inv checks.blacken --check

# 显示 diff 但不修改
inv checks.blacken --diff

# 指定行长度（默认 79）
inv checks.blacken --line-length=100

# 指定要搜索的文件夹（可多次指定）
inv checks.blacken --folders=src --folders=tests

# 额外的 find 命令选项（排除目录等）
inv checks.blacken --find-opts="-and -not -path './vendor/*'"
```

### blacken 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `line_length` | int | 79 | Black 的行长度参数 |
| `folders` | list | `["."]` | 搜索 `.py` 文件的目录列表，可在 CLI 中多次指定 `--folders` |
| `check` | bool | False | 运行 `black --check`（不修改文件，仅检查） |
| `diff` | bool | False | 运行 `black --diff`（显示差异但不修改） |
| `find_opts` | str | "" | 追加到内部 `find` 命令末尾的额外选项，用于排除目录等 |

### blacken 配置

可以在 Collection 配置中设置默认值：

```python
ns.configure({
    "blacken": {
        "folders": ["src", "tests"],
        "find_opts": "-and -not -path './vendor/*' -and -not -path './build/*'",
    },
})
```

blacken 内部构建的命令格式为：

```bash
find <folders> -name '*.py'<find_opts> | xargs black -l <line_length> [--check] [--diff]
```

### blacken 的别名

`blacken` 任务注册了别名 `format`：

```bash
inv checks.format  # 等价于 inv checks.blacken
```

## lint：Flake8 检查

`lint` 任务运行 flake8 进行代码风格检查：

```bash
inv checks.lint
```

`lint` 目前比较简单，直接运行 `flake8` 命令（`warn=True` 表示不因为 flake8 报错而中断）。未来可能改为支持 ruff 等更快的 linter。

## all：运行全部检查

`all` 任务是 checks 模块的默认任务，依次运行 `blacken` 和 `lint`：

```bash
inv checks        # 默认运行 all
inv checks.all    # 显式运行 all
```

`all` 会先设置 `c.config.run.echo = True` 让命令输出可见，然后依次调用 `blacken(c)` 和 `lint(c)`。

## 自定义检查流程

你可以基于 checks 模块构建自己的检查流程：

```python
from invoke import task, Collection
from invocations.checks import blacken, lint

@task
def typecheck(c):
    """运行 mypy 类型检查"""
    c.run("mypy src/", pty=True)

@task(pre=[blacken, lint, typecheck])
def all_checks(c):
    """运行所有代码检查"""
    print("所有检查通过!")

ns = Collection(all_checks, blacken, lint, typecheck)
```

## 注意事项

- `blacken` 使用 Unix `find` | `xargs` 管道，在 Windows 上需要 WSL 或 Git Bash 环境
- `lint` 使用 `flake8` 命令，需确保已安装（`pip install flake8`）
- Black 需要单独安装（`pip install black`）
- `find_opts` 中的路径模式注意转义 shell 特殊字符

## 相关概念

- [快速上手](01-getting-started.md)
- [Pytest 测试任务](03-testing-pytest.md)
- [组合模式：组装自己的任务集合](10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
