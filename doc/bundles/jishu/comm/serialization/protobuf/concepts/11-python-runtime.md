---
type: Concept
title: "Python 运行时（upb C 扩展）"
description: "google._upb._message C 扩展模块的九个子系统初始化链、PyUpb_ModuleState 类型注册表、DescriptorPool 方法族与对象缓存，及 setup.py 源码 glob 与三实现 conformance 构建目标。"
tags: [protobuf, python, runtime]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: runtimes
    resource: /references/runtimes.md
    title: "protobuf 多语言运行时信源"
---

Python 的 protobuf 运行时并非纯 Python 实现，而是一个名为 `google._upb._message` 的 C 扩展模块：模块初始化时 `PyModule_AddIntConstant(m, "_IS_UPB", 1)` 明确声明自己运行在 upb C 内核之上（F-RT-004）。这是"双运行时内核"洞察的直接证据——Python 只是 upb 内核的 C FFI 绑定（binding），解析与序列化全部下沉到 C 层（内核本体见 [upb 内核与 Rust 双 kernel 运行时](/concepts/12-upb-and-rust-runtime.md)）。本篇从初始化链讲到类型注册表、DescriptorPool 方法族、对象缓存与构建分发。

## 模块定义与目录

python/ 目录含 C 源文件 buffer_convert.c/.h、convert.c/.h、descriptor_containers.c/.h、descriptor_pool.c/.h、descriptor.c/.h、extension_dict.c/.h、map.c/.h、message.c/.h、protobuf.c、protobuf.h、repeated.c/.h、unknown_fields.c/.h、python_api.h、version_script.lds，及构建文件 internal.bzl、build_targets.bzl、子目录 dist/、google/ 等（F-RT-001）。

protobuf.h 定义核心宏（F-RT-002）：`PYUPB_MODULE_NAME "google._upb._message"`、`PYUPB_PROTOBUF_PUBLIC_PACKAGE "google.protobuf"`、`PYUPB_PROTOBUF_INTERNAL_PACKAGE "google.protobuf.internal"`、`PYUPB_DESCRIPTOR_MODULE "google.protobuf.descriptor_pb2"`。

## 初始化链：PyInit__message 到九个 Init 子系统

模块初始化函数为 `PyMODINIT_FUNC PyInit__message(void)`，内部依次调用（F-RT-004）：

```text
PyUpb_InitDescriptorContainers
PyUpb_InitDescriptorPool
PyUpb_InitDescriptor
PyUpb_InitArena
PyUpb_InitExtensionDict
PyUpb_InitMap
PyUpb_InitMessage
PyUpb_Repeated_Init
PyUpb_UnknownFields_Init
```

最后 `PyModule_AddIntConstant(m, "_IS_UPB", 1)`——这就是运行时自报内核身份的开关。模块级方法表 PyUpb_ModuleMethods 含 SetAllowOversizeProtos、_AllocationCount_IsAvailable、_AllocationCount_Get、_AllocationCount_Reset、_AllocationCount_FailOn（F-RT-005）。

所有子系统类型注册在 `struct PyUpb_ModuleState`（F-RT-003）：字段含 `descriptor_types[kPyUpb_Descriptor_Count]`、`default_pool`、`descriptor_pool_type`、`c_descriptor_symtab`、`extension_dict_type`、`map_iterator_type`、`message_map_container_type`、`scalar_map_container_type`、`cmessage_type`、`message_meta_type`、`arena_type`、`obj_cache`、`repeated_composite_container_type`、`repeated_scalar_container_type`、`unknown_fields_type` 等。另有 descriptor_containers 对应的 `by_name_map_type`、`by_name_iterator_type`、`by_number_map_type`、`by_number_iterator_type`、`generic_sequence_type` 五个类型（F-RT-030）。

## 对象缓存与 Arena

protobuf.c 定义 `PyUpb_WeakMap`（含 `upb_inttable table`、`upb_Arena* arena`）与函数 `PyUpb_WeakMap_New/Free/Add/Delete/TryDelete/Get/Next/DeleteIter`，以及对象缓存 `PyUpb_ObjCache_Add/Delete/Get/Instance`（F-RT-006）——upb C 对象到 Python wrapper 的一对一映射由此维护，避免同一 C 对象被包装两次。

`PyUpb_Arena` 类型（PyType_Spec 名为 `PYUPB_MODULE_NAME ".Arena"`）与函数 `PyUpb_Arena_New/Get/IsFrozen/SetFrozen`；含 `upb_trim_allocfunc` 分配器（GLIBC 下周期调用 `malloc_trim`）（F-RT-007）。自由线程（free-threading）支持：在 `Py_GIL_DISABLED` 且 `_POSIX_THREADS` 时定义 ENABLE_MUTEX（FreeThreadingMutex 包含 `pthread_mutex_t`），提供 FreeThreadingLock/Unlock（F-RT-008）。Arena 语义详见 [Arena 内存管理](/concepts/04-arena-memory-management.md)。

