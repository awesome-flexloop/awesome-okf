---
type: Concept
title: Pytest 测试任务
description: 使用 pytest 模块运行单元测试、集成测试、覆盖率测试，以及 testing 模块的 Spec/Nose 兼容与 flakiness 检测
tags: [invocations, pytest, testing, coverage, integration-tests]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# Pytest 测试任务

`invocations.pytest` 模块提供基于 [pytest](https://pytest.org/) 的测试任务，是 Invocations 中推荐使用的测试模块（将逐步替代旧的 `testing.py`）。

## 快速使用

```python
# tasks.py
from invoke import Collection
from invocations.pytest import test, integration, coverage

ns = Collection(test, integration, coverage)
```

## test：运行单元测试

```bash
# 默认运行所有测试
inv test

# 详细输出 + 彩色
inv test --verbose --color

# 运行特定模块（tests/main.py）
inv test --module=main

# 按名称筛选测试
inv test -k "test_login"

# 失败即停
inv test -x

# 不捕获输出（用于 print 调试）
inv test --capture=no

# 传递额外 pytest 选项
inv test --opts="-p no:warnings"

# 禁用警告
inv test --no-warnings
```

### test 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `verbose` | bool | True | 详细输出模式（`--verbose`） |
| `color` | bool | True | 彩色输出（`--color=yes`） |
| `capture` | str | `"sys"` | stdout/stderr 捕获模式，默认 `sys` 避免 PTY 检测问题，可设为 `no` |
| `module` | str | None | 运行 `tests/<module>.py` 指定模块 |
| `k` | str | None | 对应 `pytest -k`，按名称筛选测试 |
| `x` | bool | False | 对应 `pytest -x`，首次失败即停止 |
| `opts` | str | "" | 额外传递给 pytest 的选项 |
| `pty` | bool | True | 是否使用伪终端执行 |
| `warnings` | bool | True | False 时添加 `--disable-warnings`（CLI 使用 `--no-warnings`） |

> **为什么默认 `capture="sys"`？** pytest 默认的 `fd` 捕获模式在子进程检测 PTY 状态时容易出问题，`sys` 模式更稳定。

## integration：集成测试

`integration` 任务运行集成测试套件（`integration/` 目录），参数与 `test` 基本相同：

```bash
# 运行所有集成测试
inv integration

# 运行特定集成测试模块
inv integration --module=db

# 失败即停
inv integration -x
```

`integration` 内部在 opts 中追加 `integration/` 路径，然后调用 `test()`。集成测试通常比单元测试慢。

## coverage：覆盖率测试

`coverage` 任务使用 [pytest-cov](https://pytest-cov.readthedocs.io/) 插件运行测试并收集覆盖率数据：

```bash
# 终端覆盖率报告
inv coverage

# HTML 报告（自动在浏览器中打开）
inv coverage --report=html

# 生成 XML 并上传到 Codecov
inv coverage --codecov

# 传递额外选项
inv coverage --opts="-k 'not slow'"

# 使用自定义测试任务
inv coverage --tester=my_custom_test_task

# 多轮追加覆盖率（如先单元测试再集成测试）
inv coverage --additional-testers=integration
```

### coverage 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `report` | str | `"term"` | 覆盖率报告类型（`term`/`html`/`xml` 等），`html` 时自动打开浏览器 |
| `opts` | str | "" | 额外传递给 pytest 的选项 |
| `tester` | task | None | 指定测试任务对象，默认使用本模块的 `test` |
| `codecov` | bool | False | 是否生成 XML 报告并上传到 Codecov（需要 `codecov` 工具） |
| `additional_testers` | list | None | 追加运行的测试任务列表，自动使用 `--cov-append` 模式 |

coverage 内部使用 `--cov --no-cov-on-fail --cov-report=<report>` 参数组合。

## testing.py：旧版 Spec/Nose 测试

`invocations.testing` 模块是较旧的测试任务集，面向 [Spec](https://github.com/bitprophet/spec)（BDD 风格的 Nose 插件）测试框架：

| 任务 | 说明 |
|------|------|
| `test` | 运行 Spec/Nose 测试套件（默认 runner=`spec`，自动添加 `--with-timing`） |
| `integration` | 运行集成测试 |
| `watch_tests` | 监控源码和测试文件变化，自动重跑测试（依赖 watchdog） |
| `coverage` | 使用 coverage.py 运行测试并生成 HTML 报告 |
| `count_errors` | 多次运行命令统计失败率（flakiness 检测），使用 tqdm 进度条 |

### count_errors：Flakiness 检测

`count_errors` 对于检测不稳定的测试（flaky tests）特别有用：

```bash
# 运行10次，统计失败率
inv count-errors --command="inv test --module=mymodule"

# 运行100次
inv count-errors --command="inv test" --trials=100

# 首次失败即停，显示错误输出
inv count-errors --command="inv test" --fail-fast --verbose

# 显示失败时的 stderr
inv count-errors --command="inv test" --trials=50 --verbose
```

输出示例：

```
3/10 trials failed
Stats: min=2s, mean=15s, mode=12s, max=30s
First failure occurred after 2 successes
```

### watch_tests：文件监控自动测试

`watch_tests` 利用文件监控在代码或测试变化时自动重跑测试：

```bash
# 监控所有源码和测试
inv watch-tests

# 只监控特定模块
inv watch-tests --module=mymodule
```

`watch_tests` 读取 `tests.package` 配置确定要监控的源码目录，默认监控 `./tests/` 和配置的包目录。首次运行时设置 `warn=True` 避免初始失败导致退出。

## 配置示例

```python
ns.configure({
    "tests": {
        "package": "myproject",  # 要监控的源码包名
        "logformat": "%(asctime)s %(levelname)s %(message)s",
    },
})
```

## 相关概念

- [快速上手](/concepts/01-getting-started.md)
- [代码检查与格式化](/concepts/02-checks-formatting.md)
- [工具函数与文件监控](/concepts/07-utilities-watchers.md)
- [组合模式：组装自己的任务集合](/concepts/10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
