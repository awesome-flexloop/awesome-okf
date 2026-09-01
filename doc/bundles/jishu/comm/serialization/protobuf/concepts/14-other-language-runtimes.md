---
type: Concept
title: "其他语言运行时概览：Java/C#/ObjC/PHP/Ruby/Lua"
description: "以语言绑定与内核选择的二维视角综述 Java、C#、Objective-C、PHP、Ruby、Lua 六语言运行时的目录结构、核心类与构建规则。"
tags: [protobuf, multi-language-runtime, bindings]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
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

protobuf 主仓在 C++ 全功能内核与 upb 轻量 C 内核之外，还维护六个一等语言运行时：Java、C#、Objective-C、PHP、Ruby 与 Lua（Python、Rust、hpb 分别见 /concepts/11-python-runtime.md、/concepts/12-upb-and-rust-runtime.md、/concepts/13-hpb.md）。这些运行时的实现路线并不相同：Java、C#、Objective-C 各自携带自研内核（分别基于 JVM、.NET 与 Objective-C 语言的完整独立实现），而 PHP、Ruby、Lua 则通过 C 扩展或 C API 直接内嵌 upb 内核——"同一份 schema、两个内核、多种绑定"的双内核架构（见 /concepts/12-upb-and-rust-runtime.md）在语言生态上得到完整投影。

本篇以"语言绑定 × 内核选择"二维表格组织六语言，再按 Java → C# → Objective-C → PHP → Ruby → Lua 逐一展开目录结构、核心 API 与构建入口。各语言版本常量来自主仓根 protobuf_version.bzl：PROTOBUF_JAVA_VERSION = "4.37.0"、PROTOBUF_PHP_VERSION = "5.37.0"、PROTOBUF_RUBY_VERSION = "4.37.0"（F-REPO-028）。

## "语言绑定 × 内核选择"总览

| 语言 | 主目录 | 内核选择 | 代码生成入口 |
|---|---|---|---|
| Java | java/ | 自研 JVM 内核（core 全功能 / lite 轻量双运行时） | `--java_out`、`--kotlin_out` |
| C# | csharp/src/Google.Protobuf | 自研 .NET 内核 | `--csharp_out` |
| Objective-C | objectivec/ | 自研 ObjC 内核（GPB 前缀全家桶） | `--objc_out` |
| PHP | php/ext/google/protobuf | upb C 内核（php-upb.c）+ 纯 PHP 前端 | `--php_out` |
| Ruby | ruby/ext/google/protobuf_c | upb C 内核（ruby-upb.c）与 FFI 双实现 | `--ruby_out`、`--rbs_out` |
| Lua | lua/ | upb C 内核（lupb 绑定） | protoc 插件 upbc.cc |

表格传达的关键判断：前三行为"自带内核"的独立实现路线，后三行为 upb 绑定路线。conformance 的 failure list 以 python/python_cpp/python_upb、php/php_c、rust_cc/rust_upb 等双实现分列（详见 /concepts/16-wkt-conformance-benchmarks.md），印证"同一语言多内核"是 protobuf 的常态设计而非例外。

## Java：core/lite 双运行时与 Maven 布局

java/ 下含 bom、core、internal、kotlin、kotlin-lite、lite、osgi、protoc、test、util 十个子目录，顶层为 BUILD.bazel、pom.xml、linkage_monitor.sh、lite.md 与 README.md（F-RT-071）。Java 是六语言中唯一同时提供"全功能与轻量"两套官方运行时的语言。

java/BUILD.bazel 定义三个聚合目标（F-RT-072）：`sh_test(name = "linkage_monitor", srcs = [":linkage_monitor.sh"], data = [":core", ":kotlin", ":kotlin-lite", ":lite", ":util", "//:protoc", ...], tags = ["manual"])`、`test_suite(name = "tests", tests = ["//java/core:tests", "//java/kotlin:tests", "//java/kotlin-lite:tests", "//java/lite:tests", "//java/util:tests"])` 与 `filegroup(name = "release", srcs = ["//java/core:release", "//java/kotlin:release", "//java/kotlin-lite:release", "//java/util:release"])`。

java/core/BUILD.bazel 的 srcs 全部位于 src/main/java/com/google/protobuf/ 之下，抽样包括 AbstractMessageLite.java、AbstractParser.java、AbstractProtobufList.java、ArrayDecoders.java、BooleanArrayList.java、ByteString.java、CodedInputStream.java、CodedOutputStream.java、DoubleArrayList.java、ExtensionRegistryLite.java、FieldInfo.java、FieldSet.java、GeneratedMessageLite.java、IntArrayList.java、Internal.java、InvalidProtocolBufferException.java 等（F-RT-073）——core 与 lite 共享同一套源码树，lite 版本由处理器脚本裁剪而来（java/lite/ 含 lite.awk、process-lite-sources-build.xml、proguard.pgcfg、generate-sources-build.xml，F-RT-074）。