## Descriptor 体系

公开 C API 声明位于 descriptor.h（F-RT-010）：`PyUpb_Descriptor_GetClass`、`PyUpb_Descriptor_SetClass`、`PyUpb_Descriptor_Get`、`PyUpb_EnumDescriptor_Get`、`PyUpb_FieldDescriptor_Get`、`PyUpb_FileDescriptor_Get`、`PyUpb_OneofDescriptor_Get`、`PyUpb_EnumValueDescriptor_Get`、`PyUpb_Descriptor_GetOrCreateWrapper`、`PyUpb_ServiceDescriptor_Get`、`PyUpb_MethodDescriptor_Get`、`PyUpb_FileDescriptor_GetDef`、`PyUpb_FieldDescriptor_GetDef`、`PyUpb_Descriptor_GetDef`、`PyUpb_AnyDescriptor_GetDef`、`PyUpb_InitDescriptor`。

枚举 `PyUpb_DescriptorType`（F-RT-011）：kPyUpb_Descriptor、kPyUpb_EnumDescriptor、kPyUpb_EnumValueDescriptor、kPyUpb_FieldDescriptor、kPyUpb_FileDescriptor、kPyUpb_MethodDescriptor、kPyUpb_OneofDescriptor、kPyUpb_ServiceDescriptor，`kPyUpb_Descriptor_Count = 8`——八类 descriptor 与 C++ 侧一一对应（见 [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md)）。

Python 侧类型规格 PyUpb_Descriptor_Spec 的 getter 族（F-RT-012）含 `name`、`full_name`、`file`、`fields`、`fields_by_name`、`nested_types`、`extensions`、`enum_types`、`oneofs`、`containing_type`、`is_extendable`；另有 PyUpb_EnumDescriptor_Spec、PyUpb_EnumValueDescriptor_Spec、PyUpb_FieldDescriptor_Spec、PyUpb_FileDescriptor_Spec、PyUpb_MethodDescriptor_Spec 等。

## DescriptorPool 方法族

`struct PyUpb_DescriptorPool` 的方法表 `PyUpb_DescriptorPool_Methods`（F-RT-013 照录）：`Add`、`AddSerializedFile`、`SetFeatureSetDefaults`、`FindFileByName`、`FindMessageTypeByName`、`FindFieldByName`、`FindExtensionByName`、`FindEnumTypeByName`、`FindOneofByName`、`FindServiceByName`、`FindMethodByName`、`FindFileContainingSymbol`、`FindExtensionByNumber`、`FindAllExtensions`——AddSerializedFile 正是序列化 FileDescriptorProto 入池的入口，与 C++ `DescriptorPool::BuildFile` 同位（见 [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md)）。

descriptor_pool.c 另导出 `PyUpb_DescriptorPool_GetDefaultPool`、`PyUpb_DescriptorPool_GetFileProtoDef`、`PyUpb_DescriptorPool_GetSymtab`、`PyUpb_DescriptorPool_Get`，并实现 `PyUpb_DescriptorPool_TryLoadFileProto/TryLoadSymbol/TryLoadFilename/TryLoadExtension`（回调 db 的 `FindFileContainingSymbol`/`FindFileByName`/`FindFileContainingExtension`）（F-RT-014）——fallback database 的 Python 形态。

## Message 与容器 API

message.h 声明（F-RT-015）：`PyUpb_Message_MergeFrom`、`PyUpb_Message_MergeFromString`、`PyUpb_Message_SerializeToString`、`PyUpb_Message_SerializePartialToString`、`PyUpb_Message_InitAttributes`、`PyUpb_Message_GetExtensionDef`、`PyUpb_Message_DoClearField`、`PyUpb_Message_ClearExtensionDict`、`PyUpb_Message_GetFieldValue`、`PyUpb_Message_SetFieldValue`、`PyUpb_MessageMeta_DoCreateClass`、`PyUpb_Message_GetVersion`、`PyUpb_Message_IsFrozen`、`PyUpb_InitMessage` 等。

容器类型方法表（F-RT-016/017/018/019）：

- map.c：`PyUpb_ScalarMapContainer_Spec`（方法 clear、setdefault、get、GetEntryClass、MergeFrom）与 `PyUpb_MessageMapContainer_Spec`（另含 get_or_create）与 `PyUpb_MapIterator_Spec`；
- repeated.c：`PyUpb_RepeatedCompositeContainer_Spec`（方法 `__deepcopy__`、add、append、insert、extend、pop、remove、sort、reverse、clear、MergeFrom）与 `PyUpb_RepeatedScalarContainer_Spec`（另含 `__array__`、`__reduce__`）；
- extension_dict.c：`PyUpb_ExtensionDict_Spec`（方法 `_FindExtensionByName`、`_FindExtensionByNumber`；slot 含 Py_tp_iter、Py_sq_contains、Py_mp_subscript 等）与 `PyUpb_ExtensionIterator_Spec`；
- unknown_fields.c：`PyUpb_UnknownFieldSet_Spec`；初始化时导入 `collections.namedtuple` 构造 `"PyUnknownField"`（字段 field_number、wire_type、data）。

