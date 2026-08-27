---
okf_version: "0.2"
type: "concept"
title: "UnlinkLinkTransaction 事务与包链接"
sources:
  - "conda/core/link.py"
  - "conda/core/path_actions.py"
  - "conda/models/enums.py"
---

# UnlinkLinkTransaction 事务与包链接

## 概述

conda 的包安装和卸载不是简单的文件复制/删除，而是通过事务机制（Transaction）来保证操作的原子性和一致性。`UnlinkLinkTransaction` 是事务的核心类，它将求解器输出的包差异（unlink/link 列表）转化为一系列具体的文件系统操作（Action），按确定顺序执行，支持验证、回滚和进度报告 [F-051]。每个事务由一个或多个 `PrefixSetup` 描述，每个 PrefixSetup 对应一个环境前缀的变更计划。

## PrefixSetup

`PrefixSetup` 是一个 `NamedTuple`，描述单个环境前缀的变更计划：

```python
class PrefixSetup(NamedTuple):
    target_prefix: str                           # 目标环境路径
    unlink_precs: tuple[PackageRecord, ...]      # 需要卸载的包
    link_precs: tuple[PackageRecord, ...]        # 需要安装的包
    remove_specs: tuple[MatchSpec, ...]          # 用户请求移除的specs
    update_specs: tuple[MatchSpec, ...]          # 用户请求安装/更新的specs
    neutered_specs: tuple[MatchSpec, ...]        # 被"中和"的specs（约束被放松）
```

PrefixSetup 由 `BaseSolver.solve_for_transaction()` 方法创建，是连接求解器和事务执行层的桥梁 [F-044]。`unlink_precs` 中的包按依赖顺序从叶到根排列（先卸载被依赖者），`link_precs` 中的包按依赖顺序从根到叶排列（先安装被依赖者）。

## UnlinkLinkTransaction 类

`UnlinkLinkTransaction` 接收一个或多个 PrefixSetup，管理整个事务的生命周期：

```python
class UnlinkLinkTransaction:
    def __init__(self, *setups):
        self.prefix_setups = {stp.target_prefix: stp for stp in setups}
        self.prefix_action_groups = {}
        self._prepared = False
        self._verified = False
```

事务支持多前缀操作（通过 `enable_private_envs` 配置），但当前实现中对多前缀事务抛出 `NotImplementedError`，常规操作都是单前缀事务。

### 事务执行三阶段

事务的执行遵循严格的三阶段模型：

#### 1. prepare() — 准备阶段

```python
def prepare(self):
    # 先下载并解压包
    self.download_and_extract()
    # 为每个 prefix 生成 Action 组
    for stp in self.prefix_setups.values():
        self.prefix_action_groups[stp.target_prefix] = self._prepare(
            self.transaction_context,
            stp.target_prefix,
            stp.unlink_precs,
            stp.link_precs,
            stp.remove_specs,
            stp.update_specs,
            stp.neutered_specs,
        )
    self._prepared = True
```

`_prepare()` 方法是核心逻辑，它：
- 确定每个包的链接类型（hardlink/softlink/copy）；
- 生成所有需要执行的 `Action` 对象；
- 将 Action 分组为 `PrefixActionGroup`。

#### 2. verify() — 验证阶段

```python
def verify(self):
    if context.safety_checks == SafetyChecks.disabled:
        self._verified = True
        return
    exceptions = self._verify(self.prefix_setups, self.prefix_action_groups)
    if exceptions:
        self._cleanup_transaction_artifacts()
        maybe_raise(CondaMultiError(exceptions), context)
    self._verified = True
```

验证阶段检查磁盘空间、文件冲突、包完整性、路径权限等。安全检查级别由 `context.safety_checks` 控制（disabled/warn/enabled）。验证失败时会清理临时产物并抛出异常。

#### 3. execute() — 执行阶段

执行阶段按顺序执行所有验证通过的 Action，使用 `ThreadLimitedThreadPoolExecutor` 并行执行 I/O 密集型操作。

事务还维护两个线程池：`verify_executor`（CPU 密集型验证，默认多线程）和 `execute_executor`（I/O 密集型执行，默认多线程）。在 debug 模式或线程数设为1时，退化为 `DummyExecutor`（串行执行）。

### nothing_to_do 属性

`nothing_to_do` 属性检查事务是否为空——当既没有包需要卸载也没有包需要安装，且环境已经存在时，返回 `True`，调用者可以跳过执行。

## determine_link_type() 链接类型决策

包安装时文件如何链接到环境目录，由 `determine_link_type()` 函数决定 [F-052]：

```python
def determine_link_type(extracted_package_dir, target_prefix):
    source_test_file = join(extracted_package_dir, "info", "index.json")
    if context.always_copy:
        return LinkType.copy
    if context.always_softlink:
        return LinkType.softlink
    if hardlink_supported(source_test_file, target_prefix):
        return LinkType.hardlink
    if context.allow_softlinks and softlink_supported(source_test_file, target_prefix):
        return LinkType.softlink
    return LinkType.copy
```

决策优先级从高到低：

1. **always_copy**：若配置了 `always_copy: true`，直接使用复制；
2. **always_softlink**：若配置了 `always_softlink: true`，直接使用软链接；
3. **hardlink**：检测硬链接是否支持（跨文件系统不支持），优先使用硬链接——硬链接不占额外磁盘空间，是最高效的方式；
4. **softlink**：若允许软链接且软链接支持，使用软链接；
5. **copy**：以上都不行时，退化为文件复制。

硬链接测试通过实际创建一个到测试文件（info/index.json）的硬链接来检测，确保源和目标在同一文件系统。软链接测试通过 `os.symlink()` 检测。

## LinkType 枚举

