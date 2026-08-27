---
okf_version: "0.2"
type: "concept"
title: "Index 索引与 SubdirData 仓库数据"
sources:
  - "conda/core/index.py"
  - "conda/core/subdir_data.py"
  - "conda/gateways/repodata/__init__.py"
---

# Index 索引与 SubdirData 仓库数据

## 概述

conda 的包索引系统由两个核心类协作完成：`Index` 和 `SubdirData`。`Index` 是一个聚合容器，继承自 `UserDict`，将来自四类信息源的包记录统一汇聚为一个可查询的字典结构 [F-050]。`SubdirData` 则负责管理单个通道子目录（subdir）下的 `repodata.json` 数据，包括网络加载、本地缓存和懒转换 [F-046]。这两个类共同构成了 conda 求解器的数据基础——求解器从 Index 获取所有可用包的信息，再通过 SAT 算法求解依赖。

## Index 聚合四类信息源

`Index(UserDict)` 是包信息的聚合入口，在其类文档字符串中明确定义了四类信息源 [F-050]：

### 1. Channels（远端通道包）

Channels 代表从标准 URL 源（主要是在线通道，也支持 `file://` 本地文件系统）获取的包。每个 Channel 对象通过 URL 分解为 scheme、auth、location、token、channel、subdir 等组件。通道数据由 `SubdirData` 类负责获取，单个包记录类型为 `PackageRecord`。

### 2. Prefix（已安装包）

Prefix 代表当前环境中已安装的包。每个 Index 可以关联恰好一个 Prefix（即一个 conda 环境的路径）。已安装包信息由 `PrefixData` 类管理，通过读取环境目录下 `conda-meta/*.json` 文件获取。单个包记录类型为 `PrefixRecord`。

当 Prefix 中的包与远端通道的包同名同版本时，Index 会合并两者信息——以远端 repodata 为主，但复制 PrefixRecord 的 link 信息，使求解器知道该包已安装。

### 3. Package Cache（本地缓存包）

Package Cache 代表已下载解压到本地包缓存目录（pkgs_dirs）但可能未安装到关联环境中的包。这些包可能曾安装在本地的其他环境中，但后来已从所有环境移除。缓存包信息由 `PackageCacheData` 类管理，单个包记录类型为 `PackageCacheRecord`。

### 4. Virtual Packages（虚拟包）

虚拟包代表系统属性而非真正的 conda 包，用于告知求解器当前操作系统、CPU 架构、CUDA 版本等系统信息。虚拟包通过 `conda_virtual_packages` 插件钩子注入，如 `__linux`、`__osx`、`__win`、`__cuda`、`__glibc`、`__archspec` 等。单个虚拟包使用特殊构造的 `PackageRecord` 表示，通过 `PackageRecord.virtual_package()` 和 `PackageRecord.feature()` 工厂方法创建。

### Index 初始化流程

Index 的 `__init__` 方法接受以下关键参数：

```python
class Index(UserDict):
    def __init__(
        self,
        channels: Iterable[str | Channel] = (),
        prepend: bool = True,          # 是否在传入 channels 前追加配置的默认通道
        platform: str | None = None,
        subdirs: tuple[str, ...] | None = None,
        use_local: bool = False,       # 是否添加 local 通道
        use_cache: bool | None = None, # 是否包含包缓存
        prefix: PathType | PrefixData | None = None,
        repodata_fn: str | None = context.repodata_fns[-1],
        use_system: bool = False,      # 是否添加虚拟系统包
    ) -> None:
```

初始化过程中，Index 为每个 channel × subdir 组合创建对应的 `SubdirData` 实例，建立通道到 SubdirData 列表的映射 `self.channels`。

### 懒加载与 _realize()

Index 采用懒加载策略：`__init__` 只建立通道和 SubdirData 的映射关系，不实际加载数据。真正的数据加载发生在首次访问 `self.data` 属性时，触发 `_realize()` 方法：

```python
def _realize(self) -> None:
    self._data = {}
    # 1. 从所有 SubdirData 加载通道包
    for subdir_datas in self.channels.values():
        for subdir_data in subdir_datas:
            self._data.update((prec, prec) for prec in subdir_data.iter_records())
    # 2. 补充已安装包信息
    self._supplement_index_dict_with_prefix()
    # 3. 补充包缓存信息
    if self.use_cache:
        self._supplement_index_dict_with_cache()
    # 4. 添加 track features
    self._data.update(self.features)
    # 5. 添加虚拟系统包
    if self.use_system:
        self._data.update(self.system_packages)
```

文档明确警告避免使用 `.data` 属性，因为它会强制完整加载所有包记录，开销显著。推荐通过 `__getitem__` 按需查询。

### ReducedIndex

`ReducedIndex` 是 Index 的子类，用于创建包的子集索引。它接收一组 `MatchSpec`，通过 BFS 遍历依赖图，只收集与给定 specs 相关的包及其传递依赖，大幅减少求解器需要处理的包数量。`get_reduced_index()` 方法用于从已有 Index 便捷构造 ReducedIndex。