lite.md 标题为 "The Protobuf Java Lite Runtime"，内含 Maven 依赖配置与 "R8 rule to make production app builds work" 章节（F-RT-075），面向 Android 等代码体积敏感环境。core、lite、kotlin、kotlin-lite、util 五个子目录均含 src/、BUILD.bazel 与 pom_template.xml（F-REPO-007），构成 Maven 多模块发布布局；java/protoc/ 仅含 pom.xml 与 README.md 两个文件（F-RT-076、F-REPO-008）。

## C#：Google.Protobuf 纯托管运行时

csharp/ 顶层含 src、keys、protos、google、compatibility_tests 五个子目录，以及 BUILD.bazel、buildall.bat、buildall.sh、build_packages.bat、build_release.sh、build_tools.sh、generate_protos.sh、Google.Protobuf.Tools.nuspec、Google.Protobuf.Tools.targets、NuGet.Config、CHANGES.txt、install_dotnet_sdk.ps1、README.md（F-RT-077）。

csharp/src/ 下含 AddressBook、Google.Protobuf、Google.Protobuf.Conformance、Google.Protobuf.JsonDump、Google.Protobuf.Test、Google.Protobuf.Test.TestProtos 六个子项目，加 Directory.Build.props 与 Google.Protobuf.sln（F-RT-078）。

运行时本体 Google.Protobuf 的源文件抽样（F-RT-079）：ByteString.cs、ByteStringAsync.cs、CodedInputStream.cs、CodedOutputStream.cs、CodedOutputStream.ComputeSize.cs、Extension.cs、ExtensionRegistry.cs、ExtensionSet.cs、FieldCodec.cs、FieldMaskTree.cs、IBufferMessage.cs、ICustomDiagnosticMessage.cs、IDeepCloneable.cs、IExtendableMessage.cs、IMessage.cs、InvalidProtocolBufferException.cs、JsonFormatter.cs、JsonParser.cs、JsonToken.cs、JsonTokenizer.cs、MessageExtensions.cs、MessageParser.cs、ParseContext.cs、UnknownField.cs、UnknownFieldSet.cs、UnsafeByteOperations.cs、WireFormat.cs，及 Collections/、Compatibility/、Compiler/、Properties/、Reflection/、WellKnownTypes/ 六个子目录——C# 自研内核同时覆盖 wire 层（CodedInputStream/CodedOutputStream/WireFormat.cs）、反射层（Reflection/）与 JSON 层（JsonFormatter/JsonParser）。

签名密钥位于 csharp/keys/（Google.Protobuf.snk、Google.Protobuf.public.snk），测试 proto 位于 csharp/protos/（unittest.proto、unittest_proto3.proto、nrt.proto、map_unittest_proto3.proto、old_extensions1.proto、unittest_issue6936_a/b/c.proto）（F-RT-080）。

## Objective-C：GPB 前缀全家桶

objectivec/ 下含 DevTools、Tests 子目录、三个 Xcode 工程（ProtocolBuffers_iOS.xcodeproj、ProtocolBuffers_OSX.xcodeproj、ProtocolBuffers_tvOS.xcodeproj）与 BUILD.bazel、defs.bzl、generate_well_known_types.sh（F-REPO-010）。运行时全部以 GPB 前缀命名（F-RT-081）：GPBMessage.h/.m、GPBDescriptor.h/.m、GPBArray.h/.m、GPBDictionary.h/.m、GPBWireFormat.h、GPBUtilities.h、GPBBootstrap.h、GPBRootObject.h/.m、GPBCodedInputStream.h/.m、GPBCodedOutputStream.h/.m、GPBExtensionRegistry.h/.m、GPBProtocolBuffers.h/.m，以及 WKT 生成文件（GPBAny.pbobjc.h/.m、GPBDuration.pbobjc.h/.m、GPBStruct.pbobjc.h/.m、GPBTimestamp.pbobjc.h/.m 等）。

消息基类的声明（F-RT-082）：

```objc
@interface GPBMessage : NSObject <NSSecureCoding, NSCopying>
```

前向声明 `@class GPBCodedInputStream;`、`@class GPBCodedOutputStream;`、`@class GPBUnknownFields;`。描述符体系在 GPBDescriptor.h 中成族出现（F-RT-083）：GPBDescriptor、GPBFileDescriptor、GPBOneofDescriptor、GPBFieldDescriptor、GPBEnumDescriptor、GPBExtensionDescriptor，均实现 `NSObject<NSCopying>`。

