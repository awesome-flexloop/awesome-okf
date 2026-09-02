---
type: Reference
title: 信源：《WSL2 安装和配置无人驾驶系统 autoware.auto》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《WSL2安装和配置无人驾驶系统autoware.auto》信源登记——Ubuntu子系统与远程桌面、初始化构建测试、VcXsrv显示转发（2020 年前后）
tags: [autoware, WSL2, Ubuntu20.04, xrdp, VcXsrv, 信源登记, 简书]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-dfc1df4eb6ee
    url: https://www.jianshu.com/p/dfc1df4eb6ee
    title: 《WSL2 安装和配置无人驾驶系统 autoware.auto》
---
# 信源：《WSL2 安装和配置无人驾驶系统 autoware.auto》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中介绍在 WSL2 上安装配置 autoware.auto 的完整流程的文章，作者为"水之心"，内容时点为 2020 年前后。本 autoware 束的 WSL2 环境内容以其为事实依据（F-357~F-361）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | WSL2 安装和配置无人驾驶系统 autoware.auto |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/dfc1df4eb6ee |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- 初始步骤：安装 docker、安装 Anaconda3、使用 vscode 创建名为 autoware 的工作区、使用 Git 拉取 AutowareAuto 到 d:/adehome/AutowareAuto（可自定义），命令 `git clone --recursive https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git`（F-357）
- 需安装 Ubuntu20.04 子系统与远程桌面（参考文章《WSL2 配置深度学习环境》），并使用 conda 创建 autoware 环境安装 ade-cli（`pip install ade-cli`）（F-358）
- 初始化 Autoware.Auto：`sudo service xrdp restart`、`sudo service docker start`、`cd /mnt/d/adehome/AutowareAuto && conda activate autoware && ade start --update --enter`（F-359）
- 构建与测试：`colcon build && colcon test`、`colcon test-result`，激活 autoware.auto 命令为 `source /opt/AutowareAuto/setup.bash`（F-360）
- 处理 VcXsrv 不显示：PowerShell 执行 ipconfig 获取 IPv4 地址（示例 172.30.240.1），WSL2 的 ~/.bashrc 添加 `export DISPLAY=172.30.240.1:0`，`source ~/.bashrc` 激活，用 `ros2 launch autoware_demos ekf_ndt_smoothing_lgsvl.launch.py` 测试 X Play 效果（F-361）

## 覆盖事实编号

F-357 ~ F-361
