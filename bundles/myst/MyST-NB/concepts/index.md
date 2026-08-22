# 概念文档（Concepts）

按学习路径排列的概念文档，从入门到深入。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | MyST-NB 简介——定位、核心能力、四阶段管线 |
| [01-getting-started.md](01-getting-started.md) | 快速开始——安装、最小 conf.py、第一个 Notebook |
| [02-notebook-format.md](02-notebook-format.md) | MyST Notebook 文件格式——.ipynb 和 .md（mystnb）两种格式 |

## 核心架构

| 文档 | 说明 |
|------|------|
| [03-processing-pipeline.md](03-processing-pipeline.md) | 四阶段处理管线——读取→执行→转换→渲染 |
| [04-config-system.md](04-config-system.md) | 配置系统——三层覆盖体系、nb_* 配置项 |
| [05-execution-modes.md](05-execution-modes.md) | 执行模式与缓存——5 种模式、jupyter-cache、超时/错误处理 |
| [06-render-and-mime.md](06-render-and-mime.md) | 渲染与 MIME 类型——MIME 优先级、多格式输出、ipywidgets |

## 核心功能

| 文档 | 说明 |
|------|------|
| [07-glue.md](07-glue.md) | Glue 变量粘贴——代码中存储、文档中引用、跨页面 |
| [08-eval.md](08-eval.md) | Eval 内联求值——正文内联计算变量值 |
| [09-hiding-code.md](09-hiding-code.md) | 代码隐藏与输出控制——remove/hide 标签、滚动、折叠 |

## 集成与扩展

| 文档 | 说明 |
|------|------|
| [10-sphinx-integration.md](10-sphinx-integration.md) | Sphinx 集成机制——setup 注册流程、Post-Transforms、资源加载 |
| [11-docutils-standalone.md](11-docutils-standalone.md) | Docutils 独立使用——CLI 工具、Python API |
| [12-custom-formats.md](12-custom-formats.md) | 自定义格式与扩展——自定义 Reader、渲染器、MIME 插件 |
