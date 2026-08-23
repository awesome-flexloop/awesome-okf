---
type: Example
title: 增量构建与依赖追踪
description: 深入探索Ninja增量构建机制的四个核心场景：源文件修改、头文件修改、restat规则、phony与order-only依赖，配合ninja -d explain和.ninja_log/.ninja_deps工具进行诊断。
tags: [ninja, example, advanced, incremental-build, restat, phony, order-only, deps, explain]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 增量构建与依赖追踪

增量构建是 Ninja 的核心能力——它只重新执行因输入变化而过期的构建步骤，最大程度减少不必要的工作。本示例通过 4 个递进场景，深入讲解 Ninja 的依赖追踪机制。

你将学习：
- 场景1：修改源文件→重编译该文件+重链接
- 场景2：修改头文件→重编译所有包含该头的源文件
- 场景3：`restat` 规则——生成器未改变输出时不触发下游重编译
- 场景4：`phony` 目标与 `order-only` 依赖（如目录创建）
- 使用 `ninja -d explain` 诊断重建原因
- 查看 `.ninja_log` 和 `.ninja_deps`
- 清理后重新构建的完整流程

> **前置知识**：请先完成 [最简构建](01-minimal-build.md) 和 [多文件C++项目](02-cxx-project.md)。相关概念文档：[增量构建](../concepts/06-incremental-build.md)、[依赖图模型](../concepts/03-dependency-graph.md)。

---

## 项目准备

```shell
$ mkdir -p ~/ninja-demo/04-incremental && cd ~/ninja-demo/04-incremental
```

---

## 场景1：修改源文件 → 重编译+重链接

这是最基础的增量构建场景。我们用 C++ 项目来演示。

### 1.1 创建项目文件

**math_utils.h**：

```cpp
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int add(int a, int b);
int multiply(int a, int b);

#endif
```

**math_utils.cpp**：

```cpp
#include "math_utils.h"

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}
```

**main.cpp**：

```cpp
#include <iostream>
#include "math_utils.h"

int main() {
    std::cout << "3 + 4 = " << add(3, 4) << std::endl;
    std::cout << "3 * 4 = " << multiply(3, 4) << std::endl;
    return 0;
}
```

**build.ninja**：

```ninja
cxx = g++
cxxflags = -Wall -std=c++17

rule cxx
  command = $cxx $cxxflags -MMD -MT $out -MF $out.d -c $in -o $out
  description = CXX $out
  depfile = $out.d
  deps = gcc

rule link
  command = $cxx $in -o $out
  description = LINK $out

build main.o: cxx main.cpp
build math_utils.o: cxx math_utils.cpp
build app: link main.o math_utils.o

default app
```

### 1.2 首次构建

```shell
$ ninja
[3/3] LINK app
$ ./app
3 + 4 = 7
3 * 4 = 12
```

### 1.3 修改源文件 math_utils.cpp

我们修改 `add` 函数的实现：

```shell
$ # 使用sed修改：将 return a + b 改为 return a + b + 1（引入bug用于演示）
$ sed -i 's/return a + b;/return a + b + 1;/' math_utils.cpp
```

使用 `-d explain` 查看 Ninja 的决策过程：

```shell
$ ninja -d explain
ninja: explain: output 'math_utils.o' of edge 'cxx' is older than input 'math_utils.cpp'
ninja: explain: output 'app' of edge 'link' is older than input 'math_utils.o'
[2/3] CXX math_utils.o
[3/3] LINK app
```

**关键观察**：
- `main.o` **没有**被重编译！因为它不依赖 `math_utils.cpp`
- `math_utils.o` 被重编译（因为 `math_utils.cpp` 更新了）
- `app` 被重链接（因为 `math_utils.o` 更新了）
- 总共执行了 2 个步骤，而不是全部 3 个

验证变化：

```shell
$ ./app
3 + 4 = 8    # 现在输出8而不是7（因为我们加了1）
3 * 4 = 12
```

恢复正确代码后重新构建：

```shell
$ sed -i 's/return a + b + 1;/return a + b;/' math_utils.cpp
$ ninja
[2/3] CXX math_utils.o
[3/3] LINK app
```

### 1.4 依赖传播链

这个场景展示了 Ninja 依赖图的**脏标记传播**（dirty propagation）：

```
math_utils.cpp (修改 → 变脏)
    ↓
math_utils.o (依赖已变脏 → 重编译 → 变脏)
    ↓
app (依赖已变脏 → 重链接 → 更新)
```

