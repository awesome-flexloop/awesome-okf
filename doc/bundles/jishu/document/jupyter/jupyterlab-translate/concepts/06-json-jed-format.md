---
type: Concept
title: Jed JSON翻译格式
description: JupyterLab前端使用的Jed JSON翻译格式详解，包括元数据结构、EOT上下文分隔符、复数形式处理和新旧合并策略
tags: [jed, json, format, frontend, plural, msgctxt, eot, i18n]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: converters-source
    resource: /references/converters-source.md
    title: 格式转换源码映射
---

# Jed JSON翻译格式

JupyterLab前端使用[Jed](https://messageformat.github.io/Jed/)库加载翻译数据。jupyterlab-translate的 `convert_catalog_to_json()` 函数负责将gettext PO文件转换为Jed兼容的JSON格式。

## JSON结构总览

```json
{
    "": {
        "domain": "<project-name>",
        "version": "<version-string>",
        "language": "<locale-with-dash>",
        "plural_forms": "<plural-forms-expression>"
    },
    "<message-key>": ["<translation>"],
    "<message-key>": ["<singular>", "<plural>", ...]
}
```

## 元数据字段

顶层key为空字符串 `""` 的对象包含翻译域的元数据：

| 字段 | 来源 | 说明 |
|------|------|------|
| `domain` | `project` 参数 | 翻译域名称，通常为项目名 |
| `version` | PO的 `Project-Id-Version` 最后一段 | 版本号（空格分割后取最后一段） |
| `language` | PO的 `Language` 字段，`_`替换为`-` | 语言代码（如 `zh-CN`, `ko-KR`） |
| `plural_forms` | PO的 `Plural-Forms` 字段 | 复数形式表达式 |

### 元数据示例

```json
{
    "": {
        "domain": "jupyterlab",
        "version": "3.0.0",
        "language": "ko-KR",
        "plural_forms": "nplurals=1; plural=0;"
    }
}
```

## 消息Key的构造规则

Jed JSON中的消息key取决于PO条目是否有msgctxt（上下文）：

### 无上下文条目

key为msgid原文本身：

```json
{
    "Hello World": ["你好，世界"]
}
```

对应PO：
```po
msgid "Hello World"
msgstr "你好，世界"
```

### 有上下文条目

key格式为 `{msgctxt}\x04{msgid}`，其中 `\x04` 是ASCII EOT（End of Transmission，0x04）控制字符：

```json
{
    "schema\u0004Markdown viewer settings.": ["마크다운 뷰어 설정"]
}
```

对应PO：
```po
msgctxt "schema"
msgid "Markdown viewer settings."
msgstr "마크다운 뷰어 설정"
```

> **为什么用EOT字符？** 这是gettext的约定。EOT字符（`\x04`）在正常文本中几乎不会出现，用作分隔符可以避免msgid中包含分隔符导致的歧义。Jed库在查找翻译时也使用同样的约定拼接key。

### 常见上下文类型

| msgctxt | 来源 | 说明 |
|---------|------|------|
| `schema` | JSON Schema的 `/title` 和 `/description` | Schema级别的标题和描述 |
| `settings` | JSON Schema的属性字段、icon-label | 设置项标题和描述 |
| `menu` | JSON Schema的 `jupyter.lab.menus` | 菜单项标签 |
| `toolbar` | JSON Schema的 `jupyter.lab.toolbars` | 工具栏按钮标签和提示 |
| `metadataforms` | JSON Schema的 `jupyter.lab.metadataforms` | 元数据表单标签 |

## 翻译值的格式

### 简单翻译

无复数形式的翻译，值为单元素数组：

```json
{
    "Cut Cell": ["셀 잘라내기"]
}
```

### 复数翻译

有复数形式的翻译，值为按plural index排序的数组：

```json
{
    "One file": ["一个文件", "{count}个文件"]
}
```

对应PO：
```po
msgid "One file"
msgid_plural "{count} files"
msgstr[0] "一个文件"
msgstr[1] "{count}个文件"
```

数组长度应等于plural_forms中定义的nplurals值。

### 单复数形式语言的特殊处理

对于nplurals=1的语言（如韩语、日语、中文等），即只有一种复数形式的语言，Jed/JupyterLab前端期望数组至少有2个元素。因此转换时会在只有一个翻译值时追加一个空字符串：

```json
{
    "Cut Cell": ["셀 잘라내기", ""]
}
```

这是为了通过JupyterLab前端的校验逻辑——前端检查复数数组长度，如果长度为1会认为无效。空字符串作为dummy元素保证前端正确加载。

## 新旧合并策略

当目标JSON文件已存在时，`convert_catalog_to_json()` 会执行合并：

1. 读取现有JSON文件
2. 移除旧的元数据（`""` key）
3. 用现有数据初始化result（保留旧翻译）
4. 用新的PO数据覆盖/更新条目
5. 写入新的JSON

这保证了即使PO文件中某些条目暂时没有翻译（msgstr为空），旧的翻译值也不会丢失。

## 过滤规则

以下条目不写入JSON：

1. **obsolete条目**：PO中标记为obsolete的条目被跳过（`entry.obsolete`）
2. **空翻译条目**：如果msgstr为空且没有msgid_plural，该条目不写入
3. **空复数条目**：如果msgid_plural存在但所有msgstr_plural都为空，不写入

## 输出格式

JSON输出使用以下格式化选项：
- `sort_keys=True`：按键名排序
- `indent=4`：4空格缩进

## 完整示例

以下是一个编译后的JSON文件示例（来自韩语语言包测试）：

```json
{
    "": {
        "domain": "jupyterlab",
        "language": "ko-KR",
        "plural_forms": "nplurals=1; plural=0;",
        "version": "jupyterlab"
    },
    "Cut Cell": [
        "셀 잘라내기",
        ""
    ],
    "schema\u0004Markdown viewer settings.": [
        "마크다운 뷰어 설정"
    ],
    "settings\u0004Markdown Viewer": [
        "마크다운 뷰어"
    ],
    "settings\u0004The font family used to render markdown.\nIf `null`, value from current theme is used.": [
        "마크다운을 표시할 때 사용하는 글꼴.\n값이 `null`이면 현재 테마의 해당 값이 사용됩니다."
    ]
}
```

## 与MO文件的关系

| 特性 | MO文件 | JSON/Jed文件 |
|------|--------|-------------|
| 使用者 | Python后端（gettext） | JupyterLab前端（Jed） |
| 格式 | 二进制 | 文本JSON |
| 加载速度 | 快（直接mmap） | 中（JSON解析） |
| 复数处理 | gettext内置 | Jed库处理 |
| 上下文分隔 | gettext内置 | \x04字符约定 |
| 编译工具 | pybabel compile / polib | convert_catalog_to_json |

两种文件都从同一个PO文件生成，内容相同但格式不同，分别服务于前后端。

## 相关概念

- [翻译目录管理](05-catalog-management.md)
- [字符串提取流水线](04-extraction-pipeline.md)
- [Hatch构建钩子集成](07-hatch-build-hook.md)
- [格式转换源码映射](../references/converters-source.md)
