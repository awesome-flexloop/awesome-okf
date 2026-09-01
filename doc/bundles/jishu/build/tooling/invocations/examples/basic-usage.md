---
type: Example
title: 基础使用：在自己项目中引入 Invocations
description: 从零开始创建一个使用 Invocations 的 Python 项目 tasks.py，包含测试、格式化、文档构建
tags: [invocations, example, getting-started, tasks.py]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 基础使用：在自己项目中引入 Invocations

本示例展示如何从零开始在一个 Python 项目中使用 Invocations 管理自动化任务。

## 场景

假设你有一个 Python 项目，目录结构如下：

```
myproject/
├── myproject/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
├── docs/
│   ├── conf.py
│   └── index.rst
├── pyproject.toml
└── tasks.py        # 我们要创建的文件
```

你需要：运行测试、格式化代码、检查 lint、构建文档。

## 步骤

### 1. 安装依赖

```bash
pip install invocations pytest black flake8 sphinx watchdog
```

### 2. 创建 tasks.py

```python
"""myproject 自动化任务"""
from invoke import task, Collection
from invocations import checks
from invocations.docs import ns as docs_ns
from invocations.pytest import test, coverage
from invocations.packaging import release

@task
def clean(c):
    """清理构建产物和缓存"""
    c.run("rm -rf build dist *.egg-info")
    c.run("find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true")
    c.run("find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true")

@task
def install(c):
    """以可编辑模式安装项目"""
    c.run("pip install -e '.[dev]'")

# 组装命名空间
ns = Collection(
    clean,
    install,
    checks,          # checks.blacken, checks.lint, checks.all（模块自动收集）
    test,            # test（直接导入的任务函数）
    coverage,        # coverage（直接导入的任务函数）
    docs_ns,         # docs.build, docs.clean, docs.browse 等（预配置 Collection，含默认 sphinx 配置）
    release,         # release.status, release 等（子模块自动收集）
)

# 配置默认值
ns.configure({
    # Black 格式化配置
    "blacken": {
        "folders": ["myproject", "tests"],
        "line_length": 88,  # Black 默认 88
        "find_opts": "-and -not -path './build/*' -and -not -path './dist/*'",
    },
    # Sphinx 文档配置
    "sphinx": {
        "source": "docs",
        "target": "docs/_build",
        "target_file": "index.html",
    },
    # 打包配置
    "packaging": {
        "wheel": True,
        "changelog_file": "CHANGELOG.rst",
        "package": "myproject",
    },
    # 测试配置
    "tests": {
        "package": "myproject",
    },
    # 默认回显命令
    "run": {
        "echo": True,
    },
})
```

### 3. 查看可用任务

```bash
inv --list
```

你会看到一个层次化的任务列表：自定义的 `clean`、`install`，以及来自 invocations 的所有任务。

### 4. 常用命令

```bash
# 运行测试
inv test

# 运行覆盖率测试
inv coverage --report=html

# 格式化代码
inv checks.blacken

# 检查格式（不修改）
inv checks.blacken --check

# Lint 检查
inv checks.lint

# 构建文档
inv docs.build

# 构建文档并自动打开浏览器
inv docs.build --browse --clean

# 监控文档变化自动重建
inv docs.watch-docs

# 清理构建产物
inv clean

# 检查发布状态
inv release.status
```

### 5. 添加 CI 任务（可选）

如果需要 CI 支持，扩展 tasks.py：

```python
from invocations.ci import make_sudouser, sudo_run

@task
def ci_setup(c):
    """CI 环境准备"""
    make_sudouser(c)

@task
def ci_test(c):
    """CI 中运行测试"""
    sudo_run(c, "inv test")

ns.add_task(ci_setup)
ns.add_task(ci_test)
```

### 6. 添加交互确认（可选）

对于破坏性操作，使用 `confirm` 增加安全确认：

```python
from invocations.console import confirm

@task
def clean_dist(c):
    """清理 dist 目录"""
    if confirm("确定要删除 dist 目录?"):
        c.run("rm -rf dist")
        print("已清理 dist 目录")
    else:
        print("已取消")
```

## 关键要点

1. **按需导入**：只导入你需要的模块/任务，不需要的不导入
2. **配置覆盖**：通过 `ns.configure()` 覆盖默认值以匹配你的项目结构
3. **混合自定义**：在同一 tasks.py 中混合自定义任务和 invocations 任务
4. **命名空间嵌套**：导入 Collection 对象（如 checks、docs）会创建子命名空间，导入单个任务函数（如 test、coverage）则直接在根命名空间
5. **echo=True**：开发时设置 `"run": {"echo": True}` 可以看到实际执行的命令

## 相关概念

- [快速上手](../concepts/01-getting-started.md)
- [代码检查与格式化](../concepts/02-checks-formatting.md)
- [组合模式：组装自己的任务集合](../concepts/10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
