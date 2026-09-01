---
type: Concept
title: Rust API 使用指南
description: libocispec Rust 绑定的完整使用流程：Cargo 依赖配置、加载/保存配置、字段访问、模式匹配、错误处理、可选字段处理
tags: [concept, rust-api, guide, serde, cargo, option, error-handling]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: rust-api-source
    resource: /bundles/containers/libocispec/references/rust-api-source.md
    title: Rust API 源码信源
  - id: readme-source
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: README 项目说明信源
---

# Rust API 使用指南

本文档详细介绍 libocispec Rust 语言绑定的使用方法，包括 Cargo 依赖配置、加载/保存 OCI 配置、类型安全的字段访问、错误处理和可选字段处理。

## Cargo 依赖配置

### 添加依赖

在 `Cargo.toml` 中添加 libocispec 作为 git 依赖：

```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec" }
```

对于 Cargo 版本早于 0.51.0，需要显式指定分支：

```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec", branch = "main" }
```

### Feature 说明

libocispec 定义了两个 feature，默认全部启用：

| Feature | 默认 | 说明 |
|---------|:----:|------|
| `serde` | ✅ | 启用 serde 序列化/反序列化 |
| `deps-serde` | ✅ | 为 chrono 和 url 启用 serde integration |

如果不需要 chrono/url 的 serde 支持，可以禁用默认 features 并手动选择：

```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec", default-features = false, features = ["serde"] }
```

### 传递依赖

libocispec 会自动引入以下依赖：

| Crate | 版本 | 用途 |
|-------|------|------|
| serde | 1.0 | 序列化/反序列化框架 |
| serde_json | 1.0 | JSON 解析和生成 |
| serde_derive | 1.0 | `#[derive(Serialize, Deserialize)]` 宏 |
| serde-value | 0.7 | 动态 serde 值类型 |
| chrono | 0.4 | 日期时间类型（用于 OCI 时间字段） |
| url | 2.1 | URL 类型 |

## 导入 crate

在 Rust 代码中导入 libocispec 和需要的模块：

```rust
extern crate libocispec;

use libocispec::runtime;
use libocispec::image;
```

也可以直接使用 `use` 导入具体类型：

```rust
use libocispec::runtime::Spec as RuntimeSpec;
use libocispec::image::ImageSpec;
```

## 加载 OCI 配置文件

### 使用 load() 便捷方法

`runtime::Spec` 和 `image::ImageSpec` 都提供了 `load()` 关联方法，直接从文件路径加载：

```rust
fn main() {
    // 加载 runtime spec
    let spec = match runtime::Spec::load("config.json") {
        Ok(spec) => spec,
        Err(e) => {
            eprintln!("加载 config.json 失败: {}", e);
            std::process::exit(1);
        }
    };

    // 加载 image spec
    let image_spec = match image::ImageSpec::load("image.json") {
        Ok(spec) => spec,
        Err(e) => {
            eprintln!("加载 image.json 失败: {}", e);
            std::process::exit(1);
        }
    };

    println!("OCI 版本: {}", spec.oci_version);
    println!("架构: {}", image_spec.architecture);
}
```

### 使用 ? 运算符传播错误

在返回 `Result` 的函数中，可以使用 `?` 运算符简化错误处理：

```rust
use libocispec::serialize::SerializeError;

fn load_config(path: &str) -> Result<runtime::Spec, SerializeError> {
    let spec = runtime::Spec::load(path)?;
    Ok(spec)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let spec = load_config("config.json")?;
    println!("主机名: {:?}", spec.hostname);
    Ok(())
}
```

由于 `SerializeError` 实现了 `std::error::Error` trait，它可以自动转换为 `Box<dyn Error>`。

## 字段访问

Rust API 利用类型系统保证安全访问，所有字段都是类型化的。

### 必需字段

必需字段直接使用 `T` 类型，可以直接访问：

```rust
// oci_version 是 String 类型，必需字段，总是存在
println!("OCI 版本: {}", spec.oci_version);

// image spec 中的必需字段
println!("架构: {}", image_spec.architecture);
println!("操作系统: {}", image_spec.os);
```

### 可选字段：Option<T>

可选字段使用 `Option<T>` 类型，需要通过模式匹配或 `if let` 访问：

```rust
// 主机名是 Option<String>
if let Some(ref hostname) = spec.hostname {
    println!("主机名: {}", hostname);
} else {
    println!("主机名: (未设置)");
}

// 使用 unwrap_or 提供默认值
let hostname = spec.hostname.as_deref().unwrap_or("(未设置)");
println!("主机名: {}", hostname);

// 使用 map 进行链式处理
spec.process.as_ref().map(|p| {
    println!("工作目录: {:?}", p.cwd);
});
```

> **注意**：访问嵌套在 `Option` 内的字段时，注意引用级别。`spec.hostname` 是 `Option<String>`，`spec.hostname.as_ref()` 是 `Option<&String>`，`spec.hostname.as_deref()` 是 `Option<&str>`。

