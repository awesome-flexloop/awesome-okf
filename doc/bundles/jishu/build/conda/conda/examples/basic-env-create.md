---
okf_version: "0.2"
type: "example"
title: "程序化创建 conda 环境"
sources: ["conda/api.py", "conda/core/solve.py"]
---

# 程序化创建 conda 环境

本示例演示如何从 Python 代码中使用 conda 的高层 API 创建环境、求解依赖并执行安装事务。核心流程分为三步：初始化求解器、调用 `solve_for_transaction()` 获取事务对象、执行 `UnlinkLinkTransaction` 完成安装。

相关概念：[求解器与依赖解析](../concepts/09-solver-and-resolve.md)、[事务与链接](../concepts/10-transaction-link.md)。

## 完整示例

```python
"""
程序化创建 conda 环境示例。

引用事实：[F-064] Solver 高层API类，采用 _internal 委托模式
         [F-065] Solver.__init__() 通过 plugin_manager 获取求解器后端
         [F-066] SubdirData.query_all() 静态方法查询所有通道
         [F-067] 每个API类都有 reload() 方法
"""

import tempfile
import os
from conda.api import Solver
from conda.models.channel import Channel
from conda.models.match_spec import MatchSpec
from conda.common.constants import NULL
from conda.base.constants import DepsModifier, UpdateModifier


def create_environment(prefix: str, specs: list[str], channels: list[str] = None):
    """
    在指定 prefix 路径创建 conda 环境并安装包。

    参数:
        prefix: 目标环境的文件系统路径，例如 /home/user/.conda/envs/myenv
        specs:  要安装的包规格列表，例如 ["python=3.10", "numpy"]
        channels: 通道列表，默认为 context.channels（defaults）
    """
    # 1. 构造 Channel 对象列表
    #    [F-031] Channel 使用缓存模式，从字符串创建后自动解析URL和subdir
    if channels is None:
        channel_objs = None  # 使用 context.channels 默认值
    else:
        channel_objs = [Channel(c) for c in channels]

    # 2. 构造 MatchSpec 集合
    #    MatchSpec 是 conda 的包查询语言，字符串自动解析为 MatchSpec 对象
    specs_to_add = [MatchSpec(s) for s in specs]

    # 3. 初始化 Solver
    #    [F-065] Solver.__init__() 通过 context.plugin_manager.get_cached_solver_backend()
    #    获取求解器后端（默认为 classic），内部委托给 _internal 对象
    #    参数: prefix(环境路径), channels(通道), subdirs(平台子目录),
    #          specs_to_add(添加包), specs_to_remove(移除包)
    solver = Solver(
        prefix=prefix,
        channels=channel_objs,
        subdirs=(),           # 空元组表示使用 context.subdirs（当前平台）
        specs_to_add=specs_to_add,
        specs_to_remove=(),
    )

    # 4. 求解依赖并获取事务对象
    #    [F-044] solve_for_transaction() 返回 UnlinkLinkTransaction 实例
    #    该方法内部会调用 solve_for_diff() 计算差异，再构建事务
    #    可通过参数控制求解行为：
    #    - deps_modifier: 依赖处理方式（NO_DEPS/ONLY_DEPS/UPDATE_DEPS/FREEZE_INSTALLED）
    #    - prune: 是否修剪不再需要的依赖
    #    - force_reinstall: 是否强制重装已满足的包
    unlink_link_transaction = solver.solve_for_transaction(
        update_modifier=NULL,
        deps_modifier=NULL,
        prune=NULL,
        ignore_pinned=NULL,
        force_remove=NULL,
        force_reinstall=False,
    )

    # 5. 执行事务三部曲：prepare → verify → execute
    #    prepare(): 计算所有路径动作（下载、解压、链接等）
    #    verify():  校验事务的合法性（磁盘空间、权限、文件冲突等）
    #    execute(): 实际执行链接/卸载操作
    unlink_link_transaction.prepare()
    unlink_link_transaction.verify()
    unlink_link_transaction.execute()

    print(f"环境创建成功: {prefix}")
    return unlink_link_transaction


def create_and_list_packages():
    """创建一个临时环境并列出已安装的包。"""
    # 使用临时目录作为环境路径
    with tempfile.TemporaryDirectory() as tmpdir:
        env_prefix = os.path.join(tmpdir, "myenv")

        # 创建环境并安装 python 和 numpy
        txn = create_environment(
            prefix=env_prefix,
            specs=["python=3.10", "numpy"],
            channels=["defaults"],
        )

        # 查看事务中要链接的包
        print("\n将要安装/链接的包:")
        for stp in txn.prefix_setups.values():
            for prec in stp.link_precs:
                print(f"  + {prec.name} {prec.version} {prec.build}")

        # 查看事务中要卸载的包（新环境应为空）
        for stp in txn.prefix_setups.values():
            for prec in stp.unlink_precs:
                print(f"  - {prec.name} {prec.version} {prec.build}")


if __name__ == "__main__":
    create_and_list_packages()
```

## 代码说明

1. **Solver 初始化**：`Solver` 是 conda.api 暴露的高层入口（[F-064]），构造时通过插件管理器获取求解器后端实例。所有实际逻辑委托给 `self._internal`。

2. **solve_for_transaction()**：这是最常用的方法，返回的 `UnlinkLinkTransaction` 封装了完整的安装/卸载操作序列。如果你只需要查看求解结果而不执行，可以用 `solve_final_state()` 获取最终包列表，或用 `solve_for_diff()` 获取增删差异。

3. **事务执行**：`UnlinkLinkTransaction` 遵循 prepare→verify→execute 三段式流程（[F-051]）。`prepare()` 阶段计算所有 `path_actions`（链接、编译.pyc、创建入口点等），`verify()` 做前置校验，`execute()` 执行实际磁盘操作。

4. **参数控制**：`deps_modifier` 和 `update_modifier` 控制依赖更新策略，`prune=True` 会移除不再被任何用户包依赖的孤立依赖。

## 注意事项

- API 标记为 **Beta**，跨小版本可能有变化。
- 执行事务会实际修改磁盘文件，请确保 `prefix` 路径正确。
- 首次运行需要下载 repodata.json 和包文件，耗时取决于网络状况。
- 如果只想模拟求解而不安装，可以只调用 `solve_for_diff()` 查看差异。
