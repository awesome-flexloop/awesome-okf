---
type: "concept"
title: "基础类型系统"
sources:
  - id: rattler-conda-types
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_conda_types"
---

# 基础类型系统

`rattler_conda_types` 是 Rattler 生态的基石 crate，定义了 conda 生态所有核心数据类型。它是一个纯数据模型 crate，不包含业务逻辑、网络 I/O 或文件操作。所有其他 crate 都直接或间接依赖它。

## 核心类型分类

rattler_conda_types 提供的类型可以分为六大类：

| 类别 | 类型 | 说明 |
|------|------|------|
| **标识类型** | `PackageName`、`NormalizedPackageName`、`Channel`、`ChannelConfig`、`Platform` | 命名与定位 |
| **版本系统** | `Version`、`VersionBump`、`VersionOrder`、`ParseVersionError`、`VersionWithSource` | 版本解析与比较 |
| **约束系统** | `MatchSpec`、`NamelessMatchSpec`、`VersionSpec`、`BuildNumberSpec`、`StringMatcher`、`ChannelPriority` | 包匹配与依赖约束 |
| **包记录** | `PackageRecord`、`RepoDataRecord`、`PrefixRecord`、`PackageFilePathsEntry`、`PathsEntry` | 包元数据与安装记录 |
| **索引数据** | `RepoData` | repodata.json 的完整模型 |
| **虚拟包** | `GenericVirtualPackage`、`VirtualPackage` | 虚拟包模型 |
| **环境模型** | `EnvironmentYaml`、`NoArchType`、`RunExportKind`、`ExplicitEnvironmentSpec` | 环境配置 |

## 标识类型

### PackageName

`PackageName` 是 conda 包名称的规范表示。它验证名称的有效性（只允许小写字母、数字、下划线、中划线），并提供规范化的 `NormalizedPackageName` 用于比较和 HashMap 键。

```rust
use rattler_conda_types::PackageName;

let name: PackageName = "numpy".parse()?;
assert_eq!(name.as_source(), "numpy");

// 规范化名称用于查找（自动处理下划线/中划线差异）
let norm = name.as_normalized();
assert_eq!(norm.as_str(), "numpy");
```

**关键设计点**：conda 包名称中 `-` 和 `_` 被视为等价（`my-package` 和 `my_package` 是同一个包），`NormalizedPackageName` 自动将 `-` 转换为 `-` 统一表示。

### Platform

`Platform` 是一个枚举，覆盖 conda 支持的所有平台：

```rust
pub enum Platform {
    NoArch,           // noarch 平台（跨平台包）
    Linux32,          // linux-32
    Linux64,          // linux-64
    LinuxAarch64,     // linux-aarch64
    LinuxArmV6l,      // linux-armv6l
    LinuxArmV7l,      // linux-armv7l
    LinuxPpc64le,     // linux-ppc64le
    LinuxPpc64,       // linux-ppc64
    LinuxS390X,       // linux-s390x
    LinuxRiscv32,     // linux-riscv32
    LinuxRiscv64,     // linux-riscv64
    Osx64,            // osx-64
    OsxArm64,         // osx-arm64
    Win32,            // win-32
    Win64,            // win-64
    WinArm64,         // win-arm64
    EmscriptenWasm32, // emscripten-wasm32
    WasiWasm32,       // wasi-wasm32
    FreeBsd13Amd64,   // freebsd-13-amd64
}
```

常用关联方法：
- `Platform::current()` — 返回当前运行平台
- `Platform::host()` — 返回编译目标平台
- `Platform::linux()` / `Platform::osx()` / `Platform::windows()` — 返回对应 OS 的平台列表
- `Platform::is_windows()` / `is_unix()` / `is_linux()` — 平台类别判断

```rust
use rattler_conda_types::Platform;

let current = Platform::current();
println!("当前平台: {}", current);  // e.g. "win-64"

let linux_platforms = Platform::linux();
for p in linux_platforms {
    println!("Linux 平台: {}", p);
}
```

### Channel 与 ChannelConfig

`Channel` 表示一个 conda channel（包来源），`ChannelConfig` 控制 channel URL 的解析行为：

```rust
use rattler_conda_types::{Channel, ChannelConfig};

let config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);

// 简写名称自动解析为 conda-forge 等配置
let channel = Channel::from_str("conda-forge", &config)?;
println!("Channel base URL: {}", channel.base_url());

// 直接使用 URL
let channel = Channel::from_url("https://repo.anaconda.com/pkgs/main".parse()?);
```

## 版本系统

`Version` 类型实现了 conda 的版本排序算法。conda 版本是分段式的（如 `1.2.3.20240101`），支持字母数字混合、特殊后缀（`post`、`dev`、`rc`、`alpha` 等）。

