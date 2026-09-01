---
type: Example
title: "examples 构建体系与多语言互操作"
description: "解析 examples 目录四套构建入口（CMake/Makefile/Bazel/pubspec+go）与 protoc 多语言 --*_out 代码生成，演示跨语言互操作。"
tags: [protobuf, examples, build, cmake, makefile, bazel]
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

examples/ 目录（F-REPO-060）在约二十个源文件里并排放置了四套互相独立的构建入口：CMakeLists.txt、Makefile、Bazel（BUILD.bazel + MODULE.bazel + WORKSPACE + WORKSPACE.bzlmod + .bazelrc），以及 Dart（pubspec.yaml）与 Go（go/ 子目录）的各自包管理文件。这不是冗余，而是同一份 [addressbook.proto](/examples/01-addressbook-proto.md) 在"安装态 protoc + 手写构建"与"仓库态 Bazel 规则"两种世界里的完整对照（F-TST-061 ~ F-TST-065）。

README.md 对目录的定位原句为："This directory contains example code that uses Protocol Buffers to manage an address book. Two programs are provided for each supported language."（F-TST-063）。

## CMake：find_package + protobuf_generate

examples/CMakeLists.txt 的项目名为 `protobuf-examples`，核心只有三步（F-TST-061）：

```cmake
project(protobuf-examples)

# Find required protobuf package
find_package(protobuf CONFIG REQUIRED)
```

```cmake
foreach(example add_person list_people)
  set(${example}_SRCS ${example}.cc)
  set(${example}_PROTOS addressbook.proto)
  ...
  #Executable setup
  set(executable_name ${example}_cpp)
  add_executable(${executable_name} ${${example}_SRCS} ${${example}_PROTOS})
  if(protobuf_MODULE_COMPATIBLE) #Legacy mode
    target_include_directories(${executable_name} PUBLIC ${PROTOBUF_INCLUDE_DIRS})
    target_link_libraries(${executable_name} ${PROTOBUF_LIBRARIES})
  else()
    target_link_libraries(${executable_name} protobuf::libprotobuf)
    protobuf_generate(TARGET ${executable_name})
  endif()

endforeach()
```

`foreach(example add_person list_people)` 循环把两个示例统一展开为 `add_person_cpp` / `list_people_cpp` 可执行目标；非 legacy 模式链接导入目标 `protobuf::libprotobuf`，并把代码生成交给 CMake 模块函数 `protobuf_generate(TARGET ...)`（legacy 的 `protobuf_MODULE_COMPATIBLE` 分支则改用 `protobuf_generate_cpp` 变体与 `PROTOBUF_LIBRARIES` 变量）。MSVC 下还有一段把 `/MD` 运行时替换为 `/MT` 的循环，与 `protobuf_MSVC_STATIC_RUNTIME` 配合。

## Makefile：protoc_middleman 与多语言 --*_out

Makefile 是最直观的"protoc 驱动"构建（F-TST-062）。语言目标全集：

```make
cpp:    add_person_cpp    list_people_cpp
dart:   add_person_dart   list_people_dart
go:     add_person_go     list_people_go
gotest: add_person_gotest list_people_gotest
java:   add_person_java   list_people_java
python: add_person_python list_people_python
ruby:   add_person_ruby   list_people_ruby
```

三个中间目标（middleman）各自负责一部分语言的代码生成（F-TST-062）：

```make
protoc_middleman: addressbook.proto
	protoc $$PROTO_PATH --cpp_out=. --java_out=. --python_out=. addressbook.proto
	@touch protoc_middleman
```

```make
protoc_middleman_dart: addressbook.proto
	mkdir -p dart_tutorial # make directory for the dart package
	protoc -I ../src/:. --dart_out=dart_tutorial addressbook.proto ../src/google/protobuf/timestamp.proto
	pub get
	@touch protoc_middleman_dart
```

```make
protoc_middleman_ruby: addressbook.proto
	protoc $$PROTO_PATH --ruby_out=. addressbook.proto
	@touch protoc_middleman_ruby
```

`protoc_middleman` 一次调用同时产出 C++/Java/Python 三种代码（`--cpp_out=. --java_out=. --python_out=.`）；Dart 中间目标额外把 `../src/google/protobuf/timestamp.proto` 一并传入（满足 schema 对 WKT 的 import），Go 则有独立规则并指定路径风格（F-TST-062）：

