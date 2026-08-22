---
type: Concept
title: 构建时 Addon 系统
description: 三个 JupyterLite Addon（PyodideAddon/PipliteAddon/PyodideLockAddon）的工作机制和生命周期
tags: [addon, build, lifecycle, configuration, pyodide, piplite, lockfile]
prerequisites: ["01-getting-started", "02-architecture-overview"]
objectives: ["理解 JupyterLite Addon 生命周期钩子", "掌握三个 Addon 的职责和配置", "学会自定义 Pyodide 发行版和 wheel 包"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: addon-pyodide
    resource: /references/addon-source.md
    title: addons/pyodide.py
  - id: addon-piplite
    resource: /references/addon-source.md
    title: addons/piplite.py
  - id: addon-lock
    resource: /references/addon-source.md
    title: addons/lock.py
  - id: constants
    resource: /references/addon-source.md
    title: constants.py
---

# 构建时 Addon 系统

## 为什么需要构建时 Addon

JupyterLite 是纯静态站点，但 Python 运行时（Pyodide WASM）和第三方包（wheels）是大型二进制资源。这些资源需要在构建阶段被下载、组织、配置好，才能在浏览器中通过 HTTP 静态加载。

JupyterLite 提供 Addon 插件系统，允许扩展在构建生命周期的各个阶段执行自定义逻辑。pyodide-kernel 注册了三个 Addon，分别负责 Pyodide 发行版管理、piplite 包管理和 Lockfile 定制。

## Addon 生命周期

JupyterLite Addon 遵循以下生命周期钩子，按顺序执行：

```
1. post_init(manager)    — 初始化阶段：下载外部资源
2. build(manager)         — 构建阶段：复制文件到输出目录
3. post_build(manager)   — 构建后阶段：生成配置、索引
4. check(manager)        — 检查阶段：验证构建结果
5. status(manager)       — 状态查询：报告当前配置状态
```

三个 Addon 共享一个基类 `_BaseAddon`，提供了配置读写的便捷方法。

## _BaseAddon 基类

所有 pyodide-kernel Addon 继承自 `_BaseAddon`（F-031），它提供了几个关键工具方法：

### 配置路径管理

```python
@property
def output_extensions(self) -> Path:
    """输出目录中的 extensions 路径：{output_dir}/extensions"""
```

### Pyodide 设置读写

```python
def get_pyodide_settings(self, config_path: Path) -> dict:
    """获取 Pyodide Kernel 插件设置
    等价于：config_data['litePluginSettings'][PYODIDE_KERNEL_PLUGIN_ID]
    """

def set_pyodide_settings(self, config_path: Path, settings: dict) -> None:
    """更新 Pyodide Kernel 插件设置
    写入：config_data['litePluginSettings'][PYODIDE_KERNEL_PLUGIN_ID]
    """
```

其中插件 ID 为常量 `PYODIDE_KERNEL_PLUGIN_ID`：

```python
PYODIDE_KERNEL_PLUGIN_ID = "@jupyterlite/pyodide-kernel-extension:kernel"  # F-023
```

### 通用插件设置读写

```python
def get_lite_plugin_settings(self, config_path: Path, plugin_id: str) -> dict:
    """获取任意插件的设置，支持 jupyter-lite.json 和 notebook metadata 两种来源"""

def set_lite_plugin_settings(self, config_path: Path, plugin_id: str, settings: dict) -> None:
    """更新任意插件的设置"""
```

### 配置文件发现

```python
def get_output_config_paths(self) -> Generator[Path, None, None]:
    """遍历输出目录中所有 jupyter-lite*.json 配置文件"""
```

## PyodideAddon

负责管理 Pyodide WASM 发行版的下载、缓存和部署（F-018）。

### Trait 配置

```python
pyodide_url = Unicode(allow_none=True).tag(config=True)
# CLI 别名：--pyodide
```

### 生命周期实现

**status(manager)**：
- 报告当前 pyodide URL（自定义 URL 或默认 CDN URL）
- 检查缓存目录中是否有已下载的发行版
- 检查输出目录中是否有已部署的发行版

**post_init(manager)**：
1. 如果未设置 `pyodide_url`，直接返回（使用默认 CDN）
2. 如果设置了本地路径（`file://` 或本地文件路径），记录本地路径
3. 如果设置了远程 URL，下载到缓存目录 `{cache_dir}/pyodide/{hash}/`
4. 解压下载的 tar.bz2 文件
5. 验证解压后包含 `pyodide.mjs` 和 `pyodide-lock.json`

**build(manager)**：
1. 确定 Pyodide 源路径（本地路径或缓存路径）
2. 将整个 Pyodide 目录复制到输出目录 `{output_dir}/static/pyodide/`
3. 保留文件结构（pyodide.mjs、python_stdlib.zip、*.wasm、packages/ 等）

**post_build(manager)**：
1. 遍历所有输出配置文件（`get_output_config_paths()`）
2. 调用 `set_pyodide_settings()` 更新配置：
   - 设置 `pyodideUrl` 为本地路径 `./static/pyodide/pyodide.mjs`（或 CDN URL）
3. 确保配置包含 piplite wheel URL

**check(manager)**：
1. 验证配置中的 pyodideUrl 路径存在
2. 验证 pyodide.mjs 文件存在

### 缓存策略

PyodideAddon 使用 URL 的 SHA256 哈希作为缓存目录名：

```
{cache_dir}/pyodide/
└── {url_sha256}/
    └── pyodide/
        ├── pyodide.mjs
        ├── pyodide-lock.json
        ├── python_stdlib.zip
        └── ...
```

同一 URL 只下载一次，后续构建直接使用缓存。

## PipliteAddon

负责管理 piplite wheel 包的下载、索引生成和配置（F-022）。

### Trait 配置

```python
piplite_urls = List().tag(config=True)
# CLI 别名：--piplite-wheels
```

接受 URL 列表，每个 URL 指向一个 `.whl` 文件。

### 生命周期实现

**post_init(manager)**：
1. 遍历 `piplite_urls` 列表
2. 对每个 URL：下载 wheel 文件到缓存目录
3. 支持本地文件路径和远程 URL

**build(manager)**：
1. 从多个来源收集 wheel 文件：
   - 缓存中下载的 wheels（来自 `piplite_urls`）
   - `{lite_dir}/pypi/` 目录中的本地 wheels
   - federated extensions 提供的 wheels
2. 将所有 wheels 复制到输出目录 `{output_dir}/pypi/*.whl`

**post_build(manager)**：
1. 扫描输出目录中所有 wheel 文件
2. 对每个 wheel 调用 `get_wheel_fileinfo()` 生成元数据：
   ```python
   {
     "filename": "package-1.0.0-py3-none-any.whl",
     "url": "./pypi/package-1.0.0-py3-none-any.whl",
     "sha256": "<hex digest>",
     "md5": "<hex digest>",
     "releases": [{ "filename": "...", "url": "...", "digests": {...} }]
   }
   ```
3. 写出 `{output_dir}/pypi/all.json` — Warehouse-like 索引
4. 更新 `jupyter-lite.json` 的 `pipliteUrls` 配置，包含：
   - 本地 `all.json?sha256=<checksum>`
   - federated extensions 的 wheel 索引

**check(manager)**：
1. 验证 `all.json` 符合 JSON Schema
2. 验证索引中引用的 wheel 文件存在
3. 验证 sha256 校验和

### Wheel 索引格式

生成的 `all.json` 遵循 PEP 503 (Simple Repository API) 的 JSON 变体，结构类似于 PyPI 的 JSON API：

```json
{
  "package-name": {
    "filename": "package-name-1.0.0-py3-none-any.whl",
    "url": "./pypi/package-name-1.0.0-py3-none-any.whl",
    "sha256": "abcdef...",
    "md5": "123456...",
    "releases": [
      {
        "filename": "package-name-1.0.0-py3-none-any.whl",
        "url": "./pypi/package-name-1.0.0-py3-none-any.whl",
        "digests": {
          "sha256": "abcdef...",
          "md5": "123456..."
        }
      }
    ]
  }
}
```

piplite 包管理器在浏览器端加载这个索引，用于查找可用的本地 wheel 包。

## PyodideLockAddon

使用 `pyodide-lock` 工具和 `uv` 包管理器定制 `pyodide-lock.json`，用于控制哪些包被预加载、添加额外 wheels、添加约束等（F-026）。

### Trait 配置

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 lockfile 定制（`--pyodide-lock`） |
| `pyodide_lock_url` | str/None | `None` | 基础 lockfile URL（默认使用 Pyodide 自带） |
| `wheels` | tuple | `()` | 额外 wheel 文件路径 |
| `specs` | tuple | `()` | 要添加到 lockfile 的包 spec（如 "numpy>=1.20"） |
| `constraints` | tuple | `()` | 版本约束 |
| `constrain_extensions` | bool | `True` | 是否约束 federated extensions 的依赖版本 |
| `excludes` | tuple | 内置列表 | 要排除的包（F-028） |
| `prefetch` | tuple | 内置列表 | 要预加载的包（F-029） |
| `patches` | dict | `{}` | lockfile 补丁（直接修改条目） |

默认排除的包（F-028）：`test`,tests,distutils,setuptools,packaging`
默认预取的包（F-029）：`ipykernel,comm,pyodide-kernel,jedi,ipython`

### CLI 选项

PyodideLockAddon 注册了丰富的 CLI 选项：

| CLI 选项 | 说明 |
|----------|------|
| `--pyodide-lock` | 启用 lockfile 定制 |
| `--pyodide-lock-url` | 指定基础 lockfile URL |
| `--pyodide-lock-wheels` | 添加 wheel 文件 |
| `--pyodide-lock-specs` | 添加包 spec |
| `--pyodide-lock-constraints` | 添加版本约束 |
| `--pyodide-lock-exclude` | 排除包 |
| `--pyodide-lock-prefetch` | 预取包 |

### 工作流程

启用后，`post_build` 阶段执行：

```
1. 加载基础 pyodide-lock.json（来自 Pyodide 发行版或自定义 URL）
2. 使用 UvPipCompile 解析 specs 中的额外依赖
3. 应用 constraints 约束版本
4. 将额外 wheels 添加到 lockfile
5. 应用 excludes 移除不需要的包
6. 确保 prefetch 列表中的包在 packages 中
7. 应用 patches 直接修改条目
8. 写出定制后的 pyodide-lock.json 到输出目录
```

## 核心常量

构建端关键常量定义在 `jupyterlite_pyodide_kernel/constants.py`：

| 常量 | 值 | 说明 |
|------|---|------|
| `PYODIDE_VERSION` | `"0.29.3"` | 目标 Pyodide 版本（F-014） |
| `PYODIDE_API_INDEX_URL` | CDN jsdelivr URL | Pyodide 包索引基础 URL（F-034） |
| `PYODIDE_URL` | `{CDN}/v{version}/full/pyodide.mjs` | 默认 pyodide.mjs URL（F-037） |
| `PYODIDE_KERNEL_PLUGIN_ID` | `"@jupyterlite/pyodide-kernel-extension:kernel"` | 插件设置 ID（F-023） |
| `DISABLE_PYPI_FALLBACK` | `False` | 默认不禁用 PyPI 回退（F-014） |

## 配置示例

### 使用自定义 Pyodide 发行版

```bash
jupyter lite build --pyodide https://example.com/custom-pyodide.tar.bz2
```

或在 `jupyter-lite.json` 中：

```json
{
  "LiteBuildConfig": {
    "PyodideAddon": {
      "pyodide_url": "https://example.com/custom-pyodide.tar.bz2"
    }
  }
}
```

### 添加自定义 Wheel 包

```bash
jupyter lite build --piplite-wheels https://example.com/my-package-1.0.0-py3-none-any.whl
```

或在 `jupyter-lite.json` 中：

```json
{
  "LiteBuildConfig": {
    "PipliteAddon": {
      "piplite_urls": [
        "https://example.com/my-package-1.0.0-py3-none-any.whl",
        "./local-wheels/another-2.0.0-py3-none-any.whl"
      ]
    }
  }
}
```

也可以将 `.whl` 文件直接放到 `{lite_dir}/pypi/` 目录中，构建时自动索引。

## 下一步

- [浏览器端包管理](/concepts/05-package-management.md) — 构建产物如何在浏览器中被使用
- [Lockfile 定制](/concepts/08-lockfile-customization.md) — PyodideLockAddon 深入
- [基本安装与配置示例](/examples/basic-install-config.md)

## 源码参考

- [Python Addon 源码](/references/addon-source.md)
