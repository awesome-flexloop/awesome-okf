---
type: "concept"
title: "包记录与 RepoData"
sources:
  - id: rattler-conda-types
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_conda_types/repodata"
---

# 包记录与 RepoData

conda 生态的核心数据交换格式是 `repodata.json`——每个 channel 的每个平台子目录（subdir）都有一个 repodata.json 文件，列出该 channel 在该平台上可用的所有包。`rattler_conda_types` 提供了 `RepoData`、`PackageRecord`、`RepoDataRecord` 等类型来解析和操作这些数据。

## repodata.json 结构

一个 repodata.json 文件的基本结构：

```json
{
  "info": {
    "subdir": "linux-64",
    "default_python_version": "3.12",
    "repodata_version": 2
  },
  "packages": {
    "numpy-1.24.0-py310h1234_0.tar.bz2": {
      "name": "numpy",
      "version": "1.24.0",
      "build": "py310h1234_0",
      "build_number": 0,
      "depends": ["python >=3.10,<3.11", "libopenblas >=0.3.20"],
      "constrains": [],
      "license": "BSD-3-Clause",
      "md5": "abc123...",
      "sha256": "def456...",
      "size": 6543210,
      "subdir": "linux-64",
      "timestamp": 1672531200000
    }
  },
  "packages.conda": {
    "numpy-1.26.0-py312habcd_0.conda": {
      "name": "numpy",
      "version": "1.26.0",
      "build": "py312habcd_0",
      "build_number": 0,
      "depends": ["python >=3.12,<3.13", "libopenblas >=0.3.24"],
      "constrains": [],
      "license": "BSD-3-Clause",
      "md5": "xyz789...",
      "sha256": "uvw012...",
      "size": 7000000,
      "subdir": "linux-64",
      "timestamp": 1696118400000
    }
  },
  "removed": [],
  "repodata_version": 2
}
```

字段说明：
- **`packages`**：旧格式 `.tar.bz2` 包（传统 conda 包格式）
- **`packages.conda`**：新格式 `.conda` 包（基于 Zstandard 的双压缩格式，更快更小）
- **`removed`**：被标记为移除的包文件名列表
- **`info.subdir`**：平台子目录（如 `linux-64`、`osx-arm64`、`win-64`）

## PackageRecord 字段详解

`PackageRecord` 包含包的完整元数据：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | `PackageName` | ✅ | 包名 |
| `version` | `VersionWithSource` | ✅ | 版本号（保留原始字符串） |
| `build` | `String` | ✅ | Build 字符串（标识编译变体，如 `py310h1234_0`） |
| `build_number` | `u64` | ✅ | 构建序号（越大越新） |
| `subdir` | `String` | ✅ | 平台子目录 |
| `depends` | `Vec<MatchSpec>` | ✅ | 运行时依赖列表 |
| `constrains` | `Vec<MatchSpec>` | ✅ | 可选约束（不强制安装） |
| `md5` | `Option<Md5Hash>` | ❌ | MD5 哈希（旧包可能没有） |
| `sha256` | `Option<Sha256Hash>` | ❌ | SHA256 哈希（新包必有） |
| `size` | `Option<u64>` | ❌ | 包文件大小（字节） |
| `license` | `Option<String>` | ❌ | 许可证名称 |
| `license_family` | `Option<String>` | ❌ | 许可证家族 |
| `timestamp` | `Option<DateTime<Utc>>` | ❌ | 包发布时间戳（毫秒） |
| `noarch` | `NoArchType` | ✅ | noarch 类型（None/Python/Generic） |
| `run_exports` | `Option<RunExports>` | ❌ | 运行时导出依赖 |
| `track_features` | `Vec<String>` | ❌ | track_features 标记 |
| `features` | `Option<String>` | ❌ | features 字符串（已弃用） |

### NoArchType

noarch 包是与平台无关的包，可以跨平台安装：

```rust
pub enum NoArchType {
    None,           // 平台相关包
    Python,         // noarch: python（纯 Python 包，需要 pyc 编译）
    Generic,        // noarch: generic（跨平台的通用包，如 shell 脚本）
}
```

### RunExports

`run_exports` 是包的运行时依赖导出机制，当包 A 被安装时，其 `run_exports` 中声明的包会自动添加到依赖中：

