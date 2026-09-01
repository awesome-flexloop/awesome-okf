---
type: Concept
title: 组合模式：组装任务集合
description: 深入理解 Invocations 的组合设计——如何按需导入、配置覆盖、跨 Collection 调用、自定义子集合，以及 Invoke 任务组合的最佳实践
tags: [invocations, composition, collection, namespace, patterns, best-practices]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 组合模式：组装任务集合

Invocations 的核心设计理念是**模块化组合**——每个模块是独立的乐高积木，用户在自己的 `tasks.py` 中按需组装。本文深入讲解 Invoke Collection 的组合模式和最佳实践。

## 三种导入方式

### 方式1：导入子命名空间

对于**有预配置 ns 的模块**（如 docs、ci），导入其 ns Collection：

```python
from invoke import Collection
from invocations.docs import ns as docs_ns
from invocations.ci import ns as ci_ns
from invocations.packaging import release

ns = Collection(docs_ns, ci_ns, release)
```

对于**无 ns 的模块**（如 checks、pytest、testing），直接导入模块（Invoke 自动从中收集 @task 函数）：

```python
from invoke import Collection
from invocations import checks, testing
from invocations.packaging import release

ns = Collection(checks, testing, release)
```

这会创建嵌套命名空间：
- `inv checks.blacken`、`inv checks.lint`、`inv checks.all`
- `inv docs.build`、`inv docs.clean`、`inv docs.browse`
- `inv ci.make-sudouser`、`inv ci.sudo-run`
- `inv release.status`、`inv release`

适合你想完整使用某个模块的所有任务。导入预配置 ns 可以获得模块内置的默认配置（如 docs 的 sphinx.source/target 默认值）。

### 方式2：导入单个任务

```python
from invoke import Collection
from invocations.pytest import test, coverage
from invocations.console import confirm

ns = Collection(test, coverage)
```

任务直接挂载到根命名空间：
- `inv test`、`inv coverage`

适合你只需要某些特定任务，不想要整个子命名空间。

### 方式3：导入工具函数（非任务）

```python
from invocations.console import confirm
from invocations.util import tmpdir
from invocations.environment import in_ci
from invocations.watch import watch, make_handler, observe
```

工具函数不带 @task 装饰器，不会出现在 CLI 任务列表中，而是在你的自定义任务中作为 Python 函数调用。

## 配置覆盖模式

### 全局配置

```python
ns.configure({
    "run": {"echo": True},  # 全局显示执行的命令
    "sphinx": {
        "source": "docs",
        "target": "docs/_build",
    },
    "packaging": {
        "wheel": True,
        "changelog_file": "CHANGELOG.rst",
    },
})
```

### 子 Collection 配置

当导入 Collection 对象时，可以在添加到父 Collection 后覆盖其配置：

```python
ns = Collection()
ns.add_collection(checks)
ns.configure({
    "blacken": {
        "folders": ["src", "tests"],
        "line_length": 100,
    },
})
```

或者创建独立 Collection 时传入配置：

```python
from invocations.docs import _site
# _site 工厂函数已内置 configure
my_docs = _site("docs", "my API docs")
```

### 配置优先级

Invoke 的配置系统按以下优先级合并（从高到低）：
1. CLI 参数
2. 运行时修改（`c.config.run.echo = True`）
3. 环境变量
4. 用户级配置文件
5. 项目级配置文件
6. Collection 层级配置（ns.configure）
7. 系统默认值

## 跨 Collection 任务调用

### 方式1：Python 函数调用（推荐）

任务本质是 Python 函数，可以直接调用：

```python
from invoke import task, Collection
from invocations.checks import blacken, lint

@task
def all_checks(c):
    """运行所有检查"""
    c.config.run.echo = True
    blacken(c)
    lint(c)

ns = Collection(all_checks, blacken, lint)
```

### 方式2：使用独立 Context（多配置场景）

当需要在同一个任务中以不同配置调用子 Collection 的任务时，需要克隆 Context：

```python
from invoke import task, Collection, Context
from invocations.docs import docs, www

@task
def build_all(c):
    """构建所有文档站点"""
    # 为每个子站点创建独立 Context
    docs_c = Context(config=c.config.clone())
    www_c = Context(config=c.config.clone())
    docs_c.update(**docs.configuration())
    www_c.update(**www.configuration())
    
    # 静默第一轮构建（生成 intersphinx inventory）
    docs_c["run"].hide = True
    www_c["run"].hide = True
    docs["build"](docs_c)
    www["build"](www_c)
    
    # 严格模式第二轮构建
    docs_c["run"].hide = False
    www_c["run"].hide = False
    docs["build"](docs_c, nitpick=True)
    www["build"](www_c, nitpick=True)
```

这种模式来自 `invocations.docs.sites`，是当前 Invoke API 下的标准做法。

## 创建自定义子集合

### 工厂函数模式

模仿 `docs._site()` 工厂函数：

