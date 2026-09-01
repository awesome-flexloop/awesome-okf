---
type: Reference
title: "protobuf 多语言运行时信源登记"
description: "登记 protobuf 主仓 Python、Rust、hpb、Java、C#、Objective-C、PHP、Ruby、Lua 九大运行时源码路径，支撑 F-RT-001~105 事实。"
tags: [protobuf, multi-language-runtime, upb, bindings, hpb]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-source
    resource: external/libs/protocolbuffers/protobuf
    title: "protobuf 主仓库源码（v37.0-dev）"
---

本信源文件登记 protobuf 多语言运行时的源码路径，是 R 阶段事实清单 facts-runtimes.md（F-RT-001~105，共 105 条事实）的信源登记表。protobuf 束 concepts/ 中凡引用 F-RT 编号事实的文档，其 frontmatter 的 sources 字段均应指向本文件。

登记范围覆盖 python/、rust/、hpb/、hpb_generator/、java/、csharp/、objectivec/、php/、ruby/、lua/ 十个语言运行时目录，对应"双内核架构"（C++ 全功能内核与 upb 轻量 C 内核）之上的多语言绑定。除特别说明外，路径均相对 protobuf 主仓根。

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

版本常量来自主仓根 protobuf_version.bzl（各语言运行时版本与 PROTOC_VERSION 同源对齐）；版本基准 v37.0-dev（F-REPO-028、F-REPO-031）。源码根路径：external/libs/protocolbuffers/protobuf。

## 核心模块与文件清单

### python/（Python 运行时，upb C 扩展）

- `python/protobuf.c` — C 扩展模块入口
- `python/protobuf.h` — 模块头文件
- `python/descriptor.c/.h` — descriptor 绑定
- `python/descriptor_pool.c/.h` — DescriptorPool 绑定
- `python/descriptor_containers.c/.h` — descriptor 容器绑定
- `python/message.c/.h` — Message 绑定
- `python/map.c/.h` — Map 容器绑定
- `python/repeated.c/.h` — Repeated 容器绑定
- `python/unknown_fields.c/.h` — 未知字段绑定
- `python/convert.c/.h` — 值转换绑定
- `python/buffer_convert.c/.h` — 缓冲区转换绑定
- `python/extension_dict.c/.h` — 扩展字典绑定
- `python/python_api.h` — 公开 C API 头文件
- `python/version_script.lds` — 符号导出脚本
- `python/internal.bzl` — 内部构建规则
- `python/build_targets.bzl` — 构建目标定义
- `python/dist/setup.py` — PyPI 发行构建脚本
- `python/requirements.txt` — Python 依赖清单
- `python/google/protobuf/__init__.py` — 包初始化入口
- `python/google/__init__.py` — google 包初始化文件
- `python/dist/` — 发行版子目录

### rust/（Rust 双 kernel 运行时）

- `rust/protobuf.rs` — 全功能运行时入口
- `rust/protobuf_lite.rs` — 双 kernel 编译开关
- `rust/proxied.rs` — Proxied 视图抽象
- `rust/singular.rs` — singular 字段视图
- `rust/repeated.rs` — Repeated 容器
- `rust/map.rs` — Map 容器
- `rust/enum.rs` — 枚举支持
- `rust/extension.rs` — 扩展支持
- `rust/codegen_traits.rs` — 代码生成 trait
- `rust/string.rs` — 字符串类型
- `rust/primitive.rs` — 标量类型
- `rust/shared.rs` — 共享定义
- `rust/prelude.rs` — prelude 导出
- `rust/internal.rs` — 内部实现
- `rust/cord.rs` — Cord 字符串支持
- `rust/defs.bzl` — rust_proto_library 规则
- `rust/dist.bzl` — 发布规则
- `rust/rules.bzl` — 构建规则
- `rust/upb/lib.rs` — upb Rust 绑定入口
- `rust/upb/arena.rs` — Arena 绑定
- `rust/upb/message.rs` — Message 绑定
- `rust/upb/wire.rs` — wire 层绑定
- `rust/upb/sys/lib.rs` — upb C API 转导出
- `rust/upb/sys/upb_api.c` — C API 封装实现
- `rust/upb_kernel/` — upb kernel 变体
- `rust/cpp_kernel/` — cpp kernel 变体
- `rust/release_crates/` — 发布 crate 集合
- `rust/test/` — 测试目录

### hpb/（C++ 多后端 API 层）

- `hpb/hpb.h` — hpb 主头文件
- `hpb/arena.h` — Arena 接口
- `hpb/multibackend.h` — 后端编译期选择
- `hpb/ptr.h` — Ptr 代理
- `hpb/repeated_field.h` — RepeatedField 代理
- `hpb/extension.h/.cc` — 扩展访问
- `hpb/status.h/.cc` — Status 错误类型
- `hpb/options.h` — 选项定义
- `hpb/requires.h` — requires 工具
- `hpb/backend/cpp/` — C++ 后端实现
- `hpb/backend/upb/` — upb 后端实现
- `hpb/internal/` — 内部实现
- `hpb/bazel/hpb_proto_library.bzl` — hpb 构建规则

### hpb_generator/（hpb 代码生成器，protoc 插件）

- `hpb_generator/generator.h/.cc` — 生成器实现
- `hpb_generator/protoc-gen-hpb.cc` — 插件入口
- `hpb_generator/context.h` — 生成上下文
- `hpb_generator/gen_accessors.h/.cc` — accessor 生成
- `hpb_generator/gen_enums.h/.cc` — 枚举生成
- `hpb_generator/gen_extensions.h/.cc` — 扩展生成
- `hpb_generator/gen_messages.h/.cc` — 消息生成
- `hpb_generator/gen_repeated_fields.h/.cc` — repeated 字段生成
- `hpb_generator/gen_utils.h/.cc` — 生成工具
- `hpb_generator/keywords.h/.cc` — 关键字处理
- `hpb_generator/names.h/.cc` — 命名工具
- `hpb_generator/tests/` — 测试目录

