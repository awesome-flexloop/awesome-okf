---
type: Concept
title: "hpb：C++ 多后端 API 层与 hpb_generator"
description: "hpb 的 CreateMessage/Parse/Serialize 模板 API、multibackend.h 编译期后端选择（upb=1/cpp=2）、双后端实现与 Ptr 代理技巧，及 hpb_generator 插件的生成流程与注解。"
tags: [protobuf, hpb, cpp]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: runtimes
    resource: /references/runtimes.md
    title: "protobuf 多语言运行时信源"
  - id: repo-structure
    resource: /references/repo-structure.md
    title: "protobuf 仓库结构与构建系统信源"
---

hpb 是 C++ 的多后端（multibackend）API 层：同一套模板 API 在编译期按 `HPB_INTERNAL_BACKEND` 宏选择 upb 轻量内核或 C++ 全功能内核（F-RT-059），配合 hpb_generator 代码生成器（以 protoc 插件身份实现）形成完整的开发闭环。它是"双运行时内核"洞察在 C++ 侧的体现——与 Rust 的 kernel 编译开关（见 [upb 内核与 Rust 双 kernel 运行时](/concepts/12-upb-and-rust-runtime.md)）互为印证。本篇从模板 API 讲到后端选择、代理技巧、错误体系与生成器。

## hpb 顶层结构

hpb/ 顶层文件：hpb.h、arena.h、status.h、status.cc、status_test.cc、multibackend.h、ptr.h、repeated_field.h、extension.h、extension.cc、options.h、requires.h；子目录 backend/（cpp/、upb/、types.h）、bazel/（hpb_proto_library.bzl）、internal/（F-RT-055、F-REPO-017）。

## 模板 API：CreateMessage/Parse/Serialize

hpb.h（namespace hpb）模板函数（F-RT-056）：`CreateMessage<T>(Arena&)`、`CloneMessage<T>(Ptr<T>, Arena&)`、`DeepCopy`（3 个重载）、`ClearMessage<T>`、`Parse<T>(absl::string_view, ParseOptions)` 返回 `hpb::StatusOr<T>`、`Parse(internal::PtrOrRaw<T>, bytes, ExtensionRegistry&)`、`Serialize<T>` 返回 `absl::StatusOr<absl::string_view>`；按 `HPB_INTERNAL_BACKEND` 包含 `hpb/backend/upb/upb.h` 或 `hpb/backend/cpp/cpp.h`——每个 API 调用都在编译期绑定到选定后端。

Arena 适配（F-RT-057）：`class Arena` 构造 `Arena()`、`Arena(char* initial_block, size_t size)`、`explicit Arena(size_t size_hint)`；upb 后端下提供 `Fuse(Arena&)`、`IsFused(Arena&)`、`RefArena(const Arena&)`；内部成员 `backend::Arena arena_`，`friend struct hpb::internal::PrivateAccess`（Arena 融合语义见 [Arena 内存管理](/concepts/04-arena-memory-management.md)）。

扩展访问（F-RT-062）：`class ExtensionRegistry`（extension.h L38）及模板函数组 GetExtension/SetExtension/HasExtension/ClearExtension（L98-192 区间的 8 个模板签名，含 `DeductionBarrier` 形参的写法——用于阻止模板参数推导的隔离类型）。

## multibackend.h：编译期后端选择

multibackend.h 定义（F-RT-059）：

```cpp
#define HPB_INTERNAL_BACKEND_UPB 1
#define HPB_INTERNAL_BACKEND_CPP 2
```

并按 `HPB_INTERNAL_BACKEND` 将 `namespace backend` 别名到 `hpb::internal::backend::upb` 或 `::cpp`——此后全库所有 `backend::` 引用自动解析到选定实现。这是纯编译期机制：一个二进制只含一个后端，切换后端需要重新编译。

双后端实现目录（F-RT-063）：

- hpb/backend/cpp/：cpp.h、cpp_test.cc、error.h、interop.h、repeated_field.h（定义空类 RepeatedFieldScalarProxy、RepeatedFieldStringProxy、RepeatedFieldProxy）；
- hpb/backend/upb/：upb.h、error.h、extension.h/.cc、interop.h、interop_test.cc、repeated_field.h、repeated_field_iterator.h、repeated_field_iterator_test.cc。

hpb/internal/ 另含 internal.h、message_lock.h/.cc、message_lock_test.cc、template_help.h、template_help_test.cc、os_macros_restore.inc、os_macros_undef.inc（F-RT-064）。

## Ptr/RepeatedField 的 Proxy conditional_t 技巧

多后端类型差异用 `std::conditional_t` 在类型别名层抹平（F-RT-060/061）：

