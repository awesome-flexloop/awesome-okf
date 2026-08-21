---
okf_version: "0.2"
type: "example"
title: "虚拟包检测与使用"
sources: ["conda/plugins/virtual_packages/", "conda/models/records.py"]
---

# 虚拟包检测与使用

虚拟包（Virtual Packages）是 conda 用来表示当前系统环境特性的一种特殊包机制。它们不以真实文件形式存在于通道或缓存中，而是由插件在运行时动态检测生成，名称以双下划线 `__` 开头（如 `__cuda`、`__glibc`、`__osx`）。虚拟包参与依赖求解过程，使得包可以声明对特定系统能力的依赖（如 CUDA 版本、CPU 架构、操作系统版本）。

相关概念：[包记录模型](../concepts/06-package-records.md)、[插件系统](../concepts/15-plugin-system.md)、[求解器与依赖解析](../concepts/09-solver-and-resolve.md)。

## 完整示例

```python
"""
虚拟包检测与使用示例。

引用事实：[F-071] 内置虚拟包插件在 plugins/virtual_packages/ 目录：
              archspec/cuda/conda/linux/osx/windows/freebsd
"""

from conda.base.context import context
from conda.models.records import PackageRecord
from conda.models.match_spec import MatchSpec
from conda.models.enums import PackageType


# ============================================================
# 1. 检测当前系统的虚拟包
# ============================================================

def list_virtual_packages():
    """
    获取当前系统中所有可用的虚拟包。

    [F-071] 虚拟包通过 conda_virtual_packages 插件钩子注册，
    插件管理器提供 get_virtual_package_records() 方法获取所有虚拟包记录。
    每个虚拟包最终通过 PackageRecord.virtual_package() 类方法创建，
    package_type 设置为 PackageType.VIRTUAL_SYSTEM。
    """
    # 通过插件管理器获取所有虚拟包记录
    # 内部遍历 conda_virtual_packages 钩子结果，调用 to_virtual_package()
    virtual_pkgs = context.plugin_manager.get_virtual_package_records()

    print(f"当前系统虚拟包数量: {len(virtual_pkgs)}")
    print("-" * 60)
    for prec in sorted(virtual_pkgs, key=lambda p: p.name):
        # PackageType.VIRTUAL_SYSTEM 标识虚拟系统包
        print(f"  {prec.name:20s} {str(prec.version):15s} build={prec.build or '0'}")

    return virtual_pkgs


# ============================================================
# 2. 内置虚拟包详解
# ============================================================

def describe_virtual_packages():
    """
    conda 内置虚拟包一览。

    [F-071] plugins/virtual_packages/ 目录下的内置插件：
    - conda.py:   __conda      — 当前 conda 版本（始终导出）
    - archspec.py: __archspec   — CPU 微架构名称（如 x86_64, aarch64, haswell）
    - cuda.py:    __cuda       — NVIDIA CUDA 驱动版本（通过 libcuda.so 检测）
    - linux.py:   __unix, __linux, __glibc — Linux 内核和 glibc 版本
    - osx.py:     __unix, __osx — macOS 版本
    - windows.py: __win         — Windows 版本
    - freebsd.py: __unix, __freebsd — FreeBSD 版本
    """
    print("\n内置虚拟包说明:")
    print("-" * 60)
    descriptions = {
        "__conda": "当前 conda 版本，始终可用。用于包声明对 conda 版本的依赖。",
        "__archspec": "CPU 微架构标识（如 x86_64_v3、haswell、aarch64）。"
                      "优化包可依赖特定架构提供性能优化版本。",
        "__cuda": "NVIDIA CUDA 驱动版本（如 12.1、11.8）。"
                  "GPU 加速包（如 cupy、pytorch-gpu）依赖此包确保驱动兼容。"
                  "通过子进程加载 libcuda.so/nvcuda.dll 检测。",
        "__glibc": "GNU C 库版本（如 2.35）。"
                   "Linux 下的预编译包依赖特定 glibc 版本。",
        "__linux": "Linux 内核版本（如 5.15.0）。",
        "__osx": "macOS 版本（如 14.0）。",
        "__win": "Windows 版本（如 10、11）。",
        "__unix": "Unix-like 系统标记（Linux/macOS/FreeBSD 均导出）。",
        "__freebsd": "FreeBSD 版本。",
    }
    for name, desc in descriptions.items():
        print(f"  {name:15s} — {desc}")


# ============================================================
# 3. 使用环境变量覆盖虚拟包
# ============================================================

def override_virtual_packages():
    """
    CondaVirtualPackage 支持通过环境变量覆盖检测值。

    [F-071] CondaVirtualPackage 的 override_entity 参数指定哪个字段可被覆盖，
    环境变量格式为 CONDA_OVERRIDE_<NAME>（全大写）。
    例如：
        CONDA_OVERRIDE_CUDA=12.1        # 覆盖 __cuda 版本为 12.1
        CONDA_OVERRIDE_GLIBC=2.28       # 覆盖 __glibc 版本为 2.28
        CONDA_OVERRIDE_LINUX=5.4.0      # 覆盖 __linux 版本
        CONDA_OVERRIDE_ARCHSPEC=x86_64  # 覆盖 __archspec 的 build 字段

    设置为空字符串时，行为取决于 empty_override 参数：
        - empty_override=NULL（默认）：跳过该虚拟包（不导出）
        - empty_override=None：版本设为 "0"（始终导出，版本为0）
    """
    import os

    print("\n虚拟包覆盖机制:")
    print("-" * 60)
    print("环境变量格式: CONDA_OVERRIDE_<VIRTUAL_PACKAGE_NAME>")
    print()
    print("示例:")
    print("  # 强制模拟 CUDA 12.1 环境（即使系统没有 GPU）")
    print("  export CONDA_OVERRIDE_CUDA=12.1")
    print("  conda install cupy")
    print()
    print("  # 在非 Linux 系统上创建 Linux 环境（结合 CONDA_SUBDIR）")
    print("  export CONDA_SUBDIR=linux-64")
    print("  export CONDA_OVERRIDE_GLIBC=2.28")
    print("  conda create -n linux_env python=3.10")

    # 也可以通过 context.override_virtual_packages 字典配置覆盖
    print(f"\n当前 context 中的虚拟包覆盖: {context.override_virtual_packages}")


# ============================================================
# 4. 虚拟包在依赖求解中的作用
# ============================================================

def virtual_package_in_solve():
    """
    演示虚拟包如何参与依赖匹配。

    包可以在其依赖中声明对虚拟包的约束，例如：
        - cupy 依赖 __cuda>=11.0：表示需要 CUDA 11.0+
        - tensorflow-gpu 依赖 __cuda>=11.2,__glibc>=2.17
        - 某些 mkl 包依赖 __archspec=x86_64_v3

    MatchSpec 的 when 字段可用于条件依赖：
        package[when=__cuda]  # 仅在 __cuda 存在时依赖
    """
    print("\n虚拟包依赖示例:")
    print("-" * 60)

    # 示例：构造一个对 CUDA 版本有要求的 MatchSpec
    cuda_spec = MatchSpec("__cuda>=11.0")
    print(f"CUDA 依赖 spec: {cuda_spec}")

    # 检查当前系统是否满足 CUDA 依赖
    virtual_pkgs = context.plugin_manager.get_virtual_package_records()
    cuda_pkg = next((p for p in virtual_pkgs if p.name == "__cuda"), None)

    if cuda_pkg:
        print(f"检测到 __cuda={cuda_pkg.version}")
        # 使用 MatchSpec.match() 检查是否满足
        # matches = cuda_spec.match(cuda_pkg)
        # print(f"满足 __cuda>=11.0: {matches}")
    else:
        print("当前系统未检测到 CUDA（__cuda 虚拟包不存在）")
        print("GPU 加速包将无法在无 CUDA 的环境中安装，除非设置 CONDA_OVERRIDE_CUDA")

    # when 字段示例：条件依赖
    when_spec = MatchSpec("cupy[when=__cuda]")
    print(f"\n条件依赖 spec: {when_spec}")
    print("含义：仅当 __cuda 虚拟包存在时才依赖 cupy")


# ============================================================
# 5. 编写自定义虚拟包插件
# ============================================================

def custom_virtual_package_example():
    """
    通过插件机制注册自定义虚拟包。

    使用 @plugins.hookimpl 装饰器实现 conda_virtual_packages 钩子，
    yield CondaVirtualPackage 实例即可。
    """
    print("\n自定义虚拟包插件代码示例:")
    print("-" * 60)
    print('''
# my_virtual_pkg.py
from conda import plugins
from conda.plugins.types import CondaVirtualPackage

def detect_my_feature():
    """检测系统是否存在某个特性，返回版本字符串或 None/NULL。"""
    # 自定义检测逻辑，例如检查特定硬件、驱动、库文件等
    try:
        # with open("/proc/my_feature", "r") as f:
        #     return f.read().strip()
        return None  # 未检测到，返回 None 或 NULL
    except Exception:
        from conda.auxlib import NULL
        return NULL  # 返回 NULL 表示不导出该虚拟包

@plugins.hookimpl
def conda_virtual_packages():
    # 注册一个 __my_feature 虚拟包
    yield CondaVirtualPackage(
        name="my_feature",              # 导出为 __my_feature
        version=detect_my_feature,      # 版本可以是字符串或延迟调用函数
        build=None,                     # build 字符串
        override_entity="version",      # 允许通过 CONDA_OVERRIDE_MY_FEATURE 覆盖版本
        # empty_override=NULL,          # 空覆盖时跳过该包
    )

# pyproject.toml 中注册:
# [project.entry-points.conda]
# my-virtual-pkg = "my_virtual_pkg"
''')


# ============================================================
# 6. PackageRecord.virtual_package() 工厂方法
# ============================================================

def create_virtual_package_record():
    """
    PackageRecord.virtual_package() 是创建虚拟包记录的工厂方法。

    设置 package_type=PackageType.VIRTUAL_SYSTEM，channel="@"，subdir=context.subdir。
    """
    # 创建一个虚拟包记录（用于测试或自定义插件中）
    vpkg = PackageRecord.virtual_package(
        name="__cuda",
        version="12.1",
        build_string="0",
    )
    print(f"\n虚拟包记录属性:")
    print(f"  name: {vpkg.name}")
    print(f"  version: {vpkg.version}")
    print(f"  build: {vpkg.build}")
    print(f"  package_type: {vpkg.package_type}")
    print(f"  channel: {vpkg.channel}")
    print(f"  subdir: {vpkg.subdir}")
    print(f"  是否为虚拟系统包: {vpkg.package_type == PackageType.VIRTUAL_SYSTEM}")


# ============================================================
# 主函数
# ============================================================

if __name__ == "__main__":
    # 1. 列出当前系统虚拟包
    print("=" * 60)
    print("1. 当前系统虚拟包")
    print("=" * 60)
    list_virtual_packages()

    # 2. 内置虚拟包说明
    print()
    describe_virtual_packages()

    # 3. 覆盖机制说明
    print()
    override_virtual_packages()

    # 4. 在依赖求解中的作用
    print()
    virtual_package_in_solve()

    # 5. 自定义虚拟包插件示例
    print()
    custom_virtual_package_example()

    # 6. 创建虚拟包记录
    print()
    create_virtual_package_record()
```

