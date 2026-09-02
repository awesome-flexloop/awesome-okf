---
type: Concept
title: 无人驾驶常用数据集盘点
description: 2020 年前后无人驾驶常用数据集盘点——KITTI/Cityscapes/Mapillary/comma.ai/Udacity/ApolloCar3D/BDDV/nuScenes/H3D/CamVid 规模与用途（2020 年前后）
tags: [数据集, KITTI, nuScenes, Cityscapes, BDDV, ApolloCar3D, 自动驾驶, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-0066c78a2f43
    resource: /references/source-01.md
    title: 《无人驾驶数据集》
---
# 无人驾驶常用数据集盘点

本文基于 2020 年前后教程，盘点无人驾驶领域常用数据集及其规模特点（F-301~F-311）。这些数据集覆盖自动驾驶研究中的传感器配置、目标检测、语义分割、3D 标注等核心任务。

## KITTI

KITTI（http://www.cvlibs.net/datasets/kitti/）被文章称为"目前最知名的自动驾驶数据集之一"（F-301）。数据集使用高分辨率彩色和灰度立体相机、Velodyne 3D 激光扫描仪和高精度 GPS/IMU 惯性导航系统，在 10-100 Hz 下进行 6 小时拍摄的交通场景（F-302）。

## Cityscapes

Cityscapes 包含从 50 个不同城市的街景中记录的各种立体视频序列，高质量的像素级注释为 5000 帧，另有 20000 个弱注释帧（F-303）。

## Mapillary

Mapillary 包含 25,000 个高分辨率图像，注释为 66 个对象类别，另有 37 个类别的特定于实例的标签；注释通过使用多边形描绘单个对象完成（F-304）。

## comma.ai's Driving Dataset

comma.ai 驾驶数据集（archive.org 的 comma-dataset）包含 7.25 小时的高速公路驾驶，10 个可变大小的视频片段以 20 Hz 频率录制；相机安装在 Acura ILX 2016 的挡风玻璃上，测量值转换为均匀的 100 Hz 时基（F-305）。

## Udacity's Driving Dataset

优达学城（Udacity）的自动驾驶数据集包含 ROSBAG 训练数据，约 80 GB（F-306）。

## ApolloCar3D

ApolloCar3D 包含 5,277 个驾驶图像和超过 60K 的汽车实例，每辆汽车配备具有绝对模型尺寸和语义标记关键点的行业级 3D CAD 模型（F-307）。

## BDDV

BDDV（Berkeley 的大规模自动驾驶视频数据集）包含超过 100K 的视频，包括图像级别标记、对象边界框、可行驶区域、车道标记和全帧实例分割（F-308）。

## nuScenes

nuscenes 由安波福（aptiv）于 2019 年 3 月正式公开，包含从波士顿和新加坡收集的 1000 个"场景"，由 140 万张图像、39 万次激光雷达扫描和 140 万个 3D 人工注释边界框组成（F-309）。

## H3D - HRI-US

H3D 由本田研究所于 2019 年 3 月发布（介绍见 arXiv:1903.01568），使用 3D LiDAR 扫描仪收集，包含 160 个拥挤且高度互动的交通场景，在 27,721 帧中共有 100 万个标记实例（F-310）。

## CamVid

CamVid（剑桥驾驶标签视频数据库）是第一个具有对象类语义标签的视频集合，数据库提供将每个像素与 32 个语义类之一关联的基础事实标签（F-311）。

## 现状

本文基于 2020 年前后教程，所列数据集规模与开放范围是当时状态，此后无人驾驶领域又出现了许多新数据集，既有数据集的版本与标注也在持续扩充。数据集清单请以各数据集的官方当前页面为准。

## 事实溯源

- F-301~F-311（[source-01.md](../references/source-01.md)）
