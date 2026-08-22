---
type: Concept
title: mdformat-footnote 项目介绍与安装
description: mdformat-footnote 是 mdformat 的脚注语法支持插件，提供脚注格式化和自动排序功能。
tags: [introduction, installation, footnote, markdown, mdformat]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-init
    resource: /references/source-init.md
    title: mdformat-footnote 插件入口模块
---

## 什么是 mdformat-footnote

mdformat-footnote 是 [mdformat](https://github.com/executablebooks/mdformat) 的插件，为 Pandoc 风格的脚注语法提供解析、验证和格式化支持。脚注是学术和技术文档中常用的功能，允许作者在正文中标注引用来源，在文末集中放置注释内容。

安装此插件后，mdformat 能够：

- 正确识别和解析脚注引用和脚注定义
- 自动按引用顺序重新编号脚注
- 规范化脚注定义的缩进格式
- 处理嵌套脚注（脚注内引用其他脚注）
- 识别代码围栏中的脚注引用
- 自动移除未引用的孤立脚注定义（可配置）

当前版本为 0.1.3，处于 Beta 阶段。

## 安装

### 前置条件

- Python 3.10 或更高版本
- mdformat >= 0.7.0

### 使用 pip 安装

```bash
pip install mdformat-footnote
```

安装后，mdformat 通过 entry point 自动发现并加载插件，插件名称为 `footnote`。

### 依赖说明

| 依赖包 | 最低版本 | 作用 |
|--------|---------|------|
| mdformat | 0.7.0 | Markdown 格式化引擎 |
| mdit-py-plugins | 0.4.0 | markdown-it-py 的脚注语法插件 |

## 基本使用

安装插件后，直接使用 mdformat 格式化包含脚注的 Markdown 文件：

```bash
mdformat document.md
```

格式化后的脚注将按照首次引用顺序排列，定义块使用 4 空格缩进。

## 脚注语法

Pandoc 风格脚注的基本语法：

```markdown
正文引用脚注[^label]，再次引用[^label]。

[^label]: 这是脚注定义内容。
    可以有多行，使用4空格缩进。
```

脚注引用使用 `[^label]` 格式，脚注定义以 `[^label]:` 开头，后续内容缩进。标签可以是任意字符串（数字、文字等），格式化后会按引用顺序重新编号。

## 注意事项

- **内联脚注暂不支持**：`^[inline footnote]` 语法被显式禁用，因为渲染器尚未支持
- **标签不影响编号**：脚注编号完全由引用顺序决定，与定义书写顺序无关
- **代码块中的引用**：代码围栏内的 `[^label]` 也会被识别为脚注引用，影响排序

## 相关概念

- [插件配置与 CLI 选项](/concepts/01-plugin-configuration.md)
- [脚注渲染格式与缩进规则](/concepts/02-footnote-rendering.md)