```python
from invoke import Collection, task
import sys

def make_docs_collection(name, source_dir, help_text):
    """创建一个文档子集合"""
    @task(default=True)
    def build(c, clean=False, browse=False):
        if clean:
            c.run(f"rm -rf {source_dir}/_build")
        c.run(f"sphinx-build {source_dir} {source_dir}/_build", pty=True)
        if browse:
            c.run(f"open {source_dir}/_build/index.html")
    
    coll = Collection(name, build)
    coll.configure({
        "sphinx": {"source": source_dir, "target": f"{source_dir}/_build"},
    })
    coll.__doc__ = f"Tasks for {help_text}"
    return coll

# 创建多个站点
api_docs = make_docs_collection("api", "docs/api", "API documentation")
user_docs = make_docs_collection("user", "docs/user", "user guides")

ns = Collection(api_docs, user_docs)
```

### Collection.from_module 模式

从一个 Python 模块自动加载所有任务：

```python
from invoke import Collection
import myproject.dev_tasks
import myproject.deploy_tasks

dev = Collection.from_module(myproject.dev_tasks, name="dev")
deploy = Collection.from_module(myproject.deploy_tasks, name="deploy")

ns = Collection(dev, deploy)
```

这在多项目共享任务模块时特别有用。

## 命名技巧

### 避免命名冲突

当不同模块有同名任务时，使用子命名空间避免冲突：

```python
# testing.py 和 pytest.py 都有 test 任务
from invocations import testing as nose_testing
from invocations import pytest as pytest_mod

ns = Collection(nose_testing, pytest_mod)
# inv nose-testing.test / inv pytest-mod.test
```

或者导入时重命名：

```python
from invocations.pytest import test as pytest_test
from invocations.testing import test as nose_test

ns = Collection(pytest_test, nose_test)
# inv pytest-test / inv nose-test
```

### 下划线与连字符

Invoke 自动将函数名中的下划线转换为连字符：

```python
@task(name="all")  # 显式指定 CLI 名称，避免与 Python 内置 all 冲突
def all_(c):
    pass

@task  # 自动映射为 watch-docs
def watch_docs(c):
    pass
```

### 默认任务

使用 `default=True` 标记默认任务：

```python
@task(default=True)
def build(c):
    """默认任务"""
    pass

# inv docs 等价于 inv docs.build
```

## 典型组合范例

以下是一个综合了各种导入方式的典型 `tasks.py`：

```python
from invoke import Collection
from invocations.docs import ns as docs_ns   # 有预配置 ns 的模块
from invocations.ci import ns as ci_ns       # 有预配置 ns 的模块
from invocations import checks               # 无 ns 的模块（自动收集 @task）
from invocations.packaging import release    # packaging 子包的 release 子模块
from invocations.pytest import test, coverage  # 直接导入单个任务函数

@task
def all_checks(c):
    """运行所有检查和测试"""
    c.config.run.echo = True
    checks.blacken(c, check=True)
    checks.lint(c)
    test(c)

ns = Collection(
    all_checks,
    checks,              # 子命名空间: checks.blacken, checks.lint, checks.all
    docs_ns,             # 子命名空间: docs.build, docs.clean, docs.browse 等
    ci_ns,               # 子命名空间: ci.make-sudouser, ci.sudo-run 等
    release,             # 子命名空间: release.status, release 等
    test,                # 根命名空间: test
    coverage,            # 根命名空间: coverage
)
ns.configure({
    "packaging": {"wheel": True, "changelog_file": "CHANGELOG.rst"},
    "blacken": {"folders": ["src", "tests"], "line_length": 88},
    "sphinx": {"source": "docs", "target": "docs/_build"},
    "run": {"echo": True},
})
```

注意几个要点：
1. **有 ns 的模块**（docs/ci）通过 `from invocations.xxx import ns as xxx_ns` 导入，获得预配置的 Collection
2. **无 ns 的模块**（checks）通过 `from invocations import checks` 直接导入模块，Collection 构造函数自动从中收集 @task 函数
3. **packaging 子包**通过 `from invocations.packaging import release` 导入 release 子模块（模块自动收集）
4. **单个任务函数**（test/coverage）直接导入后在根命名空间可用
5. 自定义任务（all_checks）与 invocations 任务混合使用
6. 通过 `ns.configure()` 一次性覆盖所有模块的默认配置

## 组合检查清单

- [ ] 每个导入的任务/Collection 确实需要（不要导入不用的模块）
- [ ] 配置覆盖使用正确的配置键路径（如 `blacken.folders`、`sphinx.source`）
- [ ] 自定义任务使用工具函数（confirm/tmpdir/in_ci/watch）而非重复造轮子
- [ ] 命名冲突通过重命名或子命名空间解决
- [ ] 默认任务（`default=True`）只设置一个 per-Collection
- [ ] 在跨 Collection 调用时使用 Context.clone() 隔离配置

## 相关概念

- [快速上手](01-getting-started.md)
- [基础使用示例](../examples/basic-usage.md)
- [Invocations 简介](00-introduction.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
