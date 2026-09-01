---
type: Example
title: Rust 语言解析 OCI 配置
description: 完整的 Rust 示例程序：解析 OCI config.json、打印配置摘要、修改并保存、错误处理最佳实践
tags: [example, rust, serde, cargo, runtime-config, walkthrough]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: lib-rs-tests
    resource: /bundles/containers/libocispec/references/rust-api-source.md
    title: src/lib.rs 单元测试参考
  - id: rust-api-concept
    resource: /bundles/containers/libocispec/concepts/02-rust-api.md
    title: Rust API 使用指南
---

# Rust 语言解析 OCI 配置

本示例提供完整的 Rust 程序，演示如何使用 libocispec Rust 绑定解析 OCI 配置文件、类型安全访问字段、修改配置并保存。

## 前置条件

- Rust 工具链（rustc ≥ 1.40+，支持 2018 edition）
- Cargo 包管理器
- 一个有效的 OCI `config.json` 文件（可通过 `runc spec` 生成）

## 项目设置

### 1. 创建新项目

```sh
cargo new oci_inspect_rs
cd oci_inspect_rs
```

### 2. 配置 Cargo.toml

编辑 `Cargo.toml` 添加 libocispec 依赖：

```toml
[package]
name = "oci_inspect_rs"
version = "0.1.0"
edition = "2018"

[dependencies]
libocispec = { git = "https://github.com/containers/libocispec" }
serde_json = "1.0"
```

> 如果需要处理日期时间，可以启用 chrono feature；基础解析只需要默认 features 即可。

## 示例程序：OCI 配置检查工具

下面的 Rust 程序实现与 C 示例相同的功能，但利用 Rust 的类型系统和错误处理机制提供更安全的实现。

### 完整代码

编辑 `src/main.rs`：

