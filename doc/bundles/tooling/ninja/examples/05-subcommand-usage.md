---
type: Example
title: 子命令实用指南
description: 以多文件C++项目为基础，系统掌握ninja -t子命令的日常使用：targets、commands、deps、inputs、query、graph、clean、compdb、recompact，每个命令附实际输出示例与解释。
tags: [ninja, example, intermediate, subcommands, tools, compdb, graph, query, clean]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 子命令实用指南

Ninja 提供了丰富的 `-t`（tool）子命令，用于查询构建状态、调试依赖关系、生成编译数据库、清理产物等。本示例以 [多文件C++项目](02-cxx-project.md) 为基础，逐一演示日常开发中最常用的子命令。

> **前置知识**：请先完成 [多文件C++项目](02-cxx-project.md) 并确保项目已成功构建。相关概念文档：[子命令与工具](../concepts/08-subcommands-tools.md)。

---

## 0. 准备工作

进入 [02-cxx-project](02-cxx-project.md) 的项目目录（如果已清理则重新构建）：

```shell
$ cd ~/ninja-demo/02-cxx

# 如果尚未构建或已清理，先完整构建
$ ninja
[3/3] LINK main
```

确认构建产物存在：

```shell
$ ls
build.ninja  main  main.cpp  main.o  main.o.d  util.cpp  util.h  util.o  util.o.d
```

---

## 1. ninja -t targets all —— 列出所有构建目标

`targets` 子命令列出构建图中所有可用的目标。

### 列出所有目标

```shell
$ ninja -t targets all
main: phony
main.o: cxx
util.o: cxx
main: link
```

**输出解读**：
- 格式为 `目标名: 规则名`
- `main: phony` 来自 `default main`（Ninja 内部创建了一个 phony 目标）
- `main.o: cxx` 表示 `main.o` 使用 `cxx` 规则构建
- `util.o: cxx` 表示 `util.o` 使用 `cxx` 规则构建
- `main: link` 表示最终的 `main` 可执行文件使用 `link` 规则构建

### 按规则过滤

```shell
$ ninja -t targets rule cxx
main.o: cxx
util.o: cxx
```

只列出使用 `cxx` 规则的目标（即编译步骤）。

### 列出深度为0的目标（默认目标/直接请求的目标）

```shell
$ ninja -t targets depth 0
main: phony
```

默认目标只有 `main`。`main.o` 和 `util.o` 是中间目标，不会在 depth 0 中显示。

### 常用场景

- 想知道某个项目有哪些可构建的目标
- 想确认某个文件是否在构建系统中被追踪
- CI 脚本中遍历目标列表

---

## 2. ninja -t commands \<target\> —— 查看目标的构建命令

`commands` 子命令打印构建指定目标所需的所有命令（递归展开所有依赖）。

### 查看 main 的完整命令链

```shell
$ ninja -t commands main
g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT main.o -MF main.o.d -c main.cpp -o main.o
g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT util.o -MF util.o.d -c util.cpp -o util.o
g++  main.o util.o -o main
```

**输出解读**：按执行顺序列出了构建 `main` 需要的 3 条命令——编译 `main.cpp`、编译 `util.cpp`、链接。

### 对比 ninja -n（干运行）

```shell
$ ninja -n
```

`-n` 只显示**需要执行**的命令（即过期的命令）。`ninja -t commands` 则始终显示**所有**相关命令，无论是否过期：

```shell
$ ninja -n          # 项目已最新，无输出
$ ninja -t commands main   # 始终输出全部命令
g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT main.o -MF main.o.d -c main.cpp -o main.o
g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT util.o -MF util.o.d -c util.cpp -o util.o
g++  main.o util.o -o main
```

### 常用场景

- 想查看某个目标到底会执行什么命令（而不必实际运行或先clean）
- 调试构建规则是否正确展开变量
- 生成命令列表用于外部分析

---

## 3. ninja -t deps \<target\> —— 查看头文件依赖

`deps` 子命令显示 `.ninja_deps` 数据库中记录的隐式依赖（主要是头文件）。

### 查看 main.o 的头依赖

```shell
$ ninja -t deps main.o
main.o: #deps 6, deps mtime 1755820800000000000
    /usr/include/c++/11/iostream
    /usr/include/c++/11/string
    /usr/include/c++/11/bits/...（系统头省略）
    main.cpp
    util.h
```

