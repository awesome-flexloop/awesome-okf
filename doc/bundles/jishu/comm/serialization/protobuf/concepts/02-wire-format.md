---
type: Concept
title: "Wire Format 二进制编码"
description: "protobuf 线格式（Wire Format）的核心编码规则：WireType 六值枚举、tag 的字段编号与类型合体构成、varint 变长编码，以及 WireFormatLite/WireFormat 两层静态工具与 CodedStream、ZeroCopy 流族的完整 IO 栈。"
tags: [protobuf, wire-format, serialization, io]
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
---

线格式（Wire Format）是 protobuf 消息在线上的字节表示：`.proto` 声明只定义逻辑模式，真正跨进程、跨语言、跨版本传输的是这套极简的二进制编码。它的全部复杂度浓缩为三个原语——wire type（值怎么编码）、tag（这是哪个字段）、varint（变长整数）——以及围绕它们的一组静态工具与流式 IO 栈。本篇是入门组最后一篇，向上承接消息模型（`MessageLite::ParseFromString` 的底层实现，见 /concepts/01-message-model.md），向下为核心机制组（未知字段、反射、conformance）提供字节级词汇表。

## WireType：六种线格式类型

`wire_format_lite.h` 中的 `WireFormatLite::WireType` 枚举完整定义了六种编码类型（F-CPP-076）：

| 值 | 枚举名 | 语义 |
|---|---|---|
| 0 | `WIRETYPE_VARINT` | 变长整数（int32/int64/uint32/uint64/bool/enum） |
| 1 | `WIRETYPE_FIXED64` | 固定 8 字节（double/fixed64/sfixed64） |
| 2 | `WIRETYPE_LENGTH_DELIMITED` | 长度前缀字节串（string/bytes/嵌套 message/打包 repeated） |
| 3 | `WIRETYPE_START_GROUP` | group 开始（legacy） |
| 4 | `WIRETYPE_END_GROUP` | group 结束（legacy） |
| 5 | `WIRETYPE_FIXED32` | 固定 4 字节（float/fixed32/sfixed32） |

注意 group 类型（3/4）是 proto2 时代遗物，在现代 schema 中已被嵌套 message 取代，但线格式层面仍须完整保留解析能力——这正是未知字段机制要处理五种 wire type 的原因（见 /concepts/05-containers-extensions-unknown-fields.md）。

## Tag：字段编号与类型的合体

线格式不传输字段名，每个字段值前只有一个 tag：一个 32 位 varint，低 3 位是 wire type，其余位是字段编号。这套位运算由 `WireFormatLite` 的常量与函数直接编码（F-CPP-077 ~ F-CPP-079）：

```cpp
static constexpr int kTagTypeBits = 3;
static constexpr uint32_t kTagTypeMask = (1 << kTagTypeBits) - 1;

constexpr static uint32_t MakeTag(int field_number, WireType type);
static WireType GetTagWireType(uint32_t tag);
static int GetTagFieldNumber(uint32_t tag);
```

`MakeTag` 在序列化侧组装 tag，`GetTagWireType`/`GetTagFieldNumber` 在解析侧拆解。解码器看到未知 tag（不认识的字段编号）时据此判断该跳过多少字节，从而实现前向/后向兼容。

## Varint 编码与尺寸计算

varint 将整数按 7 位一组切分，每组最高位作为继续标志（小端序组序）。编码尺寸可在写出前静态计算（F-CPP-080）：

```cpp
static size_t VarintSize32(uint32_t value);
static size_t VarintSize64(uint64_t value);
```

这套尺寸计算是 protobuf"先算后写"序列化策略的基础——`ByteSizeLong` 遍历消息缓存总尺寸，随后序列化器按缓存尺寸一次性写出，避免缓冲区扩容。`CodedOutputStream` 上亦有同名的 `VarintSize32`/`VarintSize64` 静态方法（F-CPP-090）。

## WireFormatLite 与 WireFormat：两层静态工具

`WireFormatLite`（F-CPP-075）是可脱离完整描述符体系的底层工具：tag 位运算、varint 尺寸、类型编码等原语均在此定义，libprotobuf-lite 只依赖这一层。

完整层 `WireFormat`（`wire_format.h`，`WireFormat() = delete;`，仅静态方法，F-CPP-081）面向 `Message` 与 `FieldDescriptor`，提供描述符感知的编解码（F-CPP-082 ~ F-CPP-088）：

