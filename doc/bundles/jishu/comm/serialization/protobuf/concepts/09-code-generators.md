---
type: Concept
title: "代码生成器体系与各语言实现"
description: "CodeGenerator 接口契约（Generate 纯虚/GenerateAll 默认实现/Feature 位标志/edition 协商）与 GeneratorContext 输出抽象，及 cpp/java/python 等 9 个内置生成器的目录结构与 edition 支持矩阵。"
tags: [protobuf, codegen, compiler]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: compiler
    resource: /references/compiler.md
    title: "protoc 编译器信源"
---

protoc 的语言扩展能力统一收敛在 CodeGenerator 抽象接口上：内置语言生成器在 main.cc 进程内注册（见 [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md)），外部插件通过 stdin/stdout 协议获得完全相同的输入与协商机制（见 [插件协议](/concepts/10-plugin-protocol.md)）——两者唯一的差异是"进程内注册"还是"协议化通信"。本篇先讲接口契约，再逐一过 9 个内置生成器的目录结构与特色组件，并给出 edition 支持矩阵。

## CodeGenerator 接口契约

代码生成的主接口（F-CMP-035）：

```cpp
class PROTOC_EXPORT CodeGenerator {
  virtual bool Generate(const FileDescriptor* file, const std::string& parameter,
                        GeneratorContext* generator_context, std::string* error) const = 0;
};
```

Generate 为纯虚——每个生成器必须实现"单个 FileDescriptor → 目标代码"的转换。批量入口 GenerateAll 非纯虚、有默认实现（F-CMP-036）：

```cpp
virtual bool GenerateAll(const std::vector<const FileDescriptor*>& files, const std::string& parameter,
                         GeneratorContext* generator_context, std::string* error) const;
```

能力声明由三组虚方法承担。Feature 位标志（F-CMP-037）：

```cpp
enum Feature { FEATURE_PROTO3_OPTIONAL = 1, FEATURE_SUPPORTS_EDITIONS = 2 };
virtual uint64_t GetSupportedFeatures() const { return 0; }
```

注释原句 "This must be kept in sync with plugin.proto."——与插件协议中 CodeGeneratorResponse.Feature 枚举保持同步。edition 协商（F-CMP-040）：

```cpp
virtual Edition GetMinimumEdition() const { return Edition::EDITION_UNKNOWN; }
virtual Edition GetMaximumEdition() const { return Edition::EDITION_UNKNOWN; }
```

feature 扩展点（F-CMP-039）：`virtual std::vector<const FieldDescriptor*> GetFeatureExtensions() const { return {}; }`，供语言特化 feature（如 pb.cpp）声明。另有 `virtual bool HasGenerateAll() const { return true; }`（F-CMP-038，注释原句："This is no longer used, but this class is part of the opensource protobuf library, so it has to remain to keep vtables the same for the current version of the library."）与公有非虚方法 `absl::StatusOr<FeatureSetDefaults> BuildFeatureSetDefaults() const;`（F-CMP-041）。

编译器自身的 edition 边界（F-CMP-043）：

```cpp
constexpr auto ProtocMinimumEdition() { return Edition::EDITION_PROTO2; }
constexpr auto ProtocMaximumEdition() { return Edition::EDITION_2026; }
constexpr auto MaximumKnownEdition() { return Edition::EDITION_2026; }
```

protected 静态工具（F-CMP-042）：`template <typename DescriptorT> static const FeatureSet& GetResolvedSourceFeatures(const DescriptorT& desc)`（内部调用 `::google::protobuf::internal::InternalFeatureHelper::GetFeatures(desc)`）、`static auto GetResolvedSourceFeatureExtension(...)`、`static typename TypeTraitsT::ConstType GetUnresolvedSourceFeatures(...)`、`static Edition GetEdition(const FileDescriptor& file)`。文件级导出 `PROTOC_EXPORT bool CanSkipEditionCheck(absl::string_view filename);`（F-CMP-045）。

code_generator_lite.h 不定义任何类，导出轻量工具（F-CMP-046）：`PROTOC_EXPORT void ParseGeneratorParameter(absl::string_view, std::vector<std::pair<std::string, std::string>>*);`、`PROTOC_EXPORT std::string StripProto(absl::string_view filename);`、`PROTOC_EXPORT bool IsKnownFeatureProto(absl::string_view filename);`。

## GeneratorContext 输出抽象

生成器的输出侧抽象（F-CMP-044）：