**输出解读**：
- `#deps 6` 表示 `main.o` 有 6 个隐式依赖
- `deps mtime` 是依赖记录的时间戳
- 列出了所有被 `main.cpp`（递归）包含的头文件
- `util.h` 在列表中——修改 `util.h` 会触发 `main.o` 重编译

### 查看 util.o 的头依赖

```shell
$ ninja -t deps util.o
util.o: #deps 5, deps mtime 1755820800000000000
    /usr/include/c++/11/iostream
    /usr/include/c++/11/string
    util.cpp
    util.h
```

### 查看所有目标的依赖

```shell
$ ninja -t deps
main.o: #deps 6, deps mtime 1755820800000000000
    /usr/include/c++/11/iostream
    /usr/include/c++/11/string
    ...
    main.cpp
    util.h
util.o: #deps 5, deps mtime 1755820800000000000
    /usr/include/c++/11/iostream
    /usr/include/c++/11/string
    util.cpp
    util.h
main: deps not found
```

注意 `main`（链接目标）没有 deps 记录，因为 `link` 规则没有设置 `deps = gcc`。

### 常用场景

- 验证头文件依赖是否被正确捕获
- 排查"修改头文件但没有触发重编译"的问题
- 理解某个 `.o` 文件到底依赖了哪些头文件

---

## 4. ninja -t inputs \<target\> —— 查看目标的所有输入

`inputs` 子命令递归列出构建目标所依赖的所有输入文件（包括源文件、头文件、库等）。

```shell
$ ninja -t inputs main
main.o
util.o
main.cpp
util.cpp
util.h
/usr/include/c++/11/iostream
/usr/include/c++/11/string
/usr/include/c++/11/bits/stringfwd.h
...（更多系统头文件）
```

**输出解读**：
- 首先列出直接依赖的 `.o` 文件
- 然后递归展开 `.o` 的源文件和头文件
- 包括系统头文件（因为 depfile 追踪了它们）

### 与 deps 的区别

| 子命令 | 范围 | 来源 |
|--------|------|------|
| `ninja -t deps <target>` | 单个目标的隐式依赖 | `.ninja_deps` 数据库 |
| `ninja -t inputs <target>` | 递归所有输入文件 | 完整依赖图遍历 |

`inputs` 是更全面的视图——它同时考虑了显式依赖（build 语句中列出的）和隐式依赖（depfile 中的头文件）。

### 常用场景

- 生成源文件列表用于打包/分发
- 确定哪些文件变更会影响某个目标
- 理解项目的完整依赖闭包

---

## 5. ninja -t query \<target\> —— 查询目标的依赖关系

`query` 子命令提供目标依赖关系的双向查询：既显示目标依赖什么（输入），也显示什么依赖目标（输出/反向依赖）。

```shell
$ ninja -t query main
main:
  input: phony
    main: link
      input: main.o
        main.o: cxx
          input: main.cpp
          input: util.h
          ...
      input: util.o
        util.o: cxx
          input: util.cpp
          input: util.h
          ...
```

输出以树形结构展示：
- `main` 依赖 `main.o` 和 `util.o`（以及 phony 包装）
- `main.o` 由 `cxx` 规则从 `main.cpp` 和 `util.h` 等构建
- `util.o` 由 `cxx` 规则从 `util.cpp` 和 `util.h` 等构建

### 查询中间目标

```shell
$ ninja -t query util.h
util.h:
  output: main.o
  output: util.o
```

这个输出告诉我们：`util.h` 被 `main.o` 和 `util.o` 依赖。这就是修改 `util.h` 会重编译两个 `.o` 的原因。

### 查询不存在的目标

```shell
$ ninja -t query nonexistent
ninja: error: unknown target 'nonexistent'
```

### 常用场景

- 快速理解某个文件在依赖图中的位置
- 排查"谁依赖了这个文件"
- 理解构建图的连接关系

---

## 6. ninja -t graph \<target\> —— 生成依赖图并渲染

`graph` 子命令输出 Graphviz DOT 格式的依赖图，可以渲染为可视化图片。这对于理解复杂项目的构建结构非常有用。

### 生成 DOT 文件

