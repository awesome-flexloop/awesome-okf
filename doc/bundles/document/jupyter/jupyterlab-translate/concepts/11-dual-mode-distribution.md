---
type: Concept
title: 双模式分发机制
description: jupyterlab-translate支持两种翻译分发模式：独立扩展包自带翻译和集中式语言包仓库，两种模式共享核心提取/编译逻辑但目录结构不同
tags: [distribution, dual-mode, extension, language-pack, packaging, directory-structure]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: api-source
    resource: /references/api-source.md
    title: API层源码映射
  - id: finder-source
    resource: /references/finder-source.md
    title: 运行时发现模块源码映射
---

# 双模式分发机制

jupyterlab-translate 支持两种翻译分发模式，以适应不同的使用场景。两种模式共享核心的字符串提取和翻译编译逻辑，但在输出目录结构、CLI命令和打包方式上有所区别。

## 模式一：独立扩展包模式

扩展包自身包含翻译文件，用户安装扩展时翻译文件随包一起安装。

### 适用场景

- 你是扩展作者，希望扩展开箱即用地支持多语言
- 翻译文件数量较少，不希望依赖外部语言包
- 希望翻译更新与扩展发布同步

### CLI命令

```bash
jupyterlab-translate extract <ext-dir> <project>
jupyterlab-translate update <ext-dir> <project> -l <locale>
jupyterlab-translate compile <ext-dir> <project> -l <locale>
```

### 目录结构

```
my-extension/
├── pyproject.toml          # 包含jupyterlab.locale entry point
├── my_extension/           # Python包
│   ├── __init__.py
│   └── locale/             # 翻译文件在包内
│       ├── my_extension.pot
│       ├── zh_CN/
│       │   └── LC_MESSAGES/
│       │       ├── my_extension.po
│       │       ├── my_extension.mo
│       │       └── my_extension.json
│       └── es_ES/
│           └── LC_MESSAGES/
│               └── ...
└── src/                    # TypeScript源码
```

### Entry Point配置

扩展包需要在pyproject.toml中注册 `jupyterlab.locale` entry point：

```toml
[project.entry-points."jupyterlab.locale"]
my-extension = "my_extension"
```

### 打包配置

wheel中需要包含.json和.mo文件，排除.po文件：

```toml
[tool.hatch.build.targets.wheel]
artifacts = [
    "my_extension/**/*.json",
    "my_extension/**/*.mo",
]
exclude = [
    "my_extension/**/*.po",
]
```

### 运行时发现

JupyterLab启动时通过 `jupyterlab.locale` entry point发现扩展自带的翻译，加载对应的JSON文件。

## 模式二：集中语言包模式

所有翻译集中在[language-packs](https://github.com/jupyterlab/language-packs)仓库管理，每个语言作为独立的pip包发布。用户安装语言包后获得所有扩展的翻译。

### 适用场景

- 你是语言包维护者，为JupyterLab生态维护某一语言的翻译
- 翻译由社区贡献者在Crowdin上协作完成
- 希望翻译更新独立于各个扩展的发布周期

### CLI命令

```bash
jupyterlab-translate extract-pack <ext-dir> <packs-dir> <project>
jupyterlab-translate update-pack <ext-dir> <packs-dir> <project> -l <locale>
jupyterlab-translate compile-pack <packs-dir> <project> -l <locale>
```

### 目录结构

```
language-packs/
├── jupyterlab/                      # JupyterLab核心POT/PO
│   └── locale/
│       ├── jupyterlab.pot
│       └── <locale>/LC_MESSAGES/jupyterlab.po
├── extensions/                      # 扩展POT（extract时）
│   └── <project>/locale/<project>.pot
├── jupyterlab_extensions/           # 扩展PO（update时）
│   └── <project>/locale/<locale>/LC_MESSAGES/<project>.po
└── language-packs/                  # 编译后语言包
    └── jupyterlab-language-pack-zh-CN/
        ├── CONTRIBUTORS.md
        └── jupyterlab_language_pack_zh_CN/
            ├── __init__.py
            └── locale/zh_CN/LC_MESSAGES/
                ├── jupyterlab.json
                ├── jupyterlab.mo
                ├── <ext>.json
                └── <ext>.mo
```

### 输出目录差异

在语言包模式下，extract和update的输出目录有细微差别：

| 操作 | JupyterLab核心 | 第三方扩展 |
|------|---------------|-----------|
| extract | `<packs>/jupyterlab/locale/` | `<packs>/extensions/<project>/locale/` |
| update | `<packs>/jupyterlab/locale/` | `<packs>/jupyterlab_extensions/<project>/locale/` |
| compile | 移动到 `language-packs/` 下 | 移动到 `language-packs/` 下 |

> 注意extract和update对扩展使用不同的目录名（`extensions` vs `jupyterlab_extensions`）。

### Entry Point配置

语言包通过 `jupyterlab.languagepack` entry point注册：

```toml
[project.entry-points."jupyterlab.languagepack"]
zh_CN = "jupyterlab_language_pack_zh_CN"
```

### 语言包创建

`compile_language_pack()` 在编译时，如果目标语言包目录不存在，会自动通过copier从cookiecutter模板创建：

- **模板URL**：`https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter`
- **模板引用**：`master` 分支
- **模板数据**：locale（短横线格式）、language（英文语言名）、version

### 运行时发现

JupyterLab启动时通过 `jupyterlab.languagepack` entry point发现已安装的语言包，加载对应语言的Jed JSON数据。

## 两种模式对比

| 特性 | 独立扩展包 | 集中语言包 |
|------|----------|-----------|
| CLI命令 | extract/update/compile | extract-pack/update-pack/compile-pack |
| Entry point | `jupyterlab.locale` | `jupyterlab.languagepack` |
| 翻译位置 | 扩展包内locale/目录 | 独立的jupyterlab-language-pack-xx包 |
| 安装方式 | 随扩展自动安装 | 用户单独pip install |
| 维护者 | 扩展作者 | 语言包社区/Crowdin |
| 翻译更新 | 随扩展版本发布 | 独立发布，更新更灵活 |
| 适用规模 | 单扩展，少量语言 | 全生态，多语言 |
| Hatch Hook | 可选 | 标准配置 |
| compile后文件移动 | 不移动，留在原地 | 移动到language-packs/目录 |

## 项目名规范化

两种模式都使用 `normalize_project()` 函数规范化项目名：

```python
def normalize_project(project: str) -> str:
    return project.lower().replace("-", "_")
```

例如：`JupyterLab-Git` → `jupyterlab_git`

规范化后的名称用于：
- locale目录名
- POT/PO/MO/JSON文件名
- Python包名

## Locale格式约定

在整个工具中，locale代码使用**下划线格式**（如 `zh_CN`、`pt_BR`），这是gettext和Babel的标准。但在以下场景会转换为**短横线格式**（如 `zh-CN`、`pt-BR`）：

- Jed JSON中的language字段
- pip包名（`jupyterlab-language-pack-zh-CN`）
- Crowdin API调用参数

转换由各处的 `.replace("_", "-")` 处理。

## 相关概念

- [快速开始](01-getting-started.md)
- [CLI命令参考](03-cli-commands.md)
- [翻译目录管理](05-catalog-management.md)
- [Hatch构建钩子集成](07-hatch-build-hook.md)
- [运行时语言包发现](08-runtime-discovery.md)
- [语言包工作流示例](../examples/02-language-pack-workflow.md)
