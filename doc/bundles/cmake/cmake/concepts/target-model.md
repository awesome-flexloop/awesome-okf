---
type: concept
title: "目标模型 (Target Model)"
description: "CMake 目标（executable/library/custom）的数据模型、属性系统、以及 INTERFACE/PUBLIC/PRIVATE 传播规则"
sources:
  references: [../references/cmstate.md, ../references/cmmakefile.md, ../references/cmdexec.md]
  facts: [F-034, F-089, F-080]
---

# 目标模型 (Target Model)

## 核心理解

CMake 中的**目标（Target）**是构建系统的核心单元。每个 `add_executable()` 或 `add_library()` 调用创建一个 `cmTarget` 对象，代表一个可执行文件、库或自定义构建步骤。目标之间通过 `target_link_libraries()` 建立依赖关系，编译选项、包含目录等属性沿依赖链**自动传播**。

## 目标类型

```cmake
# 可执行文件
add_executable(myapp main.cpp helper.cpp)

# 库
add_library(mylib STATIC lib.cpp)     # 静态库 (.a/.lib)
add_library(mylib SHARED lib.cpp)     # 动态库 (.so/.dll/.dylib)
add_library(mylib MODULE lib.cpp)     # 可加载模块（插件）
add_library(mylib OBJECT lib.cpp)     # 对象库（编译但不归档）
add_library(mylib INTERFACE)          # 头文件-only 库（无源文件）

# 自定义目标
add_custom_target(docs ALL COMMAND doxygen Doxyfile)

# 别名目标
add_library(MyProj::mylib ALIAS mylib)

# 导入目标（外部已构建库）
add_library(ext::lib SHARED IMPORTED)
set_target_properties(ext::lib PROPERTIES IMPORTED_LOCATION /path/to/lib.so)
```

目标类型通过 `cmTarget::TargetType` 枚举区分：
- `EXECUTABLE`
- `STATIC_LIBRARY`
- `SHARED_LIBRARY`
- `MODULE_LIBRARY`
- `OBJECT_LIBRARY`
- `INTERFACE_LIBRARY`
- `UTILITY`（自定义目标）

## 目标属性

每个目标拥有一组**属性（Properties）**，存储构建该目标所需的所有信息：

| 属性 | 用途 | 设置命令 |
|------|------|---------|
| `INCLUDE_DIRECTORIES` | 头文件搜索路径 | `target_include_directories()` |
| `COMPILE_DEFINITIONS` | 预处理宏定义 | `target_compile_definitions()` |
| `COMPILE_OPTIONS` | 编译选项 | `target_compile_options()` |
| `LINK_LIBRARIES` | 链接的库 | `target_link_libraries()` |
| `LINK_OPTIONS` | 链接选项 | `target_link_options()` |
| `LINK_DEPENDS` | 链接依赖 | 隐式/`add_dependencies()` |
| `SOURCES` | 源文件列表 | `target_sources()` |
| `OUTPUT_NAME` | 输出文件名 | `set_target_properties()` |
| `RUNTIME_OUTPUT_DIRECTORY` | 运行时输出目录 | `set_target_properties()` |
| `CXX_STANDARD` | C++ 标准版本 | `target_compile_features()` 或属性 |
| `POSITION_INDEPENDENT_CODE` | PIC 标志 | `set_target_properties()` |
| `INTERFACE_INCLUDE_DIRECTORIES` | 传播给消费者的头文件路径 | `target_include_directories(... INTERFACE/PUBLIC)` |

## PUBLIC/PRIVATE/INTERFACE 传播关键字

这是现代 CMake（3.0+）目标模型最重要的概念：

```
┌─────────────────────────────────────────────────┐
│              mylib (SHARED LIBRARY)              │
│                                                 │
│   PRIVATE 部分（仅 mylib 自己使用）：             │
│   ├─ INCLUDE_DIRECTORIES: src/internal/         │
│   ├─ COMPILE_DEFINITIONS: MYLIB_BUILD_DLL       │
│   └─ COMPILE_OPTIONS: -Wall                    │
│                                                 │
│   INTERFACE 部分（传播给消费者）：                │
│   ├─ INTERFACE_INCLUDE_DIRECTORIES: include/   │
│   ├─ INTERFACE_COMPILE_DEFINITIONS: MYLIB_SHARED│
│   └─ 链接到 mylib 的目标自动获得这些              │
│                                                 │
│   PUBLIC = PRIVATE + INTERFACE                   │
│   （自己用，同时传播给消费者）                     │
└────────┬────────────────────────────────────────┘
         │ target_link_libraries(myapp PRIVATE mylib)
         ▼
┌─────────────────────────────────────────────────┐
│              myapp (EXECUTABLE)                  │
│                                                 │
│   自动获得 mylib 的 INTERFACE 属性：              │
│   ├─ INCLUDE_DIRECTORIES: include/ (来自mylib)  │
│   └─ COMPILE_DEFINITIONS: MYLIB_SHARED          │
│                                                 │
│   自己的设置：                                   │
│   ├─ INCLUDE_DIRECTORIES: src/                  │
│   └─ ...                                        │
└─────────────────────────────────────────────────┘
```

