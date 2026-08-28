---
type: Concept
title: "公共契约层：Well-Known Types、Conformance 与 Benchmarks"
description: "综述 Well-Known Types 全家族与顶层四十个 BUILD 别名、Conformance 三层测试框架与十九语言失败清单、Benchmarks 基准函数族。"
tags: [protobuf, well-known-types, conformance, benchmarks]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: cpp-core
    resource: /references/cpp-core.md
    title: "protobuf C++ 运行时核心信源"
  - id: repo-structure
    resource: /references/repo-structure.md
    title: "protobuf 仓库结构与构建系统信源"
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
---

protobuf 的生态承诺是"同一份 schema、多个语言实现"。支撑这一承诺的是仓库顶层的三块公共契约层（contract layer）：Well-Known Types（WKT，众所熟知类型）——跨语言共享的标准消息家族；Conformance（一致性）测试——用同一份测试协议经管道校验任意语言的实现；Benchmarks（基准测试）——用同一套 BM_* 函数族度量各内核性能。三者分别锁定"数据契约""行为契约"与"性能基线"，是所有语言运行时（见 /concepts/14-other-language-runtimes.md）共同对齐的坐标系。

本篇先给出 WKT 全家族与顶层 BUILD 的 40 个 alias，再剖析 conformance 的三层框架（ConformanceTestRunner / Testee / TestManager）与 19 语言 failure list，最后过一遍 benchmarks 的 BM_* 函数族与 descriptor 基准数据。

## Well-Known Types 全家族

WKT 的 proto 定义集中于 src/google/protobuf/ 下（该目录含 bridge、compiler、io、json、stubs、test_protos、testdata、testing、util 九个子目录，共 330 个条目，F-REPO-004），按信源事实逐族列出（F-CPP-126~136）：

| proto 文件 | 消息 / 枚举（定义行号） |
|---|---|
| any.proto | message Any（72） |
| duration.proto | message Duration（102），字段 `int64 seconds = 1` / `int32 nanos = 2` |
| timestamp.proto | message Timestamp（133），字段 `int64 seconds = 1` / `int32 nanos = 2` |
| struct.proto | Struct（56）、Value（67）、ListValue（108）、enum NullValue（102） |
| wrappers.proto | DoubleValue（66）、FloatValue（77）、Int64Value（88）、UInt64Value（99）、Int32Value（110）、UInt32Value（121）、BoolValue（132）、StringValue（143）、BytesValue（154），共九个 |
| type.proto | Type（52）、Field（75）、Enum（160）、EnumValue（181）、Option（196）、enum Syntax（210） |
| api.proto | Api（59）、Method（112）、Mixin（222） |
| source_context.proto | message SourceContext（44） |
| field_mask.proto | message FieldMask（240） |
| empty.proto | `message Empty {}`（51） |
| cpp_features.proto | message CppFeatures（18）——特性扩展（见 /concepts/15-editions-feature-system.md） |

若干细节值得留意：type.proto 的 Field 含 `int32 number = 3` 与 `int32 oneof_index = 7`，EnumValue 含 `int32 number = 2`（F-CPP-131）；wrappers 家族每个消息只包一个原生值字段（Int64Value 含 `int64 value = 1`，Int32Value 含 `int32 value = 1`，F-CPP-130）。Any 的 C++ 交互接口位于 any.h（F-CPP-126）：

```cpp
bool PackFrom(const ::google::protobuf::Message& message);
bool UnpackTo(::google::protobuf::Message* message) const;
template <typename T> bool Is() const;
```

入门教程中对 Timestamp WKT 的实际用法见 /examples/01-addressbook-proto.md。

## 顶层 BUILD 的 40 个 alias 与 feature proto

WKT 的构建入口集中暴露在主仓顶层 BUILD.bazel（F-REPO-048）：any、api、duration、empty、field_mask、source_context、struct、timestamp、type、wrappers 十个 target 各有 `_proto`、`_cc_proto`、`_upb_proto`、`_upb_reflection_proto` 四个变体，合计 **40 个 alias**；actual 均指向 `//src/google/protobuf:` 下同名 target，visibility 为 `//visibility:public`。

