---
type: Concept
title: "Editions 特性系统"
description: "解析 Edition 八值枚举、FeatureSet 与 FeatureSetDefaults 数据模型、编译器与九个生成器的协商矩阵，以及 editions 目录的默认值编译与测试体系。"
tags: [protobuf, editions, feature-set, code-generator]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: cpp-core
    resource: /references/cpp-core.md
    title: "protobuf C++ 运行时核心信源"
  - id: compiler
    resource: /references/compiler.md
    title: "protoc 编译器信源"
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
  - id: repo-structure
    resource: /references/repo-structure.md
    title: "protobuf 仓库结构与构建系统信源"
---

Editions（版本）特性系统是 protobuf v37 对"语法版本"概念的一次彻底重构：proto2 与 proto3 不再是两套平行的独立语法，而是 FeatureSet（特性集合）中的两个 legacy（遗留）预设值；编译器、生成器与运行时通过 edition（版本）区间与 supported_features 位标志协商各自能力。理解这条主线的钥匙是：**语法版本被降维为 feature 预设**——每个"新语法"只是往 Edition 数值刻度上追加一个更大的值，并配一张 FeatureSetDefaults 默认值表。

本篇依次展开 Edition 八值枚举、FeatureSet/FeatureSetDefaults 数据模型、编译器的 feature 解析链、九个生成器的协商矩阵，以及 editions/ 目录的默认值编译规则与 56 个 codegen_tests 前缀分组。证据横跨 F-CPP/F-CMP/F-TST/F-REPO 四份事实清单。

## Edition 枚举：从语法版本到数值刻度

Edition 枚举定义于 protobuf 自举生成的 descriptor.pb.h（该文件由 protobuf 代码生成器产出，生成器"先吃自己的狗粮"，见 /concepts/03-descriptors-and-reflection.md），完整八值逐条照录如下（F-CPP-063，descriptor.pb.h:999-1007）：

```cpp
enum Edition : int {
  EDITION_UNKNOWN = 0,
  EDITION_LEGACY = 900,
  EDITION_PROTO2 = 998,
  EDITION_PROTO3 = 999,
  EDITION_2023 = 1000,
  EDITION_2024 = 1001,
  EDITION_2026 = 1002,
  EDITION_UNSTABLE = 9999,
};
```

各值的语义解读：

| 值 | 名称 | 含义 |
|---|---|---|
| 0 | EDITION_UNKNOWN | 默认值，版本未指定 |
| 900 | EDITION_LEGACY | 遗留语法区间的界标 |
| 998 | EDITION_PROTO2 | proto2 预设（被编码为枚举中的一个"过去的版本"） |
| 999 | EDITION_PROTO3 | proto3 预设 |
| 1000 | EDITION_2023 | 正式发布的第一代 edition |
| 1001 | EDITION_2024 | 第二代 edition |
| 1002 | EDITION_2026 | 第三代 edition（当前 protoc 支持上界） |
| 9999 | EDITION_UNSTABLE | 不稳定开发版（conformance 测试专用，见第 16 篇） |

关键观察：EDITION_PROTO2=998 与 EDITION_PROTO3=999 夹在 LEGACY=900 与 2023=1000 之间——旧语法在 v37 编译器内部只是 feature 解析系统中的两个预设，而非独立体系。该枚举在 descriptor.proto 中位于第 45 行（F-CPP-067），同文件还定义了 enum SymbolVisibility（descriptor.proto:1547）。

## FeatureSet 与 FeatureSetDefaults：特性的数据模型

descriptor.proto 顶层共定义 23 个 message（F-CPP-066），其中两个专为 editions 服务：

- **FeatureSet**（descriptor.proto:1060）——可组合的特性开关集合，字段即特性；其关联枚举包括 FeatureSet_FieldPresence（字段存在性）、FeatureSet_EnumType、FeatureSet_EnforceNamingStyle（命名风格强制）等（前向声明见 F-CPP-065/F-CPP-068）。
- **FeatureSetDefaults**（descriptor.proto:1297）——"每个 edition 的默认特性值"表，即预设的本体：给定一个 Edition，查表得到一份 FeatureSet。

运行时侧，FileDescriptor 提供两个入口（F-CPP-055/F-CPP-056）：

```cpp
Edition edition() const;  // 注释原句：For legacy proto2/proto3 files,
                          // special EDITION_PROTO2 and EDITION_PROTO3 values are used
const FeatureSet& features() const { return *merged_features_; }
```