```rust
use libocispec::runtime;
use libocispec::image;
use std::env;
use std::process;

fn print_usage(program: &str) {
    eprintln!("用法: {} <command> [args]", program);
    eprintln!();
    eprintln!("命令:");
    eprintln!("  inspect <config.json>    打印 runtime spec 配置摘要");
    eprintln!("  inspect-image <img.json> 打印 image spec 配置摘要");
    eprintln!("  modify <input> <output>   修改主机名并保存到新文件");
}

fn inspect_runtime(path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("=== 正在解析 runtime spec: {} ===\n", path);

    let spec = runtime::Spec::load(path)?;

    println!("解析成功!\n");
    println!("=== 配置摘要 ===");
    println!("  OCI 版本: {}", spec.oci_version);
    println!("  主机名: {}", spec.hostname.as_deref().unwrap_or("(未设置)"));
    println!("  域名: {}", spec.domainname.as_deref().unwrap_or("(未设置)"));

    if let Some(ref root) = spec.root {
        print!("  根文件系统: path={}", root.path.as_deref().unwrap_or("rootfs"));
        if root.readonly.unwrap_or(false) {
            print!(" (只读)");
        }
        println!();
    }

    println!();
    print_process_summary(&spec);
    println!();
    print_mounts_summary(&spec);
    println!();
    print_linux_summary(&spec);
    print_hooks_summary(&spec);
    print_annotations_summary(&spec);

    Ok(())
}

fn inspect_image(path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("=== 正在解析 image spec: {} ===\n", path);

    let spec = image::ImageSpec::load(path)?;

    println!("解析成功!\n");
    println!("=== 镜像配置摘要 ===");
    println!("  创建时间: {}", spec.created.as_deref().unwrap_or("(未知)"));
    println!("  作者: {}", spec.author.as_deref().unwrap_or("(未指定)"));
    println!("  架构: {}", spec.architecture);
    println!("  操作系统: {}", spec.os);
    println!("  OS 版本: {}", spec.os_version.as_deref().unwrap_or("(未指定)"));
    println!("  变体: {}", spec.variant.as_deref().unwrap_or("(未指定)"));

    if let Some(ref config) = spec.config {
        println!("\n  运行时配置:");
        println!("    用户: {}", config.user.as_deref().unwrap_or("(未指定)"));
        println!("    工作目录: {}", config.working_dir.as_deref().unwrap_or("/"));
        
        if let Some(ref env) = config.env {
            println!("    环境变量 ({} 个):", env.len());
            for (i, e) in env.iter().take(5).enumerate() {
                println!("      [{}] {}", i, e);
            }
            if env.len() > 5 {
                println!("      ... (还有 {} 个)", env.len() - 5);
            }
        }

        if let Some(ref cmd) = config.cmd {
            println!("    Cmd: {:?}", cmd);
        }
        if let Some(ref entrypoint) = config.entrypoint {
            println!("    Entrypoint: {:?}", entrypoint);
        }
    }

    println!("\n  RootFS 层 ({} 个):", spec.rootfs.diff_ids.len());
    for (i, diff_id) in spec.rootfs.diff_ids.iter().enumerate() {
        let short = if diff_id.len() > 20 {
            format!("{}...{}", &diff_id[..16], &diff_id[diff_id.len()-8..])
        } else {
            diff_id.clone()
        };
        println!("    [{}] {} ({})", i, short, spec.rootfs.type_);
    }

    if let Some(ref history) = spec.history {
        println!("\n  历史记录 ({} 条):", history.len());
        for (i, h) in history.iter().take(3).enumerate() {
            println!("    [{}] {}", i, h.created_by.as_deref().unwrap_or("(无命令)"));
            if let Some(empty) = h.empty_layer {
                if empty {
                    println!("         (empty layer)");
                }
            }
        }
        if history.len() > 3 {
            println!("    ... (还有 {} 条)", history.len() - 3);
        }
    }

    Ok(())
}

fn modify_config(input: &str, output: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("=== 读取配置: {} ===", input);
    
    let mut spec = runtime::Spec::load(input)?;
    
    let old_hostname = spec.hostname.clone().unwrap_or_else(|| "(未设置)".to_string());
    
    // 修改主机名
    spec.hostname = Some("rust-modified-hostname".to_string());
    
    // 添加或修改一个注解
    let mut annotations = spec.annotations.take().unwrap_or_default();
    annotations.insert(
        "com.example.modified-by".to_string(),
        Some(serde_json::Value::String("libocispec-rust-example".to_string())),
    );
    annotations.insert(
        "com.example.modified-at".to_string(),
        Some(serde_json::Value::String(chrono::Local::now().to_rfc3339())),
    );
    spec.annotations = Some(annotations);
    
    // 修改进程工作目录
    if let Some(ref mut process) = spec.process {
        process.cwd = Some("/modified-workdir".to_string());
    }

    println!("  主机名: {} -> rust-modified-hostname", old_hostname);
    println!("  已添加注解: com.example.modified-by");
    println!("  工作目录已改为: /modified-workdir");

    // 保存到输出文件
    spec.save(output)?;
    println!("\n修改后的配置已保存到: {}", output);

    // 验证：重新读取并打印
    let verify = runtime::Spec::load(output)?;
    println!("\n验证 - 新主机名: {:?}", verify.hostname);
    println!("验证 - 新工作目录: {:?}", 
             verify.process.and_then(|p| p.cwd));

    Ok(())
}

fn print_process_summary(spec: &runtime::Spec) {
    let proc = match spec.process {
        Some(ref p) => p,
        None => {
            println!("  进程配置: (无)");
            return;
        }
    };

    println!("  进程配置:");
    println!("    终端: {}", if proc.terminal.unwrap_or(false) { "是" } else { "否" });
    println!("    工作目录: {}", proc.cwd.as_deref().unwrap_or("/"));
    println!("    NoNewPrivileges: {}", proc.no_new_privileges.unwrap_or(false));

    if let Some(ref user) = proc.user {
        print!("    用户: ");
        match (user.uid, user.gid) {
            (Some(uid), Some(gid)) => println!("uid={}, gid={}", uid, gid),
            (Some(uid), None) => println!("uid={}", uid),
            (None, Some(gid)) => println!("gid={}", gid),
            (None, None) => println!("(未指定)"),
        }
        if let Some(ref username) = user.username {
            println!("    用户名: {}", username);
        }
    }

    if let Some(ref args) = proc.args {
        if !args.is_empty() {
            print!("    命令: ");
            for (i, arg) in args.iter().enumerate() {
                if i > 0 { print!(" "); }
                print!("{}", arg);
            }
            println!();
        }
    }

    if let Some(ref env) = proc.env {
        println!("    环境变量 ({} 个):", env.len());
        for (i, e) in env.iter().take(5).enumerate() {
            println!("      [{}] {}", i, e);
        }
        if env.len() > 5 {
            println!("      ... (还有 {} 个)", env.len() - 5);
        }
    }

    if let Some(ref capabilities) = proc.capabilities {
        let mut caps = Vec::new();
        if let Some(ref b) = capabilities.bounding { caps.extend(b.iter().map(|s| s.as_str())); }
        if let Some(ref p) = capabilities.permitted { caps.extend(p.iter().map(|s| s.as_str())); }
        if let Some(ref e) = capabilities.effective { caps.extend(e.iter().map(|s| s.as_str())); }
        if !caps.is_empty() {
            println!("    Capabilities: {} 个 (bounding/permitted/effective)", caps.len());
        }
    }
}

fn print_mounts_summary(spec: &runtime::Spec) {
    let mounts = match spec.mounts {
        Some(ref m) => m,
        None => {
            println!("  挂载点: (无)");
            return;
        }
    };

    println!("  挂载点 ({} 个):", mounts.len());
    for (i, m) in mounts.iter().enumerate() {
        let source = m.source.as_deref().unwrap_or("(无来源)");
        print!("    [{}] {} -> {}", i, source, m.destination);
        if let Some(ref t) = m.type_ {
            print!(" (type={})", t);
        }
        if let Some(ref opts) = m.options {
            if !opts.is_empty() {
                print!(" [{}]", opts.join(","));
            }
        }
        println!();
    }
}

fn print_linux_summary(spec: &runtime::Spec) {
    let linux = match spec.linux {
        Some(ref l) => l,
        None => {
            println!("  Linux 配置: (无)");
            return;
        }
    };

    println!("  Linux 配置:");

    if let Some(ref namespaces) = linux.namespaces {
        println!("    Namespaces ({} 个):", namespaces.len());
        for ns in namespaces {
            print!("      - {}", ns.type_);
            if let Some(ref path) = ns.path {
                print!(" (path={})", path);
            }
            println!();
        }
    }

    if let Some(ref resources) = linux.resources {
        if let Some(ref memory) = resources.memory {
            if let Some(limit) = memory.limit {
                println!("    内存限制: {} bytes ({:.2} MB)", limit, limit as f64 / 1024.0 / 1024.0);
            }
        }
        if let Some(ref cpu) = resources.cpu {
            if let Some(shares) = cpu.shares {
                println!("    CPU shares: {}", shares);
            }
            if let Some(quota) = cpu.quota {
                println!("    CPU quota: {} us", quota);
            }
            if let Some(period) = cpu.period {
                println!("    CPU period: {} us", period);
            }
        }
        if let Some(ref pids) = resources.pids {
            println!("    PIDs limit: {}", pids.limit);
        }
    }

    if let Some(ref cgroups_path) = linux.cgroups_path {
        println!("    Cgroup 路径: {}", cgroups_path);
    }

    if let Some(ref seccomp) = linux.seccomp {
        println!("    Seccomp: 默认动作={:?}", seccomp.default_action);
        if let Some(ref syscalls) = seccomp.syscalls {
            println!("      Syscall 规则: {} 条", syscalls.len());
        }
    }

    if let Some(ref masked) = linux.masked_paths {
        println!("    Masked paths ({} 个):", masked.len());
        for p in masked.iter().take(3) {
            println!("      - {}", p);
        }
        if masked.len() > 3 {
            println!("      ...");
        }
    }

    if let Some(ref readonly) = linux.readonly_paths {
        println!("    Readonly paths ({} 个):", readonly.len());
        for p in readonly.iter().take(3) {
            println!("      - {}", p);
        }
        if readonly.len() > 3 {
            println!("      ...");
        }
    }
}

fn print_hooks_summary(spec: &runtime::Spec) {
    let hooks = match spec.hooks {
        Some(ref h) => h,
        None => return,
    };

    let hook_types = [
        ("prestart", &hooks.prestart),
        ("poststart", &hooks.poststart),
        ("poststop", &hooks.poststop),
        ("createRuntime", &hooks.create_runtime),
        ("createContainer", &hooks.create_container),
        ("startContainer", &hooks.start_container),
    ];

    let mut has_hooks = false;
    for (name, hooks_list) in &hook_types {
        if let Some(list) = hooks_list {
            if !list.is_empty() {
                if !has_hooks {
                    println!("\n  生命周期钩子:");
                    has_hooks = true;
                }
                println!("    {} ({} 个):", name, list.len());
                for hook in list.iter().take(2) {
                    println!("      - path={}", hook.path);
                    if let Some(ref args) = hook.args {
                        println!("        args={:?}", args);
                    }
                }
                if list.len() > 2 {
                    println!("      ...");
                }
            }
        }
    }
}

fn print_annotations_summary(spec: &runtime::Spec) {
    let annotations = match spec.annotations {
        Some(ref a) => a,
        None => return,
    };

    if annotations.is_empty() {
        return;
    }

    println!("\n  注解 ({} 个):", annotations.len());
    for (i, (key, value)) in annotations.iter().take(10).enumerate() {
        let val_str = match value {
            Some(v) => format!("{}", v),
            None => "null".to_string(),
        };
        let display = if val_str.len() > 50 {
            format!("{}...", &val_str[..47])
        } else {
            val_str
        };
        println!("    [{}] {} = {}", i, key, display);
    }
    if annotations.len() > 10 {
        println!("    ... (还有 {} 个)", annotations.len() - 10);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let program = &args[0];

    if args.len() < 2 {
        print_usage(program);
        process::exit(1);
    }

    let command = &args[1];
    let result = match command.as_str() {
        "inspect" if args.len() >= 3 => inspect_runtime(&args[2]),
        "inspect-image" if args.len() >= 3 => inspect_image(&args[2]),
        "modify" if args.len() >= 4 => modify_config(&args[2], &args[3]),
        _ => {
            eprintln!("错误: 无效命令或参数不足\n");
            print_usage(program);
            process::exit(1);
        }
    };

    if let Err(e) = result {
        eprintln!("\n错误: {}", e);
        
        // 提供更友好的错误提示
        let err_str = e.to_string();
        if err_str.contains("No such file") {
            eprintln!("提示: 请检查文件路径是否正确");
        } else if err_str.contains("expected value") || err_str.contains("JSON") {
            eprintln!("提示: JSON 解析失败，请检查文件格式");
        }
        
        process::exit(1);
    }
}
```

