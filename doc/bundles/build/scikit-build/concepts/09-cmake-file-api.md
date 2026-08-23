---
type: concept
title: CMake File API
description: scikit-build-core 如何通过 CMake File API 程序化读取构建结果，实现可靠的构建产物发现
tags:
  - scikit-build
  - build
  - cmake
  - file-api
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/file_api/"
---

# CMake File API

CMake File API 是 CMake 3.14+ 引入的官方编程接口，允许构建工具在 configure 阶段后通过 JSON 文件读取构建系统信息。scikit-build-core 利用它替代解析 CMake stdout 来获取构建产物路径、目标信息和编译选项。

## 为什么需要 File API

传统方式获取 CMake 构建信息：

- ❌ 解析 `cmake --build` 的 stdout（格式不稳定，不可靠）
- ❌ 硬编码构建产物路径（跨平台/生成器路径不同）
- ❌ 通过 install 规则猜测文件位置（复杂项目难以准确跟踪）

File API 提供了结构化的 JSON 数据，包含：

- ✅ 所有构建目标的名称、类型、源文件
- ✅ 编译标志、宏定义、include 目录
- ✅ 安装路径和 artifact 路径
- ✅ 生成器名称和配置

## Stateless Query

scikit-build-core 在 configure 之前调用 `stateless_query(build_dir)` 写入查询文件：

```
build_dir/.cmake/api/v1/
├── query/
│   ├── codemodel-v2           # 请求 CodeModel
│   ├── cache-v2               # 请求 CMake 缓存
│   ├── cmakeFiles-v1          # 请求文件列表
│   └── toolchains-v1          # 请求工具链信息
└── reply/
    └── ...（configure 后生成）
```

这些是空文件（零字节标记文件），CMake 在 configure 时检测到它们，自动在 reply 目录生成对应的 JSON 响应。

"Stateless" 意味着每次 configure 前重新写入查询文件，不依赖之前的查询状态。

## Reply 解析

configure 完成后，`load_reply_dir(query_dir)` 读取 reply 目录：

1. 查找 `index-*.json` 文件（最新的索引文件）
2. 解析 index，获取各对象文件路径
3. 加载并解析 CodeModel、Cache、CMakeFiles、Toolchains JSON
4. 使用 typed dataclass 模型反序列化为 Python 对象

## 类型化模型

`file_api/model/` 目录包含完整的 dataclass 类型定义：

| 模型 | 内容 |
|------|------|
| `Index` | reply 索引，指向其他对象文件 |
| `CodeModel` | 项目结构、目标列表、配置 |
| `Configuration` | 单个构建配置（Debug/Release） |
| `Target` | 单个构建目标（可执行文件/库/自定义命令） |
| `InstallRule` | 安装规则（路径、component、权限） |
| `Artifact` | 构建产物路径 |
| `Cache` | CMake 缓存变量 |
| `CMakeFiles` | CMake 处理的文件列表 |
| `Toolchains` | 编译器和工具链信息 |

### Target 关键信息

每个 `Target` 对象包含：

```python
@dataclass
class Target:
    name: str                    # 目标名（如 _core）
    type: str                    # "STATIC_LIBRARY" / "MODULE_LIBRARY" / ...
    artifacts: list[Artifact]    # 构建产物路径列表
    install_rules: list[InstallRule]  # 安装规则
    compile_groups: list[CompileGroup] # 编译信息
    source_dir: Path             # 源码目录
    build_dir: Path              # 构建目录
```

### 类型映射

CMake 目标类型到 Python 扩展模块类型的映射：

| CMake 类型 | Python 对应 |
|-----------|------------|
| `MODULE_LIBRARY` | Python C 扩展模块（.so/.pyd） |
| `SHARED_LIBRARY` | 共享库（非 Python 模块） |
| `EXECUTABLE` | 可执行文件 |
| `STATIC_LIBRARY` | 静态库 |

## scikit-build-core 如何使用 File API

### 构建产物发现

CMaker.configure() 加载 File API 后，scikit-build-core 使用 CodeModel 信息：

1. 识别所有 `MODULE_LIBRARY` 目标（Python 扩展模块）
2. 获取它们的 artifact 路径（编译后的 .so/.pyd 位置）
3. 验证 install 规则是否正确指向 Python 包目录
4. 检测是否有未安装的编译产物

### 安装验证

通过 `install_rules` 验证：

- 目标是否被 install 到正确位置
- install component 是否正确
- 路径是否在 wheel 临时目录内

### 错误诊断

File API 信息用于生成更友好的错误信息：

- "Target _core is a MODULE_LIBRARY but has no install rule"
- "Target _core is installed to the wrong location"
- 列出所有发现的目标和它们的类型

## 跨平台路径处理

File API 返回的路径是 CMake 内部路径格式（使用 `/`），scikit-build-core 自动转换为平台原生路径。

## 版本兼容性

| CMake 版本 | File API 支持 |
|-----------|-------------|
| < 3.14 | ❌ 不支持（scikit-build-core 要求 CMake 3.15+） |
| 3.14 ~ 3.25 | 基本 CodeModel v2 |
| 3.26+ | 增强的 target 信息 |

scikit-build-core 要求 CMake 3.15+ 以确保 File API 可用。