`LinkType` 枚举定义在 `conda/models/enums.py` 中 [F-042]：

```python
class LinkType(Enum):
    hardlink = 1   # 硬链接：inode 共享，空间最优
    softlink = 2   # 软链接/符号链接：路径引用，跨文件系统可用但有兼容性问题
    copy = 3       # 复制：独立文件，最安全但占空间最大
    directory = 4  # 目录：不是链接类型，用于目录操作
```

LinkType 的整数值与历史的 conda 索引格式兼容（paths.json 中使用整数）。`directory` 类型虽然定义在 LinkType 中，但注释明确说明"directory 不是链接类型"，它用于在卸载时标记目录删除操作。

## path_actions 操作集合

事务中的具体文件系统操作由 `conda/core/path_actions.py` 中的 Action 类层次表示。所有 Action 继承自抽象基类 `Action`，保证实现 `verify()`、`execute()`、`reverse()` 等方法 [F-053]。核心 Action 类型包括：

### 链接/卸载操作

| Action 类 | 功能 |
|-----------|------|
| `LinkPathAction` | 将包缓存中的文件链接/复制到目标环境 |
| `UnlinkPathAction` | 从目标环境中移除已链接的文件 |

`LinkPathAction` 根据 LinkType 调用不同的底层磁盘操作：硬链接使用 `create_hard_link_or_copy()`，软链接使用 `os.symlink()`，复制使用 `copy()`。`UnlinkPathAction` 则根据链接类型决定删除策略——硬链接/软链接直接 `os.unlink()`，复制文件直接删除，目录类型则反向清理空目录。

### Python 相关操作

| Action 类 | 功能 |
|-----------|------|
| `CompileMultiPycAction` / `AggregateCompileMultiPycAction` | 批量编译 Python `.pyc` 字节码文件 |

Python 包安装后，需要编译 `.py` 文件为 `.pyc` 以加速导入。这些 Action 聚合多个文件的编译请求，在所有文件链接完成后统一执行，使用多进程并行编译。

### 入口点和菜单操作

| Action 类 | 功能 |
|-----------|------|
| `CreatePythonEntryPointAction` | 创建 Python 包的命令行入口点（如 `conda` 命令） |
| `MakeMenuAction` | 创建开始菜单/桌面快捷方式（通过 menuinst） |
| `RemoveMenuAction` | 移除菜单/快捷方式 |

Windows 上 Python 入口点使用 `.exe` 存根（`shell/cli-64.exe` 或 `shell/cli-32.exe`），Unix 上使用 shebang 脚本。菜单操作通过 `menuinst` 库实现跨平台的快捷方式创建。

### 元数据操作

| Action 类 | 功能 |
|-----------|------|
| `CreatePrefixRecordAction` | 在 `conda-meta/` 目录创建包的 JSON 元数据文件 |
| `RemoveLinkedPackageRecordAction` | 从 `conda-meta/` 目录删除包的 JSON 元数据文件 |
| `UpdateHistoryAction` | 更新 `conda-meta/history` 文件记录变更历史 |
| `RegisterEnvironmentLocationAction` | 注册环境位置到 `~/.conda/environments.txt` |
| `UnregisterEnvironmentLocationAction` | 注销环境位置 |

这些 Action 维护环境元数据的一致性：`conda-meta/` 目录中的 JSON 文件是环境已安装包的权威记录，history 文件记录变更历史，environments.txt 追踪所有已知环境。

## PrefixActionGroup 分组

`PrefixActionGroup` 是一个 `@dataclass`，将同一前缀的所有 Action 按类型分组，确保执行顺序正确：

```python
@dataclass
class PrefixActionGroup:
    remove_menu_action_groups: Iterable[ActionGroup]      # 1. 移除旧菜单
    unlink_action_groups: Iterable[ActionGroup]           # 2. 卸载旧文件
    unregister_action_groups: Iterable[ActionGroup]       # 3. 注销环境
    link_action_groups: Iterable[ActionGroup]             # 4. 链接新文件
    register_action_groups: Iterable[ActionGroup]         # 5. 注册环境
    compile_action_groups: Iterable[ActionGroup]          # 6. 编译pyc
    make_menu_action_groups: Iterable[ActionGroup]        # 7. 创建新菜单
    entry_point_action_groups: Iterable[ActionGroup]      # 8. 创建入口点
    prefix_record_groups: Iterable[ActionGroup]           # 9. 写入conda-meta
    initial_action_groups: Iterable[ActionGroup] = ()     # 0. 插件pre-action
    final_action_groups: Iterable[ActionGroup] = ()       # 10. 插件post-action
```

执行顺序遵循"先破后立"原则：先移除菜单和旧文件，再链接新文件，最后编译、创建菜单和入口点、写入元数据。插件可以通过 `conda_pre_transaction_actions` 和 `conda_post_transaction_actions` 钩子在事务前后插入自定义 Action。

## ActionGroup 与进度报告

`ActionGroup` 是一个 `NamedTuple`，将一组相关的 Action 与包信息和类型标签关联：

```python
class ActionGroup(NamedTuple):
    type: str                           # 动作类型描述
    pkg_data: PackageInfo | None        # 关联的包信息
    actions: Iterable[Action]           # Action 集合
    target_prefix: str                  # 目标前缀
```

ActionGroup 用于进度报告和显示——每个包的链接/卸载操作显示为独立的进度项，提供清晰的用户反馈。

## 相关概念

- [Solver 求解器与 SAT 算法](09-solver-and-resolve.md)：`solve_for_transaction()` 输出 UnlinkLinkTransaction
- [环境管理与 History](11-environments-history.md)：事务通过 UpdateHistoryAction 和 RegisterEnvironmentLocationAction 维护环境元数据
