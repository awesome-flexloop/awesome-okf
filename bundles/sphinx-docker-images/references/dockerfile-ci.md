---
type: reference
title: "CI 测试镜像 Dockerfile 源码"
description: "sphinxdoc/docker-ci Sphinx CI 测试镜像 Dockerfile 完整源码与解析"
tags: [docker, dockerfile, ci, testing, ubuntu]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-ci, resource: "external/libs/docs/sphinx-docker-images/ci/Dockerfile", title: "ci/Dockerfile 源码" }
---

# CI 测试镜像 Dockerfile 源码

## 完整源码

```dockerfile
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV TERM xterm
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y \
       build-essential \
       dvipng \
       epubcheck \
       git \
       gettext \
       graphviz \
       imagemagick \
       make \
       lmodern \
       openjdk-11-jre-headless \
       python3-venv \
       python3-pip \
       python3-dev \
       texlive-latex-recommended \
       texlive-latex-extra \
       texlive-fonts-recommended \
       tex-gyre \
       texlive-fonts-extra \
       texlive-luatex \
       texlive-xetex \
 && apt-get autoremove \
 && apt-get clean

RUN mkdir /sphinx
WORKDIR /sphinx
```

## 逐行解析

| 行 | 指令 | 说明 |
|----|------|------|
| 1 | `FROM ubuntu:24.04` | 基于 Ubuntu 24.04（Noble Numbat），非 python:slim |
| 3-5 | `ENV` | 设置环境变量：`DEBIAN_FRONTEND=noninteractive`（避免 apt 交互提示）、`LANG=C.UTF-8`、`TERM=xterm` |
| 6-30 | `RUN apt-get` | 升级系统 + 安装 20 个开发/测试依赖包（**不使用 --no-install-recommends**，需要完整环境） |
| 32-33 | `RUN mkdir /sphinx + WORKDIR` | 创建并设置工作目录为 `/sphinx`（Sphinx 源码挂载点） |

## CI 镜像额外依赖（相比 latexpdf）

| 包名 | 用途 |
|------|------|
| `build-essential` | C/C++ 编译工具链（编译 C 扩展） |
| `dvipng` | DVI 转 PNG（数学公式渲染测试） |
| `epubcheck` | EPUB 规范验证工具（需 Java 运行时） |
| `git` | Git 版本控制（checkout 源码测试） |
| `gettext` | 国际化工具（i18n 测试） |
| `openjdk-11-jre-headless` | Java 11 运行时（epubcheck 依赖） |
| `python3-venv` | Python 虚拟环境支持 |
| `python3-dev` | Python 开发头文件（编译 C 扩展） |

## 关键事实

- **基础镜像**：`ubuntu:24.04`（不同于 base/latexpdf 的 python:slim）
- **工作目录**：`/sphinx`（不同于 base/latexpdf 的 `/docs`）
- **包管理**：不使用 `--no-install-recommends`，安装完整开发环境
- **不预装 Sphinx**：CI 镜像中不 pip install Sphinx，测试时从源码安装
- **Java 支持**：内置 OpenJDK 11 供 epubcheck 使用
- **镜像标签**：`sphinxdoc/docker-ci`、`ghcr.io/sphinx-doc/sphinx-ci`
- **Tag 策略**：日期 tag（YYYY-MM-DD）+ latest（非版本号）
- **缺少**：没有 `rm -rf /var/lib/apt/lists/*` 清理（CI 环境对体积不敏感）
