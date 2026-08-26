# 概念文档索引

jupyterlab-latex 的核心概念按阅读顺序排列，从入门到进阶逐层递进。

## 入门篇

| 序号 | 文档 | 一句话说明 |
|------|------|-----------|
| 00 | [jupyterlab-latex 简介](00-introduction.md) | 扩展定位、双组件架构、核心模块速览 |
| 01 | [安装与快速上手](01-getting-started.md) | 安装步骤、验证方法、第一个 LaTeX 文档 |
| 02 | [架构总览](02-architecture-overview.md) | 双插件架构、数据流、HTTP API、文档工厂 |

## 核心篇

| 序号 | 文档 | 一句话说明 |
|------|------|-----------|
| 03 | [LaTeX 编译流程](03-latex-compilation.md) | 命令序列构建、BibTeX 多轮编译、输出过滤、临时文件清理 |
| 04 | [PDF 查看器](04-pdf-viewer.md) | pdfjs-dist 渲染管线、缩放翻页、工具栏、坐标转换 |
| 05 | [SyncTeX 双向同步](05-synctex-sync.md) | 正向/反向搜索、坐标系统、CLI 命令解析 |

## 功能篇

| 序号 | 文档 | 一句话说明 |
|------|------|-----------|
| 06 | [编辑工具栏与快捷操作](06-editing-tools.md) | 格式化按钮、列表表格、数学符号、LaTeX 菜单 |
| 07 | [配置指南](07-configuration.md) | 后端 traitlets 配置项、前端设置、常见场景 |

## 阅读路径建议

```
初学者路径：00 → 01 → 06（直接使用工具栏操作）
开发者路径：00 → 02 → 03 → 04 → 05（理解架构后二次开发）
运维路径：   01 → 07 → 04 troubleshooting（安装配置与排障）
```

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-latex-compilation
04-pdf-viewer
05-synctex-sync
06-editing-tools
07-configuration
```
