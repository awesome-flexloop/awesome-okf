---
type: Concept
title: OCI 规范与代码生成机制
description: libocispec 项目定位、OCI 规范简介、JSON Schema 代码生成原理、双语言绑定架构概览
tags: [concept, introduction, overview, oci, code-generation, schema, json-schema]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme-source
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: README 项目说明信源
  - id: c-api-source
    resource: /bundles/containers/libocispec/references/c-api-source.md
    title: C API 源码信源
  - id: rust-api-source
    resource: /bundles/containers/libocispec/references/rust-api-source.md
    title: Rust API 源码信源
---

# OCI 规范与代码生成机制

## libocispec 是什么

libocispec 是 containers 组织下的开源库，专门用于**解析和生成 OCI（Open Container Initiative）规范文件**。它同时提供 C 语言和 Rust 语言两套绑定，让容器运行时开发者能够以类型安全的方式操作 OCI 配置文件。

> libocispec 的核心特点：**解析器直接从 JSON Schema 自动生成**，而非手动编写。这确保了 API 与官方规范的严格一致性，当 OCI 规范更新时只需重新运行代码生成器即可同步更新。

## OCI 规范简介

OCI（Open Container Initiative）是 Linux 基金会旗下的开放容器标准组织，定义了容器运行时和镜像的两大核心规范：

### OCI Runtime Specification（运行时规范）

定义容器运行时的配置格式和生命周期，核心是 `config.json` 文件。该文件描述了如何运行一个容器，包括：

- **进程配置**：命令、参数、环境变量、工作目录、用户/组 ID、终端
- **根文件系统**：根路径、是否只读
- **挂载点**：需要挂载到容器内的目录列表
- **平台特定配置**：Linux namespaces、cgroups、capabilities、seccomp、sysctl；Windows/Hyper-V；Solaris zones；z/OS；VM-based containers
- **生命周期钩子**：prestart、poststart、poststop、createRuntime、createContainer、startContainer
- **注解**：任意键值对元数据

### OCI Image Specification（镜像规范）

定义容器镜像的格式，核心是镜像配置 JSON，包括：

- **架构与 OS**：CPU 架构（amd64/arm64 等）、操作系统（linux/windows 等）
- **根文件系统 diff**：层叠文件系统的 diff_id 列表
- **历史记录**：每一层的创建命令、作者、时间戳
- **运行时配置**：默认入口点、命令、环境变量、工作目录、暴露端口、用户、卷、标签、停止信号

### 为什么需要专门的解析库？

直接使用通用 JSON 解析库操作 OCI 配置存在以下问题：

1. **类型不安全**：JSON 字段名拼写错误只能在运行时发现
2. **手动映射繁琐**：每个字段都需要手动从 JSON 对象提取、类型转换
3. **规范跟进困难**：OCI 规范更新时需要同步修改大量解析代码
4. **内存管理复杂**：C 语言中嵌套 JSON 对象的内存释放容易出错
5. **序列化同样繁琐**：将结构体写回 JSON 也需要重复劳动

libocispec 通过代码生成一次性解决所有这些问题。

## 代码生成机制

### 代码生成流程

libocispec 使用 Python 脚本从 OCI 规范的 JSON Schema 文件生成 C 和 Rust 代码：