```shell
$ ninja -t graph main > deps.dot
$ cat deps.dot
digraph ninja {
rankdir="LR"
node [fontsize=10, shape=box, height=0.25]
edge [fontsize=10]
"main" [label="main"]
"main.o" [label="main.o\ncxx"]
"util.o" [label="util.o\ncxx"]
"main.cpp" [label="main.cpp"]
"util.cpp" [label="util.cpp"]
"util.h" [label="util.h"]
"main" -> "main.o" [label="link"]
"main" -> "util.o" [label="link"]
"main.o" -> "main.cpp" [label="cxx"]
"main.o" -> "util.h" [label="cxx"]
"util.o" -> "util.cpp" [label="cxx"]
"util.o" -> "util.h" [label="cxx"]
}
```

### 渲染为 PNG（需要安装 Graphviz）

```shell
# 安装Graphviz（如果尚未安装）
$ sudo apt install graphviz      # Debian/Ubuntu
$ brew install graphviz          # macOS

# 渲染为PNG
$ dot -Tpng deps.dot -o deps.png
```

生成的 `deps.png` 将显示：

```
main.cpp ──┐                      ┌── main
           ├──→ main.o ──┐        │
util.h ────┘             ├──────→ │
util.cpp ──┐             │        │
           ├──→ util.o ──┘        │
util.h ────┘                      └── (通过link规则)
```

> 实际图形中节点和边带有标签（规则名），箭头方向表示依赖方向。

### 直接一步渲染

```shell
$ ninja -t graph main | dot -Tpng -o deps.png
```

### 常用场景

- 文档化项目构建结构
- 理解复杂项目的依赖拓扑
- 排查意外的依赖关系（为什么A依赖B？）
- 向团队展示构建流程

---

## 7. ninja -t clean —— 清理构建产物

`clean` 子命令删除所有构建产物（即 build 语句中作为输出的文件）。

### 基本清理

```shell
$ ninja -t clean
Cleaning... 6 files.
$ ls
build.ninja  main.cpp  util.cpp  util.h
```

被删除的文件包括：`main`、`main.o`、`main.o.d`、`util.o`、`util.o.d`、`.ninja_deps`/`.ninja_log` 等构建产物。源文件（`main.cpp`、`util.cpp`、`util.h`）和 `build.ninja` 不会被删除。

### 清理指定目标

```shell
$ ninja    # 重新构建
$ ninja -t clean main.o
Cleaning... 1 file.
$ ls *.o
util.o
```

只清理 `main.o` 及其关联文件（`main.o.d`）。注意这不会触发重建，只是删除文件。下次运行 `ninja` 时会重编译 `main.o` 并重链接 `main`。

### clean 机制说明

`ninja -t clean` 的工作原理：
1. 读取 `.ninja_log` 获取所有历史构建输出
2. 删除这些文件（如果存在）
3. 删除 `.ninja_deps` 和 `.ninja_log` 本身

如果 `.ninja_log` 丢失（比如手动删除了），`clean` 只能清理默认目标的产物。在这种情况下可能需要手动清理：

```shell
$ rm -f *.o *.d main .ninja_deps .ninja_log
```

### 常用场景

- 发布前clean build确保没有脏状态
- 调试构建问题时从零开始
- CI流水线中的clean步骤

---

## 8. ninja -t compdb —— 生成 compile_commands.json

`compdb`（compilation database）子命令生成 `compile_commands.json` 文件，这是 Clang 工具链（clangd、clang-tidy、clang-format 等）和各种 IDE/编辑器（VS Code、CLion 等）用于代码补全、静态分析、跳转定义的关键文件。

### 为指定规则生成 compdb

```shell
$ ninja -t compdb cxx > compile_commands.json
$ cat compile_commands.json
[
  {
    "directory": "/home/user/ninja-demo/02-cxx",
    "command": "g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT main.o -MF main.o.d -c main.cpp -o main.o",
    "file": "main.cpp",
    "output": "main.o"
  },
  {
    "directory": "/home/user/ninja-demo/02-cxx",
    "command": "g++ -Wall -Wextra -std=c++17 -O2 -MMD -MT util.o -MF util.o.d -c util.cpp -o util.o",
    "file": "util.cpp",
    "output": "util.o"
  }
]
```

### 为多个规则生成

```shell
$ ninja -t compdb cxx link > compile_commands.json
```

这会包含 `cxx` 和 `link` 规则的所有命令。通常只需要编译规则（`cxx`/`cc`），因为 clangd 等工具只关心编译命令。

### 实际效果