`main.o` 不在这条传播路径上，所以不受影响。

---

## 场景2：修改头文件 → 重编译所有包含该头的源文件

头文件依赖是 C/C++ 项目中最容易出错的地方。在 [多文件C++项目](02-cxx-project.md) 中我们已经使用了 `depfile` + `deps = gcc` 来自动追踪头文件依赖。这里我们深入验证其正确性。

### 2.1 修改 math_utils.h

```shell
$ # 在头文件中添加一个新函数声明
$ sed -i 's/int multiply(int a, int b);/int multiply(int a, int b);\nint subtract(int a, int b);/' math_utils.h
```

查看 Ninja 的决策：

```shell
$ ninja -d explain
ninja: explain: output 'main.o' of edge 'cxx' is older than input 'math_utils.h'
ninja: explain: output 'math_utils.o' of edge 'cxx' is older than input 'math_utils.h'
ninja: explain: output 'app' of edge 'link' is older than input 'main.o'
[2/3] CXX main.o
[3/3] CXX math_utils.o
[... 链接错误：subtract 未定义，这是预期的 ...]
```

**关键观察**：
- **两个** `.o` 文件都被重编译了！因为 `main.cpp` 和 `math_utils.cpp` 都 `#include "math_utils.h"`
- Ninja 通过 `.ninja_deps` 数据库知道哪些 `.o` 依赖 `math_utils.h`
- 这与场景1形成对比：修改 `.cpp` 只影响对应的 `.o`，修改 `.h` 影响所有包含它的 `.o`

> 恢复头文件后继续：将 `int subtract(int a, int b);` 行删除。

### 2.2 查看 .ninja_deps 依赖数据库

使用 `ninja -t deps` 查看持久化的头依赖：

```shell
$ ninja -t deps
main.o: #deps X, deps mtime 1755820800000000000
    /usr/include/c++/.../iostream
    main.cpp
    math_utils.h
    ...
math_utils.o: #deps X, deps mtime 1755820800000000000
    math_utils.cpp
    math_utils.h
    ...
```

可以清楚看到两个 `.o` 都依赖 `math_utils.h`。

### 2.3 手动查看 .d 文件

编译器生成的 `.d` 文件是人类可读的：

```shell
$ cat main.o.d
main.o: main.cpp /usr/include/c++/11/iostream math_utils.h

math_utils.h:
```

这就是 Ninja 获取隐式依赖信息的原始来源。

### 2.4 查看 .ninja_log 构建日志

`.ninja_log` 记录了每次命令执行的起止时间：

```shell
$ cat .ninja_log
# ninja log v5
1755820800000	1755820800500	abc123	main.o	0
1755820800000	1755820800600	def456	math_utils.o	0
1755820800600	1755820800800	789abc	app	0
1755820801000	1755820801500	abc124	main.o	0    # 修改头文件后重编译
1755820801000	1755820801600	def457	math_utils.o	0
1755820801600	1755820801800	789abd	app	0
```

格式为：`开始时间(ms)\t结束时间(ms)\tmtime哈希\t输出路径\t命令哈希`。同一输出文件（如 `main.o`）会有多条记录，对应每次重编译。

---

## 场景3：restat 规则——生成器未改变输出时不触发下游重编译

### 3.1 问题背景

某些构建规则（如代码生成器）可能在**输入没有实质性变化时，输出文件内容不变**。但由于命令重新执行，输出文件的 mtime 总会更新，导致所有依赖该输出的下游目标都被认为过期，引发不必要的级联重编译。

**`restat`** 关键字告诉 Ninja：命令执行完后，重新检查输出文件的 mtime。如果文件内容实际没变（mtime 没变），就不要标记下游为脏。

### 3.2 示例：代码生成器

创建一个模拟代码生成器的项目。假设我们有一个配置文件 `config.txt`，一个生成器脚本 `gen.sh` 根据配置生成 `config.h`。

**项目结构**：

```
04-incremental/
├── config.txt      # 配置文件
├── gen.sh          # 代码生成器
├── main_restat.cpp
└── build.ninja
```

**config.txt**：

```
VERSION=1
MODE=release
```

**gen.sh**（生成器脚本——只有当配置内容变化时才更新输出）：

