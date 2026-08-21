---
type: Concept
title: 快速上手
description: 安装 Invocations、创建第一个组合 tasks.py、执行与配置
tags: [invocations, getting-started, setup, tasks.py]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 快速上手

## 安装

```bash
pip install invocations
```

验证安装：

```bash
pip show invocations
# 应显示 Version: 4.1.0
```

## 最小示例：组合任务

Invocations 的核心使用方式是**在你的 `tasks.py` 中导入并组合已有任务**。以下是一个最小可用示例：

```python
# tasks.py
from invoke import Collection
from invocations import checks
from invocations.pytest import test, coverage
from invocations.docs import ns as docs_ns
from invocations.packaging import release

ns = Collection(
    checks,       # 代码检查子命名空间：inv checks.blacken, inv checks.lint
    test,         # 测试任务：inv test
    coverage,     # 覆盖率：inv coverage
    docs_ns,      # 文档子命名空间：inv docs.build, inv docs.watch-docs
    release,      # 发布子命名空间：inv release.status, inv release
)

# 覆盖默认配置
ns.configure({
    "sphinx": {
        "source": "docs",
        "target": "docs/_build",
    },
    "packaging": {
        "wheel": True,
        "changelog_file": "docs/changelog.rst",
    },
    "blacken": {
        "folders": ["src", "tests"],
        "find_opts": "-and -not -path './vendor/*'",
    },
})
```

## 查看可用任务

```bash
inv --list
```

你应该看到类似以下的任务树：

```
Available tasks:

  checks.blacken (checks.format)  Run black on the current source tree
  checks.lint                     Apply linting
  coverage                        Run pytest with coverage enabled
  docs.browse (docs._browse)      Open build target's index.html in a browser
  docs.build (default)            Build the project's Sphinx docs
  docs.clean (docs._clean)        Nuke docs build target directory
  docs.doctest                    Run Sphinx' doctest builder
  docs.sites                      Build both doc sites w/ maxed nitpicking
  docs.tree                       Display documentation contents with 'tree'
  docs.watch-docs                 Watch both doc trees & rebuild them if files change
  docs.www.build (default)        Build the main project website
  release.all (release, default)  Catchall version-bump/tag/changelog/PyPI upload
  release.build                   Build sdist and/or wheel archives
  release.prepare                 Edit changelog & version, git commit, and git tag
  release.publish                 Publish code to PyPI or index of choice
  release.push                    Push current branch and tags to default Git remote
  release.status                  Print current release status
  release.test-install            Test installation of build artifacts
  release.upload                  Upload (potentially also signing) all artifacts
  test                            Run pytest with given options
```

注意命名空间嵌套：`docs.www.build` 是 docs 模块内 www 子集合的 build 任务。

## 执行任务

```bash
# 运行测试
inv test

# 运行覆盖率测试并生成 HTML 报告
inv coverage --report=html

# 构建文档
inv docs.build

# 构建文档并在浏览器中打开
inv docs.build --browse

# 检查发布状态（不会做任何修改）
inv release.status

# 干跑发布流程（不会真的上传）
inv release --dry-run

# 代码格式化
inv checks.blacken

# 只检查不修改
inv checks.blacken --check
```

## 添加自定义任务

你可以在同一 `tasks.py` 中混合自定义任务和 Invocations 任务：

```python
from invoke import task, Collection
from invocations import checks
from invocations.pytest import test

@task
def clean(c):
    """清理构建产物"""
    c.run("rm -rf build dist *.egg-info")
    c.run("find . -type d -name __pycache__ -exec rm -rf {} +")

@task
def install(c):
    """以可编辑模式安装项目"""
    c.run("pip install -e '.[dev]'")

ns = Collection(clean, install, checks, test)
```

## 配置覆盖

每个 Invocations 模块都通过 `ns.configure()` 设置了默认值，你可以在自己的 Collection 中覆盖：

```python
ns.configure({
    # black 行长度改为 100
    "blacken": {"folders": ["src"], "find_opts": ""},
    # 测试默认使用详细模式
    "run": {"echo": True},
    # 打包配置
    "packaging": {
        "changelog_file": "CHANGELOG.rst",
        "package": "myproject",
        "wheel": True,
    },
})
```

配置可以从 YAML 文件、环境变量和 CLI 参数多层级合并，这属于 PyInvoke 核心功能（参见 [PyInvoke 配置系统](../pyinvoke/concepts/05-configuration.md)）。

## 相关概念

- [Invocations 简介](/concepts/00-introduction.md)
- [代码检查与格式化](/concepts/02-checks-formatting.md)
- [Pytest 测试任务](/concepts/03-testing-pytest.md)
- [Sphinx 文档管理](/concepts/04-docs-sphinx.md)
- [包发布生命周期](/concepts/05-packaging-release.md)
- [Invocations 源码信源登记](/references/invocations-source.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