```cpp
class PROTOC_EXPORT GeneratorContext {
  virtual io::ZeroCopyOutputStream* Open(const std::string& filename) = 0;
  virtual io::ZeroCopyOutputStream* OpenForAppend(const std::string&);
  virtual io::ZeroCopyOutputStream* OpenForInsert(const std::string& filename,
                                                  const std::string& insertion_point);
  virtual io::ZeroCopyOutputStream* OpenForInsertWithGeneratedCodeInfo(
      const std::string&, const std::string&, const google::protobuf::GeneratedCodeInfo&);
  virtual void ListParsedFiles(std::vector<const FileDescriptor*>*);
  virtual bool GetCompilerVersion(Version*) const;
};
typedef GeneratorContext OutputDirectory;
```

OpenForInsert 与插入点（insertion point）机制配合，允许生成器向既有文件的指定位置追加内容——插件协议的 CodeGeneratorResponse.File.insertion_point 字段即映射到这里（见 [插件协议](/concepts/10-plugin-protocol.md)）。

## C++ 生成器（cpp/）

`class PROTOC_EXPORT CppGenerator final : public CodeGenerator`（cpp/generator.h L43；cpp_generator.h 全文仅 `#include` 该头，F-CMP-056）。特色成员（F-CMP-057）：`enum class Runtime { kGoogle3, kOpensource, kOpensourceGoogle3 };`、`void set_opensource_runtime(bool)`、`void set_runtime_include_base(std::string base)`，私有 `bool GenerateImpl(const FileDescriptor*, const std::string&, GeneratorContext*, std::string*, const Options&) const;` 与 `absl::Status ValidateFeatures(const FileDescriptor*) const;`。

文件级编排由 `class PROTOC_EXPORT FileGenerator`（F-CMP-058）承担：`void GeneratePBHeader(io::Printer* p, absl::string_view info_path);`、`void GenerateProtoHeader(io::Printer* p, absl::string_view info_path);`、`void GenerateSource(io::Printer* p);`、`int NumMessages() const;`、`int NumExtensions() const;`、`void GenerateSourceForMessage(int idx, io::Printer* p);`、`void GenerateSourceForExtension(int idx, io::Printer* p);`、`void GenerateGlobalSource(io::Printer* p);`。

cpp/ 目录的类清单（F-CMP-059）：EnumGenerator、ExtensionGenerator、FieldGeneratorBase、FieldGenerator、FieldGeneratorTable、FileGenerator、MessageSCCAnalyzer、Formatter、NamespaceOpener、FieldLayout、MessageGenerator、IfdefGuardPrinter、FieldGroup、MessageLayoutHelper、NamespacePrinter、ParseFunctionGenerator、ServiceGenerator。字段级生成走 field_generators/ 工厂（F-CMP-060/061）：目录含 8 个文件（cord_field.cc、enum_field.cc、map_field.cc、message_field.cc、primitive_field.cc、string_field.cc、string_view_field.cc、generators.h），generators.h 提供 14 个工厂函数（返回类型均为 `std::unique_ptr<FieldGeneratorBase>`，参数均为 `const FieldDescriptor* desc, const Options& options`；函数名 "Singuar" 为源码原文拼写）：MakeSinguarPrimitiveGenerator、MakeRepeatedPrimitiveGenerator、MakeSinguarEnumGenerator、MakeRepeatedEnumGenerator、MakeSinguarStringGenerator、MakeRepeatedStringGenerator、MakeSingularStringViewGenerator、MakeRepeatedStringViewGenerator、MakeSinguarMessageGenerator、MakeRepeatedMessageGenerator、MakeOneofMessageGenerator、MakeMapGenerator、MakeSingularCordGenerator、MakeOneofCordGenerator。

解析函数生成（F-CMP-063）：`class ParseFunctionGenerator` 含静态常量 `static constexpr float kUnknownPresenceProbability = 0.5f;`、静态方法 `static std::vector<internal::TailCallTableInfo::FieldOptions> BuildFieldOptions(...)`、`static internal::TailCallTableInfo BuildTcTableInfoFromDescriptor(...)`、公有 `void GenerateAliasParseTableType(io::Printer* printer);`、`void GenerateParseTableHelperDefinition(io::Printer* printer);`——尾调用解析表（TailCallTable）的生成入口。命名工具集中在 helpers.h（F-CMP-062）：`PROTOC_EXPORT std::string ClassName(const Descriptor* descriptor);`、`std::string QualifiedClassName(const Descriptor* d, const Options& options);`（4 重载）、`PROTOC_EXPORT std::string FieldName(const FieldDescriptor* field);`、`std::string FieldConstantName(const FieldDescriptor* field);`、`std::string DefaultValue(const Options& options, const FieldDescriptor* field);`、`std::string Namespace(const FileDescriptor* d);`（4 重载）、`PROTOC_EXPORT bool ValidateCcNamespace(const FileDescriptor* file, std::string* error);`、`std::string ExtensionName(const FieldDescriptor* d);`、`std::string QualifiedExtensionName(const FieldDescriptor* d, const Options& options);`、`PROTOC_EXPORT std::string StripProto(absl::string_view filename);`。tracker.h（F-CMP-064）导出两个 MakeTrackerCalls 重载生成字段访问追踪调用。