- 类型映射：`WireTypeForField(const FieldDescriptor* field)` 与 `WireTypeForFieldType(FieldDescriptor::Type type)`；
- 尺寸：`TagSize(int field_number, FieldDescriptor::Type type)`、`ByteSize(const Message& message)`；
- 解析：`ParseAndMergePartial(io::CodedInputStream* input, Message* message)` 与 `_InternalParse(Message* msg, const char* ptr, internal::ParseContext* ctx)`——后者是现代解析入口；
- 序列化：`SerializeWithCachedSizes(const Message& message, int size, io::CodedOutputStream* output)` 与 `_InternalSerialize(const Message& message, uint8_t* target, io::EpsCopyOutputStream* stream)`；
- 跳过：`SkipField(io::CodedInputStream* input, uint32_t tag, UnknownFieldSet* unknown_fields)` 与 `SkipMessage(...)`——遇到未知字段时"跳过并保留"的关键路径；
- 未知字段序列化：`SerializeUnknownFields(const UnknownFieldSet&, io::CodedOutputStream*)`、`SerializeUnknownFieldsToArray(...)`、`InternalSerializeUnknownFieldsToArray(...)`。

`WireFormatForFieldType` 是从 schema 类型到线格式的权威映射表——`FieldDescriptor::Type` 的 18 个标量类型（见 /concepts/03-descriptors-and-reflection.md）各自落到六种 wire type 之一。

## CodedInputStream 与 CodedOutputStream

`io/coded_stream.h` 提供线格式专用的编解码流（F-CPP-089 / F-CPP-090）。读取侧 `CodedInputStream`：

```cpp
bool ReadVarint32(uint32_t* value);
bool ReadVarint64(uint64_t* value);
bool ReadLittleEndian32(uint32_t* value);
bool ReadLittleEndian64(uint64_t* value);
Limit PushLimit(int byte_limit);
void PopLimit(Limit limit);
```

`PushLimit`/`PopLimit` 实现嵌套消息的边界追踪——进入 LENGTH_DELIMITED 子消息前压入字节上限，越界读取立即失败，这是防御恶意输入（如超长长度前缀）的第一道闸门。写入侧 `CodedOutputStream` 提供 `WriteVarint32`/`WriteVarint64`/`WriteLittleEndian32`/`WriteLittleEndian64` 与静态 `VarintSize32`/`VarintSize64`。

## ZeroCopy 流族：缓冲管理的抽象

`CodedStream` 之下是零拷贝流接口：`ZeroCopyInputStream`（纯虚：`Next(const void** data, int* size)`、`BackUp(int count)`、`Skip(int count)`、`ByteCount() const`，F-CPP-091）与 `ZeroCopyOutputStream`（纯虚：`Next(void** data, int* size)`、`BackUp(int count)`、`ByteCount() const`，F-CPP-092）——以"借出一块连续缓冲"代替"逐字节读"，让上层直接在原始缓冲上解析。

具体实现是 `io/zero_copy_stream_impl_lite.h` 的一族适配器（F-CPP-093）：

| 类 | 继承 | 用途 |
|---|---|---|
| `ArrayInputStream` / `ArrayOutputStream` | ZeroCopyIn/OutputStream | 直接包裸内存数组 |
| `StringOutputStream` | ZeroCopyOutputStream | 追加写入 std::string |
| `CopyingInputStream` + `CopyingInputStreamAdaptor` | ZeroCopyInputStream | 把传统逐字节流适配为零拷贝接口 |
| `CopyingOutputStream` + `CopyingOutputStreamAdaptor` | ZeroCopyOutputStream | 同上（写侧） |
| `LimitingInputStream` | ZeroCopyInputStream | 限定读取上限 |
| `CordInputStream` / `CordOutputStream` | ZeroCopyIn/OutputStream | absl::Cord 支持（配合 `ParseFromString(const absl::Cord&)`） |

`ZeroCopyOutputStream` 本身不拥有内存——这正是 `SerializeToString(std::string* output)`（F-CPP-006）与 `TextFormat::Print`（见 /concepts/06-text-format-and-json.md）共享的输出底座。

## 跨语言对照：GPBWireFormat

Objective-C 运行时把同一套编码规则原样复刻为函数族（F-RT-086）：`GPBWireFormatMakeTag`、`GPBWireFormatGetTagWireType`、`GPBWireFormatGetTagFieldNumber`、`GPBWireFormatIsValidTag`、`GPBWireFormatForType`（均 `__attribute__((const))`），另有 MessageSet 宏。命名与 `WireFormatLite` 逐一对应——线格式是各语言运行时必须逐字节一致的公共契约（conformance 测试即以二进制 roundtrip 校验之，见 /concepts/16-wkt-conformance-benchmarks.md）。

## 相关概念

- [/concepts/01-message-model.md](/concepts/01-message-model.md)——调用方视角的消息序列化接口。
- [/concepts/05-containers-extensions-unknown-fields.md](/concepts/05-containers-extensions-unknown-fields.md)——未知 wire type 的保留机制与打包 repeated 的容器语义。
- [/concepts/03-descriptors-and-reflection.md](/concepts/03-descriptors-and-reflection.md)——`FieldDescriptor::Type` 到 wire type 的映射来源。
- [/concepts/16-wkt-conformance-benchmarks.md](/concepts/16-wkt-conformance-benchmarks.md)——线格式跨语言一致性的一线验证。
