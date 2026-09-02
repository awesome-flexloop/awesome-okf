---
okf_version: "0.2"
---

# protobuf 知识库

本知识包是 Google [Protocol Buffers](https://github.com/protocolbuffers/protobuf) 主仓（v37.0-dev）的系统化中文教程，基于源码深度阅读生成。内容以五条架构主线贯穿：双运行时内核（C++ 全功能内核与 upb 轻量内核，多语言实为多绑定）、descriptor 单一事实源（protobuf 用 protobuf 描述 protobuf 的自举设计）、protoc 生成器统一接口（内置生成器与外部插件同构）、Editions 特性系统（proto2/proto3 被降维为 feature 预设）、双构建系统（Bazel 与 CMake 并列的一等公民路径）。所有内容均溯源至 protobuf 源码，遵循 [OKF v0.2 规范](../../../../meta/okf-spec/index.md)。

## 入门组（concepts/）

* [仓库总览与双构建系统](concepts/00-repo-overview-and-build-systems.md) — 32 个顶层目录与版本常量全景，Bazel 与 CMake 两套构建系统并列讲解。
* [消息模型基础：Message 与 MessageLite](concepts/01-message-model.md) — MessageLite 序列化最小接口与 Message 反射全功能接口的两层类层次。
* [Wire Format 二进制编码](concepts/02-wire-format.md) — WireType 六值枚举、tag 构成、varint 编码与 CodedStream/ZeroCopy 流族。

## 核心机制组（concepts/）

* [Descriptor 体系与运行时反射](concepts/03-descriptors-and-reflection.md) — 八类 Descriptor、Reflection 读写矩阵、DescriptorPool/DescriptorDatabase——贯穿全生命周期的单一事实源。
* [Arena 内存管理](concepts/04-arena-memory-management.md) — Make/Own/DoCreateMessage 生命周期模型与 ArenaStringPtr 字符串机制。
* [容器、扩展与未知字段](concepts/05-containers-extensions-unknown-fields.md) — Map/RepeatedField 容器语义、ExtensionSet 扩展体系、UnknownFieldSet 未知字段保留。
* [文本格式与 JSON 序列化](concepts/06-text-format-and-json.md) — TextFormat 文本协议、DebugString 三态输出与 json/ 目录选项体系。

## 编译器组（concepts/）

* [protoc 命令行与编译管线](concepts/07-protoc-command-line.md) — ProtobufMain 入口、11 组生成器注册与四模式执行，含 flag 全集。
* [Parser 与源码导入体系](concepts/08-parser-and-importer.md) — Parser 解析方法族、LocationRecorder 源位置记录与 Importer 虚拟路径映射。
* [代码生成器体系与各语言实现](concepts/09-code-generators.md) — CodeGenerator 接口契约与 9 个内置生成器的 edition 支持矩阵。
* [插件协议（plugin.proto）](concepts/10-plugin-protocol.md) — CodeGeneratorRequest/Response 字段表与 PluginMain 插件进程骨架。

## 运行时组（concepts/）

* [Python 运行时（upb C 扩展）](concepts/11-python-runtime.md) — google._upb._message 模块九子系统初始化链与 PyUpb_ModuleState 类型注册表。
* [upb 内核与 Rust 双 kernel 运行时](concepts/12-upb-and-rust-runtime.md) — upb C 内核 17 子目录、Rust kernel 编译开关与 Proxied trait 体系。
* [hpb：C++ 多后端 API 层与 hpb_generator](concepts/13-hpb.md) — CreateMessage/Parse/Serialize 模板 API 与 multibackend.h 编译期后端选择。
* [其他语言运行时概览：Java/C#/ObjC/PHP/Ruby/Lua](concepts/14-other-language-runtimes.md) — 以"语言绑定 × 内核选择"二维视角综述六语言运行时。

## 高级组（concepts/）

* [Editions 特性系统](concepts/15-editions-feature-system.md) — Edition 八值枚举、FeatureSet 数据模型与编译器/生成器协商矩阵。
* [公共契约层：Well-Known Types、Conformance 与 Benchmarks](concepts/16-wkt-conformance-benchmarks.md) — WKT 全家族、Conformance 三层测试框架与基准函数族。
* [版本选型与迁移实践](concepts/17-version-selection-and-migration.md) — proto2/proto3/Editions 工程视角：版本演进速查表、选型决策树、六大反模式、十项迁移检查清单与渐进式灰度迁移策略。

## 实战示例（examples/）

* [addressbook.proto：入门 schema 解析](examples/01-addressbook-proto.md) — 官方教程 schema 逐字段解析与五语言文件级 option。
* [C++ 教程：add_person 与 list_people](examples/02-cpp-tutorial.md) — setter/mutable/add API 与 istream 文件 IO。
* [Python 教程：add_person 与 list_people](examples/03-python-tutorial.md) — addressbook_pb2 动态模块与容器追加。
* [Java、Ruby 与 Dart 教程](examples/04-java-ruby-dart-tutorials.md) — builder 模式、encode/decode 与级联语法三套教程对照。
* [examples 构建体系与多语言互操作](examples/05-examples-build-systems.md) — 四套构建入口与 protoc 多语言 --*_out 代码生成。

## 信源登记簿（references/）

* [仓库结构与构建系统信源登记](references/repo-structure.md) — F-REPO-001~067 共 67 条事实的源码路径。
* [C++ 运行时核心信源登记](references/cpp-core.md) — F-CPP-001~144 共 144 条事实的源码路径。
* [protoc 编译器信源登记](references/compiler.md) — F-CMP-001~090 共 90 条事实的源码路径。
* [多语言运行时信源登记](references/runtimes.md) — F-RT-001~105 共 105 条事实的源码路径。
* [测试与规范体系信源登记](references/testing.md) — F-TST-001~080 共 80 条事实的源码路径。

## 信任与生命周期说明

* **status 判定依据**：全部 28 个内容文档（18 个概念 + 5 个示例 + 5 个信源登记）均 `status: stable`。源码篇内容基于对 protobuf 主仓 v37.0-dev 源码（`external/libs/protocolbuffers/protobuf/`）的逐模块阅读与事实提取（5 份事实清单合计 486 条主仓事实），经 R→I→E→V→C 五阶段流程生成；工程实践篇（17）于 2026-09-02 从 SpecWeave learning 侧 protobuf-wiki 合并而来。
* **stale_after 解释**：统一设置为 `2027-06-30`。protobuf 处于 Editions 演进活跃期（EDITION_2026 已进入枚举），该日期作为针对 Edition 2026 正式发布后重新评估的保守节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-28）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-28），两者分离、可追溯。
* **关联知识包**：CI 层面的 GitHub Actions 复用体系见姊妹束 [protobuf-ci](../protobuf-ci/index.md)。

本知识包共收录 28 个内容文档（18 个概念 + 5 个示例 + 5 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