四个变体分别服务四类消费者：schema 引用（proto_library）、C++ 内核（cc_proto）、upb 内核（upb_proto）与 upb 反射（upb_reflection_proto）——双内核架构（/concepts/12-upb-and-rust-runtime.md）在构建层的又一次显影。同一 BUILD 另定义 descriptor_proto、compiler_plugin_proto、cpp_features_proto、java_features_proto、go_features_proto、c_sharp_features_proto，以及 test_messages_proto2/proto3 的多语言变体等 target（F-REPO-049）。

## Conformance 三层框架

conformance/README.md 开宗明义（F-TST-001/F-TST-002 原句）：

> This directory contains conformance tests for testing completeness and correctness of Protocol Buffers implementations.
> This directory contains the tester process `conformance-test`, which contains all of the tests themselves. Then separate programs written in whatever language you want to test communicate with the tester program over a pipe.

即"测试器（tester）进程 + 被测程序（Testee）经管道通信"的架构。测试协议本身定义于 conformance/conformance.proto：`package conformance;`，含 enum WireFormat、enum TestCategory、message TestStatus、message FailureSet、message ConformanceRequest（含 `oneof payload`）、message ConformanceResponse（含 `oneof result`）、message JspbEncodingConfig（F-TST-033）。被测程序 "only needs to be able to read from stdin and write to stdout."，C++ 参考实现 conformance_cpp.cc 仅 150 行（F-TST-006）。

框架分三层：

**第一层：ConformanceTestRunner 抽象接口**（conformance/test_runner.h，F-TST-008），唯一纯虚方法：

```cpp
virtual std::string RunTest(absl::string_view test_name,
                            absl::string_view input) = 0;
```

input 为 serialized conformance.ConformanceRequest，返回 serialized conformance.ConformanceResponse。

**第二层：Testee 流式 DSL**（conformance/testee.h，命名空间 `google::protobuf::conformance::internal`）。`Testee` 持有 runner 指针，`CreateTest(name, strictness)` 创建 `Test`；Test 经 `ParseBinary(const Descriptor* type, Wire input)` / `ParseText(...)` / `ParseJson(..., JsonParseOptions options = {})` 产出 `InMemoryMessage`，再由 `SerializeBinary() / SerializeText(TextSerializationOptions) / SerializeJson()` 完成"解析→序列化"往返（均为右值限定方法，F-TST-009~013）。`TestStrictness` 分 `kRequired = 0` 与 `kRecommended = 1`；`TestResult` 记录 name/strictness/type/format/response（F-TST-009/010）。Testee::Run 在响应解析失败时置 `response.set_runtime_error("response proto could not be parsed.")`（F-TST-015）；Parse* 方法分别设置 test_category 为 BINARY_TEST / TEXT_FORMAT_TEST / JSON_TEST 或 JSON_IGNORE_UNKNOWN_PARSING_TEST（F-TST-016）。完整测试名拼接格式为 `strictness_string + "." + syntax_identifier + "." + FormatIdentifier(Input) + "Input." + test_name + "." + FormatIdentifier(Output) + "Output"`（F-TST-017），其中 GetEditionIdentifier 把 EDITION_PROTO3→"Proto3"、EDITION_PROTO2→"Proto2"、EDITION_UNSTABLE→"EditionUnstable"、其余→"Editions"（F-TST-022），GetFormatIdentifier 把 PROTOBUF→"Protobuf"、JSON→"Json"、TEXT_FORMAT→"TextFormat"（F-TST-023）——edition 直接进入测试命名。

**第三层：TestManager**（conformance/test_manager.h，F-TST-018~020）：管理期望失败清单（私有成员 `FailureListTrieNode expected_failure_list_`，即三级 trie 树节点实现 failure_list_trie_node.cc）与五个计数器 skipped()/expected_failures()/unexpected_failures()/expected_successes()/unexpected_successes()，方法 LoadFailureList/SaveFailureList/ReportSuccess/ReportFailure/ReportSkip/Finalize。文件级常量 `kMaximumWildcardExpansions = 20` 与 `kFailureMessageLengthLimit = 128`；未调用 Finalize 即析构会 `ABSL_LOG(FATAL)`。