## 内置虚拟包清单

| 虚拟包名称 | 提供插件 | 检测方式 | 可覆盖 | 说明 |
|---|---|---|---|---|
| `__conda` | conda.py | 直接读取 `conda.__version__` | 否 | conda 自身版本 |
| `__archspec` | archspec.py | 调用 `get_archspec_name()` 检测 CPU 微架构 | build 字段 | CPU 架构优化匹配 |
| `__cuda` | cuda.py | 子进程加载 `libcuda.so`/`nvcuda.dll`，调用 `cuDriverGetVersion()` | version 字段 | GPU CUDA 驱动版本 |
| `__glibc` | linux.py | `linux_get_libc_version()` 检测 libc 版本 | version 字段 | Linux glibc 版本 |
| `__linux` | linux.py | `platform.release()` 获取内核版本 | version 字段 | Linux 内核版本 |
| `__unix` | linux.py/osx.py/freebsd.py | 固定为 `0=0` | 否 | Unix-like 系统标记 |
| `__osx` | osx.py | `platform.mac_ver()` 获取 macOS 版本 | version 字段 | macOS 版本 |
| `__win` | windows.py | `platform.version()` 获取 Windows 版本 | version 字段 | Windows 版本 |
| `__freebsd` | freebsd.py | FreeBSD 版本检测 | version 字段 | FreeBSD 版本 |

## 关键设计要点

1. **延迟检测**：`CondaVirtualPackage` 的 `version` 和 `build` 参数可以传入可调用对象（如 `cached_cuda_version`），在 `to_virtual_package()` 时才实际执行检测。
2. **版本为 NULL 时跳过**：如果检测函数返回 `NULL`（来自 `conda.auxlib`），该虚拟包不导出（`to_virtual_package()` 返回 NULL）。
3. **缓存机制**：CUDA 检测使用 `@functools.cache` 装饰的 `cached_cuda_version()` 避免重复子进程调用。
4. **跨平台模拟**：设置 `CONDA_SUBDIR=linux-64` 配合 `CONDA_OVERRIDE_GLIBC=2.28` 可以在非 Linux 系统上为 Linux 环境创建/安装包。
5. **虚拟包参与 SAT 求解**：在 `Index` 构建时（[F-050]），虚拟包记录被加入索引，参与 SAT 约束求解，就像它们是真实安装的包一样。
