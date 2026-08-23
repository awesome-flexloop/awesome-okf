---
okf_version: "0.2"
type: reference
title: "Conda 求解器 (conda_solver.py)"
sources:
  - "conda_lock/conda_solver.py"
  - "conda_lock/invoke_conda.py"
  - "conda_lock/models/lock_spec.py"
---

# Conda 求解器 (conda_solver.py)

conda-lock 不自实现依赖求解算法，而是通过调用 conda/mamba/micromamba 的 `create --dry-run --json` 命令获取求解结果，然后从 JSON 输出中解析出包安装计划。核心函数 `solve_conda()` 对每个目标平台依次调用 `solve_specs_for_arch()` 获取该平台的求解结果。

## solve_conda() — 顶层求解入口

```python
# conda_lock/conda_solver.py

from typing import Dict, List
from .models.lock_spec import LockSpecification, Dependency, VersionedDependency

def solve_conda(
    spec: LockSpecification,
    conda: str = "conda",
    platforms: List[str] | None = None,
) -> Dict[str, List[VersionedDependency]]:
    """对每个目标平台求解 conda 依赖，返回平台→VersionedDependency列表的映射。"""
    from .invoke_conda import determine_conda_executable
    conda_executable = determine_conda_executable(conda)

    platforms = platforms or spec.platforms
    result = {}
    for platform in platforms:
        deps = solve_specs_for_arch(
            conda=conda_executable,
            platform=platform,
            channels=spec.channels,
            specs=spec.dependencies[platform],
        )
        result[platform] = deps
    return result
```

**设计要点**：
- 对每个平台独立求解，结果按平台分组存储在字典中。
- 求解器可执行文件通过 `ensureconda` 自动发现（conda/mamba/micromamba），无需硬编码路径。

## solve_specs_for_arch() — 单平台 dry-run 求解

```python
# conda_lock/conda_solver.py

import json
import tempfile
from pathlib import Path
from .invoke_conda import _invoke_conda, conda_pkgs_dir
from .models.lock_spec import VersionedDependency, Channel

def solve_specs_for_arch(
    conda: str,
    platform: str,
    channels: List[Channel],
    specs: List[Dependency],
    virtual_package_spec=None,
) -> List[VersionedDependency]:
    """通过 conda create --dry-run --json 获取单平台求解结果。"""

    # 1. 将 Dependency 转换为 MatchSpec 字符串
    match_specs = [_to_match_spec(dep) for dep in specs if dep.manager == "conda"]

    # 2. 设置虚拟包环境（构造假的 repodata 注入系统依赖）
    with virtual_package_spec as fake_repo:
        # 3. 构建 conda 命令行
        args = [
            conda, "create", "--prefix", str(temp_dir),
            "--dry-run", "--json", "--override-channels",
        ]
        for ch in channels:
            args.extend(["--channel", ch.env_replaced_url()])

        # 添加虚拟包 repodata 作为额外通道
        if fake_repo:
            args.extend(["--channel", f"file://{fake_repo}"])

        args.extend(match_specs)

        # 4. 执行命令，解析 JSON 输出
        with conda_pkgs_dir() as pkgs_dir:
            env = conda_env_override(platform, pkgs_dir)
            output = _invoke_conda(args, env=env)
            dry_run_result = json.loads(output)

    # 5. 从 LINK actions 解析 VersionedDependency 列表
    dependencies = []
    link_actions = dry_run_result.get("actions", {}).get("LINK", [])
    fetch_actions = dry_run_result.get("actions", {}).get("FETCH", [])

    # 如果没有 FETCH（包从缓存链接），从 LINK 重建 FETCH
    if not fetch_actions and link_actions:
        fetch_actions = _reconstruct_fetch_actions(link_actions)

    for pkg_info in link_actions:
        dep = VersionedDependency(
            name=pkg_info["name"],
            version=pkg_info["version"],
            manager="conda",
            category="main",
            build=pkg_info.get("build", ""),
            conda_channel=pkg_info.get("channel", ""),
            hash=pkg_info.get("md5", ""),
        )
        dependencies.append(dep)

    return dependencies
```

**关键设计**：
- **dry-run 策略**：不实际创建环境，通过 `--dry-run --json` 获取求解计划，零副作用。
- **虚拟包注入**：通过 `VirtualPackage` 上下文管理器设置 CONDA_OVERRIDE_* 环境变量，并在临时目录构造假的 repodata.json 包含 __glibc/__cuda/__archspec 等系统依赖，确保求解结果包含正确的系统级约束。
- **FETCH/LINK 重建**：当包已在本地缓存中时，conda 只报告 LINK action 不报告 FETCH action；`_reconstruct_fetch_actions()` 从 LINK action 中提取必要信息重建 FETCH 记录，保证获取完整的下载元数据。

## update_specs_for_arch() — 增量更新

```python
# conda_lock/conda_solver.py

def update_specs_for_arch(
    conda: str,
    platform: str,
    channels: List[Channel],
    specs: List[Dependency],
    existing_lock_deps: List[VersionedDependency],
) -> List[VersionedDependency]:
    """基于已有锁文件进行增量更新，而非全量重新求解。"""

    with fake_conda_environment(existing_lock_deps, platform) as fake_prefix:
        # 在假环境中，已安装的包被 pinning 机制约束
        # mamba/libmamba 通过 pinned packages 限制更新范围
        args = [
            conda, "install", "--prefix", str(fake_prefix),
            "--dry-run", "--json", "--override-channels",
        ]
        for ch in channels:
            args.extend(["--channel", ch.env_replaced_url()])
        args.extend(_to_match_spec(dep) for dep in specs)

        # ... 执行命令并解析结果
```

**关键设计**：
- **fake_conda_environment()**：上下文管理器，在临时目录中构造包含 `conda-meta/` 目录的假 conda 环境，写入已有锁文件中每个包的 JSON 元数据记录。conda/mamba 读取这些元数据认为包已安装。
- **pinning 约束**：通过 conda 的 pinned packages 机制，将已安装的包版本写入 `<prefix>/conda-meta/pinned` 文件，限制求解器不随意升级这些包，仅在用户显式指定更新时才变更。
- **make_fake_python_binary()**：libmamba v2 在求解时会调用 `pip inspect` 检查已安装的 pip 包，如果找不到 python 二进制就会失败。该函数在假环境中创建一个最小的假 python 可执行文件来绕过此检查。

## _to_match_spec() — 依赖规格转换

```python
# conda_lock/conda_solver.py

def _to_match_spec(dep: VersionedDependency) -> str:
    """将 VersionedDependency 转换为 conda MatchSpec 字符串。"""
    parts = [dep.name]
    if dep.version:
        parts.append(dep.version)
    if dep.build:
        parts.append(f"={dep.build}")
    if dep.conda_channel:
        parts.append(f"channel::{dep.conda_channel}")
    return " ".join(parts) if len(parts) == 1 else "=".join(parts[:2])
```

**设计要点**：
- 将内部 `VersionedDependency` 模型转换为 conda 的 MatchSpec 字符串格式（`name=version=build`），用于传给 `conda create/install` 命令行。
- conda channel 前缀通过 `channel::name=version` 语法指定，确保从正确的通道获取包。