```rust
use rattler_conda_types::Version;

let v1: Version = "1.2.3".parse()?;
let v2: Version = "1.2.4".parse()?;
assert!(v1 < v2);

// conda 版本的复杂比较
let v_alpha: Version = "1.0alpha".parse()?;
let v_beta: Version = "1.0beta".parse()?;
let v_rc: Version = "1.0rc1".parse()?;
let v_stable: Version = "1.0".parse()?;
let v_post: Version = "1.0post1".parse()?;
assert!(v_alpha < v_beta < v_rc < v_stable < v_post);

// 版本分段
let v: Version = "2024.01.01-h1234".parse()?;
assert_eq!(v.epoch(), 0);  // 默认 epoch 为 0
```

### VersionSpec

`VersionSpec` 表示版本约束关系，支持 `=`、`>`、`>=`、`<`、`<=`、`~=`（兼容版本）、`!=`、`*`（任意版本）等操作符：

```rust
use rattler_conda_types::{Version, VersionSpec, VersionBump};
use std::str::FromStr;

let spec = VersionSpec::from_str(">=1.0,<2.0")?;
assert!(spec.matches(&"1.5".parse::<Version>()?));
assert!(!spec.matches(&"2.0".parse::<Version>()?));

// ~= 兼容版本（PEP 440 风格）：~=1.2 等价于 >=1.2,<2.0
let tilde = VersionSpec::from_str("~=1.2.3")?;
assert!(tilde.matches(&"1.2.5".parse()?));
assert!(!tilde.matches(&"1.3.0".parse()?));
```

`VersionBump` 类型表示版本递增策略（Major/Minor/Patch/Last）。

## 包记录类型

### PackageRecord

`PackageRecord` 是一个包的完整元数据，对应 repodata.json 中 `packages` 或 `packages.conda` 字段的一条记录。它包含包名、版本、build 字符串、build number、依赖列表、license、subdir、md5/sha256 哈希、时间戳、文件列表等字段。

```rust
// PackageRecord 的核心字段（概念性示意）
pub struct PackageRecord {
    pub name: PackageName,
    pub version: VersionWithSource,
    pub build: String,
    pub build_number: u64,
    pub subdir: String,
    pub depends: Vec<MatchSpec>,           // 运行时依赖
    pub constrains: Vec<MatchSpec>,       // 约束依赖
    pub license: Option<String>,
    pub license_family: Option<String>,
    pub md5: Option<Md5Hash>,
    pub sha256: Option<Sha256Hash>,
    pub size: Option<u64>,
    pub timestamp: Option<chrono::DateTime<chrono::Utc>>,
    pub noarch: NoArchType,
    pub run_exports: Option<RunExports>,
    // ... 其他字段
}
```

### RepoDataRecord

`RepoDataRecord` 是 `PackageRecord` 的扩展，增加了 channel、文件名和 URL 信息，是求解器返回的结果类型：

```rust
pub struct RepoDataRecord {
    pub package_record: PackageRecord,
    pub file_name: String,     // 包文件名（如 numpy-1.24-py310h1234.conda）
    pub channel: String,       // 来源 channel URL
    pub url: Url,              // 完整下载 URL
}
```

### PrefixRecord

`PrefixRecord` 记录已安装到环境前缀中的包状态，包含 `paths_data`（安装的文件列表及其 SHA256）和包来源信息。环境中的 `conda-meta/<package>.json` 文件就是 `PrefixRecord` 的序列化。

## RepoData 索引模型

`RepoData` 直接对应 `repodata.json` 文件的结构：

```rust
pub struct RepoData {
    pub info: RepoDataInfo,
    pub packages: BTreeMap<String, PackageRecord>,      // .tar.bz2 包
    pub conda_packages: BTreeMap<String, PackageRecord>, // .conda 包
    pub removed: Vec<String>,                           // 已移除的包名
    pub repodata_version: u64,                          // repodata 格式版本
}
```

关键方法：
- `RepoData::from_str()` / `from_reader()` — 解析 JSON
- `RepoData::into_repo_data_records(channel)` — 转换为带 URL 的 `RepoDataRecord` 列表
- `RepoData::shards()` / `sharded()` — 分片 repodata 支持

## 设计特点

1. **类型安全的解析**：所有字符串（包名、版本、平台、MatchSpec）都通过 `FromStr` trait 解析为强类型，避免了在业务代码中使用裸字符串的错误风险。

2. **serde 优先**：几乎所有类型都实现了 `Serialize`/`Deserialize`，直接对应 JSON 结构。字段命名使用 `#[serde(rename_all = "kebab-case")]` 等属性与 conda 的 JSON 格式对齐。

3. **内存高效**：使用 `CompactString`/`Arc` 等优化减少内存占用，在处理数百万包记录时保持高效。

4. **零业务逻辑**：该 crate 只提供数据模型和解析，不做求解、下载、安装等操作。这确保了类型系统的稳定性，其他 crate 可以安全依赖。

5. **错误类型规范化**：每个子模块定义自己的错误类型（`ParseVersionError`、`ParseMatchSpecError`、`ParsePlatformError` 等），都实现了 `std::error::Error` 和 `miette::Diagnostic`。

## 相关概念

- [Crates 分层架构](02-crates-architecture.md)
- [MatchSpec 查询语言与版本约束](04-matchspec-and-versionspec.md)
- [包记录与 RepoData](05-package-records-and-repodata.md)
