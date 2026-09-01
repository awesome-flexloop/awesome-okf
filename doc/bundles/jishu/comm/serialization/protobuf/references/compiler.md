---
type: Reference
title: "protoc 编译器信源登记"
description: "登记 src/google/protobuf/compiler/ 下 protoc 源码路径，覆盖命令行框架、解析导入、九语言生成器与插件协议，支撑 F-CMP-001~090。"
tags: [protobuf, protoc, code-generator, plugin-protocol]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-source
    resource: external/libs/protocolbuffers/protobuf
    title: "protobuf 主仓库源码（v37.0-dev）"
---

本信源文件登记 protoc 编译器的源码路径，是 R 阶段事实清单 facts-compiler.md（F-CMP-001~090，共 90 条事实）的信源登记表。protobuf 束 concepts/ 中凡引用 F-CMP 编号事实的文档，其 frontmatter 的 sources 字段均应指向本文件。

登记范围覆盖 src/google/protobuf/compiler/ 下的编译器入口（含无内置生成器变体）、命令行框架、proto 语法解析与导入体系、CodeGenerator 抽象与插件协议，以及 cpp/java/python/csharp/objectivec/php/ruby/rust/kotlin 九语言内置生成器目录。除特别说明外，路径均相对 src/google/protobuf/compiler/。

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

版本常量来自主仓根 protobuf_version.bzl；版本基准 v37.0-dev（F-REPO-028、F-REPO-031）。源码根路径：external/libs/protocolbuffers/protobuf（本文件登记路径相对其下 src/google/protobuf/compiler/）。

## 核心模块与文件清单

### 编译器入口

- `main.cc` — protoc 主入口，注册 11 组生成器
- `main_no_generators.cc` — 无内置生成器的 protoc 变体

### 命令行框架

- `command_line_interface.h` — 命令行接口声明
- `command_line_interface.cc` — 参数解析与编译管线

### 解析与导入

- `parser.h` — proto 语法解析器声明
- `parser.cc` — proto 语法解析实现
- `importer.h` — Importer 与 SourceTree 体系

### 生成器抽象与插件协议

- `code_generator.h` — CodeGenerator 抽象接口
- `code_generator_lite.h` — 轻量生成器接口
- `plugin.h` — 插件协议支持声明
- `plugin.cc` — 插件协议实现
- `plugin.proto` — CodeGeneratorRequest/Response 定义
- `plugin.pb.h` — plugin.proto 生成代码

### cpp/（C++ 生成器）

- `cpp/generator.h` — 生成器入口声明
- `cpp/cpp_generator.h` — C++ 生成器接口
- `cpp/file.h` — 文件级生成单元
- `cpp/helpers.h` — 生成辅助函数
- `cpp/options.h` — 生成选项定义
- `cpp/parse_function_generator.h` — 解析函数生成器
- `cpp/field.h` — 字段生成抽象
- `cpp/enum.h` — 枚举生成
- `cpp/extension.h` — 扩展生成
- `cpp/message.h` — 消息生成
- `cpp/service.h` — 服务生成
- `cpp/ifndef_guard.h` — include 守卫生成
- `cpp/namespace_printer.h` — 命名空间输出
- `cpp/message_layout_helper.h` — 消息布局辅助
- `cpp/tracker.h` — 生成过程追踪
- `cpp/field_generators/` — 字段生成器工厂子目录

### java/（Java 生成器）

- `java/generator.h` — 生成器入口声明
- `java/java_generator.h` — Java 生成器接口
- `java/generator.cc` — Java 生成器实现
- `java/shared_code_generator.h` — 共享代码生成
- `java/name_resolver.h` — 命名解析器
- `java/context.h` — 生成上下文
- `java/full/` — full 运行时变体生成
- `java/lite/` — lite 运行时变体生成

### python/（Python 生成器）

- `python/generator.h` — 生成器入口声明
- `python/python_generator.h` — Python 生成器接口
- `python/pyi_generator.h` — .pyi 类型存根生成器
- `python/plugin_main.cc` — 独立插件入口
- `python/names.h` — 命名工具
- `python/helpers.h` — 生成辅助函数

### csharp/（C# 生成器）

- `csharp/csharp_generator.h` — C# 生成器接口
- `csharp/csharp_helpers.h` — C# 生成辅助函数
- `csharp/csharp_field_base.h` — 字段生成基类
- （csharp/ 目录共 19 个 .h 文件，以上为代表性清单）

### 其他语言生成器

- `objectivec/generator.h` — Objective-C 生成器
- `php/php_generator.h` — PHP 生成器
- `ruby/ruby_generator.h` — Ruby 生成器
- `ruby/rbs_generator.h` — RBS 签名生成器
- `rust/generator.h` — Rust 生成器
- `rust/context.h` — Rust 生成上下文
- `kotlin/generator.h` — Kotlin 生成器

## 事实关联

| 事实区间 | 条数 | 事实清单文件 |
|---|---|---|
| F-CMP-001 ~ F-CMP-090 | 90 | facts-compiler.md |

事实清单文件为 R 阶段产出，位于 spec 目录 .trae/specs/protocolbuffers-okf-wiki/。本束 concepts/ 文档中所有 F-CMP 编号事实均以本信源登记的源码路径为出处。

## 相关概念

- /concepts/07-protoc-command-line.md — 含 F-CMP-001~020
- /concepts/08-parser-and-importer.md — 含 F-CMP-021~034
- /concepts/09-code-generators.md — 含 F-CMP-035~046、056~090
- /concepts/10-plugin-protocol.md — 含 F-CMP-008、016、047~055、078
- /concepts/15-editions-feature-system.md — 含 F-CMP-014、017、027、037、040~043、057、068、075、080、084~088、090
