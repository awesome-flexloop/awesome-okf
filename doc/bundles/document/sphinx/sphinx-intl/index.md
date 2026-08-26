---
okf_version: "0.2"
type: "index"
title: "sphinx-intl 教程"
description: "sphinx-intl 源码学习教程——Sphinx 文档国际化翻译工具的系统化知识，从 CLI 使用到内部实现"
tags: [sphinx-intl, i18n, translation, gettext, sphinx, localization]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:55:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: commands-api, resource: "/references/commands-api.md", title: "CLI 入口 API 参考" }
  - { id: basic-api, resource: "/references/basic-api.md", title: "核心业务逻辑 API 参考" }
  - { id: catalog-api, resource: "/references/catalog-api.md", title: "Catalog 文件操作 API 参考" }
  - { id: transifex-api, resource: "/references/transifex-api.md", title: "Transifex 集成 API 参考" }
  - { id: official-docs, resource: "https://sphinx-intl.readthedocs.io", title: "sphinx-intl 官方文档" }
---

# sphinx-intl 教程

> 基于 sphinx-intl 源码（BSD-2-Clause）+ 官方文档的系统化学习教程

sphinx-intl 是 Sphinx 文档生态的国际化（i18n）翻译辅助工具，提供从 POT 模板生成、PO 文件更新维护、到 MO 编译的完整命令行工具链，并可选集成 Transifex 云端翻译协作平台。本教程从源码出发系统讲解 sphinx-intl 的 CLI 架构、核心实现与使用方法。

## 快速导航

### 入门

| 文档 | 说明 |
|------|------|
| [sphinx-intl 简介](concepts/00-introduction.md) | 是什么、核心能力、项目信息、代码结构概览 |
| [5分钟快速上手](concepts/01-getting-started.md) | 安装、配置、基本翻译流程（7步完成） |
| [CLI 命令体系详解](concepts/02-cli-commands.md) | Click 架构、6 个子命令、选项、自动配置检测 |

### 核心原理（源码视角）

| 文档 | 说明 |
|------|------|
| [翻译工作流原理](concepts/03-translation-workflow.md) | POT→PO→MO 三阶段生命周期、LC_MESSAGES 约定、文件路径映射 |
| [目录文件操作：Catalog 模块](concepts/04-catalog-operations.md) | Babel 封装、两阶段 charset 探测、条目过滤、fuzzy 合并 |
| [更新机制：多进程合并与 Fuzzy](concepts/05-update-mechanism.md) | multiprocessing 并行、UpdateItem/UpdateResult 数据类、增量判断 |
| [编译与统计机制](concepts/06-build-stat-mechanism.md) | MO 增量编译（mtime）、translated/fuzzy/untranslated 统计 |

### 高级主题（源码视角）

| 文档 | 说明 |
|------|------|
| [Transifex 平台集成](concepts/07-transifex-integration.md) | CLI 检测、资源名规范化、tx config 自动配置、协作工作流 |
| [配置读取与 Python 兼容层](concepts/08-config-and-compat.md) | conf.py 执行机制、Tags 类、Python 2→3 降级、自动检测流程 |

### 实战示例

| 示例 | 说明 |
|------|------|
| [基本翻译全流程](examples/basic-translation.md) | 从零开始添加多语言支持的完整教程（含日常更新、Makefile 集成） |
| [Transifex 协作翻译](examples/transifex-collaboration.md) | 多人云端协作翻译配置与工作流（含 CI/CD 集成） |

### 信源登记簿

* [信源索引](references/index.md) — 源码 API 签名、常量定义、函数参数速查

## 学习路径建议

**使用者路径（给文档做翻译）**：
```
00 → 01 → examples/basic-translation → 02（CLI参考）→ examples/transifex-collaboration（团队协作时）
```

**源码/开发者路径（理解实现）**：
```
00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08
```

**团队协作路径（多人翻译）**：
```
00 → 01 → examples/basic-translation → examples/transifex-collaboration → 07
```

## 源码版本

本教程基于 sphinx-intl 源码（随 Sphinx 主仓库在 `external/libs/docs/sphinx-intl/`），核心依赖：

- 许可证：BSD-2-Clause
- Python 要求：≥ 3.9
- 核心依赖：click ≥ 8.0.0、Babel ≥ 2.9.0、Sphinx
- 可选依赖：Transifex CLI ≥ 1.2.1（云端协作功能）
- 构建系统：setuptools + setuptools_scm
- CLI 入口：`sphinx-intl` → `sphinx_intl.commands:main`
- 代码规模：7 个 Python 文件，约 600 行核心代码

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
