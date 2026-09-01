---
type: concept
title: "自定义扩展与最佳实践"
description: "如何基于官方镜像创建自定义镜像、安装额外依赖、配置持久化、优化构建速度的实用指南"
tags: [docker, customization, best-practices, volumes, performance]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: readme, resource: "/references/readme-source.md", title: "README 原文与使用说明" }
  - { id: base, resource: "/references/dockerfile-base.md", title: "Base 镜像 Dockerfile 源码" }
---

# 自定义扩展与最佳实践

官方镜像提供了开箱即用的基础环境，但实际项目中经常需要额外的 Python 包、系统依赖或特殊配置。本章介绍自定义扩展的方法和 Docker 使用最佳实践。

## 安装额外 Python 依赖

### 方法一：运行时 pip install（快速但不持久）

```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx \
  bash -c "pip install sphinx-rtd-theme recommonmark && sphinx-build -M html . _build"
```

每次运行都需要安装，速度慢但适合临时使用。

### 方法二：创建自定义镜像（推荐）

创建一个项目级别的 `Dockerfile`：

```dockerfile
# Dockerfile
FROM sphinxdoc/sphinx

WORKDIR /docs
ADD requirements.txt /docs
RUN python3 -m pip install --no-cache-dir -r requirements.txt
```

创建 `requirements.txt`：
```txt
sphinx-rtd-theme==2.0.0
recommonmark==0.7.1
sphinx-autobuild==2024.4.16
myst-parser>=3.0
```

构建自定义镜像：
```bash
docker build -t my-sphinx .
```

使用自定义镜像：
```bash
docker run --rm -v "$(pwd):/docs" my-sphinx sphinx-build -M html . _build
```

## 安装额外系统依赖

如果需要额外的系统包（如 PlantUML、特定字体等）：

```dockerfile
FROM sphinxdoc/sphinx

# 安装额外系统依赖
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      plantuml \
      fonts-noto-cjk \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
ADD requirements.txt /docs
RUN python3 -m pip install --no-cache-dir -r requirements.txt
```

## 为 PDF 镜像添加 LaTeX 包

```dockerfile
FROM sphinxdoc/sphinx-latexpdf

# 安装额外 LaTeX 包
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      texlive-science \
      texlive-publishers \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 或使用 tlmgr 安装单个包
RUN tlmgr update --self && tlmgr install algorithmicx algorithm
```

## 使用 docker-compose 简化命令

对于频繁使用的项目，创建 `docker-compose.yml` 简化操作：

```yaml
# docker-compose.yml
version: '3.8'
services:
  sphinx:
    build: .
    image: my-sphinx
    volumes:
      - .:/docs
    ports:
      - "8000:8000"  # 用于 sphinx-autobuild 预览
    command: sphinx-build -M html . _build
```

常用命令：
```bash
# 构建 HTML
docker-compose run --rm sphinx

# 自动重建 + 预览服务器
docker-compose run --rm sphinx sphinx-autobuild --host 0.0.0.0 --port 8000 . _build/html

# 构建 PDF
docker-compose run --rm sphinx sphinx-build -M latexpdf . _build

# 清理构建
docker-compose run --rm sphinx make clean
```

## 性能优化技巧

### 1. 使用 .dockerignore

创建 `.dockerignore` 加快构建速度：
```
_build/
__pycache__/
*.pyc
.git/
.gitignore
```

### 2. 利用 Docker 层缓存

将不常变化的依赖安装放在前面：
```dockerfile
FROM sphinxdoc/sphinx

# 先复制 requirements.txt（变化频率低）
COPY requirements.txt /docs/
RUN pip install --no-cache-dir -r requirements.txt

# 再复制文档源码（变化频率高）
COPY . /docs/
```

这样 requirements.txt 不变时，pip install 层可以使用缓存。

### 3. 挂载 pip 缓存目录

