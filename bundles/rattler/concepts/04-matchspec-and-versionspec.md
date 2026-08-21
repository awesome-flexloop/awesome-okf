---
type: "concept"
title: "MatchSpec 查询语言与版本约束"
sources:
  - id: rattler-conda-types
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_conda_types/match_spec"
---

# MatchSpec 查询语言与版本约束

MatchSpec 是 conda 生态中用于描述包匹配条件的查询语言，类似于 SQL 的 WHERE 子句。`rattler_conda_types` 提供了 `MatchSpec` 和 `NamelessMatchSpec` 两种类型来解析和匹配包。

## MatchSpec 语法

一个完整的 MatchSpec 字符串格式为：

```
[channel::][namespace::][name ][version_spec][build_spec][subdir_spec][extra_spec]
```

常见示例：

| MatchSpec | 含义 |
|-----------|------|
| `numpy` | 任意版本的 numpy 包 |
| `numpy=1.24` | numpy 1.24 版本（等价于 `1.24.*`） |
| `numpy==1.24.3` | numpy 精确版本 1.24.3 |
| `numpy>=1.20,<2.0` | numpy 版本在 [1.20, 2.0) 之间 |
| `numpy~=1.24` | numpy 兼容版本（>=1.24,<2.0） |
| `numpy[version='>=1.24',build=py310*]` | 带 build 字符串匹配 |
| `conda-forge::numpy>=1.24` | 指定 channel |
| `python 3.12*` | 带版本通配符 |
| `*` | 匹配所有包 |

## MatchSpec 结构

`MatchSpec` 是一个带包名的匹配规范，`NamelessMatchSpec` 是不含包名的版本/build 约束。

```rust
// MatchSpec 结构（概念性示意）
pub struct MatchSpec {
    pub name: Option<PackageName>,        // 包名（可选）
    pub version: NamelessMatchSpec,       // 版本/build/channel 等约束
}

pub struct NamelessMatchSpec {
    pub version: Option<VersionSpec>,          // 版本约束
    pub build: Option<StringMatcher>,          // build 字符串匹配
    pub build_number: Option<BuildNumberSpec>, // build number 约束
    pub sha256: Option<Sha256Hash>,            // 精确 SHA256
    pub md5: Option<Md5Hash>,                  // 精确 MD5
    pub channel: Option<Matcher>,              // channel 匹配
    pub subdir: Option<StringMatcher>,         // 子目录（平台）匹配
    pub namespace: Option<String>,             // 命名空间
    pub url: Option<UrlMatcher>,               // URL 匹配
    pub file_name: Option<String>,             // 文件名匹配
    pub extras: BTreeMap<String, String>,      // 额外键值对
}
```

## 解析与匹配

```rust
use rattler_conda_types::{MatchSpec, PackageRecord, NamelessMatchSpec, Version, StringMatcher};
use std::str::FromStr;

// 解析 MatchSpec
let spec: MatchSpec = "numpy>=1.20,<2.0".parse()?;
assert_eq!(spec.name.as_ref().unwrap().as_source(), "numpy");

// 使用 NamelessMatchSpec（不含包名）
let spec: NamelessMatchSpec = ">=1.20,<2.0".parse()?;
let version: Version = "1.21.0".parse()?;
assert!(spec.matches(&version));

// 解析带 build 匹配的 spec
let spec: MatchSpec = "python=3.12[build=*cpython*]".parse()?;

// 构建 NamelessMatchSpec（Builder 模式）
let spec = NamelessMatchSpec::from_version_spec(
    VersionSpec::from_str(">=3.12,<3.13")?
);
```

## StringMatcher 字符串匹配

`StringMatcher` 用于 build 字符串和 subdir 字段的匹配，支持 glob 模式：

| 模式 | 含义 |
|------|------|
| `*` | 任意字符串 |
| `py310*` | 以 `py310` 开头 |
| `*h1234*` | 包含 `h1234` |
| `*_0` | 以 `_0` 结尾 |
| `py310he1234_0` | 精确匹配 |
| `abc\|def` | 匹配 abc 或 def（regex 模式，前缀 `~=`） |

```rust
use rattler_conda_types::StringMatcher;

let matcher = StringMatcher::from("py310*");
assert!(matcher.matches("py310h1234_0"));
assert!(!matcher.matches("py39he2345_1"));
```

## BuildNumberSpec

`BuildNumberSpec` 约束包的 build number（构建序号）：

```rust
pub enum BuildNumberSpec {
    Exact(u64),                // 精确匹配
    GreaterThan(u64),          // > N
    GreaterThanOrEqual(u64),   // >= N
    LessThan(u64),             // < N
    LessThanOrEqual(u64),      // <= N
    Range(Range),              // 范围
}
```

```rust
use rattler_conda_types::BuildNumberSpec;

let spec: BuildNumberSpec = ">=2".parse()?;
assert!(spec.matches(3));
assert!(!spec.matches(1));
```

## 实际使用模式

MatchSpec 在 Rattler 的多个场景中使用：

1. **依赖列表解析**：`PackageRecord.depends` 字段是 `Vec<MatchSpec>`，表示该包运行时需要的其他包
2. **用户输入**：CLI 和 Python 绑定中，用户指定要安装的包名和版本
3. **约束依赖**：`constrains` 字段也是 `Vec<MatchSpec>`，表示可选约束（不强制安装但如果存在必须满足版本）
4. **SolverTask**：求解器的 `specs` 参数是 `Vec<MatchSpec>`，表示用户请求安装的包

```rust
// 在 SolverTask 中使用
let specs = vec![
    "python ~=3.12.0".parse()?,
    "pip".parse()?,
    "requests >=2.31,<3".parse()?,
];
```

## MatchSpec 与 conda CLI 的兼容

Rattler 的 MatchSpec 解析器与 conda CLI 和 libsolv 的语法兼容。需要注意的差异：

- `=` 表示 starts-with 匹配（如 `python=3.12` 匹配 3.12.*），`==` 表示精确匹配
- `~=` 是 PEP 440 兼容版本运算符，如 `~=3.12` 等价于 `>=3.12,<4.0`
- 空格分隔的多个版本约束被视为 AND（如 `>=1.0,<2.0`）
- Channel 使用 `::` 分隔（`conda-forge::numpy`），不是 `/`
- 方括号 `[]` 中的额外条件使用 `key=value` 格式，多个条件用逗号分隔

## 相关概念

- [基础类型系统](03-conda-types-foundation.md)
- [包记录与 RepoData](05-package-records-and-repodata.md)
- [依赖求解](06-solving-dependencies.md)
