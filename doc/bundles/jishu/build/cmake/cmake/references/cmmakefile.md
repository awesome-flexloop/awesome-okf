---
type: reference
title: "cmMakefile：目录级执行上下文"
description: "cmMakefile 类作为单目录执行上下文的信源登记，记录变量/属性作用域、命令执行入口、子目录管理"
sources:
  - path: "external/libs/tools/CMake/Source/cmMakefile.h"
    facts: [F-083, F-084, F-085, F-086, F-087, F-089, F-090, F-092]
  - path: "external/libs/tools/CMake/Source/cmMakefile.cxx"
    facts: [F-088, F-091, F-093, F-094, F-095, F-096, F-097]
---

# cmMakefile：目录级执行上下文

## 信源概述

| 信源 | 类型 | 核心职责 |
|------|------|----------|
| `Source/cmMakefile.h` | 头文件 | cmMakefile 类声明、变量/属性 API |
| `Source/cmMakefile.cxx` | 实现文件 | 命令分发执行、变量管理、文件解析 |

## 关键事实登记

### F-083：cmMakefile 是单目录的执行上下文

**信源**：`Source/cmMakefile.h`

每个 `add_subdirectory()` 调用创建一个新的 `cmMakefile` 实例，代表该子目录的执行上下文。持有：
- `cmStateSnapshot Snapshot` — 当前目录的状态快照
- `cmGlobalGenerator* GlobalGenerator` — 回指全局生成器
- `std::vector<std::unique_ptr<cmCommand>> Commands` — 脚本中 function()/macro() 定义的自定义命令
- `cmListFileBackentr Backentr; // 解析回指`

### F-084：ReadListFile 解析并执行 CMakeLists.txt

**信源**：`Source/cmMakefile.cxx`

`bool ReadListFile(const std::string& filename, bool NO_POLICY_SCOPE = false, std::string* errorString = nullptr);`

1. 调用 cmListFile 解析器 tokenize 文件
2. 遍历解析后的命令列表
3. 对每个命令调用 `ExecuteCommand()`
4. 记录执行的 ListFile 到快照中

### F-085：变量管理 API

**信源**：`Source/cmMakefile.h`

```cpp
void AddDefinition(const std::string& name, const char* value);
const char* GetDefinition(const std::string& name) const;
void RemoveDefinition(const std::string& name);
bool IsSet(const std::string& name) const;
```

变量通过快照链查找（见 cmStateSnapshot），`AddDefinition` 在当前作用域设置。

### F-086：ConfigureString 变量替换

**信源**：`Source/cmMakefile.cxx`

`void ConfigureString(const std::string& input, std::string& output, bool escapeQuotes, bool atOnly);`

将 `${VAR}` 和 `@VAR@` 替换为变量值，用于 `configure_file()` 和 `string(CONFIGURE)` 实现。

### F-087：AddSubDirectory 创建子目录上下文

**信源**：`Source/cmMakefile.cxx`

`bool AddSubDirectory(const std::string& sub_dir, bool excludeFromAll);`

1. 创建新的 cmStateSnapshot（BuildsystemDirectory 类型）
2. 创建新的 cmMakefile 实例
3. 调用子目录的 `ReadListFile()`
4. 执行后将子目录的目标/测试合并到全局

### F-089：Properties 分层存储

**信源**：`Source/cmMakefile.h`

CMake 属性系统分为多层：
- 全局属性（`cmake --help-property-list`）
- 目录属性（`set_directory_properties()`）
- 目标属性（`set_target_properties()`）
- 源文件属性（`set_source_files_properties()`）
- 测试属性（`set_tests_properties()`）
- 安装属性
- 缓存变量属性

每层有独立的 GetProperty/SetProperty/AppendProperty API。

### F-090：策略管理

**信源**：`Source/cmMakefile.h`

- `cmPolicies* Policies` — 策略状态
- `void SetPolicy(cmPolicies::PolicyID id, cmPolicies::PolicyStatus status)`
- `cmake_policy(SET CMPxxxx NEW/OLD)` 通过 cmMakefile 执行策略设置

### F-091：缓存变量通过 cmCacheManager 管理

**信源**：`Source/cmMakefile.cxx`

- 缓存变量存储在 `CMakeCache.txt` 中
- `set(... CACHE ...)` 设置缓存变量
- `option(OPT "description" OFF)` 创建布尔缓存变量
- 缓存变量在所有目录间共享，优先级高于普通变量（除非普通变量在当前作用域显式设置）

### F-092：项目信息通过 cmProjectCommand 设置

**信源**：`Source/cmProjectCommand.cxx`

`project(MyProject VERSION 1.0 LANGUAGES CXX C)`：
- 设置 `PROJECT_NAME`、`CMAKE_PROJECT_NAME`
- 设置 `PROJECT_VERSION`、`PROJECT_VERSION_MAJOR/MINOR/PATCH/TWEAK`
- 调用 `EnableLanguage()` 初始化指定语言的编译器检测

### F-097：错误报告通过 IssueMessage

**信源**：`Source/cmMakefile.cxx`

`void IssueMessage(cmake::MessageType t, std::string const& text) const;`

所有命令错误/警告通过此方法统一报告，支持 `dev`/`deprecated`/`author_warning` 等级别过滤。
