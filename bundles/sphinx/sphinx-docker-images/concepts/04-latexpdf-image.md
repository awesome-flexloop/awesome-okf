---
type: concept
title: "LaTeX/PDF 镜像详解"
description: "深入解析 sphinx-latexpdf 镜像的 TeXLive 包选择、多语言 CJK 支持与中文 PDF 构建要点"
tags: [docker, latex, pdf, texlive, cjk, chinese]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: latexpdf, resource: "/references/dockerfile-latexpdf.md", title: "LaTeX/PDF 镜像 Dockerfile 源码" }
---

# LaTeX/PDF 镜像详解

`sphinxdoc/sphinx-latexpdf` 是用于构建 LaTeX/PDF 文档的镜像，相比基础镜像增加了完整的 TeXLive 环境和多语言支持。

## 镜像构成

latexpdf 镜像在 base 镜像的基础上增加了 14 个 TeXLive 相关包：

### 基础工具

| 包 | 用途 |
|----|------|
| `latexmk` | LaTeX 自动编译驱动（sphinx-build 调用 latexmk 来编译 .tex → .pdf） |
| `xindy` | Unicode 友好的索引生成工具（替代 makeindex，支持中文索引） |

### 字体包

| 包 | 用途 |
|----|------|
| `lmodern` | Latin Modern 字体（LaTeX 推荐西文字体） |
| `fonts-freefont-otf` | FreeFont OTF 字体（Unicode 覆盖广） |
| `tex-gyre` | TeX Gyre 字体集合（高质量 PostScript 字体替代） |
| `texlive-fonts-recommended` | TeXLive 推荐字体 |
| `texlive-fonts-extra` | TeXLive 扩展字体 |

### LaTeX 宏包

| 包 | 用途 |
|----|------|
| `texlive-latex-recommended` | LaTeX 推荐宏包集合 |
| `texlive-latex-extra` | LaTeX 扩展宏包集合 |

### 引擎支持

| 包 | 用途 |
|----|------|
| `texlive-luatex` | LuaTeX 引擎（Lua 脚本扩展的 TeX 引擎） |
| `texlive-xetex` | XeTeX 引擎（原生 Unicode/OpenType 支持，**中文 PDF 推荐**） |

### 多语言 CJK 支持

| 包 | 用途 |
|----|------|
| `texlive-lang-cjk` | CJK（中日韩）宏包基础支持 |
| `texlive-lang-chinese` | 中文语言支持（中文模板、字体配置） |
| `texlive-lang-japanese` | 日文语言支持 |

## 中文 PDF 构建

latexpdf 镜像内置了中文支持，但要正确生成中文 PDF 需要在 Sphinx 的 `conf.py` 中配置 LaTeX 选项：

```python
# conf.py 中文 PDF 配置示例
latex_engine = 'xelatex'  # 使用 XeTeX 引擎（推荐中文）

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': r'''
        \usepackage{ctex}       % ctex 宏包处理中文
        \setCJKmainfont{SimSun} % 设置中文字体（如有需要）
    ''',
}
```

构建命令：
```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx-latexpdf \
  sphinx-build -M latexpdf . _build
```

## 为什么镜像这么大？

latexpdf 镜像超过 2GiB，主要因为：

1. **TeXLive 完整安装**：TeXLive 完整版安装约 3-5GB，即使只安装 latex-recommended + fonts + CJK 也需要 1.5-2GB
2. **多语言字体**：CJK 字体文件（中文字体）体积很大
3. **多个 TeX 引擎**：同时安装 pdfTeX、XeTeX、LuaTeX 三个引擎
4. **Debian 基础系统**：python:slim 加上各种依赖约 200-300MB

**体积优化建议**：如果不需要多语言支持，可以基于 base 镜像只安装必要的 TeXLive 包。

## 与 base 镜像的差异

latexpdf 镜像和 base 镜像有以下关键差异：

| 项目 | base | latexpdf |
|------|------|----------|
| 系统包 | graphviz, imagemagick, make | + 14 个 TeXLive 包 |
| Python 包 | Sphinx 8.2.3, Pillow | 相同 |
| 默认 CMD | `sphinx-build -M html` | `sphinx-build -M latexpdf` |
| 体积 | ~200MB | >2GiB |
| 适用输出 | HTML, EPUB | PDF（LaTeX） |

> **注意**：latexpdf 镜像也可以构建 HTML/EPUB（因为包含了 base 的全部依赖），但因为体积大不推荐这样使用。

## LaTeX 引擎选择

| 引擎 | 特点 | 适用场景 |
|------|------|---------|
| `pdflatex` | 默认引擎，速度快，输出 PDF | 纯英文文档 |
| `xelatex` | 原生 Unicode/OTF 字体支持 | **中文/多语言文档（推荐）** |
| `lualatex` | Lua 脚本扩展，灵活度高 | 需要复杂排版逻辑的文档 |

在 `conf.py` 中通过 `latex_engine` 配置：
```python
latex_engine = 'xelatex'  # 中文推荐
```

## 相关概念

- [三镜像架构解析](/concepts/02-image-architecture.md)：三个镜像的分工对比
- [Base 镜像详解](/concepts/03-base-image.md)：基础镜像的构建细节
- [PDF 文档构建示例](/examples/02-pdf-build.md)：完整的 PDF 构建流程
- [自定义镜像扩展](/concepts/07-customization.md)：安装额外 LaTeX 包
