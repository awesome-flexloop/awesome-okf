---
type: Example
title: "Java、Ruby 与 Dart 教程"
description: "并排讲解 examples 目录 Java builder 模式、Ruby encode/decode 与符号枚举、Dart 级联语法三套语言教程的写入与读取程序。"
tags: [protobuf, examples, java, ruby, dart]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
---

examples/ 目录中，Java、Ruby 与 Dart 三种语言各自提供了操作同一份通讯录文件的 add_person / list_people 双程序（F-REPO-060），并与 [C++ 教程](/examples/02-cpp-tutorial.md)、[Python 教程](/examples/03-python-tutorial.md) 共享 schema [addressbook.proto](/examples/01-addressbook-proto.md)。三种语言的 API 风格差异明显：Java 以 Builder 模式构造不可变消息，Ruby 走动态类 + 模块方法，Dart 则用级联语法直接填充消息（F-TST-056 ~ F-TST-060）。

## Java：Builder 模式与流式 IO

AddPerson.java 导入 `com.example.tutorial.protos.AddressBook / Person`（来自 schema 的 java_package option）与 `com.google.protobuf.util.Timestamps`（F-TST-058）。

### 写入：newBuilder / mergeFrom / writeTo

Java 消息不可变，构造一律经 Builder（F-TST-058）：

```java
    Person.Builder person = Person.newBuilder();

    stdout.print("Enter person ID: ");
    person.setId(Integer.valueOf(stdin.readLine()));

    stdout.print("Enter name: ");
    person.setName(stdin.readLine());
```

嵌套消息与 repeated 的追加链式完成：

```java
      Person.PhoneNumber.Builder phoneNumber =
        Person.PhoneNumber.newBuilder().setNumber(number);
```

```java
      person.addPhones(phoneNumber);
      person.setLastUpdated(Timestamps.now());
```

枚举写入用 `phoneNumber.setType(Person.PhoneType.MOBILE / HOME / WORK)`；`person.setLastUpdated(Timestamps.now())` 是 WKT Timestamp 在 Java 侧的取当前时间入口。main 中整本通讯录的读入与写回（F-TST-058）：

```java
    AddressBook.Builder addressBook = AddressBook.newBuilder();
    ...
        addressBook.mergeFrom(input);
    ...
      addressBook.build().writeTo(output);
```

`mergeFrom` 在 Builder 上把现有文件内容并入，`build().writeTo(output)` 把构建结果整体写出到流——与 C++ `ParseFromIstream` / `SerializeToOstream` 一一对应。

### 读取：parseFrom 与 getXxxList

ListPeople.java 无 Builder，直接从流解析（F-TST-059）：

```java
    AddressBook addressBook =
      AddressBook.parseFrom(new FileInputStream(args[0]));
```

repeated 字段读取为不可变列表，枚举用 switch：

```java
    for (Person person: addressBook.getPeopleList()) {
      System.out.println("Person ID: " + person.getId());
      ...
      for (Person.PhoneNumber phoneNumber : person.getPhonesList()) {
        switch (phoneNumber.getType()) {
          case MOBILE:
            ...
```

getter 家族为 `person.getId() / getName() / getEmail()` 与 `phoneNumber.getType() / getNumber()`（F-TST-059）。

## Ruby：动态类与符号枚举

Ruby 教程从 protoc `--ruby_out` 产物加载（F-TST-056）：

```ruby
require './addressbook_pb'
```

### 写入：Tutorial::Person 与 encode

创建 Person 的源码原文如下（F-TST-056，注意 `newlD()` 为源码原文拼写，非本知识束改写；常规 Ruby 读者会预期这是 `new` 之类的构造方法名的笔误，但仓库文件中确实如此）：

```ruby
def prompt_for_address()
  person = Tutorial::Person.newlD()
```

嵌套消息构造用带关键字参数的 `new`：

```ruby
    phone_number = Tutorial::Person::PhoneNumber.new(number: number)
```

枚举以符号赋值（F-TST-056）：

