---
type: concept
title: "5分钟快速上手"
description: "sphinx-intl 安装、配置、基本翻译工作流——从安装到生成多语言文档的完整步骤"
tags: [getting-started, installation, quickstart, tutorial]
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

# 5分钟快速上手

本教程演示如何使用 sphinx-intl 为 Sphinx 文档添加多语言翻译支持。

## 安装

### 使用 pip 安装

推荐在虚拟环境中安装 [F-012]：

```bash
pip install sphinx-intl
```

安装后即可使用 `sphinx-intl` 命令：

```bash
sphinx-intl --help
```

### 可选：安装 Transifex CLI

如果需要使用 Transifex 云端协作翻译功能，需额外安装 [Transifex CLI](https://github.com/transifex/cli) [F-013]：

```bash
curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash
```

sphinx-intl 要求 Transifex CLI 版本 ≥ 1.2.1。

## 完整翻译流程

以下是将 Sphinx 文档翻译为日语（ja）和德语（de）的完整步骤。

### 步骤 1：准备 Sphinx 文档

确保已有一个可用的 Sphinx 文档项目。如果没有，可以使用 `sphinx-quickstart` 创建：

```bash
sphinx-quickstart docs
cd docs
```

### 步骤 2：配置 conf.py

在 Sphinx 的 `conf.py` 中添加以下配置 [F-014]：

```python
# 翻译文件存放目录
locale_dirs = ['locale/']   # 推荐路径

# 可选：禁用 gettext 紧凑模式，使每个文档生成独立的 POT 文件
gettext_compact = False
```

- `locale_dirs`：告诉 Sphinx 和 sphinx-intl 在哪里查找/生成翻译文件
- `gettext_compact = False`：让 Sphinx 为每个文档生成独立的 POT 文件（而不是合并为一个大文件），便于管理

### 步骤 3：提取可翻译消息（生成 POT）

使用 Sphinx 的 gettext 构建器从文档中提取可翻译字符串：

```bash
make gettext
```

这会在 `_build/gettext/` 目录下生成 `.pot` 文件（POT = Portable Object Template）。每个 `.rst` 源文件对应一个 `.pot` 文件。

也可以修改 Makefile 将 POT 输出到 `locale/pot/` 目录，这样更方便管理 [F-015]。

### 步骤 4：创建/更新 PO 文件

使用 sphinx-intl 从 POT 文件创建指定语言的 PO 文件 [F-016]：

```bash
sphinx-intl update -p _build/gettext -l de -l ja
```

参数说明：
- `-p _build/gettext`：指定 POT 文件所在目录
- `-l de -l ja`：指定目标语言（可以多次使用 `-l`，也可以用逗号分隔：`-l de,ja`）

执行后会生成以下目录结构：

```
locale/
├── de/
│   └── LC_MESSAGES/
│       ├── index.po
│       ├── install.po
│       └── ...
└── ja/
    └── LC_MESSAGES/
        ├── index.po
        ├── install.po
        └── ...
```

每个 `.po` 文件对应一个 `.pot` 模板，包含待翻译的字符串。

**当源文档更新后**，重新执行 `make gettext` 和 `sphinx-intl update` 即可——sphinx-intl 会智能合并新消息（新消息标记为 fuzzy，已翻译的内容保持不变，已删除的消息标记为 obsolete）。

### 步骤 5：翻译 PO 文件

使用任意 PO 文件编辑器（如 [Poedit](https://poedit.net/)、[Lokalize](https://kde.org/applications/en/office/org.kde.lokalize)）或直接用文本编辑器打开 `.po` 文件进行翻译。

PO 文件格式示例：

```po
#: ../../index.rst:7
msgid "Welcome to Sphinx"
msgstr "Sphinx へようこそ"
```

- `msgid`：原始字符串（英文）
- `msgstr`：翻译后的字符串
- `#, fuzzy`：标记表示翻译需要审校（通常是自动合并的新消息）

### 步骤 6：编译 MO 文件

翻译完成后，使用 sphinx-intl 将 PO 编译为 MO（二进制格式，Sphinx 运行时加载）：

```bash
sphinx-intl build
```

这会在 `locale/<lang>/LC_MESSAGES/` 下生成对应的 `.mo` 文件。sphinx-intl 会自动跳过已经是最新的 MO 文件（通过 mtime 判断增量编译）。

也可以让 Sphinx 自动编译——Sphinx 在构建多语言文档时如果发现 `.mo` 文件缺失会自动编译。

### 步骤 7：构建翻译后的文档

使用 `-D language=<lang>` 选项构建指定语言的文档：

**Linux/macOS**:
```bash
make -e SPHINXOPTS="-Dlanguage='ja'" html
```

**Windows (cmd)**:
```cmd
set SPHINXOPTS=-Dlanguage=ja
make html
```

**Windows (PowerShell)**:
```powershell
$env:SPHINXOPTS="-Dlanguage=ja"
make html
```

生成的翻译文档在 `_build/html/` 中。

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `sphinx-intl update -p <pot_dir> -l <lang>` | 从 POT 创建/更新 PO 文件 |
| `sphinx-intl build` | 编译 PO 为 MO |
| `sphinx-intl stat` | 查看翻译进度统计 |
| `sphinx-intl --help` | 查看帮助信息 |

## 常用选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `-d, --locale-dir` | 指定 locale 目录（默认 `locales`） | `-d locale` |
| `-p, --pot-dir` | 指定 POT 目录 | `-p _build/gettext` |
| `-l, --language` | 目标语言 | `-l ja -l de` |
| `-w, --line-width` | PO 文件行宽（默认 76，≤0 禁用换行） | `-w 0` |
| `-j, --jobs` | 并行 CPU 数（0=全部） | `-j 4` |
| `--no-obsolete` | 移除过时消息 | `--no-obsolete` |

## 环境变量

所有 CLI 选项都可以通过 `SPHINXINTL_` 前缀的环境变量设置 [F-017]：

```bash
# 等同于 sphinx-intl update -l de -l ja
export SPHINXINTL_LANGUAGE=de,ja
sphinx-intl update -p _build/gettext
```

## 相关概念

- [sphinx-intl 简介](00-introduction.md)
- [CLI 命令体系详解](02-cli-commands.md)
- [翻译工作流原理](03-translation-workflow.md)
- [基本翻译全流程示例](../examples/basic-translation.md)
