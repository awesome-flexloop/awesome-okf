---
type: Reference
title: 运行时发现模块源码映射
description: jupyterlab-translate finder模块（finder.py）的entry point发现机制
tags: [finder, entry-points, runtime, discovery, language-pack]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: finder-source
    resource: /references/finder-source.md
    title: finder.py 源码
---

# 运行时发现模块源码映射

本文档记录 `jupyterlab_translate/finder.py` 模块的函数和entry point发现机制。

## 模块信息

- **源文件**：`jupyterlab_translate/finder.py`
- **角色**：运行时发现已安装的语言包和扩展locale数据
- **外部依赖**：importlib.metadata / importlib_metadata, json, os

## Entry Point常量

| 常量 | 值 | 源码行 | 用途 |
|------|-----|--------|------|
| `JUPYTERLAB_LANGUAGEPACK_ENTRY` | `"jupyterlab.languagepack"` | 第16行 | 发现集中式语言包 |
| `JUPYTERLAB_LOCALE_ENTRY` | `"jupyterlab.locale"` | 第17行 | 发现扩展包自带locale数据 |

## 函数清单

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `merge_data` | `() -> None` | 第20-23行 | 合并语言包数据（空实现，未完成） |
| `get_installed_packages_locale` | `(locale: str) -> dict` | 第26-66行 | 获取所有包含指定locale数据的已安装扩展包 |
| `get_installed_language_packs` | `() -> list` | 第69-81行 | 返回所有已安装语言包名称列表 |
| `get_language_pack` | `(locale: str) -> dict` | 第84-101行 | 获取指定locale的语言包数据（Jed格式dict） |

## Python版本兼容

- Python < 3.10：使用 `importlib_metadata.entry_points`（第三方包）
- Python >= 3.10：使用标准库 `importlib.metadata.entry_points`

## Entry Point配置示例

### 语言包（jupyterlab.languagepack）

```toml
[project.entry-points."jupyterlab.languagepack"]
ko_KR = "jupyterlab_language_pack_ko_KR"
```

### 扩展包自带locale（jupyterlab.locale）

```toml
[project.entry-points."jupyterlab.locale"]
jupyterlab-git = "jupyterlab_git"
```

扩展包需在包目录下包含 `locale/<locale>/LC_MESSAGES/<name>.json` 文件。

## 相关概念

- [运行时语言包发现](../concepts/08-runtime-discovery.md)
- [Hatch构建钩子集成](../concepts/07-hatch-build-hook.md)
- [双模式分发机制](../concepts/11-dual-mode-distribution.md)
