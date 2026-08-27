---
type: Concept
title: 字符串提取流水线
description: jupyterlab-translate的三源字符串提取机制：Python文件通过pybabel提取、TypeScript/TSX通过gettext-extract提取、JSON Schema通过自定义递归遍历提取
tags: [extraction, pybabel, gettext-extract, typescript, python, schema, pot]
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

# 字符串提取流水线

字符串提取是jupyterlab-translate的核心能力，它从三种不同类型的源文件中提取可翻译字符串，合并后生成统一的POT模板文件。整个提取过程由 `create_catalog()` 函数编排。

## 提取流水线总览

```
源文件输入
    │
    ├──→ Python (*.py) ──→ pybabel extract ──→┐
    │                                         │
    ├──→ TypeScript (*.ts) ──→ gettext-extract ──→ 合并(fix_location) → 去重(remove_duplicates) → POT输出
    ├──→ TSX (*.tsx)     ──→ gettext-extract ──→│
    │                                         │
    └──→ JSON Schema (*.json) ──→ 自定义递归 ──→┘
```

## 一、Python字符串提取

Python文件的字符串提取由 `extract_strings()` 函数完成，底层调用Babel的 `pybabel extract` 命令。

### 提取命令

```bash
pybabel extract --no-wrap --charset=utf-8 \
    -o <output.pot> \
    --project=<project> \
    --version=<version> \
    --mapping=pybabel_config.cfg \
    <input_paths...>
```

### 提取哪些函数

根据 `pybabel_config.cfg` 配置，pybabel从以下函数调用中提取字符串：

| 函数 | gettext等价 | 用途 |
|------|------------|------|
| `trans.__` / `trans.gettext` | gettext | 简单翻译 |
| `trans._n` / `trans.ngettext` | ngettext | 复数翻译 |
| `trans._p` / `trans.pgettext` | pgettext | 带上下文翻译 |
| `trans._np` / `trans.npgettext` | npgettext | 带上下文复数翻译 |

### 源文件发现

`find_source_files()` 函数递归查找 `.py` 文件，默认跳过以下目录：
`tests`, `test`, `node_modules`, `lib`, `.git`, `.ipynb_checkpoints`

### Python代码中的使用示例

```python
from some_module import trans

# 简单翻译
text = trans.__("Hello World")

# 复数翻译
text = trans._n("One item", "{count} items", count)

# 带上下文翻译
text = trans._p("menu", "File")
```

## 二、TypeScript/TSX字符串提取

TS/TSX文件的字符串提取由 `extract_tsx_strings()` 函数完成，底层调用Node.js的gettext-extract工具。

### 为什么需要Node.js

gettext-extract是一个npm包，专门用于从JavaScript/TypeScript源码中提取gettext标记的字符串。jupyterlab-translate使用 `@vercel/ncc` 将其打包为单个 `index.js` 文件，内嵌在Python包中。

### 调用流程

1. 创建临时JSON配置文件，内容为 `GETTEXT_CONFIG`
2. 调用 `gettext-extract --config <config.json>`（通过子进程执行node）
3. 读取生成的POT文件，使用polib解析
4. 提取每个条目的msgid、msgid_plural、msgctxt、occurrences、comment等字段
5. 返回条目列表字典

### JS/TS中的翻译函数

JS端支持5种调用根和8种翻译函数的组合（共40种模式）：

**调用根（receiver objects）：**
- `trans`
- `this.trans`
- `this._trans`
- `this.props.trans`
- `props.trans`

**翻译函数：**

| 函数 | 参数位置 | 说明 |
|------|---------|------|
| `__` / `gettext` | text: 0 | 简单翻译 |
| `_n` / `ngettext` | text: 0, textPlural: 1 | 复数翻译 |
| `_p` / `pgettext` | context: 0, text: 1 | 带上下文翻译 |
| `_np` / `npgettext` | context: 0, text: 1, textPlural: 2 | 带上下文复数翻译 |

### 文件匹配

