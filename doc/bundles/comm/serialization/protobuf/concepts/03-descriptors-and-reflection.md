---
type: Concept
title: "Descriptor 体系与运行时反射"
description: "protobuf 用 protobuf 描述 protobuf 的自举设计：八类 Descriptor 描述 schema 全貌，Reflection 提供字段级读写矩阵，DescriptorPool/DescriptorDatabase 支撑动态构建——descriptor 是贯穿编译、生成、反射、传输的单一事实源。"
tags: [protobuf, reflection, descriptor, runtime]
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

反射（Reflection）能力是 `Message` 区别于 `MessageLite` 的本质（见 /concepts/01-message-model.md），而它的根基是一套用 protobuf 自身定义的元数据体系：descriptor（描述符）。本束最重要的架构洞察在此成立——**descriptor 是贯穿全生命周期的单一事实源**：编译器把 `.proto` 源码解析进 `FileDescriptorProto`；插件协议以 `repeated FileDescriptorProto` 为载荷把 schema 发给外部生成器；运行时反射从序列化的 descriptor 数据构建 `DescriptorPool`；跨进程传 schema 时它又化身 descriptor set 文件。protobuf 用 protobuf 描述 protobuf，完成自举——`descriptor.pb.h` 本身就是 protobuf 自己生成的代码，"生成器先吃自己的狗粮"。本篇是核心机制组的枢纽：编译器组（07-10 篇）与运行时组（11-14 篇）在 schema 流转处都将回链到这里。

## descriptor.proto：自举的元数据模式

`descriptor.proto` 定义了 schema 世界的"元语言"，顶层共 23 个 message（F-CPP-066），按行号顺序包括：`FileDescriptorSet(33)`、`FileDescriptorProto(85)`、`DescriptorProto(132)`、`ExtensionRangeOptions(169)`、`FieldDescriptorProto(227)`、`OneofDescriptorProto(334)`、`EnumDescriptorProto(340)`、`EnumValueDescriptorProto(372)`、`ServiceDescriptorProto(380)`、`MethodDescriptorProto(391)`、各层 Options（`FileOptions(439)`、`MessageOptions(593)`、`FieldOptions(682)` 等）、`UninterpretedOption(1029)`、`FeatureSet(1060)`、`FeatureSetDefaults(1297)`、`SourceCodeInfo(1330)`、`GeneratedCodeInfo(1507)`。

每个 `message`/`field`/`enum` 声明都能在其中找到对应的 Proto 类型：`DescriptorProto` 描述消息，`FieldDescriptorProto` 描述字段，`FeatureSet` 描述 Editions 特性（见 /concepts/15-editions-feature-system.md）。运行时 C++ 侧的描述符类（`Descriptor` 等）正是这些 Proto 的内存化镜像。

## 八类 Descriptor

`descriptor.h` 提供八个描述符类，全部 `private internal::SymbolBase`（或其模板变体）继承，构成 schema 的静态视图：

- **`FileDescriptor`**（F-CPP-054）——proto 文件级：包名、依赖、edition 等；私有成员 `Edition edition()` 的注释明言旧语法用特殊值表示："For legacy proto2/proto3 files, special EDITION_PROTO2 and EDITION_PROTO3 values are used"；`features()` 返回合并后的 `const FeatureSet&`（`*merged_features_`）。
- **`Descriptor`**（F-CPP-042 ~ F-CPP-044）——消息级：`name()`/`full_name()`/`file()` 返回 `absl::string_view` 或指针；字段访问有 `field_count()`、`field(int index)`、`FindFieldByName(absl::string_view name)`、`FindFieldByNumber(int number)`——按名与按编号双索引。
- **`FieldDescriptor`**（F-CPP-045）——字段级，双重继承 `internal::SymbolBase` 与 `internal::FieldDescriptorLite`（后者来自 `descriptor_lite.h`，见 01 篇）。
- **`OneofDescriptor`**（F-CPP-049）——oneof 组。
- **`EnumDescriptor`**（F-CPP-050）与 **`EnumValueDescriptor`**（F-CPP-051）——枚举与枚举值。
- **`ServiceDescriptor`**（F-CPP-052）与 **`MethodDescriptor`**（F-CPP-053）——服务与方法（RPC 契约）。

### FieldDescriptor 的 Type 与 Label

字段的类型系统由两个枚举完整定义（F-CPP-046 / F-CPP-047）。`FieldDescriptor::Type` 共 18 值：