### 用法示例

```cmake
# mylib/CMakeLists.txt
add_library(mylib src/mylib.cpp)
target_include_directories(mylib
  PUBLIC  include/        # 自己+消费者都需要
  PRIVATE src/internal/   # 只有自己需要
)
target_compile_definitions(mylib
  PRIVATE MYLIB_BUILDING  # 内部宏
  PUBLIC  MYLIB_VERSION=1 # 消费者也需要知道
)
target_link_libraries(mylib
  PUBLIC  fmt::fmt        # fmt 头文件在 mylib 公共头文件中暴露 → PUBLIC
  PRIVATE spdlog::spdlog  # 仅内部使用 spdlog → PRIVATE
)
```

```cmake
# app/CMakeLists.txt
add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE mylib)
# myapp 自动获得：
#   - include/ 头文件路径（来自 mylib PUBLIC）
#   - MYLIB_VERSION=1 宏定义（来自 mylib PUBLIC）
#   - fmt::fmt（来自 mylib PUBLIC，传递链接）
# 但不获得：
#   - src/internal/ 路径（mylib PRIVATE）
#   - MYLIB_BUILDING 宏（mylib PRIVATE）
#   - spdlog::spdlog（mylib PRIVATE，不传递）
```

## 传递性链接（Transitive Linking）

目标依赖形成 DAG（有向无环图），属性沿依赖边传播：

```
myapp → mylib → fmt::fmt
             → spdlog::spdlog (PRIVATE, 不传播)
             → Boost::filesystem (PUBLIC, 传播给 myapp)
```

CMake 的 Compute 阶段遍历此 DAG：
1. 收集所有递归 PUBLIC/INTERFACE 属性
2. 处理循环依赖检测（报错）
3. 按正确顺序排列链接行（静态库符号依赖顺序）
4. 处理生成器表达式

## 头文件-only 库 (INTERFACE Library)

对于纯模板/头文件库，不需要编译源文件：

```cmake
add_library(header-only INTERFACE)
target_include_directories(header-only INTERFACE include/)
target_compile_features(header-only INTERFACE cxx_std_20)

# 使用
target_link_libraries(myapp PRIVATE header-only)
```

INTERFACE 库不产生任何构建输出，但传播属性与普通库一样。

## 目标属性的生成器表达式

属性值中可以使用**生成器表达式**（Generator Expressions），在 Generate 阶段求值：

```cmake
target_compile_options(mylib PRIVATE
  $<$<CONFIG:Debug>:-g -O0>           # Debug 配置：-g -O0
  $<$<CONFIG:Release>:-O2 -DNDEBUG>    # Release 配置：-O2 -DNDEBUG
  $<$<PLATFORM_ID:Linux>:-pthread>     # Linux：-pthread
  $<$<CXX_COMPILER_ID:GNU>:-Wall>     # GCC：-Wall
)
```

常见生成器表达式：
- `$<CONFIG:cfg>` — 当前配置是否为 cfg
- `$<PLATFORM_ID:id>` — 平台匹配
- `$<CXX_COMPILER_ID:id>` — 编译器匹配
- `$<TARGET_FILE:tgt>` — 目标文件的完整路径
- `$<TARGET_PROPERTY:tgt,prop>` — 目标属性值

## 关联概念

- [配置-生成两阶段](configure-generate.md) — 目标在 Configure 阶段创建、在 Generate 阶段使用
- [查找模块机制](find-module.md) — 如何通过 find_package 创建导入目标
- [构建类型与多配置](build-type.md) — 多配置下目标属性的处理
- [工具链检测](toolchain-detection.md) — 目标编译时使用的编译器信息
