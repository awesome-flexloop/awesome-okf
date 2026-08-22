---
type: Reference
title: 常量与配置映射
description: jupyterlab-translate常量定义（constants.py）和Babel提取配置（pybabel_config.cfg）
tags: [constants, configuration, babel, gettext, pybabel]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: constants-config
    resource: /references/constants-config.md
    title: constants.py 和 pybabel_config.cfg 源码
---

# 常量与配置映射

本文档记录 `jupyterlab_translate/constants.py` 中的常量定义和 `jupyterlab_translate/pybabel_config.cfg` 中的Babel提取配置。

## 路径常量

| 常量 | 值 | 源码行 | 说明 |
|------|-----|--------|------|
| `TEMPLATE_URL` | `"https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter"` | 第11行 | 语言包cookiecutter模板URL |
| `TEMPLATE_REF` | `"master"` | 第12行 | 模板Git引用 |
| `EXTENSIONS_FOLDER` | `"extensions"` | 第13行 | 扩展目录名 |
| `JUPYTERLAB` | `"jupyterlab"` | 第14行 | JupyterLab核心项目标识 |
| `LANG_PACKS_FOLDER` | `"language-packs"` | 第15行 | 语言包输出目录名 |
| `LC_MESSAGES` | `"LC_MESSAGES"` | 第16行 | gettext标准消息目录名 |
| `LOCALE_FOLDER` | `"locale"` | 第17行 | locale目录名 |
| `TRANSLATIONS_FOLDER` | `"translations"` | 第18行 | 翻译目录名 |

## GETTEXT_CONFIG配置

GETTEXT_CONFIG是传给gettext-extract（JS端）的配置字典：

```python
GETTEXT_CONFIG = {
    "js": {
        "parsers": __build_parsers(),  # 由__build_parsers()动态生成
        "glob": {
            "pattern": "**/*.ts*(x)",
            "options": {
                "ignore": "{examples/**/*.ts*(x),**/*.spec.ts,node_modules/**/*.ts*(x)}"
            },
        },
        "comments": {"otherLineLeading": True},
    },
    "headers": {"Language": ""},
    "output": None,
}
```

### JS翻译函数解析器

`__build_parsers()` 动态生成40个解析器配置，由5个调用根×8个翻译函数组合而成：

**调用根（roots）**：
- `trans`
- `this.trans`
- `this._trans`
- `this.props.trans`
- `props.trans`

**翻译函数（functions）**：

| 函数 | 参数映射 | gettext等价 | 说明 |
|------|---------|------------|------|
| `__` | `{text: 0}` | gettext | 简单翻译 |
| `gettext` | `{text: 0}` | gettext | 标准gettext |
| `_n` | `{text: 0, textPlural: 1}` | ngettext | 复数翻译 |
| `ngettext` | `{text: 0, textPlural: 1}` | ngettext | 标准ngettext |
| `_p` | `{context: 0, text: 1}` | pgettext | 带上下文翻译 |
| `pgettext` | `{context: 0, text: 1}` | pgettext | 标准pgettext |
| `_np` | `{context: 0, text: 1, textPlural: 2}` | npgettext | 带上下文复数翻译 |
| `npgettext` | `{context: 0, text: 1, textPlural: 2}` | npgettext | 标准npgettext |

每个解析器的expression格式为 `{root}.{function}`，例如 `trans.__`, `this.trans.gettext` 等。

## pybabel_config.cfg

Babel Python字符串提取配置文件：

```ini
[python: **.py]
extract_messages = trans.gettext, trans.pgettext, trans.ngettext, trans.npgettext, trans.__, trans._p, trans._n, trans._np
```

此配置告诉pybabel从Python文件中提取以下函数调用中的字符串：
- `trans.gettext` / `trans.__`
- `trans.pgettext` / `trans._p`
- `trans.ngettext` / `trans._n`
- `trans.npgettext` / `trans._np`

## 相关概念

- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [Schema国际化选择器](/concepts/09-schema-i18n-selectors.md)
- [核心工具源码映射](/references/utils-source.md)
