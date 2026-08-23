---
okf_version: "0.2"
type: "example"
title: "自定义求解器插件"
sources: ["conda/plugins/manager.py", "conda/plugins/hookspec.py"]
---

# 自定义求解器插件

conda 的插件系统基于 pluggy 框架，允许开发者通过 `@hookimpl` 装饰器注册自定义求解器后端。当用户通过 `--solver` 参数或 `CONDA_SOLVER` 环境变量选择求解器时，conda 会从插件管理器中查找对应的后端类并实例化。本示例展示如何创建一个自定义求解器插件，包括后端类实现、钩子注册和包配置。

相关概念：[插件系统](../concepts/15-plugin-system.md)、[求解器与依赖解析](../concepts/09-solver-and-resolve.md)。

## 完整示例

```python
"""
自定义求解器插件示例。

引用事实：[F-068] CondaPluginManager 继承 pluggy.PluginManager，使用 importlib.metadata 发现插件
         [F-069] 使用 pluggy.HookspecMarker 定义 _hookspec 和 hookimpl 装饰器
         [F-070] conda_solvers 是内置插件钩子类型之一
         [F-071] 内置 classic 求解器插件在 plugins/solvers.py 中注册
"""

# ============================================================
# 文件1: my_solver_plugin.py — 插件模块
# ============================================================

"""
自定义求解器插件实现。

安装后，可通过 `conda install --solver my-logging-solver <package>` 使用。
"""

import logging
from conda import plugins
from conda.core.solve import Solver as ClassicSolver
from conda.models.match_spec import MatchSpec

log = logging.getLogger(__name__)


class LoggingSolver(ClassicSolver):
    """
    一个在 classic 求解器基础上增加日志输出的自定义求解器。

    [F-069] 自定义求解器后端应继承自 conda.core.solve.Solver（即 classic 求解器），
    也可以直接继承 BaseSolver 实现完全自定义的 SAT 求解逻辑。

    构造函数签名必须与 BaseSolver.__init__ 兼容：
        (prefix, channels, subdirs=(), specs_to_add=(), specs_to_remove=(),
         repodata_fn=REPODATA_FN, command=NULL)
    """

    def solve_final_state(self, *args, **kwargs):
        """
        求解最终环境状态。在求解前后输出日志。

        [F-044] BaseSolver 三个公开方法：solve_final_state, solve_for_diff, solve_for_transaction
        重写时可在调用 super() 前后插入自定义逻辑。
        """
        log.info("[LoggingSolver] 开始求解环境: %s", self.prefix)
        log.info("[LoggingSolver] 待添加包: %s", [str(s) for s in self.specs_to_add])
        log.info("[LoggingSolver] 待移除包: %s", [str(s) for s in self.specs_to_remove])

        # 调用父类（classic）求解逻辑
        result = super().solve_final_state(*args, **kwargs)

        log.info("[LoggingSolver] 求解完成，共 %d 个包", len(result))
        for prec in result[:10]:
            log.debug("  - %s %s %s", prec.name, prec.version, prec.build)

        return result

    def solve_for_diff(self, *args, **kwargs):
        """求解环境差异（增删包列表）。"""
        log.info("[LoggingSolver] 开始计算环境差异")
        unlink_precs, link_precs = super().solve_for_diff(*args, **kwargs)
        log.info(
            "[LoggingSolver] 差异计算完成: 移除 %d 个包, 安装 %d 个包",
            len(unlink_precs),
            len(link_precs),
        )
        return unlink_precs, link_precs

    def solve_for_transaction(self, *args, **kwargs):
        """生成可执行的安装事务。"""
        log.info("[LoggingSolver] 开始生成事务对象")
        transaction = super().solve_for_transaction(*args, **kwargs)
        log.info("[LoggingSolver] 事务生成完成")
        return transaction


# ============================================================
# 使用 @hookimpl 装饰器注册 conda_solvers 钩子
# ============================================================

@plugins.hookimpl
def conda_solvers():
    """
    [F-069][F-070] conda_solvers 钩子函数。

    该函数必须返回一个可迭代对象，产出 CondaSolver 实例。
    CondaSolver 包含两个字段：
        - name: 求解器名称（用户通过 --solver <name> 选择）
        - backend: 求解器后端类（必须是 Solver/BaseSolver 的子类）

    参考内置 classic 求解器的注册方式（plugins/solvers.py）：
        @hookimpl(tryfirst=True)
        def conda_solvers():
            yield CondaSolver(name=CLASSIC_SOLVER, backend=Solver)
    """
    yield plugins.types.CondaSolver(
        name="my-logging-solver",
        backend=LoggingSolver,
    )


# ============================================================
# 进阶示例：完全自定义的求解器（替换SAT后端）
# ============================================================

class CustomSATSolver(ClassicSolver):
    """
    演示如何重写求解的核心逻辑。

    实际的自定义求解器需要：
    1. 构造 Index 对象（聚合通道包/已安装包/缓存包/虚拟包）
    2. 使用自己的 SAT 求解逻辑或调用外部求解器
    3. 返回按依赖拓扑排序的 PackageRecord 元组
    """

    def solve_final_state(self, update_modifier=None, deps_modifier=None,
                          prune=None, ignore_pinned=None, force_remove=None):
        # 这里可以实现完全自定义的求解逻辑
        # 例如：调用 libsolv、mamba 的 libsolv 绑定、或其他 SAT 求解器
        #
        # 最小实现需要：
        # 1. 调用 self._prepare() 准备索引（经典求解器的方法）
        # 2. 使用 self._r（Resolve 实例）或自定义求解器计算解
        # 3. 返回排序后的 PackageRef 元组
        #
        # 此处仅为演示，直接回退到 classic 行为
        return super().solve_final_state(
            update_modifier, deps_modifier, prune, ignore_pinned, force_remove
        )


@plugins.hookimpl
def conda_solvers():  # noqa: F811  # 实际插件中此函数在独立模块
    """注册第二个自定义求解器。"""
    yield plugins.types.CondaSolver(
        name="my-custom-sat",
        backend=CustomSATSolver,
    )


# ============================================================
# 文件2: 验证插件是否被正确注册
# ============================================================

def verify_plugin_registration():
    """
    验证自定义求解器是否已成功注册到 conda 插件管理器。
    """
    from conda.base.context import context

    # 获取插件管理器中的所有求解器
    # [F-068] get_solvers() 返回 {name: CondaSolver} 映射
    solver_backend = context.plugin_manager.get_cached_solver_backend("my-logging-solver")
    print(f"自定义求解器后端类: {solver_backend}")
    print(f"是否为 LoggingSolver 子类: {issubclass(solver_backend, ClassicSolver)}")

    # 列出所有可用的求解器
    all_solvers = context.plugin_manager.get_solvers()
    print(f"\n所有已注册求解器:")
    for name, solver_plugin in all_solvers.items():
        print(f"  {name}: {solver_plugin.backend.__name__}")


# ============================================================
# 文件3: pyproject.toml 配置（供 pip 安装时自动注册）
# ============================================================
# 插件包需要在 pyproject.toml 中声明 conda 入口点，
# 这样 conda 启动时才能通过 importlib.metadata 自动发现。
#
# pyproject.toml 示例:
#
# [project]
# name = "my-conda-solver-plugin"
# version = "0.1.0"
# requires-python = ">=3.10"
# dependencies = ["conda"]
#
# [project.entry-points.conda]
# my-solver-plugin = "my_solver_plugin"
#
# 其中:
# - [project.entry-points.conda] 中的 "conda" 必须与 APP_NAME 一致
#   [F-028] APP_NAME = "conda"
# - 键名是插件名称（任意，用于去重）
# - 值是包含 hookimpl 函数的模块路径
```