`edition()` 返回文件所属版本（对 proto2/proto3 文件使用专用特殊值），`features()` 返回合并（merged）后的 FeatureSet——文件、消息、字段各级特性逐层覆盖合并的最终结果。解析与合并的核心组件 feature_resolver.h 位于 src/google/protobuf/ 根目录（F-CPP-138）。

各语言还可声明自己的特性扩展（feature extension）：主仓顶层 BUILD.bazel 定义了 cpp_features_proto、java_features_proto、go_features_proto、c_sharp_features_proto 等 target（F-REPO-049）。其中 C++ 的 `message CppFeatures`（cpp_features.proto:18）对应的 C++ 侧声明 `namespace pb { class CppFeatures; }` 位于 extension_set.h（F-CPP-136）。

## 编译器协商：feature 解析链

**（1）CodeGenerator::Feature 位标志**（F-CMP-037，code_generator.h）：

```cpp
enum Feature {
  FEATURE_PROTO3_OPTIONAL = 1,
  FEATURE_SUPPORTS_EDITIONS = 2,
};
// 注释原句：This must be kept in sync with plugin.proto.
virtual uint64_t GetSupportedFeatures() const { return 0; }
```

FEATURE_SUPPORTS_EDITIONS=2 声明"该生成器理解 editions"；注释明确要求与 plugin.proto 的 CodeGeneratorResponse 字段保持同步（插件协议见 /concepts/10-plugin-protocol.md）。

**（2）edition 区间虚方法**，默认均为 EDITION_UNKNOWN（F-CMP-040）：

```cpp
virtual Edition GetMinimumEdition() const { return Edition::EDITION_UNKNOWN; }
virtual Edition GetMaximumEdition() const { return Edition::EDITION_UNKNOWN; }
```

**（3）protoc 本体的能力边界**（F-CMP-043，constexpr 版本函数）：

```cpp
constexpr auto ProtocMinimumEdition() { return Edition::EDITION_PROTO2; }
constexpr auto ProtocMaximumEdition() { return Edition::EDITION_2026; }
constexpr auto MaximumKnownEdition() { return Edition::EDITION_2026; }
```

**（4）协商执行点**：CommandLineInterface 的私有方法 `EnforceEditionsSupport(codegen_name, supported_features, minimum_edition, maximum_edition, parsed_files)` 与 `SetupFeatureResolution(DescriptorPool& pool)`（F-CMP-017）负责校验与初始化；非虚公有方法 `absl::StatusOr<FeatureSetDefaults> BuildFeatureSetDefaults() const;`（F-CMP-041）供生成器获取默认值表；受保护静态方法族 `GetResolvedSourceFeatures(desc)`（内部调用 `InternalFeatureHelper::GetFeatures`）等（F-CMP-042）供生成器读取解析后的特性。

**（5）命令行 flag**：`--edition_defaults_out`、`--edition_defaults_minimum`、`--edition_defaults_maximum`（F-CMP-014）——直接导出 FeatureSetDefaults 的工具通道（命令行全景见 /concepts/07-protoc-command-line.md）。

**（6）Parser 行为切换**：`DefaultToOptionalFields()` 对 `syntax_identifier_ == "editions"` 与 `"proto3"` 返回 true（F-CMP-027）——语法差异在解析器内部即被吸收进 feature 体系。

## 九个生成器的协商矩阵

protoc 内置九个声明 edition 能力的生成器，其协商参数高度一致（P3O = FEATURE_PROTO3_OPTIONAL，SE = FEATURE_SUPPORTS_EDITIONS）：

| 生成器 | supported_features | GetMinimumEdition | GetMaximumEdition | GetFeatureExtensions |
|---|---|---|---|---|
| cpp（CppGenerator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | {GetExtensionReflection(pb::cpp)} |
| java（JavaGenerator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | {GetExtensionReflection(pb::java)} |
| kotlin（KotlinGenerator） | P3O \| SE（.cc 实现） | EDITION_PROTO2 | EDITION_2026 | {GetExtensionReflection(pb::java)} |
| python（Generator / PyiGenerator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | {} |
| csharp（Generator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | {GetExtensionReflection(pb::csharp)} |
| objectivec（ObjectiveCGenerator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | — |
| php（Generator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | {} |
| ruby（Generator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | — |
| rust（RustGenerator） | P3O \| SE | EDITION_PROTO2 | EDITION_2026 | — |

来源：F-CMP-057（cpp）、F-CMP-068（java）、F-CMP-090（kotlin）、F-CMP-075/077（python 与 pyi）、F-CMP-080（csharp）、F-CMP-084（objc）、F-CMP-085（php）、F-CMP-086（ruby）、F-CMP-088（rust）。

