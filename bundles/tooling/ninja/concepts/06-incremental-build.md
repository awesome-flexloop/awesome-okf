---
type: Concept
title: 增量构建机制
description: mtime 脏检测、depfile 头依赖追踪、DepsLog 缓存、restat 优化、命令哈希与 dyndep 动态依赖
tags: [ninja, concept, incremental-build, mtime, depfile, depslog, restat, dyndep, dirty]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 增量构建机制

增量构建是 Ninja 的核心价值所在——只重新构建受变更影响的目标，跳过所有已经是最新的目标。Ninja 通过多层检测机制实现精确的增量判断：mtime 比较、命令哈希检测、头依赖追踪、restat 优化和动态依赖。

## mtime 基础检测

增量构建最基础的判断依据是文件的**修改时间（mtime）**。

### 基本原理

如果输出文件的 mtime **新于或等于**所有输入文件的 mtime，则认为输出是最新的，无需重建。如果输出文件的 mtime **旧于**任何输入文件的 mtime，或输出文件不存在，则需要重建。

```
输入 main.c  (mtime = 100)
输入 main.h  (mtime = 200)  ← 头文件更新了
    │
    ↓ cc 命令
输出 main.o (mtime = 150)  ← 旧于 main.h 的 200，需要重编译！
```

### Node::Stat() 与 StatIfNecessary()

Ninja 通过 [Node::Stat()](../references/graph-source.md) 调用文件系统获取文件的 mtime 和存在状态：

```cpp
bool Node::Stat(DiskInterface* disk_interface, string* err) {
  exists_ = ExistenceStatusUnknown;
  mtime_ = disk_interface_->Stat(path_, err);  // 系统调用 stat()
  if (mtime_ == -1) {
    exists_ = ExistenceStatusMissing;
    mtime_ = 0;
  } else {
    exists_ = ExistenceStatusExists;
  }
  return true;
}
```

为避免对同一文件重复调用 stat()（系统调用开销），[Node::StatIfNecessary()](../references/graph-source.md) 缓存结果：

```cpp
bool Node::StatIfNecessary(DiskInterface* disk_interface, string* err) {
  if (status_known())  // exists_ != ExistenceStatusUnknown
    return true;       // 已经 stat 过，直接返回缓存结果
  return Stat(disk_interface, err);
}
```

这确保了构建过程中每个文件最多进行一次 stat() 系统调用。

## 脏状态计算：DependencyScan::RecomputeDirty

[DependencyScan::RecomputeDirty()](../references/graph-source.md) 是增量构建的核心算法，它递归遍历依赖图，判断哪些 Edge 需要重新执行。

### 递归算法

```
RecomputeDirty(Edge* edge):
  most_recent_input = NULL

  # 第一步：递归处理所有输入
  for each input in edge.inputs_ + edge.implicit_deps_ + edge.order_only_deps_:
    if input.in_edge_ exists (即 input 是构建产物):
      RecomputeDirty(input.in_edge_)  # 递归：生产者先判断
    input.StatIfNecessary()
    if input.mtime() > most_recent_input.mtime():
      most_recent_input = input

  # 第二步：加载头依赖（从 deps log 或 depfile）
  if edge uses deps (deps = gcc/msvc) and !edge.deps_loaded_:
    LoadDepsFromLog(edge)  # 从 .ninja_deps 加载缓存的头依赖
    # 对新加载的头依赖递归处理

  # 第三步：比较输出与输入
  for each output in edge.outputs_:
    output.StatIfNecessary()

    # 判断是否脏
    dirty = false
    if !output.exists():
      dirty = true                           # 输出不存在
    else if most_recent_input.mtime() > output.mtime():
      dirty = true                           # 输入比输出新
    else if command_hash_changed(edge):
      dirty = true                           # 命令行变了
    # (还有 restat、dyndep 等其他判断)

    if dirty:
      output.MarkDirty()
      edge 标记为需要执行
```

### RecomputeOutputDirty：输出脏判断

[DependencyScan::RecomputeOutputDirty()](../references/graph-source.md) 对单个输出进行脏判断，考虑以下因素：

1. **输出文件不存在** → 脏
2. **输入文件比输出新** → 脏
3. **命令行变化** → 脏（通过 BuildLog 中的 command_hash 比较）
4. **depfile 中发现新的头文件依赖** → 可能脏（新头文件的 mtime 可能比输出新）
5. **dyndep 尚未加载** → 可能脏
6. **总是构建（generator 规则）** → 脏

