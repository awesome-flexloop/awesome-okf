---
okf_version: "0.2"
type: "concept"
title: "conda.api公开Python API"
sources:
  - "conda/api.py"
---

# conda.api公开Python API

`conda.api` 模块提供了四个高层API类，以**薄门面（thin facade）**模式将 conda 内部的core层实现包装为稳定的公开接口。所有API类统一采用 `_internal` 委托模式——公开类本身不含业务逻辑，构造时创建内部实现类实例（来自 `core/` 模块），所有方法调用委托给 `self._internal`。这一设计保证了API稳定性：内部实现可重构，只要公开接口签名不变，下游代码不受影响。

> ⚠️ **Beta声明**：所有API类当前标记为 **Beta**，小版本间可能发生重大变更和次要变更。

## _internal 委托模式

四个API类的构造模式完全一致 [F-064]：

```python
class Solver:
    def __init__(self, prefix, channels, subdirs=(), specs_to_add=(), specs_to_remove=()):
        solver_backend = context.plugin_manager.get_cached_solver_backend()
        self._internal = solver_backend(
            prefix, channels, subdirs, specs_to_add, specs_to_remove
        )

class SubdirData:
    def __init__(self, channel):
        channel = Channel(channel)
        if not channel.subdir:
            raise ValueError("SubdirData requires platform-aware Channel objects.")
        self._internal = _SubdirData(channel)

class PackageCacheData:
    def __init__(self, pkgs_dir):
        self._internal = _PackageCacheData(pkgs_dir)

class PrefixData:
    def __init__(self, prefix_path):
        self._internal = _PrefixData(prefix_path)
```

每个公开方法都是一行委托调用，例如 `Solver.solve_final_state()` 直接调用 `self._internal.solve_final_state(...)`。

## Solver：求解器API

`Solver` 是环境求解的高层入口，提供三个公开方法，对应求解结果的三种不同表示形式 [F-044]：

### 构造参数

```python
Solver(
    prefix,              # 环境前缀路径
    channels,            # 优先级排序的通道列表（Channel对象序列）
    subdirs=(),          # 优先级排序的子目录列表（如 linux-64, noarch）
    specs_to_add=(),     # 要添加的包规格（MatchSpec集合）
    specs_to_remove=(),  # 要移除的包规格（MatchSpec集合）
)
```

构造时通过 `context.plugin_manager.get_cached_solver_backend()` 获取求解器后端类（默认为 classic 求解器），再实例化 `_internal`。这意味着求解器后端完全可插拔——插件可注册自定义求解器（如 libmamba）。

### solve_final_state()

```python
def solve_final_state(
    self,
    update_modifier=NULL,   # UpdateModifier 枚举
    deps_modifier=NULL,     # DepsModifier 枚举
    prune=NULL,             # 是否修剪不再需要的依赖
    ignore_pinned=NULL,     # 是否忽略pinned配置
    force_remove=NULL,      # 是否强制移除（不检查依赖）
)
```

返回环境的最终求解状态：按依赖顺序（从根到叶）排序的 `PackageRecord` 元组。这是最底层的结果形式，直接给出求解后环境中应存在的所有包。

### solve_for_diff()

```python
def solve_for_diff(
    self,
    update_modifier=NULL, deps_modifier=NULL, prune=NULL,
    ignore_pinned=NULL, force_remove=NULL,
    force_reinstall=False,  # 是否强制重装已满足的包
)
```

返回二元组 `(unlink_precs, link_precs)`：
- **unlink_precs**：需要从环境中移除的包（按叶到根的依赖顺序排序）
- **link_precs**：需要添加到环境中的包（按根到叶的依赖顺序排序）

这是事务执行的直接输入——分别对应卸载和安装操作。

### solve_for_transaction()

```python
def solve_for_transaction(
    self,
    update_modifier=NULL, deps_modifier=NULL, prune=NULL,
    ignore_pinned=NULL, force_remove=NULL,
    force_reinstall=False,
)
```

返回 `UnlinkLinkTransaction` 实例，可直接执行求解结果。这是最高层的方法——从规格到可执行事务一步到位。

### 控制标志

**DepsModifier**（依赖处理模式）：
- `NO_DEPS`：不安装依赖
- `ONLY_DEPS`：仅安装依赖
- `UPDATE_DEPS`：更新依赖
- `UPDATE_DEPS_ONLY_DEPS`：仅更新依赖
- `FREEZE_INSTALLED`：冻结已安装包

**UpdateModifier**（更新模式）：
- `UPDATE_SPECS`（默认）：仅更新用户明确请求的包
- `UPDATE_ALL`：更新所有包
- `UPDATE_ALL_DEPS`：更新所有依赖
- `FREEZE_INSTALLED`：冻结已安装版本

## SubdirData：通道repodata API

`SubdirData` 管理单个通道子目录（如 `conda-forge/linux-64`）的 repodata.json 加载和查询。

### 构造

```python
SubdirData(channel)  # channel: str 或 Channel，必须包含subdir
```

Channel 参数必须包含平台子目录（如 `Channel('conda-forge/linux-64')`），否则抛出 `ValueError`。内部使用 `_SubdirData` 元类缓存机制——相同 channel URL 返回同一实例，file:// URL通过mtime检测缓存失效 [F-046][F-047]。

