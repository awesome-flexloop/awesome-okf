---
okf_version: "0.2"
type: "concept"
title: "源文件解析"
sources:
  - "conda_lock/src_parser/__init__.py"
  - "conda_lock/src_parser/environment_yaml.py"
  - "conda_lock/src_parser/selectors.py"
  - "conda_lock/src_parser/markers.py"
  - "conda_lock/src_parser/aggregation.py"
  - "conda_lock/src_parser/pyproject_toml.py"
  - "conda_lock/src_parser/meta_yaml.py"
---

# 源文件解析

源解析层负责将不同格式的输入文件转换为统一的 `LockSpecification` 模型。conda-lock 支持三种输入格式：`environment.yml`（Conda 标准环境文件）、`meta.yaml`（conda-build 配方文件）、`pyproject.toml`（PEP 621/Poetry 配置文件）。核心入口函数是 `make_lock_spec()`。

## make_lock_spec()：解析入口

```python
# conda_lock/src_parser/__init__.py

def make_lock_spec(
    src_files: List[Path],
    platforms: Optional[List[str]] = None,
    filtered_categories: Optional[Set[str]] = None,
) -> LockSpecification:
    """从源文件列表构建 LockSpecification。

    根据文件扩展名分派到对应解析器，然后聚合结果。
    filtered_categories: 如果指定，仅保留属于这些类别的依赖，
                        在解析后直接过滤 dependencies 字典。
    """
    specs = []
    for src in src_files:
        ext = src.suffix.lower()
        if ext in (".yml", ".yaml"):
            # 判断是 environment.yml 还是 meta.yaml
            if src.name == "meta.yaml" or _is_meta_yaml(src):
                spec = parse_meta_yaml(src, platforms=platforms)
            else:
                spec = parse_environment_yaml(src, platforms=platforms)
        elif ext == ".toml":
            spec = parse_pyproject_toml(src, platforms=platforms)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        if filtered_categories is not None:
            # 按类别过滤依赖
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

[F-001]

解析流程：
1. 按文件扩展名分派到对应解析器
2. 每个解析器独立解析，返回一个 LockSpecification
3. 如果指定了 `filtered_categories`，过滤每个 LockSpecification 的 dependencies
4. 调用 `aggregate_lock_specs()` 聚合多源规格

## environment_yaml.py：解析 environment.yml

environment.yml 是最常用的输入格式。解析器支持 Conda 标准字段和 conda-lock 扩展字段。

### 平台选择器（Platform Selectors）

```python
# conda_lock/src_parser/selectors.py

def filter_selector_lines(lines: List[str], platform: str) -> List[str]:
    """过滤 # [selector] 格式的条件注释行。

    支持的选择器：
    - 操作系统: linux, osx, win, unix
    - 架构: x86_64, x86, aarch64, arm64, ppc64le
    - 组合: linux64 (linux+x86_64), osx64, win64 等
    - 逻辑运算: not, and, or
    """
```

[F-002]

平台选择器允许在同一 environment.yml 中为不同平台声明不同依赖：

```yaml
dependencies:
  - python=3.10
  - numpy
  - llvm-openmp  # [osx]
  - libgomp      # [linux]
  - pywin32      # [win]
```

解析时，`selectors.py` 评估每行的选择器条件，为每个目标平台过滤出适用的依赖行。

### pip 子段解析

```yaml
dependencies:
  - python=3.10
  - pip:
      - requests>=2.28
      - pydantic[email]>=2.0
      - git+https://github.com/user/repo.git@main#egg=mypkg
```

[F-003]

pip 子段中的依赖解析为 `manager="pip"` 的 Dependency 对象：
- `requests>=2.28` → VersionedDependency(pip)
- `pydantic[email]>=2.0` → VersionedDependency(pip, extras=["email"])
- `git+https://...` → VCSDependency(pip)

### category 扩展字段

conda-lock 扩展了 environment.yml 格式，支持通过 `category:` 字段标记依赖类别：

```yaml
dependencies:
  - python=3.10
  - numpy
  - pytest:
      category: dev
  - black:
      category: dev
  - sphinx:
      category: docs
```

[F-004]

这些 category 字段在解析时设置 Dependency 的 category 属性，后续通过 `apply_categories()` BFS 传播到传递依赖。

### channels 和 pip-repositories 提取

```python
# conda_lock/src_parser/environment_yaml.py

def parse_environment_yaml(path, platforms=None) -> LockSpecification:
    with open(path) as f:
        data = yaml.safe_load(f)

    channels = [Channel.from_string(c) for c in data.get("channels", [])]
    pip_repositories = [
        PipRepository(url=url)
        for url in data.get("pip-repositories", [])
    ]
    # ... 解析 dependencies
```

[F-005]

## markers.py：PEP 508 环境标记评估

```python
# conda_lock/src_parser/markers.py

def evaluate_marker(marker: dict, platform: str, python_version: str) -> bool:
    """评估 PEP 508 环境标记，判断 pip 依赖是否适用于目标平台。

    支持的标记：
    - os_name: "posix"/"nt"
    - sys_platform: "linux"/"darwin"/"win32"
    - platform_machine: "x86_64"/"aarch64"/"arm64"
    - platform_system: "Linux"/"Darwin"/"Windows"
    - python_version: 如 "3.10"
    - implementation_name: "cpython"/"pypy"
    """
```