> **注意**：上面的代码使用了 `chrono` crate 来格式化修改时间。如果不想添加额外依赖，可以移除 `chrono::Local::now()` 那行，或者添加 chrono 依赖：
> ```toml
> chrono = "0.4"
> ```

如果不想使用 chrono，将 `modify_config` 函数中的注解插入部分替换为：

```rust
annotations.insert(
    "com.example.modified-at".to_string(),
    Some(serde_json::Value::String("2026-01-01T00:00:00Z".to_string())),
);
```

### 添加 chrono 依赖（可选）

如果想使用时间戳功能，更新 Cargo.toml：

```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec" }
serde_json = "1.0"
chrono = "0.4"
```

### 编译和运行

```sh
# 构建（debug 模式）
cargo build

# 生成示例 config.json（需要 runc）
runc spec

# 运行 inspect 命令
cargo run -- inspect config.json

# 运行 modify 命令
cargo run -- modify config.json modified.json

# 检查生成的文件
cargo run -- inspect modified.json
```

预期输出（inspect）：

```
=== 正在解析 runtime spec: config.json ===

解析成功!

=== 配置摘要 ===
  OCI 版本: 1.0.0
  主机名: runc
  域名: (未设置)
  根文件系统: path=rootfs

  进程配置:
    终端: 是
    工作目录: /
    用户: uid=0, gid=0
    命令: /bin/sh
    环境变量 (8 个):
      [0] PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
      [1] TERM=xterm
      ...
  ...
```

