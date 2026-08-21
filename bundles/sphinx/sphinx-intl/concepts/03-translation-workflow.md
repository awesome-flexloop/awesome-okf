---
type: concept
title: "翻译工作流原理"
description: "POT→PO→MO 三阶段翻译文件生命周期、gettext 目录结构规范、LC_MESSAGES 约定"
tags: [workflow, pot, po, mo, gettext, lifecycle]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: basic-api
    resource: /references/basic-api.md
    title: "basic.py 核心业务逻辑 API 参考"
  - id: catalog-api
    resource: /references/catalog-api.md
    title: "catalog.py PO/POT/MO 文件操作 API 参考"
---

# 翻译工作流原理

sphinx-intl 管理的翻译工作流遵循 GNU gettext 标准，涉及三种文件类型和两个核心转换操作。理解这些概念是掌握 sphinx-intl 的基础。

## gettext 三文件类型

### POT（Portable Object Template）— 翻译模板

POT 文件是翻译的模板，由 Sphinx 的 gettext 构建器从文档源文件提取生成。

- **扩展名**：`.pot`
- **内容**：包含所有可翻译的原始字符串（msgid），但翻译字符串（msgstr）为空
- **生成者**：Sphinx（`sphinx-build -b gettext` 或 `make gettext`）
- **位置**：`_build/gettext/`（Sphinx 默认输出）或 `locale/pot/`
- **特点**：每次文档更新都应该重新生成 POT

示例 POT 文件内容：

```po
#: ../../index.rst:7
msgid "Welcome to the project documentation"
msgstr ""

#: ../../install.rst:12
msgid "Installation Guide"
msgstr ""
```

### PO（Portable Object）— 翻译文件

PO 文件是面向翻译人员的可编辑文本文件，从 POT 复制/更新而来。

- **扩展名**：`.po`
- **内容**：msgid（原始字符串）+ msgstr（翻译字符串）
- **位置**：`locale/<lang>/LC_MESSAGES/<domain>.po`
- **特点**：人工编辑，包含翻译进度元数据

示例 PO 文件内容：

```po
#: ../../index.rst:7
msgid "Welcome to the project documentation"
msgstr "プロジェクトドキュメントへようこそ"

#: ../../install.rst:12
#, fuzzy
msgid "Installation Guide"
msgstr "インストールガイド（要確認）"
```

### MO（Machine Object）— 编译后的二进制文件

MO 文件是 PO 文件编译后的二进制格式，供程序运行时快速加载。

- **扩展名**：`.mo`
- **内容**：PO 文件的二进制索引格式，优化查找速度
- **位置**：与 PO 文件同目录（`locale/<lang>/LC_MESSAGES/<domain>.mo`）
- **使用者**：Sphinx 构建时加载 MO 文件实现文档翻译
- **特点**：不可手动编辑，由 sphinx-intl build 自动编译

## 目录结构规范

sphinx-intl 遵循 gettext 的标准目录布局——`LC_MESSAGES` 约定 [F-030]：

```
locale/                          # locale_dir（由 locale_dirs 配置指定）
├── pot/                         # POT 目录（可选，推荐位置）
│   ├── index.pot
│   ├── install.pot
│   └── ...
├── <lang_code>/                 # 语言目录（如 ja, de, zh_CN, en_US）
│   └── LC_MESSAGES/             # gettext 标准目录名（固定）
│       ├── index.po             # 对应 index.pot 的翻译文件
│       ├── index.mo             # 编译后的二进制文件
│       ├── install.po
│       ├── install.mo
│       └── ...
└── <lang_code>/
    └── LC_MESSAGES/
        └── ...
```

### 为什么是 LC_MESSAGES？

`LC_MESSAGES` 是 gettext 规范中的固定目录名。gettext 除了消息翻译（LC_MESSAGES）外，还定义了 LC_CTYPE（字符分类）、LC_TIME（日期时间格式）、LC_NUMERIC（数字格式）等多个本地化分类目录。Sphinx 文档翻译只使用消息分类，因此所有 PO/MO 文件都放在 `LC_MESSAGES` 目录下。

### 语言代码

语言目使用标准的语言代码：
- 两字母代码：`ja`（日语）、`de`（德语）、`fr`（法语）、`zh`（中文）
- 带地区代码：`zh_CN`（简体中文）、`zh_TW`（繁体中文）、`pt_BR`（巴西葡萄牙语）

语言代码必须与 Sphinx 的 `language` 配置值对应，如 `language = 'ja'` 对应 `locale/ja/` 目录。

## 核心转换流程

### 转换 1：POT → PO（sphinx-intl update）

`sphinx-intl update` 命令执行 POT 到 PO 的转换/更新，这是翻译文件的生命周期起点。

**新文件创建**：
1. 加载 POT 文件（`c.load_po(pot_file)`）
2. 设置 catalog 的 locale 属性为目标语言
3. 写入新的 PO 文件（`c.dump_po(po_file, cat_pot, ...)`）

