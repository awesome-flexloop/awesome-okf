---
type: Concept
title: "Minimal 到 SciPy 层"
description: "minimal-notebook工具增强层与scipy-notebook科学计算层的包清单、TeX Live配置、matplotlib缓存"
tags: [minimal-notebook, scipy-notebook, tex-live, scientific-computing, pandas, matplotlib]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-minimal, resource: "/references/dockerfiles.md", title: "Minimal Notebook Dockerfile" }
  - { id: src-scipy, resource: "/references/dockerfiles.md", title: "SciPy Notebook Dockerfile" }
---

# Minimal 到 SciPy 层

本章节介绍 L3 minimal-notebook 和 L4c scipy-notebook 两层——从工具增强到Python科学计算全栈。

## minimal-notebook（L3：工具增强层）

minimal-notebook 在 base-notebook 基础上添加**日常开发必需的命令行工具**和**文档导出能力**，同时作为 R/Julia 多语言镜像的共同父层。

### OS工具包

```dockerfile
RUN apt-get install --yes --no-install-recommends \
    curl \
    git \
    nano-tiny \
    tzdata \
    unzip \
    vim-tiny \
    openssh-client \
    less \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    xclip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```

| 包 | 作用 |
|----|------|
| curl | HTTP客户端（API调试、文件下载） |
| git | 版本控制 |
| nano-tiny | 精简版nano编辑器（替代完整版nano减小体积） |
| tzdata | 时区数据 |
| unzip | ZIP解压 |
| vim-tiny | 精简版vim编辑器 |
| openssh-client | SSH客户端（git-over-ssh、远程连接） |
| less | 分页器（R的help()函数需要） |
| texlive-xetex | XeTeX引擎（nbconvert PDF导出，支持Unicode/CJK） |
| texlive-fonts-recommended | TeX推荐字体 |
| texlive-plain-generic | 纯TeX宏包 |
| xclip | X11剪贴板（Linux主机上的剪贴板支持） |

> **nano-tiny vs nano**：完整版nano依赖较多，nano-tiny是编译时禁用了大部分功能的精简版本。Dockerfile通过`update-alternatives`将nano-tiny注册为`nano`命令。

### R mimetype配置

```dockerfile
COPY --chown=${NB_UID}:${NB_GID} Rprofile.site /opt/conda/lib/R/etc/
```

Rprofile.site 配置R图形在Jupyter中的返回mimetype选项，确保R图形能正确在notebook中显示。这是为下游R镜像做准备（minimal层本身不安装R，但预置配置避免后续重复）。

### Setup Scripts

```dockerfile
COPY setup-scripts/ /opt/setup-scripts/
```

`/opt/setup-scripts/`目录包含供下游镜像使用的安装脚本：
- `setup_julia.py`：下载安装Julia
- `setup-julia-packages.bash`：安装IJulia和常用Julia包
- `setup_spark.py`：下载安装Apache Spark
- `activate_notebook_custom_env.py`：激活自定义conda环境

这是一个**模板方法模式**的设计：minimal层提供脚本框架，下游镜像调用这些脚本完成各自的安装。

## scipy-notebook（L4c：Python科学计算层）

scipy-notebook 是最受欢迎的镜像之一，在minimal-notebook基础上安装了完整的Python科学计算栈。

### 编译工具与媒体包

```dockerfile
RUN apt-get install --yes --no-install-recommends \
    build-essential \
    cm-super \
    dvipng \
    ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```

| 包 | 作用 |
|----|------|
| build-essential | gcc/g++/make等编译工具（Cython编译C扩展需要） |
| cm-super | LaTeX Computer Modern字体增强（matplotlib LaTeX标签） |
| dvipng | DVI转PNG（matplotlib的TeX渲染后端） |
| ffmpeg | 视频编解码（matplotlib动画保存需要） |

### Python科学计算包清单

```dockerfile
RUN mamba install --yes \
    'altair' \
    'beautifulsoup4' \
    'bokeh' \
    'bottleneck' \
    'cloudpickle' \
    'conda-forge::blas=*=openblas' \
    'cython' \
    'dask' \
    'dill' \
    'h5py' \
    'ipympl' \
    'ipywidgets' \
    'jupyterlab-git' \
    'matplotlib-base' \
    'numba' \
    'numexpr' \
    'openpyxl' \
    'pandas' \
    'patsy' \
    'protobuf' \
    'pytables' \
    'scikit-image' \
    'scikit-learn' \
    'scipy' \
    'seaborn' \
    'sqlalchemy' \
    'statsmodels' \
    'sympy' \
    'widgetsnbextension' \
    'xlrd'
```

按功能分类：

| 类别 | 包 |
|------|-----|
| 数据处理 | pandas, bottleneck, numexpr, dask |
| 数值计算 | scipy, numpy（依赖）, sympy |
| 机器学习 | scikit-learn |
| 图像处理 | scikit-image |
| 可视化 | matplotlib-base, seaborn, bokeh, altair, ipympl |
| 交互控件 | ipywidgets, widgetsnbextension |
| 数据存储 | h5py, pytables, openpyxl, xlrd, sqlalchemy |
| 并行/编译 | numba, cython |
| 序列化 | cloudpickle, dill, patsy, protobuf |
| Web/解析 | beautifulsoup4 |
| Jupyter扩展 | jupyterlab-git |
| BLAS | blas=*=openblas（从conda-forge强制使用OpenBLAS） |

> **为什么用matplotlib-base而不是matplotlib？** matplotlib-base不包含PyQt等GUI后端依赖，体积更小。在无头容器环境中不需要GUI后端。

> **为什么强制OpenBLAS？** conda-forge的blas默认可能选择其他BLAS实现（如BLIS或MKL）。显式指定openblas确保数值计算的一致性和兼容性。

### Matplotlib字体缓存预热

```dockerfile
RUN MPLBACKEND=Agg python -c "import matplotlib" && \
    fix-permissions "/home/${NB_USER}"
```

首次导入matplotlib时会构建字体缓存。这一步在构建时执行，避免用户首次使用时的延迟。`MPLBACKEND=Agg`强制使用非交互式后端（容器中无显示）。

## 层选择指南

| 需求 | 选择 |
|------|------|
| 只需要Jupyter+CLI工具，Python包自己装 | minimal-notebook |
| Python科学计算开箱即用 | scipy-notebook |
| 需要TeX PDF导出 | minimal及以上（TeX在minimal层） |
| 需要编译C扩展 | scipy及以上（build-essential在scipy层） |
| 多语言（R/Julia）基础 | minimal-notebook（作为父层） |

## 相关概念

- [镜像层级架构](02-image-hierarchy.md)
- [Base Notebook层详解](04-base-notebook.md)
- [专项镜像详解](06-specialized-stacks.md)
