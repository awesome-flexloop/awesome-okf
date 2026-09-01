---
okf_version: "0.2"
type: "concept"
title: "Solver 求解器与 SAT 算法"
sources:
  - "conda/core/solve.py"
  - "conda/resolve.py"
  - "conda/common/logic.py"
  - "conda/api.py"
  - "conda/base/constants.py"
---

# Solver 求解器与 SAT 算法

## 概述

conda 的依赖求解是一个布尔可满足性问题（SAT），即给定一组包和它们之间的依赖/冲突约束，寻找一组满足所有约束的包安装方案。求解器系统分为三层：高层 API 类 `conda.api.Solver` 提供公开接口；`conda.core.solve.BaseSolver` 定义求解器框架和三个公开方法；`conda.resolve.Resolve` 实现经典的 SAT 求解逻辑，底层通过 `conda.common.logic.Clauses` 管理 SAT 子句 [F-044][F-057]。求解器后端完全可插拔，通过插件系统支持 classic（经典SAT）、libmamba 等不同后端 [F-064][F-065]。

## BaseSolver 三个公开方法

`BaseSolver` 是经典求解器的高层抽象类，定义了三个公开方法，构成"最终状态→差异→事务"的递进式求解接口 [F-044]：

### 1. solve_final_state() — 求解最终状态

```python
def solve_final_state(
    self,
    update_modifier=NULL,
    deps_modifier=NULL,
    prune=NULL,
    ignore_pinned=NULL,
    force_remove=NULL,
    should_retry_solve=False,
) -> tuple[PackageRecord, ...]:
```

该方法是求解的核心，返回环境求解后的最终状态——一组按依赖顺序（从根到叶）排列的 `PackageRecord` 元组，表示环境中应该安装的所有包 [F-044]。

关键参数控制求解行为：

- **`update_modifier`**（`UpdateModifier` 枚举）：控制已有包的更新策略，包括 `FREEZE_INSTALLED`（冻结已安装包，不更新依赖）、`UPDATE_DEPS`（更新依赖）、`UPDATE_SPECS`（更新指定spec，默认）、`UPDATE_ALL`（更新所有包）、`SPECS_SATISFIED_SKIP_SOLVE`（spec已满足时跳过求解）[F-028]。
- **`deps_modifier`**（`DepsModifier` 枚举）：控制依赖处理方式，包括 `NOT_SET`（默认）、`NO_DEPS`（不安装依赖，仅安装请求的包）、`ONLY_DEPS`（仅安装依赖）[F-028]。
- **`prune`**：若为 `True`，移除不再被任何包依赖且非用户请求的包。
- **`ignore_pinned`**：若为 `True`，忽略 `conda-meta/pinned` 文件中的版本固定。
- **`force_remove`**：强制移除包而不移除依赖它的包（危险操作）。

在 `BaseSolver` 中 `solve_final_state()` 抛出 `NotImplementedError`，由子类 `Solver`（classic 求解器）实现 [F-044]。子类实现中会创建 `ReducedIndex`、实例化 `Resolve` 对象、执行 SAT 求解、处理冲突并返回最终包集合。

### 2. solve_for_diff() — 求解差异

```python
def solve_for_diff(
    self,
    update_modifier=NULL,
    deps_modifier=NULL,
    prune=NULL,
    ignore_pinned=NULL,
    force_remove=NULL,
    force_reinstall=NULL,
    should_retry_solve=False,
) -> tuple[tuple[PackageRecord, ...], tuple[PackageRecord, ...]]:
```

该方法调用 `solve_final_state()` 获取最终状态，然后与当前环境状态对比，返回一个二元组：需要卸载（unlink）的包序列和需要安装（link）的包序列 [F-044]。卸载包按依赖顺序从叶到根排列，安装包按依赖顺序从根到叶排列。`force_reinstall` 参数强制重新安装已满足条件的包。

### 3. solve_for_transaction() — 求解事务

```python
def solve_for_transaction(
    self,
    update_modifier=NULL,
    deps_modifier=NULL,
    prune=NULL,
    ignore_pinned=NULL,
    force_remove=NULL,
    force_reinstall=NULL,
    should_retry_solve=False,
) -> UnlinkLinkTransaction:
```

该方法是最外层接口，调用 `solve_for_diff()` 获取差异，然后包装为 `UnlinkLinkTransaction` 事务对象 [F-044]。在求解前后分别调用插件钩子 `invoke_pre_solves()` 和 `invoke_post_solves()`，允许插件在求解前后执行自定义逻辑。同时检查 conda 是否有新版本可用并发出提示。

