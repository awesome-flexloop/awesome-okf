---
okf_version: "0.2"
type: concept
title: "国际化系统"
description: "深入理解jupyterlab_server的gettext翻译体系：TranslationBundle封装、translator全局管理器、语言包发现与加载、JSON Schema自动翻译和REST API。"
tags: [i18n, internationalization, translation, gettext, babel, language-pack, pgettext, ngettext, locale]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: translation-utils-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/translation_utils.py"
    title: "jupyterlab_server/translation_utils.py"
  - id: translations-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/translations_handler.py"
    title: "jupyterlab_server/translations_handler.py"
---

# 国际化系统

jupyterlab_server 提供了一套完整的国际化（i18n）基础设施，基于Python标准库的gettext和Babel库，支持前端界面的多语言切换、JSON Schema自动翻译和语言包动态发现。

## 架构概览

```
┌──────────────────────────────────────────────┐
│             前端 JavaScript 代码              │
│  使用 gettext 类API（通过 @jupyterlab/translation）│
└─────────────────┬────────────────────────────┘
                  │ HTTP GET /lab/api/translations/{locale}
┌─────────────────▼────────────────────────────┐
│         TranslationsHandler (REST API)       │
│  - 列出语言包 / 返回翻译数据                   │
│  - 调用 translator.set_locale()              │
└─────────────────┬────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────┐
│            translator (全局管理器)             │
│  - 管理 TranslationBundle 缓存                │
│  - set_locale() 切换全局语言                   │
│  - translate_schema() 翻译JSON Schema         │
└─────────────────┬────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────┐
│         TranslationBundle (单domain翻译)       │
│  - gettext() / ngettext() / pgettext()       │
│  - 封装 gettext.GNUTranslations              │
└──────────────────────────────────────────────┘
```

## 核心概念

### Locale 代码

使用标准BCP 47语言代码：
- `en` — 英语（默认，不加载翻译文件）
- `zh_CN` — 简体中文
- `zh_TW` — 繁体中文
- `ja` — 日语
- `fr` — 法语
- `ach_UG` — 伪语言（pseudo-language，用于i18n测试）
- `default` — API中的特殊值，映射到系统locale（SYS_LOCALE）

`is_valid_locale()` 使用 Babel 的 `Locale.parse()` 验证locale有效性，对挪威语 `no_NO` 做了特殊处理（Babel默认不识别但实际有效）。

### Domain 域名

在gettext体系中，domain是翻译文件的命名空间。jupyterlab_server中：
- `jupyterlab` — 默认domain（常量 `DEFAULT_DOMAIN`）
- 其他domain对应各扩展包名，如 `jupyterlab_application`

Domain规范化：`translator.normalize_domain()` 将连字符 `-` 替换为下划线 `_`。

## TranslationBundle 类

```python
class TranslationBundle:
```

TranslationBundle是单个domain的翻译单元，封装了gettext.NullTranslations。

### 初始化与locale切换

```python
def __init__(self, domain: str = DEFAULT_DOMAIN, locale_: str = DEFAULT_LOCALE):
    self._domain = domain
    self._translator = gettext.NullTranslations()
    self.update_locale(locale_)
```

`update_locale(locale_)` 执行实际的翻译加载：
- locale为"en"时，使用NullTranslations（返回原文）
- 其他locale：尝试import对应的语言包模块 `jupyterlab_language_pack_{locale_}`
- 使用 `gettext.translation(domain, localedir, languages=[locale_], fallback=True)` 加载翻译
- fallback=True确保翻译缺失时不抛异常，返回原文

### 翻译方法

| 方法 | 简写 | 说明 | gettext对应 |
|------|------|------|-------------|
| `gettext(msgid)` | `__()` | 单数翻译 | `_()` |
| `ngettext(singular, plural, n)` | `_n()` | 复数翻译 | 自动选择单数/复数形式 |
| `pgettext(context, msgid)` | `_p()` | 带上下文的单数翻译 | 消除同词多义 |
| `npgettext(context, sing, plur, n)` | `_np()` | 带上下文的复数翻译 | 上下文+复数 |

上下文翻译示例：
```python
# "Open"作为动词（打开文件）
bundle._p("verb", "Open")

# "Open"作为形容词（打开的文件）
bundle._p("adjective", "Open")
```

> ⚠️ Python 3.7及以下版本，pgettext/npgettext回退到gettext/ngettext（丢失上下文区分）。

## translator 全局管理器

```python
class translator:
```

