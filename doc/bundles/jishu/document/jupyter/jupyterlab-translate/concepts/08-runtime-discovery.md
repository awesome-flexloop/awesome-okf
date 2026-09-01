---
type: Concept
title: 运行时语言包发现
description: JupyterLab通过Python entry points机制在运行时发现已安装的语言包和扩展翻译数据
tags: [runtime, discovery, entry-points, finder, language-pack, locale, installed]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: finder-source
    resource: /references/finder-source.md
    title: 运行时发现模块源码映射
---

# 运行时语言包发现

JupyterLab在运行时通过Python entry points机制发现已安装的语言包和第三方扩展自带的翻译数据。`finder.py` 模块提供了这一发现机制的实现。

## Entry Point 机制

Python的entry points是一种插件发现机制，包可以在安装时向特定group注册对象，其他包可以在运行时发现并加载这些对象。jupyterlab-translate定义了两个entry point group。

### jupyterlab.languagepack

用于发现**集中式语言包**。每个语言包（如中文、韩语、西班牙语包）通过这个group注册自己：

```toml
[project.entry-points."jupyterlab.languagepack"]
zh_CN = "jupyterlab_language_pack_zh_CN"
ko_KR = "jupyterlab_language_pack_ko_KR"
es_ES = "jupyterlab_language_pack_es_ES"
```

entry point的name是locale代码，value是语言包Python模块路径。加载后，该模块应提供Jed格式的翻译数据。

### jupyterlab.locale

用于发现**第三方扩展自带的locale数据**。扩展可以选择不依赖集中语言包，而是在自身包中包含翻译文件：

```toml
[project.entry-points."jupyterlab.locale"]
jupyterlab-git = "jupyterlab_git"
my-extension = "my_extension"
```

entry point的name是包名（`-`会被转为`_`并小写），value是扩展的Python模块路径。模块目录下需要包含 `locale/<locale>/LC_MESSAGES/<name>.json` 文件。

## finder.py API

### get_installed_language_packs()

返回所有已安装语言包的名称列表。

```python
from jupyterlab_translate import get_installed_language_packs

packs = get_installed_language_packs()
# 返回: ["zh_CN", "ko_KR", "es_ES", ...]
```

**实现：**
- 遍历 `jupyterlab.languagepack` group的所有entry points
- 返回每个entry point的name（即locale代码）列表

### get_language_pack(locale)

获取指定locale的语言包数据（Jed格式dict）。

```python
from jupyterlab_translate import get_language_pack

data = get_language_pack("zh_CN")
# 返回: {"": {"domain": ..., "language": ..., ...}, "key": ["translation"], ...}
# 如果locale无效或未安装，返回 {}
```

**实现：**
1. 调用 `check_locale(locale)` 验证locale有效性
2. 遍历 `jupyterlab.languagepack` entry points
3. 如果找到匹配name的entry point，调用 `entry_point.load()` 加载模块并返回
4. 如果locale无效，打印警告并返回空dict

### get_installed_packages_locale(locale)

获取所有包含指定locale翻译数据的已安装扩展包。

```python
from jupyterlab_translate.finder import get_installed_packages_locale

data = get_installed_packages_locale("zh_CN")
# 返回: {"jupyterlab_git": {"zh_CN": <jed_json_data>}, ...}
```

**实现：**
1. 遍历 `jupyterlab.locale` group的所有entry points
2. 加载每个entry point模块，获取其 `__file__` 路径
3. 在模块目录下查找 `locale/` 子目录
4. 如果指定locale目录存在，加载对应的 `<name>.json` 文件
5. 返回 `{package_name: {locale: json_data}}` 格式的dict

### merge_data()

> **注意**：此函数当前为空实现（只有pass），语言包数据与扩展locale数据的合并逻辑尚未在此模块中实现。

## 包结构约定

### 语言包结构

集中式语言包需要遵循以下目录结构才能被正确发现：

```
jupyterlab_language_pack_<locale>/
├── __init__.py           # 提供Jed格式翻译数据（通过entry point加载）
└── locale/
    └── <locale>/
        └── LC_MESSAGES/
            ├── jupyterlab.json    # JupyterLab核心翻译
            ├── jupyterlab.mo
            ├── <extension>.json   # 扩展翻译
            └── <extension>.mo
```

包名格式为 `jupyterlab_language_pack_<locale_with_underscore>`，例如：
- `jupyterlab_language_pack_zh_CN`
- `jupyterlab_language_pack_ko_KR`
- `jupyterlab_language_pack_pt_BR`

### 扩展自带locale结构

选择自带翻译的扩展需要遵循：

```
my_extension/
├── __init__.py
└── locale/
    ├── zh_CN/
    │   └── LC_MESSAGES/
    │       └── my_extension.json
    └── es_ES/
        └── LC_MESSAGES/
            └── my_extension.json
```

JSON文件名为normalize后的包名（`-`转`_`，全小写）。

## Python版本兼容

finder.py对Python 3.10前后的 `entry_points` API差异做了兼容：

```python
import sys
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points
```

这就是为什么 `importlib-metadata>=4.8.3` 是Python < 3.10的条件依赖。

## 公开API

`__init__.py` 中从finder模块导出了两个函数作为包的公开API：

```python
from .finder import get_installed_language_packs
from .finder import get_language_pack
```

`get_installed_packages_locale` 和 `merge_data` 没有在 `__init__.py` 中导出，需要从 `jupyterlab_translate.finder` 直接导入。

## 工作流总结

语言包的运行时加载流程：

```
JupyterLab启动
    │
    ├──→ get_installed_language_packs() 发现可用语言
    │
    ├──→ 用户选择语言
    │
    ├──→ get_language_pack(locale) 加载核心语言包Jed数据
    │
    └──→ get_installed_packages_locale(locale) 加载扩展翻译
         │
         └──→ 合并所有Jed数据 → 前端i18n系统
```

## 相关概念

- [Hatch构建钩子集成](07-hatch-build-hook.md)
- [Jed JSON翻译格式](06-json-jed-format.md)
- [双模式分发机制](11-dual-mode-distribution.md)
- [运行时发现模块源码映射](../references/finder-source.md)
