---
type: Concept
title: Manifest 语言详解
description: Ninja build.ninja 的完整语法：rule、build、pool、变量系统、作用域链与延迟求值
tags: [ninja, concept, manifest, build.ninja, syntax, rule, build, variable, scope]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Manifest 语言详解

Ninja 的 manifest 文件（通常命名为 `build.ninja`）使用极简的声明式语法描述构建依赖关系。本章详细介绍 manifest 的语法元素、词法规则、变量系统、作用域链和延迟求值机制。

## 语法元素

Ninja manifest 只有七种语法结构：

| 语句 | 用途 | 示例 |
|------|------|------|
| **变量赋值** | 定义字符串变量 | `cflags = -Wall -O2` |
| **rule** | 定义构建命令模板 | `rule cc ...` |
| **build** | 声明一条构建边（输入→输出转换） | `build main.o: cc main.c` |
| **pool** | 定义并发控制池 | `pool link_pool` / `depth = 2` |
| **default** | 指定默认构建目标 | `default main` |
| **include** | 包含其他 ninja 文件（同作用域） | `include config.ninja` |
| **subninja** | 包含其他 ninja 文件（子作用域） | `subninja sub/build.ninja` |

此外，`#` 开头的行为注释，空行被忽略。缩进（空格）用于表示块结构（rule/build/pool 块内的缩进行）。

## 词法分析

[Lexer](../references/parser-source.md) 将输入文本分解为 Token 流。核心 Token 类型：

```cpp
enum Token {
  kError = 0,
  kBuild,        // "build" 关键字
  kColon,        // ":"
  kDefault,      // "default" 关键字
  kEquals,       // "="
  kIdentifier,   // 标识符（变量名、规则名、文件名等）
  kInclude,      // "include" 关键字
  kIndent,       // 缩进（块开始）
  kNewline,      // 换行
  kPipe,         // "|" （隐式依赖分隔符）
  kPipe2,        // "||"（order-only 依赖分隔符）
  kPipeAt,       // "|@"（验证依赖分隔符）
  kPool,         // "pool" 关键字
  kRule,         // "rule" 关键字
  kTNewline,     // 块内换行
  kTEquals,      // 块内 "="
  kEOF           // 文件结束
};
```

### 词法要点

- **标识符**：字母、数字、下划线、`.`、`/`、`-`、`+` 等字符组成，可包含路径
- **路径**：支持绝对路径和相对路径，`$` 开头为转义或变量引用
- **空白处理**：行尾空白被忽略，变量值中空格保留（非首字符）
- **换行**：语句结束标记，块内换行（`kTNewline`）表示块内继续

## Rule 定义

`rule` 定义一个命名的命令模板，每个 rule 可以指定多个属性：

```ninja
rule <name>
  command = <shell command>      # 必需：要执行的命令
  description = <text>           # 可选：构建时显示的描述（如 "CC $out"）
  depfile = <path>               # 可选：depfile 路径（GCC -MMD 生成的 .d 文件）
  deps = <gcc|msvc>              # 可选：depfile 格式（gcc=Makefile格式，msvc=/showIncludes）
  generator = <bool>             # 可选：标记为生成器规则（特殊处理）
  restat = <bool>                # 可选：命令执行后重新 stat 输出
  pool = <pool_name>             # 可选：指定执行池
  rspfile = <path>               # 可选：响应文件路径（处理超长命令行）
  rspfile_content = <text>       # 可选：响应文件内容
  dyndep = <path>                # 可选：动态依赖文件路径
```

### command（必需）

`command` 是 rule 唯一必需的属性，指定要执行的 shell 命令。命令中可以使用 `$in`、`$out` 等自动变量和自定义变量：

```ninja
rule cc
  command = gcc -c $cflags $includes -c $in -o $out
  description = CC $out
```

### depfile 与 deps

`depfile` 指定编译器生成的依赖文件路径，`deps` 指定依赖文件格式：

- `deps = gcc`：Makefile 格式（GCC/Clang 的 `-MMD -MF` 输出）
- `deps = msvc`：MSVC `/showIncludes` 输出格式

```ninja
rule cxx
  command = g++ $cflags -MMD -MF $out.d -c $in -o $out
  depfile = $out.d
  deps = gcc
  description = CXX $out
```

