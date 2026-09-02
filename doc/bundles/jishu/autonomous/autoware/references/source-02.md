---
type: Reference
title: 信源：《AutowareAuto 基础》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《AutowareAuto基础》信源登记——Autoware三系、2020年5月能力范围、ADE安装与目标检测演示命令链（2020 年前后）
tags: [autoware, Autoware.Auto, ADE, ROS2, 信源登记, 简书]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-8f97786e1631
    url: https://www.jianshu.com/p/8f97786e1631
    title: 《AutowareAuto 基础》
---
# 信源：《AutowareAuto 基础》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中介绍 Autoware.Auto 基础概念的文章，作者为"水之心"，内容时点为 2020 年前后（文中能力描述以 2020 年 5 月为参照）。本 autoware 束的 Autoware.Auto 基础内容以其为事实依据（F-333~F-340）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | AutowareAuto 基础 |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/8f97786e1631 |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- Autoware 是由 The Autoware Foundation 维护的软件堆栈，2020 年已有三个项目：Autoware.AI、Autoware.IO、Autoware.Auto（F-333）
- Autoware.AI 基于 ROS1，是第一个 Autoware 项目；Autoware.IO 是 Autoware 的接口，包含传感器驱动、有线控制器、SoC 板硬件程序；Autoware.Auto 基于 ROS 2，提供实时（RT）功能与更多安全措施（F-334）
- 2020 年 5 月 Autoware.Auto 具备使用 LIDAR 和 GPS 的全面定位、对 2D/3D 其他交通参与者的完整感知、相对简单的动作运动计划（F-335）
- 开发环境 ADE 是 Docker 的包装器，允许与 Docker 交互、配置与 docker 卷版本控制（F-336）
- ADE 安装命令：`wget .../ade-cli/uploads/.../ade+x86_64`、`mv ade+x86_64 ade`、`chmod +x ade`、`mv ade ~/.local/bin`、`which ade`（F-337）
- NVIDIA Docker（nvidia-container-toolkit）安装：添加 nvidia.github.io/nvidia-docker 的 GPG 公钥与软件源，`sudo apt-get install -y nvidia-container-toolkit`、`sudo systemctl restart docker`（F-338）
- ADE setup：`touch .adehome`、`git clone --recurse-submodules .../AutowareAuto.git`、`ade start`、`ade enter`；Autoware.Auto 使用 ROS2 Dashing，安装在 /opt/ros/dashing/，`ade$ ros2 -h` 确认（F-339）
- 目标检测演示流程：将 Palo Alto 行驶时记录的 pcap 文件移到 adehome 的 data/ 文件夹、克隆 ApexAI/autowareclass2020、`source /opt/AutowareAuto/setup.bash`，随后执行 `udpreplay`、`rviz2`、`velodyne_cloud_node_exe`、`robot_state_publisher`、`point_cloud_filter_transform_nodes`、`ray_ground_classifier_nodes`、`euclidean_cluster_nodes` 等命令（F-340）

## 覆盖事实编号

F-333 ~ F-340
