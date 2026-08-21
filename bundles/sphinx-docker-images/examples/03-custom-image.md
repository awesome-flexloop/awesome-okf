---
type: example
title: "自定义镜像扩展"
description: "基于官方镜像创建包含额外 Python 依赖、系统包和 LaTeX 宏包的自定义 Docker 镜像"
tags: [example, custom-image, dockerfile, extension]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: readme, resource: "/references/readme-source.md", title: "README 原文与使用说明" }
  - { id: base, resource: "/references/dockerfile-base.md", title: "Base 镜像 Dockerfile 源码" }
---

# 自定义镜像扩展

本示例演示如何基于官方 Sphinx Docker 镜像创建自定义镜像，安装项目所需的额外依赖。

## 场景

假设你的项目需要：
- Sphinx 主题：`sphinx-rtd-theme`、`furo`
- Markdown 支持：`myst-parser`
- 自动 API 文档：`sphinx-autodoc2`
- 图表支持：PlantUML（需要 Java）
- PDF 构建中需要额外的科学公式宏包

## 示例 1：HTML 自定义镜像（最常见）

创建以下文件结构：

```
my-project/
├── docs/
│   ├── conf.py
│   ├── index.rst
│   └── requirements.txt
└── Dockerfile
```

`Dockerfile`：
```dockerfile
FROM sphinxdoc/sphinx:8.2.3

LABEL org.opencontainers.image.authors="Your Name <you@example.com>"
LABEL org.opencontainers.image.description="Custom Sphinx image for my project"

WORKDIR /docs

# 安装额外系统依赖（PlantUML 需要 Java 和 graphviz）
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      default-jre-headless \
      plantuml \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt 以利用 Docker 层缓存
COPY docs/requirements.txt /docs/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 默认命令
CMD ["sphinx-build", "-M", "html", ".", "_build"]
```

`docs/requirements.txt`：
```txt
sphinx-rtd-theme==2.0.0
furo==2024.8.6
myst-parser>=4.0
sphinx-autodoc2>=0.5
sphinxcontrib-plantuml>=0.30
```

构建镜像：
```bash
docker build -t my-sphinx-docs .
```

使用自定义镜像构建文档：
```bash
cd docs
docker run --rm -v "$(pwd):/docs" my-sphinx-docs
```

## 示例 2：包含 PDF 支持的自定义镜像

如果需要同时构建 HTML 和 PDF：

```dockerfile
FROM sphinxdoc/sphinx-latexpdf:8.2.3

LABEL description="Custom Sphinx image with LaTeX and project dependencies"

WORKDIR /docs

# 安装额外 LaTeX 包（科学论文常用）
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      texlive-science \
      texlive-publishers \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 使用 tlmgr 安装 CTAN 上的额外包
RUN tlmgr update --self \
 && tlmgr install algorithmicx algorithm2e cleveref

# 安装 Python 依赖
COPY requirements.txt /docs/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 默认改为 HTML（可覆盖）
CMD ["sphinx-build", "-M", "html", ".", "_build"]
```

构建 HTML：
```bash
docker run --rm -v "$(pwd):/docs" my-sphinx-pdf sphinx-build -M html . _build
```

构建 PDF：
```bash
docker run --rm -v "$(pwd):/docs" my-sphinx-pdf sphinx-build -M latexpdf . _build
```

## 示例 3：使用 docker-compose 简化开发

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  sphinx-html:
    build:
      context: .
      dockerfile: Dockerfile
    image: my-sphinx-docs
    volumes:
      - ./docs:/docs
    command: sphinx-build -M html . _build

  sphinx-pdf:
    build:
      context: .
      dockerfile: Dockerfile.pdf
    image: my-sphinx-pdf
    volumes:
      - ./docs:/docs
    command: sphinx-build -M latexpdf . _build

  sphinx-autobuild:
    build:
      context: .
      dockerfile: Dockerfile
    image: my-sphinx-docs
    volumes:
      - ./docs:/docs
    ports:
      - "8000:8000"
    command: >
      bash -c "pip install --no-cache-dir sphinx-autobuild &&
               sphinx-autobuild --host 0.0.0.0 --port 8000 . _build/html"
```

使用方式：
```bash
# 构建 HTML
docker-compose run --rm sphinx-html

# 构建 PDF
docker-compose run --rm sphinx-pdf

# 启动自动预览服务器（文件修改自动重建）
docker-compose up sphinx-autobuild
# 访问 http://localhost:8000
```

## 示例 4：多阶段构建减小镜像体积

```dockerfile
# 阶段 1：安装依赖
FROM sphinxdoc/sphinx:8.2.3 AS builder

WORKDIR /docs
COPY requirements.txt /docs/
RUN pip install --no-cache-dir --user -r requirements.txt

# 阶段 2：运行镜像
FROM sphinxdoc/sphinx:8.2.3

WORKDIR /docs
COPY --from=builder /root/.local /root/.local
COPY . /docs/

CMD ["sphinx-build", "-M", "html", ".", "_build"]
```

> 注意：多阶段构建对于 Sphinx 镜像收益有限（pip 包本身不大），主要用于包含编译型扩展的场景。

## 最佳实践清单

1. **固定基础镜像版本**：使用 `sphinxdoc/sphinx:8.2.3` 而非 `sphinxdoc/sphinx:latest`
2. **requirements.txt 先复制**：利用 Docker 层缓存，避免每次修改文档都重装依赖
3. **同层清理**：apt-get install 和 clean 在同一个 RUN 中
4. **--no-cache-dir**：pip 安装始终使用此参数
5. **使用 .dockerignore**：排除 _build/、__pycache__/ 等不需要的文件
6. **添加 LABEL**：标注镜像作者、描述等元数据

## 相关概念

- [自定义扩展与最佳实践](/concepts/07-customization.md)：更多自定义技巧
- [Base 镜像详解](/concepts/03-base-image.md)：理解基础镜像的层结构
- [构建流水线详解](/concepts/06-build-pipeline.md)：官方镜像的 CI/CD 流程