## 代码要点解析

### 1. Result 与 ? 运算符

Rust API 的所有失败操作都返回 `Result<T, SerializeError>`：

```rust
let spec = runtime::Spec::load(path)?;
```

`?` 运算符会在错误时提前返回，将错误向上传播。由于 `SerializeError` 实现了 `std::error::Error`，它可以自动转换为 `Box<dyn Error>`。

### 2. Option 处理模式

Rust 提供了多种优雅处理 `Option<T>` 的方式：

**as_deref().unwrap_or() 模式**（字符串快速读取）：
```rust
println!("主机名: {}", spec.hostname.as_deref().unwrap_or("(未设置)"));
```

**if let 模式**（条件访问）：
```rust
if let Some(ref root) = spec.root {
    println!("根文件系统: {}", root.path);
}
```

**match 模式**（多分支处理）：
```rust
match (user.uid, user.gid) {
    (Some(uid), Some(gid)) => println!("uid={}, gid={}", uid, gid),
    (Some(uid), None) => println!("uid={}", uid),
    // ...
}
```

**map/and_then 链式调用**：
```rust
let cwd = spec.process
    .as_ref()
    .and_then(|p| p.cwd.as_deref())
    .unwrap_or("/");
```

### 3. 引用级别注意事项

访问嵌套 Option 字段时，注意引用层次：

