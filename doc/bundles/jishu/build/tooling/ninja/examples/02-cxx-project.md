---
type: Example
title: 多文件C++项目
description: 构建包含main.cpp、util.cpp和util.h的多文件C++项目，掌握分离编译与链接、depfile头文件依赖追踪、deps = gcc机制以及变量定义。
tags: [ninja, example, intermediate, cpp, depfile, deps-gcc, header-deps, variables]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 多文件C++项目

本示例展示如何使用 Ninja 管理一个典型的多文件 C++ 项目，核心知识点包括：

- 分离编译：每个 `.cpp` 文件独立编译为 `.o`，再统一链接
- **隐式依赖追踪**：通过 `depfile` 和 `deps = gcc` 自动捕获头文件依赖
- 构建变量（`cxxflags`、`ldflags`）的定义与引用
- 查看 `.ninja_deps` 数据库验证头依赖
- 修改头文件后验证增量重编译

> **前置知识**：请先完成 [最简构建](01-minimal-build.md)。相关概念文档：[依赖图模型](../concepts/03-dependency-graph.md)、[增量构建](../concepts/06-incremental-build.md)。

---

## 1. 项目准备

```shell
$ mkdir -p ~/ninja-demo/02-cxx && cd ~/ninja-demo/02-cxx
```

项目结构如下：

```
02-cxx/
├── build.ninja
├── main.cpp
├── util.cpp
└── util.h
```

---

## 2. 创建源文件

### 2.1 util.h —— 工具函数头文件

```cpp
// util.h
#ifndef UTIL_H
#define UTIL_H

#include <string>

// 返回格式化的问候消息
std::string make_greeting(const std::string& name);

// 打印分隔线
void print_separator();

#endif // UTIL_H
```

### 2.2 util.cpp —— 工具函数实现

```cpp
// util.cpp
#include "util.h"
#include <iostream>

std::string make_greeting(const std::string& name) {
    return "Hello, " + name + "!";
}

void print_separator() {
    std::cout << "------------------------" << std::endl;
}
```

### 2.3 main.cpp —— 主程序

```cpp
// main.cpp
#include <iostream>
#include <string>
#include "util.h"

int main() {
    print_separator();
    std::string msg = make_greeting("Ninja C++");
    std::cout << msg << std::endl;
    print_separator();
    return 0;
}
```

---

## 3. 编写 build.ninja

```ninja
# build.ninja —— 多文件 C++ 项目构建文件

# ============================================================
# 变量定义
# ============================================================
cxx = g++
cxxflags = -Wall -Wextra -std=c++17 -O2
ldflags =

# ============================================================
# 规则定义
# ============================================================

# 编译规则：将 .cpp 编译为 .o
#   -MMD -MF $out.d  让编译器自动生成依赖文件(.d)，列出所有源文件包含的头文件
#   depfile = $out.d  告诉 Ninja 从该文件读取额外的隐式依赖
#   deps = gcc       使用 Ninja 内置的 gcc 依赖解析模式，将依赖持久化到 .ninja_deps
rule cxx
  command = $cxx $cxxflags -MMD -MT $out -MF $out.d -c $in -o $out
  description = CXX $out
  depfile = $out.d
  deps = gcc

# 链接规则：将多个 .o 链接为可执行文件
rule link
  command = $cxx $ldflags $in -o $out
  description = LINK $out

# ============================================================
# 构建边
# ============================================================

# 编译 main.cpp → main.o
build main.o: cxx main.cpp
# 编译 util.cpp → util.o
build util.o: cxx util.cpp

# 链接：main 依赖两个 .o 文件
build main: link main.o util.o

# 默认目标
default main
```

### 关键机制解析

#### 3.1 分离编译与链接

与[最简构建示例](01-minimal-build.md)中直接从源文件生成可执行文件不同，这里采用标准的分离编译模式：

1. 每个 `.cpp` 通过 `cxx` 规则编译为独立的 `.o` 目标文件
2. 所有 `.o` 通过 `link` 规则链接为最终可执行文件

这种方式的好处是：修改一个 `.cpp` 只需重编译该文件，其他 `.o` 可以复用。

#### 3.2 头文件依赖追踪（核心难点）

C/C++ 项目中，`.cpp` 文件通过 `#include` 引入头文件。如果只在 `build` 语句中声明 `.cpp` 作为输入，Ninja 无法知道 `.h` 文件的变化。解决方法是 **编译器辅助依赖生成**：

