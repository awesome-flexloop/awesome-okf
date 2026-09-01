---
type: Reference
title: Rust API 源码信源
description: libocispec Rust crate 的模块结构、依赖配置、核心类型与序列化实现
tags: [reference, rust-api, source, serde, serialization, cargo]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: cargo-toml
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: Cargo.toml 包配置
  - id: lib-rs
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: src/lib.rs  crate 入口
  - id: serialize-rs
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: src/serialize.rs 序列化模块
---

# Rust API 源码信源

本文档记录 libocispec Rust crate 的包配置、模块结构、核心类型与序列化实现。Rust API 基于 serde 框架实现类型安全的 JSON 序列化/反序列化。

## Cargo 包配置

`Cargo.toml` 定义了 crate 的元数据与依赖：

```toml
[package]
name = "libocispec"
version = "0.1.0"
authors = ["@containers <https://github.com/containers>"]
edition = "2018"

[features]
default = ["serde", "deps-serde"]
deps-serde = ["chrono/serde", "url/serde"]

[dependencies]
chrono = "0.4.7"
serde = { version = "1.0.124", features = ["derive"], optional = true }
url = "2.1.0"
serde-value = "0.7.0"
serde_json = "1.0.64"
serde_derive = "1.0.125"
```

### Feature 说明

| Feature | 默认启用 | 说明 |
|---------|:--------:|------|
| `serde` | ✅ | 启用 serde 序列化/反序列化支持 |
| `deps-serde` | ✅ | 为 chrono 和 url 依赖启用 serde feature |

## Crate 模块结构

`src/lib.rs` 导出三个公共模块：

```rust
pub mod serialize;
pub mod image;
pub mod runtime;
```

### 模块职责

| 模块 | 文件 | 说明 |
|------|------|------|
| `serialize` | `src/serialize.rs` | 通用序列化/反序列化基础设施、错误类型 |
| `runtime` | `src/runtime/mod.rs` | OCI Runtime Spec 类型定义 |
| `image` | `src/image/mod.rs` | OCI Image Spec 类型定义 |

## 核心入口 Trait：load/save 方法

`src/lib.rs` 为 `runtime::Spec` 和 `image::ImageSpec` 实现了便捷的文件读写方法：

```rust
impl runtime::Spec {
    pub fn load(path: &str) -> Result<runtime::Spec, serialize::SerializeError> {
        serialize::deserialize(path)    
    }
    pub fn save(&self, path: &str) -> Result<(), serialize::SerializeError> {
        serialize::serialize(self, path)    
    }
}

impl image::ImageSpec {
    pub fn load(path: &str) -> Result<image::ImageSpec, serialize::SerializeError> {
        serialize::deserialize(path)    
    }
    pub fn save(&self, path: &str) -> Result<(), serialize::SerializeError> {
        serialize::serialize(self, path)    
    }
}
```

## 序列化模块（serialize.rs）

### 错误类型

```rust
#[derive(Debug)]
pub enum SerializeError {
    Io(io::Error),
    Json(serde_json::Error),    
}
```

`SerializeError` 统一封装 I/O 错误和 JSON 解析错误，实现了 `std::fmt::Display` 和 `std::error::Error` trait，同时提供了 `From<io::Error>` 和 `From<serde_json::Error>` 转换实现，支持 `?` 操作符自动转换。

### 公共函数

```rust
/// 将对象序列化为 pretty JSON 并写入文件
pub fn serialize<T: serde::Serialize>(obj: &T, path: &str) -> Result<(), SerializeError>;

/// 从文件读取并反序列化为指定类型
pub fn deserialize<T>(path: &str) -> Result<T, SerializeError> 
    where for<'de> T: serde::Deserialize<'de>;

/// 将对象序列化为紧凑 JSON 并写入 writer
pub fn to_writer<W: io::Write, T: serde::Serialize>(obj: &T, mut writer: W) -> Result<(), SerializeError>;

/// 将对象序列化为紧凑 JSON 字符串
pub fn to_string<T: serde::Serialize>(obj: &T) -> Result<String, SerializeError>;
```

## Runtime Spec 核心类型

`src/runtime/mod.rs` 定义了 OCI 运行时规范的完整类型树，所有类型均派生 `Serialize` 和 `Deserialize`。

### Spec 根结构体

```rust
/// Open Container Initiative Runtime Specification Container Configuration Schema
#[derive(Serialize, Deserialize)]
pub struct Spec {
    #[serde(rename = "ociVersion")]
    pub oci_version: String,  // 必需字段

    #[serde(rename = "hostname")]
    pub hostname: Option<String>,

    #[serde(rename = "domainname")]
    pub domainname: Option<String>,

    #[serde(rename = "process")]
    pub process: Option<Process>,

    #[serde(rename = "root")]
    pub root: Option<Root>,

    #[serde(rename = "mounts")]
    pub mounts: Option<Vec<Mount>>,

    #[serde(rename = "hooks")]
    pub hooks: Option<Hooks>,

    #[serde(rename = "linux")]
    pub linux: Option<Linux>,

    #[serde(rename = "windows")]
    pub windows: Option<Windows>,

    #[serde(rename = "solaris")]
    pub solaris: Option<Solaris>,

    #[serde(rename = "vm")]
    pub vm: Option<Vm>,

    #[serde(rename = "zos")]
    pub zos: Option<Zos>,

    #[serde(rename = "annotations")]
    pub annotations: Option<HashMap<String, Option<serde_json::Value>>>,
}
```

