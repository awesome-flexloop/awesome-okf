---
type: "index"
title: "概念文档索引"
description: "JupyterLab Language Packs 16篇核心概念文档目录——从入门到进阶的系统化知识讲解"
tags: [jupyterlab, language-pack, concepts, index]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22" }
status: active
---

# 概念文档（concepts/）

本目录包含 16 篇 JupyterLab Language Packs 核心概念文档，按学习路径分为五篇。

## 入门篇（00-02）

* [00. JupyterLab 语言包项目介绍](00-introduction.md) — 项目定位、Crowdin众包+Bot自动化模式、覆盖17个扩展30+语言
* [01. 整体架构概览](01-architecture-overview.md) — 五层架构（配置/源字符串/翻译/自动化/分发）、数据流转全链路
* [02. 仓库目录结构](02-repository-structure.md) — extensions/、jupyterlab/、language-packs/、scripts/、.github/workflows/ 各目录职责

## 核心配置篇（03-06）

* [03. repository-map.yml 配置详解](03-repository-map-config.md) — 核心配置文件格式、semver范围语法、版本收集算法、自动更新机制
* [04. Crowdin 翻译平台集成](04-crowdin-integration.md) — Crowdin双向同步机制、crowdin.yml配置、路径占位符、In-Context伪语言、翻译贡献流程
* [05. 语言包结构剖析](05-package-anatomy.md) — 单个语言包目录结构、pyproject.toml详解、hatchling构建规则、entry-points注册、命名约定
* [06. Gettext 国际化基础](06-gettext-i18n.md) — POT/PO/MO三种文件格式、PO条目结构、msgctxt消歧、复数形式、LC_MESSAGES目录约定、构建时编译

## 自动化流水线篇（07-09）

* [07. 自动化脚本体系](07-automation-scripts.md) — 4个Python脚本功能详解（版本检测/POT更新/发布准备/版本检查）、Bot身份认证、脚本间调用关系
* [08. CI/CD 流水线](08-cicd-pipeline.md) — 6个GitHub Actions工作流的触发条件、权限、核心步骤，从版本检测到PyPI发布的完整链路
* [09. 发布流程](09-release-workflow.md) — 从翻译积累到PyPI/conda-forge发布的6步流程、版本号规则、构建过程详解、故障排查

## 核心机制篇（10-12）

* [10. Entry Point 语言包发现机制](10-entry-point-discovery.md) — Python entry-points原理、jupyterlab.languagepack组、JupyterLab发现加载过程、语言选择优先级
* [11. 版本管理策略](11-version-management.md) — 双版本号体系（X.Y.postZ）、版本检测机制、多版本字符串合并、版本一致性强制检查、依赖版本管理
* [12. 添加新扩展到翻译](12-adding-extension.md) — 前置条件、repository-map.yml配置步骤、CI自动处理流程、目录命名映射、常见问题

## 贡献与排错篇（13-15）

* [13. 翻译规范与 PO 文件格式](13-translation-guide.md) — PO语法规则、占位符/快捷键/Markdown/复数处理、中文术语一致性、标点规范、fuzzy标记
* [14. 本地开发环境搭建](14-dev-setup.md) — 环境要求、依赖安装、常见开发任务（更新POT/构建/测试）、Conda环境配置
* [15. 故障排查与常见问题](15-troubleshooting.md) — 安装问题、翻译显示问题、构建问题、Crowdin同步问题、CI/CD问题的诊断与解决方案

```{toctree}
:maxdepth: 7

00-introduction
01-architecture-overview
02-repository-structure
03-repository-map-config
04-crowdin-integration
05-package-anatomy
06-gettext-i18n
07-automation-scripts
08-cicd-pipeline
09-release-workflow
10-entry-point-discovery
11-version-management
12-adding-extension
13-translation-guide
14-dev-setup
15-troubleshooting
```
