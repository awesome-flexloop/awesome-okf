---
type: concept
title: "CI 测试镜像详解"
description: "解析 docker-ci 镜像的特殊设计——Ubuntu 基础、全工具链、CI 专用工作目录与日构建策略"
tags: [docker, ci, testing, ubuntu, continuous-integration]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: ci, resource: "/references/dockerfile-ci.md", title: "CI 测试镜像 Dockerfile 源码" }
  - { id: build-ci, resource: "/references/workflow-build-ci.md", title: "CI 镜像工作流 build-ci.yml" }
---

# CI 测试镜像详解

`sphinxdoc/docker-ci`（GHCR 上为 `ghcr.io/sphinx-doc/sphinx-ci`）是 Sphinx 项目自身用于持续集成测试的镜像。它与面向用户的 sphinx/sphinx-latexpdf 镜像有显著不同的设计目标。

## 设计目标

CI 镜像的核心目标是**为 Sphinx 的自动化测试提供完整、一致的环境**，而非用于文档构建。因此它的设计优先级是：

1. **工具完整性** > 体积最小化
2. **环境一致性** > 灵活性
3. **快速更新** > 版本锁定

## Dockerfile 解析

### 基础镜像：Ubuntu 24.04

```dockerfile
FROM ubuntu:24.04
```

与 base/latexpdf 使用 `python:slim` 不同，CI 镜像使用 `ubuntu:24.04`：

- Ubuntu 24.04（Noble Numbat）是 LTS 版本，长期支持
- Ubuntu 的包仓库中 OpenJDK、TeXLive 等包版本更新
- 不使用 Docker 官方 Python 镜像，而是使用系统 Python + venv，方便测试多 Python 版本

### 环境变量

```dockerfile
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV TERM xterm
```

| 变量 | 作用 |
|------|------|
| `DEBIAN_FRONTEND=noninteractive` | 禁止 apt 安装时弹出交互对话框（CI 环境必须） |
| `LANG=C.UTF-8` | 设置 UTF-8 编码，避免 Python 输出编码问题 |
| `TERM=xterm` | 终端类型设置，某些工具需要 |

### 系统依赖全景

CI 镜像安装了 20 个系统包（不使用 `--no-install-recommends`）：

**编译和构建工具**：
- `build-essential`：gcc/g++/make 等 C 编译工具链（编译 C 扩展）
- `python3-dev`：Python 开发头文件（编译 Python C 扩展）
- `make`：构建工具

**Python 环境**：
- `python3-venv`：虚拟环境支持
- `python3-pip`：包管理器

**版本控制**：
- `git`：Git 客户端（checkout 源码）

**测试工具**：
- `dvipng`：DVI 转 PNG（数学公式渲染测试）
- `epubcheck`：EPUB 规范验证（需要 Java）
- `openjdk-11-jre-headless`：Java 运行时（epubcheck 依赖）

**国际化**：
- `gettext`：i18n 工具（消息提取、编译）

**文档工具**：
- `graphviz`：图表渲染
- `imagemagick`：图片处理

**LaTeX 环境**（PDF 测试）：
- `lmodern`、`tex-gyre`：字体
- `texlive-latex-recommended`、`texlive-latex-extra`：LaTeX 宏包
- `texlive-fonts-recommended`、`texlive-fonts-extra`：字体
- `texlive-luatex`、`texlive-xetex`：TeX 引擎

### 工作目录

```dockerfile
RUN mkdir /sphinx
WORKDIR /sphinx
```

CI 镜像工作目录为 `/sphinx`（而非 `/docs`），因为 CI 中挂载的是 Sphinx 源码目录而非文档目录。

### 不预装 Sphinx

与 base/latexpdf 镜像不同，CI 镜像中**不通过 pip 预装 Sphinx**。这是因为：

- CI 测试时需要从当前 commit 的源码安装 Sphinx（测试最新代码）
- 预装版本会与源码安装版本冲突
- CI 脚本中会执行 `pip install -e .` 从源码安装

### 不清理 apt 缓存

CI 镜像中没有 `rm -rf /var/lib/apt/lists/*` 清理步骤，因为：

- CI 环境对镜像体积不敏感（存储在 CI runner 上）
- 保留缓存列表方便 CI 脚本中安装额外包
- CI 镜像构建频率高，少一层清理可加快构建速度

## CI 镜像 vs 用户镜像

| 特性 | 用户镜像（sphinx） | CI 镜像（docker-ci） |
|------|-------------------|---------------------|
| 目标用户 | 文档作者 | Sphinx 核心开发者 |
| 基础镜像 | python:slim | ubuntu:24.04 |
| Sphinx | 预装（锁定版本） | 不预装（CI 时从源码装） |
| 体积优化 | 极致优化（--no-install-recommends + 清理） | 不优化（完整版） |
| 工作目录 | /docs | /sphinx |
| 默认命令 | sphinx-build | 无（bash） |
| Java/JDK | ❌ | ✅（epubcheck） |
| 编译工具链 | ❌ | ✅（build-essential） |
| git | ❌ | ✅ |
| Tag 策略 | 版本号（8.2.3） | 日期 + latest |
| 更新频率 | 跟随 Sphinx 发布 | 每次 master 合并 |

## Tag 策略

CI 镜像使用两种 tag：

1. **日期 tag**：`type=schedule,pattern={{date 'YYYY-MM-DD'}}`（如 `2026-08-21`）
   - 保留历史版本，可以回退到特定日期的环境
2. **latest tag**：`type=raw,value=latest`
   - 始终指向最新 master 构建
   - 供 CI 工作流使用 `sphinxdoc/docker-ci:latest`

这与用户镜像的 PEP 440 版本 tag（如 `8.2.3`）形成对比。

## 双 Registry

CI 镜像同样发布到两个 Registry：
- Docker Hub：`sphinxdoc/docker-ci`
- GHCR：`ghcr.io/sphinx-doc/sphinx-ci`

支持双架构（linux/amd64, linux/arm64）。

## 相关概念

- [三镜像架构解析](02-image-architecture.md)：三个镜像的设计分工
- [构建流水线详解](06-build-pipeline.md)：GitHub Actions 自动化构建
- [CI 集成测试示例](../examples/04-ci-integration.md)：在 CI 中使用 Sphinx Docker 镜像
