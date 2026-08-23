---
okf_version: "0.2"
type: "concept"
title: "虚拟包系统"
sources:
  - "conda_lock/virtual_package.py"
---

# 虚拟包系统

虚拟包（Virtual Packages）是 conda-lock 实现跨平台锁定的关键机制。它们代表目标平台的系统级依赖（如 glibc 版本、CUDA 版本、操作系统版本、CPU 架构），这些依赖不是可安装的 conda 包，而是系统环境的固有属性。conda-lock 通过构造假的 repodata.json 注入虚拟包信息，让求解器在求解时考虑这些系统约束。

## 为什么需要虚拟包

在当前平台（如 macOS）上为另一个平台（如 linux-64）锁定依赖时，求解器无法直接检测目标平台的系统属性：

- **glibc 版本**：Linux 系统的 glibc 版本决定了哪些二进制包可以安装（如 `__glibc >= 2.17`）
- **CUDA 版本**：GPU 机器的 CUDA 版本决定了 CUDA 相关包的版本选择
- **操作系统版本**：如 macOS 版本（`__osx >= 10.15`）影响包兼容性
- **CPU 架构**：x86_64、aarch64、arm64 等
- **操作系统类型**：Linux/macOS/Windows 标识（`__unix`/`__linux`/`__osx`/`__win`）

[F-001]

如果不注入这些信息，求解器可能在跨平台求解时选择不兼容目标系统的包版本。

## 三层模型

虚拟包系统采用三层模型：

```
VirtualPackage (基类)
    │  name (以 __ 开头), version, build_string
    │
    ├── FullVirtualPackage (扩展)
    │   build_number, noarch, depends, timestamp, package_type="virtual_system"
    │
    └── FakeRepoData (基础设施)
        生成包含虚拟包的假 repodata.json 目录结构
        作为额外 conda 通道传给求解器
```

[F-002]

### VirtualPackage

```python
# conda_lock/virtual_package.py

class VirtualPackage:
    """虚拟包基类，表示一个系统级依赖。"""
    name: str          # 以 __ 开头，如 "__glibc", "__cuda", "__osx"
    version: str       # 版本号，如 "2.17", "11.8", "10.15"
    build_string: str  # 构建字符串，通常为空
```

[F-003]

虚拟包名称以双下划线 `__` 开头，这是 conda 的约定，用于区分虚拟包和真实包。

### FullVirtualPackage

```python
class FullVirtualPackage(VirtualPackage):
    """完整虚拟包模型，包含 conda repodata 所需的所有字段。"""
    build_number: int = 0
    noarch: Optional[str] = None
    depends: List[str] = []
    timestamp: int = 0
    package_type: str = "virtual_system"
```

[F-004]

FullVirtualPackage 包含构造 repodata.json 记录所需的完整字段，使得虚拟包看起来像一个真实的 conda 包（但类型标记为 `virtual_system`）。

### FakeRepoData

```python
class FakeRepoData:
    """生成包含虚拟包的假 repodata.json 目录结构。"""

    def __init__(self, virtual_packages: List[FullVirtualPackage]):
        self.virtual_packages = virtual_packages
        self._tmpdir = None

    @property
    def url(self) -> str:
        """返回假 repodata 的 file:// URL，作为额外通道传给 conda。"""
        return f"file://{self._tmpdir}"

    def _build_repodata(self):
        """构造 repodata.json 目录结构：

        tmp/
        ├── noarch/
        │   └── repodata.json  (空)
        ├── linux-64/
        │   └── repodata.json  (含 linux-64 虚拟包)
        ├── osx-arm64/
        │   └── repodata.json  (含 osx-arm64 虚拟包)
        └── win-64/
            └── repodata.json  (含 win-64 虚拟包)
        """
```

[F-005]

FakeRepoData 在临时目录中为每个支持的平台子目录创建 repodata.json，包含对应平台的虚拟包。这些假 repodata 作为 `--channel file://tmp` 传给 conda，求解器从中获取虚拟包信息。

支持的平台子目录：`noarch`、`linux-aarch64`、`linux-ppc64le`、`linux-64`、`osx-64`、`osx-arm64`、`win-64`。

## 默认虚拟包集

`default_virtual_package_repodata()` 返回一套默认的虚拟包配置：

```python
def default_virtual_package_repodata(
    add_duplicate_osx_package: bool = False,
    override_cuda_version: Optional[str] = None,
) -> FakeRepoData:
    """返回默认虚拟包集。

    默认包含：
    - __unix / __linux / __osx / __win (操作系统类型，按平台)
    - __archspec (CPU架构，如 __archspec=1=x86_64)
    - __glibc (Linux glibc版本，默认2.17)
    - __cuda (CUDA版本，可选覆盖)
    """
```

[F-006]

各平台默认虚拟包：

