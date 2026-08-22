---
type: Reference
title: "Gettext 翻译格式信源"
description: "POT/PO/MO 文件格式规范——JupyterLab 使用 GNU gettext 标准进行国际化"
tags: [jupyterlab, i18n, gettext, pot, po, mo, localization]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: gettext-source
    resource: https://www.gnu.org/software/gettext/manual/
    title: "GNU gettext Manual"
---

# Gettext 翻译格式信源

## 文件类型

JupyterLab 语言包使用 GNU gettext 标准的三种文件格式：

| 格式 | 扩展名 | 说明 | 是否纳入 Git |
|------|--------|------|:------------:|
| POT | `.pot` | 翻译模板（Portable Object Template），只有源字符串无翻译 | ✅ |
| PO | `.po` | 翻译文件（Portable Object），源字符串+目标语言翻译 | ✅ |
| MO | `.mo` | 编译后的二进制（Machine Object），运行时快速加载 | ❌（构建生成） |

此外还有 JSON 格式翻译文件（由 jupyterlab-translate 构建时生成）。

## POT 文件格式

```gettext
#  translator-comments
#. extracted-comments
#: reference…
#, flag…
#| msgid previous-untranslated-string
msgctxt "context"
msgid "untranslated-string"
msgstr "translated-string"
```

### 头部元数据

```gettext
#
msgid ""
msgstr ""
"Project-Id-Version: jupyterlab 0.0.0\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
```

### 条目示例

```gettext
#: /packages/markdownviewer-extension/schema/plugin.json:/description
msgctxt "schema"
msgid "Markdown viewer settings."
msgstr ""
```

- `#:`：源文件引用（文件路径:位置）
- `msgctxt`：上下文消歧（同一字符串在不同语境有不同翻译）
- `msgid`：源字符串（英文）
- `msgstr`：翻译字符串（POT 中为空，PO 中填写翻译）

### 多行字符串

长字符串使用多个双引号拼接：

```gettext
msgid ""
"The font family used to render markdown.\n"
"If `null`, value from current theme is used."
msgstr ""
```

## PO 文件格式

PO 文件在 POT 基础上增加翻译内容和元数据：

```gettext
msgid ""
msgstr ""
"Project-Id-Version: jupyterlab\n"
"Language-Team: Chinese Simplified\n"
"Language: zh_CN\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"X-Crowdin-Project: jupyterlab\n"
"X-Crowdin-Project-ID: 409874\n"
"X-Crowdin-Language: zh-CN\n"
"PO-Revision-Date: 2026-05-04 02:41\n"
```

Crowdin 添加的元数据：
- `X-Crowdin-Project`：Crowdin 项目名
- `X-Crowdin-Project-ID`：项目 ID（409874）
- `X-Crowdin-Language`：Crowdin 语言代码
- `X-Crowdin-File` / `X-Crowdin-File-ID`：文件标识

### 复数形式

中文 `Plural-Forms: nplurals=1; plural=0;`（无复数变化）。
其他语言如英语：`nplurals=2; plural=(n != 1);`

## 文件位置约定

遵循 gettext 标准目录布局：

```
locale/
└── {lang}_{REGION}/
    └── LC_MESSAGES/
        ├── domain1.po
        ├── domain1.mo
        ├── domain2.po
        └── domain2.mo
```

- `domain` 对应包名（如 `jupyterlab`、`notebook`、`jupyterlab_git`）
- 语言代码格式：`ll_CC`（ll=ISO 639-1 语言码，CC=ISO 3166-1 国家码）

## 上下文类型（msgctxt）

常见的 msgctxt 值：

| 上下文 | 用途 |
|--------|------|
| `schema` | 设置 schema 中的描述文本 |
| `settings` | 设置界面标签 |
| `menu` | 菜单项 |
| `command` | 命令名称/描述 |
| （空） | 通用 UI 文本 |
