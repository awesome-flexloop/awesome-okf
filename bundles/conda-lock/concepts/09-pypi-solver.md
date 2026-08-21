---
okf_version: "0.2"
type: "concept"
title: "PyPI 求解器"
sources:
  - "conda_lock/pypi_solver.py"
  - "conda_lock/lookup.py"
  - "conda_lock/lookup_cache.py"
  - "conda_lock/interfaces/vendored_poetry/"
---

# PyPI 求解器

conda-lock 支持在 conda 环境中同时锁定 pip 包（来自 PyPI）。与 conda 求解器委托外部 conda 进程不同，PyPI 求解器使用 **vendored 的 Poetry 求解器**在进程内进行依赖解析。求解时模拟目标平台环境（操作系统、Python 版本、实现类型），确保 pip 依赖的解析结果与目标平台兼容。

## 双求解器架构

conda-lock 使用两个独立的求解器分别处理 conda 包和 pip 包：

```
LockSpecification.dependencies
       │
       ├─ manager="conda" → conda_solver.solve_conda()
       │                     （调用 conda/mamba dry-run）
       │
       └─ manager="pip"   → pypi_solver.solve_pypi()
                             （vendored Poetry 求解器）
                                          │
                                          ▼
                              结果合并到统一锁文件
```

[F-001]

conda 求解器负责解析 conda 包及其 conda 传递依赖，PyPI 求解器负责解析 pip 包及其 pip 传递依赖。两者独立求解，最终结果合并到同一锁文件中。

## Poetry 求解器集成

conda-lock 在 `interfaces/vendored_poetry/` 目录下 vendor 了 Poetry 的依赖求解器组件：

```
interfaces/vendored_poetry/
├── mixology/           # Poetry 的版本求解算法（基于 PubGrub）
├── packages/           # 包元数据模型
├── puzzle/             # 求解器核心（Provider/Solver）
└── repositories/       # PyPI 仓库访问（含 Pool/Repository）
```

[F-002]

vendor 策略避免了运行时对 Poetry Python 包的依赖，同时确保求解行为与 Poetry 生态一致。

## 目标平台环境模拟

求解 pip 依赖时，需要模拟目标平台的环境参数，因为某些 pip 包有平台限制（如 Windows 专属包、特定 Python 版本的 wheel 等）：

```python
# conda_lock/pypi_solver.py

def solve_pypi(
    specs: List[VersionedDependency],
    platform: str,
    python_version: str,
    pool: "RepositoryPool",
    categories: Set[str] = {"main"},
) -> List[VersionedDependency]:
    """使用 Poetry 求解器解析 PyPI 依赖。

    参数:
        specs: pip 依赖列表
        platform: 目标平台 (linux-64/osx-arm64/win-64 等)
        python_version: 目标 Python 版本 (如 "3.10.12")
        pool: PyPI 仓库池
    """
    # 1. 根据平台映射环境标记
    env = _build_environment_markers(platform, python_version)

    # 2. 创建 Poetry SolverProvider
    provider = CondaLockProvider(
        pool=pool,
        env=env,
        conda_deps=conda_deps,  # 已由 conda 求解的包（避免重复求解）
    )

    # 3. 初始化求解器并求解
    solver = Solver(provider)
    packages = solver.solve([_poetry_requirement(dep) for dep in specs])

    # 4. 转换为 VersionedDependency 列表
    return [_to_versioned_dep(pkg) for pkg in packages]
```

[F-003]

### 环境映射

| conda 平台 | os_name | sys_platform | platform_machine | platform_system |
|-----------|---------|-------------|-----------------|----------------|
| linux-64 | posix | linux | x86_64 | Linux |
| linux-aarch64 | posix | linux | aarch64 | Linux |
| osx-64 | posix | darwin | x86_64 | Darwin |
| osx-arm64 | posix | darwin | arm64 | Darwin |
| win-64 | nt | win32 | AMD64 | Windows |

[F-004]

## conda↔pip 包名映射（lookup_cache）

