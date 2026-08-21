---
type: reference
title: "LaTeX/PDF 镜像 Dockerfile 源码"
description: "sphinxdoc/sphinx-latexpdf LaTeX PDF 构建镜像 Dockerfile 完整源码与逐行解析"
tags: [docker, dockerfile, latex, pdf, texlive]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-latexpdf, resource: "external/libs/docs/sphinx-docker-images/latexpdf/Dockerfile", title: "latexpdf/Dockerfile 源码" }
---

# LaTeX/PDF 镜像 Dockerfile 源码

## 完整源码

```dockerfile
FROM python:slim

LABEL org.opencontainers.image.authors="Sphinx Team <https://www.sphinx-doc.org/>"
LABEL org.opencontainers.image.documentation="https://sphinx-doc.org/"
LABEL org.opencontainers.image.source="https://github.com/sphinx-doc/sphinx-docker-images"
LABEL org.opencontainers.image.version="8.2.3"
LABEL org.opencontainers.image.licenses="BSD-2-Clause"
LABEL org.opencontainers.image.description="LaTeX container image for Sphinx"

WORKDIR /docs
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      graphviz \
      imagemagick \
      make \
      \
      latexmk \
      lmodern \
      fonts-freefont-otf \
      texlive-latex-recommended \
      texlive-latex-extra \
      texlive-fonts-recommended \
      texlive-fonts-extra \
      texlive-lang-cjk \
      texlive-lang-chinese \
      texlive-lang-japanese \
      texlive-luatex \
      texlive-xetex \
      xindy \
      tex-gyre \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip \
 && python3 -m pip install --no-cache-dir Sphinx==8.2.3 Pillow

CMD ["sphinx-build", "-M", "latexpdf", ".", "_build"]
```

## 逐行解析

| 行 | 指令 | 说明 |
|----|------|------|
| 1 | `FROM python:slim` | 同 base 镜像，基于 python:slim（**注意：不 FROM base，独立构建**） |
| 3-8 | `LABEL` | OCI 标签，描述为 "LaTeX container image for Sphinx" |
| 10 | `WORKDIR /docs` | 工作目录同 base：`/docs` |
| 11-33 | `RUN apt-get` | 安装系统依赖：base 的 3 个包 + 14 个 TeXLive 相关包 |
| 35-36 | `RUN pip install` | 同 base：Sphinx==8.2.3 + Pillow |
| 38 | `CMD` | 默认命令改为 `sphinx-build -M latexpdf . _build`，构建 PDF |

## TeXLive 包清单

| 包名 | 用途 |
|------|------|
| `latexmk` | LaTeX 自动编译工具（sphinx-build 调用） |
| `lmodern` | Latin Modern 字体（推荐 LaTeX 字体） |
| `fonts-freefont-otf` | FreeFont OTF 字体（Unicode 支持） |
| `texlive-latex-recommended` | TeXLive LaTeX 推荐包 |
| `texlive-latex-extra` | TeXLive LaTeX 扩展包 |
| `texlive-fonts-recommended` | TeXLive 推荐字体 |
| `texlive-fonts-extra` | TeXLive 扩展字体 |
| `texlive-lang-cjk` | CJK（中日韩）语言支持 |
| `texlive-lang-chinese` | 中文语言支持（中文 PDF 必备） |
| `texlive-lang-japanese` | 日文语言支持 |
| `texlive-luatex` | LuaTeX 引擎支持 |
| `texlive-xetex` | XeTeX 引擎支持（Unicode 友好，中文推荐） |
| `xindy` | 索引生成工具（支持 Unicode） |
| `tex-gyre` | TeX Gyre 字体集合 |

## 关键事实

- **基础镜像**：`python:slim`（同 base，但不从 base 继承）
- **镜像体积**：超过 2GiB（TeXLive 巨大）
- **多语言支持**：内置 CJK/中文/日文 TeXLive 包
- **双引擎**：支持 LuaTeX 和 XeTeX（中文 PDF 推荐 XeTeX）
- **默认命令**：latexpdf 构建模式
- **镜像标签**：`sphinxdoc/sphinx-latexpdf`、`ghcr.io/sphinx-doc/sphinx-latexpdf`
