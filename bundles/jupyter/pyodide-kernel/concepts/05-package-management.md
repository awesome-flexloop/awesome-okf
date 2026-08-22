---
type: Concept
title: 浏览器端包管理
description: piplite 包管理器的三级查找策略、%pip 魔法命令拦截、micropip 包装机制
tags: [package, piplite, micropip, pip, wheel, install, import]
prerequisites: ["04-build-addons", "02-architecture-overview"]
objectives: ["理解三级包查找策略", "掌握 %pip 魔法命令的工作原理", "学会在 Notebook 中安装和使用第三方包"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: piplite
    resource: /references/piplite-source.md
    title: piplite/__init__.py
  - id: litetransform
    resource: /references/kernel-py-source.md
    title: litetransform.py
---

# 浏览器端包管理

## 为什么浏览器中需要特殊的包管理器

标准的 `pip install` 命令依赖：
1. 本地文件系统（site-packages 目录）
2. PyPI 仓库的完整索引
3. 包的解压和编译能力

在浏览器中：
- 文件系统是虚拟的（Emscripten MEMFS/IDBFS）
- 不能运行编译步骤（无 C/Fortran 编译器）
- 网络延迟高，需要预加载常用包

Pyodide 通过以下方式解决：
1. 常用包（numpy/pandas 等）预先编译为 WASM，在 `pyodide-lock.json` 中注册
2. 提供 `micropip` 包管理器，支持从 PyPI 下载纯 Python wheel
3. piplite 在 micropip 基础上增加本地 wheel 索引和自动导入加载

## 三级包查找策略

当用户执行包安装时，piplite 按三级顺序查找（F-111）：

```
┌─────────────────────────────────────────────────┐
│ 1. Pyodide 内置包（pyodide-lock.json）          │
│    - numpy, pandas, matplotlib 等预编译 WASM 包  │
│    - 加载速度最快，无需网络下载                   │
│    - 包列表在 pyodide-lock.json 的 packages 中  │
├─────────────────────────────────────────────────┤
│ 2. 本地 wheel 索引（all.json）                   │
│    - 构建时 PipliteAddon 生成                    │
│    - 包含用户自定义 wheels 和 federated wheels  │
│    - 从站点自身静态目录加载，无需访问 PyPI        │
├─────────────────────────────────────────────────┤
│ 3. PyPI 回退（pypi.org）                        │
│    - 仅当 disablePyPIFallback=False 时启用      │
│    - 支持纯 Python wheels（noarch）              │
│    - 需要网络连接，受跨域限制                    │
└─────────────────────────────────────────────────┘
```

查找逻辑：
1. 先在 `pyodide-lock.json` 的内置包中查找
2. 如果未找到，遍历 `PIPLITE_URLS` 中的所有 `all.json` 索引查找
3. 如果仍未找到且未禁用 PyPI 回退，查询 pypi.org
4. 所有来源中选择版本号最新的兼容版本

## piplite.install() API

piplite 的主要入口是 `install()` 函数（F-110）：

```python
import piplite

await piplite.install(
    requirements,        # 包名或 URL（str 或 list[str]）
    keep_going=False,    # 遇到错误是否继续
    deps=True,           # 是否安装依赖
    credentials="same-origin",  # fetch credentials
    pre=False,           # 是否允许预发布版本
    index_urls=None      # 自定义索引 URL
)
```

### 基本用法

```python
# 安装单个包
await piplite.install("numpy")

# 安装多个包
await piplite.install(["pandas", "scikit-learn"])

# 从 URL 安装 wheel
await piplite.install("https://example.com/my-package-1.0.0-py3-none-any.whl")

# 安装时忽略错误（跳过不可用的包）
await piplite.install(["package-a", "package-b"], keep_going=True)

# 禁用依赖安装
await piplite.install("my-package", deps=False)
```

### 版本约束

```python
# 精确版本
await piplite.install("numpy==1.24.0")

# 最低版本
await piplite.install("pandas>=2.0.0")

# 版本范围
await piplite.install("scipy>=1.10,<1.12")
```

## %pip 魔法命令

在 Notebook 中，用户习惯使用 `%pip install` 安装包。但在 Pyodide 环境中没有真正的 pip 命令。pyodide-kernel 通过代码预转换机制拦截 `%pip` 魔法命令。

### LiteTransformerManager

`LiteTransformerManager` 在代码执行前对 cell 内容进行转换（F-109）：

```python
class LiteTransformerManager:
    def transform_cell(self, code: str) -> str:
        """对代码进行 Pyodide 特定转换"""
```

其中 `pip_magic` 转换器将 `%pip install` 转换为 `piplite.install()`：

```python
# 转换前（用户输入）
%pip install numpy pandas

# 转换后（实际执行）
import piplite
await piplite.install(["numpy", "pandas"])
```

转换支持以下 pip 命令形式：
- `%pip install <packages>` → `piplite.install(<packages>)`
- `%pip install --pre <packages>` → `piplite.install(<packages>, pre=True)`
- `%pip install <url>` → `piplite.install(<url>)`

其他 pip 子命令（list/freeze/uninstall 等）目前不支持，会给出提示。

### 为什么需要 await？

`piplite.install()` 是异步函数（因为涉及网络下载），但 Notebook cell 中使用 `await` 需要 IPython 的异步支持。`Interpreter` 类（IPython InteractiveShell 子类）通过 `should_run_async` 判断代码是否需要异步执行，自动处理 await 调用。

## 自动导入加载（loadPackagesFromImports）

除了显式安装，pyodide-kernel 还支持**自动包加载**（F-084）：

在 `PyodideKernel.run()` 执行代码前，会调用：

```python
await pyodide_js.loadPackagesFromImports(lite_cell)
```

`loadPackagesFromImports` 是 Pyodide 内置函数，它：
1. 静态分析代码中的 `import` 语句
2. 提取顶层导入的包名
3. 如果包在 pyodide-lock.json 中但尚未加载，自动下载并加载
4. 如果包不在 lockfile 中，不做任何处理（需要用户手动 piplite.install）

这意味着对于 Pyodide 内置包（numpy/pandas/matplotlib 等），用户可以直接 `import numpy`，无需显式安装。

```python
# 这些 import 会自动触发包加载
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 但对于非内置包，仍需要先安装
await piplite.install("regex")
import regex
```

## piplite 与 micropip 的关系

piplite **不是** micropip 的替代品，而是它的包装和扩展：

```
piplite.install()
    │
    ├─→ 创建 PiplitePyPIManager（继承自 micropip.PyPIManager）
    │       │
    │       ├─→ 扩展 _query_package() 以支持本地 all.json 索引
    │       ├─→ 扩展包查找逻辑（三级查找）
    │       └─→ 支持 PIPLITE_URLS 配置
    │
    └─→ 调用 micropip 的安装逻辑
            │
            ├─→ 下载 wheel 文件
            ├─→ 解压到虚拟文件系统
            └─→ 注册到 sys.path
```

关键区别：
- **micropip**：只知道 Pyodide 内置包和 PyPI
- **piplite**：增加了本地 wheel 索引（all.json）和多索引 URL 支持

## PIPLITE_URLS 配置

在 Worker 初始化时（`initPackageManager` 阶段），piplite 的索引 URL 列表从插件配置传入：

```typescript
// worker.ts initPackageManager
piplite.set_index_urls(options.pipliteUrls);
```

默认的 `pipliteUrls` 由构建阶段 `PipliteAddon.post_build()` 生成，通常包含：

```python
[
    "./pypi/all.json?sha256=abcdef...",           # 主站点的 wheel 索引
    "../extensions/federated-ext/all.json?...",   # federated extensions 的索引
]
```

用户也可以在浏览器运行时动态添加索引：

```python
import piplite
await piplite.add_index_url("https://my-cdn.com/pypi/all.json")
```

## disablePyPIFallback

当设置 `disablePyPIFallback=True` 时，piplite 在本地索引中找不到包后不会尝试 PyPI：

```python
# jupyter-lite.json 配置
{
  "litePluginSettings": {
    "@jupyterlite/pyodide-kernel-extension:kernel": {
      "disablePyPIFallback": true
    }
  }
}
```

适用场景：
- 离线/内网部署（无法访问 pypi.org）
- 安全合规要求（只使用审核过的包）
- 确定性构建（确保所有包来自预构建的 wheels）

禁用 PyPI 回退后，只有 Pyodide 内置包和 all.json 索引中的包可以安装。

## 常见问题

### 为什么有些包安装失败？

1. **包含 C 扩展**：PyPI 上的 manylinux wheels 包含编译的 C 代码，不能在 WASM 中运行。只有纯 Python wheels（py3-none-any）可以从 PyPI 安装。包含 C 扩展的包需要在 Pyodide 中预编译。

2. **依赖不可用**：如果包的依赖不在 Pyodide 内置包或本地索引中，且 PyPI 回退禁用，安装会失败。

3. **包名与 import 名不同**：`pip install` 使用 PyPI 包名（如 `Pillow`），而 `import` 使用模块名（如 `PIL`）。`loadPackagesFromImports` 通过 Pyodide 的映射表处理这种差异。

### 如何查看已安装的包？

```python
import piplite
# piplite 目前没有 list() 方法，但可以使用 micropip
import micropip
micropip.list()  # 返回已安装包列表
```

## 下一步

- [Python 兼容性层](/concepts/06-python-compatibility.md) — IPython 适配
- [构建时 Addon 系统](/concepts/04-build-addons.md) — all.json 如何生成
- [添加自定义 Wheel 包示例](/examples/custom-wheels.md)

## 源码参考

- [piplite 源码](/references/piplite-source.md)
- [浏览器端 Python Kernel 源码](/references/kernel-py-source.md)