生成器行为开关聚合在 `struct Options`（F-CMP-065/066）：`cpp::MessageSCCAnalyzer* scc_analyzer`、`std::string dllexport_decl;`、`std::string runtime_include_base;`、`bool proto_h = false;`、`bool transitive_pb_h = true;`、`bool lite_implicit_weak_fields = false;`、`bool bootstrap = false;`、`bool opensource_runtime = false;` 等，及 `enum EnforceOptimizeMode { kNoEnforcement, kSpeed, kCodeSize, kLiteRuntime };` 与 `struct FieldListenerOptions { bool inject_field_listener_events = false; absl::flat_hash_set<std::string> forbidden_field_listener_events; };`。

## Java 生成器（java/）

`class PROTOC_EXPORT JavaGenerator : public CodeGenerator`（java/generator.h L38；java_generator.h 仅 #include，F-CMP-067）。`GetSupportedFeatures()` 实现于 generator.cc L39-42：`return CodeGenerator::Feature::FEATURE_PROTO3_OPTIONAL | CodeGenerator::Feature::FEATURE_SUPPORTS_EDITIONS;`（F-CMP-068）。

Java 的特色是 full/lite 双工厂体系（F-CMP-069/071）：java/full/ 含 14 个 .h（enum.h、enum_field.h、extension.h、field_generator.h、generator_factory.h、make_field_gens.h、map_field.h、message.h、message_builder.h、message_field.h、oneof_generator.h、primitive_field.h、service.h、string_field.h），java/lite/ 含 12 个（同上去掉 oneof_generator.h 与 service.h）。工厂入口：`std::unique_ptr<GeneratorFactory> MakeImmutableGeneratorFactory(Context* context);`（full）与 `std::unique_ptr<GeneratorFactory> MakeImmutableLiteGeneratorFactory(Context* context);`（lite）。共享代码由 SharedCodeGenerator（F-CMP-072）生成：`void Generate(GeneratorContext* generator_context, std::vector<std::string>* file_list, std::vector<std::string>* annotation_file_list);` 与 `void GenerateDescriptors(io::Printer* printer);`。命名解析集中在 `class PROTOC_EXPORT ClassNameResolver`（F-CMP-073）：`std::string GetFileClassName(const FileDescriptor* file, bool immutable);`（2 重载）、`std::string GetFileImmutableClassName(const FileDescriptor* file);`、`std::string GetDescriptorClassName(const FileDescriptor* file);`、`std::string GetClassName(const Descriptor*/const EnumDescriptor*/const ServiceDescriptor*/const FileDescriptor*, bool immutable);`、模板 `GetImmutableClassName(const DescriptorType*)`、`std::string GetExtensionIdentifierName(const FieldDescriptor*, ...);`。java/ 顶层共 17 个 .h，其中 context.h 定义 `class Context`（F-CMP-074）；java/ 顶层不存在 kotlin/ 子目录，Kotlin 生成器位于 compiler/kotlin/（F-CMP-070）。

## Python 与 pyi 生成器（python/）

`class PROTOC_EXPORT Generator : public CodeGenerator`（python/generator.h L56，F-CMP-075）：私有 `GeneratorOptions ParseParameter(absl::string_view parameter, std::string* error) const;`；选项结构（F-CMP-076）`struct GeneratorOptions { bool generate_pyi = false; bool annotate_pyi = false; bool bootstrap = false; bool strip_nonfunctional_codegen = false; };`。

`class PROTOC_EXPORT PyiGenerator : public google::protobuf::compiler::CodeGenerator`（F-CMP-077）负责 .pyi 类型存根生成。python/ 目录共 5 个 .h：python_generator.h、pyi_generator.h、names.h、helpers.h、generator.h（F-CMP-079）。

## C# 生成器（csharp/）

`class PROTOC_EXPORT Generator : public CodeGenerator`（csharp/csharp_generator.h L29，F-CMP-080）。字段生成基类 `class FieldGeneratorBase : public SourceGeneratorBase`（F-CMP-082）：纯虚方法 GenerateCloningCode(io::Printer*)、GenerateMembers(io::Printer*)、GenerateMergingCode(io::Printer*)、GenerateParsingCode(io::Printer*)、GenerateSerializationCode(io::Printer*)、GenerateSerializedSizeCode(io::Printer*)；虚方法 GenerateFreezingCode、GenerateCodecCode、GenerateExtensionCode 等。命名工具 csharp_helpers.h（F-CMP-081）：`std::string GetFieldName(const FieldDescriptor* descriptor);`、`std::string GetPropertyName(const FieldDescriptor* descriptor);`、`std::string StringToBase64(absl::string_view input);`、`std::string FileDescriptorToBase64(const FileDescriptor* descriptor);`。目录共 19 个 .h（F-CMP-083），含 c_sharp_features.pb.h。