首次构建后，Ninja 从 depfile 加载头文件依赖，记录到 `.ninja_deps`，后续构建无需重新运行编译器就能知道头文件变化。详见 [增量构建机制](06-incremental-build.md)。

### generator

`generator = 1` 标记此规则为"生成器规则"，用于重新生成 build.ninja 自身（如 CMake 的重新配置）。generator 规则的输出被特殊处理：在 manifest 重建流程中先执行。

### restat

`restat = 1` 告诉 Ninja：命令执行后重新 stat（检查文件状态）输出文件。如果输出文件的 mtime 没有变化（如重新编译生成了相同内容），则下游目标不会被触发重建。这避免了"无变化重编译风暴"。

```ninja
# 代码生成器可能输出相同内容，使用 restat
rule codegen
  command = generate_code $in > $out
  restat = 1
```

### rspfile / rspfile_content

Windows 和某些链接器对命令行长度有限制（Windows 约 32KB）。`rspfile` 提供响应文件支持：将长参数列表写入临时文件，命令通过 `@rspfile` 引用：

```ninja
rule link
  command = g++ @$rspfile -o $out
  rspfile = $out.rsp
  rspfile_content = $in $ldflags $libs
  description = LINK $out
```

Ninja 会在执行命令前自动创建 rspfile，命令完成后可选择删除或保留（`-d keeprsp`）。

### pool

指定此规则默认使用的 Pool（并发池），build 块中可以覆盖：

```ninja
rule link
  command = g++ $in -o $out
  pool = link_pool
```

## Build 语句

`build` 语句声明一条构建边——如何通过一条命令从输入产生输出：

```
build <outputs>: <rule> <explicit_inputs> | <implicit_deps> || <order_only> |@ <validations>
  <variable> = <value>    # build 块内变量覆盖
```

### 完整语法示例

```ninja
# 基本形式
build main.o: cc main.c

# 带隐式依赖（头文件）
build main.o: cc main.c | main.h util.h

# 带 order-only 依赖（目录必须先创建，但目录变化不触发重编译）
build obj/main.o: cc src/main.c | src/main.h || obj/

# 带验证依赖（构建完成后运行测试）
build main: link main.o |@ test_main

# 带隐式输出（一次命令产生多个文件）
build main.o | main.o.d: cc main.c

# build 块内变量覆盖
build main.o: cc main.c | main.h
  cflags = -O0 -g -DDEBUG    # 覆盖全局/rule 级的 cflags
  includes = -I./include
```

### Build 块变量覆盖

build 块内（缩进的）变量赋值会创建 Edge 级变量绑定，覆盖 rule 级和文件级的同名变量。这是为特定目标定制编译选项的标准方式：

```ninja
cflags = -O2                    # 文件级

rule cc
  command = gcc $cflags -c $in -o $out
  cflags = -Wall                # rule 级（覆盖文件级）

build release.o: cc release.c
  cflags = -O2 -DNDEBUG         # build 级（覆盖 rule 级）

build debug.o: cc debug.c
  cflags = -O0 -g               # build 级（覆盖 rule 级）
```

变量查找优先级：**build 块级 > rule 级 > 文件级**。

## Pool 定义

`pool` 语句定义一个并发控制池，限制使用此池的 Edge 的最大并行执行数：

```ninja
pool <name>
  depth = <N>
```

### 内置 console 池

Ninja 内置一个名为 `console` 的池，深度为 1。分配到 console 池的命令直接连接到终端（标准输入/输出/错误），输出不缓冲，适合需要终端交互的命令：

```ninja
rule configure
  command = cmake ..
  pool = console             # 直接连接终端，显示 CMake 输出
  generator = 1
```

### 自定义 Pool

典型用法是限制链接并发（链接是内存密集型操作，并发过多会耗尽内存）：

```ninja
# 限制链接命令最多并行 2 个
pool link_pool
  depth = 2

rule link
  command = g++ $in -o $out
  pool = link_pool           # 此规则使用 link_pool

# 编译不受限制，使用 -j 指定的全局并行度
rule cc
  command = gcc -c $in -o $out
```

## default 语句

```ninja
default <targets...>
```

指定默认构建目标。如果命令行未指定目标，Ninja 构建 default 指定的目标。多个 `default` 语句是累积的。