构建入口双轨（F-TST-003/004/005）：CMake 侧 `cmake . -Dprotobuf_BUILD_CONFORMANCE=ON && cmake --build .` 产出 `conformance_test_runner`（对应 CMakeLists 的 17 个 option 之一，见 /concepts/00-repo-overview-and-build-systems.md）；Bazel 侧 C++ 为 `bazel test //src:conformance_test`（CMake 方式 `ctest -R conformance_cpp_test`），其他语言目标包括 `//csharp:conformance_test`、`//java/core:conformance_test`、`//java/lite:conformance_test`、`//objectivec:conformance_test`（`--macos_minimum_os=12.0`）、`//php:conformance_test`、`//php:conformance_test_c`、`//python:conformance_test`、`//python:conformance_test_cpp`（`--define=use_fast_cpp_protos=true`）、`//ruby:conformance_test`（`--define=ruby_platform=c`）、`//ruby:conformance_test_jruby`（`--define=ruby_platform=java`）。注意 README 明言 "the test runner currently does not work on Windows."（F-TST-007）。

Starlark 宏 `conformance_test(name, testee, failure_list = None, text_format_failure_list = None, maximum_edition = None, performance = None, **kwargs)` 包装 sh_test，`tags = ["conformance"]`，data 固定包含 `//conformance:conformance_test_runner`（F-TST-021）——maximum_edition 参数把 editions 协商接入一致性测试。

## failure list：19 个语言的期望失败清单

conformance/ 目录维护 19 个 failure_list_*.txt（F-TST-034）：cpp、csharp、csharp_performance、dart_upb、java、java_lite、jruby、jruby_ffi、objc、objc_performance、php、php_c、python、python-post26、python_cpp、python_upb、ruby、rust_cc、rust_upb；另有 8 个 text_format_failure_list_{cpp, dart_upb, java, java_lite, php, python, rust_cc, rust_upb}.txt。

清单命名直接编码"同一语言多内核"：python/python_cpp/python_upb、php/php_c、rust_cc/rust_upb、ruby/jruby/jruby_ffi 各为一组（双内核洞察见 /concepts/12-upb-and-rust-runtime.md）。增量更新由 py_binary 目标 update_failure_list.py 完成（F-TST-030）；test_protos/ 子目录仅含 test_messages_edition_unstable.proto 与 test_messages_edition2023.proto（F-TST-035）。

框架自身也有单元测试：cc_test 目标 failure_list_trie_node_test、naming_test、testee_test、test_manager_test、binary_wireformat_test 汇聚为 `test_suite(name = "conformance_framework_tests")`，注释原句 "This is not to be confused with a conformance test itself."（F-TST-025/026）——框架代码与被测行为分离的自觉。

## Benchmarks：BM_* 函数族与 descriptor 基准

benchmarks/benchmark.cc 基于 google benchmark 框架（`#include <benchmark/benchmark.h>`），文件级变量 `upb_StringView descriptor = benchmarks_descriptor_proto_upbdefinit.descriptor;` 与 `int64_t buf[8191];`，自由函数 `void CollectFileDescriptors(const _upb_DefPool_Init* file, std::vector<upb_StringView>& serialized_files, absl::flat_hash_set<const _upb_DefPool_Init*>& seen)` 负责收集描述符（F-TST-037/038）。

BENCHMARK 注册的 BM_* 函数族按主题分组（F-TST-039）：

