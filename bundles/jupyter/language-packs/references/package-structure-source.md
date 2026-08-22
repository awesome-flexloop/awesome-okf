---
type: Reference
title: "语言包结构信源"
description: "单个语言包的目录结构、pyproject.toml 配置、entry-points 注册机制与构建产物规则"
tags: [jupyterlab, language-pack, pyproject, hatchling, entry-points, packaging]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: package-source
    resource: https://github.com/jupyterlab/language-packs/tree/master/language-packs
    title: "language-packs directory"
---

# 语言包结构信源

## 源码路径

以 `language-packs/jupyterlab-language-pack-zh-CN/` 为例。

## 单语言包目录结构

```
jupyterlab-language-pack-{locale}/
├── .copier-answers.yml          # Copier 模板回答记录
├── CONTRIBUTORS.md              # 贡献者列表（自动生成）
├── LICENSE.txt                  # BSD-3-Clause 许可证
├── README.md                    # 安装说明
├── pyproject.toml               # 包配置（hatchling 构建）
└── jupyterlab_language_pack_{locale_snake}/
    ├── __init__.py              # 仅含 __version__
    └── locale/
        └── {locale_snake}/
            └── LC_MESSAGES/
                ├── *.po         # 翻译源文件（git 跟踪）
                ├── *.mo         # 编译后的二进制（构建生成）
                └── *.json       # JSON 格式翻译（构建生成）
```

## pyproject.toml 配置详解

### 构建系统

```toml
[build-system]
requires = ["hatchling>=1.4.0"]
build-backend = "hatchling.build"
```

使用 hatchling 作为构建后端。

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
dynamic = ["version"]  # 版本从 __init__.py 动态读取
```

### Entry Point 注册

```toml
[project.entry-points."jupyterlab.languagepack"]
zh_CN = "jupyterlab_language_pack_zh_CN"
```

**关键机制**：JupyterLab 通过 `jupyterlab.languagepack` entry point 发现语言包。entry point 名称是 locale（下划线格式），值是 Python 包名。

### Hatch 构建配置

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

[tool.hatch.version]
path = "jupyterlab_language_pack_zh_CN/__init__.py"
```

构建规则：
- wheel 包含 `.mo`（编译后的 gettext 二进制）和 `.json` 文件
- wheel 排除 `.po` 源文件（减少包体积）
- `jupyter-translate` build hook 在构建时编译 .po → .mo/.json
- CONTRIBUTORS.md 作为额外文件打包

## __init__.py

```python
__version__ = "4.5.post3"
```

仅包含版本号一行，hatch 从此文件读取版本。

## .copier-answers.yml

```yaml
_commit: v1.1.3
_src_path: https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter
language: Chinese (Simplified, China)
locale: zh-CN
version: 4.0.post0
```

记录 Copier 模板来源、提交哈希、语言名称和初始版本。

## 命名规则

| 元素 | 格式 | 示例 |
|------|------|------|
| 目录/PyPI包名 | kebab-case locale | `jupyterlab-language-pack-zh-CN` |
| Python 包名 | snake_case locale | `jupyterlab_language_pack_zh_CN` |
| locale 目录名 | snake_case | `zh_CN` |
| entry-point 名 | snake_case | `zh_CN` |

## LC_MESSAGES 内容

每个语言包的 LC_MESSAGES 目录包含对应扩展的 .po 文件：
- dask_labextension.po
- jupyter_archive.po
- jupyter_collaboration.po
- jupyter_resource_usage.po
- jupyterlab.po
- jupyterlab_git.po
- jupyterlab_lsp.po
- jupyterlab_recents.po
- jupyterlab_search_replace.po
- jupyterlab_spreadsheet_editor.po
- jupyterlab_tour.po
- jupyterlab_widgets.po
- jupytext.po
- nbdime.po
- notebook.po
- spellchecker.po

部分包还包含 retrolab.po（已废弃扩展，部分语言仍保留）。
