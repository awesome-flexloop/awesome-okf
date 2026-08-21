---
type: "example"
title: "虚拟包检测"
sources:
  - id: rattler-virtual-packages
    resource: /references/rattler-source.md
    title: "rattler_virtual_packages crate"
---

# 虚拟包检测

本示例展示如何检测系统虚拟包，并在求解中使用自定义虚拟包（如交叉编译场景）。

## 示例1：自动检测当前系统

```rust
use rattler_virtual_packages::{VirtualPackage, DetectVirtualPackagesOptions};
use rattler_conda_types::GenericVirtualPackage;

fn main() -> anyhow::Result<()> {
    // 自动检测当前系统
    let vps = VirtualPackage::detect(
        &DetectVirtualPackagesOptions::default(),
        None,  // 缓存目录（None = 不缓存）
    )?;

    println!("系统虚拟包检测结果:");
    println!("{}", "=".repeat(50));

    for vp in &vps {
        match vp {
            VirtualPackage::Linux { version } => {
                println!("OS:           Linux {}", version);
            }
            VirtualPackage::Osx { version } => {
                println!("OS:           macOS {}", version);
            }
            VirtualPackage::Windows { version } => {
                println!("OS:           Windows {}", version);
            }
            VirtualPackage::Glibc { version } => {
                println!("C Runtime:    glibc {}", version);
            }
            VirtualPackage::Cuda { version } => {
                println!("GPU:          CUDA {}", version);
            }
            VirtualPackage::Archspec { spec } => {
                println!("CPU:          {}", spec);
            }
            VirtualPackage::Libc { family, version } => {
                println!("C Runtime:    {} {}", family, version);
            }
            _ => {
                println!("Other:        {:?}", vp);
            }
        }
    }

    // 转换为 GenericVirtualPackage 用于求解
    let generic_vps: Vec<GenericVirtualPackage> = vps
        .into_iter()
        .map(|vp| vp.into_generic())
        .collect();

    println!("\n可用于求解器的虚拟包:");
    for gvp in &generic_vps {
        println!("  {} {} {}", gvp.name, gvp.version, gvp.build_string);
    }

    Ok(())
}
```

## 示例2：环境变量覆盖

在 CI 或容器中，可以通过环境变量覆盖检测结果：

```bash
# 模拟 CUDA 11.8 环境（即使没有 GPU）
CONDA_OVERRIDE_CUDA=11.8 cargo run

# 模拟老版本 glibc（用于构建兼容旧系统的包）
CONDA_OVERRIDE_GLIBC=2.17 cargo run

# 模拟无 CUDA 环境（强制求解 CPU-only 包）
CONDA_OVERRIDE_CUDA="" cargo run

# 模拟指定 Linux 内核版本
CONDA_OVERRIDE_LINUX=5.10 cargo run

# 模拟指定 CPU 微架构
CONDA_OVERRIDE_ARCHSPEC=x86_64-v2 cargo run
```

Rust 代码中自动读取这些环境变量，无需额外代码：

```rust
// 自动尊重 CONDA_OVERRIDE_* 环境变量
let vps = VirtualPackage::detect(&Default::default(), None)?;
```

## 示例3：交叉编译场景（自定义虚拟包）

交叉编译时（在 x86_64 机器上为 aarch64 构建），不能使用本机检测结果，需要手动指定目标平台虚拟包：

```rust
use rattler_virtual_packages::VirtualPackage;
use rattler_conda_types::{GenericVirtualPackage, Version, PackageName};
use std::str::FromStr;

fn main() -> anyhow::Result<()> {
    // 目标平台：Linux aarch64, glibc 2.28, 无 CUDA
    let target_vps = vec![
        VirtualPackage::Linux {
            version: Version::from_str("5.4")?,
        },
        VirtualPackage::Glibc {
            version: Version::from_str("2.28")?,
        },
        // Archspec 对于 aarch64
        VirtualPackage::Archspec {
            spec: "aarch64".to_string(),
        },
    ];

    let generic_vps: Vec<GenericVirtualPackage> = target_vps
        .into_iter()
        .map(|vp| vp.into_generic())
        .collect();

    // 这些虚拟包会约束求解结果只包含 aarch64 兼容的包
    for gvp in &generic_vps {
        println!("{} {}", gvp.name, gvp.version);
    }

    Ok(())
}
```

## 示例4：CUDA 检测与缓存

```rust
use rattler_virtual_packages::VirtualPackage;
use std::path::PathBuf;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cache_dir = dirs::cache_dir()
        .unwrap()
        .join("rattler")
        .join("virtual-packages");

    // 首次检测可能较慢（需要执行 nvidia-smi），结果缓存到磁盘
    let vps = VirtualPackage::detect(
        &Default::default(),
        Some(cache_dir.clone()),
    )?;

    let has_cuda = vps.iter().any(|vp| matches!(vp, VirtualPackage::Cuda { .. }));
    println!("CUDA available: {}", has_cuda);

    // 后续调用从缓存读取（几乎瞬时）
    let vps2 = VirtualPackage::detect(&Default::default(), Some(cache_dir))?;
    assert_eq!(vps.len(), vps2.len());

    Ok(())
}
```

## Python 等效代码

```python
from rattler import VirtualPackage, GenericVirtualPackage

# 自动检测
vps = VirtualPackage.detect()
print(f"检测到 {len(vps)} 个虚拟包")
for vp in vps:
    print(f"  {vp}")

# 在 solve() 中使用
from rattler import solve
records = await solve(
    channels=["conda-forge"],
    specs=["pytorch"],
    virtual_packages=VirtualPackage.detect(),  # 默认自动检测
)
```

## 输出示例（Windows x86_64）

```
系统虚拟包检测结果:
==================================================
OS:           Windows 10.0.19045
CPU:          x86_64-v3

可用于求解器的虚拟包:
  __win 10.0.19045 0
  __archspec 1 x86_64-v3
```

## 输出示例（Linux with CUDA）

```
系统虚拟包检测结果:
==================================================
OS:           Linux 5.15.0
C Runtime:    glibc 2.35
GPU:          CUDA 12.1
CPU:          x86_64-v3

可用于求解器的虚拟包:
  __linux 5.15.0 0
  __glibc 2.35 0
  __cuda 12.1 0
  __archspec 1 x86_64-v3
```
