---
type: Example
title: "addressbook.proto：入门 schema 解析"
description: "逐字段解析 protobuf 官方教程示例 schema addressbook.proto，覆盖 Person/AddressBook 消息、嵌套枚举与五语言文件级 option。"
tags: [protobuf, examples, proto3, schema]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
  - id: repo-structure
    resource: /references/repo-structure.md
    title: "protobuf 仓库结构与构建系统信源"
---

`examples/addressbook.proto` 是 protobuf 仓库 examples/ 目录中的官方入门教程 schema（F-REPO-060），定义了一个通讯录（Address Book）数据模型：联系人（Person）拥有姓名、ID、邮箱、多部电话与最后更新时间。examples/ 下的 C++/Python/Java/Ruby/Dart/Go 六种语言教程程序全部基于这同一份 schema 生成代码，它是观察"一份 proto、多语言消费"的最小完整样本（F-TST-050、F-TST-051）。

本篇逐字段解析该 schema 的完整原文，重点覆盖 proto3 语法要素、嵌套 message 与 enum、Well-Known Types 引用，以及面向五种语言的文件级 option。

## schema 完整定义

以下为 examples/addressbook.proto 原文照录（含源码中的 `[START ...]`/`[END ...]` 教程分节标记注释，文件首部注释说明这些标记仅用于教程抽取、并非 Protocol Buffers 语法的一部分）：

```protobuf
// See README.md for information and build instructions.
//
// Note: START and END tags are used in comments to define sections used in
// tutorials.  They are not part of the syntax for Protocol Buffers.
//
// To get an in-depth walkthrough of this file and the related examples, see:
// https://developers.google.com/protocol-buffers/docs/tutorials

// [START declaration]
syntax = "proto3";
package tutorial;

import "google/protobuf/timestamp.proto";
// [END declaration]

// [START java_declaration]
option java_multiple_files = true;
option java_package = "com.example.tutorial.protos";
option java_outer_classname = "AddressBookProtos";
// [END java_declaration]

// [START csharp_declaration]
option csharp_namespace = "Google.Protobuf.Examples.AddressBook";
// [END csharp_declaration]

// [START go_declaration]
option go_package = "github.com/protocolbuffers/protobuf/examples/go/tutorialpb";
// [END go_declaration]

// [START messages]
message Person {
  string name = 1;
  int32 id = 2;  // Unique ID number for this person.
  string email = 3;

  enum PhoneType {
    MOBILE = 0;
    HOME = 1;
    WORK = 2;
  }

  message PhoneNumber {
    string number = 1;
    PhoneType type = 2;
  }

  repeated PhoneNumber phones = 4;

  google.protobuf.Timestamp last_updated = 5;
}

// Our address book file is just one of these.
message AddressBook {
  repeated Person people = 1;
}
// [END messages]
```

## 文件头：syntax、package 与 import

文件声明 `syntax = "proto3"`，package 为 `tutorial`（F-TST-050）。package 在生成代码中映射为各语言的命名空间骨架：C++ 侧生成 `tutorial::Person`，Ruby 侧生成 `Tutorial::Person` 模块（见本目录 [02-cpp-tutorial.md](/examples/02-cpp-tutorial.md) 与 [04-java-ruby-dart-tutorials.md](/examples/04-java-ruby-dart-tutorials.md)）。

`import "google/protobuf/timestamp.proto"` 引入了 Well-Known Types 家族中的 Timestamp 消息——这是 schema 引用 `google.protobuf.Timestamp last_updated` 字段的前提（F-TST-050）。在仓库构建体系中，examples/BUILD.bazel 的 `proto_library` 目标以 `deps = ["@com_google_protobuf//:timestamp_proto"]` 显式声明该依赖（F-TST-065 目录内文件）。

## Person 消息逐字段讲解

Person 是教程的核心消息（F-TST-051）：

