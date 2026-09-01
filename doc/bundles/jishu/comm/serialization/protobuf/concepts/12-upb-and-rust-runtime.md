---
type: Concept
title: "upb 内核与 Rust 双 kernel 运行时"
description: "upb C 内核的 17 子目录结构、Rust protobuf_lite.rs 的 kernel 编译开关、upb_kernel/cpp_kernel 平行实现与 Proxied trait 体系，及 use_upb_kernel 构建规则与 8 个 release crates。"
tags: [protobuf, upb, rust]
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

protobuf 的"多语言"实为"多绑定"：同一份 proto schema 可由 C++ 全功能内核或 upb 轻量 C 内核执行。Python（见 [Python 运行时（upb C 扩展）](/concepts/11-python-runtime.md)）、PHP、Ruby、Lua 通过 C FFI 内嵌 upb；Rust 则把"双内核"做成一等公民——`protobuf_lite.rs` 按编译开关选择 `use protobuf_cpp as kernel;` 或 `use protobuf_upb as kernel;`（F-RT-033）。本篇是"双运行时内核"洞察的主证据文档：先看 upb C 内核的结构，再解析 Rust 的双 kernel 体系与构建规则。

## upb C 内核结构

upb/ 下含 17 个子目录：base、bazel、cmake、conformance、hash、json、lex、mem、message、mini_descriptor、mini_table、port、reflection、test、text、util、wire，与 BUILD、generated_code_support.h、README.md（F-REPO-019）。核心分层清晰：mem（Arena 内存）、message（消息/数组/Map 数据结构）、mini_descriptor/mini_table（轻量描述符与表驱动访问）、reflection（反射）、wire（编解码）、text/json（文本与 JSON）、hash（哈希表）。

upb_generator/ 下含 c、cmake、common、minitable、reflection、stage0 子目录与 bootstrap_compiler.bzl、BUILD、common.cc/h、file_layout.cc/h、plugin.cc/h、plugin_bootstrap.h（F-REPO-020）——upb 自己的代码生成器，其中 stage0 与 bootstrap_compiler.bzl 支撑自举（bootstrap）编译。

Rust 侧访问 upb C API 的聚合入口是 upb_api.c（F-RT-039）：全文 26 行，`#define UPB_BUILD_API` 加 11 个 IWYU keep 头包含（`upb/mem/arena.h`、`upb/message/accessors.h`、`upb/message/array.h`、`upb/message/compare.h`、`upb/message/copy.h`、`upb/message/map.h`、`upb/message/merge.h`、`upb/mini_descriptor/decode.h`、`upb/mini_table/message.h`、`upb/text/debug_string.h`、`upb/wire/byte_size.h`）。

## Rust 运行时顶层与 kernel 编译开关

rust/ 顶层含 protobuf.rs、protobuf_lite.rs、proxied.rs、singular.rs、repeated.rs、map.rs、enum.rs、extension.rs、codegen_traits.rs、string.rs、primitive.rs、shared.rs、prelude.rs、internal.rs、cord.rs 等源文件，bzl 文件 defs.bzl、dist.bzl、rules.bzl，及子目录 upb/、upb_kernel/、cpp_kernel/、protobuf_macros/、release_crates/、test/、bazel/（F-RT-031、F-REPO-013）。

`protobuf.rs` 全部实质内容为 `pub use protobuf_lite::*;`（doc 注释标注 "Rust Protobuf Full Runtime"，声明将增加 reflection traits 与 heavy APIs）（F-RT-032）。而 `protobuf_lite.rs` 是双内核的分岔点（F-RT-033）：

```rust
use protobuf_cpp as kernel;  // L19
// 或
use protobuf_upb as kernel;  // L22
// ...
pub use kernel::*;
```

文档注释说明该文件为单一 `protobuf` crate 名的公开入口——上层 API 完全不感知内核差异，编译开关一次性切换整个实现。

## upb 绑定层

`rust/upb/lib.rs` 模块（F-RT-034）：`mod arena`（`pub use arena::Arena`）、`mod associated_mini_table`（导出 AssociatedMiniTable、AssociatedMiniTableEnum）、`mod text`（导出 debug_string）、`mod message`（导出 MessagePtr）、`mod owned_arena_box`（导出 OwnedArenaBox）、`pub mod wire`；sys 在 Bazel 构建时为外部 crate（`extern crate sys`），Cargo 构建时映射 sys/lib.rs。

