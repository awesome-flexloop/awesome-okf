# protobuf 示例文档

* [addressbook.proto：入门 schema 解析](01-addressbook-proto.md) — 逐字段解析官方教程 schema：Person/AddressBook 消息、嵌套枚举与五语言文件级 option。
* [C++ 教程：add_person 与 list_people](02-cpp-tutorial.md) — setter/mutable/add API、istream 文件 IO、版本验证宏与 TimeUtil 用法。
* [Python 教程：add_person 与 list_people](03-python-tutorial.md) — addressbook_pb2 动态模块、容器追加与 ParseFromString/SerializeToString。
* [Java、Ruby 与 Dart 教程](04-java-ruby-dart-tutorials.md) — Java builder 模式、Ruby encode/decode 与符号枚举、Dart 级联语法三套教程对照。
* [examples 构建体系与多语言互操作](05-examples-build-systems.md) — 四套构建入口（CMake/Makefile/Bazel/pubspec+go）与 protoc 多语言 --*_out 代码生成。

```{toctree}
:hidden:
:maxdepth: 7

01-addressbook-proto
02-cpp-tutorial
03-python-tutorial
04-java-ruby-dart-tutorials
05-examples-build-systems
```