```
TYPE_DOUBLE=1, TYPE_FLOAT=2, TYPE_INT64=3, TYPE_UINT64=4, TYPE_INT32=5,
TYPE_FIXED64=6, TYPE_FIXED32=7, TYPE_BOOL=8, TYPE_STRING=9, TYPE_GROUP=10,
TYPE_MESSAGE=11, TYPE_BYTES=12, TYPE_UINT32=13, TYPE_ENUM=14, TYPE_SFIXED32=15,
TYPE_SFIXED64=16, TYPE_SINT32=17, TYPE_SINT64=18, MAX_TYPE=18
```

`FieldDescriptor::Label` 三值：`LABEL_OPTIONAL=1, LABEL_REQUIRED=2, LABEL_REPEATED=3, MAX_LABEL=3`。常用判定方法（F-CPP-048）：`type()`、`label()`、`is_required()`、`is_repeated()`、`message_type()`（返回 `const Descriptor*`）、`enum_type()`（返回 `const EnumDescriptor*`）。Type 枚举值即线格式映射的输入端（见 /concepts/02-wire-format.md）。

## Reflection：字段级读写全矩阵

`Reflection` 是 `final` 类（`class PROTOBUF_EXPORT Reflection final`，F-CPP-013），一个实例服务于一种消息类型，方法按字段描述符操作任意实例——动态与静态世界的翻译官。其方法矩阵（F-CPP-014 ~ F-CPP-035）覆盖六类操作：

**未知字段**：`GetUnknownFields(const Message&)` / `MutableUnknownFields(Message*)`（F-CPP-014 / F-CPP-015）；`SpaceUsedLong(const Message&)` 估算内存占用（F-CPP-016）。

**字段生命周期**：`HasField` / `FieldSize` / `ClearField`（F-CPP-017）、`ListFields`（枚举全部已设字段，F-CPP-018）。

**标量 getter/setter**：按类型成对出现——`GetInt32`/`SetInt32` 及 Int64/UInt32/UInt64/Float/Double/Bool 各组（F-CPP-019 / F-CPP-025）；枚举的 `SetEnum(const EnumValueDescriptor*)` 与 `SetEnumValue(int)`（F-CPP-027）。

**字符串三形态**：`GetString`（拷贝，F-CPP-020）、`GetStringReference(..., std::string* scratch)`（引用，F-CPP-021）、`GetCord`（F-CPP-022）、`GetStringView(..., ScratchSpace& scratch)`（F-CPP-023）——嵌套类 `ScratchSpace` 提供 `absl::string_view CopyFromCord(const absl::Cord&)`（F-CPP-024），是临时存储的统一缓冲。写侧 `SetString` 有 `std::string` 与 `const absl::Cord&` 两个重载（F-CPP-026）。

**嵌套消息**：`GetMessage(const Message&, const FieldDescriptor*, MessageFactory* factory = nullptr)`（F-CPP-028）、`MutableMessage`（F-CPP-029）、`SetAllocatedMessage`（接管所有权，F-CPP-030）、`ReleaseMessage` 与 `UnsafeArenaReleaseMessage`（释放所有权，后者用于 Arena 场景，见 /concepts/04-arena-memory-management.md，F-CPP-031）。

**repeated 与 oneof**：`GetRepeatedInt32(const Message&, const FieldDescriptor*, int index)` 及同族（F-CPP-032）；`RemoveLast` / `ReleaseLast`（F-CPP-035）；oneof 三件套 `HasOneof` / `ClearOneof` / `GetOneofFieldDescriptor`（F-CPP-033）——oneof 的"哪个分支被设置"以字段描述符形式查询。

**交换**：`Swap`（整消息）、`SwapFields`（指定字段集）、`SwapElements`（repeated 元素，F-CPP-034）。

这套矩阵的偏移量来源即 01 篇的 `ReflectionSchema`——反射方法把 `FieldDescriptor` 翻译成 `GetFieldOffset` 得到的内存偏移后直接读写。

## DescriptorPool：构建与查找

描述符不散落存在，而是收拢进 `DescriptorPool`（F-CPP-057）。入口 `BuildFile`（F-CPP-060）：

```cpp
const FileDescriptor* BuildFile(const FileDescriptorProto& proto);
```

