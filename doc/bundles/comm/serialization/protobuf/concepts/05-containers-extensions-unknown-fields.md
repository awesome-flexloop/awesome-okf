---
type: Concept
title: "容器、扩展与未知字段"
description: "Map 与 RepeatedField/RepeatedPtrField 的容器语义，ExtensionSet 的扩展注册与读写体系，UnknownFieldSet 对五种 wire 类型的未知字段保留机制，及 Python、Rust、Objective-C 三语言的容器族对照。"
tags: [protobuf, containers, extensions, unknown-fields]
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

消息的字段语义只有三种（`LABEL_OPTIONAL`/`LABEL_REQUIRED`/`LABEL_REPEATED`，见 /concepts/03-descriptors-and-reflection.md），但数据形态远比三种丰富：map 字段、repeated 标量、repeated 消息、proto2 扩展（extension）、以及解析器遇到却不认识的未知字段。这五类"非单值"数据各有专门的运行时容器，且都被反射矩阵（`GetRepeatedInt32` 等）与反射偏移体系（`HasExtensionSet`，见 01 篇）引用。本篇属核心机制组，把这些容器一次讲清，并以 Python、Rust、Objective-C 三语言的对应容器族收尾——印证"容器语义跨内核一致、实现随语言定制"。

## Map 容器

`map.h` 的 `Map` 是模板容器（`class PROTOBUF_FUTURE_ADD_WARN_UNUSED Map final : private internal::KeyMapBase<internal::KeyForBase<Key>>`，F-CPP-100），接口刻意贴近 std::map（F-CPP-101）：

```cpp
T& operator[](const key_arg<K>& key);
iterator begin();  iterator end();
size_type size() const;  bool empty() const;
std::pair<iterator, bool> insert(const value_type& value);
iterator find(const key_arg<K>& key);
size_type erase(const key_arg<K>& key);
void clear();
```

在 wire format 上 map 编码为重复的 LENGTH_DELIMITED 键值对消息（见 /concepts/02-wire-format.md），`Map` 容器是该编码的内存投影。注意它 `final` 且私有继承 `KeyMapBase`——实现内嵌于消息布局而非独立分配。

## RepeatedField 与 RepeatedPtrField

标量 repeated 字段落到 `repeated_field.h` 的 `RepeatedField`（`class ABSL_ATTRIBUTE_WARN_UNUSED RepeatedField final : private internal::RepeatedFieldBase`，F-CPP-102），成员（F-CPP-103）：

```cpp
int size() const;  bool empty() const;
const_reference Get(int index) const;  pointer Mutable(int index);
void Add(Element value);  void Add(const Element* begin, const Element* end);
void RemoveLast();  void Clear();
void Reserve(int new_size);  void Truncate(int new_size);
```

`Reserve`/`Truncate` 暴露了底层连续数组的管理面；区间 `Add` 支持批量插入。消息与字符串的 repeated 字段则用 `RepeatedPtrField`（模板容器，F-CPP-104）——元素是指针，涉及 Arena 上的分配与共享，语义在"容器"之外叠加了所有权维度（见 /concepts/04-arena-memory-management.md）。

## ExtensionSet：扩展的注册与读写

proto2 的扩展（extension）允许在不修改原消息定义的情况下附加字段——`extendee` 消息体内嵌一个 `ExtensionSet`（`class PROTOBUF_EXPORT ExtensionSet`，含 `constexpr ExtensionSet() = default` 与 `ExtensionSet(const ExtensionSet& rhs) = delete`，F-CPP-108）。其头文件的前向声明清单（F-CPP-143）几乎是一部运行时核心类型索引：`Arena`、`Descriptor`、`FieldDescriptor`、`DescriptorPool`、`MessageLite`、`Message`、`MessageFactory`、`Reflection`、`UnknownFieldSet`、`FeatureSet`——扩展体系横跨所有机制。`generated_message_reflection.h` 亦在 internal 命名空间声明 `class ExtensionSet;`（F-CPP-142），衔接反射。

**注册**（静态方法，F-CPP-109）：

