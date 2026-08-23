---
okf_version: "0.2"
type: "concept"
title: "Conda 求解器"
sources:
  - "conda_lock/conda_solver.py"
  - "conda_lock/invoke_conda.py"
  - "conda_lock/virtual_package.py"
---

# Conda 求解器

conda-lock 的 conda 求解器采用"委托求解"策略：**不自实现依赖求解算法**，而是通过子进程调用 conda/mamba/micromamba 的 `create --dry-run --json` 命令获取求解结果。这一设计确保求解结果与实际 conda 安装行为完全一致，避免了维护 SAT 求解器的负担。

## 核心策略：dry-run 求解

```python
# conda_lock/conda_solver.py — 核心思路

def solve_specs_for_arch(conda, platform, channels, specs):
    """对单个平台执行 dry-run 求解。"""
    with tempfile.TemporaryDirectory() as tmp:
        args = [
            conda, "create", "--prefix", tmp,
            "--dry-run", "--json", "--override-channels",
        ]
        # 添加通道
        for ch in channels:
            args.extend(["--channel", ch.env_replaced_url()])
        # 添加 MatchSpec 字符串
        args.extend(_to_match_spec(d) for d in specs)

        # 设置 CONDA_SUBDIR 实现跨平台求解
        env = conda_env_override(platform)
        output = _invoke_conda(args, env=env)
        result = json.loads(output)

    # 从 actions.LINK 解析求解结果
    return _parse_link_actions(result)
```

[F-001]

**为什么用 dry-run？** `conda create --dry-run` 执行完整的依赖求解但不实际下载或安装包，JSON 输出中包含完整的安装计划（actions.LINK 和 actions.FETCH），列出每个包的名称、版本、build、channel、hash 等信息。这正是锁文件需要的精确数据。

## solve_conda()：顶层调度

```python
def solve_conda(spec: LockSpecification, conda: str = "conda"):
    """对所有目标平台依次求解，返回平台→依赖列表映射。"""
    conda_exec = determine_conda_executable(conda)
    result = {}
    for platform in spec.platforms:
        result[platform] = solve_specs_for_arch(
            conda=conda_exec,
            platform=platform,
            channels=spec.channels,
            specs=spec.dependencies[platform],
        )
    return result
```

[F-002]

对每个平台独立调用 `solve_specs_for_arch()`，结果按平台分组。平台循环内设置虚拟包环境和 CONDA_SUBDIR，确保跨平台求解正确。

## solve_specs_for_arch()：单平台求解详解

单平台求解的关键步骤：

1. **MatchSpec 转换**：将 `VersionedDependency` 转换为 conda MatchSpec 字符串格式（`name=version=build`）

2. **虚拟包注入**：通过 `VirtualPackage` 上下文管理器设置 CONDA_OVERRIDE_* 环境变量，并在临时目录构造包含虚拟包（__glibc/__cuda/__osx 等）的假 repodata.json，作为额外通道传给 conda

3. **子进程调用**：执行 `conda create --prefix <tmp> --dry-run --json --override-channels`，通过环境变量 CONDA_SUBDIR 指定目标平台

4. **结果解析**：从 JSON 输出的 `actions.LINK` 数组提取每个包的 name/version/build/channel/md5，构造 VersionedDependency 列表

[F-003]

### FETCH/LINK Actions 重建

conda dry-run 输出中有两种 action：

- **FETCH**：需要下载的包（不在本地缓存中）
- **LINK**：需要链接/安装到环境的包（包含所有包）

当包已在本地缓存中时，conda 可能只报告 LINK 而不报告 FETCH。此时需要从 LINK action 重建 FETCH 信息以获取完整的下载 URL：

```python
def _reconstruct_fetch_actions(link_actions):
    """当 FETCH 缺失时从 LINK 重建 FETCH 信息。"""
    fetch_actions = []
    for link in link_actions:
        fetch_actions.append({
            "name": link["name"],
            "version": link["version"],
            "build": link["build"],
            "url": _build_url_from_link(link),
            "md5": link.get("md5", ""),
        })
    return fetch_actions
```

[F-004]

## update_specs_for_arch()：增量更新

全量重新求解每次都从零开始，当已有锁文件时效率低下。增量更新通过"假环境"策略限制更新范围：