接收序列化的 `FileDescriptorProto`，校验并物化为池内 `FileDescriptor` 及其符号表。查找侧：`FindFileByName(absl::string_view filename)` 与 `FindFileContainingSymbol(absl::string_view symbol_name)`（F-CPP-059）。

两个关键静态方法划出池的边界：`generated_pool()`（F-CPP-058）是全进程共享的"生成代码池"——每个 `.pb.cc` 文件在静态初始化时把自己的 descriptor 数据 `BuildFile` 进去；`internal_generated_pool()`（F-CPP-062）供内部使用。池还支持惰性回填：私有方法 `TryFindFileInFallbackDatabase(...)` / `TryFindSymbolInFallbackDatabase(...)` / `TryFindExtensionInFallbackDatabase(...)`（F-CPP-061）在查找未命中时向 fallback database 求援。

## DescriptorDatabase：外部 schema 源

`DescriptorDatabase` 是池的供血抽象（抽象基类，F-CPP-069），三个纯虚方法（F-CPP-070 ~ F-CPP-072）：

```cpp
virtual bool FindFileByName(absl::string_view filename, FileDescriptorProto* output) = 0;
virtual bool FindFileContainingSymbol(absl::string_view symbol_name, FileDescriptorProto* output) = 0;
virtual bool FindFileContainingExtension(absl::string_view containing_type, int field_number, FileDescriptorProto* output) = 0;
```

实现族（前向声明见 F-CPP-074）：`SimpleDescriptorDatabase` 提供 `Add(const FileDescriptorProto& file)` / `AddAndOwn(...)` / `AddUnowned(...)` 三种收录方式（F-CPP-073）；`EncodedDescriptorDatabase` 存编码字节；`MergedDescriptorDatabase` 合并多个库。编译器的 Importer 体系正是通过把磁盘上的 `.proto` 解析成 `FileDescriptorProto` 后喂入池——这条链的完整展开见 /concepts/08-parser-and-importer.md。

## 多语言反射绑定对照

descriptor 单一事实源的跨语言印证（本束洞察 1 与洞察 2 的交汇）：

- **Python**（upb C 扩展）：C API 按 8 值枚举 `PyUpb_DescriptorType`（`kPyUpb_Descriptor`、`kPyUpb_EnumDescriptor`、`kPyUpb_EnumValueDescriptor`、`kPyUpb_FieldDescriptor`、`kPyUpb_FileDescriptor`、`kPyUpb_MethodDescriptor`、`kPyUpb_OneofDescriptor`、`kPyUpb_ServiceDescriptor`，F-RT-011）暴露 `PyUpb_Descriptor_Get`/`PyUpb_FieldDescriptor_Get`/`PyUpb_FileDescriptor_Get` 等函数（F-RT-010）；`PyUpb_Descriptor_Spec` 的 getters 覆盖 `name`、`full_name`、`file`、`fields`、`fields_by_name`、`nested_types`、`extensions`、`enum_types`、`oneofs`、`containing_type`、`is_extendable`（F-RT-012）——与 C++ Descriptor 的访问面同构。池侧 `PyUpb_DescriptorPool_Methods` 含 `Add`、`AddSerializedFile`、`FindFileByName`、`FindMessageTypeByName`、`FindExtensionByName`、`FindAllExtensions` 等（F-RT-013），回填走 `TryLoadFileProto/TryLoadSymbol/TryLoadExtension`（F-RT-014）。运行时细节见 /concepts/11-python-runtime.md。
- **Objective-C**：`GPBDescriptor.h` 声明 `GPBDescriptor : NSObject<NSCopying>` 及 `GPBFileDescriptor`、`GPBOneofDescriptor`、`GPBFieldDescriptor`、`GPBEnumDescriptor`、`GPBExtensionDescriptor` 家族（F-RT-083）。

## 相关概念

- [/concepts/01-message-model.md](/concepts/01-message-model.md)——`GetDescriptor`/`GetReflection` 入口与 ReflectionSchema 偏移机制。
- [/concepts/05-containers-extensions-unknown-fields.md](/concepts/05-containers-extensions-unknown-fields.md)——反射矩阵背后的容器与扩展载体。
- [/concepts/08-parser-and-importer.md](/concepts/08-parser-and-importer.md)——descriptor 数据在编译器侧的诞生过程。
- [/concepts/10-plugin-protocol.md](/concepts/10-plugin-protocol.md)——FileDescriptorProto 作为插件协议载荷的流转。