```cpp
static void RegisterExtension(const ClassData* extendee, int number,
    FieldType type, bool is_repeated, bool is_packed, bool is_utf8 = false);
static void RegisterEnumExtension(const ClassData* extendee, int number,
    FieldType type, bool is_repeated, bool is_packed, const uint32_t* validation_data);
static void RegisterMessageExtension(const ClassData* extendee, int number,
    FieldType type, bool is_repeated, bool is_packed,
    const ClassData* inner_data, LazyEagerVerifyFnType verify_func,
    LazyAnnotation is_lazy);
```

生成代码在静态初始化时把扩展注册进全局表（`FieldType` 是 `typedef uint8_t`，F-CPP-118）。**读写**（F-CPP-110 / F-CPP-111）：

```cpp
bool Has(int number) const;
int ExtensionSize(int number) const;
int NumExtensions() const;
FieldType ExtensionType(int number) const;
void ClearExtension(int number);

template <typename T> const T& Get(int number, const internal::type_identity_t<T>& default_value) const;
template <typename T, typename U> void Set(Arena* arena, int number, FieldType type, U&& value, const FieldDescriptor* descriptor);
```

消息型扩展经 `GetMessageByClassData(Arena*, int number, const ClassData*)` 或 `GetMessage(Arena*, int number, const Descriptor* message_type, MessageFactory* factory)` 读取（F-CPP-112）；`AppendToList(const Descriptor* extendee, const DescriptorPool* pool, std::vector<const FieldDescriptor*>* output)` 把已设置的扩展枚举给反射的 `ListFields`（F-CPP-113）。

**查找**由两个 finder 承担：`GeneratedExtensionFinder`（构造 `explicit GeneratedExtensionFinder(const MessageLite* extendee)`，查生成代码注册表）与 `DescriptorPoolExtensionFinder`（构造 `(const DescriptorPool* pool, MessageFactory* factory, const Descriptor* extendee)`，查描述符池）——都以 `bool Find(int number, ExtensionInfo* output)` 为接口（F-CPP-115 / F-CPP-116）。`ExtensionInfo` 结构体（F-CPP-114）是扩展的完整元数据包：`const MessageLite* message`、`int number`、`FieldType type`、`bool is_repeated`、`bool is_packed : 1`、`bool is_utf8 : 1`、`LazyAnnotation is_lazy`、`const FieldDescriptor* descriptor`、`LazyEagerVerifyFnType lazy_eager_verify_func`。

### LazyAnnotation：懒/急解析标注

```cpp
enum class LazyAnnotation : int8_t { kUndefined = 0, kLazy = 1, kEager = 2 };
```

（F-CPP-117）消息型扩展可标注为懒解析（kLazy）——字节在首次访问前不解码为子消息；kEager 强制立即解析；kUndefined 交由运行时默认策略。这与 01 篇的 `kLazyOffsetTag` 偏移标记、ArenaStringPtr 的惰性物化同属"按需解码"设计谱系。

## UnknownFieldSet：未知字段的五种形态

前向/后向兼容的基石：解析器遇到 schema 中不存在的字段编号时，调用 `WireFormat::SkipField`（见 02 篇）把原始字节转入 `UnknownFieldSet` 原样保留，序列化时再原样写回。`UnknownField` 的类型枚举恰是 wire type 的镜像（F-CPP-105）：

```cpp
enum Type { TYPE_VARINT, TYPE_FIXED32, TYPE_FIXED64, TYPE_LENGTH_DELIMITED, TYPE_GROUP };
```

读取接口按形态取值（F-CPP-106）：`type()`、`varint()`、`fixed32()`、`fixed64()`、`length_delimited()`（返回 `absl::string_view`）、`group()`（返回嵌套 `const UnknownFieldSet&`）。容器 `UnknownFieldSet`（F-CPP-107）提供 `Clear()`、`empty()`、`field_count()`、`field(int index)` 与按形态追加的 `AddVarint(int number, uint64_t value)`、`AddFixed32`、`AddFixed64`、`AddLengthDelimited(int number, absl::string_view value)`、`AddGroup(int number)`——反射侧的 `GetUnknownFields`/`MutableUnknownFields`（见 03 篇）即暴露此容器。

