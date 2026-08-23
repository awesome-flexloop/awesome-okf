---
type: concept
title: "CTest 测试集成"
description: "CTest 测试框架的架构：测试注册、发现、执行、过滤、Fixture、CDash 上报的完整流程"
sources:
  references: [../references/ctest-cpack.md]
  facts: [F-098, F-099, F-100, F-101, F-102, F-103, F-104]
---

# CTest 测试集成

## 核心理解

CTest 是 CMake 套件中的测试驱动工具，与 CMake 和 CDash 形成"配置-构建-测试-上报"的完整 CI 循环：

```
CMake (配置) → 构建系统 (编译) → CTest (测试) → CDash (展示)
```

## 启用测试

```cmake
# 顶层 CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(MyProject CXX)

# 启用测试（必须在 add_test 之前调用）
enable_testing()

# 或者使用 CTest 模块（包含更多功能）
include(CTest)
# 等价于 enable_testing() + 设置 BUILD_TESTING 选项 + CDash 配置
```

`include(CTest)` 会创建一个 `BUILD_TESTING` 选项（默认 ON），用户可以通过 `-DBUILD_TESTING=OFF` 禁用测试构建。

## 注册测试

### 基本用法

```cmake
add_executable(my_test test_main.cpp)
add_test(NAME my_test COMMAND my_test)
```

### 带工作目录和环境变量

```cmake
add_test(NAME my_test
  COMMAND my_test --gtest_color=yes
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

set_tests_properties(my_test PROPERTIES
  ENVIRONMENT "MY_VAR=value;PATH=/extra/path:$ENV{PATH}"
  TIMEOUT 30              # 超时秒数
  WILL_FAIL TRUE          # 预期失败
  LABELS "unit;fast"      # 标签
)
```

### 测试参数化

```cmake
# 使用 gtest_add_tests 或 catch_discover_tests 自动发现 GoogleTest/Catch2 测试
include(GoogleTest)
add_executable(my_tests test1.cpp test2.cpp)
target_link_libraries(my_tests PRIVATE GTest::gtest GTest::gtest_main)
gtest_discover_tests(my_tests)  # 自动将每个 TEST() 注册为 CTest 测试
```

## 运行测试

### 基本运行

```bash
# 构建后运行所有测试
ctest --test-dir build

# 或
cd build && ctest
```

### 常用选项

```bash
ctest -N                    # 列出所有测试（不运行）
ctest -R "regex"            # 运行名称匹配正则的测试
ctest -E "regex"            # 排除名称匹配正则的测试
ctest -L "unit"             # 运行带指定标签的测试
ctest -LE "integration"     # 排除带指定标签的测试
ctest -j 4                  # 并行运行 4 个测试
ctest --output-on-failure   # 失败时输出测试的 stdout/stderr
ctest -V                    # 详细输出（Verbose）
ctest -VV                   # 更详细输出
ctest --timeout 60          # 设置全局超时
ctest -C Debug              # 指定配置（多配置生成器）
ctest --repeat until-fail:100  # 重复运行直到失败（检测 flaky test）
ctest -R my_test --interactive-debug-mode 1  # 调试测试
```

### 通过 cmake 构建时运行测试

```bash
cmake --build build --target test
# 或在 Makefile/Ninja 中
cmake --build build -t test
```

## Fixture：测试依赖排序

Fixtures 用于设置测试间的执行顺序依赖（类似 setup/teardown）：

```cmake
# 设置阶段（创建测试资源、启动服务等）
add_test(NAME setup_db COMMAND init_db.sh)
set_tests_properties(setup_db PROPERTIES
  FIXTURES_SETUP my_fixture
)

# 清理阶段
add_test(NAME cleanup_db COMMAND cleanup_db.sh)
set_tests_properties(cleanup_db PROPERTIES
  FIXTURES_CLEANUP my_fixture
)

# 需要 fixture 的测试
add_test(NAME test_query COMMAND test_query)
set_tests_properties(test_query PROPERTIES
  FIXTURES_REQUIRED my_fixture
)

add_test(NAME test_insert COMMAND test_insert)
set_tests_properties(test_insert PROPERTIES
  FIXTURES_REQUIRED my_fixture
)
```