```
┌─────────────────────────────────────────────────────────────────┐
│                    OCI 规范 JSON Schema                         │
│  (runtime-spec/schema/*.json, image-spec/schema/*.json)         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               Python 代码生成器（src/ocispec/）                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ generate.py │→ │ headers.py  │→ │ C 头文件    │             │
│  │  (主入口)   │  │ sources.py  │  │ C 源文件    │             │
│  │             │  │ json_api.py │  │ Rust 类型   │             │
│  │             │  │ helpers.py  │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    生成的类型安全 API                           │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │     C 绑定            │    │    Rust 绑定          │          │
│  │  ∙ 结构体定义         │    │  ∙ #[derive(Serialize,│          │
│  │  ∙ parse_file()      │    │     Deserialize)]     │          │
│  │  ∙ generate_json()   │    │  ∙ Option<T> 可选字段 │          │
│  │  ∙ free_*() 内存管理 │    │  ∙ load()/save() 便捷 │          │
│  │  ∙ clone_*() 深拷贝  │    │    方法               │          │
│  └──────────────────────┘    └──────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Python 生成器模块

`src/ocispec/` 目录下的 Python 脚本分工：

| 脚本 | 职责 |
|------|------|
| `generate.py` | 主入口，解析 JSON Schema、协调各生成器 |
| `headers.py` | 生成 C 头文件（结构体声明、函数原型） |
| `sources.py` | 生成 C 源文件（解析、生成、释放、克隆函数实现） |
| `json_api.py` | 生成 JSON 访问辅助函数 |
| `helpers.py` | 命名转换、类型映射等辅助函数 |

### 重新生成代码

当 OCI 规范更新后，可以重新生成绑定代码：

```sh
# 重新生成 Rust 类型绑定
make generate-rust
```

C 代码在 `make` 构建过程中通过 autotools 规则自动生成。

## 双语言绑定架构

libocispec 同时提供 C 和 Rust 两套独立绑定，它们共享同一个代码生成器，但各自遵循语言的惯用设计：

```
libocispec/
├── src/
│   ├── lib.rs              # Rust crate 入口
│   ├── serialize.rs        # Rust 序列化基础设施
│   ├── runtime/mod.rs      # Rust: Runtime Spec 类型（生成）
│   ├── image/mod.rs        # Rust: Image Spec 类型（生成）
│   └── ocispec/
│       ├── json_common.h   # C: 公共头文件
│       ├── json_common.c   # C: 公共实现
│       ├── validate.c      # C: 验证逻辑
│       ├── generate.py     # 代码生成器
│       ├── headers.py      # C 头文件生成器
│       ├── sources.py      # C 源文件生成器
│       ├── json_api.py     # JSON API 生成器
│       └── helpers.py      # 辅助函数
├── tests/                  # C 测试用例（15个）
├── Cargo.toml              # Rust crate 配置
├── Makefile.am             # C 构建配置
└── README.md
```

### C 绑定设计特点

- **基于 json-c**：底层使用成熟的 json-c 库进行 JSON 解析
- **手动内存管理**：每个类型都有对应的 `free_*()` 函数释放内存
- **显式长度字段**：数组类型使用指针+长度两个字段表示（如 `mounts` + `mounts_len`）
- **可选字段标志**：可选数值字段使用 `*_present` 布尔标志区分"未设置"和"零值"
- **autotools 构建**：使用传统的 `./autogen.sh && ./configure && make` 构建流程
- **pkg-config 支持**：安装后提供 `ocispec.pc` 供 pkg-config 使用

### Rust 绑定设计特点

- **基于 serde**：使用 Rust 生态标准的 serde 框架进行序列化/反序列化
- **自动内存管理**：Rust 所有权系统自动处理内存释放，无需手动 free
- **Option 类型**：可选字段直接使用 `Option<T>`，类型系统保证安全
- **Vec 类型**：数组使用 `Vec<T>`，长度自动管理
- **Cargo 构建**：标准 Rust 包管理，通过 git 依赖直接引入
- **snake_case/camelCase 映射**：`#[serde(rename)]` 属性自动处理字段名转换
- **便捷方法**：为根类型提供 `load()`/`save()` 方法直接读写文件
- **错误类型统一**：`SerializeError` 统一封装 I/O 和 JSON 错误

## 设计哲学

libocispec 的设计体现了以下原则：

### 1. 规范即代码（Spec as Code）

解析器不是"实现"规范，而是"从规范生成"。JSON Schema 是唯一可信源，代码生成器确保生成代码与规范的完全一致性。

### 2. 双语言一等公民支持

C 和 Rust 绑定不是"主从"关系，而是各自独立设计，遵循各自语言的最佳实践。C API 面向系统编程场景（如 runc/crun 这类运行时），Rust API 面向 Rust 生态的容器工具（如 youki）。

### 3. 零额外抽象

libocispec 不提供高层的"便利 API"，只做一件事：在 OCI JSON 和类型化数据结构之间做双向转换。错误处理、验证逻辑（除基础结构外）留给上层应用。

### 4. 生成代码可读

虽然代码是自动生成的，但生成的 C 和 Rust 代码保持了良好的可读性和一致的命名风格，便于调试。

## 适用场景

libocispec 适合以下场景：

| 场景 | 推荐绑定 |
|------|----------|
| 编写 OCI 容器运行时（C 语言） | C API |
| 编写容器工具需要解析 config.json | C API / Rust API |
| Rust 生态容器项目（如 youki） | Rust API |
| 生成符合 OCI 规范的配置文件 | C API / Rust API |
| 验证 OCI 配置文件的结构合法性 | C API（validate 模块） |
| 需要随 OCI 规范快速同步更新 | 两套均可（代码生成） |

## 相关概念

- [C API 使用指南](01-c-api.md) — C 语言绑定的完整使用流程
- [Rust API 使用指南](02-rust-api.md) — Rust 绑定的完整使用流程
- [双语言 API 对比](03-bindings-comparison.md) — C 与 Rust API 设计差异详细对比
