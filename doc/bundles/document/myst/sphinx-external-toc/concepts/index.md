# 概念文档（Concepts）

按学习路径排列的概念文档，从入门到高级功能。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | sphinx-external-toc 简介——定位、核心问题、特点、适用场景 |
| [01-getting-started.md](01-getting-started.md) | 快速开始——安装、创建 _toc.yml、迁移现有项目、CLI验证 |

## 核心机制

| 文档 | 说明 |
|------|------|
| [02-toc-yaml-syntax.md](02-toc-yaml-syntax.md) | _toc.yml 语法详解——三种格式、条目类型(file/glob/url)、选项配置、shorthand语法 |
| [03-extension-mechanism.md](03-extension-mechanism.md) | 扩展工作机制——禁用内置Collector、SiteMap数据模型、Transform注入流程 |

## 进阶功能

| 文档 | 说明 |
|------|------|
| [04-advanced-features.md](04-advanced-features.md) | 高级功能——编号样式（数字/罗马/字母）、glob模式、外部链接、CLI工具、Jupyter Book集成 |

```{toctree}
:hidden:

00-introduction
01-getting-started
02-toc-yaml-syntax
03-extension-mechanism
04-advanced-features
```