```bash
#!/bin/bash
# gen.sh：智能代码生成器
# 只有当生成的内容与现有文件不同时，才写入输出文件
input=$1
output=$2

# 生成新内容到临时文件
tmp=$(mktemp)
echo "// Auto-generated from $input" > "$tmp"
echo "#pragma once" >> "$tmp"
while IFS='=' read -r key value; do
    echo "#define $key \"$value\"" >> "$tmp"
done < "$input"

# 只有内容不同时才更新输出文件
if ! cmp -s "$tmp" "$output"; then
    cp "$tmp" "$output"
    echo "  Generated $output (content changed)"
else
    echo "  Generated $output (unchanged, skipped write)"
fi
rm -f "$tmp"
```

```shell
$ chmod +x gen.sh
```

**main_restat.cpp**：

```cpp
#include <iostream>
#include "config.h"

int main() {
    std::cout << "Version: " << VERSION << std::endl;
    std::cout << "Mode: " << MODE << std::endl;
    return 0;
}
```

**build.ninja**（追加到已有内容，或创建新的）：

创建一个新的构建文件来独立演示 restat：

```ninja
# build_restat.ninja —— restat规则演示

cxx = g++
cxxflags = -Wall -std=c++17

# 代码生成规则：gen.sh 可能不修改输出文件内容
# restat=1 告诉Ninja：命令执行后重新stat输出文件，如果mtime未变则下游不重建
rule generate
  command = bash gen.sh $in $out
  description = GEN $out
  restat = 1

rule cxx
  command = $cxx $cxxflags -c $in -o $out
  description = CXX $out

rule link
  command = $cxx $in -o $out
  description = LINK $out

build config.h: generate config.txt
build main_restat.o: cxx main_restat.cpp | config.h
build restat_demo: link main_restat.o | config.h

default restat_demo
```

> 注意这里使用了 `| config.h`（order-only 依赖），因为 `config.h` 是由 generate 规则生成的，我们需要确保它存在，但我们通过 restat 机制处理内容变化。实际场景中 `config.h` 应该是正常输入依赖（在 `:` 前面），这样头文件变化能被检测到。下面会对比两种情况。

### 3.3 首次构建

```shell
$ ninja -f build_restat.ninja
[1/3] GEN config.h
  Generated config.h (content changed)
[2/3] CXX main_restat.o
[3/3] LINK restat_demo
```

### 3.4 重新运行生成器但输出不变

现在我们**不修改** `config.txt`，但强制重新执行生成器（touch config.txt）：

```shell
$ touch config.txt    # mtime更新，但内容不变
$ ninja -f build_restat.ninja -d explain
ninja: explain: output 'config.h' of edge 'generate' is older than input 'config.txt'
[1/1] GEN config.h
  Generated config.h (unchanged, skipped write)
ninja: explain: output 'config.h' of edge 'generate' was dirty but is now clean   # <-- restat的效果！
```

**关键观察**：
- 生成器命令确实执行了（因为 `config.txt` 的 mtime 更新了）
- 但 `gen.sh` 检测到内容没有变化，**没有写入** `config.h`
- `restat = 1` 让 Ninja 在命令执行后重新 stat `config.h`，发现其 mtime 没变
- 因此 Ninja 判断 `config.h` "was dirty but is now clean"
- **下游的 `main_restat.o` 和 `restat_demo` 没有被重建**！这就是 restat 的价值

对比：如果去掉 `restat = 1`：

```ninja
rule generate
  command = bash gen.sh $in $out
  description = GEN $out
  # restat = 1   # 注释掉
```

```shell
$ touch config.txt
$ ninja -f build_restat.ninja -d explain
ninja: explain: output 'config.h' of edge 'generate' is older than input 'config.txt'
[1/3] GEN config.h
  Generated config.h (unchanged, skipped write)
ninja: explain: output 'main_restat.o' of edge 'cxx' is older than input 'config.h'
[2/3] CXX main_restat.o
[3/3] LINK restat_demo
```

没有 restat 时，即使 `config.h` 内容没变，只要 generate 命令被执行了，Ninja 就认为输出变脏，下游会被不必要地重编译。

### 3.5 真正修改配置文件

当配置内容真正变化时：

```shell
$ echo "VERSION=2" > config.txt
$ ninja -f build_restat.ninja -d explain
ninja: explain: output 'config.h' of edge 'generate' is older than input 'config.txt'
[1/3] GEN config.h
  Generated config.h (content changed)
ninja: explain: output 'main_restat.o' of edge 'cxx' is older than input 'config.h'
[2/3] CXX main_restat.o
[3/3] LINK restat_demo
```

这时 `gen.sh` 确实写入了新内容，`config.h` 的 mtime 更新了，restat 检查发现文件变了，下游正确重建。