### java/（Java 运行时）

- `java/BUILD.bazel` — Java 构建定义
- `java/lite.md` — lite 运行时说明文档
- `java/core/` — core 运行时子目录
- `java/lite/` — lite 运行时子目录
- `java/kotlin/` — Kotlin 运行时子目录
- `java/kotlin-lite/` — Kotlin lite 子目录
- `java/util/` — util 工具子目录
- `java/protoc/` — protoc 相关子目录

### csharp/（C# 运行时）

- `csharp/src/Google.Protobuf/` — 运行时源码文件清单
- `csharp/src/Google.Protobuf/Reflection/` — 反射子目录
- `csharp/src/Google.Protobuf/WellKnownTypes/` — WKT 子目录
- `csharp/keys/` — 签名密钥目录
- `csharp/protos/` — proto 文件目录

### objectivec/（Objective-C 运行时）

- `objectivec/GPBMessage.h` — 消息基类
- `objectivec/GPBDescriptor.h` — descriptor 体系
- `objectivec/GPBArray.h` — 数组容器
- `objectivec/GPBDictionary.h` — 字典容器
- `objectivec/GPBWireFormat.h` — wire 格式
- `objectivec/GPBRootObject.h` — 根对象
- `objectivec/GPBCodedInputStream.h` — 输入流
- `objectivec/GPBCodedOutputStream.h` — 输出流
- `objectivec/GPBExtensionRegistry.h` — 扩展注册表
- `objectivec/GPBUnknownFields.h` — 未知字段
- `objectivec/GPB*.pbobjc.h` — 生成代码文件
- `objectivec/DevTools/` — 开发工具子目录

### php/（PHP 运行时）

- `php/composer.json` — Composer 包定义
- `php/ext/google/protobuf/php-upb.c/.h` — upb 内核绑定
- `php/ext/google/protobuf/arena.c` — Arena 实现
- `php/ext/google/protobuf/array.c` — 数组容器实现
- `php/ext/google/protobuf/map.c` — Map 容器实现
- `php/ext/google/protobuf/message.c` — Message 实现
- `php/ext/google/protobuf/def.c` — descriptor 定义
- `php/ext/google/protobuf/convert.c` — 值转换
- `php/ext/google/protobuf/names.c` — 命名工具
- `php/ext/google/protobuf/config.m4` — Unix 构建配置
- `php/ext/google/protobuf/config.w32` — Windows 构建配置
- `php/ext/google/protobuf/wkt.inc` — WKT 数据
- `php/src/Google/Protobuf/` — 纯 PHP 实现
- `php/tests/` — 测试目录

### ruby/（Ruby 运行时）

- `ruby/lib/google/protobuf.rb` — Ruby 入口
- `ruby/lib/google/protobuf_ffi.rb` — FFI 实现
- `ruby/lib/google/protobuf_native.rb` — C 扩展实现
- `ruby/lib/google/ffi/` — FFI 子目录
- `ruby/ext/google/protobuf_c/ruby-upb.c/.h` — upb 内核
- `ruby/ext/google/protobuf_c/defs.c` — descriptor 定义
- `ruby/ext/google/protobuf_c/message.c` — Message 实现
- `ruby/ext/google/protobuf_c/map.c` — Map 实现
- `ruby/ext/google/protobuf_c/repeated_field.c` — Repeated 实现
- `ruby/ext/google/protobuf_c/convert.c` — 值转换
- `ruby/ext/google/protobuf_c/glue.c` — 胶水层
- `ruby/tests/` — 测试目录
- `ruby/defs.bzl` — 构建规则

### lua/（Lua 运行时）

- `lua/upb.c` — C 绑定实现
- `lua/upb.h` — C 绑定头文件
- `lua/upbc.cc` — Lua 代码生成器
- `lua/upb.lua` — Lua API
- `lua/def.c` — descriptor 绑定
- `lua/msg.c` — Message 绑定
- `lua/main.c` — 模块入口
- `lua/test_upb.lua` — 测试脚本
- `lua/test.proto` — 测试 proto
- `lua/lua_proto_library.bzl` — 构建规则

## 事实关联

| 事实区间 | 条数 | 事实清单文件 |
|---|---|---|
| F-RT-001 ~ F-RT-105 | 105 | facts-runtimes.md |

事实清单文件为 R 阶段产出，位于 spec 目录 .trae/specs/protocolbuffers-okf-wiki/。本束 concepts/ 文档中所有 F-RT 编号事实均以本信源登记的源码路径为出处。

## 相关概念

- /concepts/01-message-model.md — 含 F-RT-079、082
- /concepts/02-wire-format.md — 含 F-RT-086
- /concepts/03-descriptors-and-reflection.md — 含 F-RT-010~014、083
- /concepts/04-arena-memory-management.md — 含 F-RT-007、034、036、057
- /concepts/05-containers-extensions-unknown-fields.md — 含 F-RT-016~019、046~048、084、085
- /concepts/06-text-format-and-json.md — 含 F-RT-094、102
- /concepts/10-plugin-protocol.md — 含 F-RT-065~069、104
- /concepts/11-python-runtime.md — 含 F-RT-001~030
- /concepts/12-upb-and-rust-runtime.md — 含 F-RT-031~054
- /concepts/13-hpb.md — 含 F-RT-055~070
- /concepts/14-other-language-runtimes.md — 含 F-RT-071~105
