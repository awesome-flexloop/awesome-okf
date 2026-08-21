---
okf_version: "0.2"
type: "concept"
title: "锁文件 v1/v2 格式"
sources:
  - "conda_lock/lockfile/__init__.py"
  - "conda_lock/lockfile/v1/models.py"
  - "conda_lock/lockfile/v2prelim/models.py"
---

# 锁文件 v1/v2 格式

conda-lock 支持两种锁文件格式版本：v1 和 v2。v1 使用单个字符串 category 字段，每个包只能属于一个类别；v2 使用 categories 集合，一个包可以同时属于多个类别（如同时是 main 和 dev 的依赖）。锁文件读写时自动识别版本并处理转换。

## LockedDependency 字段（v1 vs v2）

### v1 格式

```python
# conda_lock/lockfile/v1/models.py

class BaseLockedDependency(BaseModel):
    name: str
    version: str
    manager: str               # "conda" 或 "pip"
    platform: str              # 平台标识
    dependencies: Dict[str, str] = {}  # 传递依赖 name→version 映射
    url: str                   # 包下载 URL
    hash: HashModel            # 哈希校验
    source: Optional[str] = None  # 来源文件
    build: Optional[str] = None   # conda build 字符串

class LockedDependency(BaseLockedDependency):
    category: str = "main"     # 单字符串类别
    optional: bool = False     # 是否可选

class HashModel(BaseModel):
    md5: Optional[str] = None  # conda 包使用 MD5
    sha256: Optional[str] = None  # pip 包使用 SHA256
```

[F-001]

v1 的 `category` 是单个字符串，每个依赖记录只能标记一个类别。这导致一个问题：如果包 A 同时是 main 和 dev 的传递依赖，在 v1 中需要存储两条记录（一条 category=main，一条 category=dev），造成冗余。

### v2 格式

```python
# conda_lock/lockfile/v2prelim/models.py

class LockedDependency(BaseLockedDependency):
    categories: Set[str] = {"main"}  # 类别集合，支持多类别
```

[F-002]

v2 的核心变化是将 `category: str` 改为 `categories: Set[str]`，一个包可以同时属于多个类别。例如 `pytest` 可能直接属于 dev，但它的传递依赖（如 `packaging`）同时属于 main 和 dev，只需一条记录 `categories={"main", "dev"}`。

## LockMeta 元数据

```python
# conda_lock/lockfile/v1/models.py

class LockMeta(BaseModel):
    content_hash: Dict[str, str] = {}  # 平台→内容哈希映射
    channels: List[Dict] = []          # 通道列表（含URL和env vars）
    platforms: List[str] = []          # 目标平台列表
    sources: List[str] = []            # 源文件路径
    time_metadata: Optional[dict] = None     # 时间戳元数据
    git_metadata: Optional[dict] = None      # Git 信息（SHA/作者等）
    inputs_metadata: Optional[dict] = None   # 输入文件哈希
    custom_metadata: Optional[dict] = None   # 自定义元数据

class MetadataOption(Enum):
    TimeStamp = "timestamp"
    GitSha = "git_sha"
    GitUserName = "git_user_name"
    GitUserEmail = "git_user_email"
    InputMd5 = "input_md5"
    InputSha = "input_sha"
```

[F-003]

元数据记录锁文件的生成上下文，支持审计和溯源：
- `content_hash`：每个平台的输入内容哈希，用于快速检测是否需要重新锁定
- `channels`：使用的通道列表，包含脱敏后的 URL 和环境变量引用
- `sources`：参与锁定的源文件路径
- `time_metadata`/`git_metadata`：生成时间和 Git 版本信息（可选，通过命令行选项控制）

## Lockfile 顶层结构

```python
# v1
class Lockfile(BaseModel):
    version: int = 1
    package: List[LockedDependency] = []
    metadata: LockMeta = LockMeta()

# v2
class Lockfile(BaseModel):
    version: int = 2
    package: List[LockedDependency] = []
    metadata: LockMeta = LockMeta()
```

[F-004]

v2 的 Lockfile 额外提供 `merge()` 和 `toposort()` 方法：

```python
def merge(self, other: "Lockfile") -> "Lockfile":
    """合并两个锁文件（用于多源文件锁定）。"""
    ...

def toposort(self) -> List[LockedDependency]:
    """按依赖拓扑排序包列表，确保被依赖的包排在前面。"""
    ...
```

[F-005]

拓扑排序对于安装顺序很重要——conda 安装时需要先安装被依赖的包，避免依赖缺失。

## v1 ↔ v2 转换

