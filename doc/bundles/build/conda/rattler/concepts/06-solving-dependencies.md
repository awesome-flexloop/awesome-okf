---
type: "concept"
title: "依赖求解"
sources:
  - id: rattler-solve
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_solve"
---

# 依赖求解

依赖求解（dependency solving/resolution）是包管理的核心问题：给定一组包规格（specs）和可用包池（repodata），找到一组满足所有约束（版本、依赖、平台）的包集合。`rattler_solve` crate 提供了求解器的抽象接口和多种后端实现。

## 核心抽象：SolverImpl trait

`rattler_solve` 定义了求解器的统一接口：

```rust
pub trait SolverImpl {
    /// 求解器后端名称
    fn name() -> &'static str;

    /// 求解给定的任务
    fn solve(
        &self,
        task: &SolverTask<RepoDataRecord>,
    ) -> Result<SolverResult<RepoDataRecord>, SolveError>;
}
```

### SolverTask：求解输入

`SolverTask` 封装了求解所需的全部信息：

```rust
pub struct SolverTask<RepoDataIter> {
    pub specs: Vec<MatchSpec>,                // 用户请求的包规格
    pub available_packages: Vec<Vec<RepoDataRecord>>,  // 各 channel 的可用包
    pub locked_packages: Vec<RepoDataRecord>, // 已锁定的包（lockfile 中的包）
    pub pinned_packages: Vec<RepoDataRecord>, // 强制使用的包（如 Python 版本固定）
    pub virtual_packages: Vec<GenericVirtualPackage>,  // 系统虚拟包
    pub channel_priority: ChannelPriority,   // channel 优先级策略
    pub exclude_newer: Option<ExcludeNewer>, // 排除某个日期之后发布的包
    pub strategy: SolveStrategy,             // 求解策略
    pub timeout: Option<Duration>,           // 超时时间
    pub cancellation_token: Option<CancellationToken>, // 取消令牌
}
```

### SolverResult：求解结果

```rust
pub struct SolverResult<T> {
    pub records: Vec<T>,       // 求解结果：一组包记录
}
```

## 两种求解后端

### 1. libsolv_c 后端（默认）