## SubdirData 与元类缓存

`SubdirData` 管理单个 subdir 的 repodata 数据，使用 `SubdirDataType` 元类实现实例缓存 [F-046]。

### SubdirDataType 元类

`SubdirDataType` 是一个自定义元类，重写了 `__call__` 方法，在创建 SubdirData 实例前先检查缓存：

```python
class SubdirDataType(type):
    def __call__(cls, channel: Channel, repodata_fn: str = REPODATA_FN) -> SubdirData:
        cache_key = channel.url(with_credentials=True), repodata_fn
        if cache_key in SubdirData._cache_:
            cache_entry = SubdirData._cache_[cache_key]
            # file:// URL 检查 mtime 决定是否使用缓存
            if cache_key[0] and cache_key[0].startswith("file://"):
                file_path = url_to_path(channel_url + "/" + repodata_fn)
                if exists(file_path) and cache_entry._mtime >= getmtime(file_path):
                    return cache_entry
            else:
                return cache_entry
        # 缓存未命中，创建新实例
        subdir_data_instance = super().__call__(...)
        subdir_data_instance._mtime = time()
        SubdirData._cache_[cache_key] = subdir_data_instance
        return subdir_data_instance
```

缓存键为 `(channel_url_with_credentials, repodata_fn)` 元组 [F-047]。对于 `file://` 本地通道，元类通过比较文件 mtime 来判断缓存是否失效；对于远程 URL，缓存始终命中（远程 repodata 的更新通过网关层的 ETag/Cache-Control 机制处理）。

### repodata.json 加载与 pickle 缓存

SubdirData 通过网关层的 `RepodataFetch` 和 `CondaRepoInterface` 加载 repodata。加载后使用 pickle 序列化到本地缓存目录，缓存版本号为 `REPODATA_PICKLE_VERSION = 30` [F-048]，这意味着缓存格式已经历了30次迭代。`MAX_REPODATA_VERSION = 2` 表示 repodata.json 格式本身的版本上限为2。

pickle 缓存文件存储在 conda 的缓存目录中，通过 `cache_fn_url()` 函数根据 URL 生成缓存文件名。缓存状态由 `RepodataState` 类管理，记录 ETag、Last-Modified、Cache-Control 等 HTTP 缓存头信息。

### PackageRecordList 懒转换

`PackageRecordList(UserList)` 实现了从 dict 到 PackageRecord 对象的延迟转换 [F-049]：

```python
class PackageRecordList(UserList):
    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.__class__(self.data[i])
        else:
            record = self.data[i]
            if not isinstance(record, PackageRecord):
                record = PackageRecord(**record)
                self.data[i] = record
            return record
```

加载 repodata.json 后，原始数据以 dict 形式存储，只有在访问具体索引位置时才转换为 PackageRecord 对象。这避免了一次性构造数万个 PackageRecord 带来的性能开销，尤其在只查询少量包时效果显著。

### repodata_fn 参数

`repodata_fn` 参数指定 repodata 文件名，默认为 `"repodata.json"`（即常量 `REPODATA_FN`）[F-028]。该参数贯穿整个数据加载链：Index → SubdirData → RepodataFetch，允许使用替代的 repodata 文件（如 `current_repodata.json`，一个只包含最新版本包的裁剪版本）。context 提供 `context.repodata_fns` 列表，按优先级排列 repodata 文件名。

### query_all 静态方法

`SubdirData.query_all()` 是一个便捷的静态方法，用于跨所有通道和子目录并行查询包：

```python
@staticmethod
def query_all(
    package_ref_or_match_spec: MatchSpec | str,
    channels: Iterable[Channel | str] | None = None,
    subdirs: Iterable[str] | None = None,
    repodata_fn: str = REPODATA_FN,
) -> tuple[PackageRecord, ...]:
```

该方法使用 `ThreadLimitedThreadPoolExecutor` 并行查询各 SubdirData，返回匹配的 `PackageRecord` 元组。在 `ReducedIndex._derive_reduced_index()` 中，包的获取通过 Index 的 `_retrieve_all_from_channels()` 方法而非直接调用 `query_all()`，以保持与 Index 的 prefix/cache 补充逻辑一致。

## 数据流向

```
Channel URLs × subdirs
        ↓
   SubdirData (metaclass cache)
        ↓
  repodata.json (network/file)
        ↓
  pickle cache (version 30)
        ↓
 PackageRecordList (lazy convert)
        ↓
      Index ──── supplement: PrefixData (conda-meta/*.json)
           ├─── supplement: PackageCacheData (pkgs_dirs)
           ├─── supplement: Virtual Packages (plugins)
           └─── supplement: Track Features
        ↓
   ReducedIndex (BFS dependency closure)
        ↓
      Solver / Resolve (SAT solving)
```

## 相关概念

- [Context 全局配置与 condarc](07-context-configuration.md)：Index 从 context 获取 channels、subdirs、repodata_fn 等默认配置
- [Solver 求解器与 SAT 算法](09-solver-and-resolve.md)：ReducedIndex 是求解器的直接数据源
