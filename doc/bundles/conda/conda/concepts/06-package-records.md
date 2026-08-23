---
okf_version: "0.2"
type: "concept"
title: "三级记录模型：PackageRecord / PackageCacheRecord / PrefixRecord"
sources:
  - conda/models/records.py
  - conda/models/enums.py
---

# 三级记录模型：PackageRecord / PackageCacheRecord / PrefixRecord

conda 对包的描述采用三级继承的记录模型，每一级对应包生命周期中的一个阶段：从通道中的远端包元数据（PackageRecord），到下载到本地缓存的包（PackageCacheRecord），再到安装到环境中的包（PrefixRecord）。三者共享同一套主键（_pkey），使得同一个包在不同阶段的记录可以被等价比较和哈希 [F-039]。

```
PackageRecord            ← 通道中的包（repodata.json 中的条目）
    └── SolvedRecord     ← 求解结果中的包（增加 requested_spec）
         └── PrefixRecord ← 已安装到环境的包（conda-meta/*.json）
PackageCacheRecord       ← 本地包缓存中的包（pkgs_dirs 下的包）
```

注意 `PackageCacheRecord` 直接继承 `PackageRecord`（非 SolvedRecord），而 `PrefixRecord` 继承 `SolvedRecord`。

## Entity 字段系统

所有记录类基于 `auxlib.entity` 的 `Entity` 系统，使用声明式字段定义 [F-040]。字段类型在类体中以类属性声明，自动处理序列化/反序列化、类型转换、默认值和别名：

```python
from ..auxlib.entity import (
    BooleanField, ComposableField, DictSafeMixin, Entity,
    EnumField, IntegerField, ListField, NumberField, StringField,
)

class PackageRecord(DictSafeMixin, Entity):
    name = StringField()           # 必需字段，包名
    version = StringField()        # 必需字段，版本号
    build = StringField(aliases=("build_string",))  # 构建字符串，别名 build_string
    build_number = IntegerField()  # 构建号（整数）
    channel = ChannelField(aliases=("schannel",))  # 复合字段，自动从 URL 构造 Channel
    subdir = SubdirField()         # 平台子目录，支持从 url/platform/arch 推断
    fn = FilenameField(aliases=("filename",))      # 文件名，支持从 name-version-build 推断
    md5 = StringField(default=None, required=False, nullable=True, default_in_dump=False)
    sha256 = StringField(default=None, required=False, nullable=True, default_in_dump=False)
    depends = ListField(str, default=())  # 依赖列表（MatchSpec 字符串）
    constrains = ListField(str, default=())  # 约束列表
    track_features = _FeaturesField(required=False, default=())
    features = _FeaturesField(required=False, default=())
    noarch = NoarchField(NoarchType, required=False, nullable=True, default=None)
    package_type = PackageTypeField()
    timestamp = TimestampField()
```

核心字段类型：

| 字段类型 | 用途 | 示例 |
|---------|------|------|
| `StringField` | 字符串值 | name, version, build, md5, sha256 |
| `IntegerField` | 整数值 | build_number, size |
| `BooleanField` | 布尔值 | （用于内部标记） |
| `NumberField` | 数值（TimestampField 继承） | timestamp |
| `EnumField` | 枚举值 | 派生为 LinkTypeField, NoarchField, PackageTypeField |
| `ListField` | 列表值 | depends, constrains, files, track_features |
| `ComposableField` | 复合实体 | Link, PathsData, ChannelField |

特殊字段通过继承 `EnumField` 等实现自定义的 boxing/unboxing 逻辑：
- **ChannelField**：从 URL 字符串自动构造 Channel 对象，dump 时转回字符串
- **SubdirField**：从 url/platform/arch 三级回退推断 subdir 值
- **FilenameField**：从 URL 提取文件名，或拼接 name-version-build 生成
- **TimestampField**：自动在秒和毫秒之间转换（兼容 conda-build 历史数据）
- **LinkTypeField**：支持字符串别名（"hard"→hardlink, "soft"→softlink）
- **Md5Field**：本地文件存在时可即时计算 md5

### _pkey 主键系统

`PackageRecord._pkey` 属性定义了记录相等性和哈希的元组 [F-039]：

```python
@property
def _pkey(self):
    return (
        self.channel.canonical_name,  # 通道规范名
        self.subdir,                  # 平台子目录
        self.name,                    # 包名
        self.version,                 # 版本
        self.build_number,            # 构建号
        self.build,                   # 构建字符串
        # self.fn (仅在 separate_format_cache=True 时包含)
    )
```

两个记录 `__eq__` 和 `__hash__` 都基于 `_pkey`。子类不向 `_pkey` 添加字段，因此 `PackageRecord`、`PackageCacheRecord`、`PrefixRecord` 只要标识同一个包就相等。这允许在求解器中将来自不同来源（远端/缓存/已安装）的同一包记录互换使用。

## PackageRecord：通道中的包

`PackageRecord` 是三级模型的基类，表示远端通道 repodata.json 中的一条包记录 [F-039]。它包含包的完整元数据：

- **身份字段**：name, version, build, build_number, channel, subdir, fn
- **校验字段**：md5, sha256, size, timestamp
- **依赖字段**：depends（运行时依赖）, constrains（版本约束）, track_features, features
- **分类字段**：noarch, package_type, license, license_family
- **网络字段**：url（下载地址）

