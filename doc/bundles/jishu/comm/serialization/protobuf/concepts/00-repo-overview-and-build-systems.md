---
type: Concept
title: "仓库总览与双构建系统"
description: "protobuf 主仓 32 个顶层目录与 v37.0-dev 版本常量全景图，Bazel（MODULE.bazel、预编译 protoc toolchain）与 CMake（17 个 option、20 个模块）两套一等公民构建系统的并列讲解。"
tags: [protobuf, build-system, bazel, cmake]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: repo-structure
    resource: /references/repo-structure.md
    title: "protobuf 仓库结构与构建系统信源"
---

Protocol Buffers（protobuf）主仓是 Google 维护的语言中立序列化框架的单仓库（monorepo）：编译器（protoc）、C++ 运行时内核、upb 轻量 C 内核以及 Python、Java、C#、Objective-C、PHP、Ruby、Lua、Rust、hpb 等十余种语言运行时全部收拢在同一个仓库中。本篇是 protobuf 知识束入门组的第一篇，为后续所有概念文档提供空间坐标——先认识 32 个顶层目录分别承载什么，再理解本仓最特殊的工程事实：**Bazel 与 CMake 是并重的两条一等公民构建路径**，而非"主构建系统 + 备用脚本"的关系（本束洞察 5）。

## 仓库全景：32 个顶层目录

仓库根下共 32 个目录（F-REPO-001），可按职能分为五组：

- **编译器与 C++ 内核**：`src/`（C++ 运行时与编译器源码，本束 01-06 篇核心机制与 07-10 篇编译器文档的主场）、`editions/`（Editions 特性系统测试与默认值）、`go/`（Go 语言 proto 补充，含 `google/protobuf` 子目录与 BUILD.bazel，F-REPO-021）。
- **多语言运行时**：`python/`、`java/`、`csharp/`、`objectivec/`、`php/`、`ruby/`、`lua/`、`rust/`、`hpb/`（C++ 多后端 API 层）与 `hpb_generator/`、`upb/`（轻量 C 内核）与 `upb_generator/`。
- **测试与规范**：`conformance/`（一致性测试框架）、`benchmarks/`（基准测试）、`compatibility/`（版本兼容性冒烟测试）。
- **构建资产**：`bazel/`、`build_defs/`、`cmake/`、`toolchain/`、`pkg/`（发布打包）。
- **辅助设施**：`docs/`（设计文档）、`examples/`（入门教程）、`editors/`（编辑器插件）、`ci/`、`.github/`、`.bazelci/`、`.bcr/`（Bazel Central Registry）、`third_party/`（utf8_range 与 jsoncpp、zlib 的 BUILD 文件，F-REPO-024）、`patches/`（含 protobuf_v25 补丁集）。

顶层文件方面（F-REPO-002），构建入口包括 `BUILD.bazel`、`CMakeLists.txt`、`MODULE.bazel`、`WORKSPACE`、`WORKSPACE.bzlmod`、`.bazelrc`、`bazel9.bazelrc`；版本与依赖治理包括 `protobuf_version.bzl`、`protobuf_deps.bzl`、`protobuf_release.bzl`、`version.json`、`maven_install.json`；此外还有 `generate_descriptor_proto.sh`、`regenerate_stale_files.sh` 等源码再生成脚本。

## 版本常量体系

版本号分散在三个权威位置，各有分工（F-REPO-028 ~ F-REPO-031）：

- `protobuf_version.bzl` 定义 7 个常量：`PROTOC_VERSION = "37.0"`、`PROTOBUF_JAVA_VERSION = "4.37.0"`、`PROTOBUF_PYTHON_VERSION = "7.37.0"`、`PROTOBUF_PHP_VERSION = "5.37.0"`、`PROTOBUF_RUBY_VERSION = "4.37.0"`、`PROTOBUF_RUST_VERSION = "0.37.0"`、`PROTOBUF_LEGACY_RUST_VERSION = "4.37.0"`——各语言运行时版本节奏互不相同。
- `version.json` 的 `main` 段含 `protoc_version = "37-dev"`、`lts = false`、`date = "2026-07-09"`，`languages` 段给出 cpp/csharp/java/javascript/objectivec/php/python/ruby/rust/legacy_rust 十个语言的 `-dev` 版本号。
- `CMakeLists.txt` 含 `set(protobuf_VERSION_STRING "7.37.0")`，并用 `protobuf_VERSION_REGEX` 解析出 MAJOR/MINOR/PATCH/PRERELEASE 四个变量。
- `MODULE.bazel` 的 module 声明为 `name = "protobuf"`、`version = "37.0-dev"`（注释标注 "Automatically updated on release"）、`bazel_compatibility = [">=8.0.0"]`、`compatibility_level = 1`、`repo_name = "com_google_protobuf"`。

