---
okf_version: "0.2"
type: group
title: "📄 Sphinx 文档工程生态"
description: "Sphinx 文档生成器核心及其扩展、国际化、部署生态"
---

# 📄 Sphinx 文档工程生态

Sphinx 是 Python 生态最强大的文档生成工具，支持 reStructuredText/Markdown、多格式输出、扩展机制、国际化。本组涵盖 Sphinx 核心引擎、功能扩展、输出渲染扩展和 Docker 部署。

## 学习路径

按 **核心 → 功能扩展 → 输出渲染扩展 → 部署基础设施** 的顺序学习：

### 核心引擎

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 1 | [sphinx](sphinx/index.md) | Sphinx 文档生成器核心——Builder 体系、Doctree 文档树、Domain 领域模型、扩展接口、主题系统、多格式输出 |

### 功能扩展

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 2 | [sphinx-argparse](sphinx-argparse/index.md) | CLI 自动文档扩展——自动从 argparse 提取命令行参数、生成 man page、嵌套子命令支持、Markdown 集成、命令索引 |
| 3 | [sphinx-autobuild](sphinx-autobuild/index.md) | 实时预览热重载——文件监听、自动重建、WebSocket 热刷新、中间件注入、多项目/主题开发工作流 |
| 4 | [sphinx-intl](sphinx-intl/index.md) | 国际化翻译工具——gettext 消息目录提取/合并、Transifex 协作、统计机制、多语言文档工作流 |
| 5 | [sphinx-websupport](sphinx-websupport/index.md) | Web 集成扩展——将 Sphinx 文档嵌入 Web 应用、评论系统、搜索集成、WebSupport API |

### 主题与渲染扩展

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 6 | [alabaster](alabaster/index.md) | Sphinx 默认主题——极简架构（核心仅130行Python）、50+配置选项、5个组件化侧边栏模板、配置驱动样式体系、主题开发最佳范本 |
| 7 | [sphinxcontrib-jsmath](sphinxcontrib-jsmath/index.md) | 数学公式渲染——JavaScript 客户端渲染、智能 JS 按需加载、公式编号与交叉引用、并行构建安全（核心仅88行） |
| 8 | [sphinxext-opengraph](sphinxext-opengraph/index.md) | Open Graph 社交卡片——自动生成 og:title/description/image 标签、智能描述提取、四级图片回退、Matplotlib 自动生成社交分享图 |
| 9 | [sphinxext-rediraffe](sphinxext-rediraffe/index.md) | 页面重定向——自动生成 HTML 重定向页、Jinja2 模板系统、跨平台路径处理、变更检查 diff、链式重定向 |

### 部署基础设施

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 10 | [sphinx-docker-images](sphinx-docker-images/index.md) | Sphinx Docker 构建镜像——base/latexpdf/ci 三级镜像、LaTeX PDF 编译、CI 集成、自定义构建流程 |

## 相关案例

- **Sphinx 多项目架构实战**：参见 [conda 生态的 conda-docs](../../build/conda/conda-docs/index.md)，这是 Sphinx 多项目文档门户架构的典型案例，包含 Sphinx 配置深度定制与插件组合使用。

```{toctree}
:maxdepth: 7

sphinx/index
sphinx-argparse/index
sphinx-autobuild/index
sphinx-intl/index
sphinx-websupport/index
alabaster/index
sphinxcontrib-jsmath/index
sphinxext-opengraph/index
sphinxext-rediraffe/index
sphinx-docker-images/index
```