- `spec.hostname`: `Option<String>`（拥有所有权）
- `spec.hostname.as_ref()`: `Option<&String>`（借用）
- `spec.hostname.as_deref()`: `Option<&str>`（借用 + 解引用）

常见错误是忘记加 `ref` 导致所有权移动：
```rust
// ❌ 错误：会移动 proc
if let Some(proc) = spec.process {
    // proc 被移动，后续无法再访问 spec.process
}

// ✅ 正确：借用
if let Some(ref proc) = spec.process {
    // proc 是 &Process，不获取所有权
}
```

或者更符合 Rust 惯用写法：
```rust
if let Some(proc) = spec.process.as_ref() {
    // proc 是 &Process
}
```

### 4. 修改配置

修改字段时，需要先将 `Option` 变为可变。模式是：
1. `load()` 获取可变绑定 `let mut spec`
2. 直接赋值 `Some(value)` 给 `Option` 字段
3. 对于嵌套字段，先 `as_mut()` 获取可变引用

```rust
let mut spec = runtime::Spec::load(input)?;

// 修改顶层字段
spec.hostname = Some("new-name".to_string());

// 修改嵌套字段
if let Some(ref mut process) = spec.process {
    process.cwd = Some("/new/path".to_string());
}

// 修改 HashMap 字段
let mut annotations = spec.annotations.take().unwrap_or_default();
annotations.insert("key".to_string(), Some(value));
spec.annotations = Some(annotations);
```

`Option::take()` 是一个非常有用的模式：它取出 Option 中的值（留下 None），修改后再放回去，避免借用冲突。

