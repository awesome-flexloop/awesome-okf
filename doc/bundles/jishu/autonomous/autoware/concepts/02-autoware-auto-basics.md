---
type: Concept
title: Autoware.Auto 基础
description: Autoware 自动驾驶开源栈三系（AI/IO/Auto）、2020 年 5 月 Autoware.Auto 能力范围、ADE 安装与目标检测演示命令链（2020 年前后）
tags: [autoware, Autoware.Auto, Autoware.AI, Autoware.IO, ADE, ROS2, 目标检测]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-8f97786e1631
    resource: /references/source-02.md
    title: 《AutowareAuto 基础》
---
# Autoware.Auto 基础

本文基于 2020 年前后教程，介绍 Autoware 自动驾驶开源软件栈的整体面貌、Autoware.Auto 在 2020 年 5 月的能力范围，以及从 ADE 安装到目标检测演示的完整命令链（F-333~F-340）。

## Autoware 与三系

Autoware 是由 The Autoware Foundation 维护的软件堆栈，2020 年已有三个 Autoware 项目：Autoware.AI、Autoware.IO、Autoware.Auto（F-333）。

## 三系定位与分工

三个项目的定位（F-334）：

- **Autoware.AI**：基于 ROS1，是第一个 Autoware 项目；
- **Autoware.IO**：Autoware 的接口，包含传感器驱动程序（sensor drivers）、有线控制器（by-wire controllers）、SoC 板的硬件相关程序；
- **Autoware.Auto**：基于 ROS 2，提供实时（RT）功能和更多安全措施。

## 2020 年 5 月的 Autoware.Auto 能力

2020 年 5 月 Autoware.Auto 具备的能力（F-335）：

- 使用 LIDAR 和 GPS 的**全面定位**功能；
- 对 2D 和 3D 中其他交通参与者的**完整感知**；
- 相对简单的**动作运动计划**。

## ADE：Docker 的包装器

开发环境 ADE 是 Docker 的包装器，允许与 Docker 交互（如启动/停止 docker）、配置和 docker 卷版本控制（F-336）。

## 安装 ADE 命令行工具

ADE 安装命令（F-337）：

```bash
wget https://gitlab.com/ApexAI/ade-cli/uploads/85a5af81339fe55555ee412f9a3a734b/ade+x86_64
mv ade+x86_64 ade
chmod +x ade
mv ade ~/.local/bin
which ade
```

## 安装 NVIDIA Docker

NVIDIA Docker（nvidia-container-toolkit）安装：添加 nvidia.github.io/nvidia-docker 的 GPG 公钥与软件源，随后执行（F-338）：

```bash
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## 初始化 ADE 环境与 ROS2 Dashing

ADE setup 命令（F-339）：

```bash
touch .adehome
git clone --recurse-submodules https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git
ade start
ade enter
```

文章说明 Autoware.Auto 使用 **ROS2 Dashing**，安装在 `/opt/ros/dashing/`，可通过 `ade$ ros2 -h` 确认安装（F-339）。

## 目标检测演示

目标检测演示流程与命令（F-340）：

1. 将 Palo Alto 行驶时记录的 pcap 文件（UDP 软件包集合）移到 adehome 目录的 `data/` 文件夹；
2. 克隆 ApexAI/autowareclass2020 仓库；
3. `source /opt/AutowareAuto/setup.bash`；
4. 依次执行演示命令：

```bash
udpreplay ~/data/route_small_loop_rw-127.0.0.1.pcap
rviz2 -d ...
ros2 run velodyne_node velodyne_cloud_node_exe ...
ros2 run robot_state_publisher robot_state_publisher .../lexus_rx_450h.urdf
ros2 run point_cloud_filter_transform_nodes ...
ros2 run ray_ground_classifier_nodes ...
ros2 run euclidean_cluster_nodes ...
```

## 现状

本文基于 2020 年前后教程，涉及的 **Autoware.Auto 早期版本、ROS2 Dashing、ADE 早期命令行工具** 均已有较大演进，`ade+x86_64` 下载链接与 AutowareAuto 仓库路径也可能发生变化。上述内容只作历史方法与概念参考，当前安装、能力清单与演示流程请以 Autoware 官方当前文档为准。

## 事实溯源

- F-333~F-340（[source-02.md](../references/source-02.md)）