```python
def update_specs_for_arch(conda, platform, channels, specs, existing_lock_deps):
    """基于已有锁文件进行增量更新。"""
    with fake_conda_environment(existing_lock_deps, platform) as fake_prefix:
        # fake_conda_environment 在临时目录构造假 conda 环境：
        # 1. 创建 conda-meta/ 目录
        # 2. 为每个已锁定的包写入 JSON 元数据文件
        # 3. 创建 pinned 文件限制包版本

        args = [
            conda, "install", "--prefix", str(fake_prefix),
            "--dry-run", "--json", "--override-channels",
        ]
        for ch in channels:
            args.extend(["--channel", ch.env_replaced_url()])
        args.extend(_to_match_spec(d) for d in specs)

        env = conda_env_override(platform)
        output = _invoke_conda(args, env=env)
        result = json.loads(output)

    return _parse_link_actions(result)
```

[F-005]

### fake_conda_environment()：假环境构造

```python
@contextmanager
def fake_conda_environment(dependencies, platform):
    """在临时目录构造假的 conda 环境元数据。"""
    with tempfile.TemporaryDirectory() as tmp:
        prefix = Path(tmp)
        conda_meta = prefix / "conda-meta"
        conda_meta.mkdir()

        # 写入每个包的元数据 JSON（模拟已安装状态）
        for dep in dependencies:
            pkg_meta = conda_meta / f"{dep.name}-{dep.version}-{dep.build}.json"
            pkg_meta.write_text(json.dumps({
                "name": dep.name,
                "version": dep.version,
                "build": dep.build,
                "channel": dep.conda_channel,
                "files": [],
                "paths_data": {"paths": []},
            }))

        # 写入 pinned 文件限制版本
        pinned = conda_meta / "pinned"
        pinned.write_text("\n".join(
            f"{d.name} ={d.version}" for d in dependencies
        ))

        # 伪造 python 二进制（libmamba v2 需要）
        make_fake_python_binary(prefix)

        yield prefix
```

[F-006]

假环境让 conda/mamba 认为这些包已安装，结合 `conda install` 而非 `conda create`，求解器只计算需要更新的部分。pinned 文件进一步限制不更新用户未指定的包。

### make_fake_python_binary()：防 libmamba 失败

libmamba v2 在求解时会调用 `<prefix>/bin/python -m pip inspect` 检查已安装的 pip 包，如果找不到 python 可执行文件就会报错。`make_fake_python_binary()` 在假环境中创建一个最小的 python 可执行文件（shell 脚本或 Windows 批处理）来绕过此检查：

```python
def make_fake_python_binary(prefix: Path):
    """创建假 python 二进制防止 libmamba v2 的 pip inspect 检查失败。"""
    bin_dir = prefix / ("Scripts" if on_win else "bin")
    bin_dir.mkdir(parents=True, exist_ok=True)
    python_exe = bin_dir / ("python.exe" if on_win else "python")
    # 写入最小脚本，pip inspect 调用时返回空 JSON
    python_exe.write_text(...)
```

[F-007]

## _to_match_spec()：依赖规格转换

```python
def _to_match_spec(dep: VersionedDependency) -> str:
    """将 VersionedDependency 转换为 conda MatchSpec 字符串。"""
    if dep.conda_channel:
        return f"{dep.conda_channel}::{dep.name} {dep.version}"
    elif dep.version:
        return f"{dep.name} {dep.version}"
    else:
        return dep.name
```

[F-008]

MatchSpec 是 conda 的包查询语言，格式为 `[channel::]name[=version[=build]]`。channel 前缀确保从正确通道获取包，避免通道优先级问题。

## 三种后端差异

| 特性 | conda (classic) | mamba | micromamba |
|------|----------------|-------|------------|
| **求解速度** | 慢（Python SAT） | 快（C++ libsolv） | 快（C++ libsolv） |
| **token脱敏** | `<TOKEN>` | `*****` (v1) / `**********` (v2) | 同 mamba |
| **pip inspect** | 不需要 | v2需要假python | v2需要假python |
| **安装大小** | 大（完整Python环境） | 中 | 小（单二进制） |
| **自动发现** | ensureconda | ensureconda | ensureconda |

[F-009]

后端选择通过 `determine_conda_executable()` 自动发现或用户通过 `--conda` 参数显式指定。不同后端的 token 脱敏格式差异通过 `Channel.normalize_url_with_placeholders()` 统一归一化。

## 临时包缓存

`conda_pkgs_dir()` 创建临时包缓存目录，通过 CONDA_PKGS_DIRS 环境变量传给子进程，避免污染用户的包缓存，同时也避免不同平台的包文件冲突：

```python
@contextmanager
def conda_pkgs_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp
```

[F-010]

## 相关概念

- [虚拟包系统](10-virtual-packages.md)
- [Conda 调用层](13-invoke-conda.md)
- [LockSpecification 模型](03-lock-specification.md)
- [四类依赖模型](05-dependency-types.md)
- [跨平台锁定策略](15-cross-platform-locking.md)
