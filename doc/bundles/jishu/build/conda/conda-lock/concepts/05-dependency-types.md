---
okf_version: "0.2"
type: "concept"
title: "四类依赖模型"
sources:
  - "conda_lock/models/lock_spec.py"
  - "conda_lock/src_parser/environment_yaml.py"
  - "conda_lock/src_parser/pyproject_toml.py"
---

# 四类依赖模型

conda-lock 使用 Pydantic 模型表示依赖，通过四层继承体系和 TypeAlias 联合类型支持四种依赖定位方式：版本化依赖（VersionedDependency）、URL依赖（URLDependency）、VCS依赖（VCSDependency）和本地路径依赖（PathDependency）。

## 继承体系

```
_BaseDependency (公共基类)
├── VersionedDependency  — 名称+版本+build号指定
├── URLDependency        — 直接包文件 URL 指定
├── VCSDependency        — Git 等版本控制系统指定
└── PathDependency       — 本地文件系统路径指定
```

[F-001]

## _BaseDependency：公共基类

```python
# conda_lock/models/lock_spec.py

class _BaseDependency(BaseModel):
    name: str                           # 包名
    manager: str = "conda"              # 包管理器: "conda" 或 "pip"
    category: str = "main"              # 依赖类别: main/dev/test 等
    extras: Optional[List[str]] = None  # pip extras，如 ["dev", "docs"]
    markers: Optional[dict] = None      # PEP 508 环境标记
```

[F-002]

基类字段说明：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 包名称，是所有依赖类型的标识 |
| `manager` | str | `"conda"` | 区分 conda 包和 pip 包，决定求解路径 |
| `category` | str | `"main"` | 依赖类别，用于选择性安装（如 `--dev-dependencies`） |
| `extras` | List[str] | None | pip extras 标记，对应 PEP 508 的 `package[extra]` 语法 |
| `markers` | dict | None | PEP 508 环境标记（如 `python_version >= "3.10"`），用于判断 pip 依赖是否适用于目标平台 |

`manager` 字段是求解路由的关键：`manager="conda"` 的依赖走 `conda_solver`（调用 conda/mamba dry-run），`manager="pip"` 的依赖走 `pypi_solver`（Poetry 求解器）。

## VersionedDependency：版本化依赖

```python
class VersionedDependency(_BaseDependency):
    version: str = ""
    build: Optional[str] = None
    conda_channel: Optional[str] = None
    hash: Optional[str] = None
```

[F-003]

最常用的依赖类型，通过包名、版本约束和可选的构建号指定包：

```python
# conda 包
VersionedDependency(
    name="numpy",
    version=">=1.24",
    manager="conda",
    category="main",
)

# pip 包
VersionedDependency(
    name="requests",
    version=">=2.28.0",
    manager="pip",
    category="main",
)

# 带精确 build 和 hash（锁文件中）
VersionedDependency(
    name="python",
    version="3.10.12",
    build="hd12c33a_0_cpython",
    conda_channel="conda-forge",
    hash="d41d8cd98f00b204e9800998ecf8427e",
    manager="conda",
)
```

**字段说明**：
- `version`：版本约束字符串（如 `">=1.24"`、`"1.24.4"`、`""` 表示任意版本），求解后变为精确版本号
- `build`：conda 构建字符串（如 `"py310h43ef7f0_0"`），精确标识二进制构建变体
- `conda_channel`：来源通道名称，写入锁文件用于溯源
- `hash`：包哈希值（conda 包用 MD5，pip 包用 SHA256），用于安装时校验完整性

## URLDependency：直接 URL 依赖

```python
class URLDependency(_BaseDependency):
    url: str
    hashes: Optional[List[str]] = None
```

[F-004]

通过包文件的直接下载 URL 指定依赖，不经过通道索引：

```python
URLDependency(
    name="my-private-pkg",
    url="https://example.com/conda/my-private-pkg-1.0-py310_0.tar.bz2",
    hashes=["md5:d41d8cd98f00b204e9800998ecf8427e"],
    manager="conda",
)
```

