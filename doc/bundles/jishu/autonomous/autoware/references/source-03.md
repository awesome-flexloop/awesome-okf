---
type: Reference
title: 信源：《WSL2 之 autoware.auto》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《WSL2之autoware.auto》信源登记——WSL2 X桌面支持、docker安装、conda autoware环境、免sudo配置与构建测试（2020 年前后）
tags: [autoware, WSL2, docker, conda, ade-cli, 信源登记, 简书]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-a95f95276fec
    url: https://www.jianshu.com/p/a95f95276fec
    title: 《WSL2 之 autoware.auto》
---
# 信源：《WSL2 之 autoware.auto》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中介绍在 WSL2 中搭建 autoware.auto 环境的文章，作者为"水之心"，内容时点为 2020 年前后。本 autoware 束的 WSL2 环境内容以其为事实依据（F-349~F-353）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | WSL2 之 autoware.auto |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/a95f95276fec |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- WSL2 提供 X 桌面支持，不再需要安装 xrdp（F-349）
- WSL2 安装 docker：安装依赖 apt-transport-https、ca-certificates、curl、gnupg-agent、software-properties-common；`curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -` 信任 GPG 公钥；添加 `deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable` 软件源；`sudo apt-get install docker-ce docker-ce-cli containerd.io`（F-350）
- 创建 autoware 环境并安装 ade-cli：`conda create --name autoware python=3.7`、`conda activate autoware && pip install ade-cli`（F-351）
- 免 sudo 使用 docker：`docker login`、`sudo groupadd docker`、`sudo gpasswd -a ${USER} docker`、`sudo service docker restart`、`newgrp - docker`（F-352）
- 配置与测试 Autoware.Auto：`sudo service docker start`、`cd /mnt/d/adehome/AutowareAuto && conda activate autoware && ade start --update --enter`、`ade$ cd AutowareAuto`、`ade$ colcon build`、`ade$ colcon test`、`ade$ colcon test-result`；测试执行 `source /opt/AutowareAuto/setup.bash`、`ros2 launch autoware_demos ekf_ndt_smoothing_lgsvl.launch.py`（F-353）

## 覆盖事实编号

F-349 ~ F-353