translator是一个类级别的静态管理器（所有方法用`@classmethod`），管理全局语言状态和TranslationBundle缓存。

### 缓存机制

```python
_TRANSLATORS: dict[str, TranslationBundle] = {}
_LOCALE = SYS_LOCALE
```

- 每个domain的TranslationBundle只创建一次，存入缓存
- `set_locale(locale_)` 切换全局语言时，更新所有已缓存的bundle
- locale未变化时快速返回（幂等）

### Schema 自动翻译

`translate_schema(schema)` 是translator的一个关键功能：

1. 如果当前locale为en，直接返回原schema（无翻译）
2. 从schema中读取domain（默认"jupyterlab"）
3. 加载对应domain的TranslationBundle
4. 递归遍历schema的所有字符串值
5. 对路径匹配 `DEFAULT_SCHEMA_SELECTORS` 中模式的值，使用pgettext翻译

#### Schema路径选择器

```python
DEFAULT_SCHEMA_SELECTORS = {
    "properties/.*/title": "settings",           # 设置项标题
    "properties/.*/description": "settings",     # 设置项描述
    "definitions/.*/properties/.*/title": "settings",
    "definitions/.*/properties/.*/description": "settings",
    "title": "schema",                           # schema本身标题
    "description": "schema",                     # schema本身描述
    r"jupyter\.lab\.setting-icon-label": "settings",  # 设置图标标签
    r"jupyter\.lab\.menus/.*/label": "menu",     # 菜单项标签
    r"jupyter\.lab\.toolbars/.*/label": "toolbar",    # 工具栏项标签
}
```

键是正则路径模式，值是gettext上下文（msgctxt）。这确保只有用户可见的UI字符串被翻译，内部配置字段不被翻译。

## 语言包发现与加载

### 发现机制

语言包通过Python entry points发现：

```python
JUPYTERLAB_LANGUAGEPACK_ENTRY = "jupyterlab.languagepack"
JUPYTERLAB_LOCALE_ENTRY = "jupyterlab.locale"
```

`get_language_packs(display_locale)`：
1. 使用 `importlib.metadata.entry_points()` 发现 `jupyterlab.languagepack` 组的所有entry point
2. 加载语言包模块，验证locale有效性
3. 返回 `{locale_code: {displayName, nativeName}}` 字典

### 翻译数据加载

`get_language_pack(locale_)` 是核心加载函数：

1. 发现已安装语言包（同get_language_packs）
2. 发现包含locale数据的已安装包（`jupyterlab.locale` entry points）
3. 遍历语言包的locale目录，加载所有 `.json` 翻译文件
4. 合并包自带的locale数据（按版本号优先：如果包自带数据版本更新则覆盖语言包数据）
5. 添加语言包中不存在的包locale数据

### 翻译数据格式

语言包JSON文件格式：
```json
{
  "domain": "jupyterlab",
  "locale_data": {
    "jupyterlab": {
      "": {
        "domain": "jupyterlab",
        "lang": "zh_CN",
        "plural_forms": "nplurals=1; plural=0;"
      },
      "Open": ["打开"],
      "Save": ["保存"]
    }
  }
}
```

## TranslationsHandler REST API

```python
class TranslationsHandler(SchemaHandler):
```

### GET /lab/api/translations/

列出所有已安装语言包：
```json
{
  "data": {
    "en": { "displayName": "English", "nativeName": "English" },
    "zh_CN": { "displayName": "Chinese (Simplified)", "nativeName": "中文（简体）" }
  },
  "message": ""
}
```

### GET /lab/api/translations/{locale}

获取指定locale的完整翻译数据：
- `locale="default"` → 使用SYS_LOCALE
- 语言包安装成功时，调用 `translator.set_locale(locale)` 切换全局语言
- 使用 `IOLoop.run_in_executor` 在executor线程中执行阻塞IO操作
- 返回 `{"data": {...}, "message": "..."}`

## 与设置系统的集成

SettingsHandler在返回设置数据时：
1. 从请求参数获取当前locale
2. 调用 `translator.set_locale(locale)` 切换语言
3. 调用 `translator.translate_schema(schema)` 翻译JSON Schema
4. 返回翻译后的schema（含翻译后的标题和描述）

这意味着前端设置面板会根据用户选择的语言自动显示翻译后的界面。

---

**下一步阅读：**
- [进程管理与CLI工具](09-process-and-cli.md)
- [代码示例](../examples/00-basic-usage.md)
