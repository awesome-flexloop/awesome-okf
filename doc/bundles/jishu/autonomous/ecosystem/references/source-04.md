---
type: Reference
title: 信源：《wsl2 配置多环境的深度学习 GPU 环境》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《wsl2 配置多环境的深度学习 GPU 环境》信源登记——WSL2 CUDA 11.1 安装、GUI 参考、Anaconda、MXNet/TensorFlow/PyTorch conda 环境（2020 年前后）
tags: [WSL2, CUDA, Anaconda, MXNet, TensorFlow, PyTorch, 信源登记, 简书, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-98c8af1d2d33
    url: https://www.jianshu.com/p/98c8af1d2d33
    title: 《wsl2 配置多环境的深度学习 GPU 环境》
---
# 信源：《wsl2 配置多环境的深度学习 GPU 环境》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中介绍 WSL2 深度学习 GPU 环境搭建的文章，作者为"水之心"，内容时点为 2020 年前后。本 ecosystem 束的 WSL2 GPU 环境内容以其为事实依据（F-341~F-348）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | wsl2 配置多环境的深度学习 GPU 环境 |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/98c8af1d2d33 |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- 文章参考 Microsoft Docs "在 WSL 2 中启用 NVIDIA CUDA" 配置基础设置，并参考 NVIDIA 的 CUDA 工具包 11.1 下载页（target_os=Linux、target_distro=WSLUbuntu）（F-341）
- 文章给出 WSL2 安装 CUDA 11.1 的命令序列：`wget .../cuda-wsl-ubuntu.pin`、`sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600`、`wget .../cuda-repo-wsl-ubuntu-11-1-local_11.1.0-1_amd64.deb`、`sudo dpkg -i cuda-repo-wsl-ubuntu-11-1-local_11.1.0-1_amd64.deb`、`sudo apt-key add /var/cuda-repo-wsl-ubuntu-11-1-local/7fa2af80.pub`、`sudo apt-get update`、`sudo apt-get -y install cuda`（F-342）
- 文章提示安装过程中若报错 "404 Not Found [IP: 180.101.196.129 443]"，可尝试离线安装：`wget .../cuda_11.1.0_455.23.05_linux.run`、`sudo sh cuda_11.1.0_455.23.05_linux.run`（F-343）
- 文章给出 wsl2 安装 GUI 的两个参考链接：Harshit Yadav 的 "Install GUI Desktop in WSL2 Ubuntu 20.04 LTS in Windows 10" 与 "The complete WSL2 + GUI setup"（F-344）
- 文章说明下载 Anaconda Individual Edition 后执行 `sh Anaconda-...` 安装（F-345）
- 文章给出 MXNet 环境配置命令：`conda create -n mxnet python=3.9`、`conda install jupyter notebook`、`conda install cudnn=8 -c conda-forge`、`pip install mxnet-cu110`、`conda install ipykernel`、`python -m ipykernel install --name mxnet --user`、`pip install autopep8`（F-346）
- 文章给出 TensorFlow 环境配置命令：`conda create -n tensorflow python=3.9`、`conda install jupyter notebook`、`conda install cudnn=8 -c conda-forge`、`pip install tensorflow`、`conda install ipykernel`、`python -m ipykernel install --name tensorflow --user`（F-347）
- 文章给出 PyTorch 环境配置命令：`conda create -n torch python=3.9`、`conda install pytorch torchvision torchaudio cudatoolkit=11 -c pytorch -c conda-forge`、`conda install ipykernel`、`python -m ipykernel install --name torch --user`（F-348）

## 覆盖事实编号

F-341 ~ F-348