## depfile 机制

对于 C/C++ 项目，头文件依赖是增量构建的关键难点——修改一个 `.h` 文件应该重新编译所有包含它的 `.c` 文件，但 `.h` 文件没有显式出现在 build 语句的输入列表中。

### GCC/Clang 自动生成依赖

GCC 和 Clang 提供 `-MMD -MF <file>` 选项，在编译时自动生成 Makefile 格式的依赖文件：

```bash
gcc -MMD -MF main.o.d -c main.c -o main.o
```

生成的 `main.o.d` 内容：

```makefile
main.o: main.c /usr/include/stdio.h /usr/include/stdlib.h main.h util.h
```

### MSVC /showIncludes

MSVC 使用 `/showIncludes` 选项，在编译输出中以特定格式列出包含的头文件：

```
Note: including file: C:\Program Files\...\stdio.h
Note: including file: C:\...\main.h
```

Ninja 的 `deps = msvc` 解析这种格式。

### Ninja 的 depfile 处理流程

```
首次构建：
  1. build.ninja 中声明 depfile = $out.d, deps = gcc
  2. gcc -MMD -MF main.o.d -c main.c -o main.o（生成 .o 和 .d）
  3. 命令完成后，Ninja 解析 main.o.d
  4. 发现头文件：stdio.h、stdlib.h、main.h、util.h
  5. 将这些头文件加入 Edge 的 implicit_deps_
  6. 检查这些头文件的 mtime 是否比 main.o 新（判断是否需要重建——首次构建不需要，因为刚编译完）
  7. 将依赖关系记录到 .ninja_deps（DepsLog）

后续构建：
  1. 启动时从 .ninja_deps 加载缓存的头依赖（LoadDepsFromLog）
  2. main.o 已经知道它依赖 stdio.h、main.h、util.h 等
  3. 如果 main.h 被修改，RecomputeDirty 发现 main.h.mtime > main.o.mtime
  4. 触发 main.o 重编译
  5. 编译后重新解析 depfile，更新 .ninja_deps 中的依赖列表
```

### depfile 规则配置

```ninja
rule cc
  command = gcc $cflags -MMD -MF $out.d -c $in -o $out
  depfile = $out.d      # 告诉 Ninja depfile 的路径
  deps = gcc            # 告诉 Ninja depfile 的格式（gcc 或 msvc）
  description = CC $out
```

| 属性 | 作用 |
|------|------|
| `depfile` | depfile 文件的路径（通常是 `$out.d`） |
| `deps` | depfile 格式：`gcc`（Makefile 格式）或 `msvc`（/showIncludes 格式） |

如果只设置 `depfile` 不设置 `deps`，Ninja 会每次构建都重新加载 depfile（不缓存到 deps log）。同时设置两者才能启用 DepsLog 缓存。

## deps 日志：.ninja_deps

[DepsLog](../references/logs-source.md) 是头依赖的持久化二进制日志，避免每次启动都重新解析 depfile。

### DepsLog 格式

`.ninja_deps` 使用二进制格式存储：

```
文件头："# ninjadeps\n"（版本标识）
记录条目（追加写入）：
  - 输出路径 ID（4 字节）
  - 输出 mtime（4 字节）
  - 依赖数量（4 字节）
  - 依赖路径列表（每个依赖：路径 ID 4 字节 + mtime 4 字节）
路径表：路径字符串 → 唯一 ID 的映射
```

### DepsLog 生命周期

```
构建启动：
  DepsLog::Load(".ninja_deps") → 加载到内存，建立 Node→Deps 映射

构建过程中：
  Edge 首次编译后 → DepsLog::RecordDeps(output, mtime, deps) → 追加写入

构建结束：
  日志文件关闭

定期维护：
  ninja -t recompact → 清理过时条目，重写日志文件
```

DepsLog 采用**追加写入**策略——新记录追加到文件末尾，旧记录标记为过时但不立即删除。`recompact` 操作会重写文件，只保留最新的记录。

### deps 类型对比

