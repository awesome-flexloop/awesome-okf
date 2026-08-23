---
okf_version: "0.2"
type: reference
title: 插件钩子规范 (hookspec)
sources:
  - conda/plugins/hookspec.py
---

# 插件钩子规范 (hookspec)

Conda 插件系统基于 [Pluggy](https://pluggy.readthedocs.io/) 框架构建。`hookspec.py` 定义了所有插件扩展点的"钩子规范"（hookspec）：`_hookspec` 装饰器标记钩子规范方法，`hookimpl` 装饰器标记插件方的钩子实现，`CondaSpecs` 类汇集所有支持的钩子规范。每个钩子方法均包含使用示例，是插件开发者的权威参考。

```python
# conda/plugins/hookspec.py

from __future__ import annotations
from typing import TYPE_CHECKING
import pluggy
from ..base.constants import APP_NAME

if TYPE_CHECKING:
    from collections.abc import Iterable
    from .. import CondaError
    from .types import (
        CondaAuthHandler, CondaEnvironmentExporter, CondaEnvironmentSpecifier,
        CondaErrorHint, CondaExceptionObserver, CondaHealthCheck,
        CondaPackageExtractor, CondaPostCommand, CondaPostSolve,
        CondaPostTransactionAction, CondaPreCommand, CondaPrefixDataLoader,
        CondaPreSolve, CondaPreTransactionAction, CondaReporterBackend,
        CondaRequestHeader, CondaSetting, CondaSolver, CondaSubcommand,
        CondaVirtualPackage,
    )

_hookspec = pluggy.HookspecMarker(APP_NAME)
"""Decorator to mark conda plugin hook specifications."""

hookimpl = pluggy.HookimplMarker(APP_NAME)
"""Decorator to mark plugin hook implementations."""


class CondaSpecs:
    """Collection of all supported conda plugin hookspecs."""

    @_hookspec
    def conda_solvers(self) -> Iterable[CondaSolver]:
        """Register solvers in conda.

        **Example:**

        .. code-block:: python

            import logging
            from conda import plugins
            from conda.core import solve

            log = logging.getLogger(__name__)

            class VerboseSolver(solve.Solver):
                def solve_final_state(self, *args, **kwargs):
                    log.info("My verbose solver!")
                    return super().solve_final_state(*args, **kwargs)

            @plugins.hookimpl
            def conda_solvers():
                yield plugins.types.CondaSolver(
                    name="verbose-classic",
                    backend=VerboseSolver,
                )

        Returns:
            An iterable of solver entries.
        """
        yield from ()

    @_hookspec
    def conda_subcommands(self) -> Iterable[CondaSubcommand]:
        """Register external subcommands in conda.

        **Example:**

        .. code-block:: python

            from conda import plugins

            def example_command(args):
                print("This is an example command!")

            @plugins.hookimpl
            def conda_subcommands():
                yield plugins.types.CondaSubcommand(
                    name="example",
                    aliases=("example-alias",),
                    summary="example command",
                    action=example_command,
                )

        Returns:
            An iterable of subcommand entries.
        """
        yield from ()
```

**关键设计**：
- **Pluggy 双标记机制**：`_hookspec`（规范方）和 `hookimpl`（实现方）是 Pluggy 的核心机制——`_hookspec` 在 `CondaSpecs` 类上标记"这里可以被插件扩展"，`hookimpl` 在插件模块上标记"这里实现了某个扩展点"，Pluggy 在运行时通过名称匹配将两者连接
- **生成器返回协议**：所有钩子方法均以 `yield from ()` 作为默认实现（空生成器），插件通过 `yield CondaSolver(...)`/`yield CondaSubcommand(...)` 等方式注册一个或多个条目，支持一个插件注册多个同类型扩展点
- **类型安全的 TYPE_CHECKING 导入**：插件类型（`CondaSolver`、`CondaSubcommand` 等）仅在 `TYPE_CHECKING` 块中导入，避免运行时循环依赖，同时为 IDE 和类型检查器提供完整类型信息
- **APP_NAME 命名空间**：`HookspecMarker(APP_NAME)` 和 `HookimplMarker(APP_NAME)` 使用 conda 的应用名作为命名空间隔离标记，确保与其他使用 Pluggy 的项目（如 pytest）互不干扰
- **内嵌文档示例**：每个 hookspec 方法的 docstring 包含完整的使用示例代码，插件开发者无需查阅外部文档即可按示例编写插件
