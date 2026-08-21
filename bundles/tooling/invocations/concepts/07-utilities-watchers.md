---
type: Concept
title: 工具函数与文件监控
description: console.confirm 交互确认、util.tmpdir 临时目录、environment.in_ci 环境检测、watch 模块文件监控自动任务
tags: [invocations, utilities, confirm, tmpdir, watchdog, file-watcher]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 工具函数与文件监控

Invocations 提供了若干跨模块复用的纯工具函数（不依赖 @task 装饰器），可在任意 Python 代码和自定义任务中使用。

## console.confirm：交互式确认

`invocations.console.confirm()` 提供标准的 Y/n 命令行确认提示：

```python
from invocations.console import confirm

if confirm("是否继续发布?"):
    print("继续执行...")
else:
    print("已取消")

# 默认选 No
if confirm("是否删除所有构建产物?", assume_yes=False):
    c.run("rm -rf build/")
```

### 函数签名

```python
def confirm(question: str, assume_yes: bool = True) -> bool
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `question` | str | 必填 | 提示问题（语法完整的句子，不加问号） |
| `assume_yes` | bool | True | 回车时默认选 Yes（显示 `[Y/n]`）；False 时默认选 No（显示 `[y/N]`） |

### 行为特征

- 自动追加 `[Y/n]` 或 `[y/N]` 后缀
- 用户输入不区分大小写（`y`/`Y`/`yes`/`YES` 都算 Yes）
- 输入无效时循环重新提示，打印错误信息到 stderr
- 返回 Python `bool`

```
是否继续发布? [Y/n] maybe
I didn't understand you. Please specify '(y)es' or '(n)o'.
是否继续发布? [Y/n] y
```

> **使用场景**：release.prepare 中在执行修改操作前用 `confirm()` 请求用户确认，避免误操作。

## util.tmpdir：临时目录上下文管理器

`invocations.util.tmpdir()` 是一个安全的临时目录上下文管理器：

```python
from invocations.util import tmpdir
import os

with tmpdir() as tmp:
    # 在临时目录中工作
    os.chdir(tmp)
    # 执行操作...
    # 退出 with 块时自动清理（rmtree）

# 跳过清理（用于调试）
with tmpdir(skip_cleanup=True) as tmp:
    print(f"临时目录: {tmp}")
    # 退出后不会删除，可手动检查

# 指定显式路径
with tmpdir(explicit="/tmp/my-build") as tmp:
    # 使用指定目录而非 mkdtemp
    ...
```

### 函数签名

```python
@contextmanager
def tmpdir(skip_cleanup: bool = False, explicit: str = None) -> Iterator[str]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `skip_cleanup` | bool | False | 退出时是否跳过清理 |
| `explicit` | str | None | 使用指定路径而非 `tempfile.mkdtemp()` 创建 |

内部使用 `tempfile.mkdtemp()` 创建临时目录，退出时通过 `shutil.rmtree()` 清理（无论是否发生异常）。`tmpdir` 被 `packaging.release`（publish 中的临时构建目录）和 `packaging.vendorize` 共同使用。

## environment.in_ci()：CI 环境检测

```python
from invocations.environment import in_ci

if in_ci():
    # CI 环境中的特殊行为
    c.config.run.echo = False
else:
    # 本地开发环境
    c.config.run.echo = True
```

`in_ci()` 检查 `CIRCLECI` 和 `TRAVIS` 环境变量是否存在且非空。release.push 在 CI 环境中自动切换到 dry 模式避免误推送。

## watch 模块：文件监控

`invocations.watch` 模块基于 [watchdog](https://python-watchdog.readthedocs.io/) 提供文件变化监控能力，支持在文件变化时自动触发任务。需要先安装 watchdog：

```bash
pip install watchdog
```

### 三层 API

watch 模块提供三层 API，从低层到高层：

#### 1. make_handler：创建事件处理器

```python
from invocations.watch import make_handler

handler = make_handler(
    ctx=c,                           # Invoke Context 对象
    task_=my_task_function,          # 要触发的任务函数
    regexes=[r"\./src/", r"\./tests/"],  # 监控的文件路径正则
    ignore_regexes=[r".*/\..*\.swp", r".*/_build/"],  # 忽略的路径正则
    # 额外的 *args 和 **kwargs 会传递给 task_
)
```

创建的 `Handler` 类继承自 watchdog 的 `RegexMatchingEventHandler`，在任何文件事件（创建/修改/删除/移动）时调用 `task_(*args, **kwargs)`。

> **容错设计**：Handler 的 `on_any_event` 捕获所有 `BaseException`（包括 Exception 的子类），防止单次任务执行失败导致监控循环终止。

#### 2. observe：启动监控循环

```python
from invocations.watch import observe

observe(handler1, handler2, ...)  # 可传入多个 handler
```

`observe()` 创建 watchdog `Observer`，从当前目录（`.`）递归调度所有 handler，启动后进入无限循环（`time.sleep(1)`），直到收到 `KeyboardInterrupt`（Ctrl-C）时停止 observer 并 join。

#### 3. watch：便捷函数

```python
from invocations.watch import watch

watch(c, my_task, [r"\./src/"], [r".*/\..*\.swp"], module="main", opts="-v")
```

`watch()` 是 `make_handler` + `observe` 的便捷组合，适合单任务单 handler 的简单场景。

### 在自定义任务中使用 watch

```python
from invoke import task
from invocations.watch import watch
from invocations.pytest import test

@task
def watch_tests(c, module=None):
    """监控源码和测试变化，自动运行测试"""
    patterns = [r"\./tests/"]
    package = c.config.get("tests", {}).get("package")
    if package:
        patterns.append(rf"\./{package}/")
    watch(c, test, patterns, [r".*/\..*\.swp"], module=module)
```

### 实际使用案例

- `invocations.docs.watch_docs`：监控 README 和 docs/sites 目录，自动重建 Sphinx 文档
- `invocations.testing.watch_tests`：监控源码和测试目录，自动运行测试
- 两个模块都使用 `make_handler` 创建独立 handler，通过 `observe()` 同时监控多组路径

## 跨模块复用模式

Invocations 的工具函数体现了一个重要设计模式：**工具函数与任务函数分离**。纯工具函数（confirm/tmpdir/in_ci/make_handler/observe）不依赖 Invoke 的 @task 装饰器和 Context，可以：

1. 在任意 Python 代码中使用（不限于 Invoke 任务）
2. 在多个任务模块间共享（如 tmpdir 被 release 和 vendorize 同时使用）
3. 方便单元测试（不需要模拟 Context）

## 相关概念

- [Sphinx 文档管理](/concepts/04-docs-sphinx.md)（watch_docs 使用 watch）
- [Pytest 测试任务](/concepts/03-testing-pytest.md)（watch_tests 使用 watch）
- [文件监控自动测试示例](/examples/file-watch-auto-test.md)
- [组合模式：组装自己的任务集合](/concepts/10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
