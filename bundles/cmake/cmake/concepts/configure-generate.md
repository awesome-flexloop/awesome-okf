---
type: concept
title: "Configure-Generate 两阶段执行"
description: "CMake Configure 阶段（解析+执行脚本）和 Generate 阶段（输出构建文件）的详细流程与关键数据传递"
sources:
  references: [../references/cmake-class.md, ../references/cmmakefile.md, ../references/cmglobalgenerator.md]
  facts: [F-003, F-004, F-006, F-054, F-084, F-087]
---

# Configure-Generate 两阶段执行

## 核心理解

CMake 的构建配置过程严格分为两个阶段：

| 阶段 | 入口 | 输入 | 输出 | 可重复 |
|------|------|------|------|--------|
| **Configure** | `cmake::Configure()` | CMakeLists.txt + 环境 + 缓存 | cmState 完整状态树 | 是（重新 Configure） |
| **Generate** | `cmake::Generate()` | cmState 状态树 | 构建系统文件（Makefile/.ninja/.sln） | 随 Configure 自动执行 |

```
用户命令：cmake -S . -B build -G Ninja
            │
            ▼
    ┌───────────────┐
    │  解析命令行参数 │
    │  -S/-B/-G/-D  │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ CreateGlobal  │ ← 工厂创建 cmGlobalNinjaGenerator
    │ Generator()   │
    └───────┬───────┘
            │
            ▼
┌──────────────────────────────────────────┐
│           Configure 阶段                  │
│                                          │
│  1. 初始化编译器检测（EnableLanguage）    │
│  2. 加载内置模块（CMakeGenericSystem等）  │
│  3. 递归解析并执行 CMakeLists.txt         │
│     ├─ cmListFile 分词器解析文件          │
│     ├─ cmMakefile::ExecuteCommand()      │
│     ├─ add_subdirectory() 递归子目录      │
│     ├─ set/project/add_executable/...    │
│     └─ cmStateSnapshot 快照累积状态       │
│  4. 计算目标依赖图                        │
│  5. 写入 CMakeCache.txt                  │
│                                          │
│  输出：cmState（完整状态树）               │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│           Generate 阶段                   │
│                                          │
│  1. Compute() — 计算依赖关系、链接传播     │
│  2. 遍历每个 cmLocalGenerator             │
│     └─ 生成目录级构建规则                  │
│  3. 输出顶层构建文件                      │
│     ├─ Makefile / build.ninja / .sln      │
│     ├─ CMakeFiles/TargetDirectories.txt  │
│     ├─ CTestTestfile.cmake               │
│     └─ CPackConfig.cmake                 │
│  4. 输出 file-api 响应（供IDE使用）        │
│                                          │
│  输出：构建系统文件                        │
└───────────────┬──────────────────────────┘
                │
                ▼
    ┌───────────────┐
    │ 构建完成，用户可运行：
    │ cmake --build build
    └───────────────┘
```

## Configure 阶段详解

### 步骤 1：初始化

```cpp
// cmake.cxx Configure() 简化流程
bool cmake::Configure(const std::string& srcDir, const std::string& buildDir, bool clean) {
  // 1. 设置目录
  this->SetHomeDirectory(srcDir);
  this->SetHomeOutputDirectory(buildDir);

  // 2. 添加 CMake 内置路径（CMAKE_ROOT、模块路径等）
  this->AddCMakePaths();

  // 3. 创建 cmState 根快照
  this->State = new cmState();
  this->State->SetGlobalProperty("CMAKE_GENERATOR", genset);

  // 4. 创建顶层 cmMakefile
  this->Makefile = std::make_unique<cmMakefile>(this, this->State->CreateBaseSnapshot());

  // 5. 加载内置脚本（编译器检测、平台信息）
  this->Makefile->ReadListFile(Modules/CMakeGenericSystem.cmake);
  this->Makefile->ReadListFile(Modules/CMakeInitializeConfigs.cmake);
}
```

### 步骤 2：执行顶层 CMakeLists.txt

