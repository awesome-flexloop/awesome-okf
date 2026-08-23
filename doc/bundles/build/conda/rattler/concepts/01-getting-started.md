---
type: "concept"
title: "5分钟快速上手"
sources:
  - id: rattler-readme
    resource: /references/rattler-source.md
    title: "Rattler README & Crates 结构"
---

# 5分钟快速上手

本文介绍如何从零开始使用 Rattler，包括 Rust 库集成、CLI 体验和 Python 绑定。

## 前置条件

使用 Rattler 进行 Rust 开发需要：

- **Rust 工具链**：最新稳定版 Rust（通过 rustup 安装）
- **pixi**（推荐）：Rattler 使用 pixi 管理开发环境，提供预配置的构建/测试/lint 命令
- **C 编译器**（libsolv 后端）：在 Linux 上需要 gcc/cc，在 macOS 上需要 Xcode Command Line Tools，在 Windows 上需要 MSVC

使用 Python 绑定时需要：

- Python 3.8+（推荐 3.10+）
- pip 或 conda 包管理器

## 方式一：CLI 快速体验

Rattler 仓库中包含 `rattler-bin`，一个使用所有 crates 构建的示例 CLI，可以体验从零安装包的完整流程：

```bash
# 克隆仓库（含 submodule）
git clone --recursive https://github.com/conda/rattler.git
cd rattler

# 初始化 submodule（如果未使用 --recursive）
git submodule update --init

# 使用 pixi 运行 CLI，创建包含 cowpy 的环境
pixi run rattler create cowpy

# 在新环境中运行命令
pixi run rattler run -p .prefix/ cowpy --random
```

上述命令会：
1. 从 conda-forge 下载 repodata
2. 求解 `cowpy` 及其所有依赖（包括 Python 解释器）
3. 下载并解压包到 `.prefix/` 目录
4. 链接文件、生成 entry points
5. 在环境中执行 `cowpy --random`

## 方式二：Rust 库集成

在你的 Rust 项目中添加 Rattler 依赖。最简单的方式是添加高层 `rattler` crate：

```toml
# Cargo.toml
[dependencies]
rattler = "0.28"
rattler_conda_types = "0.28"
tokio = { version = "1", features = ["full"] }
anyhow = "1"
```

### 最小 Rust 示例：求解并安装环境

```rust
use std::path::PathBuf;
use rattler_conda_types::{Channel, ChannelConfig, MatchSpec, Platform};
use rattler_solve::{SolverImpl, SolverTask, libsolv_c::LibsolvBackend};
use url::Url;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // 1. 配置 channel
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let channel = Channel::from_str("conda-forge", &channel_config)?;

    // 2. 定义要安装的包规格
    let specs = vec![
        "python ~=3.12".parse()?,
        "pip".parse()?,
    ];

    // 3. 检测虚拟包
    let virtual_packages = rattler_virtual_packages::VirtualPackages::detect(
        &Default::default(),
        None,
    )?;

    // 4. 使用 Gateway 获取 repodata 并求解
    // (完整示例见 examples/basic-solve-install.md)

    Ok(())
}
```

### 按需引入 crate

Rattler 的 crate 是按需引入的，不需要引入全部功能：

```toml
[dependencies]
# 只需要基础类型解析？
rattler_conda_types = "0.28"
# 只需要版本比较？
rattler_conda_types = { version = "0.28", default-features = false }
# 需要依赖求解？
rattler_solve = { version = "0.28", features = ["resolvo"] }
```

## 方式三：Python 绑定

py-rattler 提供了最简洁的 Python API，基于 asyncio：

### 安装

```bash
# 使用 pip
pip install py-rattler

# 或使用 conda
conda install -c conda-forge py-rattler
```

### 求解并安装环境

```python
import asyncio
import tempfile
from rattler import solve, install, VirtualPackage

async def main():
    # 求解
    solved = await solve(
        channels=["conda-forge"],
        specs=["python ~=3.12.0", "pip", "requests 2.31.0"],
        virtual_packages=VirtualPackage.detect(),
    )

    # 安装
    env_path = tempfile.mkdtemp()
    await install(records=solved, target_prefix=env_path)
    print(f"环境创建于: {env_path}")

asyncio.run(main())
```

### 查询可用包

```python
from rattler import Gateway, Channel, Platform

async def list_packages():
    gateway = Gateway()
    repodata = await gateway.load_repodata(
        channels=[Channel("conda-forge")],
        platforms=[Platform.current()],
        specs=["python"],
    )
    for record in repodata:
        print(record.name, record.version)
```

## 方式四：JavaScript / WASM 绑定

Rattler 也可以在浏览器或 Node.js 中使用：

```bash
npm install @conda-org/rattler
```

```javascript
import { Version, Platform, PackageName } from '@conda-org/rattler';

// 版本比较
const v1 = new Version("1.2.3");
const v2 = new Version("1.2.4");
console.log(v1.compare(v2));  // -1 (v1 < v2)

// 平台枚举
console.log(Platform.current());  // 当前平台
```

WASM 绑定主要提供基础类型操作（版本比较、平台检测、包名解析）和求解能力，被 [mambajs](https://github.com/emscripten-forge/mambajs) 用于在浏览器中求解和安装 emscripten-forge 通道的包。

## 开发环境搭建

如果要贡献 Rattler 代码，使用 pixi 管理开发环境：

```bash
# 克隆仓库
git clone --recursive https://github.com/conda/rattler.git
cd rattler

# 构建
pixi run build

# 运行测试
pixi run test

# 格式化和 lint
pixi run cargo-fmt
pixi run cargo-clippy

# 运行单个 crate 的测试
pixi run -- cargo nextest run -p rattler_conda_types
```

## 常见问题

### 为什么选择 Rattler 而非调用 conda CLI？

直接调用 `conda` CLI 有几个缺点：需要安装完整的 Python 版 conda、进程启动开销大、输出解析脆弱。Rattler 作为库可以直接嵌入到你的程序中，避免了这些问题，同时提供类型安全的 API。

### Rattler 支持哪些平台？

Rattler 作为 Rust 库支持所有 Rust 目标平台（Linux/macOS/Windows/WASM）。但注意，某些 crate（如 rattler_shell、rattler_package_streaming 的下载功能）可能不支持 WASM 目标。

### Rattler 能创建/管理 conda 环境吗？

可以。高层 `rattler` crate 提供了安装功能（install 模块），可以创建完整的 conda 环境前缀。但 Rattler 不提供环境"管理"功能（如 `conda env list`），这需要应用层自行实现。

## 相关概念

- [Rattler 简介](00-introduction.md)
- [Crates 分层架构](02-crates-architecture.md)
- [基础类型系统](03-conda-types-foundation.md)
