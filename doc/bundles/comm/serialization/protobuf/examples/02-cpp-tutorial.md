---
type: Example
title: "C++ 教程：add_person 与 list_people"
description: "讲解 examples 目录 C++ 教程双程序：Person 的 setter/mutable/add API、istream 文件 IO、版本验证宏与 TimeUtil 的 Timestamp 用法。"
tags: [protobuf, examples, cpp]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
---

examples/ 目录为 C++ 提供一对教程程序（F-REPO-060）：`add_person.cc` 负责从通讯录文件读入 `tutorial::AddressBook`、提示用户输入一个新联系人并写回；`list_people.cc` 负责读入并打印全部联系人。二者合起来完整演示了 C++ 生成代码的消息 API、二进制文件 IO 与库生命周期管理（F-TST-054、F-TST-055）。

两个源文件都包含 `"addressbook.pb.h"`（由 protoc `--cpp_out` 从 [addressbook.proto](/examples/01-addressbook-proto.md) 生成）与 `<google/protobuf/util/time_util.h>`，并 `using google::protobuf::util::TimeUtil;`。

## add_person.cc：写入路径

### 库生命周期：版本验证与收尾清理

main 函数的第一条语句与最后一条语句构成一对生命周期护栏（F-TST-054）：

```cpp
  // Verify that the version of the library that we linked against is
  // compatible with the version of the headers we compiled against.
  GOOGLE_PROTOBUF_VERIFY_VERSION;
```

```cpp
  // Optional:  Delete all global objects allocated by libprotobuf.
  google::protobuf::ShutdownProtobufLibrary();
```

`GOOGLE_PROTOBUF_VERIFY_VERSION` 宏用于验证链接的库版本与编译所用头文件版本兼容；`ShutdownProtobufLibrary()` 释放 libprotobuf 分配的全局对象（源码注释标注为 Optional）。

### 读写文件：ParseFromIstream / SerializeToOstream

AddressBook 的整读整写直接走 std::fstream（F-TST-054）：

```cpp
  tutorial::AddressBook address_book;

  {
    // Read the existing address book.
    fstream input(argv[1], ios::in | ios::binary);
    if (!input) {
      cout << argv[1] << ": File not found.  Creating a new file." << endl;
    } else if (!address_book.ParseFromIstream(&input)) {
      cerr << "Failed to parse address book." << endl;
      return -1;
    }
  }
```

```cpp
  {
    // Write the new address book back to disk.
    fstream output(argv[1], ios::out | ios::trunc | ios::binary);
    if (!address_book.SerializeToOstream(&output)) {
      cerr << "Failed to write address book." << endl;
      return -1;
    }
  }
```

两个方法均返回 bool，解析失败与写失败都以返回码退出。注意"文件不存在时新建"的处理：打开失败不算错误，直接对空消息继续追加。

### 消息构造：setter / mutable / add API

`PromptForAddress(tutorial::Person* person)` 集中演示了 C++ 生成代码的三类写 API（F-TST-054）：

- 标量 setter：`person->set_id(id)`、`person->set_email(email)`；
- string 字段的 mutable 指针：`getline(cin, *person->mutable_name())`——`mutable_name()` 返回 `string*`，可直接作为 getline 的输出目标；
- repeated 字段的 add：`person->add_phones()` 返回新追加元素的指针，随后对其继续调用 `set_number` / `set_type`：

```cpp
    tutorial::Person::PhoneNumber* phone_number = person->add_phones();
    phone_number->set_number(number);
```

枚举赋值使用 `tutorial::Person::MOBILE / HOME / WORK` 常量（源码用 if-else 链比较用户输入字符串）。向 AddressBook 追加新联系人则在 main 中一行完成：`PromptForAddress(address_book.add_people());`（F-TST-054）。

### WKT 用法：TimeUtil::SecondsToTimestamp

`last_updated` 字段是 `google.protobuf.Timestamp` 类型，示例用工具类把当前 Unix 秒转为 Timestamp 并赋给 message 字段（F-TST-054）：

```cpp
  *person->mutable_last_updated() = TimeUtil::SecondsToTimestamp(time(NULL));
```

message 类型字段通过 `mutable_last_updated()` 获得可写指针，再整体赋值。

## list_people.cc：读取路径

读取侧对应一组 getter 与容量 API（F-TST-055）：

```cpp
  for (int i = 0; i < address_book.people_size(); i++) {
    const tutorial::Person& person = address_book.people(i);
```

- repeated 计数：`address_book.people_size()`、`person.phones_size()`；
- repeated 索引：`address_book.people(i)`、`person.phones(j)` 返回 const 引用；
- 标量 getter：`person.id()`、`person.name()`、`person.email()`、`phone_number.type()`、`phone_number.number()`。

枚举读取用 switch 遍历 `tutorial::Person::MOBILE / HOME / WORK`，default 分支打印 "Unknown phone #"。

message 字段的存在性检查与 WKT 格式化（F-TST-055）：

```cpp
    if (person.has_last_updated()) {
      cout << "  Updated: " << TimeUtil::ToString(person.last_updated()) << endl;
    }
```

`has_last_updated()` 是 message 字段专属的存在性判定；`TimeUtil::ToString(person.last_updated())` 把 Timestamp 转为可读字符串。

## 构建方式

C++ 示例有两条官方构建入口（F-TST-062、F-TST-064）：

- **Makefile + pkg-config**：`make cpp` 依赖 `protoc_middleman`（执行 `protoc --cpp_out=. --java_out=. --python_out=. addressbook.proto`）后，以 `c++ add_person.cc addressbook.pb.cc -o add_person_cpp \`pkg-config --cflags --libs protobuf\`` 编译，产物为 `add_person_cpp` 与 `list_people_cpp`（F-TST-062）。README 记录的运行方式为 `./add_person_cpp addressbook.data`。
- **CMake**：examples/CMakeLists.txt 以 `find_package(protobuf CONFIG REQUIRED)` 定位安装，`foreach(example add_person list_people)` 循环生成 `add_person_cpp` / `list_people_cpp` 可执行目标，非 legacy 模式下链接 `protobuf::libprotobuf` 并调用 `protobuf_generate(TARGET ${executable_name})` 完成代码生成（F-TST-061）。

Bazel 路径（`bazel build :all`）见 [05-examples-build-systems.md](/examples/05-examples-build-systems.md)。

## 相关概念

- [Wire Format 二进制编码](/concepts/02-wire-format.md)——`ParseFromIstream`/`SerializeToOstream` 背后的 varint 与 tag 编码机制。
- [消息模型基础：Message 与 MessageLite](/concepts/01-message-model.md)——`tutorial::Person` 继承的 Message 类层次与序列化接口。
- [公共契约层：Well-Known Types、Conformance 与 Benchmarks](/concepts/16-wkt-conformance-benchmarks.md)——`TimeUtil` 所服务的 Timestamp 等 WKT 家族。
