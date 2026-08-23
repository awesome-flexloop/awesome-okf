---
type: Concept
title: 翻译目录管理
description: jupyterlab-translate的POT/PO/MO/JSON翻译文件生命周期管理，包括创建、更新、编译和目录结构约定
tags: [catalog, pot, po, mo, locale, LC_MESSAGES, pybabel, directory-structure]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: utils-source
    resource: /references/utils-source.md
    title: 核心工具源码映射
---

# 翻译目录管理

jupyterlab-translate 围绕gettext标准的翻译目录结构进行管理。本节介绍POT、PO、MO、JSON四种文件的角色、目录结构约定，以及创建、更新、编译三个核心操作。

## 文件类型概览

gettext国际化涉及四种关键文件类型：

| 文件类型 | 扩展名 | 角色 | 生成时机 |
|---------|--------|------|---------|
| 模板文件 | `.pot` (Portable Object Template) | 包含所有待翻译字符串，不含翻译 | extract命令 |
| 翻译文件 | `.po` (Portable Object) | 包含原文和翻译的文本文件 | update命令 |
| 二进制文件 | `.mo` (Machine Object) | PO编译后的二进制，供Python后端加载 | compile命令 |
| JSON文件 | `.json` (Jed format) | PO转换的JSON格式，供JupyterLab前端加载 | compile命令 |

## 目录结构约定

### 独立扩展包模式

```
<extension-dir>/
└── <project>/                    # normalize后的项目名（小写、_替代-）
    └── locale/                   # LOCALE_FOLDER = "locale"
        ├── <project>.pot         # POT模板
        ├── <locale>/             # 如 zh_CN, es_ES, ko_KR
        │   └── LC_MESSAGES/      # gettext标准目录名
        │       ├── <project>.po  # 翻译源文件
        │       ├── <project>.mo  # 编译后二进制
        │       └── <project>.json# Jed JSON格式（前端用）
        └── <locale>/
            └── LC_MESSAGES/
                └── ...
```

### 集中语言包模式

```
<language-packs-repo>/
├── jupyterlab/                   # 核心翻译
│   └── locale/
│       ├── jupyterlab.pot
│       └── <locale>/LC_MESSAGES/
├── extensions/                   # 扩展翻译（extract时）
│   └── <project>/locale/
├── jupyterlab_extensions/        # 扩展翻译（update时）
│   └── <project>/locale/
└── language-packs/               # LANG_PACKS_FOLDER
    └── jupyterlab-language-pack-<locale-dash>/
        └── jupyterlab_language_pack_<locale>/
            └── locale/<locale>/LC_MESSAGES/
                ├── jupyterlab.mo
                ├── jupyterlab.json
                ├── <ext>.mo
                └── <ext>.json
```

## 操作一：创建POT模板（extract）

POT（Portable Object Template）文件是翻译工作的起点，包含从源码中提取的所有可翻译字符串。

### 核心函数

```python
extract_translations(repo_root_dir, output_dir, project, merge=True)
```

### 执行流程

1. **获取版本号** (`get_version`)：按优先级尝试 setup.py/hatch → package.json → git describe
2. **创建locale目录**：`output_dir / "locale"`, parents=True
3. **创建catalog** (`create_catalog`)：
   - 调用 `find_packages_source_files()` 发现源文件
   - 调用 `extract_strings()` 通过pybabel提取Python字符串
   - 调用 `extract_tsx_strings()` 通过gettext-extract提取TS/TSX字符串
   - 调用 `extract_schema_strings()` 提取JSON Schema字符串
   - 调用 `fix_location()` 修正文件路径
   - 如果merge=True，使用xgettext与已有POT合并
4. **去重** (`remove_duplicates`)：按(msgctxt, msgid, msgid_plural)三元组合并重复条目

### POT文件示例

