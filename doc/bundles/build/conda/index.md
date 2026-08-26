---
okf_version: "0.2"
type: group
title: "📦 Conda 包管理生态"
description: "Conda 跨平台包与环境管理器及其工具链生态"
---

# 📦 Conda 包管理生态

Conda 是 Python 生态中最流行的跨平台包管理器与环境管理器，支持二进制包分发、多语言依赖、环境隔离。本组涵盖 Conda 核心、周边工具链、Rust 高性能实现以及文档门户。

## 学习路径

按 **核心 → 工具链 → 高性能实现 → 文档门户** 的顺序学习：

### 第一步：核心引擎

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 1 | [conda](conda/index.md) | Conda 核心包管理器——七层架构、MatchSpec 查询语言、SAT 求解器、事务执行、插件系统（v26.7.1 源码） |

### 第二步：工具链扩展

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 2 | [conda-lock](conda-lock/index.md) | 可复现环境锁定工具——多平台 lockfile 生成、conda/pypi 双求解器、内容哈希校验、虚拟包支持 |
| 3 | [conda-pack](conda-pack/index.md) | 环境打包部署工具——将 conda 环境打包为可重定位归档、prefix 替换、跨环境部署 |
| 4 | [constructor](constructor/index.md) | 安装程序构造器——构建跨平台 Anaconda/Miniconda 风格安装器、construct.yaml 模式、FCP 求解、签名安全 |

### 第三步：下一代实现

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 5 | [rattler](rattler/index.md) | Rust 高性能 Conda 库——Crate 架构、MatchSpec/VersionSpec、依赖求解、repodata 网关、包流式安装、虚拟包 |

### 第四步：文档门户

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 6 | [conda-docs](conda-docs/index.md) | Conda 官方文档门户——Sphinx 多项目文档架构、插件生态、installer 生成、社区贡献指南 |

```{toctree}
:hidden:
:maxdepth: 7

conda/index
conda-lock/index
conda-pack/index
constructor/index
rattler/index
conda-docs/index
```
