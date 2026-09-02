---
type: Concept
title: WSL2 GPU 深度学习环境搭建
description: 2020 年前后 WSL2 配置多环境深度学习 GPU 环境——CUDA 11.1 安装与离线回退、Anaconda、MXNet/TensorFlow/PyTorch conda 环境（2020 年前后）
tags: [WSL2, CUDA, Anaconda, MXNet, TensorFlow, PyTorch, GPU, 深度学习]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-98c8af1d2d33
    resource: /references/source-04.md
    title: 《wsl2 配置多环境的深度学习 GPU 环境》
---
# WSL2 GPU 深度学习环境搭建

本文基于 2020 年前后教程，介绍在 WSL2 上配置多环境深度学习 GPU 环境的步骤（F-341~F-348）。内容为作者实测记录，适合作为历史方法参考。

## 基础设置

文章参考 Microsoft Docs "在 WSL 2 中启用 NVIDIA CUDA" 配置基础设置，并参考 NVIDIA 的 CUDA 工具包 11.1 下载页（target_os=Linux、target_distro=WSLUbuntu）（F-341）。

## 安装 CUDA 11.1

文章给出 WSL2 安装 CUDA 11.1 的命令序列（F-342）：

```bash
wget .../cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget .../cuda-repo-wsl-ubuntu-11-1-local_11.1.0-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-11-1-local_11.1.0-1_amd64.deb
sudo apt-key add /var/cuda-repo-wsl-ubuntu-11-1-local/7fa2af80.pub
sudo apt-get update
sudo apt-get -y install cuda
```

> 命令中的 `...` 为原文省略的完整下载 URL 前缀，此处按原文要点转录。

## 离线安装回退

文章提示安装过程中若报错 "404 Not Found [IP: 180.101.196.129 443]"，可尝试离线安装（F-343）：

```bash
wget .../cuda_11.1.0_455.23.05_linux.run
sudo sh cuda_11.1.0_455.23.05_linux.run
```

## GUI 参考

文章给出 wsl2 安装 GUI 的两个参考链接：Harshit Yadav 的 "Install GUI Desktop in WSL2 Ubuntu 20.04 LTS in Windows 10" 与 "The complete WSL2 + GUI setup"（F-344）。

## Anaconda 安装

文章说明下载 Anaconda Individual Edition 后执行 `sh Anaconda-...` 安装（F-345）。

## 多框架 conda 环境

文章给出三个深度学习框架的 conda 环境配置命令：

**MXNet**（F-346）：

```bash
conda create -n mxnet python=3.9
conda install jupyter notebook
conda install cudnn=8 -c conda-forge
pip install mxnet-cu110
conda install ipykernel
python -m ipykernel install --name mxnet --user
pip install autopep8
```

**TensorFlow**（F-347）：

```bash
conda create -n tensorflow python=3.9
conda install jupyter notebook
conda install cudnn=8 -c conda-forge
pip install tensorflow
conda install ipykernel
python -m ipykernel install --name tensorflow --user
```

**PyTorch**（F-348）：

```bash
conda create -n torch python=3.9
conda install pytorch torchvision torchaudio cudatoolkit=11 -c pytorch -c conda-forge
conda install ipykernel
python -m ipykernel install --name torch --user
```

## 现状

本文基于 2020 年前后教程，涉及的 **CUDA 11.1、WSL2 早期版本与老式 apt-key 安装方式** 已过时。当前 WSL2 官方已提供 GPU 加速支持，CUDA 与各框架的安装方式（如新版 conda 通道、NVIDIA 容器工具包）均有演进。上述"conda 多环境隔离 + 为内核注册 Jupyter"的思路仍然有效，具体命令请以 NVIDIA、Anaconda 与各框架的官方当前文档为准。

## 事实溯源

- F-341~F-348（[source-04.md](../references/source-04.md)）
