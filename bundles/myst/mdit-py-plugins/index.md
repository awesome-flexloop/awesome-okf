---
type: bundle
title: mdit-py-plugins 中文 Wiki
description: mdit-py-plugins（markdown-it-py插件集合）完整中文教程，涵盖22个插件的使用方法和自定义插件开发
tags:
- python
- markdown
- markdown-it
- plugins
- my-st
- executable-books
bundle_id: myst/mdit-py-plugins
version: 0.7.0
source: "https://github.com/executablebooks/mdit-py-plugins"
prerequisites:
- markdown-it-py
- mdurl
okf_version: '0.2'
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
---

# mdit-py-plugins 中文 Wiki

**mdit-py-plugins** 是 markdown-it-py 的官方插件集合，版本 0.7.0，MIT 许可证。提供22个常用的 Markdown 语法扩展插件。

- **版本**：0.7.0
- **Python 要求**：>= 3.10
- **运行时依赖**：markdown-it-py >=2.0.0,<5.0.0
- **许可证**：MIT
- **源仓库**：<https://github.com/executablebooks/mdit-py-plugins>

## 快速导航

| 目录 | 内容 | 链接 |
|------|------|------|
| 概念文档 | 10篇，入门到高级 | [concepts/index.md](concepts/index.md) |
| 示例文档 | 3篇，可运行代码 | [examples/index.md](examples/index.md) |
| 信源索引 | 插件源码映射 | [references/index.md](references/index.md) |
| 事实清单 | 130条可验证事实 | [spec/facts.md](spec/facts.md) |
| 架构洞察 | 5个核心洞察 | [spec/insights.md](spec/insights.md) |

## 五分钟快速上手

```bash
pip install mdit-py-plugins
```

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

md = (MarkdownIt()
      .use(footnote_plugin)
      .use(dollarmath_plugin)
      .use(tasklists_plugin))
```

## 插件分类

**块级插件**：front_matter（YAML元数据）、colon_fence（冒号围栏）、container（自定义容器）、deflist（定义列表）、amsmath（AMS数学）、admon（告警块）、fieldlist（字段列表）

**行内插件**：dollarmath（美元数学）、subscript（下标）、superscript（上标）、texmath（TeX数学）、myst_role（MyST角色）、gfm_autolink（自动链接）、attrs（行内属性）

**核心后处理插件**：footnote（脚注）、tasklists（任务列表）、wordcount（字数统计）、anchors（标题锚点）

**组合插件**：gfm（一键GFM风格）

## 核心架构

所有插件是接收MarkdownIt实例的函数，通过Ruler API注册规则和渲染函数：

- Block插件：操作StateBlock，识别块级语法
- Inline插件：操作StateInline，识别行内语法
- Core后处理插件：操作StateCore，遍历完整Token流
- 闭包工厂模式传递配置参数
- env字典用于插件间数据传递

## 变更日志

见 [log.md](log.md)