**已有文件更新**：
1. 加载现有 PO 文件（`c.load_po(po_file)`）
2. 加载 POT 模板（`c.load_po(pot_file)`）
3. 记录更新前的 msgid 集合
4. 调用 `c.update_with_fuzzy(cat, cat_pot)` 合并新消息
5. 比较更新前后的 msgid 变化
6. 如果有变化则写入 PO 文件

**合并行为**（Babel 的 catalog.update）：
- **新增消息**：从 POT 添加到 PO，标记为 `fuzzy`（需人工确认）
- **已删除消息**：在 PO 中标记为 obsolete（`#~` 前缀），不立即删除
- **位置变更**：更新 `#:` 行号注释
- **已翻译消息**：保留翻译内容不变

**关键选项**：
- `--no-obsolete`：更新时直接删除 obsolete 消息（不保留 `#~` 记录）
- `-w/--line-width`：PO 文件行宽（默认76字符），设置为 ≤0 禁用换行
- `-j/--jobs`：多进程并行处理多个文件

### 转换 2：PO → MO（sphinx-intl build）

`sphinx-intl build` 命令将已翻译的 PO 文件编译为 MO 二进制文件。

**编译流程**：
1. 遍历语言目录下所有 `.po` 文件
2. 检查 MO 文件是否已存在且比 PO 文件新（mtime 比较，增量编译）
3. 如果需要编译：加载 PO（`c.load_po(po_file)`）→ 写入 MO（`c.write_mo(mo_file, cat)`）

**为什么需要 MO 文件？**

MO 是二进制格式，使用哈希表索引，查找速度远快于解析文本格式的 PO 文件。Sphinx 运行时加载 MO 文件来获取翻译字符串，而不是直接解析 PO 文件。

**增量编译**：

sphinx-intl 会比较 MO 和 PO 文件的修改时间（mtime），如果 MO 文件比 PO 文件新则跳过编译，避免不必要的重复工作 [F-031]。

### 统计：sphinx-intl stat

`stat` 命令提供翻译进度的快速概览，通过三个过滤函数统计 [F-032]：

| 统计项 | 过滤函数 | 含义 |
|--------|---------|------|
| translated | `translated_entries()` | 已有翻译的消息（m.id 存在且 m.string 非空）|
| fuzzy | `fuzzy_entries()` | 模糊标记的消息（m.id 存在且 m.fuzzy 为 True）|
| untranslated | `untranslated_entries()` | 未翻译的消息（m.id 存在且 m.string 为空）|

## 文件路径映射规则

sphinx-intl 在 update 时按照以下规则从 POT 路径推导出 PO 路径：

```
POT: <pot_dir>/<relative_path>/<name>.pot
  ↓
PO:  <locale_dir>/<lang>/LC_MESSAGES/<relative_path>/<name>.po
```

关键实现代码（basic.py 中的 update 函数）：

```python
for dirpath, dirnames, filenames in os.walk(pot_dir):
    for filename in filenames:
        pot_file = os.path.join(dirpath, filename)
        base, ext = os.path.splitext(pot_file)
        if ext != ".pot":
            continue
        basename = relpath(base, pot_dir)
        for lang in languages:
            po_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
            po_file = os.path.join(po_dir, basename + ".po")
```

这意味着 POT 文件的**子目录结构会被完整保留**到 PO/MO 目录中。

## 完整生命周期示例

以下是一个文档文件从源文件到翻译输出的完整生命周期：

```
1. docs/index.rst                    ← 作者编写英文源文档
        ↓ sphinx-build -b gettext
2. _build/gettext/index.pot         ← Sphinx 提取可翻译消息
        ↓ sphinx-intl update -l ja
3. locale/ja/LC_MESSAGES/index.po   ← 生成日语 PO 文件（空翻译）
        ↓ 翻译人员编辑
4. locale/ja/LC_MESSAGES/index.po   ← 填入日语翻译
        ↓ sphinx-intl build
5. locale/ja/LC_MESSAGES/index.mo   ← 编译为 MO 二进制
        ↓ sphinx-build -D language=ja
6. _build/html/index.html           ↓ Sphinx 加载 MO，生成日语 HTML
```

**文档更新后的迭代**：

```
1. docs/index.rst 修改了内容
        ↓ sphinx-build -b gettext（重新提取）
2. _build/gettext/index.pot（包含新消息）
        ↓ sphinx-intl update -l ja（合并更新）
3. locale/ja/LC_MESSAGES/index.po
   - 已有翻译：保留
   - 新增消息：标记为 fuzzy，待翻译
   - 删除消息：标记为 obsolete
        ↓ 翻译人员处理 fuzzy 消息
4. 继续 build → html
```

## 相关概念

- [CLI 命令体系详解](02-cli-commands.md)
- [目录文件操作：Catalog 模块](04-catalog-operations.md)
- [更新机制：多进程合并与 Fuzzy](05-update-mechanism.md)
- [编译与统计机制](06-build-stat-mechanism.md)
