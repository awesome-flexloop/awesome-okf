---
type: Reference
title: "protobuf 仓库结构与构建系统信源登记"
description: "登记 protobuf 主仓 v37.0-dev 根目录结构、版本常量与 Bazel/CMake 双构建系统的源码路径，支撑 F-REPO-001~067 共 67 条事实的溯源。"
tags: [protobuf, repo-structure, build-system, bazel, cmake]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-source
    resource: external/libs/protocolbuffers/protobuf
    title: "protobuf 主仓库源码（v37.0-dev）"
---

本信源文件登记 protobuf 主仓库根目录结构相关的源码路径，是 R 阶段事实清单 facts-repo-structure.md（F-REPO-001~067，共 67 条事实）的信源登记表。protobuf 束 concepts/ 中凡引用 F-REPO 编号事实的文档，其 frontmatter 的 sources 字段均应指向本文件。

登记范围覆盖：仓库根 32 个顶层目录与顶层构建文件、版本常量定义文件、Bazel 与 CMake 双构建系统的配置目录、editions 特性系统目录、docs/ 文档目录，以及 editors/、ci/、compatibility/、pkg/、third_party/、patches/、go/ 等辅助目录。除特别说明外，路径均相对 protobuf 主仓根。

## 源码版本信息

| 常量 | 值 |
|------|-----|
| PROTOC_VERSION | 37.0 |
| PROTOBUF_JAVA_VERSION | 4.37.0 |
| PROTOBUF_PYTHON_VERSION | 7.37.0 |
| PROTOBUF_PHP_VERSION | 5.37.0 |
| PROTOBUF_RUBY_VERSION | 4.37.0 |
| PROTOBUF_RUST_VERSION | 0.37.0 |
| PROTOBUF_LEGACY_RUST_VERSION | 4.37.0 |

版本常量来自主仓根 protobuf_version.bzl；版本基准 v37.0-dev（F-REPO-028、F-REPO-031）。源码根路径：external/libs/protocolbuffers/protobuf。

## 核心模块与文件清单

### 仓库根（32 个顶层目录 + 顶层文件清单）

- `BUILD.bazel` — 顶层 Bazel 构建定义
- `CMakeLists.txt` — 顶层 CMake 构建入口
- `MODULE.bazel` — Bazel 模块依赖声明
- `WORKSPACE` — Bazel 工作区文件
- `WORKSPACE.bzlmod` — bzlmod 模式工作区
- `protobuf_version.bzl` — 版本常量定义
- `protobuf_deps.bzl` — Bazel 外部依赖声明
- `protobuf_release.bzl` — 发布相关规则
- `protobuf.bzl` — Bazel 辅助规则
- `version.json` — 版本元数据 JSON
- `.bazelrc` — Bazel 默认配置
- `bazel9.bazelrc` — Bazel 9 专用配置

（以上为顶层文件清单等；仓库根另含 32 个顶层目录。）

### 关键根文件（版本与双构建系统入口）

- `protobuf_version.bzl` — 版本常量定义
- `version.json` — 版本元数据 JSON
- `CMakeLists.txt` — 顶层 CMake 构建入口
- `MODULE.bazel` — Bazel 模块依赖声明
- `WORKSPACE` — Bazel 工作区文件
- `WORKSPACE.bzlmod` — bzlmod 模式工作区
- `.bazelrc` — Bazel 默认配置
- `BUILD.bazel`（顶层） — 顶层 Bazel 构建定义

### cmake/（CMake 构建系统）

- `cmake/` — 20 个 .cmake 模块 + 4 个 .in 模板 + 4 个 golden 清单

### bazel/、build_defs/、toolchain/（Bazel 构建系统）

- `bazel/` — 8 个 .bzl 规则与 common/flags/private/tests/toolchains 子目录
- `build_defs/` — 9 个构建定义文件
- `toolchain/` — 4 个交叉编译工具链文件

### editions/（Editions 特性系统）

- `editions/` — 含 defaults.bzl、BUILD、codegen_tests/、golden/、input/

### docs/（文档目录）

- `docs/` — 7 个 .md 与 csharp/、design/、upb/ 子目录

### 辅助目录

- `editors/` — 编辑器支持目录
- `ci/` — CI 辅助脚本目录
- `compatibility/` — 兼容性目录（smoke/、v3.25.0/）
- `pkg/` — 打包配置目录
- `third_party/` — 第三方依赖目录
- `patches/` — 补丁文件目录
- `go/` — Go 生态辅助目录

## 事实关联

| 事实区间 | 条数 | 事实清单文件 |
|---|---|---|
| F-REPO-001 ~ F-REPO-067 | 67 | facts-repo-structure.md |

事实清单文件为 R 阶段产出，位于 spec 目录 .trae/specs/protocolbuffers-okf-wiki/。本束 concepts/ 文档中所有 F-REPO 编号事实均以本信源登记的源码路径为出处。

## 相关概念

- /concepts/00-repo-overview-and-build-systems.md — 主消费者（覆盖 F-REPO-001、002、021、024、026~053、056~059、061~065）
- /concepts/12-upb-and-rust-runtime.md — 含 F-REPO-013、014、015、019、020
- /concepts/13-hpb.md — 含 F-REPO-017、018
- /concepts/14-other-language-runtimes.md — 含 F-REPO-006~012、016
- /concepts/15-editions-feature-system.md — 含 F-REPO-049、054、055
- /concepts/16-wkt-conformance-benchmarks.md — 含 F-REPO-004、048