```ruby
    case type
    when "mobile"
      phone_number.type = :MOBILE
    when "home"
      phone_number.type = :HOME
    when "work"
      phone_number.type = :WORK
```

读写文件用模块级 encode / decode（F-TST-056）：

```ruby
address_book = Tutorial::AddressBook.new()
if File.exist?(ARGV[0])
  # Read the existing address book if it exists
  f = File.open(ARGV[0], "rb")
  address_book = Tutorial::AddressBook.decode(f.read)
  f.close
```

```ruby
# Write the new address book back to disk.
f = File.open(ARGV[0], "wb")
f.write(Tutorial::AddressBook.encode(address_book))
f.close
```

追加联系人用普通 Ruby 数组语义：`address_book.people.push(person)`（F-TST-056）。

### 读取：each 迭代与 case 比较

list_people.rb 侧的迭代与枚举比较（F-TST-057）：

```ruby
  address_book.people.each do |person|
    ...
    person.phones.each do |phone_number|
      type =
        case phone_number.type
        when :MOBILE
          "Mobile phone"
        when :HOME
          "Home phone"
        when :WORK
          "Work phone"
        end
```

`Tutorial::AddressBook.decode(f.read)` 与写入侧同源。

## Dart：级联语法与字节缓冲

Dart 教程导入 protoc `--dart_out` 产物（F-TST-060）：

```dart
import 'dart_tutorial/addressbook.pb.dart';
```

### 写入：fromBuffer / writeToBuffer 与 ..number 级联

Dart 生成类名以扁平下划线命名（`Person_PhoneNumber`、`Person_PhoneType`）。PhoneNumber 的构造使用了 Dart 级联语法（F-TST-060）：

```dart
    final phoneNumber = Person_PhoneNumber()..number = number;
```

`..number = number` 在返回对象本身的同时完成字段赋值。枚举常量为 `Person_PhoneType.MOBILE / HOME / WORK`（F-TST-060）。整本的读写（F-TST-060）：

```dart
  final file = File(arguments.first);
  AddressBook addressBook;
  if (!file.existsSync()) {
    print('File not found. Creating new file.');
    addressBook = AddressBook();
  } else {
    addressBook = AddressBook.fromBuffer(file.readAsBytesSync());
  }
  addressBook.people.add(promptForAddress());
  file.writeAsBytes(addressBook.writeToBuffer());
```

`AddressBook.fromBuffer(...)` 从字节缓冲解析、`addressBook.writeToBuffer()` 序列化为字节列表；追加用列表的 `add`。

### 读取

list_people.dart 同样以 `AddressBook.fromBuffer(file.readAsBytesSync())` 读入，遍历 `addressBook.people` 与 `person.phones`，switch `Person_PhoneType.MOBILE / HOME / WORK`；其差异之一是 email 判存在调用 `person.hasEmail()`（F-TST-060）。

## 构建与互操作入口

三语言的构建入口分散在 Makefile 的 `java` / `ruby` / `dart` 目标：Java 经 `javac_middleman` 编译后生成快捷脚本，Ruby 依赖 `protoc_middleman_ruby`（`--ruby_out=.`），Dart 依赖 `protoc_middleman_dart`（`--dart_out=dart_tutorial`，附带 `../src/google/protobuf/timestamp.proto`，并执行 `pub get`）（F-TST-062）。README 指出各语言示例操作同一格式文件，可以"用 add_person_java 创建通讯录、再用 list_people_python 读取"（F-TST-063），构建体系全景见 [05-examples-build-systems.md](/examples/05-examples-build-systems.md)。

## 相关概念

- [其他语言运行时概览：Java/C#/ObjC/PHP/Ruby/Lua](/concepts/14-other-language-runtimes.md)——Java 双运行时与 Ruby C 扩展/FFI 实现的底层形态。
- [消息模型基础：Message 与 MessageLite](/concepts/01-message-model.md)——各语言 API 风格背后的统一消息模型。
- [公共契约层：Well-Known Types、Conformance 与 Benchmarks](/concepts/16-wkt-conformance-benchmarks.md)——`Timestamps.now()` 所用的 Timestamp WKT。
