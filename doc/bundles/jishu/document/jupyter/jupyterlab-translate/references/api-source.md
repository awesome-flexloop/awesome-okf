---
type: Reference
title: API层源码映射
description: jupyterlab-translate API模块（api.py）的函数签名、参数和调用关系映射
tags: [api, orchestration, layer]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: api-source
    resource: /references/api-source.md
    title: api.py 源码
---

# API层源码映射

本文档记录 `jupyterlab_translate/api.py` 模块中的所有公开函数。

## 模块信息

- **源文件**：`jupyterlab_translate/api.py`
- **角色**：编排层，连接CLI和核心工具函数
- **依赖**：constants, converters, utils

## 函数清单

| 函数 | 签名 | 源码行 | 调用的核心函数 |
|------|------|--------|---------------|
| `check_locales` | `(locales: List[str]) -> None` | 第25-38行 | `utils.check_locale()` |
| `normalize_project` | `(project: str) -> str` | 第41-50行 | （纯字符串操作） |
| `extract_package` | `(package_repo_dir, project, merge: bool = True) -> None` | 第53-66行 | `utils.extract_translations()` |
| `update_package` | `(package_repo_dir, project, locales) -> None` | 第69-84行 | `utils.update_translations()` |
| `compile_package` | `(package_repo_dir, project, locales) -> None` | 第87-100行 | `utils.compile_translations()`, `converters.convert_catalog_to_json()`, `utils.compile_to_mo()` |
| `extract_language_pack` | `(package_repo_dir, language_packs_repo_dir, project, merge: bool = True) -> None` | 第103-121行 | `utils.extract_translations()` |
| `update_language_pack` | `(package_repo_dir, language_packs_repo_dir, project, locales) -> None` | 第124-141行 | `utils.update_translations()` |
| `compile_po_file` | `(po_path: Path) -> None` | 第144-156行 | `converters.convert_catalog_to_json()`, `utils.compile_to_mo()` |
| `compile_language_pack` | `(language_packs_repo_dir, project, locales) -> None` | 第159-209行 | `utils.compile_translations()`, `converters.convert_catalog_to_json()`, `utils.compile_to_mo()`, `utils.create_new_language_pack()` |

## 关键逻辑说明

### 路径计算差异

- **独立包模式**：output_dir = `package_repo_dir / project`（normalize后）
- **语言包模式 - jupyterlab核心**：output_dir = `language_packs_repo_dir / "jupyterlab"`
- **语言包模式 - 扩展**：output_dir = `language_packs_repo_dir / "extensions" / project`（extract/update时为 `"jupyterlab_extensions"`）

### compile_language_pack的文件移动

编译完成后，将.mo和.json文件移动到：
`language_packs_dir / "jupyterlab-language-pack-{locale}" / "jupyterlab_language_pack_{locale}" / "locale" / "{locale}" / "LC_MESSAGES" /`

## 相关概念

- [架构总览](../concepts/02-architecture-overview.md)
- [CLI命令参考](../concepts/03-cli-commands.md)
- [核心工具源码映射](utils-source.md)
- [格式转换源码映射](converters-source.md)
