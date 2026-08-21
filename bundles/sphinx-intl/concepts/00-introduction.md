---
type: concept
title: "sphinx-intl 简介"
description: "sphinx-intl 是什么——Sphinx 文档国际化翻译工具，核心能力、项目信息、与 Sphinx i18n 的关系"
tags: [introduction, overview, i18n, basics]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: commands-api
    resource: /references/commands-api.md
    title: "CLI 入口 API 参考"
  - id: basic-api
    resource: /references/basic-api.md
    title: "核心业务逻辑 API 参考"
  - id: official-docs
    resource: "https://sphinx-intl.readthedocs.io"
    title: "sphinx-intl 官方文档"
---

# sphinx-intl 简介

## 什么是 sphinx-intl

sphinx-intl 是一个 **Sphinx 国际化翻译辅助工具**（Sphinx utility that make it easy to translate and to apply translation）[F-001]。它填补了 Sphinx 内置 gettext 构建器与实际翻译工作流之间的空白，提供从 POT 模板生成、PO 文件更新维护、到 MO 编译的完整命令行工具链。

Sphinx 本身通过 `sphinx-build -b gettext` 可以从文档源文件提取可翻译消息生成 POT（Portable Object Template）文件，但从 POT 到实际翻译再到构建多语言文档之间仍需要一系列文件管理操作——sphinx-intl 正是为了简化这些操作而诞生的 [F-002]。

sphinx-intl 完全使用 Python 编写，采用 **BSD-2-Clause** 开源许可证发布 [F-003]，项目托管于 GitHub（<https://github.com/sphinx-doc/sphinx-intl>），是 sphinx-doc 官方组织下的项目。

## 项目信息

| 属性 | 值 |
|------|-----|
| 包名 | `sphinx-intl`（PyPI），导入名 `sphinx_intl` |
| 许可证 | BSD-2-Clause [F-003] |
| Python 要求 | ≥ 3.9 [F-004] |
| 核心依赖 | click ≥ 8.0.0、babel ≥ 2.9.0、sphinx [F-005] |
| CLI 入口 | `sphinx-intl` 命令 → `sphinx_intl.commands:main` [F-006] |
| 构建系统 | setuptools + setuptools_scm（动态版本号）[F-007] |
| 作者 | Takayuki SHIMIZUKAWA（shimizukawa@gmail.com）[F-008] |
| 文档 | <https://sphinx-intl.readthedocs.io> [F-009] |

## 核心能力

### 基础功能（必选）

sphinx-intl 提供两个核心翻译文件管理功能 [F-010]：

1. **create/update PO 文件**：从 POT 模板文件创建或更新指定语言的 PO（Portable Object）翻译文件
2. **build MO 文件**：将已翻译的 PO 文件编译为 MO（Machine Object）二进制文件，供 Sphinx 运行时加载

### 可选功能（需 Transifex CLI）

sphinx-intl 还集成了 [Transifex](https://www.transifex.com) 在线翻译协作平台的支持（需要额外安装 Transifex CLI 工具）[F-011]：

1. 创建 `~/.transifexrc` 认证配置（已废弃，推荐 `TX_TOKEN` 环境变量）
2. 创建 `./.tx/config` Transifex 项目配置
3. 自动更新 `.tx/config` 资源段（从 POT 文件批量注册资源）
4. 与 `tx push`/`tx pull` 命令配合实现翻译的云端协作

### 辅助功能

- **统计翻译进度**：`stat` 命令显示每个 PO 文件的 translated/fuzzy/untranslated 数量
- **多进程并行更新**：`-j` 参数支持多 CPU 并行处理 PO 文件更新
- **环境变量配置**：所有 CLI 选项均支持 `SPHINXINTL_*` 环境变量设置
- **Sphinx conf.py 集成**：自动读取 `conf.py` 中的 `locale_dirs` 配置

## sphinx-intl 在 Sphinx i18n 工作流中的位置

Sphinx 文档国际化的完整工作流涉及三个阶段，sphinx-intl 主要覆盖第 2 和第 3 阶段：

```
┌─────────────────────────────────────────────────────────┐
│ 阶段1: 提取消息 (Sphinx 内置)                            │
│   sphinx-build -b gettext → 生成 POT 文件               │
├─────────────────────────────────────────────────────────┤
│ 阶段2: 管理翻译文件 (sphinx-intl)                        │
│   sphinx-intl update → 从 POT 创建/更新 PO 文件         │
│   人工翻译 PO 文件 / Transifex 协作翻译                  │
│   sphinx-intl build → 编译 PO 为 MO                     │
├─────────────────────────────────────────────────────────┤
│ 阶段3: 构建多语言文档 (Sphinx 内置)                      │
│   sphinx-build -D language=ja → 加载 MO 生成翻译文档    │
└─────────────────────────────────────────────────────────┘
```

## 核心依赖说明

| 依赖 | 版本要求 | 作用 |
|------|---------|------|
| **click** | ≥ 8.0.0 | CLI 框架，提供命令组、选项、参数类型等 |
| **Babel** | ≥ 2.9.0 | 提供 PO/POT/MO 文件的读写能力（`babel.messages.pofile`/`mofile`）|
| **Sphinx** | 无版本下限 | 提供 `Tags` 类（在 sphinx_util.py 中本地移植了一份）和 conf.py 配置读取 |

值得注意的是，sphinx-intl 的核心文件操作完全委托给 Babel 库——`catalog.py` 模块是对 Babel `pofile`/`mofile` 的轻量封装，增加了 charset 两阶段探测和目录自动创建等便利功能。

## 代码结构概览

sphinx-intl 是一个非常精简的工具，核心代码仅 7 个 Python 文件：

```
sphinx_intl/
├── __init__.py       # 版本号获取（importlib.metadata）
├── __main__.py       # python -m sphinx_intl 入口
├── commands.py       # CLI 命令定义（click 框架）
├── basic.py          # 核心业务逻辑（update/build/stat + 多进程）
├── catalog.py        # PO/POT/MO 文件读写（Babel 封装）
├── transifex.py      # Transifex 平台集成
├── pycompat.py       # Python 兼容层（execfile、relpath、2to3）
└── sphinx_util.py    # 从 Sphinx 移植的 Tags 类
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [CLI 命令体系详解](02-cli-commands.md)
- [翻译工作流原理](03-translation-workflow.md)
