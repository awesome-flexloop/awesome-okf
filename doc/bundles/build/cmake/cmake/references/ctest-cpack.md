---
type: reference
title: "ctest/cpack：集成工具链"
description: "CTest 测试框架和 CPack 打包工具的架构信源登记，记录测试发现、运行、CDash 上报和包生成流程"
sources:
  - path: "external/libs/tools/CMake/Source/ctest.cxx"
    facts: [F-098, F-099, F-100, F-101, F-102, F-104]
  - path: "external/libs/tools/CMake/Source/cpack.cxx"
    facts: [F-107, F-108, F-109, F-110, F-111, F-112]
  - path: "external/libs/tools/CMake/Source/CTest/cmCTest.h"
    facts: [F-103]
  - path: "external/libs/tools/CMake/Source/CPack/cmCPackGenerator.h"
    facts: [F-113]
---

# ctest/cpack：集成工具链

## 信源概述

| 工具 | 入口文件 | 核心类 |
|------|---------|--------|
| CTest | `Source/ctest.cxx` | `cmCTest`（测试驱动） |
| CPack | `Source/cpack.cxx` | `cmCPackGenerator`（打包器基类） |

## CTest 关键事实

### F-098：CTest 独立可执行程序入口

**信源**：`Source/ctest.cxx`

`ctest` 是独立于 `cmake` 的可执行程序，主函数在 `ctest.cxx` 中，创建 `cmCTest` 实例并执行子命令。

### F-099：CTest 支持多种运行模式

**信源**：`Source/ctest.cxx`

| 模式 | 命令 | 功能 |
|------|------|------|
| 测试运行 | `ctest`（默认） | 运行所有测试，输出通过/失败统计 |
| 测试发现 | `ctest -N` | 列出测试但不运行 |
| 测试过滤 | `ctest -R <regex>` / `-E <regex>` | 正则包含/排除测试 |
| CDash 提交 | `ctest -D Experimental` / `-D Continuous` / `-D Nightly` | 运行测试并上报到 CDash 服务器 |
| 构建和测试 | `ctest -D ExperimentalBuild` | 先构建再测试再上报 |
| 并行测试 | `ctest -j N` | 并行运行 N 个测试 |

### F-100：测试通过 add_test 注册

**信源**：`Source/cmAddTestCommand.cxx`

```cmake
add_test(NAME mytest COMMAND myexe arg1 arg2)
```

注册测试名称、命令、工作目录、环境变量等。测试信息存储在 `CTestTestfile.cmake` 文件中。

### F-101：CTest 从 CTestTestfile.cmake 发现测试

**信源**：`Source/CTest/cmCTestTest.cxx`

构建目录每个子目录包含一个 `CTestTestfile.cmake`，CTest 递归加载这些文件获取所有测试列表。

### F-102：CTest 支持标签过滤

**信源**：`Source/cmCTest.cxx`

```cmake
set_tests_properties(mytest PROPERTIES LABELS "unit;fast")
ctest -L unit    # 运行带 unit 标签的测试
ctest -LE integration # 排除带 integration 标签的测试
```

### F-103：CDash 上报使用 HTTP/HTTPS 提交

**信源**：`Source/CTest/cmCTestSubmitHandler.cxx`

`ctest -D Submit` 将测试结果（Build.xml、Test.xml、Configure.xml）通过 HTTP PUT 提交到 CDash 服务器。

### F-104：Fixture 支持测试依赖排序

**信源**：`Source/cmCTest.cxx`

```cmake
set_tests_properties(setup PROPERTIES FIXTURES_SETUP myfix)
set_tests_properties(run PROPERTIES FIXTURES_REQUIRED myfix)
set_tests_properties(cleanup PROPERTIES FIXTURES_CLEANUP myfix)
```

确保 setup → run → cleanup 顺序执行。

## CPack 关键事实

### F-107：CPack 独立可执行程序入口

**信源**：`Source/cpack.cxx`

`cpack` 是独立的打包工具入口，通过 `cmCPackGeneratorFactory` 创建对应格式的生成器。

### F-108：CPack 通过 install() 规则收集文件

**信源**：`Source/cmInstallCommand.cxx`

所有 `install(TARGETS/FILES/DIRECTORY/...)` 规则定义了打包内容，CPack 按组件（component）和安装规则收集文件到临时目录。

### F-109：支持多种包格式

**信源**：`Source/CPack/` 目录结构

| 生成器 | 格式 | 平台 |
|--------|------|------|
| `cmCPackTGZGenerator` | TGZ/ZIP | 跨平台 |
| `cmCPackDEBGenerator` | DEB | Debian/Ubuntu |
| `cmCPackRPMGenerator` | RPM | RHEL/Fedora/SUSE |
| `cmCPackNSISGenerator` | NSIS | Windows |
| `cmCPackWIXGenerator` | MSI (WiX) | Windows |
| `cmCPackDragNDropGenerator` | DMG | macOS |
| `cmCPackProductBuildGenerator` | pkg | macOS |
| `cmCPackIFWGenerator` | Qt Installer Framework | 跨平台 |

### F-110：CPack 变量控制打包行为

**信源**：`Source/CPack/cmCPackGenerator.cxx`

关键变量：
- `CPACK_PACKAGE_NAME` / `CPACK_PACKAGE_VERSION`
- `CPACK_GENERATOR`（要生成的包格式列表）
- `CPACK_PACKAGE_CONTACT`、`CPACK_PACKAGE_DESCRIPTION`
- `CPACK_DEBIAN_PACKAGE_DEPENDS`（DEB 依赖）
- `CPACK_RPM_PACKAGE_REQUIRES`（RPM 依赖）

### F-111：CPack 通过 CPackConfig.cmake 配置

**信源**：`Source/cmCPackGenerator.cxx`

Configure 阶段生成 `CPackConfig.cmake`（包含所有 install() 规则和 CPack 变量），`cpack` 命令读取此文件执行打包。

### F-112：Components 支持分包

**信源**：`Source/CPack/cmCPackComponentGroup.cxx`

```cmake
install(TARGETS myapp COMPONENT runtime)
install(FILES docs/* COMPONENT docs)
cpack -D CPACK_COMPONENTS_ALL="runtime;docs"
```

### F-113：CPack 生成器工厂模式

**信源**：`Source/CPack/cmCPackGeneratorFactory.cxx`

与 `cmGlobalGeneratorFactory` 类似，CPack 也使用静态工厂注册机制，每个包格式通过静态工厂实例自注册。