```pot
#: /src/widget.ts:42
msgid "Hello World"
msgstr ""

#: /src/widget.ts:55
msgid "One file"
msgid_plural "{count} files"
msgstr[0] ""
msgstr[1] ""

#: /schema/plugin.json:/title
msgctxt "schema"
msgid "My Extension"
msgstr ""
```

## 操作二：创建/更新PO文件（update）

PO文件是翻译人员实际编辑的文件，包含原文和对应的翻译。

### 核心函数

```python
update_translations(repo_root_dir, output_dir, project, locales=None)
```

### 执行流程

1. **发现locales**：如果未指定locales参数，在locale/目录下自动发现已有的语言目录
2. **重新提取POT**：确保模板是最新的
3. **对每个locale执行**：
   - 调用 `update_catalogs()`：
     - 如果PO文件不存在 → `pybabel init` 创建新文件
     - 如果PO文件已存在 → `pybabel update` 合并新字符串
   - 调用 `update_version()` 更新PO文件头中的Project-Id-Version

### pybabel命令

**init（创建新PO）：**
```bash
pybabel init --domain=<project> \
    --input-file=<pot_path> \
    --output-dir=<locale_dir> \
    --locale=<locale>
```

**update（更新已有PO）：**
```bash
pybabel update --domain=<project> \
    --input-file=<pot_path> \
    --output-dir=<locale_dir> \
    --locale=<locale>
```

### PO文件示例

```po
msgid ""
msgstr ""
"Project-Id-Version: my_extension 1.0.0\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"Language: zh_CN\n"

#: /src/widget.ts:42
msgid "Hello World"
msgstr "你好，世界"

#: /src/widget.ts:55
msgid "One file"
msgid_plural "{count} files"
msgstr[0] "一个文件"
msgstr[1] "{count}个文件"
```

## 操作三：编译翻译文件（compile）

编译将PO文件转换为两种运行时格式：MO（后端）和JSON（前端）。

### 核心函数

```python
compile_translations(output_dir, project, locales=None) -> Dict[str, Path]
```

### MO编译

MO文件通过两种方式生成：
- `pybabel compile`（compile_catalog函数调用）
- `polib.POFile.save_as_mofile()`（compile_to_mo函数使用）

MO是gettext标准二进制格式，加载速度快，被Python的gettext模块直接读取。

**pybabel compile命令：**
```bash
pybabel compile --domain=<project> \
    --dir=<locale_dir> \
    --locale=<locale>
```

### JSON编译

JSON文件通过 `convert_catalog_to_json()` 生成，使用Jed格式。详见[Jed JSON翻译格式](/concepts/06-json-jed-format.md)。

### 编译产物

编译后，LC_MESSAGES目录包含三种文件：
- `.po` — 翻译源文件（保留，供翻译人员编辑）
- `.mo` — 二进制编译产物（Python后端加载）
- `.json` — Jed JSON产物（JupyterLab前端加载）

## Locale验证

所有locale代码通过 `check_locale()` 函数验证，底层使用 `babel.Locale.parse()`。支持的locale格式遵循[CLDR](https://cldr.unicode.org/)标准，如：

- 双字母语言：`zh_CN`, `en_US`, `es_ES`, `fr_FR`, `de_DE`, `ko_KR`, `ja_JP`
- 三字母语言特例：`ach_UG`（Acholi/乌干达）、`no_NO`（挪威语）在白名单中

## 版本获取策略

`get_version()` 函数按以下优先级获取项目版本：

1. **Python包版本**：如果存在setup.py，运行 `python setup.py --version`；否则运行 `python -m hatch version`
2. **NPM包版本**：如果Python方式失败，读取 `<project>/package.json` 中的version字段
3. **Git标签版本**：如果以上都失败，运行 `git describe --tags --abbrev=0`（去掉前缀v）

## 相关概念

- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [Jed JSON翻译格式](/concepts/06-json-jed-format.md)
- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
- [快速开始](/concepts/01-getting-started.md)
- [核心工具源码映射](/references/utils-source.md)