- glob模式：`**/*.ts*(x)`（匹配.ts和.tsx文件）
- 忽略：`examples/**/*.ts*(x)`、`**/*.spec.ts`、`node_modules/**/*.ts*(x)`
- 提取行注释作为翻译注释（`otherLineLeading: true`）

### TypeScript代码中的使用示例

```typescript
// 简单翻译
this._trans.__("Hello World");

// 复数翻译
trans._n("One file", "{count} files", count);

// 带上下文
trans._p("toolbar", "Run");

// 带上下文复数
trans._np("menu", "One item", "{count} items", count);
```

## 三、JSON Schema字符串提取

JSON Schema文件的字符串提取由 `extract_schema_strings()` 和 `_extract_schema_strings()` 完成，采用自定义递归遍历+正则选择器匹配方案。

### 提取流程

1. 在源文件目录中查找所有 `package.json`
2. 读取 `jupyterlab.schemaDir` 字段确定schema目录位置
3. 递归查找schema目录下所有 `.json` 文件
4. 对每个schema文件，调用 `_extract_schema_strings()` 递归遍历JSON结构
5. 对匹配选择器正则的字符串值，生成翻译条目

### 默认选择器（DEFAULT_SCHEMA_SELECTORS）

| JSON路径模式 | 翻译上下文（msgctxt） | 说明 |
|-------------|-------------------|------|
| `/title` | `schema` | Schema根标题 |
| `/description` | `schema` | Schema根描述 |
| `/properties/.*/title` | `settings` | 属性标题 |
| `/properties/.*/description` | `settings` | 属性描述 |
| `/definitions/.*/properties/.*/title` | `settings` | 定义中的属性标题 |
| `/definitions/.*/properties/.*/description` | `settings` | 定义中的属性描述 |
| `/jupyter\.lab\.setting-icon-label` | `settings` | 设置图标标签 |
| `/jupyter\.lab\.menus/.*/label` | `menu` | 菜单项标签 |
| `/jupyter\.lab\.metadataforms/.*/label` | `metadataforms` | 元数据表单标签 |
| `/jupyter\.lab\.toolbars/.*/label` | `toolbar` | 工具栏标签 |
| `/jupyter\.lab\.toolbars/.*/caption` | `toolbar` | 工具栏提示 |

### 自定义选择器

扩展开发者可以在package.json中通过 `jupyter.lab.internationalization.selectors` 字段添加自定义选择器：

```json
{
  "jupyterlab": {
    "internationalization": {
      "selectors": {
        "my-custom-path/.*/label": "my-context"
      }
    }
  }
}
```

自定义选择器的路径是相对于schema根的JSON Pointer路径，使用正则表达式匹配。

### Schema条目的occurrences格式

Schema条目的occurrences格式为 `(ref_path, json_pointer_path)`，例如：
- `("/schema/plugin.json", "/title")`
- `("/schema/plugin.json", "/properties/editorConfig/title")`

## 四、合并与去重

三路提取完成后，`create_catalog()` 执行以下后处理步骤：

### fix_location — 路径修正

- 将源码文件的绝对路径转换为相对于仓库根目录的相对路径
- 将Windows反斜杠`\`统一为正斜杠`/`
- 将TS/TSX和Schema提取的条目追加到POT文件中

### remove_duplicates — 去重

- 以 `(msgctxt, msgid, msgid_plural)` 三元组作为唯一键
- 合并重复条目的occurrences（出现位置列表）
- 跳过空msgid条目
- 按occurrences排序输出

### merge — 与已有POT合并

如果设置 `merge=True`（默认），使用 `xgettext` 命令将新提取的字符串与已有的POT文件合并，保留已有翻译引用。

## 相关概念

- [翻译目录管理](05-catalog-management.md)
- [Jed JSON翻译格式](06-json-jed-format.md)
- [Schema国际化选择器](09-schema-i18n-selectors.md)
- [快速开始](01-getting-started.md)
- [核心工具源码映射](../references/utils-source.md)
- [常量与配置映射](../references/constants-config.md)