| 元素 | 作用 |
|------|------|
| `-MMD -MF $out.d` | GCC/Clang 编译选项：生成依赖文件，列出该源文件实际包含的所有头文件（不含系统头） |
| `-MT $out` | 指定依赖文件中的目标名称为 `$out`（即 `.o` 文件路径） |
| `depfile = $out.d` | 告诉 Ninja：编译完成后从 `$out.d` 读取隐式依赖（头文件列表） |
| `deps = gcc` | 启用 Ninja 的 deps 日志模式，将头依赖持久化到 `.ninja_deps` 数据库，避免每次重新解析 `.d` 文件 |

当你首次构建后，Ninja 会：
1. 执行编译，编译器生成 `.o` 和 `.d` 文件
2. 读取 `.d` 文件，发现 `main.o` 隐式依赖 `util.h`、`iostream` 等
3. 将这些依赖信息存入 `.ninja_deps`
4. 之后的构建中，Ninja 会检查所有隐式依赖的 mtime

> 关于 deps 模式的深入说明参见 [依赖图模型](../concepts/03-dependency-graph.md#隐式依赖) 和 [增量构建](../concepts/06-incremental-build.md#deps-日志)。

#### 3.3 构建变量

```ninja
cxx = g++
cxxflags = -Wall -Wextra -std=c++17 -O2
```

Ninja 中的变量使用 `=` 定义，通过 `$变量名`（或 `${变量名}`）引用。变量在规则定义和命令中展开。

---

## 4. 执行构建

### 4.1 首次完整构建

```shell
$ ninja
[3/3] LINK main
```

注意构建顺序：先编译两个 `.o` 文件，再链接。Ninja 根据依赖图自动确定执行顺序。

使用 `-v` 查看完整命令：

```shell
$ ninja -v   # 先 ninja -t clean 清理后再运行以看到完整输出
[1/3] g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT main.o -MF main.o.d -c main.cpp -o main.o
[2/3] g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT util.o -MF util.o.d -c util.cpp -o util.o
[3/3] g++  main.o util.o -o main
```

### 4.2 运行程序

```shell
$ ./main
------------------------
Hello, Ninja C++!
------------------------
```

---

## 5. 查看生成的依赖文件

### 5.1 查看 .d 文件（编译器生成）

首次构建后，每个 `.o` 都有对应的 `.d` 文件：

```shell
$ cat main.o.d
main.o: main.cpp /usr/include/c++/11/iostream /usr/include/c++/11/string \
  util.h

util.h:
```

这表明 `main.o` 依赖于 `main.cpp`、`iostream`、`string` 和 `util.h`。Ninja 读取这个文件后就知道头文件变化需要触发重编译。

### 5.2 查看 .ninja_deps（Ninja 持久化数据库）

`deps = gcc` 模式下，Ninja 将依赖信息持久化到 `.ninja_deps` 二进制文件。使用 `ninja -t deps` 查看：

```shell
$ ninja -t deps
main.o: #deps 5, deps mtime 1755820800000000000
    /usr/include/c++/11/iostream
    /usr/include/c++/11/string
    main.cpp
    util.h
    /usr/include/c++/11/...（更多系统头）
util.o: #deps 4, deps mtime 1755820800000000000
    util.cpp
    util.h
    /usr/include/c++/11/iostream
    /usr/include/c++/11/string
```

可以看到 `main.o` 和 `util.o` 都依赖 `util.h`——这正是我们需要的。

> **提示**：`.d` 文件是编译时编译器生成的临时文件，`.ninja_deps` 是 Ninja 维护的持久化数据库。使用 `deps = gcc` 后，即使删除 `.d` 文件，Ninja 也能从 `.ninja_deps` 恢复依赖信息。

---

## 6. 验证增量构建

### 6.1 不修改任何文件

```shell
$ ninja
ninja: no work to do.
```

### 6.2 修改源文件 util.cpp

```shell
$ # 修改 util.cpp，比如在 print_separator 中改变字符
$ sed -i 's/------------------------/========================/' util.cpp
$ ninja -d explain
ninja: explain: output 'util.o' of edge 'cxx' is older than input 'util.cpp'
ninja: explain: output 'main' of edge 'link' is older than input 'util.o'
[2/3] CXX util.o
[3/3] LINK main
```

注意：只重编译了 `util.o` 并重链接 `main`，`main.o` 没有被重编译。

验证输出变化：

```shell
$ ./main
========================
Hello, Ninja C++!
========================
```

### 6.3 修改头文件 util.h

这是最关键的测试——修改头文件应该触发**所有包含该头的源文件**重编译。

```shell
$ # 修改 util.h，比如修改函数签名或添加新函数
$ sed -i 's/std::string make_greeting/std::string make_greeting_v2/' util.h
$ ninja -d explain
ninja: explain: output 'main.o' of edge 'cxx' is older than input 'util.h'
ninja: explain: output 'util.o' of edge 'cxx' is older than input 'util.h'
ninja: explain: output 'main' of edge 'link' is older than input 'main.o'
[2/3] CXX main.o
[3/3] CXX util.o
# 链接错误（因为我们破坏了函数名，这是预期的）
```

可以看到 `main.o` 和 `util.o` 都被重编译了——因为它们都包含 `util.h`。这就是 `depfile` + `deps = gcc` 机制的效果。

> **注意**：先将 `util.h` 和 `util.cpp` 恢复后再继续后续实验。

### 6.4 查看 .ninja_log

`.ninja_log` 记录了每次构建命令的耗时和状态：

```shell
$ cat .ninja_log
# ninja log v5
1755820800	1755820801	12345	main.o	1234567890
1755820800	1755820802	23456	util.o	1234567891
1755820802	1755820803	34567	main	1234567892
```

列格式：`开始时间\t结束时间\tmtime(哈希)\t输出路径\t命令哈希`。更多日志格式说明参见 [日志与状态文件](../references/logs-source.md)。

---

## 7. 清理构建产物

```shell
$ ninja -t clean
Cleaning... 6 files.
$ ls
build.ninja  main.cpp  util.cpp  util.h
```

清理后所有 `.o`、`.d`、`main`、`.ninja_deps`、`.ninja_log` 都被删除。

> `ninja -t clean` 子命令的更多用法见 [子命令实用指南](05-subcommand-usage.md#ninja--t-clean)。

---

## 8. 完整文件汇总

### util.h

```cpp
#ifndef UTIL_H
#define UTIL_H

#include <string>

std::string make_greeting(const std::string& name);
void print_separator();

#endif
```

### util.cpp

```cpp
#include "util.h"
#include <iostream>

std::string make_greeting(const std::string& name) {
    return "Hello, " + name + "!";
}

void print_separator() {
    std::cout << "------------------------" << std::endl;
}
```

### main.cpp

```cpp
#include <iostream>
#include <string>
#include "util.h"

int main() {
    print_separator();
    std::string msg = make_greeting("Ninja C++");
    std::cout << msg << std::endl;
    print_separator();
    return 0;
}
```

### build.ninja

```ninja
cxx = g++
cxxflags = -Wall -Wextra -std=c++17 -O2
ldflags =

rule cxx
  command = $cxx $cxxflags -MMD -MT $out -MF $out.d -c $in -o $out
  description = CXX $out
  depfile = $out.d
  deps = gcc

rule link
  command = $cxx $ldflags $in -o $out
  description = LINK $out

build main.o: cxx main.cpp
build util.o: cxx util.cpp
build main: link main.o util.o

default main
```

---

## 9. 小结

| 概念 | 本例体现 |
|------|----------|
| 分离编译与链接 | `cxx` 规则编译 `.o`，`link` 规则链接可执行文件 |
| 构建变量 | `$cxx`、`$cxxflags`、`$ldflags` 提取公共配置 |
| 隐式依赖（depfile） | `-MMD -MF $out.d` 让编译器生成头文件依赖列表 |
| deps 模式 | `deps = gcc` 将依赖持久化到 `.ninja_deps`，加速后续构建 |
| 增量构建验证 | 修改 `.cpp` 只重编译对应 `.o`；修改 `.h` 重编译所有包含它的 `.cpp` |
| 调试工具 | `ninja -d explain` 查看重建原因，`ninja -t deps` 查看依赖数据库 |

**下一步**：
- 想深入理解增量构建机制，学习 [增量构建与依赖追踪](04-incremental-deps.md)
- 想了解如何控制并行度和资源池，学习 [并行构建与Pool控制](03-parallel-jobs.md)
- 想掌握各种 `ninja -t` 子命令，学习 [子命令实用指南](05-subcommand-usage.md)
