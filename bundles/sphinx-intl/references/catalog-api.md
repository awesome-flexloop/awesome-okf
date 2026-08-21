---
type: reference
title: "catalog.py PO/POT/MO 文件操作 API 参考"
description: "sphinx-intl 基于 Babel 的翻译目录文件读写封装的源码信源"
tags: [catalog, po, pot, mo, babel, api-reference]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: catalog-py
    resource: "sphinx_intl/catalog.py"
    title: "sphinx-intl catalog file operations module"
  - id: babel-pofile
    resource: "babel.messages.pofile"
    title: "Babel PO file read/write module"
  - id: babel-mofile
    resource: "babel.messages.mofile"
    title: "Babel MO file write module"
---

# catalog.py PO/POT/MO 文件操作 API 参考

本文件记录 `sphinx_intl/catalog.py` 中封装的翻译目录文件读写函数。底层基于 Babel 库的 `babel.messages.pofile` 和 `babel.messages.mofile` 模块。

## 文件读取

### load_po(filename, **kwargs)

读取 PO/POT 文件并返回 Babel Catalog 对象。

- **参数**:
  - `filename` (str): PO/POT 文件路径
  - `**kwargs`: 传递给 `babel.messages.pofile.read_po()` 的额外参数
- **返回**: `babel.support.Catalog` — Babel 翻译目录对象
- **实现细节**:
  1. 第一次以 binary mode 打开文件，调用 `pofile.read_po(f)` 读取以探测 charset
  2. 从 catalog 对象获取 charset，默认为 `utf-8`
  3. 第二次以 binary mode 打开文件，使用探测到的 charset 调用 `pofile.read_po(f, charset=charset, **kwargs)`
- **设计原因**: Babel 的 `read_po` 需要知道编码才能正确解码，而 PO 文件头部的 `Content-Type` 声明了 charset，因此需要两阶段读取

## 文件写入

### dump_po(filename, catalog, **kwargs)

将 Catalog 对象写入 PO 文件。

- **参数**:
  - `filename` (str): 输出 PO 文件路径
  - `catalog` (Catalog): Babel Catalog 对象
  - `**kwargs`: 传递给 `babel.messages.pofile.write_po()` 的参数
  - 特殊兼容参数: `line_width`（会被转换为 `width` 参数）
- **返回**: `None`
- **行为**:
  1. 自动创建目标目录（`os.makedirs(dirname, exist_ok=True)`）
  2. 兼容处理: 如果传入 `line_width` 参数，自动转换为 `width`
  3. 以 binary mode 打开文件，调用 `pofile.write_po(f, catalog, **kwargs)`

### write_mo(filename, catalog, **kwargs)

将 Catalog 对象写入 MO 文件（编译后的二进制翻译文件）。

- **参数**:
  - `filename` (str): 输出 MO 文件路径
  - `catalog` (Catalog): Babel Catalog 对象
  - `**kwargs`: 传递给 `babel.messages.mofile.write_mo()` 的参数
- **返回**: `None`
- **行为**:
  1. 自动创建目标目录
  2. 以 binary mode 打开文件，调用 `mofile.write_mo(f, catalog, **kwargs)`

## 条目过滤

### translated_entries(catalog) -> list

获取已翻译的消息条目列表。

- **过滤条件**: `m.id` 存在且 `m.string` 非空
- **返回**: 已翻译消息列表

### fuzzy_entries(catalog) -> list

获取模糊（fuzzy）标记的消息条目列表。

- **过滤条件**: `m.id` 存在且 `m.fuzzy` 为 True
- **返回**: 模糊标记消息列表

### untranslated_entries(catalog) -> list

获取未翻译的消息条目列表。

- **过滤条件**: `m.id` 存在且 `m.string` 为空
- **返回**: 未翻译消息列表

## 目录更新

### update_with_fuzzy(catalog, catalog_source)

用模板目录（POT）更新目标目录（PO），新消息标记为 fuzzy。

- **参数**:
  - `catalog` (Catalog): 要更新的 PO Catalog 对象（会被原地修改）
  - `catalog_source` (Catalog): 作为更新模板的 Catalog（通常是 POT）
- **返回**: `None`
- **实现**: 直接调用 `catalog.update(catalog_source)`
- **效果**:
  - POT 中新增的消息会被添加到 PO 中，标记为 fuzzy（待审校）
  - POT 中已删除的消息会被标记为 obsolete（`#~` 前缀）
  - 位置注释（`#:`）会被更新
  - 已翻译的消息保持翻译内容不变