### 嵌套结构体访问

嵌套结构体同样是 `Option<NestedStruct>` 类型，需要逐层解包：

```rust
// 访问 process -> user -> uid
if let Some(ref process) = spec.process {
    println!("工作目录: {:?}", process.cwd);
    
    if let Some(ref user) = process.user {
        // uid 是 Option<i64>
        if let Some(uid) = user.uid {
            println!("UID: {}", uid);
        }
        if let Some(gid) = user.gid {
            println!("GID: {}", gid);
        }
    }
    
    // terminal 是 Option<bool>
    if let Some(terminal) = process.terminal {
        println!("启用终端: {}", terminal);
    }
}
```

### 数组字段：Vec<T>

数组字段是 `Option<Vec<T>>` 类型：

```rust
// 遍历挂载点
if let Some(ref mounts) = spec.mounts {
    for (i, mount) in mounts.iter().enumerate() {
        println!("挂载 {}:", i);
        println!("  目标: {}", mount.destination);
        if let Some(ref source) = mount.source {
            println!("  源: {}", source);
        }
        if let Some(ref mount_type) = mount.type_ {
            println!("  类型: {}", mount_type);
        }
    }
}

// 遍历进程参数
if let Some(ref process) = spec.process {
    if let Some(ref args) = process.args {
        println!("命令:");
        for arg in args {
            println!("  {}", arg);
        }
    }
}
```

### 映射字段：HashMap

注解等键值对字段使用 `Option<HashMap<String, Option<serde_json::Value>>>` 类型：

```rust
use std::collections::HashMap;

if let Some(ref annotations) = spec.annotations {
    println!("注解:");
    for (key, value) in annotations {
        println!("  {} = {:?}", key, value);
    }
}
```

值类型是 `Option<serde_json::Value>` 以支持 null 值和任意 JSON 值类型。

### Linux 特定配置

```rust
if let Some(ref linux) = spec.linux {
    // 遍历 namespaces
    if let Some(ref namespaces) = linux.namespaces {
        for ns in namespaces {
            print!("Namespace: type={}", ns.type_);
            if let Some(ref path) = ns.path {
                print!(", path={}", path);
            }
            println!();
        }
    }
    
    // 访问资源限制
    if let Some(ref resources) = linux.resources {
        if let Some(ref memory) = resources.memory {
            if let Some(limit) = memory.limit {
                println!("内存限制: {}", limit);
            }
        }
        
        // CPU 配置
        if let Some(ref cpu) = resources.cpu {
            if let Some(shares) = cpu.shares {
                println!("CPU shares: {}", shares);
            }
        }
    }
}
```

## 构建配置并保存

除了加载现有配置，也可以手动构建 `Spec` 结构体并序列化为 JSON。

### 创建新的配置

```rust
use libocispec::runtime::{Spec, Process, User, Root, Mount, Linux};
use std::collections::HashMap;

fn create_default_spec() -> Spec {
    Spec {
        oci_version: "1.0.0".to_string(),
        hostname: Some("my-container".to_string()),
        domainname: None,
        process: Some(Process {
            cwd: Some("/".to_string()),
            args: Some(vec![
                "/bin/sh".to_string(),
                "-c".to_string(),
                "echo hello".to_string(),
            ]),
            env: Some(vec![
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin".to_string(),
                "TERM=xterm".to_string(),
            ]),
            user: Some(User {
                uid: Some(0),
                gid: Some(0),
                additional_gids: None,
                username: None,
            }),
            terminal: Some(true),
            ..Default::default()  // 其他字段填充 None
        }),
        root: Some(Root {
            path: "rootfs".to_string(),
            readonly: Some(false),
        }),
        mounts: Some(vec![
            Mount {
                destination: "/proc".to_string(),
                source: Some("proc".to_string()),
                type_: Some("proc".to_string()),
                options: Some(vec![
                    "nosuid".to_string(),
                    "noexec".to_string(),
                    "nodev".to_string(),
                ]),
                ..Default::default()
            },
        ]),
        linux: None,
        hooks: None,
        annotations: Some(HashMap::new()),
        ..Default::default()
    }
}
```

> **注意**：结构体使用 `#[derive(Default)]` 吗？实际上生成的代码可能没有实现 `Default`。如果没有，需要显式填所有 `Option` 字段为 `None`。但实践中，可以修改局部加载的配置：

```rust
// 从现有配置修改
let mut spec = runtime::Spec::load("base.json")?;
spec.hostname = Some("new-hostname".to_string());

if let Some(ref mut process) = spec.process {
    process.cwd = Some("/app".to_string());
}
```

### 使用 save() 方法保存到文件

```rust
let spec = create_default_spec();

match spec.save("config.json") {
    Ok(()) => println!("配置已保存"),
    Err(e) => eprintln!("保存失败: {}", e),
}
```

