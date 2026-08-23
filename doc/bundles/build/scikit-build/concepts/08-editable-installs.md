---
type: concept
title: 可编辑安装
description: scikit-build-core 的两种 editable 安装模式（redirect 与 inplace），rebuild-on-import 开发工作流
tags:
  - scikit-build
  - build
  - editable
  - development
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/build/_editable.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/resources/_editable_redirect.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_model.py"
---

# 可编辑安装（Editable Install）

可编辑安装（`pip install -e .`）允许开发者修改源码后无需重新安装即可测试变更。对于 C/C++ 扩展，scikit-build-core 提供了两种模式和独特的 rebuild-on-import 功能。

## 两种模式对比

| 特性 | redirect（默认） | inplace |
|------|-----------------|---------|
| 实现方式 | `.pth` + `sys.meta_path` finder | 简单 `.pth` 文件 |
| 编译产物位置 | 独立构建目录 | 源码目录（in-place build） |
| 支持 rebuild-on-import | ✅ | ❌ |
| 精确控制包加载 | ✅（白名单机制） | ❌（所有路径添加到 sys.path） |
| 隔离性 | 好（不污染源码树） | 差（构建产物在源码中） |
| 适用场景 | C/C++ 扩展开发 | 纯 Python 或简单场景 |

## Redirect 模式详解

redirect 模式是默认模式，也是 scikit-build-core 最具特色的功能之一。

### 工作原理

安装时生成两个文件到 site-packages：

1. **`.pth` 文件**（如 `my_package.pth`）：在 Python 启动时执行，加载重定向模块
2. **重定向脚本**（`_editable_redirect.py` 实例化副本）：实现自定义 `sys.meta_path` finder

```
site-packages/
├── my_package.pth               # 触发重定向加载
└── _editable_redirect/
    └── my_package.py            # 重定向逻辑（从模板实例化）
```

### 导入重定向流程

```
import my_package
      │
      ▼
Python 搜索 sys.meta_path
      │
      ▼
EditableFinder 拦截请求
      │
      ├── 检查是否在重定向映射中
      │     ├── my_package → /path/to/src/my_package（源码 .py 文件）
      │     └── my_package._core → /path/to/build/_core*.so（编译产物）
      │
      └── 不在映射中 → 回退到正常 import 流程
```

### rebuild-on-import

设置 `editable.rebuild = true` 后，每次导入 C 扩展模块时：

1. EditableFinder 检查构建产物是否存在且最新
2. 如果源码已变更，自动触发 CMake 重构建
3. 构建完成后加载新编译的模块

```toml
[tool.scikit-build.editable]
mode = "redirect"
rebuild = true
verbose = true
```

这实现了真正的"修改源码→保存→运行测试"循环，无需手动运行 build 命令。

### rebuild_dir：独立构建目录

```toml
[tool.scikit-build.editable]
mode = "redirect"
rebuild = true
rebuild-dir = "build/editable"
```

- 编译产物安装到 `build/editable/` 独立目录，而非系统 site-packages
- 源码树保持干净（不产生 .so 文件污染）
- 自动启用 rebuild-on-import
- 多个 editable 包互不干扰

### verbose 模式

`editable.verbose = true`（默认）时，导入时输出：

```
[scikit-build-core editable] Redirecting my_package -> /path/to/src/my_package
[scikit-build-core editable] Redirecting my_package._core -> /path/to/build/_core...
```

## Inplace 模式

inplace 模式是传统方式，生成简单的 `.pth` 文件将源码目录添加到 `sys.path`：

```toml
[tool.scikit-build.editable]
mode = "inplace"
```

### 工作原理

1. CMake 构建时设置 `CMAKE_LIBRARY_OUTPUT_DIRECTORY` 为源码目录
2. 编译产物（.so/.pyd）直接输出到 Python 包目录中
3. `.pth` 文件将源码根目录添加到 `sys.path`
4. Python 直接从源码目录导入

### 适用场景

- 纯 Python 包（无 C 扩展）
- 简单项目，不介意构建产物污染源码树
- 兼容 IDE 索引（编译产物在源码目录中，IDE 可以直接找到）

## 模式选择建议

```
有 C/C++ 扩展？
├── 是 → 需要 rebuild-on-import？
│   ├── 是 → redirect + rebuild=true（推荐）
│   └── 否 → redirect（默认，无需 rebuild）
└── 否（纯 Python）
    └── inplace（简单，开销最小）
```

## 注意事项

1. **rebuild-on-import 有性能开销**：每次导入都检查文件时间戳，大型项目可能较慢
2. **rebuild_dir 推荐配合版本控制**：将 `build/editable/` 加入 `.gitignore`
3. **redirect 模式不支持 namespace packages 的所有场景**：复杂 namespace 包可能需要 inplace 模式
4. **inplace 模式需要先构建一次**：`pip install -e .` 后扩展模块 .so 文件出现在源码目录中
5. **多 Python 环境**：每个 Python 环境的 editable 安装独立，rebuild_dir 中可能有多个 Python 版本的产物