### 5. 错误处理最佳实践

main 函数中演示了友好的错误提示模式：

```rust
if let Err(e) = result {
    eprintln!("\n错误: {}", e);
    
    let err_str = e.to_string();
    if err_str.contains("No such file") {
        eprintln!("提示: 请检查文件路径是否正确");
    } else if err_str.contains("expected value") {
        eprintln!("提示: JSON 解析失败，请检查文件格式");
    }
    
    process::exit(1);
}
```

实际项目中，推荐使用 `thiserror` 定义自定义错误类型，或使用 `anyhow` 简化错误处理。

### 6. 内存管理——什么都不用做！

注意代码中**没有任何 `free`、`drop` 或清理调用**。Rust 的所有权系统自动在变量离开作用域时释放所有内存：

- `spec` 在 `inspect_runtime` 函数返回时自动 drop
- 所有嵌套的 String、Vec、HashMap 自动递归释放
- 即使发生错误提前返回，RAII 也保证正确清理

这与 C 示例中需要仔细配对每个 `parse_file` 和 `free_` 形成鲜明对比。

## 扩展：使用 serde 直接操作

libocispec 类型都实现了 Serialize/Deserialize，你可以直接使用 serde_json 进行灵活操作：

```rust
use serde_json;

// 从字符串解析
let json_str = r#"{"ociVersion": "1.0.0", "hostname": "test"}"#;
let spec: runtime::Spec = serde_json::from_str(json_str)?;

// 序列化为值（动态访问）
let value: serde_json::Value = serde_json::to_value(&spec)?;
println!("hostname = {:?}", value["hostname"]);

// 合并两个 spec（通过 Value）
let mut base: serde_json::Value = serde_json::from_reader(file)?;
let overlay: serde_json::Value = serde_json::to_value(&overlay_spec)?;
// 使用 json_patch 等 crate 进行合并
```

## 测试

运行内置单元测试：

```sh
# 在 libocispec 源码目录
cargo test
```

在你的项目中也可以编写测试：

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_sample_config() {
        let spec = runtime::Spec::load("testdata/config.json").unwrap();
        assert_eq!(spec.oci_version, "1.0.0");
        assert!(spec.hostname.is_some());
    }
}
```

## 常见问题

### 编译错误：cannot find type in `runtime`

确保 Cargo.toml 中的 libocispec 依赖正确，并且版本包含需要的类型。某些较新的 OCI 字段可能需要最新版本。尝试：

```sh
cargo update
cargo clean
cargo build
```

### 链接错误或找不到 libocispec

由于 libocispec 是通过 git 依赖引入的，Cargo 会自动拉取和编译。确保网络能访问 GitHub。如果在企业防火墙后，可以配置 git 代理或使用镜像。

### 字段不存在或名称不对

Rust 绑定的字段名是 snake_case，但 OCI JSON 使用 camelCase。serde 的 `#[serde(rename)]` 属性自动处理映射。如果某个字段在代码中找不到：
1. 检查对应 JSON 字段名（camelCase）
2. 转换为 snake_case（`ociVersion` → `oci_version`）
3. 嵌套字段也是 Option 包裹，需要逐层解包

### 如何处理可选嵌套字段的链式访问

使用 `and_then` 或 `?` 运算符（在返回 Option 的函数中）：

```rust
let uid = spec.process.as_ref()
    .and_then(|p| p.user.as_ref())
    .and_then(|u| u.uid);
// uid 类型是 Option<i64>
```

## 相关主题

- [Rust API 使用指南](../concepts/02-rust-api.md) — Rust API 完整文档
- [C 语言示例](01-c-example.md) — C 版本的相同功能示例
- [Rust API 源码信源](../references/rust-api-source.md) — 类型定义和模块结构
- [双语言 API 对比](../concepts/03-bindings-comparison.md) — C 与 Rust API 设计差异