### query()

```python
def query(self, package_ref_or_match_spec)
```

在单个 subdir 的 repodata 中查询匹配的包，返回 `tuple[PackageRecord]`。参数可以是精确的 `PackageRef`、`MatchSpec` 对象或字符串（自动转为 MatchSpec）。

### query_all() —— 静态方法

```python
@staticmethod
def query_all(package_ref_or_match_spec, channels=None, subdirs=None)
```

跨所有配置的通道和子目录查询 [F-066]。当 channels/subdirs 为 None 时，回退到 `context.channels` 和 `context.subdirs`。返回所有通道×子目录矩阵中匹配的 `PackageRecord` 元组。这是搜索"哪些通道提供某个包"的标准方式。

### iter_records()

```python
def iter_records()
```

返回生成器，遍历当前 subdir repodata 中的所有 `PackageRecord`。警告：生成器首次使用后耗尽。

### reload()

```python
def reload()
```

强制刷新实例数据 [F-067]。repodata 在首次调用 query/iter_records 时懒加载，当确知数据过期时（如通道更新后）可调用此方法清除缓存、重新下载/加载。返回 self 以支持链式调用。

## PackageCacheData：包缓存API

`PackageCacheData` 管理本地包缓存目录（pkgs_dirs）中的已下载包。

### 构造与工厂方法

```python
PackageCacheData(pkgs_dir)                    # 指定缓存目录
PackageCacheData.first_writable(pkgs_dirs=None)  # 静态方法，返回第一个可写缓存实例
```

`first_writable()` 在 pkgs_dirs 为 None 时使用 `context.pkgs_dirs`，返回第一个可写缓存的 `PackageCacheData` 实例。

### 核心方法

- **`get(package_ref, default=NULL)`**：按 `PackageRef` 精确查找 `PackageCacheRecord`，不存在时返回 default 或抛出 KeyError
- **`query(package_ref_or_match_spec)`**：按 MatchSpec 查询缓存包，返回 `tuple[PackageCacheRecord]`
- **`query_all(package_ref_or_match_spec, pkgs_dirs=None)`**：静态方法，跨所有缓存目录查询
- **`iter_records()`**：生成器遍历缓存中所有包记录
- **`is_writable`**（属性）：缓存目录是否可写

### reload()

```python
def reload()
```

强制重新扫描缓存目录内容，返回 self [F-067]。缓存内容在首次访问时懒加载，`reload()` 用于确保看到最新下载的包。

## PrefixData：环境前缀API

`PrefixData` 管理已安装到环境前缀的包记录。

### 构造

```python
PrefixData(prefix_path)  # 环境前缀路径
```

内部通过读取前缀目录下 `conda-meta/` 目录中的 JSON 文件加载已安装包信息 [F-055]。

### 核心方法

- **`get(package_ref, default=NULL)`**：按包名查找 `PrefixRecord`。注意：与 PackageCacheData.get() 不同，这里使用 `package_ref.name` 作为键（因为已安装包按名称唯一）
- **`query(package_ref_or_match_spec)`**：按 MatchSpec 查询已安装包，返回 `tuple[PrefixRecord]`
- **`iter_records()`**：生成器遍历环境中所有已安装包
- **`is_writable`**（属性）：前缀是否可写。返回 True（可写）、False（只读）或 None（不存在conda环境）

### reload()

```python
def reload()
```

强制重新扫描 `conda-meta/` 目录，返回 self [F-067]。在事务执行后用于刷新已安装包列表。

## 重新导出的枚举

`conda.api` 重新导出了两个重要的枚举类型，方便调用方无需从内部模块导入：

```python
from .base.constants import DepsModifier as _DepsModifier
from .base.constants import UpdateModifier as _UpdateModifier

DepsModifier = _DepsModifier
UpdateModifier = _UpdateModifier
```

## 使用模式

典型的程序化使用流程：

```python
from conda.api import Solver, SubdirData, PrefixData
from conda.models.channel import Channel

# 1. 查询某个包在所有通道中的可用版本
records = SubdirData.query_all("python>=3.10",
    channels=[Channel("conda-forge")],
    subdirs=["linux-64", "noarch"])

# 2. 查看当前环境已安装的包
prefix_data = PrefixData("/opt/conda/envs/myenv")
for record in prefix_data.iter_records():
    print(f"{record.name}={record.version}")

# 3. 求解并执行事务
solver = Solver(
    prefix="/opt/conda/envs/myenv",
    channels=[Channel("conda-forge")],
    specs_to_add=("numpy>=1.20", "pandas"),
)
transaction = solver.solve_for_transaction()
transaction.execute()
```

## 设计要点

1. **空壳门面**：API 类不持有业务逻辑，所有实现委托给 `_internal`。这使 API 层成为稳定的契约层——内部重构不影响公开接口
2. **插件感知**：Solver 通过插件管理器获取后端，使得自定义求解器可以无缝替换 classic 求解器
3. **懒加载**：SubdirData/PackageCacheData/PrefixData 的数据在首次查询时才加载，构造开销极小
4. **reload() 模式**：每个类都提供 `reload()` 方法强制刷新，解决了缓存一致性问题
5. **Beta状态**：API 明确标记为 Beta，表明仍在演进中，用户应预期小版本间可能有API变更
