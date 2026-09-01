# protobuf 概念文档

学习路径分五组递进：入门组（00-02）→ 核心机制组（03-06）→ 编译器组（07-10）→ 运行时组（11-14）→ 高级组（15-16）。

## 入门组

* [仓库总览与双构建系统](00-repo-overview-and-build-systems.md) — 32 个顶层目录与 v37.0-dev 版本常量全景，Bazel 与 CMake 两套一等公民构建系统并列讲解。
* [消息模型基础：Message 与 MessageLite](01-message-model.md) — MessageLite 序列化最小接口与 Message 反射全功能接口的两层类层次，及 C#/ObjC 对应模型。
* [Wire Format 二进制编码](02-wire-format.md) — WireType 六值枚举、tag 构成、varint 编码，及 CodedStream/ZeroCopy 流族 IO 栈。

## 核心机制组

* [Descriptor 体系与运行时反射](03-descriptors-and-reflection.md) — 八类 Descriptor、Reflection 字段级读写矩阵、DescriptorPool/DescriptorDatabase——贯穿全生命周期的单一事实源。
* [Arena 内存管理](04-arena-memory-management.md) — Make/Own/DoCreateMessage 生命周期模型、ArenaStringPtr 字符串机制与多运行时 Arena 形态。
* [容器、扩展与未知字段](05-containers-extensions-unknown-fields.md) — Map 与 RepeatedField/RepeatedPtrField 容器语义、ExtensionSet 扩展体系、UnknownFieldSet 未知字段保留。
* [文本格式与 JSON 序列化](06-text-format-and-json.md) — TextFormat 文本协议、DebugString 三态输出、json/ 目录选项体系与跨语言视角。

## 编译器组

* [protoc 命令行与编译管线](07-protoc-command-line.md) — ProtobufMain 入口、11 组生成器注册、参数解析与四模式执行，含 flag 全集。
* [Parser 与源码导入体系](08-parser-and-importer.md) — Parser 语言构件解析方法族、LocationRecorder 源位置记录、Importer/DiskSourceTree 虚拟路径映射。
* [代码生成器体系与各语言实现](09-code-generators.md) — CodeGenerator 接口契约、GeneratorContext 输出抽象与 9 个内置生成器的 edition 支持矩阵。
* [插件协议（plugin.proto）](10-plugin-protocol.md) — CodeGeneratorRequest/Response 字段表、PluginMain 插件进程骨架与 protoc-gen-* 命名规则。

## 运行时组

* [Python 运行时（upb C 扩展）](11-python-runtime.md) — google._upb._message 模块九子系统初始化链、PyUpb_ModuleState 类型注册表与 DescriptorPool 方法族。
* [upb 内核与 Rust 双 kernel 运行时](12-upb-and-rust-runtime.md) — upb C 内核 17 子目录、Rust kernel 编译开关与 Proxied trait 体系、8 个 release crates。
* [hpb：C++ 多后端 API 层与 hpb_generator](13-hpb.md) — CreateMessage/Parse/Serialize 模板 API、multibackend.h 编译期后端选择与 Ptr 代理技巧。
* [其他语言运行时概览：Java/C#/ObjC/PHP/Ruby/Lua](14-other-language-runtimes.md) — 以"语言绑定 × 内核选择"二维视角综述六语言运行时。

## 高级组

* [Editions 特性系统](15-editions-feature-system.md) — Edition 八值枚举、FeatureSet 数据模型、编译器与九生成器协商矩阵及默认值测试体系。
* [公共契约层：Well-Known Types、Conformance 与 Benchmarks](16-wkt-conformance-benchmarks.md) — WKT 全家族与 BUILD 别名、Conformance 三层测试框架与十九语言失败清单。

```{toctree}
:hidden:
:maxdepth: 7

00-repo-overview-and-build-systems
01-message-model
02-wire-format
03-descriptors-and-reflection
04-arena-memory-management
05-containers-extensions-unknown-fields
06-text-format-and-json
07-protoc-command-line
08-parser-and-importer
09-code-generators
10-plugin-protocol
11-python-runtime
12-upb-and-rust-runtime
13-hpb
14-other-language-runtimes
15-editions-feature-system
16-wkt-conformance-benchmarks
```
