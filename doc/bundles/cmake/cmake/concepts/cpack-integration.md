---
type: concept
title: "CPack 打包集成"
description: "CPack 安装包生成机制：install() 规则收集、组件打包、TGZ/DEB/RPM/NSIS/DMG 多格式生成"
sources:
  references: [../references/ctest-cpack.md]
  facts: [F-107, F-108, F-109, F-110, F-111, F-112, F-113]
---

# CPack 打包集成

## 核心理解

CPack 是 CMake 套件中的打包工具，它从构建结果中收集文件，按指定格式生成安装包。CPack 不直接参与构建——它读取 Configure 阶段生成的 `CPackConfig.cmake`，按 `install()` 规则将文件打包。

```
CMake Configure → 生成 CPackConfig.cmake（install 规则 + 变量）
                         │
                         ▼
               cpack 命令读取配置
                         │
                         ▼
               按组件收集文件到临时目录
                         │
                         ▼
               调用具体生成器（TGZ/DEB/RPM/NSIS/...）
                         │
                         ▼
               输出安装包文件
```

## install() 规则

CPack 的输入来自 `install()` 命令定义的安装规则：

```cmake
# 安装目标文件
install(TARGETS myapp mylib
  RUNTIME DESTINATION bin           # 可执行文件 → bin/
  LIBRARY DESTINATION lib           # 共享库 → lib/
  ARCHIVE DESTINATION lib/static    # 静态库 → lib/static/
  INCLUDES DESTINATION include      # 头文件 → include/
)

# 安装文件
install(FILES LICENSE README.md DESTINATION share/doc/myapp)

# 安装目录
install(DIRECTORY include/ DESTINATION include FILES_MATCHING PATTERN "*.h")

# 安装程序
install(PROGRAMS scripts/mytool DESTINATION bin)

# 安装 CMake 导出目标（供下游 find_package）
install(EXPORT myappTargets
  FILE myappTargets.cmake
  NAMESPACE MyApp::
  DESTINATION lib/cmake/myapp
)

# 自定义安装脚本
install(CODE "message('Running custom install step')")
install(SCRIPT CustomInstall.cmake)
```

## 基本 CPack 配置

```cmake
# CMakeLists.txt
set(CPACK_PACKAGE_NAME "MyApp")
set(CPACK_PACKAGE_VENDOR "My Company")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "A great application")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_VERSION_MAJOR ${PROJECT_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${PROJECT_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${PROJECT_VERSION_PATCH})
set(CPACK_PACKAGE_INSTALL_DIRECTORY "MyApp")
set(CPACK_PACKAGE_CONTACT "supprot@")
set(CPACK_RESOURCE_FILE_LICENSE ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE)
set(CPACK_RESOURCE_FILE_README ${CMAKE_CURRENT_SOURCE_DIR}/README.md)

# 必须在最后包含 CPack
include(CPack)
```

`include(CPack)` 在 Configure 阶段生成 `CPackConfig.cmake`。

## 选择包格式

```cmake
# 指定要生成的包格式（分号分隔列表）
set(CPACK_GENERATOR "TGZ;ZIP;DEB;RPM")
```

运行打包：
```bash
# 构建后打包
cmake --build build --target package
# 或直接运行 cpack
cd build && cpack

# 指定生成器
cpack -G DEB
cpack -C Release  # 多配置生成器指定配置
```

## 组件化打包

将安装内容分为多个组件，用户可选择安装：

```cmake
# 安装时指定组件
install(TARGETS myapp DESTINATION bin COMPONENT runtime)
install(TARGETS mylib DESTINATION lib COMPONENT runtime)
install(FILES mylib.h DESTINATION include COMPONENT development)
install(FILES manpage.1 DESTINATION share/man COMPONENT documentation)

# CPack 组件配置
set(CPACK_COMPONENTS_ALL runtime development documentation)

# runtime 组件描述
set(CPACK_COMPONENT_RUNTIME_DISPLAY_NAME "Runtime")
set(CPACK_COMPONENT_RUNTIME_DESCRIPTION "Runtime libraries and executables")
set(CPACK_COMPONENT_RUNTIME_REQUIRED ON)  # 必须安装

# development 组件依赖 runtime
set(CPACK_COMPONENT_DEVELOPMENT_DISPLAY_NAME "Development")
set(CPACK_COMPONENT_DEVELOPMENT_DESCRIPTION "Headers and CMake config")
set(CPACK_COMPONENT_DEVELOPMENT_DEPENDS runtime)

# 组件分组
set(CPACK_COMPONENT_GROUP_DEVELOPMENT_DISPLAY_NAME "Development Files")
set(CPACK_COMPONENT_DEVELOPMENT_GROUP development)
set(CPACK_COMPONENT_DOCUMENTATION_GROUP development)
```

按组件打包：
```bash
cpack -D CPACK_COMPONENTS_ALL="runtime"          # 只打 runtime 包
cpack -D CPACK_COMPONENTS_ALL="runtime;development" # 多个组件

# 每个组件单独生成包
set(CPACK_DEB_COMPONENT_INSTALL ON)  # DEB 按分包
cpack -G DEB
# 生成：myapp-runtime-1.0.deb, myapp-development-1.0.deb
```

