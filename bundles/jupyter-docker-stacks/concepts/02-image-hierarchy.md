---
type: Concept
title: "镜像层级架构"
description: "Jupyter Docker Stacks 12个镜像的分层继承关系、每层职责、选型决策树"
tags: [architecture, image-hierarchy, layers, inheritance]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-makefile, resource: "/references/makefile-ci-source.md", title: "Makefile构建顺序" }
  - { id: src-hierarchy, resource: "/references/tagging-source.md", title: "镜像层级定义" }
  - { id: src-dockerfiles, resource: "/references/dockerfiles.md", title: "Dockerfile索引" }
---

# 镜像层级架构

Jupyter Docker Stacks 采用**严格的线性层级继承**体系，从操作系统基础层到全功能科学计算环境共6层12个核心镜像。每层只添加特定领域的依赖，保持"最小增量"原则。

## 继承树

```
ubuntu:24.04
  └── docker-stacks-foundation      (L1: OS + 用户 + Conda/Python/Mamba)
        └── base-notebook           (L2: Jupyter Server/Lab/Notebook/Hub)
              └── minimal-notebook  (L3: CLI工具 + TeX Live + git)
                    ├── r-notebook           (L4a: R语言)
                    ├── julia-notebook       (L4b: Julia语言)
                    └── scipy-notebook      (L4c: Python科学计算)
                          ├── tensorflow-notebook  (L5a: TensorFlow)
                          ├── pytorch-notebook     (L5b: PyTorch)
                          ├── datascience-notebook (L5c: Python+R+Julia)
                          └── pyspark-notebook     (L5d: Spark)
                                └── all-spark-notebook (L6: PySpark+R)
```

## 各层职责

### L1: docker-stacks-foundation（基础层）

**基础镜像**：ubuntu:24.04 (sha256 digest固定)

**安装内容**：
- OS系统包：ca-certificates, locales, netbase, sudo, tini, wget
- 通过 Micromamba 安装：Python 3.13, Mamba, Conda, jupyter_core
- 创建 `jovyan` 用户（UID 1000, GID 100）
- 配置 ENTRYPOINT 为 `tini → start.sh`
- 创建 hook 目录：`start-notebook.d/` 和 `before-notebook.d/`

**设计意图**：这是所有镜像的公共基础，包含操作系统配置、用户模型、Conda环境和启动框架。不包含任何Jupyter应用。

### L2: base-notebook（Jupyter核心层）

**基础镜像**：docker-stacks-foundation

**安装内容**：
- OS包：fonts-liberation, pandoc, run-one
- Conda包：jupyterhub-singleuser, jupyterlab, nbclassic, notebook>=7.2.2
- 配置：Jupyter Server配置文件、HEALTHCHECK、EXPOSE 8888
- 设置 CMD 为 `start-notebook.py`

**设计意图**：提供最小可用的Jupyter环境。适合作为自定义镜像的基础，或只需要核心Jupyter功能的场景。

### L3: minimal-notebook（工具增强层）

**基础镜像**：base-notebook

**安装内容**：
- OS包：curl, git, nano-tiny, tzdata, unzip, vim-tiny, openssh-client, less, texlive-xetex, texlive-fonts-recommended, texlive-plain-generic, xclip
- R mimetype配置（Rprofile.site）
- setup-scripts/（供下游镜像使用的安装脚本）

**设计意图**：添加日常开发需要的命令行工具和文档导出能力（TeX Live用于nbconvert PDF导出）。这是**多语言镜像（R/Julia）的共同父层**。

### L4a: r-notebook（R语言层）

**基础镜像**：minimal-notebook

**安装内容**：R语言环境（r-base）+ tidyverse + shiny + IRKernel + 常用R包

### L4b: julia-notebook（Julia语言层）

**基础镜像**：minimal-notebook

**安装内容**：Julia语言 + IJulia kernel + 常用包（通过setup_julia.py和setup-julia-packages.bash安装）

### L4c: scipy-notebook（Python科学计算层）

**基础镜像**：minimal-notebook

**安装内容**：
- OS包：build-essential, cm-super, dvipng, ffmpeg
- Conda包：pandas, scipy, matplotlib, seaborn, scikit-learn, scikit-image, sympy, cython, dask, h5py, sqlalchemy, statsmodels, bokeh, altair, ipywidgets, jupyterlab-git 等
- 预构建matplotlib字体缓存

### L5a: tensorflow-notebook（TensorFlow层）

**基础镜像**：scipy-notebook

**安装内容**：jupyter-server-proxy, protobuf>=5.28.3,<6 + tensorflow（x86_64上为tensorflow-cpu）

CUDA变体在 `cuda/` 子目录提供GPU支持。

### L5b: pytorch-notebook（PyTorch层）

**基础镜像**：scipy-notebook

**安装内容**：通过pip从PyTorch官方索引安装torch, torchaudio, torchvision（CPU版）

CUDA变体：`cuda12/` 和 `cuda13/` 子目录提供GPU支持。

### L5c: datascience-notebook（数据科学全栈层）

**基础镜像**：scipy-notebook

**安装内容**：Python+R+Julia三语言全栈（包含rpy2用于Python-R互操作）

### L5d: pyspark-notebook（Spark层）

**基础镜像**：scipy-notebook

**安装内容**：OpenJDK 21 JRE + Apache Spark（通过setup_spark.py自动下载）+ pyarrow + pandas版本对齐，EXPOSE 4040（Spark UI）

### L6: all-spark-notebook（Spark+R层）

**基础镜像**：pyspark-notebook

**安装内容**：在PySpark基础上添加R + sparklyr + ggplot2，支持SparkR和sparklyr

## 选型决策树

```
需要Jupyter环境？
├─ 只要最小核心，自己装包？ → base-notebook
├─ 需要CLI工具和PDF导出？ → minimal-notebook
├─ Python科学计算（pandas/scipy/sklearn）？
│   └─ scipy-notebook
│       ├─ 需要R语言？ → r-notebook（轻量）或 datascience-notebook（含Python+Julia）
│       ├─ 需要Julia？ → julia-notebook 或 datascience-notebook
│       ├─ 需要PyTorch？ → pytorch-notebook（CUDA变体用于GPU）
│       ├─ 需要TensorFlow？ → tensorflow-notebook（CUDA变体用于GPU）
│       ├─ 需要三语言全栈？ → datascience-notebook
│       └─ 需要Spark？
│           ├─ 只要PySpark？ → pyspark-notebook
│           └─ 需要Spark+R？ → all-spark-notebook
└─ 完全自定义，从OS开始？ → docker-stacks-foundation
```

## 镜像标签维度

每个镜像携带多组标签，由tagging系统自动生成：

| 标签类型 | 示例 | 生成器 |
|---------|------|--------|
| 日期标签 | `2026-07-28` | date_tagger |
| Git SHA | `sha-abc1234` | commit_sha_tagger |
| Ubuntu版本 | `ubuntu-24.04` | ubuntu_version_tagger |
| Python版本 | `python-3.13`, `python-3.13.14` | python_tagger |
| JupyterLab版本 | `lab-4.3.x` | jupyter_lab_tagger |
| 平台前缀 | `aarch64-...`, `x86_64-...` | 平台标记 |

## 相关概念

- [项目介绍](00-introduction.md)
- [Foundation层详解](03-foundation-layer.md)
- [Base Notebook层详解](04-base-notebook.md)
- [Minimal到SciPy层](05-minimal-scipy.md)
- [专项镜像详解](06-specialized-stacks.md)
