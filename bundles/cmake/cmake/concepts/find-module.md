---
type: concept
title: "查找模块机制 (find_package)"
description: "CMake find_package 的 Module 模式与 Config 模式、搜索路径顺序、导入目标创建与版本兼容性检查"
sources:
  references: [../references/cmdexec.md]
  facts: [F-081, F-082]
---

# 查找模块机制 (find_package)

## 核心理解

`find_package()` 是 CMake 查找外部依赖的核心命令，支持两种模式：

| 模式 | 查找文件 | 提供方 | 现代性 |
|------|---------|--------|--------|
| **Config 模式** | `<Name>Config.cmake` / `<name>-config.cmake` | 上游包安装时提供 | ✅ 推荐（现代 CMake） |
| **Module 模式** | `Find<Name>.cmake` | CMake 内置或用户编写 | ⚠️ 传统方式 |

```
find_package(Boost 1.70 REQUIRED COMPONENTS filesystem system)
            │         │      │         │
            包名     版本   必须存在  组件列表
                    (可选)
```

## 搜索路径顺序

### Module 模式搜索顺序

```
1. CMAKE_MODULE_PATH 中的目录（用户自定义模块路径）
   └─ 查找 FindBoost.cmake
2. CMAKE_ROOT/Modules/（CMake 内置 Find 模块目录）
   └─ 查找 FindBoost.cmake
```

如果找到 `Find<Name>.cmake`，执行该脚本。Find 模块负责创建导入目标或设置变量（如 `Boost_INCLUDE_DIRS`、`Boost_LIBRARIES`）。

### Config 模式搜索顺序

Config 模式更复杂，搜索 `<Name>Config.cmake` 或 `<lower-name>-config.cmake`：

```
1. CMAKE_PREFIX_PATH / CMAKE_FRAMEWORK_PATH / CMAKE_APPBUNDLE_PATH
   （用户通过 -D 或 set 指定的搜索前缀）
2. <Name>_DIR 缓存变量
   （用户显式指定的 Config 文件目录）
3. 平台标准路径：
   - Linux: /usr/lib/cmake/, /usr/local/lib/cmake/, /usr/lib/<arch>/cmake/
   - macOS: 类似 + Framework 路径
   - Windows: 注册表、Program Files 等
4. PATH 环境变量中的 bin/ 目录的上一级
5. 环境变量 <Name>_ROOT / CMAKE_PREFIX_PATH（CMake 3.12+）
```

在每个前缀下，CMake 查找：
```
<prefix>/
├── lib/cmake/<Name>/<Name>Config.cmake        # 标准安装路径
├── lib/cmake/<name>-*/<name>-config.cmake     # 带版本号
├── share/cmake/<Name>/<Name>Config.cmake      # 数据目录
├── <Name>*/<Name>Config.cmake                 # 根目录
└── cmake/<Name>Config.cmake                   # 直接 cmake 子目录
```

### 两种模式的选择

```cmake
# 默认：先 Module 模式，找不到再 Config 模式
find_package(Boost)

# 强制 Module 模式
find_package(Boost MODULE)

# 强制 Config 模式（推荐）
find_package(Boost CONFIG)
# 或（等价）
find_package(Boost NO_MODULE)
```

## 查找结果：变量 vs 导入目标

### 传统方式（Find 模块返回变量）

```cmake
find_package(Boost REQUIRED COMPONENTS filesystem)
# 设置了以下变量：
# Boost_INCLUDE_DIRS    → 头文件路径
# Boost_LIBRARIES       → 要链接的库列表
# Boost_FILESYSTEM_LIBRARY
# Boost_FOUND           → 是否找到

target_include_directories(myapp PRIVATE ${Boost_INCLUDE_DIRS})
target_link_libraries(myapp PRIVATE ${Boost_LIBRARIES})
```

问题：调用者需要手动处理包含目录和链接，不支持传递性传播。

### 现代方式（导入目标）

```cmake
find_package(Boost REQUIRED COMPONENTS filesystem)
# 创建了导入目标：
# Boost::boost              (头文件-only 目标)
# Boost::filesystem         (组件库目标)

target_link_libraries(myapp PRIVATE Boost::filesystem)
# 自动传播：
#   - Boost 头文件路径（INTERFACE_INCLUDE_DIRECTORIES）
#   - Boost 链接库
#   - 依赖关系（filesystem 依赖 system）
```

现代 CMake 包（通过 Config 模式提供）一律使用导入目标。

## 版本检查

```cmake
find_package(Boost 1.70 REQUIRED)
# Config 模式：<Name>ConfigVersion.cmake 检查版本兼容性
# Module 模式：Find 模块内部检查
```

版本检查支持：
- 精确版本：`1.70.0`
- 最小版本：`1.70`（接受 1.70.x 及以上）
- 版本范围：`1.70...2.0`（CMake 3.19+）

Config 模式下，`<Name>Config.cmake` 旁会有一个 `<Name>ConfigVersion.cmake` 文件，由 `CMakePackageConfigHelpers` 生成，处理版本兼容性逻辑（SameMajorVersion、SameMinorVersion、ExactVersion 等）。

## REQUIRED / QUIET / EXACT

```cmake
find_package(Boost 1.70 REQUIRED)           # 找不到则报错终止
find_package(Boost QUIET)                    # 找不到不输出警告
find_package(Boost 1.70.0 EXACT REQUIRED)   # 必须精确匹配 1.70.0
find_package(Boost OPTIONAL_COMPONENTS mpi) # mpi 组件可选
```

## COMPONENTS：多组件包

许多库由多个组件构成：

```cmake
find_package(Qt6 REQUIRED COMPONENTS Core Widgets Network)
# 创建导入目标：
# Qt6::Core
# Qt6::Widgets
# Qt6::Network
target_link_libraries(myapp PRIVATE Qt6::Widgets)
# Qt6::Widgets 自动传递 Qt6::Core（其依赖）
```

## 安装自己的库并提供 Config 文件

现代 CMake 项目应在安装时生成 Config 文件，使下游可以用 Config 模式找到：

```cmake
install(TARGETS mylib EXPORT mylibTargets
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include
)
install(EXPORT mylibTargets
  FILE mylibTargets.cmake
  NAMESPACE MyProj::
  DESTINATION lib/cmake/mylib
)

# 生成 Config 和 ConfigVersion 文件
include(CMakePackageConfigHelpers)
configure_package_config_file(
  cmake/mylibConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake
  INSTALL_DESTINATION lib/cmake/mylib
)
write_basic_package_version_file(
  ${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMajorVersion
)
install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake
  DESTINATION lib/cmake/mylib
)
```

下游使用：
```cmake
find_package(mylib REQUIRED)
target_link_libraries(myapp PRIVATE MyProj::mylib)
```

## 常见问题排查

### 找不到包

```bash
# 显式指定路径
cmake -S . -B build -DBoost_DIR=/path/to/boost/lib/cmake/Boost-1.70
# 或设置 CMAKE_PREFIX_PATH
cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/boost;/path/to/other

# 查看详细搜索日志
cmake -S . -B build --debug-find-pkg=Boost
```

### 找到错误的版本

检查 CMakeCache.txt 中 `<Name>_DIR` 是否指向了错误版本，清理后重新配置。

## 关联概念

- [目标模型](target-model.md) — 导入目标 (IMPORTED) 与普通目标的关系
- [配置-生成两阶段](configure-generate.md) — find_package 在 Configure 阶段执行
- [整体架构](overall-architecture.md) — find_package 是 cmFindPackageCommand 的实现
