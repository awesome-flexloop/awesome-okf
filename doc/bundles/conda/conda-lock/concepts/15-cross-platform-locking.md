---
okf_version: "0.2"
type: "concept"
title: "跨平台锁定策略"
sources:
  - "conda_lock/conda_solver.py"
  - "conda_lock/invoke_conda.py"
  - "conda_lock/virtual_package.py"
  - "conda_lock/src_parser/selectors.py"
---

# 跨平台锁定策略

conda-lock 的核心能力之一是在单一平台上为多个目标平台生成锁文件。这通过 CONDA_SUBDIR 环境变量覆盖、虚拟包系统、平台选择器（platform selectors）和假 Python 二进制等机制协同实现。

## 为什么需要跨平台锁定

在团队协作和 CI/CD 场景中，开发环境和生产环境可能运行在不同操作系统/架构上：

- 开发者使用 macOS（Apple Silicon/arm64）开发
- CI 运行在 Linux（x86_64）上测试
- 生产环境部署在 Linux（x86_64 或 aarch64）
- 部分用户使用 Windows

如果每个平台各自锁定，锁文件不一致可能导致"在我机器上能跑"的问题。conda-lock 允许一次锁定所有目标平台，生成包含所有平台包信息的统一锁文件。

[F-001]

## 默认平台与指定平台

```python
# 默认平台：当前运行平台
DEFAULT_PLATFORMS = {
    "linux": ["linux-64"],
    "darwin": ["osx-64"] if platform.machine() == "x86_64" else ["osx-arm64"],
    "win32": ["win-64"],
}
```

用户可以通过以下方式指定目标平台：

1. **environment.yml 的 platforms 字段**：
```yaml
platforms:
  - linux-64
  - osx-arm64
  - win-64
```

2. **命令行 --platform/-p 选项**（覆盖 environment.yml）：
```bash
conda-lock lock -f environment.yml -p linux-64 -p osx-arm64 -p win-64
```

[F-002]

## 跨平台求解机制

```
for platform in target_platforms:
    │
    ├─ 1. 设置 CONDA_SUBDIR=platform
    │     告诉 conda 使用目标平台的 repodata
    │
    ├─ 2. 注入虚拟包（__glibc/__osx/__cuda 等）
    │     通过假 repodata + CONDA_OVERRIDE_* 模拟目标系统
    │
    ├─ 3. 过滤 platform selectors
    │     移除不适用于目标平台的依赖行
    │
    ├─ 4. 评估 PEP 508 markers
    │     过滤不适用于目标平台的 pip 依赖
    │
    ├─ 5. 创建假 python 二进制
    │     防止 libmamba v2 的 pip inspect 检查失败
    │
    ├─ 6. 调用 conda create --dry-run --json
    │     求解目标平台的依赖
    │
    └─ 7. 收集结果
          解析 LINK/FETCH actions → VersionedDependency 列表
```

[F-003]

### CONDA_SUBDIR 覆盖

`CONDA_SUBDIR` 是 conda 原生支持的环境变量，用于覆盖当前平台子目录：

```python
# invoke_conda.py
def conda_env_override(platform, pkgs_dirs=None):
    env = {"CONDA_SUBDIR": platform}
    # ...
    return env
```

设置 `CONDA_SUBDIR=linux-64` 后，即使在 macOS 上运行 conda，它也会：
- 从 `linux-64/repodata.json` 获取包索引
- 求解 linux-64 兼容的依赖树
- 下载 linux-64 二进制包（在 dry-run 模式下只获取 URL，不实际下载）

[F-004]

### 虚拟包模拟

跨平台求解时，目标平台的系统属性（glibc 版本、OS 版本、CUDA 版本等）无法直接探测。虚拟包系统通过两种机制模拟：

1. **假 repodata.json**：在临时目录构造包含 `__glibc`/`__osx`/`__win`/`__archspec`/`__cuda` 等虚拟包的 repodata，作为额外通道传给 conda

2. **CONDA_OVERRIDE_* 环境变量**：conda 原生支持这些环境变量来覆盖自动检测的虚拟包版本：
   - `CONDA_OVERRIDE_GLIBC=2.17`
   - `CONDA_OVERRIDE_CUDA=11.8`
   - `CONDA_OVERRIDE_OSX=10.15`

```
macOS 主机
    │
    ├─ CONDA_SUBDIR=linux-64
    ├─ CONDA_OVERRIDE_GLIBC=2.17
    ├─ CONDA_OVERRIDE_LINUX=0
    └─ Fake repo with __glibc=2.17, __linux=0, __archspec=1=x86_64
        │
        ▼
    conda 认为自己在 Linux x86_64 系统上，
    glibc 2.17，求解 linux-64 兼容的包
```

[F-005]

### Platform Selectors 条件过滤

源文件中的 `# [selector]` 条件注释在解析阶段按平台过滤：

```yaml
dependencies:
  - python=3.10
  - numpy
  - llvm-openmp  # [osx]      ← 仅 macOS
  - libgomp      # [linux]     ← 仅 Linux
  - pywin32      # [win]       ← 仅 Windows
  - cudatoolkit  # [gpu]       ← 自定义 selector（需配合 --extras gpu）
```

```python
# selectors.py
def evaluate_selector(selector: str, platform: str) -> bool:
    """评估平台选择器表达式。

    支持:
    - 操作系统: linux, osx, win, unix
    - 架构: x86_64, aarch64, arm64, ppc64le
    - 组合: linux64 = linux and x86_64
    - 逻辑: not, and, or
    """
```

