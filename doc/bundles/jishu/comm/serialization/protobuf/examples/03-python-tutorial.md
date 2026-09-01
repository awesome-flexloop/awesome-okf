---
type: Example
title: "Python 教程：add_person 与 list_people"
description: "讲解 examples 目录 Python 教程双程序：addressbook_pb2 动态模块、people.add()/phones.add() 容器追加与 ParseFromString/SerializeToString。"
tags: [protobuf, examples, python]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
---

examples/ 目录的 Python 教程由 `add_person.py` 与 `list_people.py` 组成（F-REPO-060），与 [C++ 教程](/examples/02-cpp-tutorial.md) 操作完全相同的通讯录文件：add_person 读入 `AddressBook`、交互式追加一个 `Person` 后写回，list_people 读入并打印。二者演示了 Python 运行时最核心的三个 API 形态——动态模块导入、repeated 容器的 `.add()` 追加、字节串级的 `ParseFromString` / `SerializeToString`（F-TST-052、F-TST-053）。

## 生成模块：import addressbook_pb2

Python 侧不链接任何 C++ 库，只需导入 protoc `--python_out` 产出的模块（F-TST-052）：

```python
import addressbook_pb2
import sys
```

`addressbook_pb2` 中的类型在导入时经由运行时 DescriptorPool 建立消息类（其 upb C 扩展内核的机制见 [Python 运行时](/concepts/11-python-runtime.md)）。`add_person.py` 头部还有一段 Python 2/3 兼容处理：

```python
try:
  raw_input          # Python 2
except NameError:
  raw_input = input  # Python 3
```

`list_people.py` 的对应兼容手段则是文件首行的 `from __future__ import print_function`（F-TST-053）。

## add_person.py：写入路径

### 字节串读写：ParseFromString / SerializeToString

Python 侧的 IO 以 bytes 对象为单位（F-TST-052）：

```python
address_book = addressbook_pb2.AddressBook()

# Read the existing address book.
try:
  with open(sys.argv[1], "rb") as f:
    address_book.ParseFromString(f.read())
except IOError:
  print(sys.argv[1] + ": File not found.  Creating a new file.")
```

```python
# Write the new address book back to disk.
with open(sys.argv[1], "wb") as f:
  f.write(address_book.SerializeToString())
```

与 C++ 的 `ParseFromIstream`/`SerializeToOstream` 不同，Python API 直接面对 `f.read()` 得到的完整字节串；文件不存在时同样静默降级为新建空通讯录。

### 容器追加：people.add() 与 phones.add()

repeated 字段在 Python 中表现为支持 `.add()` 的容器（F-TST-052）。向顶层容器追加一个新 Person 的整行是：

```python
# Add an address.
PromptForAddress(address_book.people.add())
```

`people.add()` 无参调用即创建并返回一个空 Person，随后被送入提示函数填充。函数内嵌套 repeated 字段的追加同样如此：

```python
    phone_number = person.phones.add()
    phone_number.number = number
```

标量字段的写入则是普通属性赋值：`person.id = int(raw_input(...))`、`person.name = ...`、`person.email = email`（仅在非空时赋值）。

## 枚举常量：Person.MOBILE / HOME / WORK

PhoneType 枚举以类属性形式暴露在 Person 上（F-TST-052）。写入侧用 if-elif 链把用户输入映射到枚举：

```python
    if type == "mobile":
      phone_number.type = addressbook_pb2.Person.MOBILE
    elif type == "home":
      phone_number.type = addressbook_pb2.Person.HOME
    elif type == "work":
      phone_number.type = addressbook_pb2.Person.WORK
    else:
      print("Unknown phone type; leaving as default value.")
```

注意 `addressbook_pb2.Person.MOBILE` 这类枚举常量既是写入值，也参与读取侧比较。

## list_people.py：读取路径

Python 的 repeated 字段可直接迭代，无需 C++ 那类 `_size()`/索引 API（F-TST-053）：

```python
def ListPeople(address_book):
  for person in address_book.people:
    print("Person ID:", person.id)
    print("  Name:", person.name)
    if person.email != "":
      print("  E-mail address:", person.email)

    for phone_number in person.phones:
      if phone_number.type == addressbook_pb2.Person.MOBILE:
        print("  Mobile phone #:", end=" ")
      elif phone_number.type == addressbook_pb2.Person.HOME:
        print("  Home phone #:", end=" ")
      elif phone_number.type == addressbook_pb2.Person.WORK:
        print("  Work phone #:", end=" ")
      print(phone_number.number)
```

枚举读取以 `phone_number.type == addressbook_pb2.Person.MOBILE` 的相等比较完成，与写入侧常量同源；标量读取仍是属性访问（`person.id`、`person.email`）。main 部分与 add_person 相同的 `ParseFromString(f.read())` 读入后调用 `ListPeople(address_book)`。

## 运行方式

README 记录的 Python 路径（F-TST-064）：先 `pip install protobuf` 安装运行时（并确保运行时版本与 protoc 二进制版本一致），再执行 `make python`——Makefile 中的该目标依赖 `protoc_middleman`（`protoc --python_out=. addressbook.proto` 产出 `addressbook_pb2.py`），随后生成 `add_person_python` / `list_people_python` 两个快捷 shell 脚本（F-TST-062）。Bazel 侧 `py_binary` 目标（`add_person` / `list_people`，python_version = "PY3"）以 `addressbook_py_pb2` 为依赖。

## 相关概念

- [Python 运行时（upb C 扩展）](/concepts/11-python-runtime.md)——`addressbook_pb2` 导入时背后的 DescriptorPool 与 upb 内核。
- [消息模型基础：Message 与 MessageLite](/concepts/01-message-model.md)——与 C++ 侧 API 风格的类层次来源对照。
