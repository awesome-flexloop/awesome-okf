---
type: example
title: "基本翻译全流程"
description: "从零开始为 Sphinx 文档添加多语言支持的完整实战教程，包含安装、配置、提取消息、翻译、编译和构建"
tags: [tutorial, workflow, gettext, translation, hands-on]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: commands-api
    resource: /references/commands-api.md
    title: "CLI 入口 API 参考"
  - id: basic-api
    resource: /references/basic-api.md
    title: "核心业务逻辑 API 参考"
  - id: official-docs
    resource: "https://sphinx-intl.readthedocs.io"
    title: "sphinx-intl 官方文档"
---

# 基本翻译全流程

本示例演示如何从零开始为一个 Sphinx 文档项目添加日语（ja）和简体中文（zh_CN）双语翻译支持。

## 前置条件

- Python 3.9+
- 一个已有的 Sphinx 文档项目（如果没有，先用 `sphinx-quickstart` 创建）

## 步骤 1：安装 sphinx-intl

```bash
pip install sphinx-intl
```

验证安装：

```bash
sphinx-intl --version
sphinx-intl --help
```

## 步骤 2：配置 conf.py

在 Sphinx 项目的 `conf.py`（通常在 `source/conf.py` 或项目根目录）中添加/确认以下配置：

```python
# 国际化配置
locale_dirs = ['locale/']   # 翻译文件存放目录
gettext_compact = False     # 每个文档生成独立 POT 文件
language = 'en'             # 默认语言（源语言）
```

## 步骤 3：提取可翻译消息（生成 POT）

使用 Sphinx 的 gettext 构建器提取文档中的可翻译字符串：

```bash
# 如果使用 Makefile（sphinx-quickstart 生成的）
make gettext

# 或者直接调用 sphinx-build
sphinx-build -b gettext source _build/gettext
```

执行后，检查 `_build/gettext/` 目录下是否生成了 `.pot` 文件：

```bash
ls _build/gettext/
# 应该看到: index.pot, install.pot, usage.pot ...
```

每个 `.rst` 源文件对应一个 `.pot` 文件。如果 `gettext_compact = False`，还会有子目录结构。

## 步骤 4：初始化 PO 文件

使用 sphinx-intl 创建日语和简体中文的 PO 文件：

```bash
sphinx-intl update -p _build/gettext -l ja -l zh_CN
```

预期输出类似：

```
Create: locale/ja/LC_MESSAGES/index.po
Create: locale/ja/LC_MESSAGES/install.po
Create: locale/zh_CN/LC_MESSAGES/index.po
Create: locale/zh_CN/LC_MESSAGES/install.po
...
```

检查生成的目录结构：

```
locale/
├── ja/
│   └── LC_MESSAGES/
│       ├── index.po
│       └── ...
└── zh_CN/
    └── LC_MESSAGES/
        ├── index.po
        └── ...
```

## 步骤 5：翻译 PO 文件

### 方式 A：使用文本编辑器

直接打开 `.po` 文件进行翻译。以 `locale/ja/LC_MESSAGES/index.po` 为例：

```po
# Japanese translations for sphinx-intl-test documentation
# Copyright (C) 2026, see LICENSE
# This file is distributed under the same license as the sphinx-intl-test package.
#
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"Language: ja\n"

#: ../../source/index.rst:3
msgid "Welcome to the Project Documentation"
msgstr "プロジェクトドキュメントへようこそ"

#: ../../source/index.rst:7
msgid "This is the main documentation page."
msgstr "これはメインドキュメントページです。"
```

每个翻译条目包含：
- `#:` 注释：来源文件和行号
- `msgid`：原始英文字符串
- `msgstr`：你的翻译（初始为空，需要填入）

### 方式 B：使用 PO 编辑器

