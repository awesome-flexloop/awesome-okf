---
type: Reference
title: 信源：《无人驾驶数据集》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《无人驾驶数据集》信源登记——KITTI/Cityscapes/Mapillary/comma.ai/Udacity/ApolloCar3D/BDDV/nuScenes/H3D/CamVid 数据集盘点（2020 年前后）
tags: [数据集, KITTI, nuScenes, Cityscapes, BDDV, 信源登记, 简书, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-0066c78a2f43
    url: https://www.jianshu.com/p/0066c78a2f43
    title: 《无人驾驶数据集》
---
# 信源：《无人驾驶数据集》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中盘点无人驾驶数据集的文章，作者为"水之心"，内容时点为 2020 年前后。本 ecosystem 束的数据集盘点内容以其为事实依据（F-301~F-311）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | 无人驾驶数据集 |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/0066c78a2f43 |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- **KITTI**（http://www.cvlibs.net/datasets/kitti/）：文章称其为"目前最知名的自动驾驶数据集之一"（F-301）；使用高分辨率彩色和灰度立体相机、Velodyne 3D 激光扫描仪和高精度 GPS/IMU 惯性导航系统，在 10-100 Hz 下进行 6 小时拍摄的交通场景（F-302）
- **Cityscapes**：包含从 50 个不同城市的街景中记录的各种立体视频序列，高质量的像素级注释为 5000 帧，另有 20000 个弱注释帧（F-303）
- **Mapillary**：包含 25,000 个高分辨率图像，注释为 66 个对象类别，另有 37 个类别的特定于实例的标签，注释通过使用多边形描绘单个对象完成（F-304）
- **comma.ai's Driving Dataset**（archive.org 的 comma-dataset）：包含 7.25 小时的高速公路驾驶，10 个可变大小的视频片段以 20 Hz 频率录制，相机安装在 Acura ILX 2016 的挡风玻璃上，测量值转换为均匀的 100 Hz 时基（F-305）
- **Udacity's Driving Dataset**（优达学城的自动驾驶数据集）：包含 ROSBAG 训练数据，约 80 GB（F-306）
- **ApolloCar3D**：包含 5,277 个驾驶图像和超过 60K 的汽车实例，每辆汽车配备具有绝对模型尺寸和语义标记关键点的行业级 3D CAD 模型（F-307）
- **BDDV**（Berkeley 的大规模自动驾驶视频数据集）：包含超过 100K 的视频，包括图像级别标记、对象边界框、可行驶区域、车道标记和全帧实例分割（F-308）
- **nuscenes**：由安波福（aptiv）于 2019 年 3 月正式公开，包含从波士顿和新加坡收集的 1000 个"场景"，由 140 万张图像、39 万次激光雷达扫描和 140 万个 3D 人工注释边界框组成（F-309）
- **H3D - HRI-US**：由本田研究所于 2019 年 3 月发布（介绍见 arXiv:1903.01568），使用 3D LiDAR 扫描仪收集，包含 160 个拥挤且高度互动的交通场景，在 27,721 帧中共有 100 万个标记实例（F-310）
- **CamVid**（剑桥驾驶标签视频数据库）：第一个具有对象类语义标签的视频集合，数据库提供将每个像素与 32 个语义类之一关联的基础事实标签（F-311）

## 覆盖事实编号

F-301 ~ F-311
