---
type: concept
title: "三镜像架构解析"
description: "深入理解 sphinx、sphinx-latexpdf、docker-ci 三个镜像的分层设计与选型决策"
tags: [docker, architecture, images, design]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: base, resource: "/references/dockerfile-base.md", title: "Base 镜像 Dockerfile 源码" }
  - { id: latexpdf, resource: "/references/dockerfile-latexpdf.md", title: "LaTeX/PDF 镜像 Dockerfile 源码" }
  - { id: ci, resource: "/references/dockerfile-ci.md", title: "CI 测试镜像 Dockerfile 源码" }
---

# 三镜像架构解析

sphinx-docker-images 项目采用三层镜像架构，每个镜像服务于不同的使用场景。理解这三个镜像的差异和联系，有助于根据需求选择正确的镜像。

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    docker-ci (CI 测试)                       │
│  基础: ubuntu:24.04                                          │
│  包含: build-essential, JDK 11, epubcheck, git,             │
│        python3-dev, TeXLive, graphviz, imagemagick...        │
│  工作目录: /sphinx                                           │
│  用途: Sphinx 核心项目的 CI 自动化测试                        │
├─────────────────────────────────────────────────────────────┤
│                 sphinx-latexpdf (PDF 构建)                   │
│  基础: python:slim                                           │
│  包含: base 全部依赖 + TeXLive (CJK/中/日/英) + latexmk     │
│  工作目录: /docs                                             │
│  体积: >2GiB                                                 │
│  用途: LaTeX/PDF 文档构建                                    │
├─────────────────────────────────────────────────────────────┤
│                    sphinx (基础/HTML 构建)                    │
│  基础: python:slim                                           │
│  包含: Python 3 + Sphinx 8.2.3 + Pillow                     │
│        + graphviz + imagemagick + make                      │
│  工作目录: /docs                                             │
│  体积: ~200MB                                                │
│  用途: HTML/EPUB 文档构建（日常使用）                         │
└─────────────────────────────────────────────────────────────┘
```

## 关键设计决策

### 1. 镜像分离而非单镜像多标签

项目选择维护三个独立 Dockerfile 而非一个 Dockerfile 多 stage 构建，原因是：

- **体积差异巨大**：TeXLive 超过 2GiB，大多数用户只需要 HTML 构建，不应被迫下载巨大镜像
- **依赖不同**：CI 镜像需要 JDK（epubcheck）、编译工具链等，普通用户不需要
- **发布节奏不同**：版本镜像跟随 Sphinx 版本发布，CI 镜像每次 master 合并后发布
- **独立演进**：三个镜像可以独立更新，互不影响

### 2. latexpdf 不继承 base 镜像

`latexpdf/Dockerfile` 使用 `FROM python:slim` 而非 `FROM sphinxdoc/sphinx`，这是一个反直觉但合理的决策：

- Docker Hub 镜像在 Dockerfile 中引用时需要网络拉取，增加构建不确定性
- 独立构建可以更好地控制层缓存
- 两个 Dockerfile 的系统包安装步骤差异较大，继承带来的复用有限
- 避免基础镜像更新导致 PDF 镜像意外变化

### 3. CI 镜像使用 Ubuntu 而非 python:slim

CI 镜像选择 `ubuntu:24.04` 而非 `python:slim`（基于 Debian），原因：

- 需要 `openjdk-11-jre-headless`（epubcheck 依赖），Ubuntu 源中版本更新
- 需要 `build-essential` 和 `python3-dev` 编译 C 扩展
- CI 环境对镜像体积不敏感，优先保证工具完整性
- 使用 `python3-pip`/`python3-venv`（系统 Python）而非镜像自带 Python，方便测试多版本

## 镜像对比表

| 特性 | sphinx | sphinx-latexpdf | docker-ci |
|------|--------|-----------------|-----------|
| 基础镜像 | python:slim | python:slim | ubuntu:24.04 |
| Sphinx 版本 | 8.2.3（预装） | 8.2.3（预装） | 不预装 |
| Python 环境 | 镜像自带 python3 | 镜像自带 python3 | 系统 python3 + venv |
| TeXLive | ❌ | ✅（CJK 完整版） | ✅（推荐版） |
| Java/JDK | ❌ | ❌ | ✅（OpenJDK 11） |
| C 编译工具 | ❌ | ❌ | ✅（build-essential） |
| epubcheck | ❌ | ❌ | ✅ |
| git | ❌ | ❌ | ✅ |
| graphviz | ✅ | ✅ | ✅ |
| imagemagick | ✅ | ✅ | ✅ |
| make | ✅ | ✅ | ✅ |
| 工作目录 | /docs | /docs | /sphinx |
| 默认命令 | html 构建 | latexpdf 构建 | 无（bash） |
| 典型体积 | ~200MB | >2GiB | ~1.5GiB |
| Tag 策略 | PEP 440 版本号 | PEP 440 版本号 | 日期 + latest |
| 目标用户 | 文档作者 | 需要 PDF 的作者 | Sphinx 开发者 |

## 选型指南

```
你需要做什么？
├─ 只构建 HTML/EPUB 文档
│  └─ ✅ 使用 sphinxdoc/sphinx（最小、最快）
├─ 需要构建 PDF（特别是中文 PDF）
│  └─ ✅ 使用 sphinxdoc/sphinx-latexpdf（内置 CJK 支持）
├─ 需要在 CI 中测试 Sphinx 本身
│  └─ ✅ 使用 sphinxdoc/docker-ci（完整测试环境）
├─ 需要额外 Python 依赖
│  └─ ✅ FROM sphinxdoc/sphinx 自定义扩展
└─ 需要特殊 LaTeX 包
   └─ ✅ FROM sphinxdoc/sphinx-latexpdf + tlmgr 安装
```

## 相关概念

- [Base 镜像详解](/concepts/03-base-image.md)：base 镜像的逐层构建细节
- [LaTeX/PDF 镜像详解](/concepts/04-latexpdf-image.md)：TeXLive 包选择与中文 PDF 支持
- [CI 镜像详解](/concepts/05-ci-image.md)：CI 测试环境的特殊配置
- [自定义镜像扩展](/concepts/07-customization.md)：基于官方镜像创建自定义镜像
