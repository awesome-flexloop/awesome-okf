---
type: "concept"
title: "虚拟包检测"
sources:
  - id: rattler-virtual-packages
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_virtual_packages"
---

# 虚拟包检测

虚拟包（virtual packages）是 conda 生态中的一个概念：它们代表宿主机系统本身提供的能力，而不是可安装的软件包。虚拟包不下载、不安装，但作为约束参与依赖求解——确保安装的包与系统能力兼容（如 CUDA 版本、glibc 版本）。`rattler_virtual_packages` crate 负责自动检测宿主机的虚拟包。

## 为什么需要虚拟包

如果没有虚拟包，会出现什么问题？
1. **CUDA 版本不匹配**：安装了需要 CUDA 12 的 PyTorch，但系统只有 CUDA 11.8 驱动 → 运行时崩溃
2. **glibc 版本过低**：在 CentOS 7（glibc 2.17）上安装了需要 glibc 2.28 的包 → `ld-linux-x86-64.so.2: version 'GLIBC_2.28' not found`
3. **操作系统不兼容**：在 Linux 上尝试安装 macOS 专用包 → 无法运行
4. **CPU 架构不支持**：在不支持 AVX512 的 CPU 上安装了需要 AVX512 的包 → 非法指令

虚拟包让求解器在安装前就发现这些不兼容问题。

## 虚拟包列表

`rattler_virtual_packages` 支持检测以下虚拟包：

### 操作系统虚拟包

| 包名 | 版本含义 | 示例 |
|------|---------|------|
| `__linux` | Linux 内核版本 | `__linux=5.15=0` |
| `__osx` | macOS 版本 | `__osx=14.2=0` |
| `__win` | Windows 版本 | `__win=10.0.19045=0` |
| `__ios` | iOS 版本 | `__ios=17.0=0` |
| `__android` | Android API level | `__android=33=0` |

### C 运行时虚拟包

| 包名 | 版本含义 | 示例 |
|------|---------|------|
| `__glibc` | glibc 版本（Linux） | `__glibc=2.35=0` |
| `__libc` | libc 版本（通用） | `__libc=...` |

> 注意：glibc 检测通过执行系统 `ldd --version` 获取。Alpine Linux 使用 musl libc，不提供 __glibc。

### GPU/计算虚拟包

| 包名 | 版本含义 | 示例 | 检测方式 |
|------|---------|------|---------|
| `__cuda` | CUDA 驱动版本 | `__cuda=12.1=0` | `nvidia-smi` 或 CUDA 库 |
| `__cuda_arch` | CUDA 算力架构 | `__cuda_arch=8.6=0` | 检测 GPU 型号 |

### CPU 架构虚拟包

| 包名 | 版本含义 | 示例 | 检测方式 |
|------|---------|------|---------|
| `__archspec` | CPU 微架构 | `__archspec=1=x86_64-v3` | CPUID 指令检测支持的指令集 |