### BaseSolver 初始化

`BaseSolver.__init__()` 接收以下参数 [F-045]：

```python
def __init__(
    self,
    prefix: str,                                    # 环境路径
    channels: Iterable[Channel] | None = None,     # 通道列表
    subdirs: Iterable[str] = (),                   # 子目录列表
    specs_to_add: Iterable[MatchSpec] = (),        # 要添加的包specs
    specs_to_remove: Iterable[MatchSpec] = (),     # 要移除的包specs
    repodata_fn: str = REPODATA_FN,                # repodata文件名
    command=NULL,                                  # 执行的命令类型
):
```

初始化时，specs 通过 `MatchSpec.merge()` 合并为 `frozenset`，确保去重和规范化。subdirs 会与 `context.known_subdirs` 对比，无效 subdir 直接抛出 ValueError。

## SAT 求解器后端

### 三种后端实现

`conda/resolve.py` 支持三种 SAT 求解器后端，通过 `_sat_solvers` 字典注册 [F-058]：

```python
_sat_solvers = {
    SatSolverChoice.PYCOSAT: PycoSatSolver,      # 默认，基于 pycosat C扩展
    SatSolverChoice.PYCRYPTOSAT: PyCryptoSatSolver,  # 基于 CryptoMiniSat
    SatSolverChoice.PYSAT: PySatSolver,          # 基于 PySAT 工具包
}
```

`SatSolverChoice` 枚举定义在 `conda/base/constants.py` 中 [F-028]，三个值分别为 `"pycosat"`、`"pycryptosat"`、`"pysat"`。

### 后端选择与冒烟测试

`_get_sat_solver_cls()` 函数使用 `@cache` 装饰器确保求解器只检测一次 [F-059]：

```python
@cache
def _get_sat_solver_cls(sat_solver_choice=SatSolverChoice.PYCOSAT):
    def try_out_solver(sat_solver):
        c = Clauses(sat_solver=sat_solver)
        required = {c.new_var(), c.new_var()}
        c.Require(c.And, *required)
        solution = set(c.sat())
        if not required.issubset(solution):
            raise RuntimeError(...)
    # 首先尝试指定的求解器，失败则按顺序尝试其他求解器
    ...
```

选择逻辑为：首先尝试用户配置的求解器（默认 pycosat），执行一个简单的 SAT 冒烟测试——创建两个变量，要求它们同时为真，验证求解器返回正确的解。若指定求解器不可用，则依次尝试其他求解器作为回退。若所有求解器都不可用，抛出 `CondaDependencyError`。

## Clauses SAT 子句管理

`Clauses` 类封装了 SAT 子句的管理，是 SAT 求解的核心数据结构 [F-060]。它将底层 C 扩展 `_Clauses`（来自 `conda/common/_logic.pyx` 或 `_logic.c`）包装为 Python 友好的接口。

### Tseitin 转换

Clauses 的设计核心是 Tseitin 转换 [F-061]。嵌套逻辑表达式（如 AND/OR/XOR 嵌套）不通过分发律展开（那会导致指数级膨胀），而是通过引入新变量来表示子表达式，将等价关系（`expr <-> x`）编码为子句。这样最终的子句都是文字的析取（OR），子句数量与表达式大小线性增长。

例如，要表示 `(a ∧ b) ∨ c`，传统方法会分发为 `(a∨c) ∧ (b∨c)`；Tseitin 方法引入新变量 `x` 表示 `(a∧b)`，添加子句 `(¬x∨a) ∧ (¬x∨b) ∧ (¬a∨¬b∨x) ∧ (x∨c)`。

### 核心方法

Clauses 提供以下核心方法 [F-060]：

| 方法 | 功能 |
|------|------|
| `new_var(name=None)` | 创建新的 SAT 变量（整数），可绑定名称 |
| `add_clause(clause)` | 添加一个子句（文字的析取） |
| `add_clauses(clauses)` | 批量添加子句 |
| `Require(func, *args)` | 强制要求表达式为真（polarity=True） |
| `Prevent(func, *args)` | 强制要求表达式为假（polarity=False） |
| `And(f, g)` | 逻辑与，返回表示结果的文字 |
| `Or(f, g)` | 逻辑或，返回表示结果的文字 |
| `Not(x)` | 逻辑非，返回否定文字 |
| `Xor(f, g)` | 逻辑异或 |
| `sat()` | 调用 SAT 求解器，返回满足约束的变量赋值 |

