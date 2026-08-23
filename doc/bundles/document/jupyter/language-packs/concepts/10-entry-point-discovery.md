---
type: Concept
title: "Entry Point 语言包发现机制"
description: "JupyterLab 通过 Python entry-points（jupyterlab.languagepack 组）自动发现并加载已安装语言包的工作原理"
tags: [jupyterlab, language-pack, entry-points, plugin, discovery, importlib]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: package-structure, resource: /references/package-structure-source.md, title: "语言包结构信源" }
---

# Entry Point 语言包发现机制

JupyterLab 语言包的自动发现依赖 Python 的 [Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/) 机制。这是 Python 生态中广泛使用的插件发现方案，语言包通过声明 `jupyterlab.languagepack` entry point 组，让 JupyterLab 启动时能自动找到所有已安装的语言包。

## 什么是 Entry Point

Entry Point 是 Python 包在安装时向环境注册的"广告位"，允许包声明："我提供了某个类型的插件，可以在这个名字下被找到"。与直接 import 不同，entry point 实现了：

- **松耦合**：JupyterLab 不需要 `import` 每个语言包，不需要知道它们的存在
- **自动发现**：安装即注册，卸载即注销
- **命名分组**：不同类型的插件使用不同的组名（group）

## 语言包的 Entry Point 注册

每个语言包在 `pyproject.toml` 中声明：

```toml
[project.entry-points."jupyterlab.languagepack"]
zh_CN = "jupyterlab_language_pack_zh_CN"
fr_FR = "jupyterlab_language_pack_fr_FR"
ja_JP = "jupyterlab_language_pack_ja_JP"
```

各字段含义：

| 部分 | 含义 | 示例 |
|------|------|------|
| **Group** | Entry point 组名，JupyterLab查找的命名空间 | `jupyterlab.languagepack` |
| **Name** | Entry point 名称，即locale代码（下划线格式） | `zh_CN` |
| **Value** | Python 包的导入路径 | `jupyterlab_language_pack_zh_CN` |

### 安装后的注册

安装语言包后，entry point 信息写入环境的 `.dist-info/entry_points.txt`：

```ini
[jupyterlab.languagepack]
zh_CN = jupyterlab_language_pack_zh_CN
fr_FR = jupyterlab_language_pack_fr_FR
```

## JupyterLab 发现语言包的过程

JupyterLab 启动时大致执行以下逻辑：

```python
from importlib.metadata import entry_points

# 1. 查找 jupyterlab.languagepack 组的所有 entry points
lang_pack_eps = entry_points(group="jupyterlab.languagepack")

# 2. 构建 locale -> 包路径 映射
available_languages = {}
for ep in lang_pack_eps:
    locale = ep.name          # "zh_CN"
    package_name = ep.value   # "jupyterlab_language_pack_zh_CN"
    available_languages[locale] = package_name

# 3. 根据用户语言设置加载对应包
#    （用户在 Settings → Language 中选择，或通过 LANG 环境变量）
user_locale = get_user_language_preference()  # e.g. "zh_CN"
if user_locale in available_languages:
    package = importlib.import_module(available_languages[user_locale])
    # 加载 package/locale/{locale}/LC_MESSAGES/ 下的 .mo/.json 文件
    load_translations(package)
```

### 关键 API：importlib.metadata

Python 3.8+ 标准库提供：

```python
from importlib.metadata import entry_points

# 查询特定组的 entry points（Python 3.10+）
eps = entry_points(group="jupyterlab.languagepack")

# Python 3.8-3.9 兼容写法
eps = entry_points().get("jupyterlab.languagepack", [])
```

返回的 EntryPoint 对象有属性：
- `.name`：entry point 名称（locale代码）
- `.value`：模块/对象路径
- `.group`：组名
- `.load()`：加载并返回对应的模块或对象

## 语言选择优先级

JupyterLab 选择语言的优先级（从高到低）：

1. **用户显式设置**：Settings → Language 选择的语言
2. **命令行参数**：`--Language=` 参数
3. **Jupyter 配置文件**：`c.LanguageManager.preferred_language`
4. **环境变量**：`LANG`/`LC_ALL`（如 `zh_CN.UTF-8`）
5. **默认**：英语（`en`）

## 语言代码映射

语言包使用 POSIX locale 格式 `ll_CC`（语言_国家），但浏览器和系统可能提供 BCP 47 格式（`ll-CC` 或 `ll`）：

| 格式 | 示例 | 使用场景 |
|------|------|---------|
| POSIX locale | `zh_CN`、`fr_FR` | Entry point 名称、PO/MO 目录名 |
| BCP 47 | `zh-CN`、`fr-FR` | HTTP Accept-Language、浏览器语言设置 |
| ISO 639-1 | `zh`、`fr` | 语言代码简写 |

JupyterLab 内部会做格式转换（下划线↔连字符）以匹配。

## 为什么语言包是"空包"？

注意 `__init__.py` 只有一行：
```python
__version__ = "4.5.post3"
```

这是因为：
1. Entry point 的 value 只需要是一个**可导入的包名**，包不需要导出任何特定函数/类
2. JupyterLab 加载包后，通过包的 `__file__` 路径定位 locale 目录
3. 翻译文件是数据文件，不需要 Python 代码逻辑
4. 包的存在本身就标记了"该语言可用"

这是一种极简的插件设计模式——entry point 注册 + 包路径定位数据文件。

## 多语言包共存

用户可以同时安装多个语言包：

```bash
pip install jupyterlab-language-pack-zh-CN \
            jupyterlab-language-pack-ja-JP \
            jupyterlab-language-pack-fr-FR
```

所有语言包都会注册到 `jupyterlab.languagepack` 组，JupyterLab 在设置界面中提供语言下拉菜单让用户切换。

## 自定义扩展注册语言包

如果第三方扩展想要有自己的翻译，也可以：
1. 在自己的 pyproject.toml 中声明 entry point
2. 将 .mo/.json 文件打包到自己的包中
3. JupyterLab 会自动发现并合并翻译

但 language-packs 仓库的模式是将所有扩展的翻译集中管理，这样译者可以在一个 Crowdin 项目中翻译所有扩展。

## 手动列出已安装语言包

用户可以通过以下命令查看已安装的语言包：

```bash
# 列出所有 jupyterlab.languagepack entry points
pip show jupyterlab-language-pack-zh-CN

# 或用 Python
python -c "
from importlib.metadata import entry_points
for ep in entry_points(group='jupyterlab.languagepack'):
    print(f'{ep.name}: {ep.value}')
"
```

## 相关概念

- [语言包结构剖析](05-package-anatomy.md)
- [Gettext 国际化基础](06-gettext-i18n.md)
- [安装语言包](../examples/01-install-language-pack.md)
