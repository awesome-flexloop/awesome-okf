---
okf_version: "0.2"
type: Bundle
title: libocispec：OCI 规范文件解析库
description: libocispec 是一个用于解析和生成 OCI Runtime/Image 规范文件的库，提供 C 和 Rust 双语言绑定，解析器直接从 JSON Schema 代码生成
tags: [bundle, oci, containers, parsing, c, rust, code-generation, json-schema]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: repo
    resource: https://github.com/containers/libocispec
    title: containers/libocispec GitHub 仓库
  - id: runtime-spec
    resource: https://github.com/opencontainers/runtime-spec
    title: OCI Runtime Specification
  - id: image-spec
    resource: https://github.com/opencontainers/image-spec
    title: OCI Image Specification
---

# libocispec：OCI 规范文件解析库

libocispec 是 [containers](https://github.com/containers) 组织下的开源库，专门用于**解析和生成 OCI（Open Container Initiative）规范文件**。它同时提供 C 语言和 Rust 语言两套绑定，解析器直接从 JSON Schema 自动生成，确保 API 与官方 OCI 规范的严格一致性。

libocispec 是容器运行时生态的基础组件，被 crun、youki 等容器运行时和工具用于类型安全地操作 `config.json` 等 OCI 配置文件。

## 📚 快速导航

### [概念文档](concepts/index.md)

**入门：**
- [00-OCI规范与代码生成机制](concepts/00-introduction.md) — libocispec 是什么、OCI 规范简介、JSON Schema 代码生成原理、双语言绑定架构概览 ⭐

**核心：**
- [01-C API 使用指南](concepts/01-c-api.md) — 编译链接、解析配置、字段访问、手动构建、内存管理、错误处理、完整示例
- [02-Rust API 使用指南](concepts/02-rust-api.md) — Cargo 依赖、load/save 方法、Option 模式、serde 使用、错误处理、完整示例

**深度对比：**
- [03-双语言API对比](concepts/03-bindings-comparison.md) — 类型系统、内存管理、错误处理、构建系统、功能覆盖、适用场景推荐

### [实践示例](examples/index.md)
- [01-C 语言解析 OCI 配置](examples/01-c-example.md) — 完整 C 程序：解析 config.json、打印摘要、修改后重新生成 JSON ⭐入门
- [02-Rust 语言解析 OCI 配置](examples/02-rust-example.md) — 完整 Rust 项目：inspect/modify 命令、Runtime/Image Spec 双支持

### [信源参考](references/index.md)
- [README 项目说明信源](references/readme-source.md) — 项目定位、安装方法、官方使用示例
- [C API 源码信源](references/c-api-source.md) — C 头文件结构、核心函数签名、解析选项、内存管理宏、数据类型
- [Rust API 源码信源](references/rust-api-source.md) — Cargo 配置、模块结构、SerializeError、Runtime/Image 类型、serde 属性

## 🚀 核心特性

| 特性 | 说明 |
|------|------|
| 🔄 代码生成 | 解析器从 OCI JSON Schema 自动生成，规范更新时只需重新生成 |
| 🔀 双语言绑定 | 一等公民支持 C 和 Rust，各自遵循语言惯用设计 |
| 🔒 类型安全 | C 版本提供类型化结构体；Rust 版本编译期保证类型安全 |
| 📦 双向转换 | 支持 JSON → 类型化结构体（解析）和结构体 → JSON（生成） |
| 🧠 Runtime + Image | 同时支持 OCI Runtime Spec 和 OCI Image Spec |
| 🛡️ 内存安全选项 | C 版本手动控制；Rust 版本所有权系统自动管理 |
| ⚡ 零开销抽象 | C 版本基于 json-c 极低开销；Rust 版本基于 serde 高性能 |
| 🔧 灵活选项 | 支持严格模式、紧凑/美化 JSON、UTF-8 验证控制等 |

## 🎯 快速开始

### C 版本 30 秒上手

```c
#include <runtime_spec_schema_config_schema.h>

// 解析配置
parser_error err = NULL;
auto *config = runtime_spec_schema_config_schema_parse_file("config.json", 0, &err);
if (!config) { /* 错误处理 */ }

// 访问字段
printf("hostname: %s\n", config->hostname);
printf("OCI version: %s\n", config->oci_version);

// 生成 JSON
char *json = runtime_spec_schema_config_schema_generate_json(config, 0, &err);

// 清理
free(json);
free_runtime_spec_schema_config_schema(config);
```

编译：
```sh
gcc -o prog prog.c $(pkg-config --cflags --libs ocispec)
```

### Rust 版本 30 秒上手

Cargo.toml:
```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec" }
```

代码：
```rust
use libocispec::runtime;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 加载配置
    let spec = runtime::Spec::load("config.json")?;
    
    // 访问字段
    println!("hostname: {:?}", spec.hostname);
    println!("OCI version: {}", spec.oci_version);
    
    // 修改并保存
    // spec.hostname = Some("new-name".to_string());
    // spec.save("output.json")?;
    
    Ok(())
}
```

运行：
```sh
cargo run
```

## 📖 推荐学习路径

1. **理解定位**：阅读 [00-introduction](concepts/00-introduction.md) 了解 libocispec 解决什么问题、代码生成机制如何工作
2. **选择语言绑定**：
   - C 开发者 → 阅读 [01-c-api](concepts/01-c-api.md)，然后动手 [01-c-example](examples/01-c-example.md)
   - Rust 开发者 → 阅读 [02-rust-api](concepts/02-rust-api.md)，然后动手 [02-rust-example](examples/02-rust-example.md)
3. **对比选型**：如果在做技术选型，阅读 [03-bindings-comparison](concepts/03-bindings-comparison.md) 了解两套 API 的差异与适用场景
4. **源码精读**：配合 [references](references/index.md) 中的信源文档直接对照源码阅读

## 🏗️ 项目架构

```
libocispec
├── 代码生成器（Python）
│   └── src/ocispec/
│       ├── generate.py      # 主入口
│       ├── headers.py       # C 头文件生成
│       ├── sources.py       # C 源文件生成
│       ├── json_api.py      # JSON API 生成
│       └── helpers.py       # 辅助函数
│
├── C 绑定
│   ├── src/ocispec/json_common.h/c  # 公共基础设施
│   ├── src/ocispec/validate.c       # OCI 验证
│   └── （生成的）runtime_spec_schema_*.h/c
│
└── Rust 绑定
    ├── src/lib.rs           # crate 入口（load/save 方法）
    ├── src/serialize.rs     # 序列化/错误类型
    ├── src/runtime/mod.rs   # Runtime Spec 类型（生成）
    └── src/image/mod.rs     # Image Spec 类型（生成）
```

## 🔗 外部资源

- **GitHub 仓库**：[containers/libocispec](https://github.com/containers/libocispec)
- **OCI Runtime Spec**：[opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec)
- **OCI Image Spec**：[opencontainers/image-spec](https://github.com/opencontainers/image-spec)
- **json-c 库**：[json-c/json-c](https://github.com/json-c/json-c)（C 版本依赖）
- **serde 框架**：[serde-rs/serde](https://github.com/serde-rs/serde)（Rust 版本依赖）
- **crun**：[containers/crun](https://github.com/containers/crun) — 使用 C 绑定的 OCI 运行时
- **youki**：[containers/youki](https://github.com/containers/youki) — 使用 Rust 绑定的 OCI 运行时

## 容器生态中的位置

```
┌─────────────────────────────────────────────────────────────┐
│                  容器工具/编排层                             │
│  Podman / CRI-O / Docker / buildah / skopeo                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ 使用
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  OCI 运行时层                                │
│  runc (C) / crun (C) / youki (Rust) / krun                 │
│         │                      │                           │
│         └──────► libocispec ◄──┘                           │
│                  │      │                                   │
│           C API ─┘      └─ Rust API                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ 解析/生成
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              OCI JSON 配置文件                              │
│  config.json (runtime) / image config (image)              │
└─────────────────────────────────────────────────────────────┘
```

libocispec 作为"JSON ↔ 类型化结构体"的转换层，让上层运行时和工具无需手动编写 JSON 解析/生成代码，直接操作类型安全的结构体。

```{toctree}
:maxdepth: 2
:caption: 目录

concepts/index
examples/index
references/index
log
```