- `string name = 1;`——姓名，字段编号 1。proto3 中标量字段默认不再携带 `optional` 关键字。
- `int32 id = 2;`——唯一 ID，编号 2，源码行内注释为 `// Unique ID number for this person.`。
- `string email = 3;`——邮箱，编号 3。
- `repeated PhoneNumber phones = 4;`——电话列表，编号 4。`repeated` 声明该字段可重复出现，wire format 中同一编号可多次写入；各语言运行时将其映射为容器（C++ 的 repeated field、Python 的 `person.phones.add()`、Dart 的 `person.phones.add(...)`）。
- `google.protobuf.Timestamp last_updated = 5;`——message 类型字段，编号 5。message 字段天然具有"存在性"语义，因此 C++ 侧有 `has_last_updated()`、Java 侧有 `hasLastUpdated()` 一类判定 API（F-TST-055）。

### 嵌套 enum：PhoneType

PhoneType 定义在 Person 内部，三个值 `MOBILE = 0`、`HOME = 1`、`WORK = 2`（F-TST-051）。proto3 规定枚举首值必须为 0，而 0 值恰好充当未显式赋值时的默认状态。生成代码后，各语言以各自形态暴露这三个常量：C++ 为 `tutorial::Person::MOBILE`，Python 为 `addressbook_pb2.Person.MOBILE`，Java 为 `Person.PhoneType.MOBILE`，Ruby 为符号 `:MOBILE`，Dart 为 `Person_PhoneType.MOBILE`。

### 嵌套 message：PhoneNumber

`message PhoneNumber { string number = 1; PhoneType type = 2; }` 同样嵌套于 Person 内，type 字段的类型即上文嵌套枚举。嵌套定义让生成的类型名带上作用域前缀：C++ 是 `tutorial::Person::PhoneNumber`，Dart 以下划线扁平化为 `Person_PhoneNumber`（F-TST-054、F-TST-060）。

## AddressBook 消息

AddressBook 是顶层第二个消息，只有一个字段 `repeated Person people = 1;`（F-TST-051），源码注释原文为 `// Our address book file is just one of these.`。它把整个通讯录建模为 Person 的列表，各语言的 add_person/list_people 程序都围绕这个容器做读取（Parse）、追加（add）与写回（Serialize）。

## 五语言文件级 option

文件级 option 区是这份 schema 的"多语言输出配置"示范（F-TST-050）：

- `option java_multiple_files = true;`——Java 每个消息生成独立 .java 文件（而非全部嵌进单个外部类）。
- `option java_package = "com.example.tutorial.protos";`——Java 包名，独立于 proto `package tutorial`；AddPerson.java 顶部的 `import com.example.tutorial.protos.AddressBook;` 即来源于此（F-TST-058）。
- `option java_outer_classname = "AddressBookProtos";`——Java 外部类名。
- `option csharp_namespace = "Google.Protobuf.Examples.AddressBook";`——C# 命名空间。
- `option go_package = "github.com/protocolbuffers/protobuf/examples/go/tutorialpb";`——Go 包导入路径，与 examples/Makefile 的 `--go_out=go/tutorialpb` 输出目录相互配合（F-TST-062）。

C++/Python/Ruby 不需要 option：C++ 直接沿用 `tutorial` 命名空间，Python/Ruby 由文件名（`addressbook_pb2` / `addressbook_pb`）决定模块名。这组 option 与 `package tutorial` 的对照，正好演示了"逻辑包名"与"各语言物理命名空间"分离的设计。

## 相关概念

- [消息模型基础：Message 与 MessageLite](/concepts/01-message-model.md)——本 schema 生成代码所依赖的 C++ 类层次。
- [Editions 特性系统](/concepts/15-editions-feature-system.md)——proto3 语法在 v37 编译器中被定位为 Edition 预设的背景。
- [Descriptor 体系与运行时反射](/concepts/03-descriptors-and-reflection.md)——`.proto` 源文件被解析为 FileDescriptorProto 后进入编译管线。
