# 概念文档索引

本目录包含 jupyterlab_pygments 的概念文档，按学习路径组织。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | jupyterlab_pygments 简介与定位——连接 Pygments 语法高亮与 JupyterLab 主题系统 |
| [01-getting-started.md](01-getting-started.md) | 快速上手：安装、验证、使用 JupyterStyle 生成主题感知高亮 HTML |

## 核心

| 文档 | 说明 |
|------|------|
| [02-dual-bridge-architecture.md](02-dual-bridge-architecture.md) | 双桥架构解析：Python Style → CSS → JupyterLab 的三层桥接设计 |
| [03-jupyter-style-class.md](03-jupyter-style-class.md) | JupyterStyle 类详解：继承体系、styles 字典映射、CSS 变量体系与 token 分类差异 |

## 进阶

| 文档 | 说明 |
|------|------|
| [04-css-generation-pipeline.md](04-css-generation-pipeline.md) | CSS 生成流水线：HtmlFormatter.get_style_defs()、.highlight 过滤与 base.css 生成 |
| [05-build-and-extension.md](05-build-and-extension.md) | 构建系统与扩展机制：hatchling + jupyter-builder 双语言构建、预构建扩展加载流程 |

## 推荐阅读顺序

[简介](00-introduction.md) → [快速上手](01-getting-started.md) → [双桥架构](02-dual-bridge-architecture.md) → [JupyterStyle类](03-jupyter-style-class.md) → [CSS生成流水线](04-css-generation-pipeline.md) → [构建系统](05-build-and-extension.md)

## 导航

- [示例文档索引](../examples/index.md)
- [源码信源索引](../references/index.md)
- [教程首页](../index.md)
