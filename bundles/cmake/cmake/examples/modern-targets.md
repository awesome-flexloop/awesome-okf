---
type: example
title: "现代 CMake 目标使用：PUBLIC/PRIVATE/INTERFACE 传播"
description: "使用目标接口（target_include_directories、target_link_libraries）替代全局 include_directories/link_libraries，演示属性传递性传播"
sources:
  concepts: [../concepts/target-model.md, ../concepts/variable-scope.md]
  references: [../references/cmdexec.md]
---

# 现代 CMake 目标使用：PUBLIC/PRIVATE/INTERFACE 传播

## 目标

构建一个多层库+可执行项目，演示现代 CMake 的目标属性传播机制，替代全局命令。

## 反模式 vs 正确模式

### ❌ 传统 CMake（CMake 2.x 风格，避免使用）

```cmake
# ❌ 全局设置：影响所有后续目标
include_directories(include/)
link_directories(/usr/local/lib)
add_definitions(-Wall)

add_library(mylib src/lib.cpp)
add_executable(myapp src/main.cpp)
target_link_libraries(myapp mylib)  # 只有这一行用了 target_*
# 问题：所有目标都被污染，依赖关系不明确
```

### ✅ 现代 CMake（CMake 3.0+，推荐）

```cmake
add_library(mylib src/lib.cpp)
target_include_directories(mylib PUBLIC include/)  # 传播给消费者
target_compile_features(mylib PUBLIC cxx_std_17)     # 传播给消费者
target_compile_options(mylib PRIVATE -Wall)          # 仅自己用

add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE mylib)
# myapp 自动获得 mylib PUBLIC 的 include 路径和 C++17 要求
```

## 项目结构

```
calc/
├── CMakeLists.txt
├── include/calc/
│   ├── calculator.h     # 公共头文件
│   └── utils.h          # 内部工具头文件
├── src/
│   ├── calculator.cpp   # 实现
│   └── utils.cpp
├── app/
│   ├── CMakeLists.txt
│   └── main.cpp
└── tests/
    ├── CMakeLists.txt
    └── test_calc.cpp
```

## 顶层 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
project(Calc VERSION 2.1.0 LANGUAGES CXX)

# 全局设置
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 启用测试
include(CTest)

# 子目录
add_subdirectory(src)       # 库目标在 src/ 中定义
add_subdirectory(app)       # 可执行文件

if(BUILD_TESTING)
  add_subdirectory(tests)   # 测试
endif()
```

## src/CMakeLists.txt（库定义）

```cmake
# 创建库目标
add_library(calc)

# 源文件（PRIVATE：仅编译时使用，不传播）
target_sources(calc PRIVATE
  calculator.cpp
  utils.cpp
)

# PUBLIC：自己编译需要，链接者也需要
target_include_directories(calc PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/../include
)

# 编译特性（PUBLIC：链接者也需要 C++17）
target_compile_features(calc PUBLIC cxx_std_17)

# PRIVATE 编译选项：仅库自己编译时使用
if(MSVC)
  target_compile_options(calc PRIVATE /W4)
else()
  target_compile_options(calc PRIVATE -Wall -Wextra)
endif()

# 设置目标属性：输出名
set_target_properties(calc PROPERTIES
  OUTPUT_NAME "calc${PROJECT_VERSION_MAJOR}"
  VERSION ${PROJECT_VERSION}
  SOVERSION ${PROJECT_VERSION_MAJOR}
)

# 别名目标：方便子项目使用 Calc::calc 命名空间
add_library(Calc::calc ALIAS calc)
```

### include/calc/calculator.h（公共头文件）

```cpp
#pragma once
#include <string>

namespace calc {
class Calculator {
public:
  double add(double a, double b) const;
  double multiply(double a, double b) const;
  std::string version() const;
};
}
```

## app/CMakeLists.txt（可执行文件）

```cmake
add_executable(calc_app main.cpp)

# 链接到 calc 库
# 自动获得 calc PUBLIC 的：
#   - include/ 目录
#   - C++17 要求
target_link_libraries(calc_app PRIVATE Calc::calc)

