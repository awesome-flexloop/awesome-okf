---
okf_version: "0.2"
type: bundles-index
title: "知识束总索引"
description: "awesome-okf-xs 知识束（bundles）分组导航——按技术生态组织的开源项目源码中文教程"
total_bundles: 24
groups: 6
---

# 知识束总索引（Bundles Index）

> **OKF (Open Knowledge Format)** 知识束是面向开源项目源码的系统化中文教程，遵循 [OKF v0.2 规范](meta/okf-spec/index.md)，每个知识束包含概念文档（concepts/）、实战示例（examples/）、源码参考（references/）三层结构。
>
> 当前共 **24 个知识束**，按技术生态分为 **6 个分组**。

---

## 生态关系概览

```
┌──────────────────────────────────────────────────────┐
│            📐 meta/okf-spec (OKF 格式规范)            │
│            所有知识束遵循的格式约定                     │
└─────────────────────┬────────────────────────────────┘
                      │ 规范约束
┌─────────────────────▼────────────────────────────────┐
│           🐍 python/cpython (Python 语言底座)         │
│           对象模型 · GC · 字节码 · 导入系统            │
└──────────┬──────────────────────────┬────────────────┘
           │                          │
┌──────────▼──────────┐  ┌────────────▼─────────────────┐
│ 📦 conda/ 环境管理   │  │ 🔧 tooling/ 通用开发工具      │
│ 包管理 · 锁定 · 打包 │  │ 任务自动化 · CI 集成          │
│ 安装器 · Rust 引擎   │  │                              │
└──────────┬──────────┘  └────────────┬─────────────────┘
           │                          │
           ├──────────────────────────┤
           │                          │
┌──────────▼──────────┐  ┌────────────▼─────────────────┐
│ 📓 jupyter/ 交互式   │  │ 📄 sphinx/ 文档工程           │
│ 计算 · Notebook     │  │ 文档生成 · 扩展 · 国际化      │
│ 内核协议 · Docker   │  │ 社交卡片 · 重定向 · 数学渲染  │
└─────────────────────┘  └──────────────────────────────┘
```

---

## 推荐入门路径

从零开始系统学习开源项目源码，推荐按以下顺序：

```
📐 okf-spec       了解 OKF 知识束格式规范（30分钟）
  → 🐍 cpython   理解 Python 解释器底层（选读核心章节）
    → 🔧 pyinvoke 掌握 Python 任务自动化（实用工具）
      → 📦 conda 深入环境与包管理（日常开发必备）
        → 📄 sphinx  掌握文档工程能力（项目文档写作）
          → 📓 jupyter 交互式计算与数据分析
```

---

## 分组导航

| 分组 | 知识束数 | 说明 |
|------|---------|------|
| [📐 规范与格式](meta/index.md) | 1 | OKF 格式规范本体——阅读知识束前必读 |
| [🐍 Python 语言核心](python/index.md) | 1 | CPython 解释器核心架构——所有 Python 知识的底座 |
| [📦 Conda 包管理生态](conda/index.md) | 6 | Conda 核心、lock/pack/constructor 工具链、Rattler Rust 实现、文档门户 |
| [📓 Jupyter 数据科学生态](jupyter/index.md) | 4 | 内核协议、Notebook 格式、Notebook 应用、Docker 部署 |
| [📄 Sphinx 文档工程生态](sphinx/index.md) | 9 | Sphinx 核心、功能扩展、输出渲染扩展、Docker 部署 |
| [🔧 通用开发工具](tooling/index.md) | 3 | PyInvoke 任务引擎、invocations 任务集合、GitHub Problem Matcher |

---

## 分组详情

### 📐 [规范与格式](meta/index.md)

| 知识束 | 简介 |
|--------|------|
| [okf-spec](meta/okf-spec/index.md) | OKF v0.2 规范——目录结构、文档类型、交叉引用、术语、版本、信任与验证 |

### 🐍 [Python 语言核心](python/index.md)