`save()` 方法会写入 pretty-printed JSON（缩进格式化）。

### 序列化为字符串

如果需要 JSON 字符串而不是写入文件，可以直接使用 serde_json：

```rust
// Pretty 格式
let json_str = serde_json::to_string_pretty(&spec)?;
println!("{}", json_str);

// 紧凑格式
let json_compact = serde_json::to_string(&spec)?;
```

或者使用 serialize 模块的 `to_string` 函数：

```rust
use libocispec::serialize;

let json_str = serialize::to_string(&spec)?;
```

## 错误类型

### SerializeError 枚举

```rust
#[derive(Debug)]
pub enum SerializeError {
    Io(io::Error),
    Json(serde_json::Error),    
}
```

错误分为两类：
- `Io`：文件 I/O 错误（文件不存在、权限不足等）
- `Json`：JSON 解析/生成错误（格式错误、类型不匹配等）

### 错误显示

`SerializeError` 实现了 `Display` trait，可以直接打印：

```rust
match runtime::Spec::load("config.json") {
    Ok(spec) => { /* ... */ }
    Err(e) => {
        eprintln!("错误: {}", e);
        // 根据错误类型处理
        match e {
            SerializeError::Io(io_err) => {
                eprintln!("I/O 错误类型: {:?}", io_err.kind());
            }
            SerializeError::Json(json_err) => {
                eprintln!("JSON 错误位置: line {}, column {}", 
                          json_err.line(), json_err.column());
            }
        }
    }
}
```

## 直接使用 serde 函数

除了 `load()`/`save()` 便捷方法，也可以直接使用 `serialize` 模块的函数：

```rust
use libocispec::serialize;
use std::fs::File;

// 反序列化
let file = File::open("config.json")?;
let spec: runtime::Spec = serde_json::from_reader(file)?;

// 序列化到 writer
let mut file = File::create("output.json")?;
serialize::to_writer(&spec, &mut file)?;

// 序列化为字符串
let json = serialize::to_string(&spec)?;
```

## 重新生成 Rust 绑定

当 OCI 规范更新时，可以重新生成 Rust 类型：

```sh
make generate-rust
```

这会运行 Python 代码生成器，根据最新的 JSON Schema 重新生成 `src/runtime/mod.rs` 和 `src/image/mod.rs`。

## 测试

libocispec 自带单元测试，可以运行：

```sh
cargo test
```

测试会加载 `src/runtime/test/config.test.json` 并验证字段值。

## 完整示例：检查并修改配置

```rust
extern crate libocispec;

use libocispec::runtime;
use libocispec::serialize::SerializeError;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("用法: {} <config.json> [output.json]", args[0]);
        std::process::exit(1);
    }

    let input_path = &args[1];
    let output_path = args.get(2).map(|s| s.as_str()).unwrap_or("output.json");

    // 加载配置
    let mut spec = runtime::Spec::load(input_path)?;

    println!("=== 原始配置信息 ===");
    println!("OCI 版本: {}", spec.oci_version);
    println!("主机名: {:?}", spec.hostname);
    
    if let Some(ref process) = spec.process {
        println!("工作目录: {:?}", process.cwd);
        println!("终端: {:?}", process.terminal);
        
        if let Some(ref args) = process.args {
            println!("命令参数: {:?}", args);
        }
    }
    
    if let Some(ref mounts) = spec.mounts {
        println!("挂载点数量: {}", mounts.len());
        for mount in mounts {
            println!("  {} -> {}", mount.source.as_deref().unwrap_or("(none)"), 
                            mount.destination);
        }
    }

    // 修改配置
    spec.hostname = Some("modified-container".to_string());
    println!("\n=== 已修改主机名为: modified-container ===");

    // 保存
    spec.save(output_path)?;
    println!("配置已保存到: {}", output_path);

    Ok(())
}
```

## 与 C API 的关键区别

如果你熟悉 C API，Rust API 有几个重要区别需要注意：

1. **无手动内存管理**：Rust 所有权系统自动处理内存释放
2. **Option 替代 present 标志**：不需要检查 `*_present` 布尔值，`Option<T>` 本身就表示可选
3. **Vec 替代指针+长度**：`Vec<T>` 自带长度，不需要 `xxx_len` 字段
4. **Result 替代错误参数**：错误通过 `Result` 返回，不需要传入 `parser_error*` 输出参数
5. **snake_case 字段名**：Rust 字段使用 snake_case，通过 `#[serde(rename)]` 自动映射到 JSON 的 camelCase

详见 [双语言 API 对比](03-bindings-comparison.md)。

## 相关主题

- [C API 使用指南](01-c-api.md) — C 语言版本的 API
- [双语言 API 对比](03-bindings-comparison.md) — C vs Rust API 详细对比
- [Rust 语言解析 OCI 配置示例](../examples/02-rust-example.md) — 完整可运行示例