每个平台求解前，selectors 过滤掉不适用的依赖行，确保传给求解器的是该平台正确的依赖集合。

[F-006]

### PEP 508 Markers 评估

pip 依赖可能包含 PEP 508 环境标记：

```yaml
pip:
  - requests>=2.28
  - pywin32>=300; sys_platform == "win32"
  - importlib-metadata; python_version < "3.10"
```

`markers.py` 中的 `evaluate_marker()` 根据目标平台和 Python 版本评估这些标记，过滤掉不适用的 pip 依赖。

[F-007]

### make_fake_python_binary()：防 libmamba 失败

libmamba v2（mamba 的新求解器后端）在求解时会执行 `<prefix>/bin/python -m pip inspect` 来检查环境中已安装的 pip 包。在 dry-run 模式下，临时 prefix 目录中没有 Python 安装，这个检查会失败导致求解报错。

```python
def make_fake_python_binary(prefix: Path):
    """在假环境中创建最小的 python 可执行文件。"""
    bin_dir = prefix / ("Scripts" if on_win else "bin")
    bin_dir.mkdir(parents=True, exist_ok=True)

    if on_win:
        python_exe = bin_dir / "python.exe"
        python_exe.write_text("@echo off\r\n")
        # 创建 python.bat 和 pip.exe 等也需要
    else:
        python_exe = bin_dir / "python"
        python_exe.write_text("#!/bin/sh\necho '{}'")
        python_exe.chmod(0o755)
```

假 python 脚本在被调用时返回空 JSON `{}`，模拟一个没有安装 pip 包的 Python 环境，绕过 libmamba 的检查。

[F-008]

## 多平台锁文件结构

生成的锁文件包含所有目标平台的包信息：

```yaml
version: 2
metadata:
  platforms:
    - linux-64
    - osx-arm64
    - win-64
  content_hash:
    linux-64: "abc123..."
    osx-arm64: "def456..."
    win-64: "ghi789..."
package:
  # Linux x86_64 包
  - name: python
    version: "3.10.12"
    platform: linux-64
    manager: conda
    ...
  - name: numpy
    version: "1.24.4"
    platform: linux-64
    ...
  - name: libgcc-ng
    version: "13.1.0"
    platform: linux-64
    ...

  # macOS arm64 包
  - name: python
    version: "3.10.12"
    platform: osx-arm64
    ...
  - name: numpy
    version: "1.24.4"
    platform: osx-arm64
    ...
  - name: llvm-openmp
    version: "16.0.6"
    platform: osx-arm64
    ...

  # Windows x64 包
  - name: python
    version: "3.10.12"
    platform: win-64
    ...
  - name: pywin32
    version: "306"
    platform: win-64
    ...
```

每个包记录通过 `platform` 字段标记适用平台，同一包名在不同平台下有不同的记录（不同 build、不同依赖、不同 URL）。

[F-009]

## 跨平台安装

从多平台锁文件安装时，conda-lock 自动选择当前平台的包：

```python
# install 命令内部逻辑
current_platform = detect_current_platform()
packages_to_install = [
    pkg for pkg in lockfile.package
    if pkg.platform == current_platform
    and pkg.categories & selected_categories
]
```

```bash
# 在 macOS arm64 上，自动选择 osx-arm64 的包
conda-lock install --name myenv conda-lock.yml

# 在 Linux x86_64 上，自动选择 linux-64 的包
conda-lock install --name myenv conda-lock.yml

# 在 Windows x64 上，自动选择 win-64 的包
conda-lock install --name myenv conda-lock.yml
```

[F-010]

## 平台映射表

conda-lock 支持的 conda 平台标识与系统映射：

| conda 平台 | 操作系统 | 架构 | Python platform.machine() |
|-----------|---------|------|--------------------------|
| `linux-64` | Linux | x86_64 | x86_64/AMD64 |
| `linux-aarch64` | Linux | ARM64 | aarch64/arm64 |
| `linux-ppc64le` | Linux | POWER9/10 | ppc64le |
| `osx-64` | macOS | x86_64 | x86_64 |
| `osx-arm64` | macOS | Apple Silicon | arm64 |
| `win-64` | Windows | x64 | AMD64 |
| `noarch` | 跨平台 | 纯 Python/通用 | — |

[F-011]

## 注意事项与限制

1. **虚拟包准确性**：默认虚拟包是硬编码的保守值（如 __glibc=2.17 对应 CentOS 7），如果目标系统有更高版本要求，需要通过 `--virtual-package-spec` 自定义。

2. **pip 包跨平台**：pip 包的跨平台锁定依赖 Poetry 求解器正确模拟目标平台环境。纯 Python 包通常没问题，但包含 C 扩展的包需要目标平台有对应的 wheel。

3. **求解时间**：每个平台独立求解，3 个平台约 3 倍时间。使用 mamba 后端可显著加速。

4. **网络需求**：跨平台锁定需要下载所有目标平台的 repodata.json，确保网络能访问 conda-forge/defaults 等通道。

[F-012]

## 相关概念

- [虚拟包系统](10-virtual-packages.md)
- [Conda 求解器](08-conda-solver.md)
- [Conda 调用层](13-invoke-conda.md)
- [源文件解析](07-source-parsers.md)
- [多平台锁定示例](../examples/multi-platform-lock.md)
- [自定义虚拟包示例](../examples/custom-virtual-packages.md)