`__archspec` 的值遵循 [archspec](https://github.com/archspec/archspec) 项目的分类：
- `x86_64` / `x86_64-v2` / `x86_64-v3` / `x86_64-v4`（SSE/AVX/AVX2/AVX512）
- `aarch64` / `armv8-a` 等

### 其他虚拟包

| 包名 | 说明 |
|------|------|
| `__unix` | Unix 系统（Linux/macOS） |
| `__conda` | conda 版本（环境中存在 conda 时） |

## 使用方式

### 自动检测

```rust
use rattler_virtual_packages::VirtualPackage;

// 检测当前系统的虚拟包
let virtual_packages = VirtualPackage::detect(
    &Default::default(),  // 检测配置
    None,                 // 缓存目录（None = 不缓存）
)?;

for vp in &virtual_packages {
    println!("{:?}", vp);
    // VirtualPackage::Linux { version: "5.15" }
    // VirtualPackage::Glibc { version: "2.35" }
    // VirtualPackage::Cuda { version: "12.1" }
    // VirtualPackage::Archspec { spec: "x86_64-v3" }
}
```

### 转换为 GenericVirtualPackage

检测到的 `VirtualPackage` 需要转换为 `GenericVirtualPackage` 才能传递给求解器：

```rust
use rattler_conda_types::GenericVirtualPackage;

let generic_vps: Vec<GenericVirtualPackage> = virtual_packages
    .into_iter()
    .map(|vp| vp.into_generic())
    .collect();

// 传给 SolverTask
let task = SolverTask {
    virtual_packages: generic_vps,
    // ...
};
```

## 覆盖和自定义

### 通过环境变量覆盖

在 CI/CD 或容器环境中，可能需要覆盖自动检测结果。Rattler 支持以下环境变量：

| 环境变量 | 覆盖内容 | 示例 |
|---------|---------|------|
| `CONDA_OVERRIDE_LINUX` | Linux 内核版本 | `CONDA_OVERRIDE_LINUX=5.10` |
| `CONDA_OVERRIDE_OSX` | macOS 版本 | `CONDA_OVERRIDE_OSX=14.0` |
| `CONDA_OVERRIDE_GLIBC` | glibc 版本 | `CONDA_OVERRIDE_GLIBC=2.28` |
| `CONDA_OVERRIDE_CUDA` | CUDA 版本 | `CONDA_OVERRIDE_CUDA=11.8` |
| `CONDA_OVERRIDE_ARCHSPEC` | CPU 微架构 | `CONDA_OVERRIDE_ARCHSPEC=x86_64-v3` |

设置为空字符串表示系统没有该虚拟包（如 `CONDA_OVERRIDE_CUDA=""` 表示没有 CUDA）。

### 交叉编译场景

交叉编译时，可以显式指定目标平台的虚拟包：

```rust
let virtual_packages = vec![
    VirtualPackage::Linux { version: "5.10".parse()? },
    VirtualPackage::Glibc { version: "2.28".parse()? },
    VirtualPackage::Cuda { version: "12.1".parse()? },
];
```

### 检测配置

`DetectVirtualPackagesOptions` 控制检测行为：

```rust
use rattler_virtual_packages::{DetectVirtualPackagesOptions, CudaDetection};

let options = DetectVirtualPackagesOptions {
    cuda_detection: CudaDetection::from_env(),
    ..Default::default()
};
```

## CUDA 检测细节

CUDA 版本检测有特殊逻辑：

1. 首先尝试通过 `nvidia-smi --query-gpu=driver_version --format=csv` 获取驱动版本
2. 如果 `nvidia-smi` 不可用，尝试加载 `libcuda.so`/`nvcuda.dll` 获取 CUDA Runtime 版本
3. CUDA 版本 = `driver_version // 1000`（如驱动 535.86 → CUDA 12.2，535/1000=5 不对，实际是更复杂的映射）
4. 检测结果可以缓存到磁盘，避免重复执行 `nvidia-smi`

缓存机制：首次检测后将结果写入 `cache_dir/cuda.json`，后续读取缓存。缓存有效期可配置。

## glibc 检测细节

1. 执行 `ldd --version` 命令（通常是 glibc 提供的 ldd）
2. 解析输出中的版本字符串（如 `ldd (Ubuntu GLIBC 2.35-0ubuntu3.6) 2.35`）
3. 如果 ldd 不可用或不是 glibc（如 musl），返回空（不添加 __glibc 虚拟包）

## Archspec 检测细节

archspec 检测通过 CPUID 指令实现（在 Rust 中通过内联汇编或 raw-cpuid crate）：
- 检查 CPU 支持的指令集扩展（SSE2、SSE3、SSE4.1/4.2、AVX、AVX2、AVX-512F 等）
- 根据支持的指令集确定最接近的 archspec 级别
- 在非 x86_64 平台上返回对应架构（aarch64、armv7l 等）

## Python 绑定

```python
from rattler import VirtualPackage

# 自动检测
vps = VirtualPackage.detect()
for vp in vps:
    print(vp)  # VirtualPackage(traceback): Linux(version="5.15"), Glibc(version="2.35")
```

Python 的 `solve()` 函数默认会调用 `VirtualPackage.detect()`，用户也可以手动传入自定义虚拟包列表。

## 虚拟包在依赖声明中的使用

包作者在 `meta.yaml`/`recipe.yaml` 中可以声明对虚拟包的依赖：

```yaml
requirements:
  host:
    - __linux >=5.10       # 需要 Linux 5.10+
    - __glibc >=2.28       # 需要 glibc 2.28+
    - __cuda >=12.0        # 需要 CUDA 12+
  run:
    - __cuda >=12.0
    - __archspec >=x86_64-v3  # 需要 AVX2 支持
```

这样，在不满足条件的系统上求解器会直接报错，而不是安装后在运行时崩溃。

## 相关概念

- [依赖求解](06-solving-dependencies.md)
- [基础类型系统](03-conda-types-foundation.md)
- [5分钟快速上手](01-getting-started.md)
