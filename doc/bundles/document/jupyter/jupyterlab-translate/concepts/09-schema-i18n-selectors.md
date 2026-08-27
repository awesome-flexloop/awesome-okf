---
type: Concept
title: JSON Schema国际化选择器
description: JupyterLab扩展通过JSON Schema定义设置项，jupyterlab-translate使用正则选择器机制自动识别和提取schema中需要翻译的字段
tags: [json-schema, selectors, i18n, settings, internationalization, regex, customization]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: utils-source
    resource: /references/utils-source.md
    title: 核心工具源码映射
  - id: constants-config
    resource: /references/constants-config.md
    title: 常量与配置映射
---

# JSON Schema国际化选择器

JupyterLab扩展通过JSON Schema文件定义设置项（settings）、菜单项、工具栏按钮等UI元素的配置。jupyterlab-translate使用**选择器（selectors）**机制来识别schema中哪些字段需要被翻译，以及它们应该被归类到哪个翻译上下文。

## Schema目录发现

`extract_schema_strings()` 函数通过以下步骤定位schema文件：

1. 在源文件目录中查找所有 `package.json`
2. 读取每个package.json中的 `jupyterlab.schemaDir` 字段，确定schema目录位置
3. 递归查找schema目录下所有 `.json` 文件
4. 对每个schema文件调用 `_extract_schema_strings()` 提取可翻译字符串

## 默认选择器（DEFAULT_SCHEMA_SELECTORS）

默认情况下，以下JSON路径模式的字符串值会被提取：

### 通用Schema字段

| 正则模式 | 翻译上下文（msgctxt） | 说明 |
|---------|-------------------|------|
| `/title` | `schema` | Schema根级标题 |
| `/description` | `schema` | Schema根级描述 |
| `/properties/.*/title` | `settings` | 属性标题 |
| `/properties/.*/description` | `settings` | 属性描述 |
| `/definitions/.*/properties/.*/title` | `settings` | 定义中嵌套属性的标题 |
| `/definitions/.*/properties/.*/description` | `settings` | 定义中嵌套属性的描述 |

### JupyterLab特定字段

| 正则模式 | 翻译上下文（msgctxt） | 说明 |
|---------|-------------------|------|
| `/jupyter\.lab\.setting-icon-label` | `settings` | 设置面板图标标签 |
| `/jupyter\.lab\.menus/.*/label` | `menu` | 菜单项标签 |
| `/jupyter\.lab\.metadataforms/.*/label` | `metadataforms` | 元数据表单标签 |
| `/jupyter\.lab\.toolbars/.*/label` | `toolbar` | 工具栏按钮标签 |
| `/jupyter\.lab\.toolbars/.*/caption` | `toolbar` | 工具栏按钮提示文字 |

## 选择器工作机制

### 1. 模式编译

`_prepare_schema_patterns()` 函数将选择器字典编译为正则表达式：

```python
def _prepare_schema_patterns(schema: dict) -> Dict[Pattern, str]:
    selectors = {
        **DEFAULT_SCHEMA_SELECTORS,
        **{
            selector: _default_schema_context  # "schema"
            for selector in schema.get("jupyter.lab.internationalization", {}).get("selectors", [])
        },
    }
    return {
        re.compile("^/" + pattern + "$"): context
        for pattern, context in selectors.items()
    }
```

每个选择器模式被包装为 `^/pattern$` 的正则表达式，匹配完整的JSON Pointer路径。

### 2. 递归遍历

`_extract_schema_strings()` 递归遍历JSON schema的字典和列表结构：

- 遇到**字符串值**时，检查当前JSON Pointer路径是否匹配任何选择器正则；如果匹配，生成翻译条目
- 遇到**字典**时，递归遍历，将 `/key` 追加到路径前缀
- 遇到**列表**时，递归遍历每个dict元素，将 `[index]` 追加到路径前缀

### 3. 生成条目