有了 `compile_commands.json` 后：
- **VS Code** + clangd 插件：自动获得代码补全、错误检查、跳转到定义
- **clang-tidy**：静态分析可以正确找到头文件路径
- **include-what-you-use**：可以分析不必要的 `#include`

### 在编辑器中验证

在 VS Code 中安装 clangd 扩展后，打开 `main.cpp`，应该能看到：
- `#include "util.h"` 可以正确跳转
- `make_greeting` 函数有自动补全
- 编译错误实时显示

### 常用场景

- IDE/编辑器代码智能提示的配置
- 静态分析工具（clang-tidy、cppcheck）的输入
- 其他构建系统迁移到 Ninja 的桥梁
- 跨平台开发时确保编译选项一致

---

## 9. ninja -t recompact —— 压缩构建日志

`.ninja_log` 随着多次构建会不断增长，因为每次重编译都会追加新记录。`recompact` 子命令压缩日志，只保留每个输出文件的最新记录。

### 检查日志大小

```shell
$ wc -l .ninja_log
25 .ninja_log    # 多次构建后可能有很多行
```

### 执行压缩

```shell
$ ninja -t recompact
$ wc -l .ninja_log
5 .ninja_log    # 压缩后只剩最新记录
```

### 查看压缩后的日志

```shell
$ cat .ninja_log
# ninja log v5
1755820800000	1755820800500	abc123	main.o	0
1755820800000	1755820800600	def456	util.o	0
1755820800600	1755820800800	789abc	main	0
```

每个输出文件只保留一行最新记录。

### 何时需要 recompact？

- 日常开发中不需要频繁运行，Ninja 会在日志过大时自动触发
- 如果手动检查 `.ninja_log` 发现大量重复条目，可以手动运行
- CI 环境中可以在构建后运行以保持工作目录整洁

---

## 10. 其他有用的子命令

以下子命令在特定场景下也很有用，简要说明：

### ninja -t clean -r \<rule\> —— 按规则清理

```shell
$ ninja -t clean -r cxx
```

只清理使用 `cxx` 规则生成的文件（即 `.o` 和 `.d` 文件）。

### ninja -t msvc —— MSVC 依赖包装

在 Windows + MSVC 平台上使用，用于从 `/showIncludes` 输出中提取头依赖。

### ninja -t deps 工作目录问题

如果在子目录中运行 Ninja（通过 `-C` 参数），`-t deps` 的路径会相对于构建目录：

```shell
$ ninja -C build -t deps
```

### ninja -t targets rule \<rule\> —— 反向查询

前面已演示：列出使用特定规则的所有目标。

---

## 11. 子命令速查表

| 子命令 | 用途 | 示例 |
|--------|------|------|
| `targets [all\|depth\|rule]` | 列出构建目标 | `ninja -t targets all` |
| `commands <target>` | 打印目标的构建命令 | `ninja -t commands main` |
| `deps [target]` | 查看头文件依赖 | `ninja -t deps main.o` |
| `inputs <target>` | 递归列出所有输入 | `ninja -t inputs main` |
| `query <target>` | 查询依赖/被依赖关系 | `ninja -t query util.h` |
| `graph <target>` | 生成Graphviz DOT图 | `ninja -t graph main \| dot -Tpng -o deps.png` |
| `clean [-r rule] [targets]` | 清理构建产物 | `ninja -t clean` |
| `compdb <rules...>` | 生成compile_commands.json | `ninja -t compdb cxx > compile_commands.json` |
| `recompact` | 压缩.ninja_log | `ninja -t recompact` |
| `browse` | 启动Web浏览界面（需要Python） | `ninja -t browse` |

---

## 12. 小结

Ninja 的 `-t` 子命令是日常开发中的瑞士军刀：

| 场景 | 推荐子命令 |
|------|-----------|
| 了解项目有哪些目标 | `targets all` |
| 查看某个目标怎么构建 | `commands <target>` |
| 排查头文件依赖问题 | `deps <target>` |
| 理解完整依赖链 | `inputs <target>`、`query <target>` |
| 可视化依赖关系 | `graph <target>` |
| 从零开始构建 | `-t clean` |
| 配置IDE/编辑器 | `-t compdb` |
| 维护构建日志 | `-t recompact` |

结合 `-d explain`（诊断重建原因）和 `-v`（详细输出），你可以高效地解决绝大多数构建问题。

**返回**：[示例索引](index.md)