```shell
$ ./restat_demo
Version: 2
Mode: release    # 等等，这里Mode没了...因为我们覆盖了config.txt
```

> 恢复完整配置：`printf "VERSION=2\nMODE=release\n" > config.txt` 后重新构建。

### 3.6 restat 机制总结

```
输入变化 → 命令执行 → restat检查输出mtime
                          ↓
              ┌───── 输出mtime变了 ─────┐
              ↓                          ↓
         下游需要重建              输出mtime没变 → 下游跳过
       （正常情况）              （restat优化）
```

**典型应用场景**：
- 代码生成器（Protocol Buffers、Flex/Bison、IDL 编译器）
- 复制文件但可能内容不变的规则
- 任何可能"空运行"的生成步骤

---

## 场景4：Phony 目标与 Order-only 依赖

### 4.1 Phony 目标

`phony` 是 Ninja 内置的特殊规则，用于创建**别名目标**或**虚拟目标**。phony 目标不实际执行命令，只是创建一个依赖关系节点。

常见用途：
- 给一组目标起一个简短的别名（如 `all`、`clean`、`test`）
- 声明可选的依赖组
- 处理可能不存在的文件依赖

在 build.ninja 末尾添加：

```ninja
# Phony目标：all 是构建一切的别名
build all: phony app restat_demo

# Phony目标：test 别名（可以添加实际测试命令）
build test: phony run_tests

# 运行测试的规则
rule run_test
  command = echo "Running tests..." && ./app
  description = TEST
build run_tests: run_test app
```

使用：

```shell
$ ninja all         # 构建 app 和 restat_demo
$ ninja test        # 先构建app，再运行测试
[1/1] TEST
Running tests...
3 + 4 = 7
3 * 4 = 12
```

### 4.2 Order-only 依赖（| 语法）

普通依赖（`:` 后面列出的）意味着：如果输入变化，输出必须重建。
**Order-only 依赖**（`|` 后面列出的）只保证**执行顺序**：order-only 依赖必须在目标构建之前完成，但它的变化**不会触发**目标重建。

最典型的用途是**目录创建**。我们需要确保输出目录存在，但目录的 mtime 变化（比如其他文件写入该目录）不应触发重编译。

**build.ninja**（目录创建示例）：

```ninja
# 创建输出目录的规则
rule mkdir
  command = mkdir -p $out
  description = MKDIR $out

# phony目标：代表"build目录已就绪"
build builddir: phony build/
build build/: mkdir

# 使用 order-only 依赖（| builddir）确保目录先创建
# 但目录的mtime变化不会触发重编译
build build/main.o: cxx main.cpp | builddir
build build/math_utils.o: cxx math_utils.cpp | builddir
build build/app: link build/main.o build/math_utils.o | builddir
```

**对比普通依赖 vs order-only 依赖**：

```ninja
# 普通依赖：如果 build/ 目录的 mtime 变化（比如里面多了个文件），main.o 会被重编译
build build/main.o: cxx main.cpp build/    # ❌ 不推荐！

# Order-only依赖：只保证目录存在，目录mtime变化不影响
build build/main.o: cxx main.cpp | builddir  # ✅ 正确
```

### 4.3 演示 Order-only 依赖

我们先在主 build.ninja 中加入目录创建逻辑：

创建一个独立的演示文件：

```ninja
# build_order.ninja —— order-only依赖演示

cxx = g++
cxxflags = -Wall -std=c++17

rule cxx
  command = $cxx $cxxflags -MMD -MT $out -MF $out.d -c $in -o $out
  description = CXX $out
  depfile = $out.d
  deps = gcc

rule link
  command = $cxx $in -o $out
  description = LINK $out

rule mkdir
  command = mkdir -p $out
  description = MKDIR $out

# order-only依赖：目录
build build/: mkdir
build build: phony build/

build build/main.o: cxx main.cpp | build
build build/math_utils.o: cxx math_utils.cpp | build
build build/app: link build/main.o build/math_utils.o | build

default build/app
```

构建：

```shell
$ ninja -f build_order.ninja
[1/4] MKDIR build/
[2/4] CXX build/main.o
[3/4] CXX build/math_utils.o
[4/4] LINK build/app
$ ls build/
app  main.o  main.o.d  math_utils.o  math_utils.o.d
```

现在在 build/ 目录中创建一个无关文件（改变目录的 mtime）：

```shell
$ touch build/some_other_file.txt
$ ninja -f build_order.ninja -d explain
ninja: no work to do.
```