conda 和 PyPI 对同一个包可能使用不同的名称。conda-lock 使用 grayskull 的映射数据处理名称转换：

```python
# conda_lock/lookup_cache.py

class LookupCache:
    """conda 包名 ↔ PyPI 包名映射缓存。"""

    def conda_name(self, pypi_name: str) -> str:
        """将 PyPI 包名转换为 conda 包名。"""
        ...

    def pypi_name(self, conda_name: str) -> str:
        """将 conda 包名转换为 PyPI 包名。"""
        ...
```

[F-005]

常见映射示例：

| PyPI 名称 | conda-forge 名称 | 说明 |
|----------|-----------------|------|
| Pillow | pillow | 大小写不同 |
| scikit-learn | scikit-learn | 相同 |
| PyYAML | pyyaml | 大小写不同 |
| opencv-python | opencv | 完全不同 |
| torch | pytorch | 不同名称 |

映射数据通过 `lookup.py` 从 grayskull 项目加载，使用缓存避免重复查询。

## 避免重复求解：conda 优先

一个关键设计：已由 conda 求解的包不应再被 pip 重新安装。求解 pip 依赖时，将 conda 已解析的包作为"已满足"传入 Poetry 求解器：

```python
# 伪代码：conda 包"告知" pip 求解器它们已存在
conda_resolved = conda_solver.solve_conda(spec)
conda_package_names = {dep.name for deps in conda_resolved.values() for dep in deps}

pip_resolved = pypi_solver.solve_pypi(
    pip_specs,
    platform=platform,
    python_version=python_version,
    already_installed=conda_package_names,  # 这些包已被 conda 满足
)
```

[F-006]

这避免了 pip 拉取 conda 已安装包的 PyPI 版本（如 numpy），导致版本冲突或二进制不兼容。

## PEP 508 环境标记评估

pip 依赖可能包含 PEP 508 环境标记（如 `; python_version >= "3.10"` 或 `; sys_platform == "win32"`）。这些标记由 `src_parser/markers.py` 中的 `evaluate_marker()` 函数评估，在进入求解器之前就过滤掉不适用的依赖：

```python
# conda_lock/src_parser/markers.py

def evaluate_marker(marker: dict, platform: str, python_version: str) -> bool:
    """评估 PEP 508 环境标记表达式。

    支持逻辑运算符 and/or/not，比较运算符 ==/!=/</>/<=/>=，
    以及 in/not in 运算符。
    """
```

[F-007]

## 私有 PyPI 仓库

`LockSpecification.pip_repositories` 字段配置私有 PyPI 仓库：

```python
class PipRepository(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
```

[F-008]

这些配置传递给 Poetry 的 RepositoryPool，使求解器从私有索引获取包元数据。与 conda Channel 类似，凭证通过环境变量安全传递。

## 求解结果合并

conda 求解器和 PyPI 求解器的结果最终合并为锁文件中的 `package` 列表：

```python
# 伪代码
all_packages = []
for platform in platforms:
    # conda 包
    all_packages.extend(conda_resolved[platform])
    # pip 包
    all_packages.extend(pip_resolved[platform])

lockfile = Lockfile(
    version=2,
    package=all_packages,
    metadata=LockMeta(content_hash=content_hashes, ...),
)
```

[F-009]

在锁文件中，conda 包的 `manager: conda`，pip 包的 `manager: pip`，安装时根据 manager 字段决定使用 conda 还是 pip 安装。

## allow_pypi_requests 开关

`LockSpecification.allow_pypi_requests` 控制是否允许向 PyPI 发送网络请求 [F-010]。设为 `False` 时：
- pip 依赖求解被禁用
- 适用于离线环境或严格网络管控
- 仅锁定 conda 包

## 相关概念

- [Conda 求解器](08-conda-solver.md)
- [四类依赖模型](05-dependency-types.md)
- [源文件解析](07-source-parsers.md)
- [LockSpecification 模型](03-lock-specification.md)
- [Conda 调用层](13-invoke-conda.md)