本知识束所有文档的版本基准即 v37.0-dev。

## CMake 构建系统

CMake 侧由根 `CMakeLists.txt` 加 `cmake/` 模块目录构成，要求 `cmake_minimum_required(VERSION 3.16...3.26)`、`project(protobuf C CXX)`（F-REPO-032）。它定义 **17 个 option**（F-REPO-033），覆盖从安装、测试到各产物的开关：

- 产物开关：`protobuf_BUILD_LIBPROTOBUF`（ON）、`protobuf_BUILD_LIBPROTOC`（OFF）、`protobuf_BUILD_LIBUPB`（ON）、`protobuf_BUILD_PROTOC_BINARIES`（ON）、`protobuf_BUILD_PROTOBUF_BINARIES`（ON）；
- 测试与示例：`protobuf_BUILD_TESTS`（OFF）、`protobuf_BUILD_CONFORMANCE`（OFF）、`protobuf_BUILD_EXAMPLES`（OFF）；
- 编译行为：`protobuf_DISABLE_RTTI`、`protobuf_ALLOW_CCACHE`、`protobuf_FORCE_FETCH_DEPENDENCIES`、`protobuf_LOCAL_DEPENDENCIES_ONLY`、`protobuf_USE_UNITY_BUILD`；
- 平台选项：`protobuf_WITH_ZLIB`、`protobuf_BUILD_SHARED_LIBS`；另有 `protobuf_INSTALL`（ON）与 `protobuf_TEST_XML_OUTDIR`。

`CMakeLists.txt` 按行号顺序 include 14 个仓库内模块（F-REPO-034）：`protobuf-options.cmake` → `gtest.cmake` → `abseil-cpp.cmake` → `utf8_range.cmake` → `libprotobuf-lite.cmake` → `libprotobuf.cmake` → `libprotoc.cmake` → `libupb.cmake` → `upb_generators.cmake` → `protoc.cmake` → `tests.cmake` → `conformance.cmake` → `install.cmake` → `examples.cmake`。注意连 conformance 都有独立模块与对应 option，这是"双一等公民"的直接证据。

`cmake/` 目录含 20 个 `.cmake` 文件（F-REPO-035），除上述模块外还有 `protobuf-generate.cmake`（`protobuf_generate` 的实现，供下游消费）、`protobuf-configure-target.cmake` 与三个 `.pc.cmake`（pkg-config 文件生成）；另有 4 个 `.in` 模板（`protobuf-config.cmake.in`、`protobuf-config-version.cmake.in`、`protobuf-module.cmake.in`、`version.rc.in`）和 4 个安装清单 golden 文件（`installed_bin_golden.txt` 等）用于校验安装产物完整性（F-REPO-036）。

## Bazel 构建系统

Bazel 侧正处于 WORKSPACE 到 bzlmod 的过渡期：`WORKSPACE` 声明 `workspace(name = "com_google_protobuf")` 并调用 `protobuf_deps()`（F-REPO-037）；`WORKSPACE.bzlmod` 仅含注释（F-REPO-038），模块化路径由 `MODULE.bazel` 承担：

- **非 dev 依赖** 17 个 `bazel_dep`（F-REPO-039）：abseil-cpp 20250512.1、rules_cc 0.2.18、rules_java 8.6.1、rules_kotlin 2.3.20、rules_python 2.3.0、rules_rust 0.69.0、rules_proto 7.1.0、zlib 1.3.1.bcr.5、bazel_skylib 1.9.0、platforms 0.0.11、re2、jsoncpp 等。
- **dev 依赖** 12 项（F-REPO-040）：googletest 1.17.0、google_benchmark 1.9.2、lua 5.4.6、rules_fuzzing 0.5.3、googleapis、`com_google_protobuf_v25`（archive_override，附 patches/protobuf_v25/ 下 8 个补丁）等。
- **预编译 protoc toolchain**（F-REPO-041）：通过 `use_extension` 定义 `prebuilt_protoc`，`use_repo` 声明 9 个平台仓库（linux_aarch_64、linux_ppcle_64、linux_s390_64、linux_x86_32、linux_x86_64、osx_aarch_64、osx_x86_64、win32、win64），并 `register_toolchains` 注册——构建时可直接下载平台匹配的 protoc 二进制，而不必先自举编译编译器。
- **语言工具链声明**：Python 支持 `SUPPORTED_PYTHON_VERSIONS = ["3.10", ..., "3.14"]`（F-REPO-042）；Rust 声明 `rust.toolchain(edition = "2024", versions = ["1.85.0"])`（F-REPO-043）；Maven 工件列表 `PROTOBUF_MAVEN_ARTIFACTS` 同时定义于 MODULE.bazel 与 protobuf_deps.bzl（F-REPO-044）；模块末尾还有 11 个 `flag_alias`（如 `protocopt`、`proto_compiler`、`strict_proto_deps`，F-REPO-045）。

