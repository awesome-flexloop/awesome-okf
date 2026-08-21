---
type: Example
title: 文件监控自动测试
description: 使用 watch 模块实现代码/测试文件变化时自动运行测试，打造 TDD 反馈循环
tags: [invocations, example, watch, watchdog, tdd, auto-test]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 文件监控自动测试

本示例展示如何使用 Invocations 的 `watch` 模块实现文件变化时自动运行测试，打造快速 TDD（测试驱动开发）反馈循环。

## 前置条件

```bash
pip install watchdog pytest
```

## 基础版本：使用 testing.watch_tests

如果你使用 Spec/Nose 风格的测试，`invocations.testing` 模块内置了 `watch_tests` 任务：

```python
from invoke import Collection
from invocations.testing import watch_tests, test

ns = Collection(watch_tests, test)
ns.configure({
    "tests": {
        "package": "myproject",
    },
})
```

```bash
inv watch-tests
```

这会：
1. 首次运行所有测试（即使失败也不退出，`warn=True`）
2. 监控 `./tests/` 和 `./myproject/` 目录
3. 文件变化时自动重跑测试

## Pytest 版本：自定义 watch 任务

对于 pytest 用户，需要自定义 watch 任务（参考 testing.py 的实现模式）：

```python
from invoke import task, Collection
from invocations.watch import watch
from invocations.pytest import test as pytest_test

@task
def watch_test(c, module=None, k=None, opts=""):
    """监控文件变化，自动运行 pytest"""
    package = c.config.get("tests", {}).get("package", "")
    patterns = [r"\./tests/"]
    if package:
        patterns.append(rf"\./{package}/")
    ignore = [r".*/\..*\.swp", r".*/__pycache__/.*", r".*/\.pytest_cache/.*"]
    
    # 首次运行（不因为测试失败退出）
    c.config.run.warn = True
    kwargs = {"module": module, "k": k, "opts": opts}
    pytest_test(c, **kwargs)
    
    # 进入监控循环
    watch(c, pytest_test, patterns, ignore, **kwargs)

@task
def watch_coverage(c):
    """监控文件变化，自动运行覆盖率测试"""
    from invocations.pytest import coverage
    package = c.config.get("tests", {}).get("package", "")
    patterns = [r"\./tests/"]
    if package:
        patterns.append(rf"\./{package}/")
    ignore = [r".*/\..*\.swp", r".*/__pycache__/.*"]
    c.config.run.warn = True
    coverage(c, report="term")
    watch(c, coverage, patterns, ignore, report="term")

ns = Collection(watch_test, watch_coverage, pytest_test)
ns.configure({
    "tests": {"package": "myproject"},
})
```

使用方式：

```bash
# 自动运行所有测试
inv watch-test

# 只监控特定模块
inv watch-test --module=core

# 只运行匹配的测试
inv watch-test -k "test_login"

# 自动运行覆盖率
inv watch-coverage
```

## 高级版本：多任务监控

`make_handler` + `observe` 模式支持同时监控多组路径触发不同任务：

```python
from invoke import task, Collection, Context
from invocations.watch import make_handler, observe
from invocations.docs import docs, www
from invocations.pytest import test

@task
def watch_all(c):
    """监控所有变化：源码→测试，文档→构建"""
    package = c.config.get("tests", {}).get("package", "")
    
    # 测试 handler：源码或测试变化时运行测试
    test_patterns = [r"\./tests/"]
    if package:
        test_patterns.append(rf"\./{package}/")
    test_ignore = [r".*/\..*\.swp", r".*/__pycache__/.*", r".*/_build/.*"]
    test_handler = make_handler(c, test, test_patterns, test_ignore)
    
    # WWW 文档 handler：README 或 www 目录变化
    www_c = Context(config=c.config.clone())
    www_c.update(**www.configuration())
    www_patterns = [r"\./README\.rst", r"\./sites/www/"]
    www_ignore = [r".*/\..*\.swp", r"\./sites/www/_build/.*"]
    www_handler = make_handler(www_c, www["build"], www_patterns, www_ignore)
    
    # API 文档 handler：docs 目录或源码变化
    docs_c = Context(config=c.config.clone())
    docs_c.update(**docs.configuration())
    docs_patterns = [r"\./sites/docs/"]
    if package:
        docs_patterns.append(rf"\./{package}/")
    docs_ignore = [r".*/\..*\.swp", r"\./sites/docs/_build/.*"]
    docs_handler = make_handler(docs_c, docs["build"], docs_patterns, docs_ignore)
    
    # 首次运行
    c.config.run.warn = True
    test(c)
    
    print("\n👀 开始监控，Ctrl-C 退出")
    print("   - 源码/测试变化 → 运行测试")
    print("   - README/www 变化 → 构建主网站")
    print("   - docs/源码变化 → 构建 API 文档")
    
    # 同时启动所有 handler
    observe(test_handler, www_handler, docs_handler)

ns = Collection(watch_all, test, docs, www)
```

## watch 模块 API 详解

### make_handler

```python
handler = make_handler(ctx, task_, regexes, ignore_regexes, *args, **kwargs)
```

| 参数 | 说明 |
|------|------|
| `ctx` | Invoke Context 对象 |
| `task_` | 要触发的任务函数 |
| `regexes` | 匹配文件路径的正则列表（匹配则触发） |
| `ignore_regexes` | 忽略路径的正则列表 |
| `*args/**kwargs` | 传递给任务函数的额外参数 |

### observe

```python
observe(*handlers)
```

启动 watchdog Observer，从当前目录递归监控所有 handler，进入无限循环直到 Ctrl-C。

### watch

```python
watch(c, task_, regexes, ignore_regexes, *args, **kwargs)
```

`make_handler` + `observe` 的便捷组合，适合单任务场景。

## 工作原理

1. `make_handler` 创建 watchdog `RegexMatchingEventHandler` 子类
2. `on_any_event` 回调在文件创建/修改/删除/移动时调用 `task_(*args, **kwargs)`
3. 回调中捕获 `BaseException` 防止任务失败中断监控
4. `observe` 启动 Observer 线程，主线程每秒 sleep 直到 KeyboardInterrupt

## 实用技巧

### 首次运行测试

```python
# 进入监控前先运行一次测试，验证当前状态
c.config.run.warn = True  # 测试失败不退出
test(c)
```

### 快速反馈（只跑相关测试）

```python
@task
def watch_fast(c):
    """只跑上次失败的测试（pytest --lf）"""
    watch(c, test, [r"\./src/", r"\./tests/"], [r".*/__pycache__/.*"], opts="--lf")
```

### 多命令触发

```python
@task
def lint_and_test(c):
    c.run("flake8 src/", warn=True)
    c.run("pytest tests/")

watch(c, lint_and_test, patterns, ignore)
```

## 注意事项

- watchdog 的 `RegexMatchingEventHandler` 使用正则匹配文件路径，路径以 `./` 开头
- `on_any_event` 会捕获所有事件类型（created/modified/deleted/moved），包括临时文件（如 vim 的 `.swp`），所以 ignore 列表很重要
- Handler 中的异常被静默捕获（`except BaseException: pass`），如果任务有 bug 不会在监控输出中看到 traceback，可以临时修改为打印异常来调试
- Observer 在后台线程运行，主线程 `time.sleep(1)` 是必要的
- 停止监控：在终端按 Ctrl-C

## 相关概念

- [工具函数与文件监控](/concepts/07-utilities-watchers.md)
- [Pytest 测试任务](/concepts/03-testing-pytest.md)
- [Sphinx 文档管理](/concepts/04-docs-sphinx.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