## DEB 包配置

```cmake
set(CPACK_DEBIAN_PACKAGE_NAME "myapp")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Maintainer <m@>")
set(CPACK_DEBIAN_PACKAGE_SECTION "utils")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "libc6 (>= 2.31), libstdc++6 (>= 10)")
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)  # 自动检测共享库依赖
set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE "amd64")
set(CPACK_DEBIAN_PACKAGE_HOMEPAGE "https://myapp.example.com")

# 组件级 DEB 配置
set(CPACK_DEBIAN_RUNTIME_PACKAGE_NAME "myapp-runtime")
set(CPACK_DEBIAN_RUNTIME_PACKAGE_DEPENDS "libc6, libstdc++6")
set(CPACK_DEBIAN_DEVELOPMENT_PACKAGE_NAME "myapp-dev")
set(CPACK_DEBIAN_DEVELOPMENT_PACKAGE_DEPENDS "myapp-runtime (= ${CPACK_PACKAGE_VERSION})")
```

## RPM 包配置

```cmake
set(CPACK_RPM_PACKAGE_NAME "myapp")
set(CPACK_RPM_PACKAGE_SUMMARY "A great application")
set(CPACK_RPM_PACKAGE_LICENSE "MIT")
set(CPACK_RPM_PACKAGE_GROUP "Applications/System")
set(CPACK_RPM_PACKAGE_REQUIRES "glibc >= 2.31, libstdc++ >= 10")
set(CPACK_RPM_PACKAGE_AUTOREQ ON)  # 自动检测依赖
set(CPACK_RPM_PACKAGE_URL "https://myapp.example.com")
set(CPACK_RPM_PACKAGE_ARCHITECTURE "x86_64")

# 组件级 RPM 配置
set(CPACK_RPM_RUNTIME_PACKAGE_NAME "myapp")
set(CPACK_RPM_DEVELOPMENT_PACKAGE_NAME "myapp-devel")
set(CPACK_RPM_DEVELOPMENT_PACKAGE_REQUIRES "myapp = %{VERSION}")
```

## NSIS (Windows 安装程序)

```cmake
set(CPACK_NSIS_INSTALL_ROOT "$PROGRAMFILES64\\MyApp")
set(CPACK_NSIS_DISPLAY_NAME "MyApp")
set(CPACK_NSIS_PACKAGE_NAME "MyApp Installer")
set(CPACK_NSIS_HELP_LINK "https://myapp.example.com")
set(CPACK_NSIS_URL_INFO_ABOUT "https://myapp.example.com")
set(CPACK_NSIS_CONTACT "s@")
set(CPACK_NSIS_MODIFY_PATH ON)  # 添加到 PATH 环境变量
set(CPACK_NSIS_ENABLE_UNINSTALL_BEFORE_INSTALL ON)
set(CPACK_NSIS_MUI_ICON "${CMAKE_CURRENT_SOURCE_DIR}/icons/app.ico")
set(CPACK_NSIS_MUI_UNIICON "${CMAKE_CURRENT_SOURCE_DIR}/icons/uninstall.ico")
```

## DragNDrop / ProductBuild (macOS)

```cmake
# DMG 镜像
set(CPACK_DMG_VOLUME_NAME "MyApp")
set(CPACK_DMG_FORMAT "UDBZ")  # bzip2 压缩
set(CPACK_DMG_BACKGROUND_IMAGE "${CMAKE_CURRENT_SOURCE_DIR}/dmg_bg.png")

# pkg 安装包
set(CPACK_PRODUCTBUILD_IDENTIFIER "com.example.myapp")
```

## 源文件包

除了二进制包，CPack 也可以生成源码包：

```cmake
set(CPACK_SOURCE_GENERATOR "TGZ;ZIP")
set(CPACK_SOURCE_IGNORE_FILES
  "/build/"
  "/.git/"
  "/.github/"
  ".*~"
  "/\\\\.gitignore$"
)
```

```bash
cpack --config CPackSourceConfig.cmake
# 生成 myapp-1.0.tar.gz
```

## CPack 命令行选项

```bash
cpack [options]
  -G <generators>     # 指定生成器（分号分隔）
  -C <config>         # 指定配置（Debug/Release，多配置时）
  -D <var>=<value>    # 覆盖 CPack 变量
  --config <file>     # 指定配置文件（默认 CPackConfig.cmake）
  -V                  # 详细输出
  --trace             # 跟踪模式（调试）
  -B <package-dir>    # 输出目录
  -P <package-name>   # 包名覆盖
  -R <version>        # 版本覆盖
```

## 关联概念

- [工作模式与工具链分发](working-mode.md) — cpack 作为独立可执行程序
- [CTest 测试集成](ctest-integration.md) — 兄弟工具链
- [配置-生成两阶段](configure-generate.md) — CPackConfig.cmake 在 Generate 阶段生成
