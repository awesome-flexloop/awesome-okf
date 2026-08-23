---
type: Concept
title: 快速开始
description: 编译安装 Ninja，编写第一个 build.ninja，掌握基本命令和文件结构
tags: [ninja, concept, getting-started, tutorial, build-ninja, commands]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 快速开始

## 编译安装 Ninja

Ninja 使用 CMake 构建自身，编译安装非常简单：

```bash
# 克隆源码（或下载发布版）
git clone https://github.com/ninja-build/ninja.git
cd ninja

# 使用 CMake 配置并构建
cmake -Bbuild
cmake --build build

# 安装（可选）
cmake --install build
```

编译完成后，`build/` 目录下会生成 `ninja` 可执行文件（Windows 上为 `ninja.exe`）。将其加入 PATH 即可在任意目录使用。

也可以直接从 [GitHub Releases](https://github.com/ninja-build/ninja/releases) 下载预编译的二进制文件，Ninja 只有一个可执行文件，无需额外依赖。

验证安装：

```bash
ninja --version
```

## 第一个 build.ninja

让我们从一个最简单的 C 程序开始，手动编写 `build.ninja`：

**main.c**：

```c
#include <stdio.h>

int main() {
    printf("Hello, Ninja!\n");
    return 0;
}
```

**build.ninja**：

```ninja
# 编译规则：将 .c 文件编译为 .o 目标文件
rule cc
  command = gcc -c $in -o $out
  description = CC $out

# 链接规则：将 .o 文件链接为可执行文件
rule link
  command = gcc $in -o $out
  description = LINK $out

# 编译 main.c 为 main.o
build main.o: cc main.c

# 链接 main.o 为 main 可执行文件
build main: link main.o

# 默认目标：运行 ninja 时构建 main
default main
```

运行构建：

```bash
$ ninja
[1/2] CC main.o
[2/2] LINK main

$ ./main
Hello, Ninja!
```

再次运行（无变化）：

```bash
$ ninja
ninja: no work to do.
```

修改 `main.c` 后再次运行：

```bash
$ ninja
[1/2] CC main.o
[2/2] LINK main
```

Ninja 只重新构建了受影响的目标。

## 基本命令

| 命令 | 说明 |
|------|------|
| `ninja` | 构建默认目标（default 指定的目标） |
| `ninja TARGET` | 构建指定目标 |
| `ninja -j4` | 使用 4 个并行任务构建 |
| `ninja -n` | Dry run，只打印要执行的命令但不实际运行 |
| `ninja -v` | Verbose 模式，显示完整命令行 |
| `ninja -C DIR` | 在指定目录下执行构建（切换到 DIR） |
| `ninja -k N` | 遇到 N 个错误后继续构建（0 表示一直继续） |
| `ninja -f FILE` | 使用指定的 manifest 文件（默认 build.ninja） |
| `ninja -t clean` | 清理构建产物 |
| `ninja -t targets` | 列出所有可用目标 |
| `ninja -d explain` | 解释为什么每个目标被重建（调试增量构建） |

常用组合：

```bash
# 查看将执行什么命令（不实际运行）
ninja -n -v

# 清理后重新构建
ninja -t clean && ninja

# 8 并行构建，出错继续
ninja -j8 -k0

# 查看为什么 main 被重建
ninja -d explain main
```

## build.ninja 文件结构

一个 `build.ninja` 文件由以下几种语句组成：

```ninja
# 这是注释

# 1. 变量赋值
cc = gcc
cflags = -Wall -O2

# 2. 规则定义
rule cc
  command = $cc $cflags -c $in -o $out
  description = CC $out

# 3. 构建边（Build Edge）
build main.o: cc main.c
  cflags = -O0 -g    # build 块内变量，覆盖全局

# 4. 池定义
pool link_pool
  depth = 2

# 5. 默认目标
default main

# 6. 包含其他文件
include config.ninja     # 同一作用域包含
subninja subdir/build.ninja  # 子作用域包含
```

### 语句说明

| 语句 | 作用 | 示例 |
|------|------|------|
| **变量赋值** | 定义字符串变量，`$var` 或 `${var}` 引用 | `cflags = -Wall` |
| **rule** | 定义构建规则（命令模板） | `rule cc` ... `command = ...` |
| **build** | 声明构建边（输入→输出的转换） | `build out.o: cc in.c` |
| **pool** | 定义并发池，限制特定类型命令的并行度 | `pool link_pool` / `depth = 2` |
| **default** | 指定默认构建目标 | `default main` |
| **include** | 包含另一个 ninja 文件（共享作用域） | `include vars.ninja` |
| **subninja** | 包含另一个 ninja 文件（创建子作用域） | `subninja sub/build.ninja` |

## 自动变量

Ninja 在 rule 的 command 和 build 块中提供以下自动变量：

| 变量 | 含义 |
|------|------|
| `$in` | 输入文件列表（空格分隔），包含显式输入和隐式依赖 |
| `$out` | 输出文件列表（空格分隔） |
| `$in_newline` | 输入文件列表（换行分隔），用于响应文件等场景 |
| `$out_newline` | 输出文件列表（换行分隔） |
| `$depsfile` | depfile 文件路径（设置 depfile 后可用） |
| `$pool` | 当前 edge 使用的 pool 名称 |
| `$rspfile` | 响应文件路径（设置 rspfile 后可用） |
| `$rspfile_content` | 响应文件内容（设置 rspfile_content 后可用） |

自动变量仅在 build edge 的上下文中有意义，它们的值由具体的 build 语句决定。

## 从 CMake 生成

在实际项目中，`build.ninja` 几乎总是由元构建系统生成。CMake 是最常用的 Ninja 文件生成器：

```bash
# 创建构建目录并生成 build.ninja
cmake -G Ninja -Bbuild -DCMAKE_BUILD_TYPE=Release

# 构建
ninja -C build

# 或使用 cmake --build（自动调用 ninja）
cmake --build build
```

CMake 会自动：
- 检测编译器并设置正确的编译/链接命令
- 处理头文件依赖（生成 `deps = gcc` + `depfile =` 规则）
- 设置合理的并行度
- 生成 `compile_commands.json`（通过 `-t compdb` 或 CMake 直接生成）

## 带头文件依赖的完整示例

一个更完整的手动示例，展示隐式依赖和 depfile：

```ninja
cflags = -Wall -O2 -MMD -MF $out.d

rule cc
  command = gcc $cflags -c $in -o $out
  description = CC $out
  depfile = $out.d
  deps = gcc

rule link
  command = gcc $in -o $out
  description = LINK $out

build main.o: cc main.c | main.h  # main.h 是隐式依赖
build util.o: cc util.c | util.h main.h
build main: link main.o util.o

default main
```

关键点：
- `-MMD -MF $out.d` 让 GCC 在编译时自动生成 `.d` 依赖文件
- `depfile = $out.d` 告诉 Ninja 从 `.d` 文件加载额外的头文件依赖
- `deps = gcc` 指定 depfile 格式为 GCC Makefile 格式
- `| main.h` 声明初始隐式依赖（首次构建时的头文件）

首次构建后，Ninja 会从头文件依赖中发现更多隐式依赖（如 `stdio.h`），并缓存到 `.ninja_deps` 中。

## 相关概念

- [架构总览](02-architecture-overview.md) — 理解 Ninja 的内部模块
- [Manifest 语言详解](05-manifest-language.md) — rule/build/pool/变量的完整语法
- [增量构建机制](06-incremental-build.md) — depfile/depslog 的工作原理
- [构建生成器集成](10-build-generators.md) — CMake/Meson/gn 如何生成 Ninja 文件
