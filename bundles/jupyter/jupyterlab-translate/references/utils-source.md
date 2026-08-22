---
type: Reference
title: 核心工具模块源码映射
description: jupyterlab-translate utils模块（utils.py）的函数签名、参数和功能说明
tags: [utils, core, extraction, compilation, catalog]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: utils-source
    resource: /references/utils-source.md
    title: utils.py 源码
---

# 核心工具模块源码映射

本文档记录 `jupyterlab_translate/utils.py` 模块中的所有公开函数。

## 模块信息

- **源文件**：`jupyterlab_translate/utils.py`
- **角色**：核心功能实现层
- **外部依赖**：babel, copier, polib, subprocess, json, re, tempfile, shutil

## 函数清单

### 版本与Locale工具

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `get_version` | `(repo_root_path: Path, project: str) -> str` | 第38-89行 | 按优先级获取版本：setup.py/hatch → package.json → git describe |
| `check_locale` | `(locale: str) -> bool` | 第128-141行 | 验证locale有效性，白名单：ach_UG, no_NO |
| `find_locales` | `(output_dir: Path) -> Tuple[str]` | 第144-162行 | 在output_dir/locale/下发现可用locale |

### 语言包创建

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `create_new_language_pack` | `(output_dir, locale, template_url, template_ref, version) -> None` | 第92-125行 | 使用copier从cookiecutter模板创建新语言包 |

### 源文件发现

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `find_packages_source_files` | `(packages_path) -> Dict[str, List[Path]]` | 第167-185行 | 遍历多个包目录，返回包名→源文件列表映射 |
| `find_source_files` | `(path, extensions, skip_folders) -> List[Path]` | 第188-220行 | 递归查找指定扩展名的源文件，跳过指定目录 |

### 字符串提取

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `extract_tsx_strings` | `(input_path) -> List[Dict]` | 第225-278行 | 使用gettext-extract从TS/TSX文件提取字符串 |
| `extract_schema_strings` | `(input_path) -> List[Dict]` | 第387-417行 | 从JSON Schema文件提取可翻译字符串 |
| `extract_strings` | `(input_paths, output_path, project, version) -> Path` | 第420-450行 | 调用pybabel extract从Python文件提取字符串 |
| `_extract_schema_strings` | `(schema, ref_path, prefix, to_translate) -> List[Dict]` | 第338-384行 | 递归遍历schema字典提取字符串（内部函数） |
| `_prepare_schema_patterns` | `(schema: dict) -> Dict[Pattern, str]` | 第322-335行 | 编译schema选择器正则表达式（内部函数） |

### POT/PO目录操作

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `fix_location` | `(path_to_remove, pot_path, append_entries) -> Dict[str, str]` | 第453-500行 | 修正POT文件中的绝对路径为相对路径，追加条目 |
| `remove_duplicates` | `(pot_path: Path, metadata: Dict[str, str]) -> None` | 第503-571行 | 按(msgctxt, msgid, msgid_plural)三元组去重POT条目 |
| `create_catalog` | `(repo_root_dir, locale_dir, project, version, merge) -> Tuple[Path, Dict]` | 第574-621行 | 创建POT目录：三路提取→合并→去重 |
| `update_catalogs` | `(pot_path, output_dir, locale) -> Path` | 第624-656行 | 调用pybabel init/update创建或更新PO文件 |
| `compile_catalog` | `(locale_dir, domain, locale) -> Path` | 第659-681行 | 调用pybabel compile编译PO文件 |
| `compile_to_mo` | `(po_path: Path) -> Path` | 第684-695行 | 使用polib将PO编译为MO二进制格式 |

### 高层API

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `extract_translations` | `(repo_root_dir, output_dir, project, merge) -> Path` | 第700-728行 | 提取翻译：get_version→create_catalog→remove_duplicates |
| `update_translations` | `(repo_root_dir, output_dir, project, locales) -> None` | 第731-762行 | 更新翻译：find_locales→create_catalog→update_catalogs→update_version |
| `compile_translations` | `(output_dir, project, locales) -> Dict[str, Path]` | 第765-786行 | 编译翻译：find_locales→compile_catalog per locale |
| `update_version` | `(po_path, project, version) -> Path` | 第789-798行 | 更新PO文件的Project-Id-Version元数据 |

### 辅助函数

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `get_line` | `(lines: List[str], value: str) -> str` | 第281-299行 | 查找字符串在源码行中的最后出现行号 |

## 默认跳过目录

find_source_files默认跳过的目录：`tests`, `test`, `node_modules`, `lib`, `.git`, `.ipynb_checkpoints`

## 默认源文件扩展名

find_source_files默认查找的扩展名：`.ts`, `.tsx`, `.py`

## 相关概念

- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [翻译目录管理](/concepts/05-catalog-management.md)
- [Schema国际化选择器](/concepts/09-schema-i18n-selectors.md)
- [格式转换源码映射](/references/converters-source.md)
