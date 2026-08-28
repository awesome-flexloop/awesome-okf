---
type: Concept
title: "文本格式与 JSON 序列化"
description: "protobuf 的两种人类可读序列化：TextFormat 文本协议与 DebugString 三态调试输出，json/ 目录的 MessageToJsonString/JsonStringToMessage 及其 ParseOptions/PrintOptions 选项体系，附 Ruby、Lua、conformance 的跨语言视角。"
tags: [protobuf, text-format, json, serialization]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: cpp-core
    resource: /references/cpp-core.md
    title: "protobuf C++ 运行时核心信源"
  - id: runtimes
    resource: /references/runtimes.md
    title: "protobuf 多语言运行时信源"
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
---

二进制线格式（见 /concepts/02-wire-format.md）为机器而设计；调试日志、人工检视与 Web 互操作则需要人类可读的表示。protobuf 内建两种：TextFormat（文本格式协议，`field: value` 行式语法）与 JSON（`json/` 目录实现的标准 JSON 映射）。两者共用同一套反射底座（见 /concepts/03-descriptors-and-reflection.md），共享 ZeroCopy 输出流抽象，但各有独立的解析器与选项体系。本篇是核心机制组收官之作，也是通往 conformance 一致性测试（16 篇）的必经概念——TextFormat 与 JSON 均有专门的 conformance 套件。

## TextFormat：文本协议

`text_format.h` 的 `TextFormat` 提供静态四入口（F-CPP-094）：

```cpp
static bool Print(const Message& message, io::ZeroCopyOutputStream* output);
static bool PrintToString(const Message& message, std::string* output);
static bool Parse(io::ZeroCopyInputStream* input, Message* output);
static bool ParseFromString(absl::string_view input, Message* output);
```

Print 与 Parse 共用 ZeroCopy 流族（`StringOutputStream`、`ArrayInputStream` 等，见 02 篇），打印输出走反射遍历字段。

需要定制行为时用两个嵌套类（F-CPP-095）：

- `class PROTOBUF_EXPORT Printer`：`void SetUseShortRepeatedPrimitives(bool use_short)`（把 repeated 标量压成一行 `[1, 2, 3]`）与 `bool PrintToString(const Message& message, std::string* output) const`；
- `class PROTOBUF_EXPORT Parser`：`void AllowPartialMessage(bool allow)`（放宽完整性校验）与 `bool ParseFromCodedStream(io::CodedInputStream* input, Message* output)`。

## DebugString 三态

`Message` 基类自带三个文本输出口（F-CPP-010）：

```cpp
[[nodiscard]] std::string DebugString() const;
[[nodiscard]] std::string ShortDebugString() const;
[[nodiscard]] std::string Utf8DebugString() const;
```

`DebugString` 是标准多行文本格式；`ShortDebugString` 等价于开启 `SetUseShortRepeatedPrimitives` 的紧凑输出；`Utf8DebugString` 保持 UTF-8 字面量而非转义——三态覆盖"日志粘贴、diff 对比、国际化检视"三类场景。实现即 TextFormat Printer 的三种预设（见 /concepts/01-message-model.md 的 Message 接口层）。

## JSON：入口与选项体系

JSON 实现位于 `src/google/protobuf/json/`，公开入口是 `json/json.h` 的两个函数（F-CPP-097）：

```cpp
absl::Status MessageToJsonString(const Message& message, std::string* output, const PrintOptions& options);
absl::Status JsonStringToMessage(absl::string_view input, Message* message, const ParseOptions& options);
```

以 `absl::Status` 报错是这套 API 的显著风格。选项结构体（F-CPP-096）：

```cpp
struct ParseOptions {
  bool ignore_unknown_fields = false;
  bool case_insensitive_enum_parsing = false;
};

struct PrintOptions {
  bool add_whitespace = false;
  bool always_print_fields_with_no_presence = false;
  bool always_print_enums_as_ints = false;
  bool preserve_proto_field_names = false;
};
```

四个打印开关分别控制：格式化换行、无 presence 语义字段强制输出（proto3 的隐式默认值）、枚举转数字、保留 proto 原始字段名（默认会转 lowerCamelCase）。旧入口 `util/json_util.h` 与 `json/json.h` 并存（F-CPP-099）——前者是历史兼容层，新代码应走后者。

### json/ 目录的内部结构

`json/` 的实现分两层（F-CPP-098）：顶层 `json.cc`/`json.h` 为薄入口；`internal/` 子目录是引擎，文件按职责切分：

- **lexer**（`lexer.cc/h`、`lexer_test.cc`）——JSON 词法分析；
- **parser**（`parser.cc/h`、`parser_traits.h`、`descriptor_traits.h`）——JSON 到消息的解析；`parser_traits.h`/`descriptor_traits.h` 是描述符访问的 trait 抽象，使解析器可适配不同描述符体系；
- **unparser**（`unparser.cc/h`、`unparser_traits.h`）——消息到 JSON 的反向生成（"unparse"命名刻意对应）；
- **writer**（`writer.cc/h`）——输出写侧；
- **message_path**（`message_path.cc/h`）——错误定位的字段路径；
- **untyped_message**（`untyped_message.cc/h`）——无 schema 的中间表示；
- **zero_copy_buffered_stream**（含自测）——流式缓冲底座；
- 顶层 `json_test.cc` 收束测试。

这套"lexer/parser/unparser/writer"分层与 TextFormat 的 Printer/Parser 划分互为镜像。

## 跨语言入口

**Ruby**：`ruby/lib/google/protobuf.rb` 在 `module Google` 下定义 `def self.encode_json(msg, options = {})` 与 `def self.decode_json(klass, json, options = {})`（同文件还有 `encode`/`decode` 二进制对，F-RT-094）——顶层方法式的 API 风格。

**Lua**：`lua/msg.c` 定义静态函数族 `lupb_jsondecode`、`lupb_jsonencode`、`lupb_textencode`（同族还有二进制的 `lupb_Encode`/`lupb_decode` 与 tostring，F-RT-102）——三种序列化形态（二进制/JSON/文本）在同一文件平铺展开。

**conformance 视角**：`conformance/testee.h` 定义测试侧的选项结构（F-TST-011）：

```cpp
struct TextSerializationOptions { bool print_unknown_fields = false; };
struct JsonParseOptions { bool ignore_unknown_fields = false; };
```

TextFormat 的 conformance 特别关注"未知字段是否打印"这一跨实现分歧点；JSON 侧则聚焦未知字段容忍度——与 C++ ParseOptions 的 `ignore_unknown_fields` 同名同义，说明这是全语言必须对齐的行为开关。详见 /concepts/16-wkt-conformance-benchmarks.md。

## 相关概念

- [/concepts/02-wire-format.md](/concepts/02-wire-format.md)——二进制与文本两种编码形态的分界。
- [/concepts/03-descriptors-and-reflection.md](/concepts/03-descriptors-and-reflection.md)——文本/JSON 遍历字段所依赖的反射矩阵。
- [/concepts/11-python-runtime.md](/concepts/11-python-runtime.md)——Python 侧 JSON 与 TextFormat 的实现路径。
- [/concepts/16-wkt-conformance-benchmarks.md](/concepts/16-wkt-conformance-benchmarks.md)——TextFormat 与 JSON 的一致性套件及 failure list 机制。
