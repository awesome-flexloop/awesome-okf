---
type: Index
title: 概念文档索引
description: jupyterlab-translate概念文档按学习路径排列
tags: [index, concepts, learning-path]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
status: stable
---

# 概念文档

按照从入门到进阶的顺序排列。

## 入门层

| # | 文档 | 说明 |
|---|------|------|
| 00 | [项目简介](/concepts/00-introduction.md) | jupyterlab-translate是什么、解决什么问题、核心功能概览 |
| 01 | [快速开始](/concepts/01-getting-started.md) | 安装、基本使用、完整工作流程演示 |
| 02 | [架构总览](/concepts/02-architecture-overview.md) | 三层洋葱架构（CLI→API→Core）、核心模块职责 |

## 核心层

| # | 文档 | 说明 |
|---|------|------|
| 03 | [CLI命令参考](/concepts/03-cli-commands.md) | 7个子命令的用法、参数、选项完整参考 |
| 04 | [字符串提取流水线](/concepts/04-extraction-pipeline.md) | Python/TS/Schema三源提取、POT生成、去重机制 |
| 05 | [翻译目录管理](/concepts/05-catalog-management.md) | POT/PO/MO/JSON四种文件格式、Babel目录操作、合并更新 |
| 06 | [Jed JSON翻译格式](/concepts/06-json-jed-format.md) | 前端翻译JSON格式、EOT上下文分隔符、复数处理 |
| 07 | [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md) | 构建时自动编译PO→MO/JSON、wheel/sdist差异、entry point配置 |
| 08 | [运行时语言包发现](/concepts/08-runtime-discovery.md) | entry points机制、两种entry point group、包结构约定 |

## 进阶层

| # | 文档 | 说明 |
|---|------|------|
| 09 | [Schema国际化选择器](/concepts/09-schema-i18n-selectors.md) | 默认选择器、自定义选择器配置、JSON Pointer路径匹配 |
| 10 | [Crowdin贡献者集成](/concepts/10-contributors-crowdin.md) | API集成、报告下载、Markdown格式化、构建时自动更新 |
| 11 | [双模式分发机制](/concepts/11-dual-mode-distribution.md) | 独立扩展包vs集中语言包、目录结构差异、打包配置对比 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-cli-commands
04-extraction-pipeline
05-catalog-management
06-json-jed-format
07-hatch-build-hook
08-runtime-discovery
09-schema-i18n-selectors
10-contributors-crowdin
11-dual-mode-distribution
```