| deps 类型 | 编译器选项 | depfile 格式 | 适用平台 |
|-----------|-----------|-------------|---------|
| `deps = gcc` | `-MMD -MF <file>` | Makefile 格式：`target: dep1 dep2 ...` | GCC、Clang、MinGW |
| `deps = msvc` | `/showIncludes` | 编译器 stderr 输出：`Note: including file: <path>` | MSVC |

## restat 优化

`restat = 1` 是一个重要的优化，用于处理"命令执行后输出文件可能没有实际变化"的情况。

### 问题场景

考虑代码生成器：如果输入的 IDL 文件的注释变了（不影响生成代码），生成器可能输出与之前完全相同的内容。没有 restat 时，即使输出内容相同，输出文件的 mtime 也会被更新（因为重新写入了），导致所有下游目标被不必要地重建。

### restat 工作机制

```
没有 restat：
  命令执行 → 写入输出文件（mtime 更新）→ 下游认为输出变了 → 重建下游

有 restat：
  命令执行 → 写入输出文件（mtime 更新）→ Ninja 重新 stat 输出
  → 如果 mtime 与执行前相同（或内容哈希相同）→ 不标记为脏 → 下游不重建
```

```cpp
// FinishEdge 中的 restat 处理
if (edge->rule_->restat_) {
  for (Node* output : edge->outputs_) {
    TimeStamp old_mtime = output->mtime();
    output->Stat(disk_interface_, err);  // 重新 stat
    if (output->mtime() == old_mtime) {
      // mtime 未变，下游不需要重建
      // 但需要检查：如果依赖变了仍然要标记
    }
  }
}
```

### restat 典型用途

```ninja
# 代码生成器
rule codegen
  command = code_generator $in > $out
  restat = 1
  description = GEN $out

# 配置头文件生成（configure_file 类似功能）
rule configure
  command = cmake -E touch $out  # 或其他生成方式
  restat = 1
```

## 命令哈希检测

Ninja 在 [BuildLog](../references/logs-source.md) 中记录每个输出的**命令哈希值**，用于检测命令行是否变化。

### 为什么需要命令哈希？

假设你修改了编译选项（如从 `-O2` 改为 `-O0 -g`），源文件没有变化，但你仍然希望重新编译。仅仅比较 mtime 无法检测到这种变化。

### BuildLog 记录

每次成功构建一个 Edge，Ninja 记录：

```cpp
struct BuildLog::LogEntry {
  string output;           // 输出文件路径
  uint64_t command_hash;   // 命令字符串的哈希值
  TimeStamp start_time;    // 命令开始时间（用于 ETA）
  TimeStamp end_time;      // 命令结束时间
  TimeStamp mtime;         // 输出文件的 mtime
  bool restat;             // 是否使用了 restat
};
```

`command_hash` 使用 FNVHash 对展开后的命令字符串（所有变量已替换）计算哈希。

### 命令变化检测

在 RecomputeDirty 中：

```
如果 BuildLog 中存在 output 的记录：
  记录的 command_hash ≠ 当前 Edge 的 command_hash
  → 命令变了 → 标记为脏，需要重建
```

这样，修改 `cflags`、添加宏定义、更改链接库等操作都会触发相应的重编译/重链接。

### .ninja_log 二进制格式

`.ninja_log` 同样使用二进制追加格式：

```
文件头："# ninja log v5\n"
记录条目（定长，追加写入）：
  - start_time（4 字节）
  - end_time（4 字节）
  - mtime（4 字节）
  - command_hash（4 字节？实际为变长）
  - output path（字符串，以 \n 分隔）
```

BuildLog 还提供 ETA 预测功能——根据历史执行时间估计剩余构建时间。

## dyndep 动态依赖

Dyndep（Dynamic Dependencies）是 Ninja 最复杂的增量特性，用于在构建过程中发现依赖关系。

### 为什么需要 dyndep？

depfile 机制要求在编译命令执行**之后**才能发现头依赖，但这些依赖不影响当前编译（已经编译完成了），只影响后续增量判断。然而，某些语言（如 Fortran）的模块依赖要求在编译**之前**就知道依赖顺序——Fortran 模块必须在 `use` 它的文件之前编译。

dyndep 解决这个"构建过程中修改依赖图"的问题。

### dyndep 工作流程

