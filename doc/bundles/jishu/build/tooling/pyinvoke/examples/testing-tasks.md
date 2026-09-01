---
type: Example
title: 使用 MockContext 测试任务
description: 使用 MockContext 对 invoke 任务进行单元测试，验证命令调用和参数
tags: [pyinvoke, testing, MockContext, Result, unit-test, pytest, mock, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-src
    resource: /references/pyinvoke-source.md
    title: "PyInvoke 源码"
---

# 使用 MockContext 测试任务

Invoke 提供了 `MockContext` 类用于对任务进行单元测试。`MockContext` 是 `Context` 的子类，它不会真正执行 shell 命令，而是返回预设的 `Result` 对象。同时，`MockContext` 的 `run` 和 `sudo` 方法被 `unittest.mock.Mock` 包装，可以断言它们是否被以预期的命令和参数调用。[^pyinvoke-src]

## 1. 基础测试模式

### 待测试的任务

首先定义一些需要测试的任务：

```python
# tasks.py
from invoke import task


@task
def build(c, clean=False):
    """构建项目。"""
    if clean:
        c.run("rm -rf dist/")
    c.run("echo '编译源代码'")
    c.run("echo '打包到 dist/'")


@task
def deploy(c, env="staging"):
    """部署到指定环境。"""
    c.run(f"echo '部署到 {env} 环境'")
    if env == "production":
        c.run("echo '发送生产部署通知'")


@task
def test(c, coverage=False):
    """运行测试。"""
    result = c.run("echo '运行单元测试'", hide=True)
    if coverage:
        c.run("echo '生成覆盖率报告'")
    return result.stdout.strip()
```

### 使用 MockContext + pytest 测试

```python
# test_tasks.py
import pytest
from invoke import MockContext, Result
from tasks import build, deploy, test


class TestBuildTask:
    def test_build_without_clean(self):
        """测试 build 任务（不清理）。"""
        # 创建 MockContext，run 返回一个成功的 Result
        ctx = MockContext(run=Result("build ok"))

        # 执行任务
        build(ctx)

        # 验证 run 被正确调用：没有调用 rm -rf
        # MockContext.run 是 Mock 对象，可以用 assert_called/assert_any_call 等断言
        assert ctx.run.call_count == 2
        ctx.run.assert_any_call("echo '编译源代码'")
        ctx.run.assert_any_call("echo '打包到 dist/'")
        # 确认没有调用清理命令
        for call_args in ctx.run.call_args_list:
            assert "rm -rf" not in call_args[0][0]

    def test_build_with_clean(self):
        """测试 build 任务（带清理）。"""
        ctx = MockContext(run=Result("build ok"))

        build(ctx, clean=True)

        # 应该调用了3次 run：清理 + 编译 + 打包
        assert ctx.run.call_count == 3
        ctx.run.assert_any_call("rm -rf dist/")
        ctx.run.assert_any_call("echo '编译源代码'")
        ctx.run.assert_any_call("echo '打包到 dist/'")


class TestDeployTask:
    def test_deploy_to_staging(self):
        """测试部署到预发布环境。"""
        ctx = MockContext(run=Result("deployed"))

        deploy(ctx)  # 默认 env="staging"

        assert ctx.run.call_count == 1
        ctx.run.assert_called_once_with("echo '部署到 staging 环境'")

    def test_deploy_to_production(self):
        """测试部署到生产环境（会发送通知）。"""
        ctx = MockContext(run=Result("deployed"))

        deploy(ctx, env="production")

        assert ctx.run.call_count == 2
        ctx.run.assert_any_call("echo '部署到 production 环境'")
        ctx.run.assert_any_call("echo '发送生产部署通知'")


class TestTestTask:
    def test_test_without_coverage(self):
        """测试运行测试（无覆盖率）。"""
        # 为 run 预设返回值：stdout 包含 "运行单元测试"
        ctx = MockContext(run=Result("运行单元测试\n"))

        output = test(ctx)

        ctx.run.assert_called_once_with("echo '运行单元测试'", hide=True)
        assert output == "运行单元测试"

    def test_test_with_coverage(self):
        """测试运行测试（带覆盖率）。"""
        ctx = MockContext(run=Result("运行单元测试\n"))

        test(ctx, coverage=True)

        assert ctx.run.call_count == 2
        ctx.run.assert_any_call("echo '运行单元测试'", hide=True)
        ctx.run.assert_any_call("echo '生成覆盖率报告'")
```

运行测试：

```bash
pytest test_tasks.py -v
```

## 2. 使用字典匹配不同命令的返回值

当任务中会调用多个不同的命令时，可以使用字典将命令字符串映射到对应的 `Result` 对象，实现"命令 → 返回值"的精确匹配：

```python
# test_tasks.py
from invoke import MockContext, Result
from tasks import build


def test_build_with_dict_matching():
    """使用字典为不同命令设置不同的返回值。"""
    ctx = MockContext(run={
        "echo '编译源代码'": Result("编译成功\n"),
        "echo '打包到 dist/'": Result("打包完成\n"),
    })

    build(ctx)

    # 编译命令被调用
    ctx.run.assert_any_call("echo '编译源代码'")
    # 打包命令被调用
    ctx.run.assert_any_call("echo '打包到 dist/'")
```

### 正则表达式匹配命令

字典的 key 也可以是编译后的正则表达式对象（`re.Pattern`），用于模糊匹配一类命令：

```python
# test_tasks.py
import re
from invoke import MockContext, Result
from tasks import deploy


def test_deploy_regex_matching():
    """使用正则表达式匹配 deploy 命令。"""
    ctx = MockContext(run={
        # 匹配任意 "部署到 xxx 环境" 命令
        re.compile(r"echo '部署到 .+ 环境'"): Result("deployed\n"),
        "echo '发送生产部署通知'": Result("notification sent\n"),
    })

    deploy(ctx, env="production")

    # 两个命令都被调用
    assert ctx.run.call_count == 2
```

## 3. 多次调用返回不同结果（repeat=False）

默认情况下，`MockContext` 的 `repeat=True`，同一个预设结果会反复返回。如果需要模拟多次调用返回不同结果（如第一次调用返回某个值，第二次返回另一个值），设置 `repeat=False` 并传入一个可迭代对象：

```python
# tasks.py（待测试的任务）
from invoke import task


@task
def check_status(c):
    """检查服务状态——重试一次。"""
    result = c.run("curl -s http://localhost/health", warn=True)
    if result.failed:
        # 第一次失败，重试
        result = c.run("curl -s http://localhost/health", warn=True)
        if result.failed:
            print("❌ 服务不可用")
            return False
    print("✅ 服务正常")
    return True
```

```python
# test_tasks.py
from invoke import MockContext, Result
from tasks import check_status


def test_check_status_first_fail_then_success():
    """模拟第一次检查失败，第二次重试成功。"""
    # repeat=False：结果列表按顺序消耗，用完后抛 NotImplementedError
    ctx = MockContext(
        run=[
            Result(exited=1),   # 第一次调用：失败（exit code 1）
            Result(exited=0),   # 第二次调用：成功（exit code 0）
        ],
        repeat=False,
    )

    result = check_status(ctx)

    assert result is True
    assert ctx.run.call_count == 2


def test_check_status_both_fail():
    """模拟两次检查都失败。"""
    ctx = MockContext(
        run=[Result(exited=1), Result(exited=1)],
        repeat=False,
    )

    result = check_status(ctx)

    assert result is False
    assert ctx.run.call_count == 2


def test_check_status_repeat_true_default():
    """默认 repeat=True：同一结果反复返回（模拟始终成功）。"""
    ctx = MockContext(run=Result(exited=0))

    result = check_status(ctx)

    assert result is True
    # 只调用了一次 run（第一次就成功了）
    ctx.run.assert_called_once()
```

关键要点：

- `repeat=True`（默认值）：单个 `Result` 会被无限次重复返回；列表结果会通过 `itertools.cycle` 循环返回。
- `repeat=False`：结果按顺序消耗，消耗完后再调用 `c.run()` 会抛出 `NotImplementedError`，适合精确控制调用次数的测试场景。

## 4. 测试 sudo 命令

`MockContext` 同样支持 `sudo()` 方法的 mock，用法与 `run` 完全一致：

```python
# tasks.py
from invoke import task


@task
def install_package(c, package_name):
    """使用 sudo 安装软件包。"""
    c.sudo(f"apt-get install -y {package_name}")
    c.run(f"echo '{package_name} 安装完成'")


@task
def restart_and_check(c):
    """重启服务并检查状态。"""
    c.sudo("systemctl restart myapp")
    result = c.run("systemctl is-active myapp", hide=True)
    return result.stdout.strip() == "active"
```

```python
# test_tasks.py
from invoke import MockContext, Result
from tasks import install_package, restart_and_check


def test_install_package():
    """测试 sudo 安装软件包。"""
    ctx = MockContext(
        run=Result("安装完成\n"),
        sudo=Result("Reading package lists... Done\n"),
    )

    install_package(ctx, "nginx")

    # 验证 sudo 被正确调用
    ctx.sudo.assert_called_once_with("apt-get install -y nginx")
    # 验证 run 也被调用
    ctx.run.assert_called_once_with("echo 'nginx 安装完成'")


def test_restart_and_check_active():
    """测试服务重启后状态正常。"""
    ctx = MockContext(
        run=Result("active\n"),
        sudo=Result(""),
    )

    assert restart_and_check(ctx) is True
    ctx.sudo.assert_called_once_with("systemctl restart myapp")
    ctx.run.assert_called_once_with("systemctl is-active myapp", hide=True)


def test_restart_and_check_inactive():
    """测试服务重启后仍不正常。"""
    ctx = MockContext(
        run=Result("inactive\n", exited=3),
        sudo=Result(""),
    )

    assert restart_and_check(ctx) is False
```

## 5. 测试使用 Context 管理器的任务

如果任务中使用了 `c.cd()` 或 `c.prefix()` 上下文管理器，`MockContext` 也能正确处理——因为它继承自 `Context`，这些上下文管理器会正常工作，只是 `run()` 方法不会真正执行命令：

```python
# tasks.py
from invoke import task


@task
def build_in_venv(c):
    """在虚拟环境中构建项目。"""
    with c.prefix("source venv/bin/activate"):
        c.run("pip install -e .")
        with c.cd("docs"):
            c.run("make html")


@task
def deploy_with_config(c, config_path="config/prod.yaml"):
    """带配置部署。"""
    c.run(f"deploy --config {config_path}", echo=True)
```

```python
# test_tasks.py
from invoke import MockContext, Result
from tasks import build_in_venv, deploy_with_config


def test_build_in_venv():
    """测试在虚拟环境中构建（验证命令被正确调用）。"""
    ctx = MockContext(run=Result("ok"))

    build_in_venv(ctx)

    # 验证调用了两个 run 命令
    assert ctx.run.call_count == 2
    # 注意：MockContext 会模拟 prefix/cd 的效果，但不会在命令中真实拼接前缀
    # 因为 run 是 Mock 对象，它接收到的命令是原始命令（未加前缀）
    # 如需测试前缀拼接逻辑，可以用真实 Context 或集成测试
    ctx.run.assert_any_call("pip install -e .")
    ctx.run.assert_any_call("make html")


def test_deploy_with_default_config():
    """测试使用默认配置部署。"""
    ctx = MockContext(run=Result("deployed"))

    deploy_with_config(ctx)

    ctx.run.assert_called_once_with(
        "deploy --config config/prod.yaml", echo=True
    )


def test_deploy_with_custom_config():
    """测试使用自定义配置部署。"""
    ctx = MockContext(run=Result("deployed"))

    deploy_with_config(ctx, config_path="config/staging.yaml")

    ctx.run.assert_called_once_with(
        "deploy --config config/staging.yaml", echo=True
    )
```

## 6. 测试 c.run 的关键字参数

`MockContext.run` 是 `unittest.mock.Mock` 对象，可以通过 `call_args` 检查调用时传入的关键字参数：

```python
# test_tasks.py
from invoke import MockContext, Result
from tasks import test as test_task


def test_run_kwargs():
    """验证 c.run 的关键字参数（如 hide、echo、warn 等）。"""
    ctx = MockContext(run=Result("test output\n"))

    test_task(ctx, coverage=True)

    # 检查第一次调用的关键字参数
    first_call = ctx.run.call_args_list[0]
    assert first_call[0][0] == "echo '运行单元测试'"  # 位置参数：命令字符串
    assert first_call[1].get("hide") is True          # 关键字参数：hide=True

    # 检查第二次调用
    second_call = ctx.run.call_args_list[1]
    assert second_call[0][0] == "echo '生成覆盖率报告'"
```

## 7. 使用 set_result_for 动态设置返回值

在测试过程中，如果需要在 `MockContext` 创建后修改预设返回值，可以使用 `set_result_for()` 方法：

```python
# test_tasks.py
import pytest
from invoke import MockContext, Result


def test_set_result_for_after_creation():
    """创建 MockContext 后动态添加命令返回值。"""
    # 初始化为空字典
    ctx = MockContext(run={})

    # 此时调用未预设的命令会抛 NotImplementedError
    with pytest.raises(NotImplementedError):
        ctx.run("some command")

    # 动态添加返回值
    ctx.set_result_for("run", "some command", Result("dynamic output\n"))

    # 现在可以正常调用
    result = ctx.run("some command")
    assert result.stdout == "dynamic output\n"
```

## 相关概念

* [Context 对象（§3）](../concepts/03-context-object.md)
* [Task 基础（§2）](../concepts/02-task-basics.md)
* [Runner 与命令执行（§6）](../concepts/06-runners.md)
* [高级模式（§11）](../concepts/11-advanced-patterns.md)

[^pyinvoke-src]: PyInvoke 源码，见本 bundle 信源登记 [references/pyinvoke-source.md](../references/pyinvoke-source.md)。