# 可执行文件自己的 PRIVATE 设置
target_compile_options(calc_app PRIVATE
  $<$<CXX_COMPILER_ID:MSVC>:/W4>
  $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall>
)

# 安装
install(TARGETS calc_app RUNTIME DESTINATION bin)
```

### app/main.cpp

```cpp
#include "calc/calculator.h"
#include <iostream>

int main() {
  calc::Calculator c;
  std::cout << "Calc v" << c.version() << std::endl;
  std::cout << "2 + 3 = " << c.add(2, 3) << std::endl;
  std::cout << "4 * 5 = " << c.multiply(4, 5) << std::endl;
  return 0;
}
```

## tests/CMakeLists.txt（测试）

```cmake
# 假设使用 GoogleTest（需先 find_package）
find_package(GTest QUIET)
if(GTest_FOUND)
  add_executable(calc_tests test_calc.cpp)
  target_link_libraries(calc_tests PRIVATE Calc::calc GTest::gtest_main)

  include(GoogleTest)
  gtest_discover_tests(calc_tests)
endif()
```

## 使用外部依赖：fmt 库

现在扩展 calc 库，使用 fmt 进行格式化：

```cmake
# src/CMakeLists.txt
find_package(fmt REQUIRED)       # 查找 fmt
target_link_libraries(calc
  PUBLIC
    Calc::calc            # (自身别名)
  PRIVATE
    fmt::fmt              # fmt 仅在 .cpp 中使用 → PRIVATE
)
```

**注意**：`utils.cpp` 中 include 了 `<fmt/format.h>`，但 `calculator.h`（公共头文件）中**没有** include fmt，所以 fmt 是 PRIVATE 依赖。

如果公共头文件中 include 了 fmt：

```cpp
// calculator.h
#include <fmt/format.h>   // ⚠️ 公共头文件暴露了 fmt
namespace calc {
class Calculator {
  // 使用 fmt 的类型...
};
}
```

那 fmt 必须是 PUBLIC 依赖：

```cmake
target_link_libraries(calc
  PUBLIC
    Calc::calc
    fmt::fmt              # 公共头文件使用 → 必须 PUBLIC
)
```

这样链接 calc 的目标也会自动链接 fmt。

## 头文件-only 库（INTERFACE Library）

添加一个 `calc_config` 头文件-only 库：

```cmake
add_library(calc_config INTERFACE)
target_include_directories(calc_config INTERFACE
  ${CMAKE_CURRENT_SOURCE_DIR}/../include
)
target_compile_features(calc_config INTERFACE cxx_std_17)
target_compile_definitions(calc_config INTERFACE
  CALC_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
)
add_library(Calc::config ALIAS calc_config)
```

使用：
```cmake
target_link_libraries(calc PRIVATE Calc::config)
```

头文件-only 库不编译任何源文件，但传播 INTERFACE 属性。

## 构建验证

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
./build/app/calc_app
# Calc v2.1.0
# 2 + 3 = 5
# 4 * 5 = 20
```

## 传播规则总结表

| 命令 | PRIVATE | PUBLIC | INTERFACE |
|------|---------|--------|-----------|
| `target_include_directories` | 自己编译用 | 自己+消费者 | 仅消费者 |
| `target_compile_definitions` | 自己编译用 | 自己+消费者 | 仅消费者 |
| `target_compile_options` | 自己编译用 | 自己+消费者（少见） | 仅消费者（少见） |
| `target_compile_features` | 自己编译用 | 自己+消费者 | 仅消费者 |
| `target_link_libraries` | 链接自己，不传播 | 链接自己+传播 | 不链接自己，仅传播 |

判断口诀：**公共头文件用到的依赖 → PUBLIC；仅 .cpp 用到的 → PRIVATE；只有头文件（不编译源文件）→ INTERFACE**

## 延伸阅读

- [目标模型详解](../concepts/target-model.md)
- [查找模块机制](../concepts/find-module.md)
- [变量作用域链](../concepts/variable-scope.md)