匹配的字符串生成如下格式的翻译条目：

```python
dict(
    msgctxt=context,           # 翻译上下文，如 "settings", "menu", "toolbar"
    msgid=value,               # 待翻译的字符串值
    occurrences=[(ref_path, path)]  # (文件相对路径, JSON Pointer路径)
)
```

### JSON Pointer路径示例

对于以下schema结构：

```json
{
  "title": "Text Editor",
  "properties": {
    "editorConfig": {
      "title": "Editor Configuration",
      "properties": {
        "cursorBlinkRate": {
          "title": "Cursor blinking rate"
        }
      }
    }
  }
}
```

生成的路径为：
- `/title` → msgctxt: "schema"
- `/properties/editorConfig/title` → msgctxt: "settings"
- `/properties/editorConfig/properties/cursorBlinkRate/title` → msgctxt: "settings"

## 自定义选择器

扩展开发者可以在schema文件对应的package.json中添加自定义选择器，通过 `jupyter.lab.internationalization.selectors` 字段：

```json
{
  "jupyterlab": {
    "schemaDir": "schema",
    "internationalization": {
      "selectors": {
        "properties/.*/placeholder": "MyExtension",
        "properties/dialog/.*/title": "dialog",
        "definitions/.*/properties/.*/placeholder": "MyExtension"
      }
    }
  }
}
```

自定义选择器的规则：
- key是JSON Pointer路径模式（支持正则表达式的 `.*` 通配符）
- value是翻译上下文名称（msgctxt）
- 自定义选择器的默认上下文为 `"schema"`

### 选择器语法

选择器模式是正则表达式，最终被编译为 `^/<pattern>$`：

- `.*` 匹配任意路径段（一个层级中的任意key名）
- `/` 是路径层级分隔符
- 字面量点号需要转义：`jupyter\.lab\.menus` 匹配 `jupyter.lab.menus`
- `[index]` 格式用于数组元素的索引（在遍历列表时自动生成）

## 翻译上下文的作用

msgctxt（翻译上下文）在翻译文件中有两个重要作用：

1. **消歧义**：同一个英文单词在不同上下文中可能需要不同的翻译。例如 "Open" 在菜单中翻译为"打开"，在状态中可能翻译为"开放的"。

2. **前端查找**：JupyterLab前端根据上下文查找对应的翻译字符串。key格式为 `{msgctxt}\x04{msgid}`。

PO文件中的表现：

```po
#: /schema/plugin.json:/title
msgctxt "schema"
msgid "My Extension"
msgstr "我的扩展"

#: /schema/plugin.json:/jupyter.lab.menus/0/label
msgctxt "menu"
msgid "Open..."
msgstr "打开..."
```

编译后的JSON：

```json
{
    "schema\u0004My Extension": ["我的扩展"],
    "menu\u0004Open...": ["打开..."]
}
```

## 常见路径模式参考

在编写自定义选择器时，以下路径模式常有用：

| 模式 | 匹配内容 |
|------|---------|
| `title` | 根级title字段 |
| `properties/[^/]+/title` | 直接属性的title |
| `properties/.*/default` | 属性默认值（谨慎使用，可能包含非文本值） |
| `definitions/.*/title` | 定义的标题 |
| `jupyter\.lab\.menus/.*/label` | 菜单项标签 |
| `jupyter\.lab\.toolbars/.*/label` | 工具栏按钮标签 |
| `jupyter\.lab\.toolbars/.*/caption` | 工具栏按钮tooltip |
| `jupyter\.lab\.setting-icon-label` | 设置图标标签 |

> **注意**：路径模式不需要以 `/` 开头，编译时会自动添加。

## 相关概念

- [字符串提取流水线](04-extraction-pipeline.md)
- [Jed JSON翻译格式](06-json-jed-format.md)
- [自定义Schema选择器示例](../examples/03-custom-schema-selectors.md)
- [核心工具源码映射](../references/utils-source.md)
