---
type: Concept
title: Lockfile 定制
description: 使用 PyodideLockAddon 定制 pyodide-lock.json，控制预加载包、添加额外 wheels、版本约束和包排除
tags: [lockfile, pyodide-lock, uv, dependency, custom, optimization]
prerequisites: ["04-build-addons"]
objectives: ["理解 pyodide-lock.json 的作用", "掌握 PyodideLockAddon 的配置选项", "学会定制 lockfile 优化加载性能"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: addon-lock
    resource: /references/addon-source.md
    title: addons/lock.py
---

# Lockfile 定制

## 为什么需要定制 Lockfile

Pyodide 发行版自带一个 `pyodide-lock.json` 文件，它是一个包清单，记录了：
- 所有预编译的 WASM 包（numpy/pandas/matplotlib 等）
- 每个包的版本、文件名、SHA256 校验和、依赖关系
- 包导入名映射

默认 lockfile 包含数百个包，但你的应用可能只需要其中一小部分。加载完整 lockfile 会：
1. 增加初始下载体积（lockfile 本身约 1-2MB）
2. 导致 `loadPackagesFromImports` 查找不必要的包
3. 包含与你应用冲突的版本

PyodideLockAddon 使用 `pyodide-lock` 库（基于 `uv` 依赖解析器）来定制 lockfile，实现按需裁剪和扩展。

## pyodide-lock.json 结构

```json
{
  "info": {
    "arch": "wasm32",
    "platform": "emscripten",
    "version": "0.29.3",
    "python": "3.12"
  },
  "packages": {
    "numpy": {
      "name": "numpy",
      "version": "1.26.4",
      "file_name": "numpy-1.26.4-cp312-cp312-emscripten_wasm32.whl",
      "depends": ["setuptools"],
      "imports": ["numpy"],
      "install_dir": "site",
      "sha256": "..."
    },
    "pandas": {
      "name": "pandas",
      "version": "2.2.1",
      "depends": ["numpy", "python-dateutil", "pytz", "tzdata"],
      ...
    }
  }
}
```

关键字段：
- `packages`：所有可用包的字典，key 是包名
- `depends`：该包的依赖列表
- `imports`：该包提供的 import 模块名（用于 `loadPackagesFromImports`）
- `sha256`：wheel 文件校验和
- `file_name`：wheel 文件名

## PyodideLockAddon 配置

### 启用 Lockfile 定制

默认情况下 lockfile 定制是**禁用**的。启用方式：

```bash
jupyter lite build --pyodide-lock
```

或在 `jupyter-lite.json` 中：

```json
{
  "LiteBuildConfig": {
    "PyodideLockAddon": {
      "enabled": true
    }
  }
}
```

### 配置选项详解

| 选项 | CLI | 类型 | 说明 |
|------|-----|------|------|
| `enabled` | `--pyodide-lock` | bool | 启用 lockfile 定制（默认 false） |
| `pyodide_lock_url` | `--pyodide-lock-url` | str | 基础 lockfile URL（默认使用 Pyodide 自带） |
| `wheels` | `--pyodide-lock-wheels` | tuple[str] | 额外 wheel 文件路径 |
| `specs` | `--pyodide-lock-specs` | tuple[str] | 要添加的包 spec（如 "numpy>=1.26"） |
| `constraints` | `--pyodide-lock-constraints` | tuple[str] | 版本约束（不直接添加，只限制版本） |
| `constrain_extensions` | — | bool | 是否约束 federated extensions 的依赖版本（默认 true） |
| `excludes` | `--pyodide-lock-exclude` | tuple[str] | 要排除的包列表 |
| `prefetch` | `--pyodide-lock-prefetch` | tuple[str] | 预加载的包列表 |
| `patches` | — | dict | 直接修改 lockfile 条目的补丁 |

### 默认配置

默认排除的包（F-028）：
```python
excludes = ("test", "tests", "distutils", "setuptools", "packaging")
```

- `test`/`tests`：测试包，运行时不需要
- `distutils`：已弃用的标准库模块
- `setuptools`/`packaging`：打包工具，运行时不需要

默认预取的包（F-029）：
```python
prefetch = ("ipykernel", "comm", "pyodide-kernel", "jedi", "ipython")
```

这些是 kernel 运行必需的包，必须在启动时加载。

## 使用场景

### 场景1：添加额外的 Pyodide 包

默认 lockfile 中只包含 Pyodide 官方编译的包。如果你需要添加自己编译的 WASM wheel：

```bash
jupyter lite build --pyodide-lock \
  --pyodide-lock-wheels ./my-wheels/my-package-1.0.0-cp312-cp312-emscripten_wasm32.whl
```

```json
{
  "LiteBuildConfig": {
    "PyodideLockAddon": {
      "enabled": true,
      "wheels": ["./my-wheels/my-package-1.0.0-cp312-cp312-emscripten_wasm32.whl"]
    }
  }
}
```

wheel 文件必须是 Pyodide 兼容的（emscripten_wasm32 平台），不能是 Linux/macOS/Windows 的 wheel。

### 场景2：添加额外的包 spec

使用 `specs` 选项指定需要包含的包（及其依赖）：

```bash
jupyter lite build --pyodide-lock \
  --pyodide-lock-specs "numpy>=1.26" "pandas>=2.0" "scikit-learn"
```

这会使用 `UvPipCompile`（基于 uv 的依赖解析器）解析依赖，确保所有必要的依赖包都包含在 lockfile 中。

### 场景3：版本约束

`constraints` 用于限制依赖版本而不直接添加包。例如，如果你的应用需要 numpy >= 1.26，但不直接依赖 numpy（通过 pandas 间接依赖）：

```json
{
  "LiteBuildConfig": {
    "PyodideLockAddon": {
      "enabled": true,
      "constraints": ["numpy>=1.26"]
    }
  }
}
```

约束会影响 uv 的依赖解析结果，确保选择的版本满足约束。

### 场景4：排除不需要的包

如果某些包（及其依赖）你确定不会使用，可以排除它们来减小 lockfile 体积：

```bash
jupyter lite build --pyodide-lock \
  --pyodide-lock-exclude tkinter --pyodide-lock-exclude turtle
```

注意：排除包时要确保没有其他依赖需要它。如果排除了被其他包依赖的包，uv 解析会失败。

### 场景5：直接修补 lockfile 条目

`patches` 选项允许直接修改 lockfile 中的包条目，适用于无法通过其他配置解决的特殊情况：

```json
{
  "LiteBuildConfig": {
    "PyodideLockAddon": {
      "enabled": true,
      "patches": {
        "some-package": {
          "version": "1.0.0-custom",
          "depends": ["modified-dep"]
        }
      }
    }
  }
}
```

patches 在所有其他处理之后应用，可以覆盖任何字段。使用 patches 需要了解 lockfile 的内部结构，建议作为最后手段。

### 场景6：使用自定义基础 lockfile

如果有一个预先生成的 lockfile，可以指定 URL 作为基础：

```bash
jupyter lite build --pyodide-lock \
  --pyodide-lock-url https://my-cdn.com/my-pyodide-lock.json
```

这会加载自定义 lockfile 作为基础，然后应用 specs/constraints/excludes 等修改。

## 工作流程

启用 lockfile 定制后，`post_build` 阶段执行以下步骤：

```
1. 加载基础 lockfile
   ├─ 如果指定了 pyodide_lock_url，从 URL 加载
   └─ 否则从输出目录的 static/pyodide/pyodide-lock.json 加载（Pyodide 自带）
      ↓
2. 创建 UvPipCompile 解析器
   ├─ 加载 lockfile 中现有包作为已知包
   ├─ 注册 wheels 中的额外包
   └─ 配置 PyPI 索引（用于解析 specs 中的依赖）
      ↓
3. 解析 specs 和 constraints
   ├─ 遍历 specs，将每个包加入解析
   ├─ 应用 constraints 限制版本
   └─ 使用 uv 解析完整依赖树
      ↓
4. 如果 constrain_extensions 为 true
   └─ 将 federated extensions 的依赖也加入约束
      ↓
5. 应用 excludes
   └─ 从 lockfile 中移除指定的包及其不再需要的依赖
      ↓
6. 确保 prefetch 包存在
   └─ 检查默认和自定义 prefetch 列表中的包都在 packages 中
      ↓
7. 应用 patches
   └─ 直接修改指定包的字段
      ↓
8. 验证 lockfile 完整性
   ├─ 检查所有 depends 引用的包都存在
   └─ 检查 imports 映射正确
      ↓
9. 写出定制后的 lockfile
   └─ 保存到 {output_dir}/static/pyodide/pyodide-lock.json
```

## 与 piplite 的关系

lockfile 定制和 piplite wheel 索引是两种不同的包管理机制：

| | pyodide-lock.json | all.json（piplite） |
|---|---|---|
| **加载时机** | Pyodide 启动时自动加载 | piplite 初始化时加载 |
| **包类型** | 预编译 WASM 包（.whl with emscripten_wasm32） | 纯 Python wheels（py3-none-any） |
| **加载方式** | `pyodide.loadPackage()` 或 `loadPackagesFromImports()` | `piplite.install()` 按需安装 |
| **初始体积** | 包含在初始下载中 | 安装时才下载 |
| **适用包** | numpy/pandas/scipy 等含 C 扩展的包 | 纯 Python 业务代码包 |

最佳实践：
- 核心依赖（启动必须的）→ 通过 lockfile 预加载（prefetch 或 specs）
- 可选依赖（按需使用的）→ 通过 piplite wheels（all.json）
- PyPI 上的纯 Python 包 → 使用 PyPI 回退（不禁用）

## 注意事项

1. **lockfile 定制需要 PyodideAddon 先完成**：因为定制的 lockfile 要写入 Pyodide 输出目录，所以 `post_build` 中 PyodideLockAddon 必须在 PyodideAddon 之后执行。JupyterLite 通过 Addon 的优先级和依赖声明确保执行顺序。

2. **uv 需要网络访问**：`specs` 选项使用 uv 解析依赖，需要访问 PyPI。离线构建时不要使用 `specs`，而是直接使用 `wheels` 提供所有需要的 wheel 文件。

3. **wheel 平台标签必须正确**：添加到 lockfile 的 wheel 必须有正确的平台标签：`cp312-cp312-emscripten_wasm32`（对于 Python 3.12 + Pyodide）。标准 Linux/macOS wheel 不能用。

4. **preload vs lazy loading**：`prefetch` 列表中的包在 Pyodide 初始化时立即加载（通过 `loadPyodide({packages: [...]})`）。不在 prefetch 中的包在 `loadPackagesFromImports` 检测到 import 语句时才加载。

5. **lockfile 版本兼容性**：定制的 lockfile 必须与 Pyodide 版本匹配。如果升级 Pyodide 版本，需要重新生成 lockfile。

## 下一步

- [构建时 Addon 系统](04-build-addons.md)
- [浏览器端包管理](05-package-management.md)

## 源码参考

- [Python Addon 源码](../references/addon-source.md)