```ninja
default main test
default libfoo.a
# ninja → 构建 main、test、libfoo.a
```

如果没有 `default` 语句，Ninja 构建第一个非 `.` 开头的输出。

## include 与 subninja

两种文件包含方式的区别在于**作用域**：

### include：同作用域包含

```ninja
include vars.ninja
```

- 被包含文件的变量绑定和 rule 定义直接进入当前作用域
- 类似 C 的 `#include`，相当于文本替换
- 被包含文件可以访问和修改当前作用域的变量

### subninja：子作用域包含

```ninja
subninja subdir/build.ninja
```

- 创建新的子作用域（child BindingEnv），父级变量可见但不可修改
- 子作用域的变量和 rule 定义不污染父作用域
- 适合组织子目录的构建规则

```
父作用域（build.ninja）
  ├── cflags = -O2 （子作用域可读取）
  ├── subninja sub/build.ninja
  │     └── 子作用域
  │         ├── 可读取父级 cflags
  │         ├── cflags = -O0（覆盖但不影响父级）
  │         └── 定义的 rule 不影响父级
  └── include vars.ninja
        └── 直接在父作用域执行，变量/rule 互相可见
```

## 变量系统

### 变量引用语法

变量使用 `$var` 或 `${var}` 语法引用：

```ninja
cflags = -Wall -O2
build main.o: cc main.c
  cflags = $cflags -g         # 引用 cflags 变量，追加 -g
  out_dir = ${out_dir}/obj    # ${} 花括号语法用于变量名后紧跟非分界符的情况
```

### 转义序列

`$` 在 Ninja 中有特殊含义，以下转义序列用于表示字面字符：

| 转义 | 含义 |
|------|------|
| `$$` | 字面量 `$` |
| `$:` | 字面量 `:`（在 build 行中冒号有特殊含义） |
| `$ ` | 字面量空格（在变量值中） |
| `$\n` | 换行（续行符，用于多行变量值） |

```ninja
# 续行符：$\n 表示换行继续
cflags = -Wall $\
         -O2 $\
         -DNDEBUG
# 等价于 cflags = -Wall -O2 -DNDEBUG

# 字面量 $
dollar = $$

# 文件名中的冒号（Windows 盘符）
build C$:/output/main.o: cc C$:/src/main.c
```

### 自动变量详解

在 build edge 上下文中，以下变量自动可用：

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `$in` | 显式输入 + 隐式依赖（空格分隔） | `main.c util.c` |
| `$out` | 显式输出（空格分隔） | `main.o` |
| `$in_newline` | 同 `$in`，但用换行分隔 | 用于 rspfile |
| `$out_newline` | 同 `$out`，但用换行分隔 | |
| `$depsfile` | depfile 路径（设置 depfile 后可用） | `main.o.d` |
| `$pool` | 当前 edge 的 pool 名称 | `link_pool` |
| `$rspfile` | rspfile 路径 | `main.o.rsp` |

注意：`$in` **不包含** order-only 依赖和验证依赖，它们不传递给命令行。

## 作用域链

Ninja 使用 [BindingEnv](../references/eval-source.md) 实现链式作用域：

```
文件级作用域（State.bindings_）
    │ parent_ = nullptr
    │
    ├── subninja 创建的子作用域
    │     │ parent_ = 文件级
    │     └── Edge 作用域（subninja 内的 build）
    │           │ parent_ = 子作用域
    │
    ├── rule 定义的变量（通过 rule 查找链）
    │
    └── Edge 作用域（build 块内的变量）
          │ parent_ = 文件级（或 subninja 子作用域）
          └── 查找顺序：Edge → rule → 文件级 → parent...
```

变量查找沿 `parent_` 链向上回溯：

```cpp
string BindingEnv::LookupVariable(const string& var) {
  auto it = bindings_.find(var);
  if (it != bindings_.end())
    return it->second;         // 当前作用域找到
  if (parent_)
    return parent_->LookupVariable(var);  // 向上查找
  return "";                   // 未找到，返回空串
}
```

### 作用域层级优先级

```
优先级从高到低：
  1. build 块内变量（Edge.env_ 中的 bindings_）
  2. rule 中的 EvalString 求值（rule 级变量）
  3. 文件级变量（State.bindings_ 或 subninja 子环境）
  4. 父作用域（include 的文件、subninja 的父环境）
```

