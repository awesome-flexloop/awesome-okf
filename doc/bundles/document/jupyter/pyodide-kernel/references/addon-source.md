---
type: Reference
title: Python Addon 源码参考
description: jupyterlite-pyodide-kernel 构建端三个 Addon（PyodideAddon/PipliteAddon/PyodideLockAddon）的源码结构和核心 API 参考
tags: [addon, build, python, cli]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: addon-pyodide
    resource: /references/addon-source.md
    title: "addons/pyodide.py"
  - id: addon-piplite
    resource: /references/addon-source.md
    title: "addons/piplite.py"
  - id: addon-lock
    resource: /references/addon-source.md
    title: "addons/lock.py"
  - id: addon-base
    resource: /references/addon-source.md
    title: "addons/_base.py"
---

## 源码文件位置

Python 构建端 Addon 位于 `jupyterlite_pyodide_kernel/addons/` 目录，源码路径：
`external/libs/jupyter/pyodide-kernel/jupyterlite_pyodide_kernel/addons/`

## 核心模块清单

| 文件 | 类/函数 | 说明 |
|------|---------|------|
| `_base.py` | `_BaseAddon` | Addon 基类，继承自 `jupyterlite_core.addons.base.BaseAddon` |
| `pyodide.py` | `PyodideAddon` | 管理 Pyodide 发行版的下载、缓存、复制和配置 |
| `piplite.py` | `PipliteAddon` | 管理 piplite wheel 包的下载、索引生成和配置注入 |
| `piplite.py` | `get_wheel_fileinfo()` | 生成 Warehouse-like wheel 元数据（含 sha256/md5） |
| `piplite.py` | `write_wheel_index()` | 写出 `all.json` wheel 索引文件 |
| `lock.py` | `PyodideLockAddon` | 使用 pyodide-lock + uv 定制 pyodide-lock.json |
| `lock.py` | `UvPipCompile` | 来自 `pyodide_lock.uv_pip_compile`，用于依赖解析 |

## _BaseAddon 核心 API

```python
class _BaseAddon(BaseAddon):
    @property
    def output_extensions(self) -> Path: ...
    def get_pyodide_settings(self, config_path: Path) -> dict: ...
    def set_pyodide_settings(self, config_path: Path, settings: dict) -> None: ...
    def get_output_config_paths(self) -> Generator[Path, None, None]: ...
    def get_lite_plugin_settings(self, config_path: Path, plugin_id: str) -> dict: ...
    def set_lite_plugin_settings(self, config_path: Path, plugin_id: str, settings: dict) -> None: ...
```

- `get_pyodide_settings` / `set_pyodide_settings` 是便捷方法，内部使用插件 ID `@jupyterlite/pyodide-kernel-extension:kernel`
- `get_lite_plugin_settings` 同时支持 `jupyter-lite.json` 和 notebook metadata 两种配置源
- 配置路径嵌套结构：`config_data → litePluginSettings → <plugin_id>`

## PyodideAddon Traits 配置

```python
class PyodideAddon(_BaseAddon):
    pyodide_url: str = Unicode(allow_none=True).tag(config=True)
    # CLI alias: --pyodide
```

生命周期方法：
- `status(manager)`: 报告 pyodide URL、缓存和本地文件状态
- `post_init(manager)`: 如果设置了 pyodide_url，下载/解压 pyodide 发行版到缓存
- `build(manager)`: 将本地/缓存的 pyodide 复制到输出目录 `static/pyodide/`
- `post_build(manager)`: 更新 `jupyter-lite.json`，将 pyodideUrl 指向本地 `pyodide.mjs`
- `check(manager)`: 验证 pyodide 配置路径的正确性

## PipliteAddon Traits 配置

```python
class PipliteAddon(_BaseAddon):
    piplite_urls: list[str] = List().tag(config=True)
    # CLI alias: --piplite-wheels
```

生命周期方法：
- `post_init(manager)`: 下载用户指定 URL 的 wheel 文件
- `build(manager)`: 从 `lite_dir/pypi/` 复制本地 wheels 到输出目录
- `post_build(manager)`: 生成 `pypi/all.json` 索引，更新 `jupyter-lite.json` 的 pipliteUrls
- `check(manager)`: 验证 wheel 索引 JSON 符合 schema

## PyodideLockAddon Traits 配置

```python
class PyodideLockAddon(_BaseAddon):
    enabled: bool = Bool(default_value=False).tag(config=True)      # --pyodide-lock
    pyodide_lock_url: str | None = Unicode(allow_none=True).tag(config=True)
    wheels: tuple[str, ...] = TypedTuple(Unicode()).tag(config=True)
    specs: tuple[str, ...] = TypedTuple(Unicode()).tag(config=True)
    constraints: tuple[str, ...] = TypedTuple(Unicode()).tag(config=True)
    constrain_extensions: bool = Bool(True).tag(config=True)
    excludes: tuple[str, ...] = TypedTuple(Unicode(), default_value=[...]).tag(config=True)
    prefetch: tuple[str, ...] = TypedTuple(Unicode(), default_value=[...]).tag(config=True)
    patches: dict[str, Any] = Dict().tag(config=True)
```

CLI flags/aliases 详见 `lock.py` L67-86。

## 相关概念

- [构建时 Addon 系统](../concepts/04-build-addons.md)
- [Lockfile 定制](../concepts/08-lockfile-customization.md)
- [浏览器端包管理](../concepts/05-package-management.md)