URL 依赖绕过 conda 通道索引，直接从指定 URL 下载。适用于私有包、本地临时包、或未发布到通道的包。`hashes` 字段支持多个哈希算法的校验值。

## VCSDependency：版本控制依赖

```python
class VCSDependency(_BaseDependency):
    source: str = "git"    # VCS 类型，目前仅支持 git
    vcs: str = ""          # VCS URL
    rev: Optional[str] = None        # commit/branch/tag
    subdirectory: Optional[str] = None  # 子目录
```

[F-005]

通过 Git 等版本控制系统指定 pip 依赖（对应 pip 的 VCS 安装功能）：

```python
VCSDependency(
    name="my-package",
    source="git",
    vcs="https://github.com/user/my-package.git",
    rev="main",
    manager="pip",
)
```

VCS 依赖仅适用于 pip 包（conda 包不支持 VCS 直接安装）。`rev` 字段锁定到特定 commit/branch/tag 确保可重现性。

## PathDependency：本地路径依赖

```python
class PathDependency(_BaseDependency):
    path: str
    is_directory: bool = False
    subdirectory: Optional[str] = None
```

[F-006]

通过本地文件系统路径指定依赖，对应 pip 的可编辑安装或本地包安装：

```python
# 本地 wheel 文件
PathDependency(
    name="my-local-pkg",
    path="./dist/my_local_pkg-1.0-py3-none-any.whl",
    manager="pip",
)

# 本地目录（可编辑安装）
PathDependency(
    name="my-project",
    path="./src/my-project",
    is_directory=True,
    manager="pip",
)
```

## Dependency 联合类型

```python
Dependency = Union[VersionedDependency, URLDependency, VCSDependency, PathDependency]
```

[F-007]

`Dependency` 是四种依赖类型的 TypeAlias 联合。在 Pydantic 模型中，通过字段判别自动区分具体类型——Pydantic v2 使用 `discriminator` 字段或基于存在字段的智能Union来解析正确的子类。

```python
# LockSpecification.dependencies 的类型是 Dict[str, List[Dependency]]
# 列表中可以混合四种依赖类型
deps = [
    VersionedDependency(name="numpy", version="1.24", manager="conda"),
    VersionedDependency(name="requests", version="2.28", manager="pip"),
    URLDependency(name="private-pkg", url="https://.../pkg.tar.bz2", manager="conda"),
    VCSDependency(name="my-lib", vcs="https://...", rev="abc123", manager="pip"),
    PathDependency(name="local-pkg", path="./local", is_directory=True, manager="pip"),
]
```

## 从源文件到 Dependency

源解析器根据输入文件中的依赖描述创建相应类型的 Dependency：

| 源文件格式 | 依赖写法 | 创建的 Dependency 类型 |
|-----------|---------|---------------------|
| environment.yml | `- numpy>=1.24` | VersionedDependency(conda) |
| environment.yml | `pip: - requests>=2.28` | VersionedDependency(pip) |
| environment.yml | `- ./local-pkg` | PathDependency |
| pyproject.toml (Poetry) | `numpy = "^1.24"` | VersionedDependency(conda，经grayskull映射) |
| pyproject.toml | `git = "https://..."` | VCSDependency(pip) |
| pip 依赖 | 直接 URL | URLDependency(pip) |

[F-008]

## 求解前后的区别

值得注意的是，Dependency 模型在求解前后承载不同的信息：

- **求解前**（源解析输出）：VersionedDependency 的 `version` 是约束字符串（如 `">=1.24"`），`build`/`hash`/`conda_channel` 为空
- **求解后**（锁文件内容）：VersionedDependency 的 `version` 是精确版本（如 `"1.24.4"`），`build`/`hash`/`conda_channel` 填充求解结果

锁文件层的 `LockedDependency` 模型在此基础上增加了 `dependencies`（传递依赖列表）、`url`（下载URL）、`platform` 等字段。

## 相关概念

- [LockSpecification 模型](03-lock-specification.md)
- [Channel 与凭证安全](04-channel-model.md)
- [锁文件 v1/v2 格式](06-lockfile-formats.md)
- [源文件解析](07-source-parsers.md)