- **Arena 组**：BM_ArenaOneAlloc、BM_ArenaInitialBlockOneAlloc、BM_ArenaFuseUnbalanced（`->Range(2,128)`）、BM_ArenaFuseBalanced（`->Range(2,128)`）——对应 /concepts/04-arena-memory-management.md 的 Fuse 机制；
- **描述符加载组**：BM_LoadAdsDescriptor_Upb 与 BM_LoadAdsDescriptor_Proto2（各含 NoLayout/WithLayout 模板变体）；
- **解析组**：BM_Parse_Upb_FileDesc（CompiledIn/Parsed × UseArena/InitBlock × Copy/Alias 共 8 组模板组合）、BM_Parse_Proto2（FileDesc×NoArena/UseArena/InitBlock×Copy、FileDescSV×InitBlock×Alias）；
- **序列化组**：BM_SerializeDescriptor_Proto2、BM_SerializeDescriptor_Upb（4 组模板）；
- **JSON 组**：BM_JsonParse_Upb_Default、BM_JsonParse_Upb_Utf8Disable、BM_JsonParse_Upb_Utf8Enforce、BM_JsonParse_Proto2、BM_JsonSerialize_Upb、BM_JsonSerialize_Proto2。

模板参数由四个枚举与一组模板结构体供给：`enum LoadDescriptorMode { NoLayout, WithLayout };`、`enum CopyStrings`、`enum ArenaMode`、`enum MinitableMode`，以及 `Proto2Factory<NoArena,P>` / `<UseArena,P>` / `<InitBlock,P>` 三个特化（F-TST-040）。

基准数据是 descriptor.proto 的镜像拷贝 benchmarks/descriptor.proto（`syntax = "proto2"; package upb_benchmark;`，含 FileDescriptorSet、FileDescriptorProto、DescriptorProto（嵌套 ExtensionRange/ReservedRange）、FieldDescriptorProto（enum Type 18 值、enum Label 3 值）、FileOptions（enum OptimizeMode）、FieldOptions（enum CType、enum JSType）、UninterpretedOption、SourceCodeInfo、GeneratedCodeInfo 等 23 个消息；注意该文件中**不存在**名为 BenchmarkDataset 的 message，F-TST-041/042）。

其变体 **descriptor_sv.proto**（`package upb_benchmark.sv`、`objc_class_prefix="GPB"`）与 descriptor.proto 同名 message 集合，但字符串字段大量追加 `[ctype = STRING_PIECE]` 选项——如 `optional string name = 1 [ctype = STRING_PIECE];`（F-TST-043）——专测 string_view（视图）访问路径。empty.proto 则定义 `syntax = "proto3"; package upb_benchmark; message Empty {}`（F-TST-044）。

构建与对比流程：build_defs.bzl 提供 `tmpl_cc_binary`、`cc_optimizefor_proto_library`（cmd 追加 `'option optimize_for = ...;'`）与 `expand_suffixes` 三个函数（F-TST-045）；BUILD 目标含 descriptor_proto、benchmark_descriptor_upb_proto、benchmark_descriptor_sv_proto、ads_upb_proto_reflection、100_msgs_proto、200_msgs_proto、100_fields_proto、200_fields_proto、empty_proto 等 proto_library，benchmark_descriptor_cc_proto 与 benchmark_descriptor_sv_cc_proto 两个 cc_proto_library，cc_test benchmark 及 gen_synthetic_protos / gen_upb_binary_c / gen_protobuf_binary_cc 三个 py_binary（F-TST-048）。对比工具 compare.py（docstring 原句 "Benchmarks the current working directory against a given baseline."，baseline 默认 "main"）串联 `CC=clang bazel build -c opt --copt=-march=native benchmarks:benchmark`、`--benchmark_out_format=json --benchmark_repetitions={} --benchmark_min_time=0.05` 与 benchstat、bloaty（`-d compileunits,symbols`）、`objcopy --strip-debug` 等命令（F-TST-046/047）。

## 相关概念

- [/concepts/15-editions-feature-system.md](/concepts/15-editions-feature-system.md)——conformance_test 宏的 maximum_edition 参数与 EDITION_UNSTABLE 测试 proto 的上游机制
- [/concepts/03-descriptors-and-reflection.md](/concepts/03-descriptors-and-reflection.md)——benchmarks 镜像的 descriptor.proto 与 DescriptorPool 反射体系
- [/concepts/04-arena-memory-management.md](/concepts/04-arena-memory-management.md)——BM_ArenaFuse* 基准所度量的 Arena Fuse 机制
- [/examples/01-addressbook-proto.md](/examples/01-addressbook-proto.md)——Timestamp WKT 在入门 schema 中的实际引用
