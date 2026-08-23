---
type: Reference
title: AllTheory Docusaurus 源码
description: AllTheory Docusaurus源码，dw.cash的完整本地源码，含构建脚本与双语资源
tags: [psi, alltheory, docusaurus, source-code]
generated: { by: "trae/source-code-to-okf-wiki", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: draft
stale_after: 2027-08-23
sources:
  - id: alltheory-local
    resource: d:\spaces\SpecWeave\external\dao\AllTheory\alltheory\
    title: AllTheory Docusaurus 源码目录
---

# AllTheory Docusaurus 源码

## 信源概述

AllTheory 是 dw.cash 站点的完整 Docusaurus 源码目录，包含 17 部著作的 Markdown 源文件、Docusaurus 配置、构建脚本及中英文双语资源。该目录位于 SpecWeave 外部依赖区，通过 git submodule 引入，本地不做修改。

## 路径

- 本地路径：`d:\spaces\SpecWeave\external\dao\AllTheory\alltheory\`

## 内容结构概要

该目录为标准 Docusaurus 项目结构，包含：

- `docs/`：17 部著作的 Markdown 源文件（英文版）
- `i18n/`：简体中文翻译资源（zh-Hans）
- `docusaurus.config.js`：站点配置
- `sidebars.js`：侧边栏导航配置
- `src/`：自定义组件与 CSS
- `static/`：静态资源
- `package.json`：Node.js 依赖与构建脚本

## 关键数据点

- 对应线上站点：<https://dw.cash/zh-Hans/docs/intro>
- 包含 17 部著作的完整源文件
- 支持英文原版与简体中文双语
- 构建输出为静态站点（SSG）
- 源码仓库关联：github.com/loning/alltheory

## 免责声明

本目录内容为哲学-数理思想实验的文本载体，其中理论主张不构成科学正确性背书。源码文件仅供阅读与分析，不做修改。