| 平台 | 虚拟包 |
|------|--------|
| linux-64 | `__unix=0=0`, `__linux=0=0`, `__archspec=1=x86_64`, `__glibc=2.17=0` |
| linux-aarch64 | `__unix=0=0`, `__linux=0=0`, `__archspec=1=aarch64`, `__glibc=2.17=0` |
| osx-64 | `__unix=0=0`, `__osx=10.15=0`, `__archspec=1=x86_64` |
| osx-arm64 | `__unix=0=0`, `__osx=11.0=0`, `__archspec=1=arm64` |
| win-64 | `__win=0=0`, `__archspec=1=x86_64` |

## 自定义虚拟包：virtual-packages.yaml

用户可以通过 `--virtual-package-spec` 选项指定自定义虚拟包 YAML 文件来覆盖默认值：

```yaml
# virtual-packages.yaml
subdirs:
  linux-64:
    packages:
      __glibc:
        version: "2.28"
      __cuda:
        version: "11.8"
      __archspec:
        version: "1"
        build_string: "x86_64"
  osx-arm64:
    packages:
      __osx:
        version: "13.0"
      __archspec:
        version: "1"
        build_string: "arm64"
```

```python
def virtual_package_repo_from_specification(path) -> FakeRepoData:
    """从 YAML 文件加载虚拟包规格。"""
    with open(path) as f:
        spec = yaml.safe_load(f)
    packages = []
    for subdir, subdir_spec in spec["subdirs"].items():
        for name, pkg_spec in subdir_spec["packages"].items():
            packages.append(FullVirtualPackage(
                subdir=subdir,
                name=name,
                version=pkg_spec["version"],
                build_string=pkg_spec.get("build_string", "0"),
            ))
    return FakeRepoData(packages)
```

[F-007]

使用方式：

```bash
conda-lock lock -f environment.yml \
  --virtual-package-spec virtual-packages.yaml
```

## CUDA 版本覆盖

`override_cuda_version` 参数允许在默认虚拟包基础上覆盖 CUDA 版本 [F-008]：

```python
# 指定 CUDA 12.1
repodata = default_virtual_package_repodata(override_cuda_version="12.1")
# 将 __cuda=12.1 添加到 linux 平台的虚拟包中
```

这对于在 GPU 环境中锁定 CUDA 相关包非常有用。不同 CUDA 版本会导致不同版本的 CUDA 库（如 `cudatoolkit`、`cupy`、`pytorch-gpu`）被选择。

## 上下文管理器：自动环境设置

VirtualPackage/FakeRepoData 实现了上下文管理器协议，自动设置和清理环境变量：

```python
class FakeRepoData:
    def __enter__(self):
        """构造假 repodata 并设置 CONDA_OVERRIDE_* 环境变量。"""
        self._tmpdir = tempfile.mkdtemp()
        self._build_repodata()
        # 设置 CONDA_OVERRIDE_* 环境变量
        # 如 CONDA_OVERRIDE_GLIBC=2.17
        # 如 CONDA_OVERRIDE_CUDA=11.8
        for vpkg in self.virtual_packages:
            env_var = f"CONDA_OVERRIDE_{vpkg.name.strip('_').upper()}"
            os.environ[env_var] = vpkg.version
        return self

    def __exit__(self, *args):
        """清理临时目录和环境变量。"""
        shutil.rmtree(self._tmpdir)
        for vpkg in self.virtual_packages:
            env_var = f"CONDA_OVERRIDE_{vpkg.name.strip('_').upper()}"
            os.environ.pop(env_var, None)
```

[F-009]

CONDA_OVERRIDE_* 环境变量是 conda 原生支持的机制，用于覆盖自动检测的虚拟包版本。conda-lock 通过设置这些环境变量 + 假 repodata 双通道确保求解器正确识别目标平台的系统约束。

## 向后兼容：add_duplicate_osx_package

`add_duplicate_osx_package=True` 参数在 repodata 中添加一条重复的 `__osx=10.15` 包记录。这是为了向后兼容旧版本 conda-lock 生成的锁文件——旧版内容哈希计算包含此重复包，新版移除后会导致哈希不匹配触发不必要的重新锁定。

此参数仅在 `backwards_compatible_content_hashes()` 中使用，用于计算兼容哈希。

[F-010]

## 在求解流程中的位置

```
solve_specs_for_arch(platform)
       │
       ▼
┌─────────────────────────────┐
│ 1. 创建虚拟包 FakeRepoData  │
│    - 默认或自定义            │
│    - 设置 CONDA_OVERRIDE_*  │
│    - 构造假 repodata.json   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ 2. 将 fake repo 作为额外    │
│    --channel 传给 conda     │
│    conda 从 repodata 获取   │
│    虚拟包信息参与求解        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ 3. 求解完成，清理临时目录    │
│    和 CONDA_OVERRIDE_*      │
└─────────────────────────────┘
```

## 相关概念

- [Conda 求解器](08-conda-solver.md)
- [内容哈希机制](12-content-hash.md)
- [跨平台锁定策略](15-cross-platform-locking.md)
- [Conda 调用层](13-invoke-conda.md)
- [自定义虚拟包示例](../examples/custom-virtual-packages.md)