## 三语言容器对照

**Python**（upb 扩展，C 文件即容器语义载体）：

- `map.c`：`PyUpb_ScalarMapContainer_Spec`（方法 `clear`、`setdefault`、`get`、`GetEntryClass`、`MergeFrom`）与 `PyUpb_MessageMapContainer_Spec`（另含 `get_or_create`），加 `PyUpb_MapIterator_Spec`（F-RT-016）——标量 map 与消息 map 分型，后者提供"取或建"子消息的入口。
- `repeated.c`：`PyUpb_RepeatedCompositeContainer_Spec`（方法 `__deepcopy__`、`add`、`append`、`insert`、`extend`、`pop`、`remove`、`sort`、`reverse`、`clear`、`MergeFrom`）与 `PyUpb_RepeatedScalarContainer_Spec`（另含 `__array__`、`__reduce__`）（F-RT-017）——`add()` 是 Python 教程里建子消息的惯用法（见 examples/03-python-tutorial）。
- `extension_dict.c`：`PyUpb_ExtensionDict_Spec`（方法 `_FindExtensionByName`、`_FindExtensionByNumber`；slot 含 `Py_tp_iter`、`Py_sq_contains`、`Py_mp_subscript`）与 `PyUpb_ExtensionIterator_Spec`（F-RT-018）。
- `unknown_fields.c`：`PyUpb_UnknownFieldSet_Spec`，初始化时用 `collections.namedtuple` 构造 `"PyUnknownField"`（字段 `field_number`、`wire_type`、`data`）（F-RT-019）——把三种 wire 形态统一为具名元组。

**Rust**（view/mut 双视角体系）：`repeated.rs` 定义 `Repeated<T: Singular>`、`RepeatedView<'msg, T>`、`RepeatedMut<'msg, T>`、`RepeatedIter<'msg, T>`、`RepeatedMutIter<'msg, T>`；`singular.rs` 定义 `pub unsafe trait Singular: Proxied + SealedInternal`（F-RT-046）。map 侧 `map.rs` 定义 `MapValue` trait、`Map<K: MapKey, V: MapValue>`、`MapView<'msg, K, V>`、`MapMut<'msg, K, V>`、`MapIter<'msg, K, V>`（F-RT-047）。扩展侧 `enum.rs` 定义 `pub unsafe trait Enum` 与 `pub struct UnknownEnumValue<T>(i32, PhantomData<T>)`（未识别枚举值的显式类型）；`extension.rs` 定义 `ExtensionId<Extendee, T: Proxied>` 及 trait `ExtHas`、`ExtClear`、`ExtAccess`、`ExtGetMut`（F-RT-048）——Rust 用 borrow 类型系统把"只读视图 vs 可变引用"编码进类型。完整体系见 /concepts/12-upb-and-rust-runtime.md。

**Objective-C**（类型化容器族）：`GPBArray.h` 声明八个标量数组类——`GPBInt32Array`、`GPBUInt32Array`、`GPBInt64Array`、`GPBUInt64Array`、`GPBFloatArray`、`GPBDoubleArray`、`GPBBoolArray`、`GPBEnumArray`（均 `: NSObject <NSCopying>`，F-RT-084）；`GPBDictionary.h` 声明按键值类型组合的类型化字典族，如 `GPBUInt32UInt32Dictionary`、`GPBInt32EnumDictionary`、`GPBUInt32ObjectDictionary<__covariant ObjectType>` 等（F-RT-085）——不走泛型容器，而是编译出全组合具体类换取装箱零开销。

## 相关概念

- [/concepts/02-wire-format.md](/concepts/02-wire-format.md)——map/repeated/未知字段的线格式编码源头。
- [/concepts/03-descriptors-and-reflection.md](/concepts/03-descriptors-and-reflection.md)——容器之上的反射读写矩阵与 `AppendToList` 的消费方。
- [/concepts/11-python-runtime.md](/concepts/11-python-runtime.md)——Python 容器 C 实现的初始化链与对象缓存。
- [/concepts/14-other-language-runtimes.md](/concepts/14-other-language-runtimes.md)——Objective-C 类型化容器族的完整图景。
