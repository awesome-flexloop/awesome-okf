---
type: Concept
title: WSL2 环境搭建 Autoware.Auto
description: 在 WSL2（Windows Subsystem for Linux 2）中搭建 Autoware.Auto 开发环境的两种路径——docker/conda/ade-cli 安装、X 桌面支持与 VcXsrv 显示转发配置（2020 年前后）
tags: [autoware, WSL2, docker, conda, ade-cli, VcXsrv, 环境搭建]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-a95f95276fec
    resource: /references/source-03.md
    title: 《WSL2 之 autoware.auto》
  - id: jianshu-dfc1df4eb6ee
    resource: /references/source-04.md
    title: 《WSL2 安装和配置无人驾驶系统 autoware.auto》
---
# WSL2 环境搭建 Autoware.Auto

本文基于 2020 年前后教程，介绍在 WSL2 中搭建 Autoware.Auto 开发环境的两种路径：一种直接利用 WSL2 的 X 桌面支持（F-349~F-353），另一种借助 Ubuntu 子系统加远程桌面与 VcXsrv 显示转发（F-357~F-361）。两条路径的共同底座是 docker、conda 与 ade-cli（[ADE 开发环境](01-ubuntu-ade-environment.md)）。

> 本文所有命令为 2020 年前后作者实测记录，仅作历史方法参考，详见文末[现状](#现状)。

## 路径一：WSL2 的 X 桌面支持

### WSL2 提供 X 桌面支持

文章说明 WSL2 提供 X 桌面支持，不再需要安装 xrdp（F-349）。

### 安装 Docker

WSL2 中安装 docker 的步骤（F-350）：

1. 安装依赖：`apt-transport-https`、`ca-certificates`、`curl`、`gnupg-agent`、`software-properties-common`；
2. 信任 Docker 的 GPG 公钥：

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

3. 添加软件源：

```bash
deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable
```

4. 安装：

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

### 创建 autoware 环境并安装 ade-cli

使用 conda 创建 autoware 环境并安装 ade-cli（F-351）：

```bash
conda create --name autoware python=3.7
conda activate autoware && pip install ade-cli
```

### 免 sudo 使用 docker

配置免 sudo 使用 docker 命令（F-352）：

```bash
docker login
sudo groupadd docker
sudo gpasswd -a ${USER} docker
sudo service docker restart
newgrp - docker
```

### 初始化与构建测试 Autoware.Auto

在 autoware 环境下配置与测试（F-353）：

```bash
sudo service docker start
cd /mnt/d/adehome/AutowareAuto && conda activate autoware && ade start --update --enter
ade$ cd AutowareAuto
ade$ colcon build
ade$ colcon test
ade$ colcon test-result
```

测试时执行（F-353）：

```bash
source /opt/AutowareAuto/setup.bash
ros2 launch autoware_demos ekf_ndt_smoothing_lgsvl.launch.py
```

## 路径二：Ubuntu 子系统 + 远程桌面

### 初始步骤

文章给出的初始步骤：安装 docker、安装 Anaconda3、使用 vscode 创建名为 autoware 的工作区、使用 Git 拉取 AutowareAuto 到 `d:/adehome/AutowareAuto`（可自定义）（F-357）：

```bash
git clone --recursive https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git
```

### Ubuntu20.04 子系统与远程桌面

需安装 Ubuntu20.04 子系统与远程桌面（参考文章《WSL2 配置深度学习环境》），并使用 conda 创建 autoware 环境安装 ade-cli（F-358）：

```bash
pip install ade-cli
```

### 初始化 Autoware.Auto

初始化命令（F-359）：

```bash
sudo service xrdp restart
sudo service docker start
cd /mnt/d/adehome/AutowareAuto && conda activate autoware && ade start --update --enter
```

### 构建与测试

构建与测试命令（F-360）：

```bash
colcon build && colcon test
colcon test-result
```

激活 autoware.auto 的命令为（F-360）：

```bash
source /opt/AutowareAuto/setup.bash
```

### VcXsrv 显示转发

处理 VcXsrv 不显示的方法（F-361）：在 PowerShell 终端执行 `ipconfig` 获取 IPv4 地址（示例 172.30.240.1），在 WSL2 的 `~/.bashrc` 添加 DISPLAY 导出并激活：

```bash
export DISPLAY=172.30.240.1:0
source ~/.bashrc
```

随后用如下命令测试 X Play 效果（F-361）：

```bash
ros2 launch autoware_demos ekf_ndt_smoothing_lgsvl.launch.py
```

## 现状

本文基于 2020 年前后教程，涉及的 **WSL2 早期版本、Ubuntu 20.04、Autoware.Auto 早期版本、apt-key 与老式 docker 安装方式** 均已发生较大变化，且 WSL2 已原生支持图形界面（WSLg），显示转发方式也已不同。上述命令只作历史方法与概念参考，当前安装请以 WSL2 与 Autoware 官方当前文档为准。

## 事实溯源

- 路径一：F-349~F-353（[source-03.md](../references/source-03.md)）
- 路径二：F-357~F-361（[source-04.md](../references/source-04.md)）
