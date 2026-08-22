---
type: concept
title: "多生成器工厂模式"
description: "cmGlobalGenerator 工厂注册机制：如何通过抽象基类+静态工厂注册表支持 Makefile/Ninja/VS/Xcode 等多种构建系统"
sources:
  references: [../references/cmglobalgenerator.md]
  facts: [F-051, F-052, F-053, F-055, F-056, F-059, F-066]
---

# 多生成器工厂模式

## 核心理解

CMake 支持生成多种构建系统文件（Makefile、Ninja、Visual Studio、Xcode 等）。这些生成器通过**抽象基类 + 静态工厂自注册**模式实现，使 Configure 阶段的逻辑与具体输出格式完全解耦。

## 工厂模式架构

```
┌─────────────────────────────────────────────┐
│              cmGlobalGenerator              │
│            (抽象基类，纯虚 Generate)         │
├─────────────────────────────────────────────┤
│ + Generate() = 0                            │
│ + CreateLocalGenerator()                    │
│ + EnableLanguage()                          │
│ + SetCMakeInstance()                        │
│ # LocalGenerators[]                         │
│ # CMakeInstance                             │
└───────────┬─────────────────────────────────┘
            │
   ┌────────┼────────────────────┐
   │        │                    │
┌──▼─────┐ ┌▼──────────────┐ ┌──▼──────────────────┐
│Unix Make│ │  Ninja        │ │ Visual Studio 2022  │
│Generator│ │ Generator     │ │ Generator           │
└────────┘ └──────────────┘ └─────────────────────┘
                              (每个VS版本一个类)

每个具体生成器都有对应的 Factory 类：
┌─────────────────────────────────────────────┐
│        cmGlobalGeneratorFactory             │
│       (工厂抽象基类)                          │
├─────────────────────────────────────────────┤
│ + CreateGlobalGenerator(name, cmake)         │
│ + GetDocumentation(entry)                    │
│ + GetGenerators() → list<name+doc>          │
└───────────┬─────────────────────────────────┘
            │
   ┌────────┼────────────────────┐
   │        │                    │
┌──▼─────┐ ┌▼──────────────┐ ┌──▼──────────────────┐
│UnixMake│ │ NinjaFactory  │ │ VS2022Factory       │
│Factory │ │ (静态实例自注册)│ │ (静态实例自注册)     │
│:static │ │               │ │                     │
│instance│ │               │ │                     │
└────────┘ └──────────────┘ └─────────────────────┘
```

## 静态自注册机制

每个具体生成器通过**静态工厂实例**在程序启动时自动注册：

```cpp
// cmGlobalNinjaGenerator.cxx
class cmGlobalNinjaGeneratorFactory : public cmGlobalGeneratorFactory {
  std::unique_ptr<cmGlobalGenerator> CreateGlobalGenerator(
      const std::string& name, cmake* cm) const override {
    if (name != "Ninja") return nullptr;  // 匹配 -G 参数
    return std::make_unique<cmGlobalNinjaGenerator>(cm);
  }

  void GetDocumentation(cmDocumentationEntry& entry) const override {
    entry.Name = "Ninja";
    entry.Brief = "Generates build.ninja files.";
  }
};

// 静态实例 — 程序启动时构造函数自注册到工厂列表
static cmGlobalNinjaGeneratorFactory pn;
```

关键特性：
- **零配置**：添加新生成器只需创建新的 .cxx 文件，无需修改任何注册代码
- **编译时可裁剪**：通过 CMake 的 `CMakeConfigure.cxx.h` 宏控制哪些生成器被编译
- **大小写不敏感匹配**：`-G ninja`、`-G NINJA`、`-G Ninja` 都可以匹配

## 生成器分类

### Makefile 类生成器

| 生成器 | 工厂类 | 平台 |
|--------|--------|------|
| Unix Makefiles | `cmGlobalUnixMakefileGenerator3Factory` | Linux/macOS/Unix |
| MinGW Makefiles | `cmGlobalMinGWMakefileGeneratorFactory` | Windows MinGW |
| MSYS Makefiles | `cmGlobalMSYSMakefileGeneratorFactory` | Windows MSYS2 |
| NMake Makefiles | `cmGlobalNMakeMakefileGeneratorFactory` | Windows MSVC NMake |
| Borland Makefiles | `cmGlobalBorlandMakefileGeneratorFactory` | Windows (遗留) |
| Watcom WMake | `cmGlobalWatcomWMakeGeneratorFactory` | Windows (遗留) |

