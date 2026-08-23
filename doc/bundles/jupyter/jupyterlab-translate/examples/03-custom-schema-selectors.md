---
type: Example
title: 自定义Schema选择器
description: 在JupyterLab扩展中配置自定义JSON Schema国际化选择器，提取非标准字段的翻译字符串
tags: [example, schema, selectors, customization, i18n, settings, json-pointer]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: utils-source
    resource: /references/utils-source.md
    title: 核心工具源码映射
---

# 自定义Schema选择器

本示例演示如何在JupyterLab扩展中配置自定义JSON Schema国际化选择器，以提取默认选择器不覆盖的字段中的可翻译字符串。

## 背景

默认情况下，jupyterlab-translate会自动提取schema中以下字段的字符串：
- 根级 `title` 和 `description`
- `properties/*/title` 和 `properties/*/description`
- JupyterLab特定字段如 `jupyter.lab.menus`, `jupyter.lab.toolbars` 等

如果你的schema包含其他需要翻译的字段（如自定义占位符、分组标签、验证消息等），需要通过自定义选择器配置来提取它们。

## 配置方式

在扩展的 `package.json` 中添加 `jupyterlab.internationalization.selectors` 字段：

```json
{
  "name": "my-extension",
  "jupyterlab": {
    "schemaDir": "schema",
    "internationalization": {
      "selectors": {
        "properties/.*/placeholder": "my-ext",
        "properties/.*/enumNames/.*/.*": "my-ext",
        "definitions/.*/properties/.*/placeholder": "my-ext",
        "properties/dialog/.*/title": "dialog",
        "properties/dialog/.*/message": "dialog"
      }
    }
  }
}
```

## 选择器语法

选择器key是JSON Pointer路径模式，最终被编译为正则表达式 `^/<pattern>$`。

### 基本通配符

- `.*` 匹配任意单个路径段（一个key名）
- `/` 分隔路径层级
- 字面值直接匹配（含点号的key需要用 `\.` 转义）

### 示例模式

| 模式 | 匹配路径 | 说明 |
|------|---------|------|
| `properties/.*/title` | `/properties/foo/title` | 任意属性的title（默认已覆盖） |
| `properties/.*/placeholder` | `/properties/name/placeholder` | 属性的placeholder |
| `properties/.*/enumNames/.*` | `/properties/mode/enumNames/0` | 枚举选项的显示名 |
| `definitions/.*/title` | `/definitions/person/title` | 定义的标题 |
| `properties/.*/items/properties/.*/title` | `/properties/list/items/properties/name/title` | 嵌套数组项属性的title |

## 完整示例

### Schema文件

假设你的 `schema/plugin.json` 如下：

```json
{
  "title": "My Extension",
  "description": "An extension with custom translatable fields",
  "properties": {
    "userName": {
      "type": "string",
      "title": "User Name",
      "description": "Enter your user name",
      "placeholder": "e.g. John Doe"
    },
    "theme": {
      "type": "string",
      "title": "Theme",
      "enum": ["light", "dark", "auto"],
      "enumNames": ["Light Theme", "Dark Theme", "Auto Detect"]
    },
    "greeting": {
      "type": "string",
      "title": "Greeting Message",
      "default": "Welcome to My Extension!"
    }
  },
  "definitions": {
    "dialog": {
      "title": "Confirmation",
      "message": "Are you sure?"
    }
  }
}
```

### package.json配置

```json
{
  "name": "my-extension",
  "jupyterlab": {
    "schemaDir": "schema",
    "internationalization": {
      "selectors": {
        "properties/.*/placeholder": "my-ext",
        "properties/.*/enumNames/.*": "my-ext",
        "definitions/.*/message": "my-ext"
      }
    }
  }
}
```

### 提取结果

执行 `jupyterlab-translate extract` 后，POT文件中将包含以下条目：

```pot
# 默认选择器提取的
#: /schema/plugin.json:/title
msgctxt "schema"
msgid "My Extension"
msgstr ""

#: /schema/plugin.json:/properties/userName/title
msgctxt "settings"
msgid "User Name"
msgstr ""

#: /schema/plugin.json:/properties/userName/description
msgctxt "settings"
msgid "Enter your user name"
msgstr ""

#: /schema/plugin.json:/properties/theme/title
msgctxt "settings"
msgid "Theme"
msgstr ""

#: /schema/plugin.json:/properties/greeting/title
msgctxt "settings"
msgid "Greeting Message"
msgstr ""

# 自定义选择器提取的
#: /schema/plugin.json:/properties/userName/placeholder
msgctxt "my-ext"
msgid "e.g. John Doe"
msgstr ""

#: /schema/plugin.json:/properties/theme/enumNames/0
msgctxt "my-ext"
msgid "Light Theme"
msgstr ""

#: /schema/plugin.json:/properties/theme/enumNames/1
msgctxt "my-ext"
msgid "Dark Theme"
msgstr ""

#: /schema/plugin.json:/properties/theme/enumNames/2
msgctxt "my-ext"
msgid "Auto Detect"
msgstr ""

#: /schema/plugin.json:/definitions/dialog/message
msgctxt "my-ext"
msgid "Are you sure?"
msgstr ""
```

## 翻译上下文（msgctxt）的选择

自定义选择器的value指定了翻译上下文（msgctxt），建议：

- **按UI区域分组**：如 `"dialog"`, `"toolbar"`, `"sidebar"`, `"my-ext"`
- **避免使用默认上下文名**：不要使用已被默认选择器使用的 `"schema"`, `"settings"`, `"menu"`, `"toolbar"`, `"metadataforms"`，除非你确实要将自定义字段归入这些上下文
- **使用扩展短名作为前缀**：如 `"my-ext:placeholder"` 避免与其他扩展冲突

```json
{
  "selectors": {
    "properties/.*/placeholder": "my-ext:placeholder",
    "properties/.*/description": "my-ext:help-text"
  }
}
```

## 验证配置

配置完成后，执行extract命令检查是否正确提取了自定义字段：

```bash
# 提取字符串
jupyterlab-translate extract ./my-extension my_extension

# 查看POT文件，确认自定义字段被提取
grep -A2 "placeholder" my-extension/my_extension/locale/my_extension.pot
```

如果预期字段未被提取，检查：
1. package.json中 `jupyterlab.schemaDir` 路径是否正确
2. 选择器模式是否正确匹配JSON Pointer路径
3. JSON Pointer路径中数组索引用 `[0]`, `[1]` 格式（不是 `/0`）

## 注意事项

- 自定义选择器的默认翻译上下文是 `"schema"`（如果selectors是列表而非字典）
- 选择器模式中正则特殊字符（`.` `(` `)` `[` `]`等）需要转义
- 路径遍历对list元素使用 `[index]` 格式（如 `/properties/list[0]/title`）
- 只有字符串类型的叶子节点值才会被提取，数字、布尔值和null不会被提取
- 自定义选择器与默认选择器合并生效，不会覆盖默认配置

## 相关概念

- [Schema国际化选择器](/concepts/09-schema-i18n-selectors.md)
- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [Jed JSON翻译格式](/concepts/06-json-jed-format.md)