## EvalString 延迟求值机制

[EvalString](../references/eval-source.md) 是 Ninja 实现延迟求值的关键。它将包含变量引用的字符串解析为"文本片段 + 变量引用"的列表，等到实际需要时才在特定环境中求值。

### 为什么需要延迟求值？

Rule 中的 `command = gcc $cflags -c $in -o $out` 在解析 rule 时，`$cflags`、`$in`、`$out` 的值都还不知道：
- `$cflags` 可能在 build 块中被覆盖
- `$in`/`$out` 是自动变量，只有在具体 build edge 中才有值

因此，解析时不能立即替换变量，必须等到 Edge 执行前才求值。

### EvalString 内部表示

```cpp
class EvalString {
  vector<pair<string, bool>> parsed_;
  // 每个元素是 (文本, 是否为变量引用)
  // 例如 "gcc $cflags -c $in -o $out" 解析为：
  //   ("gcc ", false), ("cflags", true), (" -c ", false),
  //   ("in", true), (" -o ", false), ("out", true)
};
```

### 求值过程

```cpp
string EvalString::Evaluate(Env* env) const {
  string result;
  for (auto& [text, is_var] : parsed_) {
    if (is_var) {
      if (text == "in")           result += edge->GetIn();       // 自动变量
      else if (text == "out")     result += edge->GetOut();
      // ... 其他自动变量
      else                        result += env->LookupVariable(text);
    } else {
      result += text;             // 字面文本直接追加
    }
  }
  return result;
}
```

### 解析时机

- **解析阶段**（ManifestParser）：Lexer::ReadEvalString 将文本解析为 EvalString 的 parsed_ 列表，但不进行变量替换
- **执行阶段**（StartEdge）：Edge::EvaluateCommand() 在 Edge 的 env_ 环境中调用 EvalString::Evaluate()，此时所有变量都有确定值

这种"解析-求值分离"设计使得 build 块变量覆盖成为可能。

## 完整示例：带变量、隐式依赖、Pool 的 build.ninja

```ninja
# ============ 变量定义 ============
builddir = build
cc = gcc
cflags = -Wall -Wextra -O2
ldflags =
includes = -Iinclude

# ============ Pool 定义 ============
pool link_pool
  depth = 2    # 链接最多并行 2 个

# ============ Rule 定义 ============
rule cc
  command = $cc $cflags $includes -MMD -MF $out.d -c $in -o $out
  depfile = $out.d
  deps = gcc
  description = CC $out

rule link
  command = $cc $in $ldflags -o $out
  description = LINK $out
  pool = link_pool

rule ar
  command = ar rcs $out $in
  description = AR $out

# ============ 构建边 ============
# 编译源文件
build $builddir/main.o: cc src/main.c | include/main.h include/util.h
build $builddir/util.o: cc src/util.c | include/util.h
build $builddir/foo.o: cc src/foo.c | include/foo.h

# 特殊目标使用不同编译选项
build $builddir/debug_main.o: cc src/main.c | include/main.h
  cflags = -Wall -O0 -g -DDEBUG    # 覆盖 cflags

# 静态库
build $builddir/libutil.a: ar $builddir/util.o $builddir/foo.o

# 链接可执行文件
build $builddir/main: link $builddir/main.o $builddir/debug_main.o | $builddir/libutil.a
  ldflags = -L$builddir -lutil

# 默认目标
default $builddir/main

# 子目录（假设有 src/math/build.ninja）
# subninja src/math/build.ninja
```

## 相关概念

- [快速开始](01-getting-started.md) — 第一个 build.ninja 和基本命令
- [架构总览](02-architecture-overview.md) — 解析器在架构中的位置
- [依赖图模型](03-dependency-graph.md) — build 语句如何映射到 Node/Edge
- [增量构建机制](06-incremental-build.md) — depfile/deps 的工作原理
- [并行执行与并发控制](07-parallel-execution.md) — Pool 的运行时效果
- [变量求值 API](../references/eval-source.md) — Rule、BindingEnv、EvalString 的完整 API
- [Manifest解析器 API](../references/parser-source.md) — ManifestParser、Lexer 的完整 API