### 字段命名约定

所有字段使用 `#[serde(rename = "camelCase")]` 属性映射到 OCI 规范的 camelCase JSON 字段名，Rust 代码中使用 snake_case：

| JSON 字段 | Rust 字段 | 说明 |
|-----------|-----------|------|
| `ociVersion` | `oci_version` | OCI 规范版本 |
| `createContainer` | `create_container` | 创建容器钩子 |
| `createRuntime` | `create_runtime` | 创建运行时钩子 |
| `rootfs` | `rootfs` | 镜像根文件系统（image 模块） |
| `os.features` | `os_features` | OS 特性（image 模块） |

### 可选字段模式

Rust API 广泛使用 `Option<T>` 表示可选字段：
- 必需字段（如 `oci_version`、`architecture`、`os`）直接使用 `T` 类型
- 可选字段使用 `Option<T>`，反序列化时缺失对应 `null`
- 数组字段使用 `Option<Vec<T>>`
- 映射字段使用 `Option<HashMap<String, Option<serde_json::Value>>>` 支持任意值类型

## Image Spec 核心类型

`src/image/mod.rs` 定义了 OCI 镜像规范类型，根结构体为 `ImageSpec`：

```rust
/// OpenContainer Config Specification
#[derive(Serialize, Deserialize)]
pub struct ImageSpec {
    #[serde(rename = "architecture")]
    pub architecture: String,  // 必需

    #[serde(rename = "os")]
    pub os: String,  // 必需

    #[serde(rename = "rootfs")]
    pub rootfs: Rootfs,  // 必需

    #[serde(rename = "author")]
    pub author: Option<String>,

    #[serde(rename = "created")]
    pub created: Option<String>,

    #[serde(rename = "config")]
    pub config: Option<Config>,

    #[serde(rename = "history")]
    pub history: Option<Vec<History>>,

    #[serde(rename = "os.features")]
    pub os_features: Option<Vec<String>>,

    #[serde(rename = "os.version")]
    pub os_version: Option<String>,

    #[serde(rename = "variant")]
    pub variant: Option<String>,
}
```

### Image Config 结构体

镜像运行时配置对应 `Config` 结构体：

```rust
#[derive(Serialize, Deserialize)]
pub struct Config {
    #[serde(rename = "User")]
    pub user: Option<String>,
    #[serde(rename = "ExposedPorts")]
    pub exposed_ports: Option<HashMap<String, Option<serde_json::Value>>>,
    #[serde(rename = "Env")]
    pub env: Option<Vec<String>>,
    #[serde(rename = "Entrypoint")]
    pub entrypoint: Option<Vec<String>>,
    #[serde(rename = "Cmd")]
    pub cmd: Option<Vec<String>>,
    #[serde(rename = "Volumes")]
    pub volumes: Option<HashMap<String, Option<serde_json::Value>>>,
    #[serde(rename = "WorkingDir")]
    pub working_dir: Option<String>,
    #[serde(rename = "Labels")]
    pub labels: Option<HashMap<String, Option<serde_json::Value>>>,
    #[serde(rename = "StopSignal")]
    pub stop_signal: Option<String>,
    #[serde(rename = "ArgsEscaped")]
    pub args_escaped: Option<bool>,
}
```

## 代码重新生成

Rust 类型定义可通过 Makefile 目标重新生成：

```sh
make generate-rust
```

代码生成器是 `src/ocispec/` 目录下的 Python 脚本：
- `generate.py`：主入口
- `headers.py`：C 头文件生成
- `sources.py`：C 源文件生成
- `json_api.py`：JSON 访问 API 生成
- `helpers.py`：辅助函数

## 测试

`src/lib.rs` 包含内置单元测试：

```rust
#[cfg(test)]
mod tests {
  use crate::runtime;
  #[test]
  fn test_runtime_load(){
    match runtime::Spec::load("src/runtime/test/config.test.json") {
        Ok(_) => {},
        Err(e) => panic!("{}", e),
    }
  }

  #[test]
  fn test_runtime_assert_spec(){
    match runtime::Spec::load("src/runtime/test/config.test.json") {
        Ok(spec) => {assert_eq!(spec.oci_version, "0.5.0-dev")},
        Err(e) => panic!("{}", e),
    }
  }
}
```

测试配置文件位于 `src/runtime/test/config.test.json`。

## 相关概念

- [Rust API 使用指南](../concepts/02-rust-api.md) — Rust API 完整使用流程与错误处理
- [双语言 API 对比](../concepts/03-bindings-comparison.md) — C 与 Rust API 设计差异对比
