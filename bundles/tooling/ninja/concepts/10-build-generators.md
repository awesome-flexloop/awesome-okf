---
type: Concept
title: 构建生成器集成
description: CMake/Meson/gn 等元构建系统如何生成 Ninja 文件，编写自定义生成器的最佳实践
tags: [ninja, concept, build-generator, cmake, meson, gn, metabase, code-generation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 构建生成器集成

Ninja 的设计哲学是"极简执行引擎"——它故意不提供条件语句、循环、函数等高级特性。复杂的构建逻辑应该由**元构建系统**（构建生成器）处理，生成器负责计算依赖、平台适配、配置管理，输出 Ninja 可以高效执行的 `build.ninja` 文件。

## 为什么 Ninja 文件不手写？

Ninja 的 manifest 语法极简，这是有意的设计决策：

1. **无逻辑能力**：没有 if/else、循环、函数、字符串操作，无法表达复杂构建逻辑
2. **无内置编译器规则**：不像 Make 有内置的 `.c.o` 隐式规则，所有命令必须显式写出
3. **平台差异处理困难**：Windows/POSIX 的路径、编译器标志、命令语法差异需要外部处理
4. **依赖计算复杂**：头文件依赖、库依赖、传递依赖需要图算法计算
5. **配置管理**：构建类型（Debug/Release）、选项开关、特性检测需要配置系统

手写 Ninja 文件只适合极其简单的场景。实际项目中，Ninja 文件总是由生成器产生。

```
┌──────────────┐    配置/生成    ┌──────────────┐    执行    ┌──────────┐
│ 元构建系统    │ ─────────────→ │ build.ninja   │ ────────→ │  Ninja   │
│ (CMake/Meson│                │ (机器生成)     │           │ (执行)   │
│  /gn)       │                └──────────────┘           └──────────┘
└──────────────┘                      ↑
       ↑                              │
       │ 生成                         │ 自举重建
       │                              │
┌──────────────┐                ┌──────────────┐
│ 源代码/配置   │                │  重新生成规则  │
│ (CMakeLists  │                │ (generator    │
│  /meson.build│                │  rule)        │
│  /BUILD.gn)  │                └──────────────┘
└──────────────┘
```

## CMake 集成

CMake 是最广泛使用的 Ninja 文件生成器。

### 基本用法

```bash
# 配置项目，生成 build.ninja
cmake -G Ninja -Bbuild -DCMAKE_BUILD_TYPE=Release

# 构建（自动调用 ninja）
cmake --build build

# 或直接调用 ninja
ninja -C build
```

### CMake 生成的 Ninja 文件结构

CMake 生成的 `build.ninja` 通常包含：

1. **变量定义**：编译器路径、编译标志、链接标志等
2. **规则定义**：C 编译、C++ 编译、链接、自定义命令等
3. **Pool 定义**：链接池等
4. **构建边**：每个源文件的编译、每个目标的链接
5. **生成器规则**：用于重新运行 CMake（当 CMakeLists.txt 变化时）
6. **include 语句**：包含其他生成的 ninja 文件（如 `CMakeFiles/rules.ninja`）

典型的 CMake 生成规则：

```ninja
# CMake 生成的重建规则
rule RERUN_CMAKE
  command = cmake -S$cmake_source_dir -B$cmake_build_dir
  generator = 1
  depfile = $out
  pool = console

build build.ninja: RERUN_CMAKE | CMakeCache.txt
```

这使得 Ninja 在检测到 `CMakeLists.txt` 变化时，会先重新运行 CMake 生成新的 `build.ninja`，然后重新构建。

### 常用 CMake 配置

```bash
# 指定构建类型
cmake -G Ninja -Bbuild -DCMAKE_BUILD_TYPE=Debug
cmake -G Ninja -Bbuild -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake -G Ninja -Bbuild -DCMAKE_BUILD_TYPE=Release

# 指定编译器
cmake -G Ninja -Bbuild -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++

# 设置 Ninja 并行数（通过 CMAKE_MAKE_PROGRAM 传递参数不行，通常通过 -j）
ninja -C build -j8

# 导出编译数据库
cmake -G Ninja -Bbuild -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
# 或构建后用 ninja -t compdb
ninja -C build -t compdb CC CXX > build/compile_commands.json

# 安装
cmake --install build
```

### CMAKE_MAKE_PROGRAM

`CMAKE_MAKE_PROGRAM` 变量指定 Ninja 可执行文件路径。如果 Ninja 不在 PATH 中，可以设置：

```bash
cmake -G Ninja -Bbuild -DCMAKE_MAKE_PROGRAM=/path/to/ninja
```

### CMake + Ninja 的优势

- **自动头依赖**：CMake 自动添加 `deps = gcc/msvc` + `depfile =` 配置
- **正确的 Pool 设置**：CMake 自动为链接命令设置 Pool（可选）
- **响应文件支持**：CMake 自动处理 Windows 长命令行问题
- **并行优化**：正确的依赖关系使 Ninja 可以最大化并行度
- **跨平台**：同一套 CMakeLists.txt 在 Windows/Linux/macOS 上生成正确的 Ninja 文件

## Meson 集成

[Meson](https://mesonbuild.com/) 是一个较新的构建系统，原生使用 Ninja 作为后端。

### 基本用法

```bash
# 配置项目（自动选择 Ninja 后端）
meson setup builddir

# 构建
meson compile -C builddir
# 或直接 ninja
ninja -C builddir
```

Meson 的特点：
- 默认后端就是 Ninja，不需要 `-G` 参数
- 更快的配置速度（相比 CMake）
- 更现代的构建描述语言（Python-like DSL）
- 原生支持交叉编译
- 内置测试、安装、打包功能

### Meson 生成的 Ninja 文件

Meson 生成的 ninja 文件通常比 CMake 更简洁，组织在 `builddir/build.ninja` 中，并 include 多个子文件。Meson 自动处理：
- 编译器检测和标志
- 依赖检测（pkg-config、CMake packages）
- 头文件依赖追踪
- 链接依赖（包括传递依赖）
- rpath 设置
- 响应文件

```bash
# Meson 配置选项
meson setup builddir --buildtype=debugoptimized
meson setup builddir -Dprefix=/usr/local
meson configure builddir -Dbuildtype=release
```

## gn 集成

[gn](https://gn.googlesource.com/gn/)（Generate Ninja）是 Google 开发的元构建系统，用于 Chrome、V8、Fuchsia 等大型项目。

### 基本用法

```bash
# 生成 Ninja 文件
gn gen out/Default

# 构建
ninja -C out/Default
```

gn 的特点：
- **极快的生成速度**：专为大型项目设计，Chrome 的 50000+ 文件可以秒级生成
- **自定义语言**：`.gn` 和 `.gni` 文件使用简单的声明式语言
- **工具链抽象**：支持多种工具链（MSVC、GCC、Clang、交叉编译）
- **目标类型丰富**：`executable`、`shared_library`、`static_library`、`source_set`、`action` 等
- **args.gn**：构建参数通过 `out/Default/args.gn` 文件配置

### BUILD.gn 示例

```python
# BUILD.gn
executable("main") {
  sources = [
    "src/main.c",
    "src/util.c",
  ]
  include_dirs = [ "include" ]
  cflags = [ "-Wall", "-O2" ]
  deps = [ ":mylib" ]
}

static_library("mylib") {
  sources = [ "src/foo.c" ]
}
```

### gn 生成的 Ninja 文件

gn 生成的 ninja 文件组织为：
- `build.ninja`：主文件
- `toolchain.ninja`：工具链定义
- `obj/.../*.ninja`：各个目标的构建边
- 每个目标对应一组 build 语句

gn 对大型项目的优化非常出色：
- 增量生成快：只重新处理变化的 BUILD 文件
- 响应文件自动使用
- 池配置合理
- 支持分布式构建（goma）

## 手写 Ninja 的合理场景

虽然通常不推荐手写 Ninja 文件，但以下场景手写是合理的：

### 1. 极小项目/学习目的

```ninja
# 最小化单文件项目
rule cc
  command = gcc -Wall -O2 -c $in -o $out
rule link
  command = gcc $in -o $out

build main.o: cc main.c
build main: link main.o
default main
```

### 2. 简单的脚本/任务自动化

Ninja 可以作为通用的"文件到文件"的转换引擎：

```ninja
# 编译 Markdown 为 HTML
rule md2html
  command = pandoc $in -o $out
  description = PANDOC $out

build docs/index.html: md2html docs/index.md
build docs/guide.html: md2html docs/guide.md
default docs/index.html
```

### 3. 测试/实验

快速验证 Ninja 的某个特性或行为时，手写最小化的 build.ninja 是最快的方式。

### 4. 生成器自身的引导

如果正在编写一个 Ninja 生成器，可能需要一个手写的 Ninja 文件来引导构建生成器自身（自举）。

## 编写 Ninja 生成器

如果你需要为特定工具或语言编写自定义的 Ninja 文件生成器，以下是基本步骤和最佳实践。

### 基本步骤

```
1. 解析项目配置/描述文件
2. 构建依赖图（内存中）
3. 计算每个目标的命令行
4. 处理平台差异（路径、命令、标志）
5. 生成 rule 定义
6. 生成 build 语句
7. 添加 depfile/deps 配置
8. 添加 Pool 配置
9. 添加 generator 规则（自动重建）
10. 输出 build.ninja
```

### 使用 ninja_syntax.py

Ninja 源码中提供了一个 Python 模块 `misc/ninja_syntax.py`，可以帮助生成格式正确的 Ninja 文件：

```python
# 参考：external/libs/tools/ninja/misc/ninja_syntax.py
import ninja_syntax

with open('build.ninja', 'w') as f:
    n = ninja_syntax.Writer(f)

    # 变量
    n.variable('cc', 'gcc')
    n.variable('cflags', '-Wall -O2')

    # 规则
    n.rule('cc',
           command='$cc $cflags -MMD -MF $out.d -c $in -o $out',
           depfile='$out.d',
           deps='gcc',
           description='CC $out')

    n.rule('link',
           command='$cc $in -o $out',
           description='LINK $out')

    # 构建边
    n.build('main.o', 'cc', 'main.c')
    n.build('util.o', 'cc', 'util.c')
    n.build('main', 'link', ['main.o', 'util.o'])

    # 默认目标
    n.default('main')
```

### 生成器关键实现要点

#### 1. 正确处理 depfile/deps

```python
# C/C++ 编译规则必须配置 depfile
n.rule('cc',
       command='gcc -MMD -MF $out.d -c $in -o $out',
       depfile='$out.d',
       deps='gcc',  # 或 'msvc' 用于 MSVC
       description='CC $out')
```

没有 depfile 配置，Ninja 无法追踪头文件依赖，增量构建会不正确。

#### 2. 设置合理的 Pool

```python
# 限制链接并发
n.pool('link_pool', depth=2)

n.rule('link',
       command='gcc $in -o $out',
       pool='link_pool',
       description='LINK $out')
```

链接操作内存消耗大，设置 Pool 避免 OOM。

#### 3. 使用 rspfile 处理长命令行

```python
n.rule('link',
       command='gcc @$rspfile -o $out',
       rspfile='$out.rsp',
       rspfile_content='$in $ldflags $libs',
       description='LINK $out')
```

Windows 命令行长度限制约 32KB，大型项目的链接命令可能超过此限制。使用 rspfile 是跨平台兼容的最佳实践。

#### 4. 添加 generator 规则实现自举重建

```python
n.rule('configure',
       command='python ./configure.py',
       generator=1,
       pool='console')

n.build('build.ninja', 'configure',
        inputs=['configure.py', 'project.config'],
        implicit=['all', 'source', 'files', 'used', 'by', 'generator'])
```

`generator = 1` 标记此规则为生成器，Ninja 会在构建前先检查是否需要重新生成 build.ninja。

#### 5. 正确处理路径

- 使用 `/` 作为路径分隔符（Ninja 在 Windows 上自动处理）
- 路径中包含空格需要正确处理
- 避免绝对路径（使用相对路径使构建目录可重定位）

#### 6. 处理隐式依赖

```python
# 已知的头文件依赖声明为隐式依赖
# 首次构建后，depfile 会发现更多头文件
n.build('main.o', 'cc', 'main.c',
        implicit=['main.h', 'common.h'])
```

#### 7. 使用 phony 创建别名目标

```python
n.build('all', 'phony', ['main', 'test', 'libfoo.a'])
n.default('all')
```

### 生成器最小实现框架

```python
#!/usr/bin/env python3
"""极简 Ninja 生成器示例"""

import os
import sys

def generate_ninja(sources, output='a.out'):
    rules = {
        'cc': {
            'command': 'gcc -Wall -O2 -MMD -MF $out.d -c $in -o $out',
            'depfile': '$out.d',
            'deps': 'gcc',
            'description': 'CC $out',
        },
        'link': {
            'command': 'gcc $in -o $out',
            'pool': 'link_pool',
            'description': 'LINK $out',
        }
    }

    objects = []
    builds = []

    for src in sources:
        obj = os.path.splitext(src)[0] + '.o'
        objects.append(obj)
        builds.append(f'build {obj}: cc {src}')

    builds.append(f'build {output}: link ' + ' '.join(objects))

    with open('build.ninja', 'w') as f:
        f.write('# Auto-generated by my_generator.py\n\n')

        # Pool
        f.write('pool link_pool\n  depth = 2\n\n')

        # Rules
        for name, attrs in rules.items():
            f.write(f'rule {name}\n')
            for key, value in attrs.items():
                f.write(f'  {key} = {value}\n')
            f.write('\n')

        # Build edges
        for b in builds:
            f.write(b + '\n')
        f.write(f'\ndefault {output}\n')

if __name__ == '__main__':
    sources = sys.argv[1:] or ['main.c']
    generate_ninja(sources)
```

## compile_commands.json 与工具链集成

Ninja 的 `-t compdb` 子命令生成 `compile_commands.json`，这是许多开发工具需要的编译数据库：

```bash
# 生成编译数据库
ninja -t compdb cc cxx > compile_commands.json
```

### 使用 compile_commands.json 的工具

| 工具 | 用途 |
|------|------|
| **clangd** | LSP 服务器（代码补全、跳转、诊断） |
| **clang-tidy** | 静态分析 |
| **include-what-you-use** | 头文件包含优化 |
| **rtags** | 代码索引 |
| **cquery/ccls** | 另一个 C/C++ LSP 服务器 |
| **CodeQL** | 代码安全分析 |

### CMake 自动生成

```bash
# CMake 可以自动生成 compile_commands.json
cmake -G Ninja -Bbuild -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
# 文件位于 build/compile_commands.json
```

### Meson 自动生成

Meson 配置后自动在 builddir 中生成 `compile_commands.json`。

## 最佳实践总结

无论是使用 CMake/Meson/gn 还是编写自定义生成器，生成 Ninja 文件时应遵循以下最佳实践：

### 1. 始终使用 deps + depfile

```ninja
rule cc
  command = gcc -MMD -MF $out.d -c $in -o $out
  depfile = $out.d
  deps = gcc
```

没有 deps/depfile 的规则无法正确追踪头文件依赖，会导致增量构建错误。

### 2. 合理设置 Pool

```ninja
pool link_pool
  depth = <根据内存计算>
```

链接和 LTO 操作使用独立 Pool，避免并发过高导致 OOM。

### 3. 长命令行使用 rspfile

```ninja
rule link
  command = gcc @$rspfile -o $out
  rspfile = $out.rsp
  rspfile_content = $in $ldflags $libs
```

确保在 Windows 和大型项目上不会超出命令行长度限制。

### 4. 添加 generator 自举规则

```ninja
rule regenerate
  command = <重新运行生成器的命令>
  generator = 1
  pool = console
build build.ninja: regenerate | <生成器输入文件>
```

当生成器输入变化时，Ninja 自动重新生成 build.ninja。

### 5. 使用 console 池处理交互命令

```ninja
rule configure
  command = cmake ..
  pool = console
  generator = 1
```

需要终端输出或交互的命令（配置、安装）使用 console 池。

### 6. 对无变化输出使用 restat

```ninja
rule codegen
  command = generate $in -o $out
  restat = 1
```

代码生成器等可能输出相同内容的命令，使用 restat 避免不必要的下游重建。

### 7. 正确处理多输出命令

```ninja
# 一次命令产生多个输出时，显式声明所有输出
build out.o | out.d: cc in.c
```

或使用 dyndep 机制（Fortran 等需要）。

### 8. 使用 relative 路径

生成器应输出相对路径（相对于 build.ninja 位置），使构建目录可以移动。

## 相关概念

- [快速开始](01-getting-started.md) — 从 CMake 生成 Ninja 文件
- [Manifest 语言详解](05-manifest-language.md) — build/rule/pool 的完整语法
- [增量构建机制](06-incremental-build.md) — depfile/deps/restat 的运行时作用
- [并行执行与并发控制](07-parallel-execution.md) — Pool 的配置和使用
- [子命令与工具](08-subcommands-tools.md) — -t compdb 生成编译数据库
- [Ninja 简介](00-introduction.md) — 设计哲学和生态定位
- [主入口 API](../references/main-source.md) — 子命令和工具的源码实现