[F-006]

PEP 508 环境标记用于 pip 依赖的条件安装，例如：

```
requests>=2.28; python_version >= "3.10"
pywin32>=300; sys_platform == "win32"
```

解析器为每个目标平台和 Python 版本评估这些标记，过滤出适用的 pip 依赖。

## pyproject_toml.py：解析 pyproject.toml

```python
# conda_lock/src_parser/pyproject_toml.py

def parse_pyproject_toml(path, platforms=None) -> LockSpecification:
    """解析 pyproject.toml，支持 PEP 621 和 Poetry 两种格式。

    通过 grayskull 策略将 Poetry/PEP 621 依赖映射为 conda 依赖。
    """
    with open(path) as f:
        data = tomllib.load(f)

    # 优先使用 PEP 621 [project] 段
    if "project" in data:
        deps = data["project"].get("dependencies", [])
        optional_deps = data["project"].get("optional-dependencies", {})
    # 回退到 Poetry [tool.poetry] 段
    elif "tool" in data and "poetry" in data["tool"]:
        deps = data["tool"]["poetry"].get("dependencies", {})
        optional_deps = data["tool"]["poetry"].get("dev-dependencies", {})

    # 通过 grayskull 将 PyPI 包名映射为 conda 包名
    # 例如: "scikit-learn" (PyPI) → "scikit-learn" (conda, 同名)
    #       "Pillow" (PyPI) → "pillow" (conda, 小写)
    #       "pyyaml" (PyPI) → "pyyaml" (conda)
    conda_deps = _map_pypi_to_conda_deps(deps)
    pip_deps = _extract_pip_only_deps(deps)  # 无法映射的保留为pip
```

[F-007]

包名映射通过 vendored 的 grayskull 映射数据（`lookup.py`/`lookup_cache.py`）完成，将 PyPI 包名转换为对应的 conda-forge 包名。对于无法映射的包（如纯 Python 包、私有包），保留为 pip 依赖。

## meta_yaml.py：解析 conda-build meta.yaml

```python
# conda_lock/src_parser/meta_yaml.py

def parse_meta_yaml(path, platforms=None) -> LockSpecification:
    """解析 conda-build 的 meta.yaml 配方文件。

    提取 run/host 依赖，支持 Jinja2 模板变量解析（简化版）。
    """
```

[F-008]

meta.yaml 是 conda-build 的包配方格式，`requirements.run` 和 `requirements.host` 段定义运行时和构建时依赖。解析器提取 run 依赖作为锁定目标。

## aggregation.py：多源文件聚合

```python
# conda_lock/src_parser/aggregation.py

def aggregate_lock_specs(specs: List[LockSpecification]) -> LockSpecification:
    """聚合多个 LockSpecification 为一个统一规格。

    聚合规则：
    - channels: 有序去重并集（保持首次出现顺序）
    - dependencies: 按平台合并依赖列表
    - sources: 合并所有源文件路径
    - pip_repositories: 合并所有 PyPI 仓库
    - allow_pypi_requests: 取 AND（任一禁用则禁用）
    """
    # 通道有序并集
    all_channels = ordered_union([s.channels for s in specs])

    # 按平台合并依赖
    all_deps = {}
    for spec in specs:
        for platform, deps in spec.dependencies.items():
            if platform not in all_deps:
                all_deps[platform] = []
            all_deps[platform].extend(deps)

    # 源文件合并
    all_sources = ordered_union([s.sources for s in specs])

    return LockSpecification(
        dependencies=all_deps,
        channels=all_channels,
        sources=all_sources,
        pip_repositories=...,
        allow_pypi_requests=all(s.allow_pypi_requests for s in specs),
    )
```

[F-009]

聚合使用 `common.py` 中的 `ordered_union()` 函数实现有序去重并集，保持元素的首次出现顺序——这对 channels 很重要，因为通道顺序决定优先级。

## 解析流程总览

```
environment.yml ──→ environment_yaml.parse_environment_yaml() ──┐
meta.yaml ────────→ meta_yaml.parse_meta_yaml() ────────────────┤
pyproject.toml ───→ pyproject_toml.parse_pyproject_toml() ──────┤
                                                                 │
         每个解析器内部：                                         │
         ┌───────────────────────────────────────┐              │
         │ selectors.filter_selector_lines()     │              │
         │ → 按平台过滤条件行                      │              │
         │ markers.evaluate_marker()             │              │
         │ → 评估PEP 508标记                     │              │
         │ lookup/grayskull 包名映射              │              │
         │ → PyPI包名→conda包名                  │              │
         └───────────────┬───────────────────────┘              │
                         │                                      │
                         ▼                                      │
                  单个 LockSpecification                        │
                         │                                      │
                         ▼                                      │
           aggregation.aggregate_lock_specs() ◄─────────────────┘
                         │
                         ▼
                 聚合后的 LockSpecification
                         │
                         ▼
                    conda_solver / pypi_solver
```

## 相关概念

- [LockSpecification 模型](03-lock-specification.md)
- [四类依赖模型](05-dependency-types.md)
- [Conda 求解器](08-conda-solver.md)
- [PyPI 求解器](09-pypi-solver.md)
- [依赖类别与传播](14-categories-and-deps.md)
