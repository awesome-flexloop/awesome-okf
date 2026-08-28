---
type: Concept
title: "插件协议（plugin.proto）"
description: "protoc 插件的 stdin/stdout 协议：CodeGeneratorRequest/Response 完整字段表、PluginMain 插件进程骨架、protoc-gen-* 命名规则，及 hpb_generator 与 Lua upbc 插件实例。"
tags: [protobuf, plugin, codegen]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: compiler
    resource: /references/compiler.md
    title: "protoc 编译器信源"
  - id: runtimes
    resource: /references/runtimes.md
    title: "protobuf 多语言运行时信源"
---

protoc 的语言扩展能力对第三方完全开放：任何程序只要实现"从 stdin 读入 CodeGeneratorRequest、向 stdout 写出 CodeGeneratorResponse"这一协议，就能以插件（plugin）身份获得与内置生成器完全相同的输入与协商机制。协议本身定义在 plugin.proto 中——用 protobuf 描述 protobuf 的又一实例（见 [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md)）。本篇逐字段解析协议载荷、插件进程骨架与两个完整的插件实例。

## plugin.proto 文件头

plugin.proto 的声明（F-CMP-047）：

```protobuf
syntax = "proto2";
package google.protobuf.compiler;
option java_package = "com.google.protobuf.compiler";
option java_outer_classname = "PluginProtos";
import "google/protobuf/descriptor.proto";
option csharp_namespace = "Google.Protobuf.Compiler";
option go_package = "google.golang.org/protobuf/types/pluginpb";
```

它导入 descriptor.proto——插件请求的载荷主体就是 FileDescriptorProto。

## CodeGeneratorRequest：请求字段表

CodeGeneratorRequest 完整字段（F-CMP-049 逐字段照录）：

```protobuf
repeated string file_to_generate = 1;
optional string parameter = 2;
repeated FileDescriptorProto proto_file = 15;
repeated FileDescriptorProto source_file_descriptors = 17;
optional Version compiler_version = 3;
```

- `file_to_generate`：命令行上显式列出的待生成文件名；
- `parameter`：`--xxx_out` 冒号后的参数串；
- `proto_file`：待生成文件及其全部依赖的 FileDescriptorProto（含解析后的 descriptor 数据）；
- `source_file_descriptors`：源文件形态的 descriptor（保留源码层信息）；
- `compiler_version`：protoc 版本，结构为 Version message（F-CMP-048）：

```protobuf
optional int32 major = 1;
optional int32 minor = 2;
optional int32 patch = 3;
optional string suffix = 4;
```

插件与内置生成器在此同构：protoc 侧由 `CreateCodeGeneratorRequest` 组装同一份请求（见 [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md)）。

## CodeGeneratorResponse：响应字段表

CodeGeneratorResponse 完整字段（F-CMP-050 逐字段照录）：

```protobuf
optional string error = 1;
optional uint64 supported_features = 2;
optional int32 minimum_edition = 3;
optional int32 maximum_edition = 4;
repeated File file = 15;
```

嵌套 `enum Feature { FEATURE_NONE = 0; FEATURE_PROTO3_OPTIONAL = 1; FEATURE_SUPPORTS_EDITIONS = 2; }`——与 CodeGenerator::Feature 枚举 "must be kept in sync"（见 [代码生成器体系](/concepts/09-code-generators.md)）。能力协商字段 supported_features/minimum_edition/maximum_edition 让插件声明与内置生成器等价的能力矩阵。

每个输出文件由 CodeGeneratorResponse.File 描述（F-CMP-051 逐字段照录）：

```protobuf
optional string name = 1;
optional string insertion_point = 2;
optional string content = 15;
optional GeneratedCodeInfo generated_code_info = 16;
```

- `name`：输出文件名；
- `insertion_point`：向既有文件插入点追加内容的锚点；
- `content`：文件内容；
- `generated_code_info`：生成代码注解（标注哪些代码段对应哪些源字段）。

## 生成代码 plugin.pb.h

plugin.pb.h 由 protoc 自举生成四个消息类（均 `final : public ::google::protobuf::Message`，F-CMP-052）：`Version`、`CodeGeneratorResponse_File`、`CodeGeneratorResponse`、`CodeGeneratorRequest`；字段号常量与 plugin.proto 一致，如 CodeGeneratorRequest 的 `kFileToGenerateFieldNumber = 1`、`kProtoFileFieldNumber = 15`、`kParameterFieldNumber = 2`、`kCompilerVersionFieldNumber = 3`、`kSourceFileDescriptorsFieldNumber = 17`；CodeGeneratorResponse 的 `kFileFieldNumber = 15`、`kErrorFieldNumber = 1`、`kSupportedFeaturesFieldNumber = 2`、`kMinimumEditionFieldNumber = 3`、`kMaximumEditionFieldNumber = 4`；CodeGeneratorResponse_File 的 `kNameFieldNumber = 1`、`kInsertionPointFieldNumber = 2`、`kContentFieldNumber = 15`、`kGeneratedCodeInfoFieldNumber = 16`；Version 的 `kMajorFieldNumber = 1`、`kMinorFieldNumber = 2`、`kPatchFieldNumber = 3`、`kSuffixFieldNumber = 4`。