## 插件注册流程

1. **编写插件模块**：在模块中定义 `@plugins.hookimpl` 装饰的 `conda_solvers()` 函数，yield `CondaSolver` 对象。
2. **声明入口点**：在 `pyproject.toml` 的 `[project.entry-points.conda]` 中注册模块路径。
3. **安装包**：通过 `pip install` 安装后，conda 启动时通过 `importlib.metadata.distributions()` 自动发现插件。
4. **选择求解器**：用户通过 `conda install --solver my-logging-solver numpy` 或设置 `CONDA_SOLVER=my-logging-solver` 环境变量来使用自定义求解器。

## 求解器后端类要求

后端类（`backend` 字段）必须满足以下接口约束：

| 要求 | 说明 |
|------|------|
| 构造函数签名 | `__init__(self, prefix, channels, subdirs=(), specs_to_add=(), specs_to_remove=(), ...)` |
| 必须实现 | `solve_final_state()`, `solve_for_diff()`, `solve_for_transaction()` 三个公开方法 |
| 返回值类型 | `solve_final_state()` 返回按依赖排序的 `PackageRef` 元组 |
| 推荐继承 | 继承 `conda.core.solve.Solver`（classic）以复用索引构建和事务生成逻辑 |

## 注意事项

- `@hookimpl(tryfirst=True)` 可设置优先级（如 classic 求解器使用 `tryfirst=True` 防止被覆盖）。
- 插件名称必须小写，多个插件不能注册相同名称，否则会抛出 `PluginError`。
- 重写 `solve_final_state()` 时务必确保返回正确拓扑排序的包列表，否则安装顺序可能出错。
- 自定义 SAT 后端需要处理虚拟包（`__cuda`、`__glibc` 等），否则 GPU/平台相关的依赖解析会失败。
- 使用 `context.plugin_manager.get_solvers()` 可以在运行时查看所有已注册求解器。
- 开发调试时可通过 `conda config --set solver my-logging-solver` 设置默认求解器。
