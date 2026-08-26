# 概念文档（Concepts）

按学习路径排列的概念文档，从入门到定制开发。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | sphinx-copybutton 简介——定位、特点、技术栈、适用场景 |
| [01-getting-started.md](01-getting-started.md) | 快速开始——安装、启用扩展、验证效果 |

## 核心机制

| 文档 | 说明 |
|------|------|
| [02-extension-architecture.md](02-extension-architecture.md) | 扩展架构三步注册范式、Jinja2模板桥接Python与JS、静态文件加载顺序 |
| [03-text-processing.md](03-text-processing.md) | 文本处理核心——提示符剥离、正则匹配、行续接/HERE文档处理、DOM节点过滤 |

## 进阶定制

| 文档 | 说明 |
|------|------|
| [04-customization.md](04-customization.md) | 自定义CSS样式、SVG图标、选择器、本地化支持 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-extension-architecture
03-text-processing
04-customization
```