执行顺序保证：`setup_db` → (`test_query` 和 `test_insert` 可并行) → `cleanup_db`

## 测试属性

常用 `set_tests_properties` 属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `TIMEOUT` | 秒 | 测试超时时间 |
| `WORKING_DIRECTORY` | 路径 | 测试运行的工作目录 |
| `ENVIRONMENT` | 列表 | 环境变量设置 |
| `LABELS` | 列表 | 标签，用于 -L/-LE 过滤 |
| `DEPENDS` | 列表 | 测试依赖（强制顺序执行） |
| `COST` | 数字 | 测试成本，并行调度时优先运行高成本测试 |
| `WILL_FAIL` | BOOL | 测试预期失败 |
| `SKIP_RETURN_CODE` | 数字 | 指定返回码表示跳过而非失败 |
| `SKIP_REGULAR_EXPRESSION` | 正则 | 输出匹配正则时标记为跳过 |
| `PASS_REGULAR_EXPRESSION` | 正则 | 输出必须匹配正则才算通过 |
| `FAIL_REGULAR_EXPRESSION` | 正则 | 输出匹配正则则标记为失败 |
| `RESOURCE_LOCK` | 字符串 | 获取同名锁的测试不能并行执行 |
| `FIXTURES_SETUP/REQUIRED/CLEANUP` | 字符串 | Fixture 机制 |

## CDash：测试结果上报

CDash 是 CMake 官方的测试结果展示服务器（可自建或使用公共实例）。

### 配置 CDash 上报

```cmake
# CTestConfig.cmake（放在项目根目录或 build 目录）
set(CTEST_PROJECT_NAME "MyProject")
set(CTEST_NIGHTLY_START_TIME "01:00:00 UTC")
set(CTEST_DROP_METHOD "https")
set(CTEST_DROP_SITE "my-cdash.example.com")
set(CTEST_DROP_LOCATION "/submit.php?project=MyProject")
set(CTEST_DROP_SITE_CDASH TRUE)
```

### Dashboard 模式

```bash
# Experimental：一次性测试上报
ctest -D Experimental

# Nightly：夜间构建（按计划执行）
ctest -D Nightly

# Continuous：持续集成（检测到变更时执行）
ctest -D Continuous
```

Dashboard 模式完整执行：
1. `Start` — 开始新的 Dashboard 运行
2. `Update` — 从版本控制系统拉取更新
3. `Configure` — 运行 cmake 配置
4. `Build` — 构建项目
5. `Test` — 运行测试
6. `Submit` — 上报结果到 CDash

```bash
# 分步执行
ctest -D Start
ctest -D Configure
ctest -D Build
ctest -D Test
ctest -D Submit
```

### 不上报只本地运行

```bash
# 只执行 Dashboard 流程但不上报
ctest -D Experimental -DCTEST_SUBMIT_RETRY_COUNT=0
# 或者直接使用 ctest 普通模式
```

## CTest 脚本模式（高级）

可以编写 CTest 脚本（`*.cmake`）来自动化 CI 流程：

```cmake
# ci.cmake
set(CTEST_SOURCE_DIRECTORY "/path/to/source")
set(CTEST_BINARY_DIRECTORY "/path/to/build")
set(CTEST_CMAKE_GENERATOR "Ninja")
set(CTEST_BUILD_CONFIGURATION "Release")

ctest_start(Experimental)
ctest_configure(OPTIONS "-DBUILD_TESTING=ON")
ctest_build()
ctest_test(PARALLEL_LEVEL 4 RETURN_VALUE test_ret)
ctest_submit()

if(test_ret)
  message(FATAL_ERROR "Tests failed!")
endif()
```

```bash
ctest -S ci.cmake -V
```

## 关联概念

- [工作模式与工具链分发](working-mode.md) — ctest 作为独立可执行程序
- [CPack 打包集成](cpack-integration.md) — 另一个集成工具链
- [配置-生成两阶段](configure-generate.md) — CTestTestfile.cmake 在 Generate 阶段输出