```make
go/tutorialpb/addressbook.pb.go: addressbook.proto
	mkdir -p go/tutorialpb # make directory for go package
	protoc $$PROTO_PATH --go_opt=paths=source_relative --go_out=go/tutorialpb addressbook.proto
```

`--go_opt=paths=source_relative` 使生成文件路径保持与源 .proto 相对结构一致。C++ 的编译链接走 pkg-config（F-TST-062）：

```make
add_person_cpp: add_person.cc protoc_middleman
	pkg-config --cflags protobuf  # fails if protobuf is not installed
	c++ add_person.cc addressbook.pb.cc -o add_person_cpp `pkg-config --cflags --libs protobuf`
```

Java / Python / Ruby 的语言目标只产出快捷 shell 脚本（如 `add_person_python` 内部执行 `./add_person.py "$@"`），Go 目标则 `cd go && go build`（F-TST-062）。

## Bazel：bazel build :all

Bazel 路径完全不经手写 protoc 调用。README 记录的命令（F-TST-064）：

```sh
$ bazel build :all
$ bazel-bin/add_person_cpp addressbook.data
```

BUILD.bazel 中的层次是规则链：`proto_library`（`addressbook_proto`，deps 指向 `@com_google_protobuf//:timestamp_proto`）→ 各语言 `cc_proto_library` / `java_proto_library` / `java_lite_proto_library` / `py_proto_library`（`addressbook_cc_proto` / `addressbook_java_proto` / `addressbook_java_lite_proto` / `addressbook_py_pb2`）→ 各语言二进制目标（`add_person_cpp`、`add_person_java`、`py_binary add_person` 等）。其中 C++ 二元的 deps 还显式包含 `@com_google_protobuf//src/google/protobuf/util:time_util`（对应教程中的 TimeUtil）。该文件同时示范了 Java 普通版与 lite 版共用同一份源码（`AddPerson.java`）的双目标写法，以及 `pkg_files` 源分发清单。`build_test(name = "test", ...)` 聚合三个代表性目标做编译性验证。

## pubspec 与 go 子目录

Dart 侧的依赖声明在 pubspec.yaml（F-TST-065、F-TST-062 中 `pub get` 的对象）：

```yaml
name: addressbook
description: dartlang.org example code.

dependencies:
  protobuf:
```

Go 侧代码位于 go/ 子目录（`go/cmd/add_person/add_person.go`、`go/cmd/list_people/list_people.go` 与 `go/go.mod`、`go/go.sum`），由 Makefile 的 go 目标或 `go test ./cmd/add_person`（gotest 目标）驱动（F-TST-062、F-TST-065）。README 对 Go 的安装前提记录为 `go install google.golang.org/protobuf/cmd/protoc-gen-go@latest`（F-TST-064）。

## 跨语言互操作

四套构建体系最终服务于同一个演示点：所有语言的 add_person / list_people 操作同一种 wire format 文件。README 原句（F-TST-063）：

> The examples use the exact same format in all three languages, so you can, for example, use add_person_java to create an address book and then use list_people_python to read it.

即"用 add_person_java 创建通讯录，再用 list_people_python 读取"。这依赖两点：[addressbook.proto](/examples/01-addressbook-proto.md) 中按语言定制的文件级 option 让各语言生成代码落到各自的命名空间，而编码本身由统一的 [wire format](/concepts/02-wire-format.md) 保证与语言无关——这也正是 [C++](/examples/02-cpp-tutorial.md)、[Python](/examples/03-python-tutorial.md)、[Java/Ruby/Dart](/examples/04-java-ruby-dart-tutorials.md) 三篇教程可以互相读写 `addressbook.data` 的原因。

## 相关概念

- [仓库总览与双构建系统](/concepts/00-repo-overview-and-build-systems.md)——examples 的四套入口在主仓 Bazel/CMake 双一等公民构建体系中的位置。
- [protoc 命令行与编译管线](/concepts/07-protoc-command-line.md)——`--cpp_out`/`--go_opt` 等 flag 的解析与输出指令机制。
- [代码生成器体系与各语言实现](/concepts/09-code-generators.md)——`--*_out` 背后的内置生成器家族。
