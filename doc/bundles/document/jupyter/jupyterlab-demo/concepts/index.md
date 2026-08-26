# 概念文档索引（Concepts）

本目录包含 jupyterlab-demo 的概念文档，按从入门到深入的学习路径组织。

## 入门篇

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | 项目定位与设计理念——什么是"演示环境即代码" |
| [01-repo-structure.md](01-repo-structure.md) | 仓库目录结构详解——配置层/构建层/素材层/输出层的分层设计 |

## 核心篇

| 文档 | 说明 |
|------|------|
| [02-binder-config.md](02-binder-config.md) | Binder环境配置三要素——environment.yml/postBuild/workspace.json |
| [03-build-system.md](03-build-system.md) | build.py 与 talks.yml 配置化组装系统——声明式素材管理模式 |

## 内容篇

| 文档 | 说明 |
|------|------|
| [04-demo-capabilities.md](04-demo-capabilities.md) | 演示能力维度——多格式查看器/多语言内核/交互控件/协作扩展 |
| [05-notebook-examples.md](05-notebook-examples.md) | Notebook示例解析——Data/Fasta/R/Cpp/Julia/Lorenz六篇详解 |
| [06-data-files.md](06-data-files.md) | 数据文件与多格式查看器——CSV/GeoJSON/FASTA/Vega-Lite/图片/多媒体 |

## 进阶篇

| 文档 | 说明 |
|------|------|
| [07-workspace-layout.md](07-workspace-layout.md) | 工作区布局与交互体验设计——Dock Panel/单文档模式/布局预设 |
| [08-extension-demo.md](08-extension-demo.md) | 插件架构与扩展生态——Everything is a Plugin的设计哲学 |

```{toctree}
:maxdepth: 7

00-introduction
01-repo-structure
02-binder-config
03-build-system
04-demo-capabilities
05-notebook-examples
06-data-files
07-workspace-layout
08-extension-demo
```
