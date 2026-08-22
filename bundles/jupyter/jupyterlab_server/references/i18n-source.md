---
okf_version: "0.2"
type: reference
title: "国际化系统源码（translation_utils.py + translations_handler.py）"
description: "jupyterlab_server 国际化系统的完整 API：TranslationBundle gettext封装、translator全局管理器、语言包发现、JSON Schema翻译和TranslationsHandler REST端点"
tags: [i18n, internationalization, translation, gettext, language-pack, babel, locale, schema-translation]
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

# 国际化系统源码

本信源登记国际化系统两个核心文件的API：
- `translation_utils.py`（约755行）：翻译核心逻辑
- `translations_handler.py`（约68行）：REST API处理器

## 常量

```python
DEFAULT_LOCALE = "en"
SYS_LOCALE = locale.getlocale()[0] or DEFAULT_LOCALE
LOCALE_DIR = "locale"
LC_MESSAGES_DIR = "LC_MESSAGES"
DEFAULT_DOMAIN = "jupyterlab"
L10N_SCHEMA_NAME = "@jupyterlab/translation-extension:plugin"
PSEUDO_LANGUAGE = "ach_UG"
```

Entry points 名称：
- `JUPYTERLAB_LANGUAGEPACK_ENTRY = "jupyterlab.languagepack"`
- `JUPYTERLAB_LOCALE_ENTRY = "jupyterlab.locale"`

## Schema翻译选择器

```python
DEFAULT_SCHEMA_SELECTORS = {
    "properties/.*/title": "settings",
    "properties/.*/description": "settings",
    "definitions/.*/properties/.*/title": "settings",
    "definitions/.*/properties/.*/description": "settings",
    "title": "schema",
    "description": "schema",
    r"jupyter\.lab\.setting-icon-label": "settings",
    r"jupyter\.lab\.menus/.*/label": "menu",
    r"jupyter\.lab\.toolbars/.*/label": "toolbar",
}
```

正则路径模式映射到gettext上下文（pgettext的msgctxt），用于自动翻译JSON Schema中的用户可见字符串。

## 核心函数

### is_valid_locale(locale_)

```python
def is_valid_locale(locale_: str) -> bool:
```

使用 `babel.Locale.parse()` 验证locale代码有效性。特殊处理 `no_NO`（挪威语）返回True。

### get_display_name(locale_, display_locale)

```python
def get_display_name(locale_: str, display_locale: str = DEFAULT_LOCALE) -> str:
```

获取语言的本地化显示名称，首字母大写。

### merge_locale_data(language_pack_locale_data, package_locale_data)

```python
def merge_locale_data(
    language_pack_locale_data: dict[str, Any],
    package_locale_data: dict[str, Any],
) -> dict[str, Any]:
```

按版本号合并语言包数据：如果包自带locale数据版本比语言包新，则用包的版本更新对应条目。

### get_language_packs(display_locale)

```python
def get_language_packs(display_locale: str = DEFAULT_LOCALE) -> tuple[dict, str]:
```

列出所有已安装语言包：
- 通过entry points发现 `jupyterlab.languagepack` 组
- 验证每个locale有效性
- 返回 `{locale_code: {displayName, nativeName}}` 字典和错误消息
- 包含DEFAULT_LOCALE（en）和PSEUDO_LANGUAGE（ach_UG）

### get_language_pack(locale_)

```python
def get_language_pack(locale_: str) -> tuple:
```

获取指定locale的完整语言包数据：
1. 发现已安装语言包
2. 发现包含locale数据的已安装包（jupyterlab.locale entry point）
3. 遍历语言包目录加载所有.json翻译文件
4. 合并包自带的locale数据（按版本号优先）
5. 添加语言包中不存在的包locale数据

### get_installed_packages_locale(locale_)

```python
def get_installed_packages_locale(locale_: str) -> tuple[dict, str]:
```

发现所有包含指定locale数据的已安装扩展包。

## TranslationBundle 类

```python
class TranslationBundle:
```

基于gettext的翻译Bundle，封装单个domain的翻译功能。

### __init__(domain, locale_)

初始化：创建NullTranslations，调用 `update_locale()`。

### update_locale(locale_)

切换locale：
- locale非en时，尝试import `jupyterlab_language_pack_{locale_}` 模块
- 使用 `gettext.translation()` 加载翻译文件（fallback=True，缺失时返回原文）

### 翻译方法

| 方法 | 简写 | 说明 |
|------|------|------|
| `gettext(msgid)` | `__()` | 单数翻译 |
| `ngettext(msgid, msgid_plural, n)` | `_n()` | 复数翻译 |
| `pgettext(msgctxt, msgid)` | `_p()` | 带上下文的单数翻译 |
| `npgettext(msgctxt, msgid, msgid_plural, n)` | `_np()` | 带上下文的复数翻译 |

Python 3.7及以下版本pgettext/npgettext回退到gettext/ngettext。

## translator 类（全局管理器）

```python
class translator:
```

静态翻译管理器，维护domain→TranslationBundle缓存和全局locale。

### 类属性

- `_TRANSLATORS: dict[str, TranslationBundle]`：domain到bundle的缓存
- `_LOCALE = SYS_LOCALE`：当前全局locale

### 静态/类方法

#### normalize_domain(domain)

```python
@staticmethod
def normalize_domain(domain: str) -> str:
```

将domain中的 `-` 替换为 `_`（gettext domain规范）。

#### set_locale(locale_)

```python
@classmethod
def set_locale(cls, locale_: str) -> None:
```

设置全局locale，更新所有已缓存的TranslationBundle。locale不变时快速返回。

#### load(domain)

```python
@classmethod
def load(cls, domain: str) -> TranslationBundle:
```

加载/获取TranslationBundle（带缓存）。domain自动规范化。

#### translate_schema(schema)

```python
@staticmethod
def translate_schema(schema: dict) -> dict:
```

翻译JSON Schema：
1. locale为en时直接返回原schema
2. 加载schema指定domain的TranslationBundle（默认"jupyterlab"）
3. 递归遍历schema，对匹配DEFAULT_SCHEMA_SELECTORS中路径模式的字符串值调用pgettext翻译
4. 返回翻译后的schema副本

#### _translate_schema_strings(translations, schema, prefix, to_translate)

递归遍历schema字典/列表，按路径正则匹配翻译字符串值。

## TranslationsHandler 类

```python
class TranslationsHandler(SchemaHandler):
```

翻译REST API处理器，继承SchemaHandler。

### GET /lab/api/translations/ 或 /lab/api/translations/{locale}

```python
@tornado.web.authenticated
async def get(self, locale: str | None = None) -> None:
```

- 无locale：返回所有已安装语言包列表
- locale="default"：映射到SYS_LOCALE
- 有locale：返回该locale的翻译数据
- 语言包有效且安装成功时，调用 `translator.set_locale(locale)` 更新全局locale
- 使用 `IOLoop.run_in_executor` 在executor中执行阻塞IO操作
- 返回 `{"data": {...}, "message": "..."}`

[F-205]
