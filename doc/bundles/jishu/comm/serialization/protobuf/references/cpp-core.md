---
type: Reference
title: "protobuf C++ 运行时核心信源登记"
description: "登记 src/google/protobuf/ 下 C++ 运行时核心源码路径，覆盖消息模型、descriptor、wire format、IO 流、JSON 与 WKT，支撑 F-CPP-001~144。"
tags: [protobuf, cpp-runtime, descriptors, wire-format, wkt]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-source
    resource: external/libs/protocolbuffers/protobuf
    title: "protobuf 主仓库源码（v37.0-dev）"
---

本信源文件登记 protobuf C++ 运行时核心的源码路径，是 R 阶段事实清单 facts-cpp-core.md（F-CPP-001~144，共 144 条事实）的信源登记表。protobuf 束 concepts/ 中凡引用 F-CPP 编号事实的文档，其 frontmatter 的 sources 字段均应指向本文件。

登记范围覆盖 src/google/protobuf/ 下的消息模型与 Arena 内存管理、descriptor 体系与运行时反射、wire format 编解码、IO 流抽象、文本格式与 JSON 序列化、容器/扩展/未知字段、生成侧类型信息与特性解析，以及 Well-Known Types（WKT）全家桶文件。除特别说明外，路径均相对 src/google/protobuf/。

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

版本常量来自主仓根 protobuf_version.bzl；版本基准 v37.0-dev（F-REPO-028、F-REPO-031）。源码根路径：external/libs/protocolbuffers/protobuf（本文件登记路径相对其下 src/google/protobuf/）。

## 核心模块与文件清单

### 消息与内存基础

- `message_lite.h` — MessageLite 轻量消息基类
- `message.h` — class Message 与 Reflection 定义
- `arena.h` — Arena 内存分配器
- `arenastring.h` — Arena 字符串支持

### descriptor 体系

- `descriptor.h` — Descriptor 家族与 DescriptorPool
- `descriptor.pb.h` — descriptor.proto 生成代码
- `descriptor.proto` — schema 元数据定义
- `descriptor_database.h` — DescriptorDatabase 抽象
- `descriptor_lite.h` — 轻量 descriptor 定义

### wire format

- `wire_format_lite.h` — WireFormatLite 静态工具
- `wire_format.h` — WireFormat 静态工具

### IO 流

- `io/coded_stream.h` — CodedInputStream/OutputStream
- `io/zero_copy_stream.h` — ZeroCopy 流抽象
- `io/zero_copy_stream_impl_lite.h` — ZeroCopy 流轻量实现

### 文本格式与 JSON

- `text_format.h` — TextFormat Printer/Parser
- `json/` — json.cc/json.h 与 internal/ 子目录
- `util/json_util.h` — JSON 转换工具入口

### 容器、扩展与未知字段

- `map.h` — Map 容器
- `repeated_field.h` — RepeatedField 容器
- `repeated_ptr_field.h` — RepeatedPtrField 容器
- `unknown_field_set.h` — UnknownFieldSet 未知字段
- `extension_set.h` — ExtensionSet 扩展

### 生成侧类型信息与特性解析

- `class_data.h` — ClassData 类型信息
- `generated_message_reflection.h` — 生成消息反射支持
- `feature_resolver.h` — FeatureSet 特性解析器
- `port_def.inc` — 平台移植性宏定义

### WKT（Well-Known Types）文件

- `any.proto` — Any 消息定义
- `any.h` — Any C++ 支持
- `duration.proto` — Duration 定义
- `timestamp.proto` — Timestamp 定义
- `struct.proto` — Struct 定义
- `wrappers.proto` — Wrapper 类型定义
- `type.proto` — Type 体系定义
- `api.proto` — Api 定义
- `source_context.proto` — SourceContext 定义
- `field_mask.proto` — FieldMask 定义
- `empty.proto` — Empty 定义
- `cpp_features.proto` — C++ 特性扩展定义
- `any_test.proto` — Any 测试用 proto

## 事实关联

| 事实区间 | 条数 | 事实清单文件 |
|---|---|---|
| F-CPP-001 ~ F-CPP-144 | 144 | facts-cpp-core.md |

事实清单文件为 R 阶段产出，位于 spec 目录 .trae/specs/protocolbuffers-okf-wiki/。本束 concepts/ 文档中所有 F-CPP 编号事实均以本信源登记的源码路径为出处。

## 相关概念

- /concepts/01-message-model.md — 含 F-CPP-001~012、119~125、141、144
- /concepts/02-wire-format.md — 含 F-CPP-075~093
- /concepts/03-descriptors-and-reflection.md — 含 F-CPP-013~035、042~054、057~062、066、069~074
- /concepts/04-arena-memory-management.md — 含 F-CPP-036~041
- /concepts/05-containers-extensions-unknown-fields.md — 含 F-CPP-100~118、142、143
- /concepts/06-text-format-and-json.md — 含 F-CPP-094~099
- /concepts/15-editions-feature-system.md — 含 F-CPP-055、056、063~068、138、139
- /concepts/16-wkt-conformance-benchmarks.md — 含 F-CPP-126~137