该文件转导出 sys 层 C API（标注 "intended to be burned down"，即计划逐步烧除换为安全封装）（F-RT-035）：`upb_Array_Append/DataPtr/Get/GetMutable/MutableDataPtr/New/Reserve/Resize/Set/Size`、`upb_Map_Clear/Delete/Get/GetMutable/Insert/Next/Size`、`upb_Message_ClearExtension/DeepClone/DeepCopy/GetExtension*(Bool/Double/Float/Int32/Int64/Message/MutableArray/String/UInt32/UInt64)/GetMap/GetOrCreateMutableMap/HasExtension/IsEqual/MergeFrom/SetBaseField/SetExtension*/WhichOneofFieldNumber`、`upb_MiniTable*_Build/Link`、`upb_ExtensionRegistry_Add/New`、`upb_Arena`、`upb_MessageValue`、`CType`、`StringView`。

类型层（F-RT-036）：`arena.rs` 定义 `pub struct Arena`；`message.rs` 定义 `pub struct MessagePtr<T>`；`wire.rs` 定义 `pub fn encode<T: AssociatedMiniTable>(msg: MessagePtr<T>) -> Result<Vec<u8>, EncodeStatus>` 与 `pub fn byte_size<T: AssociatedMiniTable>(msg: MessagePtr<T>) -> usize`（Arena 语义见 [Arena 内存管理](/concepts/04-arena-memory-management.md)）。

sys 层结构（F-RT-037/038）：`rust/upb/sys/lib.rs` 模块清单为 `pub mod base`、`mem`、`message`、`mini_table`、`opaque_pointee`、`text`、`wire`；目录含 base/（ctype.rs、string_view.rs）、mem/（arena.rs）、message/（array.rs、map.rs、message.rs、message_value.rs）、mini_table/（extension_registry.rs、mini_table.rs）、text/（text.rs）、wire/（wire.rs）、opaque_pointee.rs、upb_api.c。错误枚举（F-RT-040）：`sys/wire/wire.rs` 定义 `pub enum EncodeStatus` 与 `pub enum DecodeStatus`；`sys/message/map.rs` 定义 `pub enum MapInsertStatus`。

## 双 kernel 平行实现

kernel 无关的抽象层之下，upb 与 cpp 两个内核各有一套平行实现：

- upb_kernel/（F-RT-041/042）：文件 conversions.rs、extension.rs、interop.rs、map.rs、message.rs、minitable.rs、repeated.rs、string.rs、mod.rs；mod.rs 将上述模块全部 `pub mod` 并 `pub use *`，导出 `debug_string<T: UpbGetMessagePtr>` 函数、`MapKey` trait、`MiniTablePtr`/`MiniTableEnumPtr`/`MiniTableExtensionPtr`/`ExtensionRegistryPtr` 类型别名、`THREAD_LOCAL_ARENA`（`ManuallyDrop<Arena>`）、`pub mod __unstable`（含 `DescriptorInfo` 结构体）。map.rs 定义 `InnerMap`、`InnerMapMut<'msg>`、`RawMapIter`；repeated.rs 定义 `InnerRepeated`、`InnerRepeatedMut<'msg>`；string.rs 定义 `InnerProtoString(OwnedArenaBox<[u8]>)`；extension.rs 定义 `InnerExtensionId`。
- cpp_kernel/（F-RT-043/044）：文件 mod.rs、extension.rs/.cc、interop.rs、map.rs/.cc、message.rs/.cc、raw.rs、repeated.rs/.cc、string.rs、strings.cc/.h、compare.cc/.h、debug.cc/.h、serialized_data.h、rust_alloc_for_cpp_api.h/.rs。cpp_kernel/map.rs 定义 `MapKey` trait、`InnerMap`、`InnerMapMut<'msg>`、`UntypedMapIterator`、`FfiMapValueTag` 枚举、`FfiMapValue`、`CppMapTypeConversions` trait、`FfiMapKey` trait；repeated.rs 定义 `InnerRepeated`、`InnerRepeatedMut<'msg>`、`CppTypeConversions` trait。