交叉编译由 `//toolchain/`（4 个文件：`BUILD.bazel`、`cc_toolchain_config.bzl`、`platforms.bzl`、`toolchains.bazelrc`，F-REPO-026）与 MODULE.bazel/WORKSPACE 注册的 **10 个交叉编译 toolchain** 支撑（F-REPO-046）：osx-x86_64、osx-aarch_64、linux-aarch_64、linux-ppcle_64、linux-s390_64、linux-x86_32、linux-x86_64、win32、win64、k8。

规则资产方面：`bazel/` 目录含 8 个 `.bzl` 规则文件（F-REPO-050）——`proto_library.bzl`、`cc_proto_library.bzl`、`py_proto_library.bzl`、`java_proto_library.bzl`、`java_lite_proto_library.bzl`、`upb_c_proto_library.bzl`、`upb_proto_reflection_library.bzl`、`proto_descriptor_set.bzl`，及 common、flags、private、tests、toolchains 五个子目录；`build_defs/` 含 9 个文件（`cpp_opts.bzl`、`compiler_config_setting.bzl` 等，F-REPO-051）；`protobuf_deps.bzl` 提供 WORKSPACE 消费者加载片段（F-REPO-052）；`.bazelrc` 含 12 条 `--incompatible_*` 标志、`prefer_prebuilt_protoc=false` 与 dbg/opt/asan/msan/tsan/ubsan 及各编译器配置段（F-REPO-053）。

顶层 `BUILD.bazel`（F-REPO-047 ~ F-REPO-049）load 了各语言 proto_library 规则与 `cpp_opts.bzl`，并通过 alias 提供 10 个 Well-Known Types target 的四组变体（`_proto`/`_cc_proto`/`_upb_proto`/`_upb_reflection_proto`，共 40 个），actual 均指向 `//src/google/protobuf/` 下同名 target——WKT 详见 /concepts/16-wkt-conformance-benchmarks.md。

## 双构建系统如何选型

两套系统覆盖的产物面几乎等宽：lite 库、全量库、libprotoc、upb、conformance、examples 在两边都有入口。实践中 Google 内部与大规模 CI 矩阵走 Bazel（远程缓存、交叉编译 toolchain、prebuilt protoc），下游 CMake 消费者与嵌入式/系统打包场景走 CMake（option 细粒度裁剪、安装清单 golden 校验）。这一"双轨并行"也塑造了 CI 侧的分层缓存治理（由独立的 protobuf-ci 知识束展开），两束在"构建系统"主题上仅以交叉引用衔接。

## 辅助目录群

- `docs/`：顶层 7 个 .md（`cmake_protobuf_generate.md`、`cpp_build_systems.md`、`field_presence.md`、`implementing_proto3_presence.md`、`jvm_aot.md`、`options.md`、`third_party.md`），及 `csharp/`、`design/`（含 editions 设计文档 22 篇与 prototiller 4 篇）、`upb/`（arena 融合、vs-cpp-protos 等 6 篇）三个子目录（F-REPO-056 ~ F-REPO-059）。
- `editors/`：proto.vim、protobuf-mode.el（F-REPO-061）。
- `ci/`：clang_wrapper、push_auto_update.sh、python_compatibility.sh 等 5 个文件（F-REPO-062）。
- `compatibility/`：`smoke/` 下 9 个历史版本目录（v3.0.0 至 v32.1）加 `v3.25.0/`，保障生成代码跨版本兼容（F-REPO-063 ~ F-REPO-065）。
- `pkg/`：发布分发资产（`cc_dist_library.bzl` 等，F-REPO-027）。

## 相关概念

- [/concepts/01-message-model.md](/concepts/01-message-model.md)——进入 src/ 后的第一个主题：Message 与 MessageLite 类层次。
- [/concepts/02-wire-format.md](/concepts/02-wire-format.md)——二进制编码格式，理解 protobuf 的传输基础。
- [/concepts/07-protoc-command-line.md](/concepts/07-protoc-command-line.md)——构建系统最终调用的编译器命令行。
- [/concepts/15-editions-feature-system.md](/concepts/15-editions-feature-system.md)——editions/ 目录背后的特性系统设计。
