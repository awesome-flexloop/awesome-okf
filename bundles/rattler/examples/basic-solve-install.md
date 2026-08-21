---
type: "example"
title: "基础求解与安装"
sources:
  - id: rattler-bin
    resource: /references/rattler-source.md
    title: "rattler-bin CLI 示例"
---

# 基础求解与安装

本示例展示使用 Rattler Rust API 完成 conda 环境的完整创建流程：从依赖求解到包安装。

## 目标

创建一个包含 Python 3.12、NumPy 和 Pandas 的 conda 环境。

## 完整 Rust 代码

```rust
use std::path::PathBuf;
use anyhow::Result;
use rattler::install::{Installer, PythonInfo};
use rattler_conda_types::{Channel, ChannelConfig, MatchSpec, Platform};
use rattler_repodata_gateway::Gateway;
use rattler_solve::{libsolv_c::Solver as LibsolvSolver, SolverImpl, SolverTask};
use rattler_virtual_packages::VirtualPackage;
use url::Url;

#[tokio::main]
async fn main() -> Result<()> {
    // ===== 1. 配置 =====
    let target_prefix = PathBuf::from("./myenv");
    let cache_dir = dirs::cache_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("rattler");
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);

    // 创建 HTTP 客户端（带重试中间件）
    let client = rattler_networking::default_retry_client()?;

    // ===== 2. 初始化 Gateway =====
    let channels = vec![Channel::from_str("conda-forge", &channel_config)?];
    let gateway = Gateway::builder()
        .with_cache_dir(cache_dir.clone())
        .with_http_client(client.clone())
        .with_channels(channels.clone())
        .finish()
        .await?;

    // ===== 3. 定义要安装的包 =====
    let specs: Vec<MatchSpec> = vec![
        "python ~=3.12".parse()?,
        "numpy >=1.24".parse()?,
        "pandas >=2.0".parse()?,
    ];

    // ===== 4. 检测虚拟包 =====
    let virtual_packages = VirtualPackage::detect(&Default::default(), Some(cache_dir.join("vp")))?;
    let generic_vps: Vec<_> = virtual_packages
        .into_iter()
        .map(|vp| vp.into_generic())
        .collect();

    println!("检测到虚拟包:");
    for vp in &generic_vps {
        println!("  {} {}", vp.name, vp.build_string);
    }

    // ===== 5. 加载 repodata =====
    println!("\n加载 repodata...");
    let platform = Platform::current();
    let repodata = gateway
        .query(
            [platform],
            specs.iter().filter_map(|s| s.name.as_ref()).map(|n| n.as_source()),
            None,
        )
        .await?;

    let total_packages: usize = repodata.values().map(|r| r.len()).sum();
    println!("可用包数量: {}", total_packages);

    // ===== 6. 求解依赖 =====
    println!("\n求解依赖...");

    // SolverTask 使用 from_iter + 结构体更新语法构造（参考 rattler-bin 实现）
    // from_iter 从 repodata 创建基础任务，然后覆盖特定字段
    let repo_data: Vec<&Vec<_>> = repodata.values().collect();
    let task = SolverTask {
        specs: specs.clone(),
        virtual_packages: generic_vps,
        ..SolverTask::from_iter(&repo_data)
    };

    let mut solver = LibsolvSolver::default();
    let result = solver.solve(task)?;

    println!("\n求解成功！共 {} 个包:", result.records.len());
    for rec in &result.records {
        println!(
            "  {:<30} {:<20} {}",
            rec.package_record.name.as_source(),
            rec.package_record.version,
            rec.package_record.build
        );
    }

    // ===== 7. 安装到前缀 =====
    println!("\n安装到 {}...", target_prefix.display());

    // 检测前缀中的 Python 信息（如果已存在）
    let python_info = PythonInfo::from_prefix(&target_prefix).await.ok();

    let installer = Installer::new()
        .with_target_prefix(target_prefix.clone())
        .with_package_cache_dir(cache_dir.join("pkgs"))
        .with_download_client(client)
        .with_python_info(python_info);

    let install_result = installer.install(result.records, None).await?;

    println!("\n安装完成！");
    println!("已安装 {} 个包", install_result.records.len());
    println!("环境路径: {}", target_prefix.display());

    Ok(())
}
```

## Cargo.toml 依赖

```toml
[package]
name = "rattler-example"
version = "0.1.0"
edition = "2021"

[dependencies]
anyhow = "1"
dirs = "5"
rattler = "0.28"
rattler_conda_types = "0.28"
rattler_solve = { version = "0.22", features = ["libsolv_c"] }
rattler_repodata_gateway = "0.20"
rattler_networking = "0.20"
rattler_virtual_packages = "2"
tokio = { version = "1", features = ["full"] }
url = "2"
```

## 代码解读

### 步骤1-2：配置与 Gateway 初始化

- 使用 `ChannelConfig::default_with_root_dir()` 创建默认 channel 配置
- `Gateway::builder()` 配置缓存目录、HTTP 客户端和 channel 列表
- `rattler_networking::default_retry_client()` 创建带重试中间件的 HTTP 客户端

### 步骤3-4：包规格与虚拟包

- `MatchSpec` 从字符串解析，支持各种版本约束语法
- `VirtualPackage::detect()` 自动检测系统虚拟包（CUDA、glibc、OS 版本等）
- 检测结果转换为 `GenericVirtualPackage` 以传递给求解器

### 步骤5：加载 repodata

- `gateway.query()` 按需加载 repodata，自动处理缓存和分片
- 传入平台列表和包名列表（从 MatchSpec 的 name 字段提取）
- 返回按 (channel, platform) 分组的包记录

### 步骤6：求解

- `SolverTask` 封装所有求解输入：规格、可用包、虚拟包、配置
- 使用 `LibsolvSolver`（libsolv C 后端）求解
- 成功时返回 `SolverResult`，包含满足所有约束的包记录列表

### 步骤7：安装

- `PythonInfo::from_prefix()` 检测前缀中是否已有 Python（用于增量安装）
- `Installer` 配置目标前缀、缓存目录和下载客户端
- `installer.install()` 执行下载、解压、链接等所有安装步骤
- 安装后可以通过 `rattler_shell` 在环境中执行命令

## Python 等效代码（更简洁）

如果使用 py-rattler，上述流程简化为：

```python
import asyncio
import tempfile
from pathlib import Path
from rattler import solve, install, VirtualPackage

async def main():
    records = await solve(
        channels=["conda-forge"],
        specs=["python ~=3.12", "numpy >=1.24", "pandas >=2.0"],
        virtual_packages=VirtualPackage.detect(),
    )

    prefix = Path(tempfile.mkdtemp()) / "myenv"
    await install(records=records, target_prefix=prefix)
    print(f"环境创建于: {prefix}")

asyncio.run(main())
```

## 运行

```bash
# Rust
cargo run --release

# Python
python example.py
```

## 预期输出

```
检测到虚拟包:
  __win 10.0.19045 0
  __archspec 1 x86_64-v3

加载 repodata...
可用包数量: ...

求解依赖...
求解成功！共 50+ 个包:
  python                          3.12.1              h1a2b3c4_0_cpython
  numpy                           1.26.3              py312h1234_0
  pandas                          2.1.4               py312h5678_0
  libopenblas                     0.3.25              h...
  ...

安装到 ./myenv...
安装完成！
环境路径: ./myenv
```