ObjC 运行时的特色是类型化容器（对应 /concepts/05-containers-extensions-unknown-fields.md 的跨语言对照）：GPBArray.h 声明 GPBInt32Array、GPBUInt32Array、GPBInt64Array、GPBUInt64Array、GPBFloatArray、GPBDoubleArray、GPBBoolArray、GPBEnumArray（均 `: NSObject <NSCopying>`，F-RT-084）；GPBDictionary.h 则声明完整的键值类型组合矩阵——GPBUInt32UInt32Dictionary、GPBUInt32Int32Dictionary、GPBUInt32UInt64Dictionary、GPBUInt32Int64Dictionary、GPBUInt32BoolDictionary、GPBUInt32FloatDictionary、GPBUInt32DoubleDictionary、GPBUInt32EnumDictionary、GPBUInt32ObjectDictionary<__covariant ObjectType>、GPBInt32UInt32Dictionary 等（F-RT-085）。

wire 层工具函数位于 GPBWireFormat.h（F-RT-086）：GPBWireFormatMakeTag、GPBWireFormatGetTagWireType、GPBWireFormatGetTagFieldNumber、GPBWireFormatIsValidTag、GPBWireFormatForType（均 `__attribute__((const))`）及 MessageSet 宏。根对象 `@interface GPBRootObject : NSObject` 承载扩展注册（F-RT-087）；DevTools/ 含 pddm.py、check_version_stamps.sh、compile_testing_protos.sh、full_mac_build.sh 等辅助脚本。

## PHP：upb 扩展与纯 PHP 前端

php/composer.json 声明包名 "google/protobuf"、`"require": {"php": ">=8.2.0"}`、require-dev phpunit >=11.5.50 <12.0.0，autoload psr-4 映射 `"Google\\Protobuf\\": "src/Google/Protobuf"` 与 `"GPBMetadata\\Google\\Protobuf\\": "src/GPBMetadata/Google/Protobuf"`；scripts 含 test_c、test_valgrind、test、aggregate_metadata_test（F-RT-088）。php/ 顶层另含 REFCOUNTING.md、release.sh、internal_generated_files.bzl、generate_descriptor_protos.sh、generate_test_protos.sh、update_reserved_words.sh（F-RT-092）。

C 扩展位于 php/ext/google/protobuf/（F-RT-090）：arena.c/.h、array.c/.h、config.m4、config.w32、convert.c/.h、def.c/.h、map.c/.h、message.c/.h、names.c/.h、php-upb.c/.h、php_protobuf.h、print_options.c/.h、protobuf.c/.h、template_package.xml、wkt.inc、generate_package_xml.sh 与 tests/。其中 php-upb.c/.h 直接内嵌 upb 内核——这是"PHP 运行时复用 upb 而非独立实现 wire format"的直接证据。

纯 PHP 前端 src/Google/Protobuf/ 提供描述符类与 WKT 类（F-RT-089）：Descriptor.php、DescriptorPool.php、EnumDescriptor.php、EnumValueDescriptor.php、FieldDescriptor.php、OneofDescriptor.php、RepeatedField.php，以及 Any.php、Api.php、Duration.php、FieldMask.php、GPBEmpty.php、Struct.php、Timestamp.php、Type.php、Value.php、ListValue.php 与九个 wrapper（BoolValue.php、BytesValue.php、DoubleValue.php、FloatValue.php、Int32Value.php、Int64Value.php、StringValue.php、UInt32Value.php、UInt64Value.php）。测试 php/tests/ 含 ArrayTest.php、DescriptorsTest.php、EncodeDecodeTest.php、GeneratedClassTest.php、MapFieldTest.php、PhpImplementationTest.php、WellKnownTest.php、WrapperTypeSettersTest.php、memory_leak_test.php、valgrind.supp 等（F-RT-091）。

## Ruby：C 扩展与 FFI 双实现

ruby/ 顶层含 Gemfile、Gemfile.lock、Rakefile、google-protobuf.gemspec、pom.xml、defs.bzl、generate_stubs.rb、BUILD.bazel、README.md、.yardopts 与 ext/、lib/、src/、tests/ 目录（F-RT-093）。

顶层 API 集中在 ruby/lib/google/protobuf.rb（F-RT-094）：

```ruby
def self.encode(msg, options = {})
def self.encode_json(msg, options = {})
def self.decode(klass, proto, options = {})
def self.decode_json(klass, json, options = {})
```

