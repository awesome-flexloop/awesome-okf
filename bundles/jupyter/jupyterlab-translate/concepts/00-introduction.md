---
type: Concept
title: JupyterLab Translate 简介
description: jupyterlab-translate是JupyterLab生态的语言包翻译辅助工具，负责从源码提取字符串、生成和编译gettext翻译目录
tags: [introduction, overview, i18n, l10n, jupyterlab, gettext]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/cli-source.md
    title: README与CLI入口
  - id: pyproject
    resource: /references/constants-config.md
    title: 项目配置与依赖
---

# JupyterLab Translate 简介

jupyterlab-translate 是 JupyterLab 生态系统中用于生成[语言包（language packs）](https://github.com/jupyterlab/language-packs)的Python工具包。它为JupyterLab核心和第三方扩展提供统一的国际化（i18n）工作流，覆盖从源码字符串提取到翻译编译分发的完整流程。

## 核心功能

该工具包执行以下与JupyterLab国际化相关的常见任务：

1. **字符串提取**：从 `*.py`、`*.ts`、`*.tsx` 源码文件中提取可翻译字符串
2. **Schema提取**：从JSON Schema配置文件中提取标题、描述等可翻译字段
3. **POT目录生成**：创建gettext标准的 `*.pot`（Portable Object Template）翻译模板文件
4. **去重处理**：自动合并POT文件中的重复字符串条目
5. **PO目录创建**：为指定语言创建 `*.po`（Portable Object）翻译文件
6. **双格式编译**：将PO文件编译为 `*.mo`（Machine Object，后端使用）和 `*.json`（Jed格式，前端使用）两种格式
7. **Hatch构建钩子**：提供Hatch Build Hook，在wheel构建时自动编译翻译目录
8. **贡献者更新**：从Crowdin项目更新翻译贡献者列表

## 安装

### 使用pip安装

```bash
pip install jupyterlab-translate
```

安装后还需要Node.js >= 14，因为TypeScript字符串提取依赖打包在Python包内的gettext-extract工具。

### 使用conda安装

```bash
conda install jupyterlab-translate -c conda-forge
```

## 版本信息

当前版本为 **1.3.7**，采用BSD-3-Clause许可证，要求Python >= 3.7。

## 两种分发模式

jupyterlab-translate 支持两种翻译分发模式：

- **独立扩展包模式**：扩展包自带翻译文件，在扩展包目录中执行extract/update/compile命令
- **集中语言包模式**：翻译文件集中在[jupyterlab/language-packs](https://github.com/jupyterlab/language-packs)仓库中统一管理，使用extract_pack/update_pack/compile_pack命令

## 技术栈

| 组件 | 技术 |
|------|------|
| CLI框架 | Click |
| Python字符串提取 | Babel（pybabel） |
| TypeScript字符串提取 | gettext-extract（通过ncc打包为单文件JS） |
| PO/MO文件操作 | polib |
| 构建系统集成 | Hatch Build Hook |
| 翻译平台集成 | Crowdin API |
| 模板生成 | Copier |

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [CLI命令参考](/concepts/03-cli-commands.md)
- [双模式分发机制](/concepts/11-dual-mode-distribution.md)
