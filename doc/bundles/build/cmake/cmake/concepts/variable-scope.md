---
type: concept
title: "变量作用域链"
description: "CMake 变量的作用域规则：普通变量 vs 缓存变量、PARENT_SCOPE、目录隔离、函数/宏作用域差异"
sources:
  references: [../references/cmstate.md, ../references/cmmakefile.md, ../references/cmdexec.md]
  facts: [F-032, F-085, F-091]
---

# 变量作用域链

## 核心理解

CMake 变量有**两种存储位置**和**多层作用域**，理解它们的交互是掌握 CMake 的关键：

| 类型 | 存储位置 | 生命周期 | 作用域 |
|------|---------|---------|--------|
| 普通变量 | cmStateSnapshot 的 Variables map | Configure 阶段 | 当前快照+子快照（按规则查找） |
| 缓存变量 | cmCacheManager（CMakeCache.txt） | 跨 Configure 运行持久 | 全局（所有目录可见） |

变量查找遵循**优先级链**：当前作用域 → 父调用作用域 → 目录链 → 缓存 → 环境变量（`ENV{VAR}` 单独处理）。

## 普通变量的作用域规则

### 1. 目录作用域（add_subdirectory）

```cmake
# 顶层 CMakeLists.txt
set(MYVAR "top")
add_subdirectory(sub)
message(STATUS "top: ${MYVAR}")  # "top"（子目录修改不影响父目录）
```

```cmake
# sub/CMakeLists.txt
message(STATUS "sub init: ${MYVAR}")  # "top"（创建快照时拷贝父变量）
set(MYVAR "sub-value")
message(STATUS "sub after: ${MYVAR}")  # "sub-value"
```

关键点：
- 子目录快照在创建时**拷贝**父目录的普通变量（快照数据初始化）
- 子目录中 `set()` 只修改子目录快照的 Variables，不影响父
- `set(MYVAR "value" PARENT_SCOPE)` 直接写入父快照的 Variables（类似传引用）

### 2. 函数作用域（function）

```cmake
set(x "outer")
function(inner)
  message(STATUS "inner: ${x}")  # 空！函数不继承外层普通变量（除非显式传参）
  set(x "inner-value")
endfunction()
inner()
message(STATUS "outer: ${x}")  # "outer"（函数内修改不影响外层）
```

函数快照**不拷贝**父作用域的普通变量，只继承参数变量（ARGC、ARGV0、ARGV1...）和函数参数名。这与目录作用域行为**不同**！

要让函数访问外层变量，要么显式传参，要么使用缓存变量。

### 3. 宏作用域（macro）

```cmake
set(x "outer")
macro(my_macro)
  set(x "macro-value")  # ⚠️ 直接修改外层作用域！
endmacro()
my_macro()
message(STATUS ${x})    # "macro-value"（外层被修改了）
```

宏本质上是**文本替换**（类似 C 语言 `#define`），不创建独立的变量作用域。宏体内的 `set()` 直接操作调用者的作用域。

### 4. 块作用域（block/endblock）

CMake 3.25+ 支持显式块作用域：

```cmake
set(x "before")
block(SCOPE_FOR VARIABLES)
  set(x "inside")
  message(STATUS ${x})  # "inside"
endblock()
message(STATUS ${x})    # "before"（自动恢复）
```

## 缓存变量（Cache Variables）

缓存变量持久化在构建目录的 `CMakeCache.txt` 中，跨 CMake 重新运行保留：

```cmake
set(MY_CACHE_VAR "default" CACHE STRING "Description of the variable")
option(ENABLE_FEATURE "Enable feature X" ON)  # 等价于 BOOL CACHE 变量
```

### 缓存变量的查找优先级

```
1. 当前快照的普通变量（如果存在）→ 使用普通变量值
2. 父调用快照的普通变量（沿 CallStackParent 链）
3. 缓存变量（CMakeCache.txt）
4. 未定义 → 空字符串
```

**重要陷阱**：如果已经存在同名普通变量，`set(... CACHE ...)` **不会更新**缓存值！

```cmake
set(MYVAR "normal")
set(MYVAR "cache" CACHE STRING "cache var")
message(STATUS ${MYVAR})  # "normal"（普通变量优先！）
```

使用 `CACHE FORCE` 可以强制覆盖：
```cmake
set(MYVAR "cache" CACHE STRING "cache var" FORCE)
```

### 命令行 -D 设置缓存变量

```bash
cmake -S . -B build -DMYVAR=value -DENABLE_FEATURE=ON
```

`-D` 参数设置缓存变量，在 Configure 执行前加载到 CMakeCache.txt。

## 变量类型与展开

### 变量引用语法

```cmake
set(name "value")
message(STATUS "${name}")           # "value"
message(STATUS "${prefix_${var}}")  # 嵌套展开
message(STATUS "$ENV{PATH}")        # 环境变量
message(STATUS "$CACHE{VAR}")       # 强制读取缓存变量（CMake 3.13+）
```

### 列表变量

CMake 列表本质是**分号分隔的字符串**：

```cmake
set(MY_LIST "a;b;c")         # 三元素列表
list(APPEND MY_LIST "d")     # 追加元素
list(LENGTH MY_LIST len)     # 获取长度
list(GET MY_LIST 0 first)    # 按索引获取
list(FILTER MY_LIST INCLUDE REGEX "^a")
foreach(item IN LISTS MY_LIST)
  message(STATUS ${item})
endforeach()
```

## 常见陷阱

### 陷阱 1：子目录 set 不影响父目录

```cmake
# CMakeLists.txt
set(FOUND OFF)
add_subdirectory(check)
if(FOUND)  # ⚠️ FOUND 仍然是 OFF！子目录的 set 没有传上来
  # ...
endif()

# check/CMakeLists.txt
set(FOUND ON PARENT_SCOPE)  # ✅ 正确做法：使用 PARENT_SCOPE
```

### 陷阱 2：缓存变量不覆盖普通变量

```cmake
set(BUILD_SHARED_LIBS ON)               # 普通变量
set(BUILD_SHARED_LIBS OFF CACHE BOOL "")# 不生效！
# BUILD_SHARED_LIBS 仍然是 ON
```

### 陷阱 3：函数内不继承外层变量

```cmake
set(COMMON_FLAGS "-Wall")
function(add_my_target name)
  target_compile_options(${name} PRIVATE ${COMMON_FLAGS})  # ⚠️ COMMON_FLAGS 为空！
  # 修复：显式传参或使用缓存变量
endfunction()
```

### 陷阱 4：宏内修改泄漏到外层

```cmake
macro(configure_things)
  set(TEMP_FILE "/tmp/tmp.txt")  # TEMP_FILE 泄漏到调用者作用域！
endmacro()
configure_things()
message(STATUS ${TEMP_FILE})  # "/tmp/tmp.txt"（意外泄漏）
```

最佳实践：优先使用 `function()` 而非 `macro()`，除非确实需要文本替换行为。

## 关联概念

- [状态快照机制](state-snapshot.md) — 变量查找的底层实现
- [配置-生成两阶段](configure-generate.md) — 变量在 Configure 阶段的生命周期
- [策略系统](policy-system.md) — 策略堆栈也使用类似的快照机制