变量以整数表示：正整数表示变量为真，负整数表示变量为假。`TRUE` 和 `FALSE` 常量从 C 扩展导入，分别表示逻辑真和逻辑假 [F-062]。

### 名称-变量映射

Clauses 维护 `self.names`（名称→变量映射）和 `self.indices`（变量→名称映射），允许通过名称引用变量。`name_var(m, name)` 方法同时注册正向名称和否定名称（`"!name"` 映射到 `-m`）。

## Resolve SAT 求解器

`Resolve` 类是经典求解器的核心，管理 SAT 子句和包到 SAT 变量的映射 [F-057]。它的主要职责包括：

1. **索引构建**：将 Index 中的包按名称分组（`groups = groupby(lambda x: x.name, index.values())`），为每个包版本创建对应的 SAT 变量；
2. **约束编码**：将依赖关系（depends/constrains）、版本冲突、通道优先级等约束编码为 SAT 子句；
3. **求解**：调用 Clauses.sat() 获取解，处理多解偏好（优先新版本、高优先级通道）；
4. **冲突分析**：求解失败时生成最小不可满足子集（MUS），用于错误报告。

Resolve 从 context 读取通道优先级（`context.channel_priority`）和时间戳忽略设置（`context.solver_ignore_timestamps`），影响约束编码方式。

## 插件后端委托模式

`conda/api.py` 中的 `Solver` 类采用**薄门面**（thin facade）+ **内部委托**模式 [F-064][F-065]：

```python
class Solver:
    def __init__(self, prefix, channels, subdirs=(), specs_to_add=(), specs_to_remove=()):
        solver_backend = context.plugin_manager.get_cached_solver_backend()
        self._internal = solver_backend(
            prefix, channels, subdirs, specs_to_add, specs_to_remove
        )

    def solve_final_state(self, ...):
        return self._internal.solve_final_state(...)
    # solve_for_diff 和 solve_for_transaction 同样委托给 self._internal
```

公开 API 类不包含业务逻辑，通过 `context.plugin_manager.get_cached_solver_backend()` 获取后端类，实例化为 `self._internal`，然后将所有方法调用委托给内部对象。classic 求解器通过内置插件注册为默认后端；conda-libmamba-solver 等第三方求解器也是通过此机制插入。

类似的委托模式也应用于 `SubdirData`、`PackageCacheData`、`PrefixData` 三个公开 API 类，它们都将实际工作委托给 core 层的同名内部类 [F-064]。每个 API 类还提供 `reload()` 方法强制刷新数据 [F-067]。

## 枚举速查

`DepsModifier` 枚举 [F-028]：
- `NOT_SET`：默认行为
- `NO_DEPS`：不安装依赖
- `ONLY_DEPS`：仅安装依赖

`UpdateModifier` 枚举 [F-028]：
- `SPECS_SATISFIED_SKIP_SOLVE`：specs 已满足时跳过求解
- `FREEZE_INSTALLED`：冻结已安装包
- `UPDATE_DEPS`：更新依赖
- `UPDATE_SPECS`：更新指定 specs（默认）
- `UPDATE_ALL`：更新所有包

`SatSolverChoice` 枚举 [F-028]：
- `PYCOSAT` = `"pycosat"`：pycosat 后端（默认）
- `PYCRYPTOSAT` = `"pycryptosat"`：CryptoMiniSat 后端
- `PYSAT` = `"pysat"`：PySAT 后端

## 求解流程概览

```
conda.api.Solver
    ↓ plugin backend selection
core.solve.Solver (classic)
    ↓
  ┌─ solve_final_state()
  │    ↓
  │  ReducedIndex (dependency closure via BFS)
  │    ↓
  │  resolve.Resolve (constraint encoding)
  │    ↓
  │  logic.Clauses (Tseitin transformation → CNF clauses)
  │    ↓
  │  _Clauses (C extension) → pycosat/pycryptosat/pysat
  │    ↓
  │  SAT solution → PackageRecord tuple (roots → leaves)
  │
  ├─ solve_for_diff() → (unlink_precs, link_precs)
  │
  └─ solve_for_transaction() → UnlinkLinkTransaction
```

## 相关概念

- [Index 索引与 SubdirData](08-index-and-repodata.md)：ReducedIndex 是 SAT 求解的数据来源
- [UnlinkLinkTransaction 事务与包链接](10-transaction-link.md)：solve_for_transaction() 的输出是事务对象
- [Context 全局配置与 condarc](07-context-configuration.md)：求解器从 context 获取 solver 后端选择、通道优先级等配置