推荐使用专用 PO 编辑器提升效率：
- [Poedit](https://poedit.net/)（跨平台，免费版可用）
- [Lokalize](https://kde.org/applications/en/office/org.kde.lokalize)（Linux/KDE）
- [Virtaal](https://virtaal.translatehouse.org/)（跨平台）

这些工具提供翻译记忆、术语表、自动补全等功能。

## 步骤 6：编译 MO 文件

翻译完成后，编译 PO 文件为 MO 二进制文件：

```bash
sphinx-intl build
```

预期输出：

```
Build: locale/ja/LC_MESSAGES/index.mo
Build: locale/ja/LC_MESSAGES/install.mo
Build: locale/zh_CN/LC_MESSAGES/index.mo
Build: locale/zh_CN/LC_MESSAGES/install.mo
...
```

检查 `.mo` 文件是否生成：

```bash
ls locale/ja/LC_MESSAGES/*.mo
```

## 步骤 7：构建翻译后的文档

### 构建日语版 HTML

```bash
# Linux/macOS
make -e SPHINXOPTS="-Dlanguage='ja'" html

# Windows PowerShell
$env:SPHINXOPTS="-Dlanguage=ja"
make html

# 或者直接用 sphinx-build
sphinx-build -b html -D language=ja source _build/html/ja
```

### 构建简体中文版 HTML

```bash
make -e SPHINXOPTS="-Dlanguage='zh_CN'" html
```

构建完成后，在 `_build/html/`（或 `_build/html/ja`）中查看翻译后的文档。

## 步骤 8：查看翻译进度

在翻译过程中，随时查看进度：

```bash
# 查看所有语言的统计
sphinx-intl stat

# 只查看日语
sphinx-intl stat -l ja
```

输出示例：

```
locale/ja/LC_MESSAGES/index.po: 15 translated, 2 fuzzy, 3 untranslated.
locale/ja/LC_MESSAGES/install.po: 8 translated, 0 fuzzy, 4 untranslated.
```

## 日常更新流程

当文档源文件更新后，需要同步更新翻译文件：

```bash
# 1. 重新提取消息（POT 更新）
make gettext

# 2. 更新 PO 文件（合并新消息）
sphinx-intl update -p _build/gettext -l ja -l zh_CN

# 3. 翻译新增/变更的消息（fuzzy 标记的条目）
#    用编辑器打开 PO 文件，处理 fuzzy 条目

# 4. 重新编译
sphinx-intl build

# 5. 重新构建文档
make -e SPHINXOPTS="-Dlanguage='ja'" html
```

## 使用环境变量简化命令

如果不想每次都输入参数，可以设置环境变量：

```bash
# Bash/Zsh
export SPHINXINTL_LANGUAGE=ja,zh_CN
export SPHINXINTL_POT_DIR=_build/gettext

sphinx-intl update  # 不需要 -p 和 -l 参数了
sphinx-intl stat
sphinx-intl build
```

```powershell
# PowerShell
$env:SPHINXINTL_LANGUAGE = "ja,zh_CN"
$env:SPHINXINTL_POT_DIR = "_build/gettext"
```

## 多语言 Makefile 集成

可以在项目的 Makefile 中添加便捷目标：

```makefile
# 在 Makefile 末尾添加
translations:
    sphinx-intl update -p _build/gettext -l ja -l zh_CN

html-ja:
    $(SPHINXBUILD) -b html -D language=ja $(ALLSPHINXOPTS) $(BUILDDIR)/html/ja

html-zh:
    $(SPHINXBUILD) -b html -D language=zh_CN $(ALLSPHINXOPTS) $(BUILDDIR)/html/zh_CN

html-all: html html-ja html-zh
```

然后使用：

```bash
make translations  # 更新翻译文件
make html-ja       # 构建日语版
make html-all      # 构建所有语言版本
```

## 常见问题

### Q: 翻译后构建文档仍然显示英文？

检查以下几点：
1. MO 文件是否已生成（`sphinx-intl build`）
2. `language` 参数是否正确（是 `ja` 不是 `jp`，是 `zh_CN` 不是 `cn`）
3. `locale_dirs` 配置路径是否正确（相对于 conf.py 的位置）
4. MO 文件路径是否符合 `locale/<lang>/LC_MESSAGES/<domain>.mo` 格式

### Q: update 后出现很多 `#, fuzzy` 标记？

这是正常的。当源文本发生变化时，Babel 会将可能的旧翻译标记为 fuzzy，提醒你重新审校。翻译完成后需要手动删除 `#, fuzzy` 行，Sphinx 才会使用该翻译。

### Q: 如何一次只翻译一个文件？

PO 文件就是按文档拆分的（因为设置了 `gettext_compact = False`），你可以只翻译 `index.po` 而暂不翻译其他文件。未翻译的部分会显示原始英文。

## 相关概念

- [5分钟快速上手](../concepts/01-getting-started.md)
- [翻译工作流原理](../concepts/03-translation-workflow.md)
- [CLI 命令体系详解](../concepts/02-cli-commands.md)
- [Transifex 协作翻译示例](transifex-collaboration.md)