Ruby 是六语言中唯一同时维护两套实现的语言：lib/google/ 下含 protobuf_ffi.rb 与 protobuf_native.rb 两个加载入口，ffi/ 子目录含 ffi.rb、message.rb、map.rb、descriptor.rb、descriptor_pool.rb、enum_descriptor.rb、field_descriptor.rb、file_descriptor.rb、method_descriptor.rb、object_cache.rb、oneof_descriptor.rb、repeated_field.rb、service_descriptor.rb 及 internal/（arena.rb、convert.rb、pointer_helper.rb）（F-RT-095）。C 扩展位于 ruby/ext/google/protobuf_c/：convert.c/.h、defs.c/.h、glue.c、map.c/.h、message.c/.h、protobuf.c/.h、repeated_field.c/.h、ruby-upb.c/.h、shared_convert.c/.h、shared_message.c/.h、extconf.rb、Rakefile、BUILD.bazel（F-RT-096）——ruby-upb.c/.h 同样是内嵌 upb 内核的证据。构建规则 ruby/defs.bzl 仅定义一个函数 `def internal_ruby_proto_library(`（F-RT-098）。

测试（F-RT-097）覆盖 basic.rb、encode_decode_test.rb、generated_code_test.rb（配 generated_code.proto 与 generated_code_proto2_test.rb、basic_test_features.proto）、gc_test.rb、memory_test.rb、oom_test.rb、repeated_field_test.rb、service_test.rb、well_known_types_test.rb、utf8.rb、implementation.rb、ruby_version.rb。Ruby 入门用法见 /examples/04-java-ruby-dart-tutorials.md。

## Lua：lupb 绑定与 lua_proto_library

Lua 绑定 lupb 位于 lua/，文件清单：upb.c、upb.h、upbc.cc、upb.lua、def.c、msg.c、main.c、test_upb.lua、test.proto、lua_proto_library.bzl、BUILD.bazel、README.md（F-RT-099、F-REPO-016）。

模块入口（F-RT-100）：

```c
int luaopen_lupb(lua_State* L)
```

lua/upb.c 内另有 lupb_checkstatus、lupb_indexmm、lupb_register_type 与 lupb_push##type 宏族、lupb_pushdouble、lupb_pushfloat；main.c 在两处调用 `lua_pushcfunction(L, luaopen_lupb)`（F-RT-101）。

消息操作在 lua/msg.c（F-RT-102）：编解码入口 lupb_decode、lupb_Encode、lupb_jsondecode、lupb_jsonencode、lupb_textencode（JSON 与文本格式入口，对应 /concepts/06-text-format-and-json.md 的跨语言对照），以及容器与消息方法 lupb_Arena_gc、lupb_Array_New/Newindex、lupb_array_index/len、lupb_Map_New、lupb_map_index/len/pairs、lupb_Map_Newindex、lupb_MapIterator_Next、lupb_msg_index、lupb_Message_Newindex、lupb_msg_tostring。描述符查询在 lua/def.c（F-RT-103）：lupb_FieldDef_ 前缀函数族（ContainingOneof/ContainingType/Default/Type/HasSubDef/Index/IsExtension/Label/Name/Number/IsPacked/MessageSubDef/EnumSubDef/CType）与 lupb_OneofDef_ContainingType/Field、lupb_oneofiter_next。

代码生成器 lua/upbc.cc 以插件身份实现（F-RT-104）：

```cpp
class LuaGenerator : public protoc::CodeGenerator
int main(int argc, char** argv)
```

与 hpb_generator（/concepts/13-hpb.md）同为"用插件身份实现内置等价能力"的实例（插件协议见 /concepts/10-plugin-protocol.md）。构建规则 lua/lua_proto_library.bzl 头部注释为 "lua_proto_library(): a rule for building Lua protos."，load @bazel_skylib//lib:paths.bzl 与 //bazel/common:proto_info.bzl，实现含 _get_real_short_path、_get_real_root、_generate_output_file 辅助函数（F-RT-105）。

## 相关概念

- [/concepts/12-upb-and-rust-runtime.md](/concepts/12-upb-and-rust-runtime.md)——upb 内核与"双内核架构"的主证据文档，本篇 PHP/Ruby/Lua 三条绑定路线的内核源头
- [/concepts/09-code-generators.md](/concepts/09-code-generators.md)——各语言 `--java_out`/`--csharp_out`/`--objc_out` 等生成 flag 背后的生成器体系
- [/concepts/13-hpb.md](/concepts/13-hpb.md)——同属"绑定 × 内核"谱系的 C++ 多后端 API 层
- [/examples/04-java-ruby-dart-tutorials.md](/examples/04-java-ruby-dart-tutorials.md)——本篇 Java 与 Ruby 运行时的入门教程实例