工厂方法：
- `PackageRecord.feature(feature_name)`：创建 feature 伪包记录（SAT 求解器使用）
- `PackageRecord.virtual_package(name, version, build_string)`：创建虚拟包记录（如 `__cuda`, `__osx`）

核心方法：
- `to_match_spec()`：将自身转换为 [MatchSpec](04-matchspec.md)
- `match(spec)`：被 MatchSpec 调用，判断是否匹配
- `dist_str()`：返回 `channel/subdir::name-version-build` 格式字符串

## PackageCacheRecord：已下载缓存的包

`PackageCacheRecord` 继承 `PackageRecord`，增加两个本地路径字段 [F-039]：

```python
class PackageCacheRecord(PackageRecord):
    package_tarball_full_path = StringField()   # 包文件完整路径（.conda 或 .tar.bz2）
    extracted_package_dir = StringField()       # 解压后的包目录路径
    md5 = Md5Field()                            # 覆盖：本地文件存在时即时计算
```

关键属性：
- `is_fetched`：包压缩文件是否存在于本地
- `is_extracted`：包是否已解压（检查 `info/index.json` 是否存在）
- `tarball_basename`：包文件的 basename

`Md5Field` 重写了 `__get__` 方法，当 md5 值缺失时自动计算本地文件的 md5 校验和（带内存缓存 `_memoized_md5`），用于下载后校验。

## PrefixRecord：已安装到环境的包

`PrefixRecord` 继承 `SolvedRecord`（后者继承 `PackageRecord`），表示安装到某个 conda 环境前缀（prefix）中的包 [F-039]。记录来源于 `$prefix/conda-meta/<name>-<version>-<build>.json` 文件。

新增字段：

```python
class PrefixRecord(SolvedRecord):
    package_tarball_full_path = StringField(required=False)  # 来源包文件路径
    extracted_package_dir = StringField(required=False)      # 来源解压目录
    files = ListField(str, default=(), required=False)       # 包安装的所有文件列表
    paths_data = ComposableField(PathsData, required=False, nullable=True)  # 文件详细信息
    link = ComposableField(Link, required=False)             # 链接信息
    auth = StringField(required=False, nullable=True)        # 认证信息
```

其中 `SolvedRecord` 增加了 `requested_spec` / `requested_specs` 字段，记录用户直接请求的 MatchSpec（区别于作为依赖被拉入的包），用于 lockfile 和环境复现。

## Link 实体

`Link` 是一个简单的嵌入式实体，描述包如何链接到环境前缀中 [F-041]：

```python
class Link(DictSafeMixin, Entity):
    source = StringField()                                    # 源文件路径
    type = LinkTypeField(LinkType, required=False)            # 链接类型
```

链接类型由 `LinkType` 枚举定义 [F-042]：

```python
class LinkType(Enum):
    hardlink = 1   # 硬链接（默认，同文件系统，节省空间）
    softlink = 2   # 符号链接
    copy = 3       # 文件复制（跨文件系统时使用）
    directory = 4  # 目录
```

`PathEnum` 枚举用于 `paths.json` 中的路径类型标记，除了 basic_types（hardlink/softlink/directory）外，还包括 linked_package_record、pyc_file、unix/windows_python_entry_point 等特殊类型。

## 关键枚举类型

[F-042] 定义的枚举：

- **NoarchType**：`generic`（纯数据/脚本包）、`python`（纯 Python 包，架构无关），通过 `NoarchType.coerce()` 兼容 bool/str/None 多种输入
- **PackageType**：`NOARCH_GENERIC`, `NOARCH_PYTHON`, `VIRTUAL_SYSTEM`, `VIRTUAL_PRIVATE_ENV`, 以及多种 `VIRTUAL_PYTHON_*` 类型（egg/wheel 管理状态）；`conda_package_types()` 返回可安装的真实包类型集合，`unmanageable_package_types()` 返回不可管理的虚拟包类型
- **Platform**：`linux`, `win`(win32), `osx`(darwin), `freebsd`, `zos`, `emscripten`, `wasi`
- **Arch**：`x86`, `x86_64`, `arm64`, `aarch64`, `ppc64le`, `riscv64`, `s390x`, `wasm32` 等
- **FileMode**：`text`, `binary`

## 三级模型的生命周期映射

```
Channel (远端repodata)
    │  SubdirData 加载 repodata.json → 创建 PackageRecord
    ▼
PackageCache (本地 pkgs_dirs)
    │  下载+解压 → 创建 PackageCacheRecord（补充本地路径）
    ▼
Prefix (环境 conda-meta/)
    │  UnlinkLinkTransaction 链接文件 → 创建 PrefixRecord（补充 files/link/paths_data）
    ▼
已安装环境（prefix）
```

三级模型通过共享 `_pkey` 实现跨阶段的包身份一致性：求解器中混合使用 PackageRecord（远端候选）和 PrefixRecord（已安装）做 SAT 约束时，同一包天然相等，无需额外转换。已安装包的依赖关系图由 `PrefixGraph` 基于 PrefixRecord 构建，用于拓扑排序等操作 [F-043]。

## 与其他模型的关系

- PackageRecord 的 `channel` 字段使用 [Channel](03-channel-subdir.md) 类型
- PackageRecord 的 `depends`/`constrains` 字段存储 [MatchSpec](04-matchspec.md) 字符串
- MatchSpec 的 `version`/`build_number` 字段委托 [VersionOrder/VersionSpec](05-version-system.md) 比较
- [Index](08-index-and-repodata.md) 聚合四类来源的记录（Channels/Prefix/Cache/Virtual）形成统一索引