`rattler_libsolv_rs::Solver`（在 rattler_solve 的 `libsolv_c` 模块中）通过 FFI 调用 [libsolv](https://github.com/openSUSE/libsolv) C 库。libsolv 是 openSUSE 开发的高性能 SAT 求解器，被 mamba、dnf、zypper 等多个包管理器使用。

```rust
use rattler_solve::{libsolv_c::Solver, SolverImpl, SolverTask};

let solver = Solver::default();
let result = solver.solve(&task)?;
for record in &result.records {
    println!("  {} {}", record.package_record.name, record.package_record.version);
}
```

**特点**：
- 性能极高，成熟稳定
- 支持 channel priority
- 需要 C 编译器（构建时）
- 阻塞执行（不支持取消）

### 2. resolvo 后端

`rattler_resolvo::Solver`（在 rattler_solve 的 `resolvo` 模块中）使用 Rust 原生的 [resolvo](https://github.com/mamba-org/resolvo) 求解器。resolvo 是基于 PubGrub 算法的 SAT 求解器，专门为包管理设计。

```rust
use rattler_solve::{resolvo::Solver, SolverImpl, SolverTask};
use rattler_solve::resolvo::CancellationBehavior;

let solver = Solver::builder()
    .cancellation_behavior(CancellationBehavior::Cancel)
    .build();
let result = solver.solve(&task)?;
```

**特点**：
- 纯 Rust，无 C 依赖，易于交叉编译到 WASM
- 原生支持 `CancellationToken`（可取消求解）
- 增量求解能力
- 错误消息更友好（可解释冲突原因）
- 性能接近 libsolv

> **提示**：Python 绑定和 JS 绑定默认使用 resolvo，因为它更容易跨平台编译。CLI 默认使用 libsolv_c 以获得最佳性能。

## 求解配置详解

### ChannelPriority

控制 channel 的优先级策略：

```rust
pub enum ChannelPriority {
    /// 严格优先级：高优先级 channel 中的包永远优先于低优先级 channel，
    /// 即使低优先级有更高版本也不考虑。这是 conda 的默认行为。
    #[default]
    Strict,

    /// 无优先级：所有 channel 平等对待，只考虑版本号
    Disabled,

    /// 灵活优先级：优先使用高优先级 channel 的包，但在依赖冲突时允许
    /// 使用低优先级 channel 的包来解决冲突
    Flexible,
}
```

**推荐**：使用 `Strict` 优先级，避免不同 channel 的包意外混合（如 conda-forge 和 defaults 混用导致的 ABI 不兼容）。

### ExcludeNewer

安全策略，排除某个日期之后发布的包。这在生产环境中很有用——你可以设置一个 cutoff 日期，确保求解器只使用经过时间验证的包：

```rust
// 排除过去 N 小时/天内发布的包
let exclude = ExcludeNewer::from_duration(Duration::from_secs(7 * 24 * 3600));  // 7天

// 排除在固定时间之后发布的包
use jiff::Timestamp;
let cutoff = Timestamp::from_second(1704067200)?;  // 2024-01-01
let exclude = ExcludeNewer::from_datetime(cutoff);

// 还支持按包名或 channel 设置不同的 cutoff
let exclude = ExcludeNewer::from_duration(Duration::from_secs(7 * 24 * 3600))
    .with_package_duration("internal-pkg".parse()?, Duration::ZERO)  // 内部包无延迟
    .with_channel_duration("https://internal-channel/conda", Duration::ZERO);  // 内部channel无延迟
```

### SolveStrategy

控制版本选择策略：

```rust
pub enum SolveStrategy {
    /// 选择满足约束的最高版本（默认，推荐大多数场景）
    Highest,

    /// 选择满足约束的最低版本
    LowestVersion,

    /// 选择直接依赖的最低版本，传递依赖使用最高版本
    LowestVersionDirect,
}
```

### 虚拟包

虚拟包（virtual packages）表示系统本身提供的能力（如 CUDA 驱动、glibc 版本），不作为实际包安装，但会作为约束参与求解：

```rust
use rattler_virtual_packages::VirtualPackage;

// 自动检测当前系统的虚拟包
let virtual_packages = VirtualPackage::detect(&Default::default(), None)?;
// 转换为求解器可用格式
let generic_vps: Vec<_> = virtual_packages
    .iter()
    .map(|vp| vp.clone().into_generic())
    .collect();

let task = SolverTask {
    virtual_packages: generic_vps,
    // ...
};
```

常见虚拟包：
- `__linux=5.15=0` — Linux 内核版本
- `__osx=14.0=0` — macOS 版本
- `__win=10.0=0` — Windows 版本
- `__glibc=2.35=0` — glibc 版本
- `__cuda=12.1=0` — CUDA 驱动版本
- `__archspec=1=x86_64-v3` — CPU 微架构

## 完整求解示例

```rust
use rattler_conda_types::{Channel, ChannelConfig, MatchSpec, Platform};
use rattler_solve::{libsolv_c::Solver, SolverImpl, SolverTask};
use rattler_repodata_gateway::Gateway;
use rattler_virtual_packages::VirtualPackage;
use std::sync::Arc;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let cache_dir = dirs::cache_dir().unwrap().join("rattler");

    // 1. 创建 Gateway
    let channels = vec![Channel::from_str("conda-forge", &channel_config)?];
    let gateway = Gateway::builder()
        .with_cache_dir(cache_dir.clone())
        .with_channels(channels.clone())
        .finish()
        .await?;

    // 2. 加载 repodata
    let repodata = gateway
        .query(
            [Platform::current()],
            ["python", "pip", "numpy"],
            None,
        )
        .await?;

    // 3. 检测虚拟包
    let virtual_packages = VirtualPackage::detect(&Default::default(), None)?;
    let generic_vps: Vec<_> = virtual_packages.into_iter().map(|vp| vp.into_generic()).collect();

    // 4. 构建求解任务（使用 from_iter + 结构体更新语法，参考 rattler-bin）
    let specs = vec![
        "python ~=3.12".parse()?,
        "numpy >=1.24".parse()?,
    ];

    let repo_data: Vec<&Vec<_>> = repodata.values().collect();
    let task = SolverTask {
        specs,
        virtual_packages: generic_vps,
        ..SolverTask::from_iter(&repo_data)
    };

    // 5. 求解
    let mut solver = Solver::default();
    let result = solver.solve(task)?;

    println!("求解完成，共 {} 个包:", result.records.len());
    for rec in &result.records {
        println!("  {}={}={}",
            rec.package_record.name.as_source(),
            rec.package_record.version,
            rec.package_record.build
        );
    }

    Ok(())
}
```

## 求解冲突诊断

当约束无法满足时，求解器返回 `SolveError`。常见原因：

1. **版本约束冲突**：A 要求 `B>=2.0`，C 要求 `B<2.0`
2. **Python 版本不兼容**：包只支持 Python 3.10+，但锁定了 Python 3.9
3. **平台不支持**：包没有对应平台的构建
4. **channel 冲突**：严格优先级下，高优先级 channel 缺少必要包
5. **虚拟包不满足**：包需要 `__cuda>=12`，但系统只有 CUDA 11.8

resolvo 后端提供更友好的错误消息，能解释具体是哪个约束导致了冲突。

## Python 绑定求解

```python
import asyncio
from rattler import solve, ChannelConfig, MatchSpec, Channel, Platform

async def main():
    result = await solve(
        channels=[Channel("conda-forge")],
        specs=[MatchSpec("python ~=3.12"), MatchSpec("numpy >=1.24")],
        platforms=[Platform.current()],
    )
    for rec in result:
        print(f"  {rec.name}={rec.version}={rec.build}")

asyncio.run(main())
```

Python 绑定的 `solve()` 函数封装了 repodata 获取和求解的完整流程，是最简单的使用方式。

## 相关概念

- [MatchSpec 查询语言与版本约束](04-matchspec-and-versionspec.md)
- [包记录与 RepoData](05-package-records-and-repodata.md)
- [Repodata 网关](07-repodata-gateway.md)
- [虚拟包检测](11-virtual-packages.md)
