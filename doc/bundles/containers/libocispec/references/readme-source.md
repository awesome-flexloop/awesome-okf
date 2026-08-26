---
type: Reference
title: README 项目说明信源
description: libocispec 项目 README 文档的源码解析与关键信息提取
tags: [reference, readme, source, oci, libocispec]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme
    resource: https://github.com/containers/libocispec/blob/main/README.md
    title: libocispec README.md
---

# README 项目说明信源

本文档提取自 libocispec 项目的 README.md，记录项目定位、安装方法与基本使用示例。

## 项目定位

libocispec 是一个用于轻松解析 [OCI runtime](https://github.com/opencontainers/runtime-spec) 和 [OCI image](https://github.com/opencontainers/image-spec) 规范文件的库，支持从 C 语言解析，并能从对应结构体生成 JSON 字符串。

> 解析器直接从源仓库中的 JSON schema 生成。

## 依赖与安装

### C 语言版本依赖

- **json-c** 库，版本要求 ≥ 0.14

### 构建与安装步骤（autotools）

```sh
$ ./autogen.sh
$ ./configure
$ make
$ sudo make install
```

## C 语言基本使用示例

### 解析 OCI 配置文件

```c
#include <config.h>
#include <runtime_spec_schema_config_schema.h>

runtime_spec_schema_config_schema *container = runtime_spec_schema_config_schema_parse_file ("config.json", NULL, &err);

if (container == NULL)
  exit (EXIT_FAILURE);

/* Print the container hostname.  */
if (container->hostname)
    printf ("The specified hostname is %s\n", container->hostname);

for (size_t i; i < container->mounts_len; i++)
    printf ("Mounting to %s\n", container->mounts[i]->destination);

printf ("Running as user ID and GID %d %d\n", container->process->user->uid, container->process->user->gid);
```

### 生成 OCI 配置 JSON 字符串

```c
#include <config.h>
#include <runtime_spec_schema_config_schema.h>

runtime_spec_schema_config_schema container;
char *json_buf = NULL;

memset (&container, 0, sizeof (runtime_spec_schema_config_schema));

container.oci_version = "2";
container.hostname = "ubuntu";
/* Add other configuration. */
/* ... ... */

json_buf = runtime_spec_schema_config_schema_generate_json (&container, NULL, &err);
if (json_buf == NULL)
  exit (EXIT_FAILURE);

printf ("The generated json string is:\n%s\n", json_buf);
```

## Rust 绑定

libocispec 也支持 Rust 绑定。可以直接将其作为依赖添加到 `Cargo.toml` 中使用，或者使用 `make generate-rust` 重新生成类型定义。

### Cargo.toml 依赖配置

```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec" }
```

对于早于 `0.51.0` 的 Cargo 版本，需要显式指定分支：

```toml
[dependencies]
libocispec = { git = "https://github.com/containers/libocispec", branch = "main" }
```

### Rust 使用示例

```rust
extern crate libocispec;
use libocispec::runtime;
use libocispec::image;

fn main() {
    let runtime_spec = match runtime::Spec::load("path/to/spec") {
        Ok(spec) => spec,
        Err(e) => panic!("{}", e),
    }
    let image_spec = match image::ImageConfig::load("path/to/spec") {
        Ok(spec) => spec,
        Err(e) => panic!("{}", e),
    }
}
```

## 相关信源

- [C API 源码信源](c-api-source.md) — C 语言公共头文件与核心实现
- [Rust API 源码信源](rust-api-source.md) — Rust crate 模块结构与序列化实现