## Objective-C、PHP、Ruby、Rust、Kotlin 生成器

`class PROTOC_EXPORT ObjectiveCGenerator final : public CodeGenerator`（F-CMP-084）：`bool GenerateAll(...) const override;` 亦有 override。

`class PROTOC_EXPORT Generator : public CodeGenerator`（php/php_generator.h，F-CMP-085）：目录仅 php_generator.h 与 names.h 两个头文件；文件级 `inline bool IsWrapperType(const FieldDescriptor* descriptor)`；私有 `bool Generate(const FileDescriptor* file, const Options& options, GeneratorContext* generator_context, std::string* error) const;` 重载。

Ruby 生成器（F-CMP-086）特色是文件级自由函数：`std::string GetRequireName(absl::string_view proto_file);`、`std::string PackageToModule(absl::string_view name);`、`std::string RubifyConstant(absl::string_view name);`、`bool IsValidRubyPackage(absl::string_view pkg, std::string* error);`、`int GeneratePackageModules(const FileDescriptor* file, io::Printer* printer);`、`void EndPackageModules(int levels, io::Printer* printer);`。

Rust 生成器（F-CMP-089）：`class RustGeneratorContext`（context.h L61）、`class Context`（context.h L89）、`class AccessorGenerator`（accessors/generator.h L26）及其 final 派生类 SingularScalar、SingularString、SingularCord、SingularMessage、RepeatedField、UnsupportedField、Map，及 `class MultiCasePrefixStripper final`、`class RelativePath final`。

Kotlin 生成器（F-CMP-090）：目录文件 generator.h、generator.cc、file.h、message.h、field.h。

## edition 支持矩阵

汇总各生成器的能力协商声明（均见对应事实）：

| 生成器 | GetSupportedFeatures | GetMinimumEdition | GetMaximumEdition |
|---|---|---|---|
| CppGenerator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| JavaGenerator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| python::Generator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| PyiGenerator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| csharp::Generator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| ObjectiveCGenerator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| php::Generator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| ruby::Generator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| RustGenerator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| KotlinGenerator | FEATURE_PROTO3_OPTIONAL \| FEATURE_SUPPORTS_EDITIONS | EDITION_PROTO2 | EDITION_2026 |
| RBSGenerator | FEATURE_PROTO3_OPTIONAL（仅此一项） | （无 override） | （无 override） |

除 RBSGenerator 外，全部生成器声明 GetMaximumEdition() = EDITION_2026、GetMinimumEdition() = EDITION_PROTO2，与编译器自身的 ProtocMinimumEdition()/ProtocMaximumEdition() 边界一致。RBSGenerator 是唯一的降级实例：只声明 FEATURE_PROTO3_OPTIONAL、不支持 editions，也没有 edition 区间 override（虚方法返回默认值 EDITION_UNKNOWN）。协商矩阵真实生效——protoc 的 EnforceEditionsSupport 会按生成器声明拒绝越界 edition 文件（见 [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md)与 [Editions 特性系统](/concepts/15-editions-feature-system.md)）。

## 生成器统一接口洞察

内置生成器与外部插件的关系可以概括为"同构"：两者共用 CodeGenerator::Generate 抽象与同一份 CodeGeneratorRequest/Response 协议；差异仅在于内置生成器在 main.cc 进程内通过 RegisterGenerator 注册，而插件通过 stdin/stdout 序列化协议通信（CommandLineInterface 中 GenerateBuiltInOutput 与 GeneratePluginOutput 是平行方法）。hpb_generator 的 `Generator : protoc::CodeGenerator`、Lua 的 `LuaGenerator : protoc::CodeGenerator`、Python 独立插件 plugin_main.cc 包装 `PluginMain(argc, argv, &generator)`——三者都是"用插件身份实现内置等价能力"的实例，详见[插件协议](/concepts/10-plugin-protocol.md)。

## 相关概念

- [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md) —— 生成器的注册与调用方
- [插件协议（plugin.proto）](/concepts/10-plugin-protocol.md) —— 外部插件的同构协议
- [Editions 特性系统](/concepts/15-editions-feature-system.md) —— edition 协商矩阵的机制背景
- [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md) —— 生成器的输入数据模型