类型转换由 convert.c/.h 提供（F-RT-020）：`PyUpb_UpbToPy(upb_MessageValue, const upb_FieldDef*, PyObject* arena)`、`PyUpb_PyToUpb(PyObject*, const upb_FieldDef*, upb_MessageValue*, upb_Arena*)`、`PyUpb_IsNumpyNdarray`、`PyUpb_IsNumpyBoolScalar`。buffer 转换由 buffer_convert.h 提供（F-RT-021）：枚举 `PyUpb_TryResult`（kPyUpb_TryResult_Success/Failure/NotSupported）、`PyUpb_SourceKind`（Float/Double/Bool/Int8/.../UInt64）、`PyUpb_SourceKindFromCType`、`PyUpb_SourceKindFromFormat`、`PyUpb_GetTargetItemSize`、`PyUpb_TryConvertBuffer`。

## 构建与分发

version_script.lds 全部内容为导出 `PyInit__message` 符号（`global: PyInit__message; local: *;`）（F-RT-022）——扩展只暴露模块入口一个符号。python_api.h 是 Python Limited API 适配头（F-RT-009）。版本：`python/google/protobuf/__init__.py` 仅含 `__version__ = '7.37.0'`（F-RT-023）；`python/google/__init__.py` 内容为 `from pkgutil import extend_path` 与 `__path__ = extend_path(__path__, __name__)`（F-RT-024）——用 pkgutil 机制把 google 做成命名空间包（namespace package），避免与其他 google 系发行版冲突。requirements.txt 三行：`numpy<=2.3.4`、`setuptools<=78.1.1`、`absl-py==2.*`（F-RT-026）。

dist/setup.py（F-RT-025）：包名 `name='protobuf'`；`ext_modules` 单项 `Extension('google._upb._message', srcs, include_dirs=[current_dir, utf8_range], language='c', ...)`；srcs 由 glob 组成（`google/protobuf/*.c`、`python/*.c`、`upb/**/*.c`、`utf8_range/*.c`，过滤含 decode_fast 的文件）；`python_requires='>=3.10'`；`install_requires=[]`；Windows 平台 `extra_link_args=['-static']`，否则 `-fvisibility=hidden`；classifiers 列出 Python 3.10–3.14。注意源码 glob 直接包含 `upb/**/*.c`——upb 内核随包整体编译进扩展。

build_targets.bzl 声明构建目标（F-RT-028）：`protobuf_python`（py_library）、`well_known_types_py_pb2`、`google/protobuf/internal/_api_implementation.so`（cc_binary，copts `-DPYTHON_PROTO2_CPP_IMPL_V2`）、`google/protobuf/pyext/_message`（py_extension，copts `-DGOOGLE_PROTOBUF_HAS_ONEOF=1`）、`python_edition_defaults`（maximum_edition="2026"、minimum_edition="PROTO2"）、`proto_api`（cc_library）、`python_toolchain`（proto_lang_toolchain，command_line `--python_out=%s`）；测试目标含 `conformance_test`/`conformance_test_cpp`/`conformance_test_upb`（env 分别设 `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION` 为 `python`/`cpp`/`upb`）。三个 conformance 目标对应 Python 的三种实现切换——"同一语言双内核"（python_cpp/python_upb）是常态设计的实证（conformance 体系见 [公共契约层：Well-Known Types、Conformance 与 Benchmarks](/concepts/16-wkt-conformance-benchmarks.md)）。internal.bzl 定义 internal_copy_files（Windows `.bat`/`cmd.exe` 与 POSIX bash 两种复制实现）、internal_is_windows、internal_py_test 包装（F-RT-027）；python/dist/ 另含 setup_wrapper.sh、py_proto_library.bzl、python_downloads.bzl 等（F-RT-029）。

## 相关概念

- [upb 内核与 Rust 双 kernel 运行时](/concepts/12-upb-and-rust-runtime.md) —— Python 绑定之下的 upb C 内核本体
- [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md) —— AddSerializedFile 的对侧机制
- [Arena 内存管理](/concepts/04-arena-memory-management.md) —— PyUpb_Arena 的内存语义
- [其他语言运行时概览](/concepts/14-other-language-runtimes.md) —— 同样内嵌 upb 的 PHP/Ruby/Lua 绑定
