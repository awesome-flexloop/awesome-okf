---
type: Concept
title: "Gettext 国际化基础"
description: "JupyterLab 使用 GNU gettext 标准进行国际化——POT模板、PO翻译、MO二进制编译的工作原理"
tags: [jupyterlab, i18n, gettext, pot, po, mo, internationalization]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: gettext-format, resource: /references/gettext-format-source.md, title: "Gettext 翻译格式信源" }
  - { id: package-structure, resource: /references/package-structure-source.md, title: "语言包结构信源" }
---

# Gettext 国际化基础

JupyterLab 的国际化（i18n）基于 [GNU gettext](https://www.gnu.org/software/gettext/) 行业标准，这是最广泛使用的开源国际化框架。理解 gettext 的三种文件格式（POT/PO/MO）和工作流程是理解 language-packs 项目的基础。

## Gettext 工作流程

```
源码中标记可翻译字符串 _("Hello")
    ↓
xgettext/jupyterlab-translate 提取
    ↓
POT 模板文件（只有英文源字符串）
    ↓
msginit/复制为各语言 PO 文件
    ↓
译者翻译 PO 文件（msgid → msgstr）
    ↓
msgfmt/jupyterlab-translate 编译
    ↓
MO 二进制文件 + JSON 文件
    ↓
运行时 gettext 加载 MO，替换界面字符串
```

## 三种核心文件格式

### POT（Portable Object Template）

POT 是**翻译模板**文件，包含从源码中提取的所有可翻译字符串，但没有翻译（msgstr 为空）。

```gettext
#: /packages/markdownviewer-extension/schema/plugin.json:/description
msgctxt "schema"
msgid "Markdown viewer settings."
msgstr ""
```

特点：
- 文件扩展名：`.pot`
- `msgstr` 始终为空字符串
- 是生成各语言 PO 文件的模板
- 当源码字符串变化时重新生成
- 存放在 `jupyterlab/locale/` 和 `extensions/*/locale/` 目录

### PO（Portable Object）

PO 是**翻译文件**，在 POT 基础上由译者填写 msgstr 翻译。

```gettext
#: /packages/markdownviewer-extension/schema/plugin.json:/description
msgctxt "schema"
msgid "Markdown viewer settings."
msgstr "Markdown 查看器设置。"
```

特点：
- 文件扩展名：`.po`
- 每个语言每个 domain 一个 PO 文件
- 可读的文本格式，译者可直接编辑
- 包含 Crowdin 元数据头（X-Crowdin-* 字段）
- 纳入 Git 版本控制
- 存放在 `language-packs/*/locale/{locale}/LC_MESSAGES/` 目录

### MO（Machine Object）

MO 是**编译后的二进制文件**，由 PO 文件编译而来，运行时快速加载。

特点：
- 文件扩展名：`.mo`
- 二进制格式，不可直接阅读
- 优化了查找性能（哈希表索引）
- 构建时生成（`jupyterlab-translate` build hook）
- 不纳入 Git（.gitignore 排除）
- 打包在 wheel 中，运行时使用

### JSON 翻译文件

除了标准 MO 文件，JupyterLab 还生成 JSON 格式翻译文件，用于前端 JavaScript 代码的国际化（gettext 原生用于 C/Python，前端需要 JSON 格式）。

## PO/POT 文件结构详解

### 头部元数据

每个 PO/POT 文件以空 msgid/msgstr 作为头部：

```gettext
msgid ""
msgstr ""
"Project-Id-Version: jupyterlab 4.6.1\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Language: zh_CN\n"
"Language-Team: Chinese Simplified\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"PO-Revision-Date: 2026-05-04 02:41\n"
```

PO 文件特有的 Crowdin 元数据：

```gettext
"X-Crowdin-Project: jupyterlab\n"
"X-Crowdin-Project-ID: 409874\n"
"X-Crowdin-Language: zh-CN\n"
"X-Crowdin-File: /main/jupyterlab/locale/jupyterlab.pot\n"
"X-Crowdin-File-ID: 191\n"
```

### 翻译条目

每个翻译条目由三部分组成：

1. **源文件引用**（`#:` 行）：字符串在源码中的位置
2. **上下文**（`msgctxt`，可选）：用于消歧，同一字符串在不同语境下有不同翻译
3. **消息 ID**（`msgid`）：英文源字符串
4. **消息字符串**（`msgstr`）：翻译后的字符串

```gettext
#: /packages/markdownviewer-extension/schema/plugin.json:/properties/fontFamily/title
msgctxt "settings"
msgid "Font Family"
msgstr "字体集"
```

### 多行字符串

长字符串用多个双引号拼接，每行末尾用 `\n` 表示换行：

```gettext
msgid ""
"The font family used to render markdown.\n"
"If `null`, value from current theme is used."
msgstr "用于渲染 Markdown 的字体集。\n"
"如果值为 `null`，则沿用当前主题的值。"
```

### 上下文消歧（msgctxt）

JupyterLab 中常见的 msgctxt 类型：

| msgctxt | 用途 | 示例 |
|---------|------|------|
| `schema` | JSON Schema 中的 description 字段 | 设置项的描述文本 |
| `settings` | 设置界面的标题/标签 | 如 "Font Family" |
| `menu` | 菜单项 | 文件/编辑/视图等菜单 |
| `command` | 命令面板中的命令名 | "Save Notebook" |
| （无） | 通用 UI 字符串 | 按钮文本、对话框提示 |

### 复数形式

不同语言有不同的复数规则，通过 `Plural-Forms` 头声明：

- **中文**：`nplurals=1; plural=0;`（无复数变化，所有数量用同一形式）
- **英语**：`nplurals=2; plural=(n != 1);`（1个用单数，其他用复数）
- **俄语**：`nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);`（3种复数形式）

中文不需要处理复数，所以 PO 文件中所有翻译都是单数形式。

## 目录布局约定

Gettext 标准的 `LC_MESSAGES` 目录结构：

```
locale/
└── {lang}_{REGION}/          # 语言目录（如 zh_CN、fr_FR）
    └── LC_MESSAGES/          # gettext 标准消息目录
        ├── jupyterlab.po     # JupyterLab核心翻译
        ├── notebook.po       # Notebook扩展翻译
        ├── jupyterlab_git.po # Git扩展翻译
        └── ...（其他扩展）
```

- `{lang}_{REGION}`：ISO 639-1 语言码（小写）+ ISO 3166-1 国家码（大写），下划线连接
- `LC_MESSAGES`：gettext 固定目录名，所有翻译文件必须放在此目录
- domain：文件名（不含扩展名）对应"域"，通常与包名一致

## Domain 概念

每个扩展对应一个 gettext domain：
- JupyterLab 核心 → domain = `jupyterlab` → `jupyterlab.po`
- Notebook → domain = `notebook` → `notebook.po`
- jupyterlab-git → domain = `jupyterlab_git` → `jupyterlab_git.po`

运行时 JupyterLab 按 domain 分别加载翻译文件，实现各扩展独立翻译。

## 构建时编译

`jupyterlab-translate` hatch build hook 在构建 wheel 时：
1. 读取 LC_MESSAGES 目录下所有 .po 文件
2. 编译为 .mo 二进制文件（Python 后端使用）
3. 转换为 .json 文件（JavaScript 前端使用）
4. .mo 和 .json 打入 wheel，.po 被排除

## 相关概念

- [语言包结构剖析](05-package-anatomy.md)
- [Crowdin 翻译平台集成](04-crowdin-integration.md)
- [Entry Point 语言包发现机制](10-entry-point-discovery.md)
