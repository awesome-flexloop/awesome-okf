---
type: "example"
title: "Repodata 获取与缓存"
sources:
  - id: rattler-repodata-gateway
    resource: /references/rattler-source.md
    title: "rattler_repodata_gateway crate"
---

# Repodata 获取与缓存

本示例展示如何使用 Gateway 获取 repodata、检查缓存状态、清除缓存。

## 示例1：使用 Gateway 查询包

```rust
use rattler_conda_types::{Channel, ChannelConfig, Platform};
use rattler_repodata_gateway::Gateway;
use std::path::PathBuf;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let cache_dir = dirs::cache_dir().unwrap().join("rattler");

    let channels = vec![
        Channel::from_str("conda-forge", &channel_config)?,
    ];

    // 创建 Gateway
    let gateway = Gateway::builder()
        .with_cache_dir(cache_dir.clone())
        .with_channels(channels)
        .finish()
        .await?;

    // 查询特定包的可用版本
    let result = gateway.query(
        [Platform::current()],
        ["python", "numpy", "pandas"],
        None,  // 取消令牌
    ).await?;

    for ((channel, platform), records) in &result {
        println!("Channel: {}, Platform: {}", channel, platform);
        println!("  包数量: {}", records.len());

        // 统计包名分布
        let mut by_name = std::collections::HashMap::new();
        for rec in records {
            let name = rec.package_record.name.as_source().to_string();
            *by_name.entry(name).or_insert(0) += 1;
        }
        for (name, count) in by_name.iter().take(10) {
            println!("  {}: {} 个版本", name, count);
        }
    }

    Ok(())
}
```

## 示例2：加载完整 Repodata 并搜索包

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let cache_dir = dirs::cache_dir().unwrap().join("rattler");

    let channel = Channel::from_str("conda-forge", &channel_config)?;

    let gateway = Gateway::builder()
        .with_cache_dir(cache_dir)
        .with_channels(vec![channel.clone()])
        .finish()
        .await?;

    // 加载指定平台的完整 repodata
    let (repo_data, channel_url, cache_action) = gateway
        .load_repodata(&channel, Platform::current(), None)
        .await?;

    println!("RepoData 加载完成");
    println!("  .tar.bz2 包数量: {}", repo_data.packages.len());
    println!("  .conda 包数量: {}", repo_data.conda_packages.len());
    println!("  Subdir: {}", repo_data.info.subdir);

    // 搜索包含 "python" 的包名（在 .conda 包中）
    println!("\n搜索包含 'python' 的包（前20个）:");
    let mut count = 0;
    for (filename, pkg) in repo_data.conda_packages.iter() {
        if pkg.name.as_source().contains("python") {
            println!("  {} ={} build={}", pkg.name.as_source(), pkg.version, pkg.build);
            count += 1;
            if count >= 20 {
                break;
            }
        }
    }

    Ok(())
}
```

## 示例3：基础 fetch API 直接下载 repodata

```rust
use rattler_repodata_gateway::fetch;
use rattler_conda_types::{Channel, ChannelConfig, Platform};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let client = rattler_networking::default_retry_client()?;
    let cache_dir = dirs::cache_dir().unwrap().join("rattler");
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let channel = Channel::from_str("conda-forge", &channel_config)?;

    // 直接获取单个 repodata（低级 API）
    let result = fetch::fetch_repo_data(
        fetch::FetchRepoDataOptions {
            cache_dir: Some(cache_dir),
            ..Default::default()
        },
        &client,
        channel.base_url(),
        Platform::current(),
        None,
    ).await?;

    println!("下载的 repodata:");
    println!("  缓存状态: {:?}", result.cache_state);
    // result.repo_data 是 RepoData 类型

    Ok(())
}
```

## 示例4：缓存管理

```rust
use rattler_repodata_gateway::CacheClearMode;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cache_dir = dirs::cache_dir().unwrap().join("rattler");
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let channels = vec![Channel::from_str("conda-forge", &channel_config)?];

    let gateway = Gateway::builder()
        .with_cache_dir(cache_dir.clone())
        .with_channels(channels)
        .finish()
        .await?;

    // 检查缓存目录大小
    let repodata_cache = cache_dir.join("repodata");
    if repodata_cache.exists() {
        let size = dir_size(&repodata_cache)?;
        println!("当前 repodata 缓存大小: {:.2} MB", size as f64 / 1024.0 / 1024.0);
    }

    // 清除 repodata 缓存（保留包缓存）
    gateway.clear(CacheClearMode::Repodata).await?;
    println!("Repodata 缓存已清除");

    // 清除所有缓存（包括下载的包）
    // gateway.clear(CacheClearMode::All).await?;
    // println!("所有缓存已清除");

    Ok(())
}

fn dir_size(path: &std::path::Path) -> std::io::Result<u64> {
    let mut total = 0u64;
    for entry in std::fs::read_dir(path)? {
        let entry = entry?;
        if entry.file_type()?.is_dir() {
            total += dir_size(&entry.path())?;
        } else {
            total += entry.metadata()?.len();
        }
    }
    Ok(total)
}
```

## 示例5：带进度报告的 Gateway

```rust
use rattler_repodata_gateway::fetch::IndicatifReporter;
use rattler_repodata_gateway::fetch::Placement;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cache_dir = dirs::cache_dir().unwrap().join("rattler");
    let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
    let channels = vec![Channel::from_str("conda-forge", &channel_config)?];

    // 使用 CLI 进度条（indicatif）
    let reporter = IndicatifReporter::builder()
        .with_placement(Placement::Below)
        .finish();

    let gateway = Gateway::builder()
        .with_cache_dir(cache_dir)
        .with_channels(channels)
        .with_reporter(reporter)
        .finish()
        .await?;

    // 查询时会显示下载进度条
    let result = gateway.query(
        [Platform::current()],
        ["python"],
        None,
    ).await?;

    println!("加载完成，共 {} 条记录", result.values().map(|r| r.len()).sum::<usize>());

    Ok(())
}
```

## 输出示例

```
Channel: https://conda.anaconda.org/conda-forge/, Platform: win-64
  包数量: 32150
  python: 127 个版本
  numpy: 89 个版本
  pandas: 65 个版本
```

## Python 等效代码

```python
from rattler import Gateway, Channel, Platform

gateway = Gateway()
repodata = await gateway.load_repodata(
    channels=[Channel("conda-forge")],
    platforms=[Platform.current()],
    specs=["python", "numpy"],
)
for channel_platform, records in repodata.items():
    print(f"{channel_platform}: {len(records)} packages")
```