访问器示例（F-CMP-053 抄录）：CodeGeneratorResponse 的 `[[nodiscard]] ::uint64_t supported_features() const;` 与 `[[nodiscard]] ::int32_t minimum_edition() const;`；CodeGeneratorResponse_File 的 `[[nodiscard]] bool has_insertion_point() const;`、`[[nodiscard]] const ::std::string& insertion_point() const;`、`::std::string* PROTOBUF_NONNULL mutable_insertion_point();`、`[[nodiscard]] const ::google::protobuf::GeneratedCodeInfo& generated_code_info() const;`。

## PluginMain 与 GenerateCode：插件进程骨架

plugin.h 导出两个函数（F-CMP-054）：

```cpp
PROTOC_EXPORT int PluginMain(int argc, char* argv[], const CodeGenerator* generator);
bool GenerateCode(const CodeGeneratorRequest& request, const CodeGenerator& generator,
                  CodeGeneratorResponse* response, std::string* error_msg);
```

实现位于 plugin.cc（`GenerateCode` 于 L99、`PluginMain` 于 L161，F-CMP-055）。PluginMain 封装了完整的插件生命周期：从 stdin 反序列化 CodeGeneratorRequest、调用 GenerateCode 驱动传入的 CodeGenerator、把 CodeGeneratorResponse 序列化到 stdout。写一个新语言插件因此只需实现一个 CodeGenerator 子类并把它交给 PluginMain。

## 插件的发现与解析

插件可执行文件命名规则（F-CMP-008）：exe_name_prefix + flag 名去掉 "_out"，如前缀 "protoc-" 加 `--foo_out` 对应程序 "protoc-gen-foo"。

`--plugin` flag 显式指定路径（F-CMP-016）：按第一个 `=` 拆分为 plugin_name 与 path；无 `=` 时取路径 basename 作为 plugin_name；结果写入 `plugins_[plugin_name] = path;`。插件在命令行层面与内置生成器同构——OutputDirective 对插件 generator 为 NULL，但两者拿到完全相同的 FileDescriptorProto 输入与 feature 协商机制（见 [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md)）。

## 以插件身份实现的实例

### Python 独立插件

python/plugin_main.cc 全文主体（F-CMP-078）：

```cpp
int main(int argc, char *argv[]) {
  ::google::protobuf::compiler::python::Generator generator;
  ...
  return ::google::protobuf::compiler::PluginMain(argc, argv, &generator);
}
```

（`#ifdef GOOGLE_PROTOBUF_RUNTIME_INCLUDE_BASE` 分支调用 `generator.set_opensource_runtime(true)` 与 `generator.set_runtime_include_base(...)`）——用插件进程包装与内置 `--python_out` 等价的生成器。

### hpb_generator

hpb_generator/ 目录（F-RT-065）含 generator.h/.cc、protoc-gen-hpb.cc、context.h、gen_accessors.h/.cc、gen_enums.h/.cc、gen_extensions.h/.cc、gen_messages.h/.cc、gen_repeated_fields.h/.cc、gen_utils.h/.cc、keywords.h/.cc、names.h/.cc 与 tests/。generator.h 在 `namespace google::protobuf::hpb_generator` 下声明 `class Generator : public protoc::CodeGenerator`（`namespace protoc = ::google::protobuf::compiler`，F-RT-066）；context.h 定义 `struct Options` 与 `class Context final`（F-RT-067）。generator.cc 使用 `GeneratedCodeInfo` 与 `io::AnnotationProtoCollector<GeneratedCodeInfo>` 处理注解（F-RT-068）——即 CodeGeneratorResponse.File.generated_code_info 字段的生产侧。tests/ 含 basic_test_editions.proto、test_model.proto、test_extension.proto 等测试 proto 与 multibackend_test.cc、extension_test.cc、repeated_test.cc、metadata_test.cc、test_generated.cc 等测试源文件（F-RT-069）。hpb 运行时本体见 [hpb：C++ 多后端 API 层与 hpb_generator](/concepts/13-hpb.md)。

### Lua upbc

lua/upbc.cc 声明 `namespace protoc = ::google::protobuf::compiler;`、`namespace protobuf = ::google::protobuf;`、`class LuaGenerator : public protoc::CodeGenerator`（L20）与 `int main(int argc, char** argv)`（L119）（F-RT-104）——Lua 代码生成同样以插件身份实现。

## 相关概念

- [代码生成器体系与各语言实现](/concepts/09-code-generators.md) —— 与插件同构的内置生成器接口
- [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md) —— 插件的发现与调用方
- [hpb：C++ 多后端 API 层与 hpb_generator](/concepts/13-hpb.md) —— 插件实例的运行时侧
- [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md) —— 协议载荷的数据模型
