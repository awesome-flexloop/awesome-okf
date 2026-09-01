---
type: Reference
title: "protobuf 测试与规范体系信源登记"
description: "登记 protobuf 主仓 conformance 一致性测试、benchmarks 基准、examples 教程、editions 测试与 CI 辅助源码路径，支撑 F-TST-001~080。"
tags: [protobuf, conformance, benchmarks, testing, examples]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-source
    resource: external/libs/protocolbuffers/protobuf
    title: "protobuf 主仓库源码（v37.0-dev）"
---

本信源文件登记 protobuf 测试与规范体系的源码路径，是 R 阶段事实清单 facts-testing.md（F-TST-001~080，共 80 条事实）的信源登记表。protobuf 束 concepts/ 与 examples/ 中凡引用 F-TST 编号事实的文档，其 frontmatter 的 sources 字段均应指向本文件。

登记范围覆盖：conformance/ 一致性测试框架（含各语言被测端与 failure list）、benchmarks/ 基准测试、examples/ 官方入门教程（addressbook）、editions/ 特性系统测试、ci/ 辅助脚本，以及 cmake/tests.cmake 测试构建配置与 editors/ 编辑器支持。除特别说明外，路径均相对 protobuf 主仓根。

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

### conformance/（一致性测试框架）

- `conformance/README.md` — 框架说明文档
- `conformance/conformance.proto` — 测试协议定义
- `conformance/conformance_test_runner.cc` — 测试运行器
- `conformance/conformance_test.cc/.h` — 测试套件实现
- `conformance/conformance_test_main.cc` — 测试主入口
- `conformance/test_runner.h` — TestRunner 接口
- `conformance/testee.h/.cc` — 被测端封装
- `conformance/test_manager.h/.cc` — 测试管理器
- `conformance/naming.h` — 命名工具
- `conformance/failure_list_trie_node.cc/.h` — 失败清单 trie 节点
- `conformance/binary_json_conformance_suite.cc/.h` — 二进制/JSON 套件
- `conformance/text_format_conformance_suite.cc/.h` — 文本格式套件
- `conformance/binary_wireformat.cc/.h` — 二进制 wire 套件
- `conformance/fork_pipe_runner.cc/.h` — fork 管道运行器
- `conformance/defs.bzl` — 构建规则
- `conformance/BUILD` — 构建定义
- `conformance/bazel_conformance_test_runner.sh` — Bazel 运行脚本
- `conformance/conformance_cpp.cc` — C++ 被测端
- `conformance/conformance_objc.m` — Objective-C 被测端
- `conformance/conformance_php.php` — PHP 被测端
- `conformance/conformance_python.py` — Python 被测端
- `conformance/conformance_rust.rs` — Rust 被测端
- `conformance/ConformanceJava.java` — Java 被测端
- `conformance/ConformanceJavaLite.java` — JavaLite 被测端
- `conformance/update_failure_list.py` — 失败清单更新脚本
- `conformance/failure_list_*.txt` — 失败清单（全 19 个）
- `conformance/text_format_failure_list_*.txt` — 文本格式失败清单（全 8 个）
- `conformance/ruby/` — Ruby 被测端目录
- `conformance/test_protos/` — 测试 proto 目录

### benchmarks/（基准测试）

- `benchmarks/BUILD` — 构建定义
- `benchmarks/build_defs.bzl` — 构建规则
- `benchmarks/benchmark.cc` — 基准测试实现
- `benchmarks/compare.py` — 结果对比脚本
- `benchmarks/descriptor.proto` — 基准用 proto
- `benchmarks/descriptor_sv.proto` — STRING_PIECE 变体 proto
- `benchmarks/empty.proto` — 空 proto
- `benchmarks/gen_protobuf_binary_cc.py` — C++ 二进制生成脚本
- `benchmarks/gen_synthetic_protos.py` — 合成 proto 生成脚本
- `benchmarks/gen_upb_binary_c.py` — upb 二进制生成脚本

### examples/（官方入门教程）

- `examples/addressbook.proto` — 教程 schema
- `examples/add_person.cc/.py/.rb/.dart` — 写入示例（4 语言）
- `examples/list_people.cc/.py/.rb/.dart` — 读取示例（4 语言）
- `examples/AddPerson.java` — Java 写入示例
- `examples/ListPeople.java` — Java 读取示例
- `examples/CMakeLists.txt` — CMake 构建入口
- `examples/Makefile` — Make 构建入口
- `examples/BUILD.bazel` — Bazel 构建入口
- `examples/MODULE.bazel` — Bazel 模块定义
- `examples/README.md` — 教程说明文档
- `examples/pubspec.yaml` — Dart 包定义

### editions/（Editions 特性系统测试）

- `editions/defaults.bzl` — edition 默认值规则
- `editions/defaults_test.cc` — 默认值测试
- `editions/edition_defaults_test_utils.cc/.h` — 默认值测试工具
- `editions/generated_files_test.cc` — 生成文件测试
- `editions/generated_reflection_test.cc` — 生成反射测试
- `editions/internal_defaults_escape.cc` — 默认值转义测试
- `editions/BUILD` — 构建定义
- `editions/*.h.template` — 头文件模板（4 个）
- `editions/codegen_tests/` — codegen 测试 proto（56 个）

### ci/（CI 辅助脚本）

- `ci/README.md` — 说明文档
- `ci/clang_wrapper` — clang 包装脚本
- `ci/clang_wrapper++` — clang++ 包装脚本
- `ci/python_compatibility.sh` — Python 兼容性脚本
- `ci/push_auto_update.sh` — 自动更新推送脚本

### 其他（测试构建与编辑器支持）

- `cmake/tests.cmake` — 测试构建配置
- `editors/proto.vim` — Vim 语法文件
- `editors/protobuf-mode.el` — Emacs 模式文件
- `editors/README.txt` — 说明文件

## 事实关联

| 事实区间 | 条数 | 事实清单文件 |
|---|---|---|
| F-TST-001 ~ F-TST-080 | 80 | facts-testing.md |

事实清单文件为 R 阶段产出，位于 spec 目录 .trae/specs/protocolbuffers-okf-wiki/。本束 concepts/ 与 examples/ 文档中所有 F-TST 编号事实均以本信源登记的源码路径为出处。

## 相关概念

- /concepts/04-arena-memory-management.md — 含 F-TST-039
- /concepts/06-text-format-and-json.md — 含 F-TST-011
- /concepts/15-editions-feature-system.md — 含 F-TST-066~073
- /concepts/16-wkt-conformance-benchmarks.md — 含 F-TST-001~049、076、079、080

此外，examples/ 下 5 篇示例文档（/examples/01-addressbook-proto.md、/examples/02-cpp-tutorial.md、/examples/03-python-tutorial.md、/examples/04-java-ruby-dart-tutorials.md、/examples/05-examples-build-systems.md，覆盖 F-TST-050~065）亦引用本信源。
