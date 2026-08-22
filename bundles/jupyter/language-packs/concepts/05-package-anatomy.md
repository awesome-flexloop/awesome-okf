---
type: Concept
title: "语言包结构剖析"
description: "单个语言包的目录结构、pyproject.toml配置、hatchling构建规则、entry-points注册机制详解"
tags: [jupyterlab, language-pack, pyproject, hatchling, entry-points, packaging, wheel]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: package-structure, resource: /references/package-structure-source.md, title: "语言包结构信源" }
  - { id: requirements, resource: /references/requirements-source.md, title: "Python 依赖信源" }
---

# 语言包结构剖析

每个语言包是一个独立的 Python 包，使用 hatchling 构建系统，通过 entry-points 向 JupyterLab 注册翻译。语言包是**纯数据包**——不含任何 Python 逻辑，仅由翻译文件和最小包元数据构成。

## 目录结构

以中文简体语言包为例：

```
jupyterlab-language-pack-zh-CN/
├── .copier-answers.yml              # Copier 模板配置记录
├── CONTRIBUTORS.md                  # 自动生成的贡献者列表
├── LICENSE.txt                      # BSD-3-Clause 许可证
├── README.md                        # 安装说明
├── pyproject.toml                   # 包构建配置
└── jupyterlab_language_pack_zh_CN/  # Python 包目录
    ├── __init__.py                  # 仅含 __version__ = "X.Y.postZ"
    └── locale/
        └── zh_CN/
            └── LC_MESSAGES/
                ├── dask_labextension.po
                ├── jupyter_archive.po
                ├── jupyter_collaboration.po
                ├── jupyter_resource_usage.po
                ├── jupyterlab.po
                ├── jupyterlab_git.po
                ├── jupyterlab_lsp.po
                ├── jupyterlab_recents.po
                ├── jupyterlab_search_replace.po
                ├── jupyterlab_spreadsheet_editor.po
                ├── jupyterlab_tour.po
                ├── jupyterlab_widgets.po
                ├── jupytext.po
                ├── nbdime.po
                ├── notebook.po
                ├── spellchecker.po
                ├── *.mo  (构建时生成，不纳入Git)
                └── *.json (构建时生成，不纳入Git)
```

## pyproject.toml 详解

### 构建系统

```toml
[build-system]
requires = ["hatchling>=1.4.0"]
build-backend = "hatchling.build"
```

使用 [hatchling](https://hatch.pypa.io/latest/) 作为 PEP 517 构建后端。

### 项目元数据

```toml
[project]
name = "jupyterlab-language-pack-zh-CN"
description = "JupyterLab Chinese (Simplified, China) Language Pack"
authors = [{ name = "Project Jupyter Contributors", email = "jupyter@googlegroups.com" }]
license = { file = "LICENSE.txt" }
readme = "README.md"
classifiers = [
    "Framework :: Jupyter",
    "Framework :: Jupyter :: JupyterLab",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
]
keywords = ["jupyterlab", "language", "language pack", "localization"]
dynamic = ["version"]
```

- `dynamic = ["version"]`：版本号不从 pyproject.toml 静态读取，而是从 `__init__.py` 动态获取

### Entry Point 注册（关键）

```toml
[project.entry-points."jupyterlab.languagepack"]
zh_CN = "jupyterlab_language_pack_zh_CN"
```

这是语言包被 JupyterLab 发现的核心机制：

1. JupyterLab 启动时扫描 `jupyterlab.languagepack` entry point 组
2. entry point 名称是 locale 代码（下划线格式，如 `zh_CN`）
3. entry point 值是 Python 包的导入路径
4. JupyterLab 根据 entry point 加载对应包，查找 locale 目录下的翻译文件
5. 用户选择语言时，JupyterLab 加载对应 .mo/.json 文件替换界面字符串

### 构建配置

```toml
[tool.hatch.build]
artifacts = ["CONTRIBUTORS.md"]

[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate>=1.2.0"]

[tool.hatch.build.targets.wheel]
artifacts = [
    "jupyterlab_language_pack_zh_CN/**/*.json",
    "jupyterlab_language_pack_zh_CN/**/*.mo",
]
exclude = [
    "jupyterlab_language_pack_zh_CN/**/*.po",
]
```

构建行为：
1. **jupyter-translate build hook**：构建时自动将 .po 文件编译为 .mo（gettext 二进制）和 .json 格式
2. **wheel 包含**：编译后的 .mo 和 .json 文件（运行时需要）
3. **wheel 排除**：.po 源文件（减小包体积，运行时不需要）
4. **额外文件**：CONTRIBUTORS.md 包含在 wheel 中

### 版本源

```toml
[tool.hatch.version]
path = "jupyterlab_language_pack_zh_CN/__init__.py"
```

hatch 从 `__init__.py` 中的 `__version__` 变量读取版本号。

## __init__.py

```python
__version__ = "4.5.post3"
```

整个包唯一的 Python 代码，仅声明版本号。版本格式为 `X.Y.postZ`：
- `X.Y`：对应 JupyterLab 主版本（如 4.5）
- `postZ`：翻译修订号（如 post3），每次翻译更新递增

## .copier-answers.yml

```yaml
_commit: v1.1.3
_src_path: https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter
language: Chinese (Simplified, China)
locale: zh-CN
version: 4.0.post0
```

记录语言包是如何通过 [Copier](https://copier.readthedocs.io/) 模板从 [jupyterlab-language-pack-cookiecutter](https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter) 生成的。发布时 `03_prepare_release.py` 使用 `copier update` 更新模板。

## README.md

每个语言包的 README 自动生成，包含：
- 语言名称
- pip 安装命令
- conda 安装命令
- Crowdin 贡献链接

## 命名约定

| 元素 | 格式 | 示例 |
|------|------|------|
| 目录名/PyPI包名 | `jupyterlab-language-pack-{ll-CC}` | `jupyterlab-language-pack-zh-CN` |
| Python 包名 | `jupyterlab_language_pack_{ll_CC}` | `jupyterlab_language_pack_zh_CN` |
| locale 目录 | `{ll_CC}` | `zh_CN` |
| entry-point 名 | `{ll_CC}` | `zh_CN` |
| .po 文件名 | `{domain}.po` | `jupyterlab.po` |

其中 `ll` 是 ISO 639-1 语言码（小写），`CC` 是 ISO 3166-1 国家码（大写），目录/PyPI名用连字符，Python包/entry-point用下划线。

## Wheel 构建产物

构建后 wheel 包含：
- `*.dist-info/`：标准包元数据（METADATA、WHEEL、entry_points.txt等）
- `jupyterlab_language_pack_zh_CN/__init__.py`
- `jupyterlab_language_pack_zh_CN/locale/zh_CN/LC_MESSAGES/*.mo`：编译后的 gettext 二进制
- `jupyterlab_language_pack_zh_CN/locale/zh_CN/LC_MESSAGES/*.json`：JSON 格式翻译
- `CONTRIBUTORS.md`

## 相关概念

- [Entry Point 语言包发现机制](10-entry-point-discovery.md)
- [Gettext 国际化基础](06-gettext-i18n.md)
- [版本管理策略](11-version-management.md)
- [安装语言包](../examples/01-install-language-pack.md)