### Ninja 类生成器

| 生成器 | 工厂类 | 说明 |
|--------|--------|------|
| Ninja | `cmGlobalNinjaGeneratorFactory` | 标准 Ninja |
| Ninja Multi-Config | `cmGlobalNinjaMultiConfigGeneratorFactory` | 支持 Debug/Release 多配置 |

### IDE 类生成器

| 生成器 | 工厂类 | 平台 |
|--------|--------|------|
| Visual Studio 17 2022 | `cmGlobalVisualStudio17GeneratorFactory` | Windows |
| Visual Studio 16 2019 | `cmGlobalVisualStudio16GeneratorFactory` | Windows |
| Xcode | `cmGlobalXCodeGeneratorFactory` | macOS |
| ... | ... | (多个 VS 版本) |

### 其他

| 生成器 | 工厂类 | 说明 |
|--------|--------|------|
| Green Hills MULTI | `cmGlobalGhsMultiGeneratorFactory` | 嵌入式 |
| CodeBlocks | 等 extra 生成器 | IDE 项目文件 + Makefile/Ninja |

## 生成器选择流程

```
cmake -G Ninja -S . -B build
        │
        ▼
cmake::SetGenerator("Ninja")
        │
        ▼
cmake::CreateGlobalGenerator("Ninja")
        │
        ▼
遍历所有已注册的 Factory → 调用 CreateGlobalGenerator("Ninja", this)
        │
        ├─ UnixMakeFactory: name != "Ninja" → nullptr
        ├─ NinjaFactory: name == "Ninja" → return cmGlobalNinjaGenerator
        ├─ VS2022Factory: name != "Ninja" → nullptr
        └─ ...
        │
        ▼
GlobalGenerator = cmGlobalNinjaGenerator 实例
        │
        ▼
Configure() → 使用此生成器的 EnableLanguage()、Compute() 等
        │
        ▼
Generate() → cmGlobalNinjaGenerator::Generate() 输出 build.ninja
```

如果未指定 `-G`，CMake 根据平台选择默认生成器：
- Windows：最新版本的 Visual Studio
- Linux/Unix：Unix Makefiles
- macOS：Xcode（如果已安装）或 Unix Makefiles

## LocalGenerator：目录级生成器

`cmGlobalGenerator` 是全局的（一个构建一个），而每个源码目录有一个 `cmLocalGenerator`：

```
cmGlobalGenerator
├── cmLocalGenerator (src/)
│   └── 生成 src/CMakeFiles/ 中的规则
├── cmLocalGenerator (src/lib/)
│   └── 生成 src/lib/CMakeFiles/ 中的规则
└── cmLocalGenerator (src/app/)
    └── 生成 src/app/CMakeFiles/ 中的规则
```

具体生成器（如 Ninja）使用对应的 LocalGenerator 子类（`cmLocalNinjaGenerator`）。

## 多配置 vs 单配置生成器

这是生成器的一个重要分类：

| 类型 | 代表 | 构建目录 | CMAKE_BUILD_TYPE |
|------|------|---------|-----------------|
| 单配置 | Makefile、Ninja | 一个配置一个构建目录 | Configure 时设置 |
| 多配置 | Visual Studio、Xcode、Ninja Multi-Config | 一个构建目录包含所有配置 | Build 时通过 `--config Debug` 选择 |

```bash
# 单配置（Ninja/Makefile）
cmake -S . -B build-debug -DCMAKE_BUILD_TYPE=Debug
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release

# 多配置（VS/Xcode/Ninja Multi-Config）
cmake -S . -B build -G "Visual Studio 17 2022"
cmake --build build --config Debug
cmake --build build --config Release
```

## 关联概念

- [配置-生成两阶段](configure-generate.md) — Generate 阶段如何使用 GlobalGenerator
- [构建类型与多配置](build-type.md) — 单配置/多配置的具体差异
- [工具链检测](toolchain-detection.md) — EnableLanguage 在生成器中的实现
