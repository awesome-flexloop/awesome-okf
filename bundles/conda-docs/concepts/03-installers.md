---
okf_version: "0.2"
type: "concept"
title: "双发行版策略：Miniconda 与 Miniforge"
sources:
  - docs/source/index.rst
  - docs/source/user/install/index.rst
  - docs/source/user/install/regular.rst
  - docs/source/user/install/miniforge.rst
  - docs/source/user/install/docker.rst
---

# 双发行版策略：Miniconda 与 Miniforge

conda-docs 文档门户同时维护两套 Conda 发行版的安装文档：**Miniconda**（Anaconda 官方发行）和 **Miniforge**（conda-forge 社区驱动发行）。两者共享 Conda 核心引擎，但在默认频道、许可证、目标用户上有明确差异。

## 发行版对比

| 维度 | Miniconda | Miniforge |
|---|---|---|
| 维护方 | Anaconda, Inc. | conda-forge 社区 |
| 默认频道 | `defaults`（Anaconda 仓库） | `conda-forge`（社区仓库） |
| 许可证 | Anaconda EULA（商业使用需付费） | BSD 3-Clause（完全开源） |
| 预装包 | conda + Python + 基础依赖 | conda + mamba + Python + conda-forge 配置 |
| 平台支持 | Linux/macOS/Windows/Linux s390x | Linux/macOS/Windows + 更多架构（arm64等） |
| 安装脚本名 | Miniconda3-latest-*.{sh,exe,pkg} | Miniforge3-*.{sh,exe} |

## Miniconda 安装要点

**安装脚本下载地址**：
```
https://repo.anaconda.com/miniconda/Miniconda3-latest-{platform}.{ext}
```

**命令行静默安装示例**（Linux/macOS）：
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
```

**关键参数**：
- `-b`：batch 模式，无交互
- `-p PREFIX`：指定安装路径
- `-u`：升级现有安装

## Miniforge 安装要点

**安装脚本下载地址**：
```
https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-{platform}.{ext}
```

**命令行静默安装示例**（Linux/macOS）：
```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3
```

**Miniforge 优势**：
- 预装 mamba（C++ 实现的快速包解析器）
- 默认使用 conda-forge 频道，包数量更多、更新更快
- 无商业许可证限制
- 对 ARM 架构（Apple Silicon、AWS Graviton）原生支持更好

## Docker 镜像

文档还提供了官方 Docker 镜像安装方式：

```bash
# Miniconda
docker run -it --rm continuumio/miniconda3:latest

# Miniforge
docker run -it --rm condaforge/miniforge3:latest
```

## 安装后验证

安装完成后验证：
```bash
conda --version
conda info
conda config --show channels
```

> 📌 **选择建议**：企业/商业环境优先评估许可证合规（Miniconda 默认频道需 Anaconda 商业许可）；社区/学术/个人开发推荐 Miniforge，包更全且无许可问题。