- ptr.h：`template <typename T> using Proxy = std::conditional_t<...>`（L17）与 `class Ptr final`（L27，含 `friend class Ptr<const T>`）；
- repeated_field.h：`template <typename T> class RepeatedField` 内含类型别名 `Proxy`、`CProxy`、`ValueProxy`、`ValueCProxy`、`Access`（均为 `std::conditional_t`）。

即"同一逻辑类型，按后端条件展开为不同物理类型"——与 Rust 侧 `pub use kernel::*;` 的转导出是同一思想的两语言实现。

## StatusOr/SourceLocation 错误体系

status.h 定义（F-RT-058）：

```cpp
struct SourceLocation {  // current()/file_name()/line()
};
MessageEncodeError(upb_EncodeStatus, SourceLocation);
MessageAllocationError;
ExtensionNotFoundError(uint32_t, SourceLocation);
MessageDecodeError(upb_DecodeStatus, SourceLocation);

template <typename T> class StatusOr {
  std::variant<T, internal::backend::Error> value_;
  // ok() / value() / error() / ToAbslStatusOr()
};
```

注意错误类型绑定 `upb_EncodeStatus`/`upb_DecodeStatus`——错误模型以 upb 状态码为基底，StatusOr 可经 `ToAbslStatusOr()` 转入 absl 生态。

## hpb_generator：以插件身份实现

hpb_generator/ 目录（F-RT-065、F-REPO-018）含 generator.h/.cc、protoc-gen-hpb.cc、context.h、gen_accessors.h/.cc、gen_enums.h/.cc、gen_extensions.h/.cc、gen_messages.h/.cc、gen_repeated_fields.h/.cc、gen_utils.h/.cc、keywords.h/.cc、names.h/.cc、README.md、tests/。生成流水线按构件拆分为五个模块：gen_accessors（访问器）、gen_enums（枚举）、gen_extensions（扩展）、gen_messages（消息）、gen_repeated_fields（repeated 字段），各自 .h/.cc 成对；keywords.h/.cc 处理 C++ 关键字冲突转义，names.h/.cc 承担命名解析，gen_utils.h/.cc 提供共享工具。插件入口是 protoc-gen-hpb.cc——按 "protoc-gen-" 前缀命名规则被 `--hpb_out` 发现（见 [插件协议（plugin.proto）](/concepts/10-plugin-protocol.md)）。

generator.h 在 `namespace google::protobuf::hpb_generator` 下声明 `class Generator : public protoc::CodeGenerator`（`namespace protoc = ::google::protobuf::compiler`，F-RT-066）——它不是 main.cc 里的内置注册项，而是标准 protoc 插件。context.h 定义 `struct Options` 与 `class Context final`（F-RT-067）承载生成上下文。

双后端的类型桥接另有关键一环：hpb/backend/ 下存在 types.h（F-RT-063），upb 侧的 repeated_field.h 配套 repeated_field_iterator.h（迭代器实现），cpp 侧的 repeated_field.h 则定义空类 RepeatedFieldScalarProxy、RepeatedFieldStringProxy、RepeatedFieldProxy（F-RT-063）——两后端以不同粒度提供同形接口。Bazel 侧入口 hpb/bazel/hpb_proto_library.bzl（F-RT-070），hpb/BUILD、hpb/backend/BUILD、hpb/internal/BUILD、hpb/bazel/BUILD 均存在。

注解生产（F-RT-068）：generator.cc 使用 `GeneratedCodeInfo` 与 `io::AnnotationProtoCollector<GeneratedCodeInfo>` 处理注解——生成的代码段与源 proto 字段的映射关系写入 CodeGeneratorResponse.File.generated_code_info。测试（F-RT-069、F-REPO-018）：hpb_generator/tests/ 含 basic_test_editions.proto、child_model.proto、test_model.proto、test_enum.proto、test_extension.proto、legacy-name.proto、naming_conflict.proto、no_package.proto、null_enum.proto、set_alias.proto，及 multibackend_test.cc、extension_test.cc、repeated_test.cc、metadata_test.cc、test_generated.cc 等——multibackend_test.cc 直接验证双后端行为一致性。

## 相关概念

- [upb 内核与 Rust 双 kernel 运行时](/concepts/12-upb-and-rust-runtime.md) —— 双内核洞察的 Rust 侧对应
- [插件协议（plugin.proto）](/concepts/10-plugin-protocol.md) —— hpb_generator 的通信协议
- [Python 运行时（upb C 扩展）](/concepts/11-python-runtime.md) —— upb 内核的另一绑定形态
- [Arena 内存管理](/concepts/04-arena-memory-management.md) —— Fuse/IsFused 的内存语义
