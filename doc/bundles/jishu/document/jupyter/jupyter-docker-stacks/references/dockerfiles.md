---
type: Reference
title: "Dockerfile 源码索引"
description: "Jupyter Docker Stacks 各层镜像 Dockerfile 源码信源登记"
tags: [docker, dockerfile, image, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-foundation, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/Dockerfile", title: "docker-stacks-foundation/Dockerfile" }
  - { id: src-base, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/Dockerfile", title: "base-notebook/Dockerfile" }
  - { id: src-minimal, resource: "external/libs/jupyter/docker-stacks/images/minimal-notebook/Dockerfile", title: "minimal-notebook/Dockerfile" }
  - { id: src-scipy, resource: "external/libs/jupyter/docker-stacks/images/scipy-notebook/Dockerfile", title: "scipy-notebook/Dockerfile" }
  - { id: src-r, resource: "external/libs/jupyter/docker-stacks/images/r-notebook/Dockerfile", title: "r-notebook/Dockerfile" }
  - { id: src-julia, resource: "external/libs/jupyter/docker-stacks/images/julia-notebook/Dockerfile", title: "julia-notebook/Dockerfile" }
  - { id: src-datascience, resource: "external/libs/jupyter/docker-stacks/images/datascience-notebook/Dockerfile", title: "datascience-notebook/Dockerfile" }
  - { id: src-pytorch, resource: "external/libs/jupyter/docker-stacks/images/pytorch-notebook/Dockerfile", title: "pytorch-notebook/Dockerfile" }
  - { id: src-tensorflow, resource: "external/libs/jupyter/docker-stacks/images/tensorflow-notebook/Dockerfile", title: "tensorflow-notebook/Dockerfile" }
  - { id: src-pyspark, resource: "external/libs/jupyter/docker-stacks/images/pyspark-notebook/Dockerfile", title: "pyspark-notebook/Dockerfile" }
  - { id: src-allspark, resource: "external/libs/jupyter/docker-stacks/images/all-spark-notebook/Dockerfile", title: "all-spark-notebook/Dockerfile" }
  - { id: src-pytorch-cuda12, resource: "external/libs/jupyter/docker-stacks/images/pytorch-notebook/cuda12/Dockerfile", title: "pytorch-notebook/cuda12/Dockerfile" }
  - { id: src-pytorch-cuda13, resource: "external/libs/jupyter/docker-stacks/images/pytorch-notebook/cuda13/Dockerfile", title: "pytorch-notebook/cuda13/Dockerfile" }
  - { id: src-tf-cuda, resource: "external/libs/jupyter/docker-stacks/images/tensorflow-notebook/cuda/Dockerfile", title: "tensorflow-notebook/cuda/Dockerfile" }
---

# Dockerfile 源码索引

本文档登记 Jupyter Docker Stacks 各层镜像 Dockerfile 的源码路径与关键内容概要。

## 镜像层级与源码路径

| 镜像名 | 基础镜像 | 源码路径 | 核心内容 |
|--------|---------|---------|---------|
| docker-stacks-foundation | ubuntu:24.04 | images/docker-stacks-foundation/Dockerfile | OS系统包、用户创建、Micromamba安装Python/conda/mamba |
| base-notebook | docker-stacks-foundation | images/base-notebook/Dockerfile | JupyterLab/Notebook/Hub、pandoc、HEALTHCHECK |
| minimal-notebook | base-notebook | images/minimal-notebook/Dockerfile | 常用CLI工具、TeX Live、git/ssh、R配置 |
| scipy-notebook | minimal-notebook | images/scipy-notebook/Dockerfile | 科学计算Python包（pandas/scipy/matplotlib等） |
| r-notebook | minimal-notebook | images/r-notebook/Dockerfile | R语言 + IRKernel + tidyverse |
| julia-notebook | minimal-notebook | images/julia-notebook/Dockerfile | Julia语言 + IJulia kernel |
| datascience-notebook | scipy-notebook | images/datascience-notebook/Dockerfile | Python+R+Julia三语言全栈 |
| pytorch-notebook | scipy-notebook | images/pytorch-notebook/Dockerfile | PyTorch CPU版（pip安装） |
| tensorflow-notebook | scipy-notebook | images/tensorflow-notebook/Dockerfile | TensorFlow（pip安装） |
| pyspark-notebook | scipy-notebook | images/pyspark-notebook/Dockerfile | OpenJDK 21 + Spark + PyArrow |
| all-spark-notebook | pyspark-notebook | images/all-spark-notebook/Dockerfile | PySpark + R(sparklyr/ggplot2) |

## CUDA 变体

| 镜像 | 源码路径 | 说明 |
|------|---------|------|
| pytorch-notebook CUDA 12 | images/pytorch-notebook/cuda12/Dockerfile | NVIDIA CUDA 12 + PyTorch GPU |
| pytorch-notebook CUDA 13 | images/pytorch-notebook/cuda13/Dockerfile | NVIDIA CUDA 13 + PyTorch GPU |
| tensorflow-notebook CUDA | images/tensorflow-notebook/cuda/Dockerfile | NVIDIA CUDA + TensorFlow GPU |

## 关键构建参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| ROOT_IMAGE | default_root_image | Foundation层根镜像，可替换 |
| PYTHON_VERSION | 3.13 | Python版本 |
| REGISTRY | quay.io | 镜像仓库 |
| OWNER | jupyter | 仓库命名空间 |
| spark_version | (latest) | Spark版本 |
| openjdk_version | 21 | OpenJDK版本 |
