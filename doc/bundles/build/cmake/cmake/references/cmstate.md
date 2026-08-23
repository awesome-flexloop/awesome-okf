---
type: reference
title: "cmState：不可变状态管理核心"
description: "cmState 类与 cmStateSnapshot 快照机制的信源登记，记录 CMake 的目录状态、目标定义、变量存储设计"
sources:
  - path: "external/libs/tools/CMake/Source/cmState.h"
    facts: [F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-036, F-037, F-039, F-040, F-042]
  - path: "external/libs/tools/CMake/Source/cmState.cxx"
    facts: [F-038, F-041, F-043, F-044]
  - path: "external/libs/tools/CMake/Source/cmStateSnapshot.h"
    facts: [F-045, F-046, F-047, F-048]
  - path: "external/libs/tools/CMake/Source/cmStateSnapshot.cxx"
    facts: [F-049, F-050]
---

# cmState：不可变状态管理核心

## 信源概述

| 信源 | 类型 | 核心职责 |
|------|------|----------|
| `Source/cmState.h` | 头文件 | cmState 类声明、SnapshotType 枚举、目录/构建/目标数据结构 |
| `Source/cmState.cxx` | 实现文件 | 快照创建、变量查找、目标注册 |
| `Source/cmStateSnapshot.h` | 头文件 | cmStateSnapshot 轻量句柄声明 |
| `Source/cmStateSnapshot.cxx` | 实现文件 | 快照位置导航、变量/属性访问代理 |

## 关键事实登记

### F-028：cmState 是全局状态存储

**信源**：`Source/cmState.h`

`cmState` 是 CMake 构建过程的全局状态容器，持有：
- `std::unique_ptr<cmStateDirectory> RootDirectory` — 根目录状态
- `std::vector<std::unique_ptr<cmStateSnapshotData>> PositionData` — 快照数据池
- `std::map<std::string, cmTarget*> Targets` — 目标注册表
- `std::map<std::string, cmPropertyDefinition> PropertyDefinitions` — 属性定义表

### F-029：cmStateSnapshot 是不可变值语义

**信源**：`Source/cmStateSnapshot.h`

```cpp
class cmStateSnapshot {
  cmState* State = nullptr;
  std::size_t Position = 0;
public:
  // 值语义：可拷贝、可赋值
  cmStateSnapshot() = default;
  // Position 是 PositionData 数组的索引
};
```

`cmStateSnapshot` 是轻量句柄（8 字节指针 + 8 字节索引），不持有数据所有权。所有操作通过 `Position` 索引定位到 `PositionData` 中的快照数据。

### F-030：SnapshotType 定义快照上下文

**信源**：`Source/cmState.h`

```cpp
enum class SnapshotType {
  Base,       // 基础快照（初始化时）
  BuildsystemDirectory, // 目录级快照（add_subdirectory）
  FunctionCall, // 函数调用快照（function() 调用）
  MacroCall,    // 宏调用快照（macro() 调用）
  IncludeFile,  // include 文件快照
  VariableScope, // 变量作用域快照
  PolicyScope,  // 策略作用域快照
};
```

### F-031：快照形成树形结构

**信源**：`Source/cmStateSnapshot.cxx`

每个快照有 `BuildsystemDirectoryParent`（父目录快照）和 `CallStackParent`（调用栈父快照）。`add_subdirectory()` 创建新的目录快照，`function()`/`macro()` 调用创建新的调用快照。

### F-032：变量查找沿作用域链向上

**信源**：`Source/cmStateSnapshot.cxx`

`GetDefinition(name)` 方法：
1. 在当前 Position 的 `Variables` 中查找
2. 如果当前快照类型是 FunctionCall/MacroCall/VariableScope，则向 CallStackParent 递归查找
3. 到达根快照后停止
4. 如果是目录级快照，父目录查找通过 BuildsystemDirectoryParent 链

### F-033：目录信息存储在 cmStateDirectory

**信源**：`Source/cmState.h`

每个目录快照关联一个 `cmStateDirectory`，存储：
- `CurrentSourceDir` / `CurrentBinaryDir`
- `RelativePathTopSource` / `RelativePathTopBinary`
- `ListFiles`（该目录下处理的 CMakeLists.txt 和 .cmake 文件）
- `Targets`（该目录定义的目标）

### F-034：目标注册通过 AddTarget

**信源**：`Source/cmState.cxx`

`void AddTarget(cmStateSnapshot& snapshot, std::unique_ptr<cmTarget> target);`

目标注册在当前目录快照下，目标名称全局唯一。

## 快照机制关系图

```
Base Snapshot (Position 0)
├── BuildsystemDirectory: / (root CMakeLists.txt)
│   ├── VariableScope: set() / if() 块
│   ├── FunctionCall: 调用 myfunc()
│   │   └── VariableScope: 函数内 set()
│   └── BuildsystemDirectory: sub/ (add_subdirectory)
│       ├── MacroCall: 调用 mymacro()
│       └── ...
```

## 代码引用

```cpp
// cmStateSnapshot.cxx - 变量查找核心逻辑
const char* cmStateSnapshot::GetDefinition(const std::string& name) const {
  auto pos = this->Position;
  while (pos != 0) {
    auto& data = this->State->PositionData[pos];
    auto it = data->Variables.find(name);
    if (it != data->Variables.end()) {
      return it->second.c_str();
    }
    // 根据快照类型决定向上查找路径
    if (data->SnapshotType == SnapshotType::FunctionCall ||
        data->SnapshotType == SnapshotType::MacroCall ||
        data->SnapshotType == SnapshotType::VariableScope) {
      pos = data->CallStackParent;
    } else {
      break; // 目录级快照不沿调用链查找
    }
  }
  // 在根目录查找
  return this->State->RootDirectory->Variables[name].c_str();
}
```