```rust
pub struct RunExports {
    pub strong: Vec<MatchSpec>,           // 强导出（严格版本约束）
    pub strong_constrains: Vec<MatchSpec>, // 强约束
    pub weak: Vec<MatchSpec>,             // 弱导出（可被其他包覆盖）
    pub weak_constrains: Vec<MatchSpec>,  // 弱约束
    pub noarch: Vec<MatchSpec>,           // noarch 包导出
}
```

## RepoDataRecord：带位置信息的包记录

`RepoDataRecord` = `PackageRecord` + 下载位置信息，是求解器返回的结果：

```rust
pub struct RepoDataRecord {
    pub package_record: PackageRecord,
    pub file_name: String,   // 包文件名（如 "numpy-1.26.0-py312habcd_0.conda"）
    pub channel: String,     // 来源 channel 基础 URL
    pub url: Url,            // 完整下载 URL
}
```

`url` 通常由 `channel` + `/` + `subdir` + `/` + `file_name` 拼接而成。

## 解析 RepoData

```rust
use rattler_conda_types::RepoData;

// 从文件路径解析
let repo_data_path = Path::new("repodata.json");
let repo_data = RepoData::from_path(repo_data_path)?;

// 从字符串解析
let json_str = r#"{ "info": {...}, "packages": {...} }"#;
let repo_data: RepoData = serde_json::from_str(json_str)?;

// 转换为 RepoDataRecord 列表（附带 channel URL）
let channel = Channel::from_str("conda-forge", &channel_config)?;
let records = repo_data.into_repo_data_records(channel);
```

## PrefixRecord：已安装包记录

`PrefixRecord` 记录包被安装到环境前缀后的状态，存储在 `<prefix>/conda-meta/<name>-<version>-<build>.json` 中：

```rust
pub struct PrefixRecord {
    pub repodata_record: RepoDataRecord,  // 原始包记录
    pub files: Vec<String>,               // 安装的文件相对路径列表
    pub paths_data: PathsData,            // 文件详细信息（含 SHA256）
    pub requested_spec: MatchSpec,        // 用户最初请求的 MatchSpec
    pub link: Option<Link>,               // 链接类型信息
    // ...
}
```

`PathsData` 包含每个安装文件的路径、SHA256 哈希、文件类型（hardlink/symlink/directory）等信息，用于卸载时验证文件完整性和清理。

## Sharded Repodata（分片 Repodata）

对于大型 channel（如 conda-forge 有数十万包），完整的 repodata.json 可能超过 100MB，下载和解析很慢。Rattler 支持 **sharded repodata**（v3 格式），将 repodata 按包名分片：

- `repodata.json` 变为一个索引文件，包含分片信息和 shard 校验
- 实际包数据按包名 hash 分布在多个小文件中（如 `shards/0a/0a1b2c.json`）
- 求解时只下载所需的分片，大幅减少初始加载时间

```rust
// rattler_repodata_gateway 自动处理分片 repodata
let gateway = Gateway::builder()
    .with_cache_dir(cache_dir)
    .with_channel(Channel::from_str("conda-forge", &config)?)
    .finish()
    .await?;

// 查询时自动按需获取分片
let repodata = gateway.query(
    [Platform::Linux64],
    ["numpy", "pandas"],
    None,
).await?;
```

## 性能考虑

大型 channel（如 conda-forge）的 repodata 可能包含：
- 20+ 万个包记录
- 超过 100MB 的 JSON 数据
- 解析需要 500ms-2s（取决于硬件）

Rattler 的优化策略：
1. **内存高效**：使用 `CompactString`、`Arc<str>` 等减少内存占用
2. **bincode 缓存**：首次解析 JSON 后缓存为 bincode 格式，后续加载快 10x+
3. **按需加载**：Gateway 的 sharded repodata 只加载查询涉及的包
4. **增量更新**：支持 zstd 增量补丁（patches）更新，不必每次下载完整 repodata

## 相关概念

- [基础类型系统](03-conda-types-foundation.md)
- [MatchSpec 查询语言与版本约束](04-matchspec-and-versionspec.md)
- [Repodata 网关](07-repodata-gateway.md)
- [依赖求解](06-solving-dependencies.md)