**唯一例外是 Ruby 的 RBS 签名生成器**（F-CMP-087，ruby/rbs_generator.h）：

```cpp
class PROTOC_EXPORT RBSGenerator : public CodeGenerator {
  uint64_t GetSupportedFeatures() const override { return FEATURE_PROTO3_OPTIONAL; }
};
```

RBSGenerator 只声明 FEATURE_PROTO3_OPTIONAL，既不含 FEATURE_SUPPORTS_EDITIONS，也没有 GetMinimumEdition/GetMaximumEdition override——即停留在基类默认的 EDITION_UNKNOWN。这个"能力降级"实例写入矩阵的价值在于防止读者误以为所有生成器能力等价：协商矩阵是真实生效的，RBS 生成器只消费 proto3 语法级别的信息，无需理解 editions。

## editions/ 目录：默认值编译与 codegen_tests

editions/ 目录（F-REPO-054）由 codegen_tests/、golden/、input/ 三个子目录与 BUILD、defaults.bzl 及一组测试文件构成（含 4 个 defaults_test_embedded*.h.template 模板、edition_defaults_test_utils.cc/.h、generated_files_test.cc、generated_reflection_test.cc、internal_defaults_escape.cc）。

defaults.bzl 定义两条规则（F-TST-066/F-TST-067）：

- **compile_edition_defaults**：把 proto 源编译为 FeatureSetDefaults 二进制（输出 `%{name}.binpb`），attrs 含 srcs、minimum_edition、maximum_edition 与可选 protoc（默认 `//src/google/protobuf/compiler/release:protoc_minimal`），mnemonic 为 "ProtobufCompileEditionDefaults"，向 protoc 传 `--edition_defaults_out/--edition_defaults_minimum/--edition_defaults_maximum/--proto_path`；
- **embed_edition_defaults**：doc 原句 "genrule to embed edition defaults binary data into a template file."，把 .binpb 以 octal/base64/decimal_array/hex_array 四种编码嵌入 .h.template 模板（placeholder 替换），mnemonic 为 "ProtobufEmbedEditionDefaults"。

测试侧，defaults_test.cc 的 TEST 用例覆盖 Check2023、Check2024、Check2026、CheckFuture、CheckFarFuture、Embedded、EmbeddedBase64、EmbeddedDecimalArray、EmbeddedHexArray（F-TST-068）；`OverridableDefaultsTest` 则对 Proto2、Proto3、Edition2023、Edition2024、Edition2026 五个预设逐一验证——辅助函数 `absl::StatusOr<FeatureSetDefaults> ReadDefaults(absl::string_view name)` 经 bazel runfiles 读取 .binpb 文件（F-TST-069）。

codegen_tests/ 下 56 个 proto 按文件名前缀分组（F-REPO-055 / F-TST-072）：

| 前缀 | 数量 | 代表文件 |
|---|---|---|
| edition2023_* | 30 | edition2023_ctype.proto、edition2023_go_api_*（5 个）、edition2023_java_*（7 个）、edition2023_naming_style_*（9 个）、edition2023_symbol_visibility*.proto、edition2023_string_type*.proto |
| edition2024_* | 6 | edition2024_default_symbol_visibility.proto 及其 5 个变体 |
| proto2_* | 13 | proto2_enum.proto、proto2_group.proto、proto2_optional.proto、proto2_packed.proto、proto2_required.proto、proto2_utf8_*.proto（3 个）等 |
| proto3_* | 7 | proto3_enum.proto、proto3_implicit.proto、proto3_optional.proto、proto3_packed.proto、proto3_unpacked.proto、proto3_utf8_strict.proto、proto3_import.proto |

前缀本身就是 edition 语义的具象化：packed、optional、utf8 验证等同一组行为差异在四个前缀族下各有一份拷贝，直接对比即可看出 feature 预设如何改变代码生成结果——这正是"proto2/proto3 降维为 feature 预设"主线的最后一块证据。

## 相关概念

- [/concepts/03-descriptors-and-reflection.md](/concepts/03-descriptors-and-reflection.md)——descriptor.proto 单一事实源：FeatureSet/FeatureSetDefaults 所在的 23 个顶层 message
- [/concepts/07-protoc-command-line.md](/concepts/07-protoc-command-line.md)——`--edition_defaults_*` flag 与编译管线全景
- [/concepts/09-code-generators.md](/concepts/09-code-generators.md)——九个生成器的目录结构与特色组件（本篇矩阵的生成器清单来源）
- [/concepts/16-wkt-conformance-benchmarks.md](/concepts/16-wkt-conformance-benchmarks.md)——conformance 测试如何以 maximum_edition 参数接入 editions 协商
