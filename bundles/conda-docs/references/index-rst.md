---
okf_version: "0.2"
type: reference
title: "首页 index.rst 结构"
sources:
  - docs/source/index.rst
---

# 首页 index.rst 结构

`index.rst` 是 conda-docs 门户的首页，采用 sphinx-design 扩展的网格卡片布局，分为四个区域。

## 区域一：快速导航卡片

使用 `.. grid:: 1 2 2 2` 响应式网格，包含6个导航卡片：

| 卡片 | 链接目标 | 说明 |
|------|---------|------|
| Getting started | conda 稳定版用户指南/入门 | 教程和快速入门 |
| Package search | https://anaconda.org | Anaconda 包搜索平台 |
| Commands | conda 稳定版命令参考 | 所有 conda 命令文档 |
| Building Packages | conda-build 稳定版文档 | 包构建工具文档 |
| What's new? | https://conda.org/blog | 博客与发布公告 |
| Developer guide | conda 稳定版开发者指南 | 内部机制深度指南 |

## 区域二：安装下载

两列布局展示两个发行版：

**Miniconda**（Anaconda 维护）：
- 5平台下载按钮：Windows x86_64 (.exe)、macOS arm64 (.pkg)、macOS x86_64 (.pkg)、Linux x86_64 (.sh)、Linux aarch64 (.sh)
- Homebrew 安装：`brew install miniconda`
- 标注 Anaconda ToS 注意事项

**Miniforge**（conda-forge 社区维护）：
- 5平台下载（同 Miniconda），但 macOS/Linux 使用 .sh 脚本
- Homebrew 安装：`brew install miniforge`

## 区域三：项目矩阵

`.. grid:: 1 2 2 2` 网格列出6个生态项目：

| 项目 | 链接 | 说明 |
|------|------|------|
| conda | docs.conda.io/projects/conda | 核心包/环境管理命令 |
| conda build | docs.conda.io/projects/conda-build | 包构建工具 |
| Miniconda | docs.anaconda.com/free/miniconda | Anaconda 安装器 |
| conda lock | conda.github.io/conda-lock | 可复现 lock 文件生成 |
| constructor | conda.github.io/constructor | OS 特定安装器构建 |
| conda pack | conda.github.io/conda-pack | 环境打包归档 |

## 区域四：隐藏 toctree

```rst
.. toctree::
   :hidden:
   :maxdepth: 1

   help-support
   contributing
   license
```

`:hidden:` 使 toctree 不在正文显示，但构建侧栏导航。

## 重定向页面

- `intro.rst` → meta refresh 到 `index.html`
- `announcements.rst` → meta refresh 到 `help-support.html`
- `get-involved.rst` → meta refresh 到 `help-support.html`
- `redirects.rst` → meta refresh 到 `index.html`（标记 `:orphan:`）
- `conda-build.rst`/`miniconda.rst`/`conda.rst` → 通过 sphinx-reredirects 外部跳转

## 相关概念

- [文档门户架构](../concepts/01-doc-portal-arch.md)
- [双发行版策略](../concepts/03-installers.md)
- [Conda 生态项目矩阵](../concepts/04-ecosystem-projects.md)
- [Sphinx 配置](conf-py.md)