```cpp
// 执行项目根目录的 CMakeLists.txt
if (!this->Makefile->ReadListFile(srcDir + "/CMakeLists.txt")) {
  return false; // 配置失败
}
```

`ReadListFile` 的核心流程：
1. 读取文件内容
2. `cmListFile::ParseFile()` 分词（识别命令名、参数、括号、引号）
3. 返回 `std::vector<cmListFileFunction>` 命令列表
4. 遍历每个命令，调用 `ExecuteCommand()`

### 步骤 3：递归处理 add_subdirectory()

`cmMakefile::AddSubDirectory()` 处理 `add_subdirectory(child)`：
1. 在 cmState 上创建新的 BuildsystemDirectory 快照
2. 创建新的 cmMakefile 实例（与子目录快照关联）
3. 创建对应的 cmLocalGenerator
4. 调用子 cmMakefile 的 `ReadListFile(child/CMakeLists.txt)`
5. 子目录的目标、测试、安装规则合并到全局状态

这是一个**深度优先递归**过程，直到遍历完整个源码树。

### 步骤 4：Configure 结束的计算

所有 CMakeLists.txt 执行完毕后，GlobalGenerator 执行 Compute：
- `cmGlobalGenerator::Compute()` — 建立目标间依赖关系
- 传播 INTERFACE 链接库、编译选项、包含目录
- 解析生成器表达式（`$<CONFIG:Debug>`、`$<TARGET_FILE:tgt>` 等）
- 检测循环依赖

## Generate 阶段详解

Generate 阶段**不执行任何用户脚本**，完全使用 Configure 阶段累积的状态。

### 单配置生成器（Ninja/Makefile）输出示例

```
build/
├── build.ninja                  # Ninja 主文件
├── CMakeCache.txt               # 缓存变量（Configure 阶段写入）
├── CMakeFiles/
│   ├── CMakeConfigureLog.yaml   # 配置日志
│   ├── TargetDirectories.txt    # 目标目录映射
│   ├── rules.ninja              # 编译/链接规则
│   ├── build-(target).ninja     # 每个目标的构建语句
│   └── rules-<lang>.ninja       # 语言特定规则
├── CTestTestfile.cmake          # CTest 测试发现文件
├── CPackConfig.cmake            # CPack 配置
└── cmake_install.cmake          # install 规则脚本
```

### 多配置生成器（VS/Xcode）输出示例

```
build/
├── ALL_BUILD.vcxproj            # 顶层目标
├── MyApp.sln                    # Visual Studio 解决方案
├── MyApp.vcxproj                # 目标项目文件
├── CMakeSettings.json           # IDE 设置
└── CMakeFiles/
    └── ...
```

## file-api：Generate 阶段的现代输出

CMake 3.14+ 支持 file-api，在 Generate 阶段输出结构化的 JSON 描述：

```
build/.cmake/api/v1/reply/
├── cache-v2-*.json          # 缓存变量
├── cmakeFiles-v1-*.json     # 处理的文件列表
├── codemodel-v2-*.json      # 完整代码模型（目录、目标、源文件）
├── toolchains-v1-*.json     # 工具链信息
└── index-*.json             # 索引
```

IDE（VS Code、CLion、Qt Creator）通过 file-api 获取项目结构，不依赖 SERVER 模式。

## 重新 Configure 的触发条件

CMake 自动检测何时需要重新 Configure：
- `CMakeLists.txt` 或 `*.cmake` 模块被修改
- `CMakeCache.txt` 被修改（如 `-D` 参数变化）
- 依赖的 CMake 版本变化

重新 Configure 由构建工具在构建时自动触发（如 ninja 检测到 CMakeLists.txt 变化会自动重新运行 CMake）。

## 关联概念

- [整体架构](overall-architecture.md) — 两阶段在整体架构中的位置
- [多生成器工厂模式](generator-pattern.md) — Generate 阶段的多态实现
- [状态快照机制](state-snapshot.md) — Configure 阶段的状态累积方式
- [目标模型](target-model.md) — Configure 阶段创建的核心数据结构
