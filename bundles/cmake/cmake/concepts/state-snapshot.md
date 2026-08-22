---
type: concept
title: "状态快照机制 (cmStateSnapshot)"
description: "cmStateSnapshot 不可变快照树的设计：如何用值语义句柄实现 CMake 作用域隔离、目录遍历和状态回滚"
sources:
  references: [../references/cmstate.md, ../references/cmmakefile.md]
  facts: [F-028, F-029, F-030, F-031, F-032, F-033, F-083]
---

# 状态快照机制 (cmStateSnapshot)

## 核心理解

CMake 的 Configure 阶段本质上是**遍历源码目录树，执行脚本命令，累积构建状态**的过程。`cmStateSnapshot` 是这个过程的核心——它用**轻量值语义句柄**表示执行点，通过**快照树**实现作用域隔离和状态管理。

每个 snapshot 只有 16 字节：
```cpp
class cmStateSnapshot {
  cmState* State;     // 8 字节指针，指向全局状态池
  std::size_t Position; // 8 字节索引，定位到 PositionData[] 中的数据
};
```

## 为什么需要快照？

CMake 的执行路径不是线性的：
- `add_subdirectory(sub)` 进入子目录 → 子目录有独立的变量和目标
- `function(foo) ... endfunction()` 调用时 → 函数内有独立的变量作用域
- `include(file.cmake)` → 被包含文件可以看到当前作用域
- `cmake_policy(PUSH/POP)` → 策略设置可临时更改

如果用全局变量 + 手动保存/恢复，代码极易出错。快照机制通过**写时复制**（Copy-on-Write）语义天然解决这些问题。

## SnapshotType：7 种快照上下文

```cpp
enum class SnapshotType {
  Base,                  // 根快照（CMake 初始化时创建）
  BuildsystemDirectory,  // 目录快照（add_subdirectory 创建）
  FunctionCall,          // 函数调用快照（function() 调用时创建）
  MacroCall,             // 宏调用快照（macro() 调用时创建）
  IncludeFile,           // include() 文件快照
  VariableScope,         // 变量作用域块（cmake_policy(PUSH)、block()）
  PolicyScope,           // 策略作用域
};
```

不同类型决定了**变量查找时的向上路径**（是沿调用栈父链查找，还是沿目录父链查找）。

## 快照树结构

假设项目结构：
```
CMakeLists.txt
├── add_subdirectory(lib)  # lib/CMakeLists.txt
│   └── add_subdirectory(core)  # lib/core/CMakeLists.txt
└── add_subdirectory(app)  # app/CMakeLists.txt
```

Configure 执行时快照树：

```
Position 0: Base (Root)
│
Position 1: BuildsystemDirectory (project root)
│  Variables: PROJECT_NAME, CMAKE_CXX_COMPILER, ...
│  Targets: (none yet)
│
├─ Position 2: BuildsystemDirectory (lib/)
│  │  CallStackParent → 1
│  │  BuildsystemDirectoryParent → 1
│  │
│  ├─ Position 3: FunctionCall (myfunc 被调用时)
│  │  │  CallStackParent → 2
│  │  │  Variables: 函数参数 ARGC/ARGV/arg1,...
│  │  │
│  │  └─ Position 4: VariableScope (函数内 set())
│  │     CallStackParent → 3
│  │     Variables: 局部变量
│  │
│  └─ Position 5: BuildsystemDirectory (lib/core/)
│     CallStackParent → 2
│     BuildsystemDirectoryParent → 2
│
└─ Position 6: BuildsystemDirectory (app/)
   CallStackParent → 1
   BuildsystemDirectoryParent → 1
```

## 变量查找规则

`cmStateSnapshot::GetDefinition(name)` 的查找逻辑是理解 CMake 变量作用域的关键：

```
当前快照 Position → 查找 Variables map
  │
  ├─ 找到 → 返回值
  │
  └─ 未找到 → 根据快照类型决定：
      │
      ├─ FunctionCall/MacroCall/VariableScope/PolicyScope/IncludeFile
      │   → 沿 CallStackParent 链向上递归查找
      │
      └─ BuildsystemDirectory
          → 不沿 CallStackParent 查找（不穿透目录边界）
          → 但目录属性通过 BuildsystemDirectoryParent 向上传播
```

这解释了几个 CMake 行为：

### 行为 1：子目录看不到父目录的普通变量？

不对。`add_subdirectory()` 创建的新 BuildsystemDirectory 快照**确实有自己的 Variables**，但在创建时会从父快照**拷贝**初始变量。子目录中 `set()` 不影响父目录，除非用 `set(... PARENT_SCOPE)`。

```cmake
# 父目录 CMakeLists.txt
set(MY_VAR "parent")
add_subdirectory(child)
message(STATUS ${MY_VAR})  # 仍然是 "parent"，子目录的 set 不影响这里
```

```cmake
# child/CMakeLists.txt
message(STATUS ${MY_VAR})  # "parent"（初始化拷贝）
set(MY_VAR "child")        # 只影响当前目录
set(MY_VAR "to-parent" PARENT_SCOPE)  # 写入父目录的快照
```

### 行为 2：function() 内默认不污染外层

```cmake
set(x "outer")
function(myfunc)
  set(x "inner")           # 只在 FunctionCall 快照内
  message(STATUS ${x})     # "inner"
endfunction()
myfunc()
message(STATUS ${x})       # "outer"，外层不受影响
```

### 行为 3：macro() 不创建独立作用域？

实际上 `macro()` 也创建 MacroCall 快照，但宏内的变量操作会**直接替换字符串**（类似 C 宏预处理），与 function 的作用域行为不同。

## 快照的创建 API

```cpp
// cmState.h
cmStateSnapshot CreateBaseSnapshot();       // 创建根快照
cmStateSnapshot CreateBuildsystemDirectorySnapshot(
    const cmStateSnapshot& parent,         // 父目录快照
    const std::string& sourceDir,
    const std::string& binaryDir);
cmStateSnapshot CreateFunctionCallSnapshot(
    const cmStateSnapshot& parent,         // 调用方快照
    const std::string& functionName);
cmStateSnapshot CreateVariableScopeSnapshot(
    const cmStateSnapshot& parent);
```

每个 Create 方法：
1. 在 `PositionData[]` 中 push 一个新的 `cmStateSnapshotData`
2. 初始化 Variables（从父快照拷贝或空）
3. 设置 CallStackParent / BuildsystemDirectoryParent
4. 返回指向新 Position 的 cmStateSnapshot

## 不可变性与状态回滚

快照机制的一个关键优势是**天然支持状态回滚**：

- `block() ... endblock()`：进入 block 时创建 VariableScope 快照，退出时简单丢弃该 Position
- `cmake_policy(PUSH/POP)`：类似，通过快照实现
- 错误恢复：如果 Configure 过程中某子目录出错，可以丢弃该子目录的快照树

## 与 cmMakefile 的关系

`cmMakefile` 持有一个 `cmStateSnapshot Snapshot` 成员，代表该目录执行上下文的当前快照位置。每次进入子目录或函数调用时，创建新快照 + 新 cmMakefile（或在 cmMakefile 上更新快照位置）。

## 关联概念

- [整体架构](overall-architecture.md) — 快照在整体架构中的位置
- [变量作用域链](variable-scope.md) — 基于快照机制的变量查找详解
- [目录级执行上下文](../references/cmmakefile.md) — cmMakefile 如何使用快照
