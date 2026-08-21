---
okf_version: "0.2"
type: "concept"
title: "LockSpecification 模型"
sources:
  - "conda_lock/models/lock_spec.py"
  - "conda_lock/src_parser/__init__.py"
  - "conda_lock/src_parser/aggregation.py"
---

# LockSpecification 模型

`LockSpecification` 是 conda-lock 的核心数据模型，承载从源文件解析到求解器输入之间的完整中间状态。它将一个或多个环境规格文件解析后的结果聚合为统一的数据结构，包含按平台分组的依赖字典、通道列表、源文件追踪、PyPI 仓库配置等信息。

## 模型结构

```python
# conda_lock/models/lock_spec.py

class LockSpecification(BaseModel):
    dependencies: Dict[str, List[Dependency]]
    channels: List[Channel] = []
    sources: List[str] = []
    pip_repositories: List[PipRepository] = []
    allow_pypi_requests: bool = True
```

[F-001]

### dependencies：按平台分组的依赖字典

`dependencies` 是一个字典，key 为目标平台标识字符串（如 `"linux-64"`、`"osx-arm64"`、`"win-64"`），value 为该平台需要求解的 `Dependency` 列表。

```python
# 示例：两个平台的依赖结构
spec = LockSpecification(
    dependencies={
        "linux-64": [
            VersionedDependency(name="python", version="3.10", manager="conda"),
            VersionedDependency(name="numpy", version=">=1.24", manager="conda"),
            VersionedDependency(name="requests", version=">=2.28", manager="pip"),
        ],
        "osx-arm64": [
            VersionedDependency(name="python", version="3.10", manager="conda"),
            VersionedDependency(name="numpy", version=">=1.24", manager="conda"),
            VersionedDependency(name="requests", version=">=2.28", manager="pip"),
            # macOS 可能有平台特定依赖，通过 platform selectors 自动过滤
        ],
    },
    channels=[Channel.from_string("conda-forge")],
    sources=["environment.yml"],
)
```

[F-002]

**设计要点**：平台选择器（`# [linux]` 等条件注释）在源解析阶段已经处理完毕，每个平台的依赖列表已经预先过滤。求解器层无需再关心平台条件逻辑，直接按平台遍历字典即可。

### channels：通道列表

`channels` 是 `Channel` 对象的有序列表，按优先级排列。Channel 是不可变 Pydantic 模型（`frozen=True`），自动处理凭证安全（详见 [Channel 与凭证安全](04-channel-model.md)）。

```python
channels = [
    Channel.from_string("conda-forge"),
    Channel.from_string("https://conda.anaconda.org/t/$MY_TOKEN/my-private-channel"),
    Channel.from_string("https://user:pass@private.conda.com/channel"),
]
```

[F-003]

通道在求解时通过 `--override-channels --channel <url>` 参数传给 conda/mamba，确保使用精确指定的通道集合而非用户配置中的默认通道。

### sources：源文件追踪

`sources` 记录参与锁定的所有源文件路径，写入锁文件的 metadata 中用于审计溯源。多源文件聚合时，每个文件路径都会被记录。

```python
# 多源文件聚合时
spec = make_lock_spec([
    "environment.yml",
    "pyproject.toml",
    "dev-environment.yml",
])
# spec.sources == ["environment.yml", "pyproject.toml", "dev-environment.yml"]
```

[F-004]

### pip_repositories：PyPI 私有仓库

`pip_repositories` 列表配置 PyPI 私有仓库（用于企业内部 PyPI 镜像）。这些配置传递给 pip 求解器，使其从私有索引而非公共 PyPI 获取包信息。

### allow_pypi_requests：PyPI 请求开关

布尔标志，控制是否允许向 PyPI 发送网络请求。设为 `False` 时，pip 依赖求解被禁用，仅锁定 conda 包。适用于离线环境或严格管控的网络环境。

## platforms 属性

```python
@property
def platforms(self) -> List[str]:
    """返回所有目标平台，从 dependencies 字典的 key 提取。"""
    return list(self.dependencies.keys())
```

[F-005]

便捷属性，从 `dependencies` 字典的键提取平台列表。求解器层通过此属性知道需要为哪些平台求解。

## 构建过程

`LockSpecification` 通过 `src_parser.make_lock_spec()` 构建 [F-006]：

```
输入文件路径列表
      │
      ▼
┌─────────────────────┐
│ 根据扩展名分派解析器  │
│ .yml/.yaml → environment_yaml │
│ meta.yaml  → meta_yaml        │
│ .toml      → pyproject_toml  │
└─────────┬───────────┘
          │ 每个文件解析为独立 LockSpecification
          ▼
┌─────────────────────┐
│ aggregate_lock_specs()  │
│ - 通道合并(有序去重)     │
│ - 依赖合并(按平台分组)   │
│ - sources 合并          │
│ - pip_repositories 合并 │
└─────────┬───────────┘
          │
          ▼
   聚合后的 LockSpecification
```

## 类别过滤机制

类别过滤不是通过 `LockSpecification` 上的方法实现的，而是在构建阶段由 `src_parser.make_lock_spec()` 函数的 `filtered_categories` 参数完成。当 CLI 传入 `--dev-dependencies`、`--extras`（lock/render 命令）或 `--dev`、`--extras`（install 命令）时，解析器会计算出目标类别集合，在构建 `LockSpecification` 时直接过滤 dependencies 字典，仅保留属于目标类别的依赖。

```python
# conda_lock/src_parser/__init__.py
def make_lock_spec(
    src_files: List[Path],
    platforms: Optional[List[str]] = None,
    filtered_categories: Optional[Set[str]] = None,
) -> LockSpecification:
    """从源文件列表构建 LockSpecification。

    filtered_categories: 如果指定，仅保留属于这些类别的依赖；
                        None 表示保留所有类别。
    """
    specs = []
    for src in src_files:
        # ... 分派解析器解析每个文件
        spec = _parse_src(src, platforms=platforms)
        if filtered_categories is not None:
            # 直接过滤 dependencies 字典
            filtered_deps = {}
            for platform, deps in spec.dependencies.items():
                filtered_deps[platform] = [
                    d for d in deps if d.category in filtered_categories
                ]
            spec = LockSpecification(
                dependencies=filtered_deps,
                channels=spec.channels,
                sources=spec.sources,
                pip_repositories=spec.pip_repositories,
                allow_pypi_requests=spec.allow_pypi_requests,
            )
        specs.append(spec)
    return aggregate_lock_specs(specs)
```

[F-007]

此过滤机制用于实现命令行的类别控制选项。例如：
- `lock --dev-dependencies` 传入 `filtered_categories={"main", "dev"}`，保留主依赖和开发依赖
- 默认锁定（不加类别选项）传入 `filtered_categories={"main"}`，仅保留主依赖
- `install --dev --extras test` 传入 `filtered_categories={"main", "dev", "test"}`
- install 命令在安装阶段对已有的锁文件包记录执行类似的类别过滤

## 在数据流中的位置

LockSpecification 位于架构的核心枢纽位置：

```
源文件 → src_parser → LockSpecification → conda_solver/pypi_solver → 锁文件
```

它是源解析层和求解层之间的数据契约。源解析层负责构建正确的 LockSpecification，求解层只消费 LockSpecification 而不关心输入格式。

## 相关概念

- [四类依赖模型](05-dependency-types.md)
- [Channel 与凭证安全](04-channel-model.md)
- [源文件解析](07-source-parsers.md)
- [Conda 求解器](08-conda-solver.md)
- [锁文件 v1/v2 格式](06-lockfile-formats.md)