因为 `build`（即 `build/`）是 order-only 依赖，它的 mtime 变化不会触发任何重建。如果我们用的是普通依赖，所有 `.o` 和 `app` 都会被重建。

### 4.4 Phony + Order-only 的组合模式

在真实项目中，常见模式是用 phony 目标聚合一组 order-only 依赖：

```ninja
# 确保所有输出目录存在
build build/: mkdir
build build/obj/: mkdir
build build/bin/: mkdir
build dirs: phony build/ build/obj/ build/bin/

# 所有构建目标都依赖dirs
build build/obj/main.o: cxx main.cpp | dirs
build build/obj/util.o: cxx util.cpp | dirs
build build/bin/app: link build/obj/main.o build/obj/util.o | dirs
```

---

## 5. 完整诊断工具链

### 5.1 ninja -d explain：为什么重建？

这是最常用的诊断工具。任何时候你觉得"为什么 Ninja 重新构建了这个？"都可以加上 `-d explain`：

```shell
$ ninja -d explain
ninja: explain: output 'foo.o' of edge 'cxx' is older than input 'foo.h'
ninja: explain: output 'foo' of edge 'link' is older than input 'foo.o'
```

常见输出信息：

| 消息 | 含义 |
|------|------|
| `older than input 'X'` | 输出比输入X旧，需要重建 |
| `older than most recent input 'build.ninja'` | build.ninja被修改了 |
| `missing output file` | 输出文件不存在（首次构建或被删除） |
| `command line changed` | 规则的command变了 |
| `deps file is missing, needs recompaction` | .ninja_deps需要压缩 |
| `was dirty but is now clean` | restat规则执行后输出未变化 |

### 5.2 ninja -t deps：查看依赖数据库

```shell
$ ninja -t deps                    # 列出所有目标的依赖
$ ninja -t deps main.o             # 只查看main.o的依赖
```

### 5.3 ninja -t inputs：查看所有输入

```shell
$ ninja -t inputs app
main.o
math_utils.o
main.cpp
math_utils.cpp
math_utils.h
/usr/include/c++/11/iostream
...
```

### 5.4 .ninja_log：构建历史

```shell
$ cat .ninja_log       # 查看构建历史
$ ninja -t recompact   # 压缩日志（清理旧的重复条目）
```

---

## 6. 清理后重新构建的完整流程

当需要从零开始（clean build）时：

```shell
$ # 清理所有构建产物
$ ninja -t clean
Cleaning... 8 files.

$ # 确认清理干净
$ ls
build.ninja  config.txt  gen.sh  main.cpp  main_restat.cpp  math_utils.cpp  math_utils.h

$ # 重新构建
$ ninja
[3/3] LINK app

$ # 验证
$ ./app
3 + 4 = 7
3 * 4 = 12
```

`ninja -t clean` 会删除构建图中所有不是源文件的文件（即所有作为 `build` 输出的文件）。它通过遍历 `.ninja_log` 来确定要删除的文件。

如果需要更彻底的清理（包括 `.ninja_deps`、`.ninja_log` 本身），可以手动删除：

```shell
$ rm -rf build/ *.o *.d *.o.d app restat_demo .ninja_deps .ninja_log config.h
$ ls
build.ninja  config.txt  gen.sh  main.cpp  main_restat.cpp  math_utils.cpp  math_utils.h
```

---

## 7. 小结

| 概念 | 关键要点 |
|------|----------|
| 脏标记传播 | 修改源文件→重编译对应.o→重链接，依赖图上不相关节点不受影响 |
| 隐式依赖（depfile/deps） | 编译器生成 `.d` 文件列出头依赖，Ninja 存入 `.ninja_deps`；修改头文件触发所有包含它的.o重编译 |
| restat 规则 | `restat=1` 让命令执行后重新检查输出mtime；内容未变则下游不重建；适用于智能代码生成器 |
| phony 目标 | 创建别名/虚拟目标（all、test等），不执行命令，仅聚合依赖 |
| order-only 依赖（\|） | 只保证执行顺序，不触发重建；用于目录创建等场景 |
| `-d explain` | 诊断"为什么重建/为什么不重建"的首选工具 |
| `.ninja_log` / `.ninja_deps` | 持久化的构建日志和依赖数据库，支持增量判断 |
| `ninja -t clean` | 清理构建产物；`ninja -t recompact` 压缩日志 |

**下一步**：学习 [子命令实用指南](05-subcommand-usage.md) 系统掌握 Ninja 的 `-t` 工具集，将日常诊断工作效率最大化。