```
1. 构建开始前，一个特殊的 dyndep 扫描器扫描 Fortran 源文件
2. 扫描器输出一个 dyndep 文件（特殊格式的 ninja 文件）
3. Ninja 在构建过程中加载 dyndep 文件
4. dyndep 文件可以：
   - 为已有的 Edge 添加隐式输入
   - 为已有的 Edge 添加隐式输出
   - 添加验证依赖
   - 指定 restat 行为
5. Plan 在加载 dyndep 后重新调度受影响的 Edge
```

### dyndep 文件格式

```ninja
# dyndep 文件使用特殊语法
build out.o: dyndep
  restat = 1
  implicit_inputs = mod1.mod mod2.mod
  implicit_outputs = out.mod
```

### dyndep 规则声明

```ninja
rule fortran_scan
  command = scan_fortran_deps $in -o $out
  description = SCAN $in

build main.dd: fortran_scan main.f90
build main.o: fortran main.f90 || main.dd
  dyndep = main.dd       # 指定 dyndep 文件
```

关键：dyndep 文件本身必须是一个 order-only 依赖，确保在编译目标之前先运行扫描器生成 dyndep 文件。

### DyndepsLoaded 处理

[Plan::DyndepsLoaded()](../references/build-source.md) 在 dyndep 文件加载后：
1. 将新发现的隐式输入加入 Edge 的依赖列表
2. 对新输入递归进行脏状态扫描
3. 重新检查 Edge 的就绪状态
4. 如果新依赖满足，Edge 可以进入就绪队列

dyndep 主要用于 Fortran 项目，普通 C/C++ 项目使用 depfile 即可。

## 调试增量构建：-d explain

`ninja -d explain` 是调试增量构建问题的最重要工具。它输出每个目标为什么被重建（或为什么不被重建）的原因：

```bash
$ ninja -d explain
ninja: explain: output main.o of edge CC main.o is dirty
ninja: explain:   command line changed  ← 命令行变了
ninja: explain:   depfile dependency is newer than output  ← 头文件更新了
ninja: explain: output main of edge LINK main is dirty
ninja: explain:   input main.o is dirty  ← 依赖的 main.o 脏了
[1/2] CC main.o
[2/2] LINK main
```

常见的 explain 输出：

| 输出 | 原因 |
|------|------|
| `output doesn't exist` | 输出文件不存在 |
| `command line changed` | 命令哈希与记录不同 |
| `depfile dependency is newer than output` | depfile 中的头文件比输出新 |
| `input is dirty` | 输入本身被标记为脏 |
| `implicit input is dirty` | 隐式依赖脏了 |
| `output is older than most recent input` | 输入文件比输出新 |
| `dyndep pending` | 动态依赖尚未加载 |
| `restat of output changed` | restat 后发现 mtime 变化（特殊情况） |

### 其他 -d 调试选项

```bash
ninja -d stats      # 输出性能统计（metric 信息）
ninja -d keeprsp    # 构建后保留 rspfile（不删除）
ninja -d keepdepfile # 构建后保留 depfile
```

## 增量构建的状态文件

Ninja 在构建目录下维护两个隐藏文件，它们是增量构建的关键状态：

| 文件 | 格式 | 内容 | 删除影响 |
|------|------|------|---------|
| `.ninja_log` | 二进制 | 命令哈希、执行时间、输出 mtime | 重新构建时无法检测命令变化（不会错误构建，但可能遗漏命令变更）；丢失 ETA 数据 |
| `.ninja_deps` | 二进制 | 每个输出的头文件依赖列表 | 首次构建需要重新发现头依赖（通过 depfile），可能需要一次额外构建才能完全恢复 |

> **注意**：删除这些文件不会导致构建错误，只是首次构建会稍慢（需要重新发现依赖和记录命令哈希）。

## 相关概念

- [依赖图模型](03-dependency-graph.md) — Node/Edge 结构与脏状态传播
- [构建执行管线](04-build-execution.md) — FinishEdge 中 depfile 加载和 restat 处理
- [Manifest 语言详解](05-manifest-language.md) — depfile/deps/restat/generator 的语法
- [子命令与工具](08-subcommands-tools.md) — -t recompact、-t deps、-t missingdeps
- [日志系统 API](../references/logs-source.md) — BuildLog、DepsLog、Dyndeps 的完整 API
- [图结构 API](../references/graph-source.md) — DependencyScan 的完整 API