InnerMap/InnerRepeated 在两个 kernel 中同名平行存在——上层 Repeated/Map 容器（见 [容器、扩展与未知字段](/concepts/05-containers-extensions-unknown-fields.md)）按 kernel 选择实例化其一。

## Proxied trait 体系

kernel 之上的类型抽象层由一组 trait 构成：

- proxied.rs（F-RT-045）：`Proxied`（L54）、`MutProxied`（L67）、`AsView`（L93）、`IntoView<'msg>`（L139）、`AsMut`（L192）、`IntoMut<'msg>`（L210）、`IntoProxied<T>`（L256）——"视图（view）/可变视图（mut）"分离的所有权模型；
- singular.rs/repeated.rs（F-RT-046）：`pub unsafe trait Singular: Proxied + SealedInternal`；`Repeated<T: Singular>`、`RepeatedView<'msg, T>`、`RepeatedMut<'msg, T>`、`RepeatedIter<'msg, T>`、`RepeatedMutIter<'msg, T>`；
- map.rs（F-RT-047）：`MapValue` trait、`Map<K: MapKey, V: MapValue>`、`MapView<'msg, K, V>`、`MapMut<'msg, K, V>`、`MapIter<'msg, K, V>`；
- enum.rs/extension.rs（F-RT-048）：`pub unsafe trait Enum` 与 `pub struct UnknownEnumValue<T>(i32, PhantomData<T>)`；`ExtensionId<Extendee, T: Proxied>` 及 trait `ExtHas`、`ExtClear`、`ExtAccess`、`ExtGetMut`；
- codegen_traits.rs（F-RT-049）：trait `MessageType`、`Message`、`MessageView<'msg>`、`MessageMut<'msg>`、`EntityType`——生成代码实现的运行时接口；
- string.rs/shared.rs（F-RT-050）：`ProtoBytes`、`Utf8Error`、`ProtoString`、`ProtoStr([u8])`；`ParseError` 与 `SerializeError`。

## 构建规则与发布

`rust/defs.bzl` 定义 `rust_proto_library(name, deps, **args)` 宏（F-RT-051）：校验 name 以 `_rust_proto` 结尾，创建 `native.alias` 在 `//rust:use_upb_kernel` 条件下指向 `name_upb_rust_proto`、否则 `name_cpp_rust_proto`；导出 `ProtoCrateNamesInfo`、`rust_upb_proto_library`、`rust_cc_proto_library`——这是"双内核编译开关"在 Bazel 侧的落点。dist.bzl 定义 `pkg_cross_compiled_binaries(name, cpus, targets, prefix, tags, visibility)` 与内部 `_cpu_transition`/`_cross_compiled_binary` 规则（F-RT-052）。

测试资产（F-RT-053、F-REPO-015）：rust/test/ 含 proto 文件 bad_names.proto、edition2023.proto、unittest.proto、unittest_proto3.proto、map_unittest.proto、dots_in_package.proto、same_name_direct_deps.proto、no_package.proto 等，及子目录 cpp/、upb/、shared/、p/、q/、more_test_protos/、treeshaking/、encode_raw_string_as_crate_name/、rust_proto_library_unit_test/——cpp/ 与 upb/ 子目录再次印证双内核平行测试。

发布（F-RT-054、F-REPO-014）：rust/release_crates/ 含 `google_protobuf`、`google_protobuf_codegen`、`protobuf`、`protobuf_codegen`、`protobuf_example`、`protobuf_macros`、`protobuf_tests`、`protobuf_well_known_types` 八个 crate 目录，及 Cargo.toml、cargo_test.sh、substitute_rust_release_version.bzl。版本基准：PROTOBUF_RUST_VERSION = "0.37.0"（见 [仓库总览与双构建系统](/concepts/00-repo-overview-and-build-systems.md)）。

## 相关概念

- [Python 运行时（upb C 扩展）](/concepts/11-python-runtime.md) —— upb 内核的 Python 绑定
- [hpb：C++ 多后端 API 层与 hpb_generator](/concepts/13-hpb.md) —— C++ 侧的多后端选择
- [其他语言运行时概览](/concepts/14-other-language-runtimes.md) —— 内嵌 upb 的 PHP/Ruby/Lua 绑定
- [Arena 内存管理](/concepts/04-arena-memory-management.md) —— upb::Arena 与 THREAD_LOCAL_ARENA