```python
# conda_lock/lockfile/v2prelim/models.py

def lockfile_v1_to_v2(v1_lockfile) -> "Lockfile":
    """将 v1 锁文件转换为 v2 格式。

    v1 中同 key (manager, name, platform) 可能有多条不同 category 的记录，
    v2 将它们合并为一条记录，categories 为所有 category 的并集。
    """
    merged = {}
    for pkg in v1_lockfile.package:
        key = (pkg.manager, pkg.name, pkg.platform)
        if key in merged:
            merged[key].categories.add(pkg.category)
        else:
            merged[key] = LockedDependency(
                **pkg.dict(exclude={"category", "optional"}),
                categories={pkg.category} if not pkg.optional else set(),
            )
    return Lockfile(
        version=2,
        package=list(merged.values()),
        metadata=v1_lockfile.metadata,
    )

def to_v1(self) -> "v1_models.Lockfile":
    """将 v2 锁文件转换为 v1 格式。

    categories 集合展开为多条单 category 记录。
    """
    v1_packages = []
    for pkg in self.package:
        for cat in pkg.categories:
            v1_packages.append(v1_models.LockedDependency(
                **pkg.dict(exclude={"categories"}),
                category=cat,
                optional=False,
            ))
    return v1_models.Lockfile(
        version=1,
        package=v1_packages,
        metadata=self.metadata,
    )
```

[F-006]

转换逻辑清晰：
- **v1→v2**：按 (manager, name, platform) 三元组去重，category 合并到 categories 集合
- **v2→v1**：每个 category 展开为一条独立记录

## 锁文件读写

```python
# conda_lock/lockfile/__init__.py

def parse_conda_lock_file(path) -> Lockfile:
    """解析锁文件，自动识别 v1/v2 版本，v1 自动转换为 v2 内部表示。"""
    with open(path) as f:
        data = yaml.safe_load(f)
    version = data.get("version", 1)
    if version == 1:
        v1_lock = v1_models.Lockfile(**data)
        return lockfile_v1_to_v2(v1_lock)
    elif version == 2:
        return v2_models.Lockfile(**data)
    else:
        raise ValueError(f"Unknown lockfile version: {version}")

def write_conda_lock_file(lockfile: Lockfile, path, include_help_comment=True):
    """写入锁文件为 YAML 格式，包含帮助注释头。"""
    with open(path, "w") as f:
        if include_help_comment:
            f.write("# This lock file was generated by conda-lock.\n")
            f.write("# For more information, see https://github.com/conda/conda-lock\n")
        yaml.dump(lockfile.dict(), f, sort_keys=False)
```

[F-007]

**读取时自动升级**：无论磁盘上是 v1 还是 v2 格式，`parse_conda_lock_file()` 都返回 v2 的 Lockfile 对象（内部统一使用 v2）。写入时输出 v2 格式。

## 锁文件示例（v2 YAML 片段）

```yaml
version: 2
metadata:
  content_hash:
    linux-64: "abc123def456..."
    osx-arm64: "789abc012def..."
  channels:
    - url: "conda-forge"
  platforms:
    - linux-64
    - osx-arm64
  sources:
    - environment.yml
package:
  - name: python
    version: "3.10.12"
    manager: conda
    platform: linux-64
    dependencies:
      libffi: ">=3.4"
      openssl: ">=3.0"
    url: "https://conda.anaconda.org/conda-forge/linux-64/python-3.10.12-..."
    hash:
      md5: "d41d8cd98f00b204e9800998ecf8427e"
    build: "hd12c33a_0_cpython"
    categories:
      - main
  - name: numpy
    version: "1.24.4"
    manager: conda
    platform: linux-64
    dependencies:
      libgcc-ng: ">=12"
      python: ">=3.10"
    url: "https://conda.anaconda.org/conda-forge/linux-64/numpy-1.24.4-..."
    hash:
      md5: "a1b2c3d4e5f6..."
    categories:
      - main
      - dev
```

[F-008]

## apply_categories()：类别传播

```python
def apply_categories(
    lockfile: Lockfile,
    specs: Dict[str, List[Dependency]],
) -> Lockfile:
    """从显式依赖向传递依赖传播 category 标签。

    使用 BFS 遍历依赖树：如果一个显式依赖标记为 dev，
    则它的所有传递依赖也获得 dev category。
    """
```

[F-009]

传播算法：
1. 首先标记显式依赖（用户直接指定的包）的 category
2. BFS 遍历依赖图：对于每个包，将其 categories 传播给它的直接依赖
3. 最终 main category 的包通过 `_truncate_main_category()` 移除其他 category（main 优先）

```python
def _truncate_main_category(lockfile: Lockfile):
    """main category 的包移除其他 category。

    如果一个包属于 main（生产依赖），即使它也通过 dev 路径被依赖，
    它仍然只标记为 main。安装时选择安装 main，dev 依赖不会导致
    main 包重复安装。
    """
    for pkg in lockfile.package:
        if "main" in pkg.categories:
            pkg.categories = {"main"}
```

[F-010]

## 相关概念

- [四类依赖模型](05-dependency-types.md)
- [依赖类别与传播](14-categories-and-deps.md)
- [Conda 求解器](08-conda-solver.md)
- [内容哈希机制](12-content-hash.md)
