---
okf_version: "0.2"
type: reference
title: Solver 求解器 API
sources:
  - conda/api.py
---

# Solver 求解器 API

`Solver` 类是 Conda 求解逻辑的高层 API 门面（Facade），采用**插件后端委托模式**：构造时通过 `context.plugin_manager.get_cached_solver_backend()` 获取已注册的求解器后端（如经典求解器或 libmamba 求解器），所有公开方法均委托给 `self._internal` 后端实例执行。三个公开方法分别提供三种求解结果形态：最终环境状态、增删差异、可执行事务。

```python
# conda/api.py

class Solver:
    """
    **Beta** While in beta, expect both major and minor changes across minor releases.

    A high-level API to conda's solving logic. Three public methods are provided:
      * solve_final_state()
      * solve_for_diff()
      * solve_for_transaction()
    """

    def __init__(
        self, prefix, channels, subdirs=(), specs_to_add=(), specs_to_remove=()
    ):
        """
        Args:
            prefix: The conda prefix / environment location.
            channels: A prioritized list of channels to use for the solution.
            subdirs: A prioritized list of subdirs to use for the solution.
            specs_to_add: The set of package specs to add to the prefix.
            specs_to_remove: The set of package specs to remove from the prefix.
        """
        solver_backend = context.plugin_manager.get_cached_solver_backend()
        self._internal = solver_backend(
            prefix, channels, subdirs, specs_to_add, specs_to_remove
        )

    def solve_final_state(
        self,
        update_modifier=NULL,
        deps_modifier=NULL,
        prune=NULL,
        ignore_pinned=NULL,
        force_remove=NULL,
    ):
        """Gives the final, solved state of the environment.

        Returns:
            tuple[PackageRef]: In sorted dependency order from roots to leaves,
                the package references for the solved state.
        """
        return self._internal.solve_final_state(
            update_modifier, deps_modifier, prune, ignore_pinned, force_remove
        )

    def solve_for_diff(
        self,
        update_modifier=NULL,
        deps_modifier=NULL,
        prune=NULL,
        ignore_pinned=NULL,
        force_remove=NULL,
        force_reinstall=False,
    ):
        """Gives the package references to remove and add to an environment.

        Returns:
            tuple[PackageRef], tuple[PackageRef]: A two-tuple: (packages_to_remove,
                packages_to_add), both in sorted dependency order.
        """
        return self._internal.solve_for_diff(
            update_modifier, deps_modifier, prune, ignore_pinned,
            force_remove, force_reinstall,
        )

    def solve_for_transaction(
        self,
        update_modifier=NULL,
        deps_modifier=NULL,
        prune=NULL,
        ignore_pinned=NULL,
        force_remove=NULL,
        force_reinstall=False,
    ):
        """Gives an UnlinkLinkTransaction instance for executing the solution.

        Returns:
            UnlinkLinkTransaction
        """
        return self._internal.solve_for_transaction(
            update_modifier, deps_modifier, prune, ignore_pinned,
            force_remove, force_reinstall,
        )
```

**关键设计**：
- **门面模式**：`Solver` 本身不包含求解逻辑，仅作为稳定的公开 API 表面，将调用转发给通过插件系统获取的后端实现
- **后端可插拔**：求解器后端通过 `conda_solvers` 插件钩子注册，支持在运行时切换经典求解器与 libmamba 求解器
- **渐进式结果**：三个方法形成调用链——`solve_final_state()` 给出最终包集合，`solve_for_diff()` 给出增删差异，`solve_for_transaction()` 给出可直接执行的事务对象，满足不同调用场景的需求
- **统一修饰符参数**：`update_modifier`、`deps_modifier`、`prune`、`ignore_pinned`、`force_remove` 等参数贯穿三个方法，控制求解行为（如是否更新依赖、是否修剪孤立依赖、是否忽略 pinned 包等）