| 知识束 | 简介 |
|--------|------|
| [cpython](python/cpython/index.md) | CPython 解释器——对象模型、引用计数、GC、字节码、编译器管线、C 扩展 |

### 📦 [Conda 包管理生态](conda/index.md)

| 知识束 | 简介 |
|--------|------|
| [conda](conda/conda/index.md) | Conda 核心——七层架构、MatchSpec、SAT 求解器、事务、插件系统 |
| [conda-lock](conda/conda-lock/index.md) | 环境锁定——多平台 lockfile、conda/pypi 双求解器、内容哈希 |
| [conda-pack](conda/conda-pack/index.md) | 环境打包——可重定位归档、prefix 替换、跨环境部署 |
| [constructor](conda/constructor/index.md) | 安装器构造——跨平台安装包、construct.yaml、FCP、签名安全 |
| [rattler](conda/rattler/index.md) | Rust 实现——Crate 架构、高性能求解、repodata 网关、包流式安装 |
| [conda-docs](conda/conda-docs/index.md) | 文档门户——Sphinx 多项目架构、插件生态、社区贡献 |

### 📓 [Jupyter 数据科学生态](jupyter/index.md)

| 知识束 | 简介 |
|--------|------|
| [jupyter-client](jupyter/jupyter-client/README.md) | 协议客户端——ZMQ 五通道、内核管理、消息签名、多内核并行 |
| [nbformat](jupyter/nbformat/index.md) | Notebook 格式——NotebookNode 模型、v4 JSON、验证器、信任签名 |
| [jupyter-notebook](jupyter/jupyter-notebook/index.md) | Notebook v7——后端 App、前端 Shell、Handler、扩展系统 |
| [jupyter-docker-stacks](jupyter/jupyter-docker-stacks/index.md) | Docker 镜像——层级体系、启动生命周期、Hook 自定义、GPU 支持 |

### 📄 [Sphinx 文档工程生态](sphinx/index.md)

| 知识束 | 简介 |
|--------|------|
| [sphinx](sphinx/sphinx/index.md) | 文档生成器核心——Builder、Doctree、Domain、扩展接口、主题 |
| [sphinx-argparse](sphinx/sphinx-argparse/index.md) | CLI 文档——argparse 自动文档、man page、嵌套子命令 |
| [sphinx-autobuild](sphinx/sphinx-autobuild/index.md) | 热重载预览——文件监听、自动重建、WebSocket 刷新 |
| [sphinx-intl](sphinx/sphinx-intl/index.md) | 国际化——gettext 目录、Transifex、翻译统计 |
| [sphinx-websupport](sphinx/sphinx-websupport/index.md) | Web 集成——嵌入式文档、评论、搜索 API |
| [sphinxcontrib-jsmath](sphinx/sphinxcontrib-jsmath/index.md) | 数学渲染——JS 客户端渲染、公式编号、按需加载 |
| [sphinxext-opengraph](sphinx/sphinxext-opengraph/index.md) | 社交卡片——OGP 标签、智能描述、Matplotlib 自动生成图 |
| [sphinxext-rediraffe](sphinx/sphinxext-rediraffe/index.md) | 页面重定向——HTML 跳转、跨平台路径、diff 检查 |
| [sphinx-docker-images](sphinx/sphinx-docker-images/index.md) | Docker 构建——base/latexpdf/ci 镜像、LaTeX 编译 |

### 🔧 [通用开发工具](tooling/index.md)

| 知识束 | 简介 |
|--------|------|
| [pyinvoke](tooling/pyinvoke/index.md) | 任务自动化——Pythonic CLI 任务、Context、Runner、Watcher |
| [invocations](tooling/invocations/index.md) | 官方任务集——打包、测试、文档、CI、检查格式化 |
| [github-problem-matcher](tooling/github-problem-matcher/index.md) | Actions 注解——Problem Matcher 模式、正则捕获、PR 错误高亮 |
