---
type: example
title: "基础项目配置：从零开始的 CMakeLists.txt"
description: "一个最小但完整的 CMake 项目模板，涵盖 cmake_minimum_required、project、add_executable、install 等基础命令"
sources:
  concepts: [../concepts/overall-architecture.md, ../concepts/configure-generate.md, ../concepts/toolchain-detection.md]
  references: [../references/cmdexec.md, ../references/cmake-class.md]
---

# 基础项目配置：从零开始的 CMakeLists.txt

## 目标

创建一个简单但结构完整的 C++ 项目，包含可执行文件、头文件、源文件、安装规则。

## 项目结构

```
myapp/
├── CMakeLists.txt        # 顶层构建配置
├── include/
│   └── myapp/
│       └── greeter.h     # 公共头文件
├── src/
│   ├── main.cpp          # 入口点
│   └── greeter.cpp       # 实现
└── README.md
```

## 完整代码

### CMakeLists.txt

```cmake
# 1. 指定最小 CMake 版本（必须放在最前）
cmake_minimum_required(VERSION 3.20)

# 2. 项目声明（版本、语言、描述）
project(MyApp
  VERSION 1.0.0
  DESCRIPTION "A simple greeting application"
  LANGUAGES CXX
)

# 3. C++ 标准设置（全局）
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 4. 默认构建类型（单配置生成器）
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "Build type" FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    Debug Release RelWithDebInfo MinSizeRel)
endif()

# 5. 创建可执行目标
add_executable(myapp)

# 6. 指定源文件（推荐 target_sources 而非 add_executable 中直接列出）
target_sources(myapp PRIVATE
  src/main.cpp
  src/greeter.cpp
)

# 7. 头文件包含路径
target_include_directories(myapp PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 8. 编译选项（区分编译器）
if(MSVC)
  target_compile_options(myapp PRIVATE /W4 /permissive-)
else()
  target_compile_options(myapp PRIVATE -Wall -Wextra -Wpedantic)
endif()

# 9. 安装规则
install(TARGETS myapp
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include
  FILES_MATCHING PATTERN "*.h"
)
```

### include/myapp/greeter.h

```cpp
#pragma once
#include <string>

namespace myapp {
class Greeter {
public:
  explicit Greeter(std::string name);
  void sayHello() const;
private:
  std::string name_;
};
}
```

### src/greeter.cpp

```cpp
#include "myapp/greeter.h"
#include <iostream>

namespace myapp {
Greeter::Greeter(std::string name) : name_(std::move(name)) {}
void Greeter::sayHello() const {
  std::cout << "Hello, " << name_ << "!" << std::endl;
}
}
```

### src/main.cpp

```cpp
#include "myapp/greeter.h"

int main(int argc, char* argv[]) {
  myapp::Greeter greeter(argc > 1 ? argv[1] : "World");
  greeter.sayHello();
  return 0;
}
```

## 构建与运行

```bash
# 配置
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release

# 构建
cmake --build build

# 运行
./build/myapp "CMake"
# 输出：Hello, CMake!

# 安装
cmake --install build --prefix /tmp/myapp-install
# 安装到 /tmp/myapp-install/bin/myapp
# 安装到 /tmp/myapp-install/include/myapp/greeter.h
```

## 要点解析

### cmake_minimum_required 为什么必须在最前？

`cmake_minimum_required(VERSION 3.20)` 做三件事：
1. 设置 `CMAKE_MINIMUM_REQUIRED_VERSION`，版本过低时直接报错
2. 隐式调用 `cmake_policy(VERSION 3.20)`，将 3.20 之前引入的所有策略设为 NEW
3. 确保后续命令使用 3.20+ 的行为语义

### target_sources vs add_executable 直接列源文件

```cmake
# ❌ 传统写法：所有源文件列在 add_executable 中
add_executable(myapp src/main.cpp src/greeter.cpp)

# ✅ 推荐写法：target_sources 分 PRIVATE/PUBLIC
add_executable(myapp)
target_sources(myapp PRIVATE
  src/main.cpp
  src/greeter.cpp
)
```

`target_sources` 更清晰地区分源文件的可见性（PRIVATE=仅自己编译，PUBLIC/INTERFACE=传播给链接者，通常库才用 PUBLIC），且更容易在子目录中追加源文件。

### CMAKE_CXX_EXTENSIONS OFF

```cmake
set(CMAKE_CXX_EXTENSIONS OFF)
```

默认 CMake 使用 `-std=gnu++17`（GNU 扩展），设为 OFF 后使用 `-std=c++17`（标准模式），避免依赖编译器特定扩展。

### CMAKE_CURRENT_SOURCE_DIR vs CMAKE_SOURCE_DIR

- `CMAKE_SOURCE_DIR`：顶层源码目录（最外层 CMakeLists.txt 所在目录）
- `CMAKE_CURRENT_SOURCE_DIR`：当前正在处理的 CMakeLists.txt 所在目录

`target_include_directories` 中使用 `CMAKE_CURRENT_SOURCE_DIR` 更安全——如果项目作为子项目被 `add_subdirectory` 引入，路径仍然正确。

## 延伸阅读

- 学习现代目标传播：见 [现代 CMake 目标使用](modern-targets.md)
- 了解配置-生成两阶段：[配置-生成两阶段](../concepts/configure-generate.md)
- 学习工具链检测原理：[工具链检测与语言启用](../concepts/toolchain-detection.md)
