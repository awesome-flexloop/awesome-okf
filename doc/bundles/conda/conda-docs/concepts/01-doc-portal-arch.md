---
okf_version: "0.2"
type: "concept"
title: "文档门户架构：ReadTheDocs 多项目模式"
sources:
  - README.md
  - docs/source/conf.py
  - docs/source/index.rst
  - .readthedocs.yml
---

# 文档门户架构：ReadTheDocs 多项目模式

Conda 文档生态采用 ReadTheDocs 平台的**项目+子项目（projects and subprojects）**功能，实现文档的分布式维护与统一访问。

## 架构模式

```
docs.conda.io/                          (conda-docs 主项目)
├── /                                   → 首页/门户（conda-docs 仓库）
├── /projects/conda/                    → Conda CLI 文档（conda/conda 仓库）
│   └── /en/stable/...
├── /projects/conda-build/              → conda-build 文档（conda/conda-build 仓库）
│   └── /en/stable/...
└── /en/latest/help-support.html        → 共通支持页面（conda-docs 仓库）
```

**核心原则**：文档内容存放在对应的源码仓库中，conda-docs 只做导航和共通资源聚合。

## 三种页面类型

conda-docs 仓库中的 RST 文件分为三类：

**1. 有效内容页面**（实际承载内容）：
- `index.rst` — 首页门户
- `contributing.rst` — 贡献指南
- `help-support.rst` — 社区支持
- `license.rst` — 许可证文本

**2. 内部重定向页面**（HTML meta refresh 跳转到本站其他页面）：
- `intro.rst` → `index.html`
- `announcements.rst` → `help-support.html`
- `get-involved.rst` → `help-support.html`
- `redirects.rst` → `index.html`（标记为 `:orphan:`）

这些页面使用原始 HTML 实现跳转：
```html
<html><head><meta http-equiv="refresh" content="0; URL='index.html'" /></head><body></body></html>
```

**3. 外部重定向页面**（通过 sphinx-reredirects 跳转到外部 URL）：
- `conda.rst` → conda 子项目稳定版文档
- `conda-build.rst` → conda-build 子项目稳定版文档
- `miniconda.rst` → Anaconda Miniconda 文档页面

这些 RST 文件只有标题，内容为空，实际跳转由 Sphinx 扩展在构建时处理。

## 隐藏 toctree 策略

首页使用 `:hidden:` 选项的 toctree 指令：

```rst
.. toctree::
   :hidden:
   :maxdepth: 1

   help-support
   contributing
   license
```

`:hidden:` 使目录树不在页面正文中渲染，但仍然：
- 生成左侧导航侧栏
- 确保这些页面被 Sphinx 纳入构建
- 建立文档间的父子关系

首页的主导航不依赖 toctree，而是使用 sphinx-design 的卡片组件手动构建，提供更灵活的视觉布局。

## 版本管理策略

conda-docs 作为门户仓库**不发布版本化文档**（conf.py 中 version/release 设为空字符串）。sitemap 配置固定使用 `latest`：

```python
sitemap_url_scheme = "{lang}latest/{link}"
```

子项目（conda、conda-build）维护 stable/latest 等多版本文档，门户始终指向子项目的 `stable` 版本。

## 架构优势

1. **文档与代码同版本**：每个项目的文档与代码在同一 git 仓库中，PR 同时修改代码和文档
2. **独立发布节奏**：各子项目可以独立更新文档，不需要协调门户仓库
3. **统一品牌体验**：所有文档在 docs.conda.io 域名下，使用相同的 conda_sphinx_theme
4. **轻量级门户**：conda-docs 仓库本身内容极少，构建快速，维护简单
5. **灵活导航**：首页使用卡片式布局而非传统 toctree，视觉体验更好

## 可迁移模式

这种"主项目做门户+子项目承载内容"的模式可迁移到任何多项目开源组织。关键要素：
- 主项目只放着陆页、共通页面、项目导航
- 使用 sphinx-design 构建卡片式首页
- 使用 sphinx-reredirects 处理外部子项目跳转
- 子项目文档与源码同仓库
- ReadTheDocs 配置子项目关联

## 相关概念

- [conda-docs 简介](00-introduction.md)
- [Sphinx 构建系统配置详解](02-sphinx-config.md)
- [基于 conda-docs 模式搭建文档门户](../examples/doc-portal-template.md)
- [信源：Sphinx 配置 conf.py](../references/conf-py.md)