```bash
docker run --rm \
  -v "$(pwd):/docs" \
  -v sphinx-pip-cache:/root/.cache/pip \
  sphinxdoc/sphinx pip install sphinx-rtd-theme
```

### 4. 使用 Makefile 简化命令

项目中创建便捷的 Make 目标：
```makefile
# Makefile（补充或覆盖 sphinx-quickstart 生成的）
DOCKER = docker run --rm -v "$(CURDIR):/docs"
SPHINX = sphinxdoc/sphinx
SPHINX-PDF = sphinxdoc/sphinx-latexpdf

.PHONY: html pdf epub clean

html:
	$(DOCKER) $(SPHINX) sphinx-build -M html . _build

pdf:
	$(DOCKER) $(SPHINX-PDF) sphinx-build -M latexpdf . _build

epub:
	$(DOCKER) $(SPHINX) sphinx-build -M epub . _build

clean:
	$(DOCKER) $(SPHINX) make clean

livehtml:
	$(DOCKER) -p 8000:8000 $(SPHINX) \
	  sphinx-autobuild --host 0.0.0.0 --port 8000 . _build/html
```

## 卷挂载注意事项

### 权限问题

Linux 上 Docker 挂载目录可能出现权限问题（容器内 root 创建的文件本地无法编辑）。解决方案：

```bash
# Linux: 指定用户 ID
docker run --rm -u "$(id -u):$(id -g)" -v "$(pwd):/docs" \
  sphinxdoc/sphinx sphinx-build -M html . _build
```

macOS 和 Windows（Docker Desktop）通常不需要额外处理，因为它们使用了自动权限映射。

### 挂载点选择

- **必须挂载**：文档源码目录 → `/docs`
- **可选挂载**：pip 缓存、sphinx 配置
- **不要挂载**：`/usr/local/lib/python3*/`（会覆盖容器内的包）

## 镜像选择决策树

```
需要什么输出？
├─ HTML/EPUB → 使用 sphinxdoc/sphinx
│  ├─ 有额外 Python 包？
│  │  └─ 创建自定义 Dockerfile FROM sphinxdoc/sphinx
│  └─ 只有标准 Sphinx → 直接使用官方镜像
├─ PDF/LaTeX → 使用 sphinxdoc/sphinx-latexpdf
│  ├─ 需要额外 LaTeX 包？
│  │  └─ 自定义镜像 + tlmgr/apt-get 安装
│  └─ 标准 PDF → 直接使用官方镜像
└─ CI 测试 Sphinx 本身 → sphinxdoc/docker-ci
```

## 常见问题

### Q: 为什么 latexpdf 镜像不基于 sphinx 镜像构建？

这是为了构建可靠性。如果 latexpdf FROM sphinxdoc/sphinx，每次 sphinx 镜像更新后 latexpdf 需要重新拉取和构建。独立构建可以更好地控制缓存和版本一致性。

### Q: 如何固定镜像版本？

使用版本 tag 而非 latest：
```bash
# 指定版本（推荐用于生产/CI）
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx:8.2.3 sphinx-build -M html . _build

# 使用 latest（不推荐，可能不稳定）
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx:latest sphinx-build -M html . _build
```

### Q: 如何在 Apple Silicon (M1/M2/M3) 上使用？

镜像支持 linux/arm64 架构，在 Apple Silicon Mac 上原生运行（无需 Rosetta 模拟），直接使用即可。

### Q: 构建时中文 PDF 报字体错误怎么办？

确保：
1. 使用 sphinx-latexpdf 镜像（内置 CJK 支持）
2. conf.py 中设置 `latex_engine = 'xelatex'`
3. 使用 ctex 宏包：`\usepackage{ctex}`

## 相关概念

- [Base 镜像详解](03-base-image.md)：基础镜像的构建细节
- [LaTeX/PDF 镜像详解](04-latexpdf-image.md)：PDF 镜像的 TeXLive 配置
- [自定义镜像扩展示例](../examples/03-custom-image.md)：完整的自定义镜像示例
