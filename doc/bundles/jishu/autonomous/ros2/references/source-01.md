---
type: Reference
title: 信源：《ROS2 概念》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《ROS2概念》信源登记——ROS2发布订阅中间件、节点/话题/消息/发现、DDS/RTPS中间件与QoS、Topic Statistics（2020 年前后）
tags: [ros2, DDS, QoS, 客户端库, 信源登记, 简书, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-86377a66ecef
    url: https://www.jianshu.com/p/86377a66ecef
    title: 《ROS2 概念》
---
# 信源：《ROS2 概念》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中介绍 ROS 2 概念的文章，作者为"水之心"，内容时点为 2020 年前后。本 ros2 束的 ROS 2 概念内容以其为事实依据（F-324~F-332）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | ROS2 概念 |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/86377a66ecef |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- ROS 2 是基于匿名发布/订阅（publish/subscribe）机制的中间件，允许消息在不同 ROS 进程之间传递；ROS graph 是所有 ROS 2 系统的核心（F-324）
- 基本概念：Nodes（与其他节点通信的实体）、Messages（订阅或发布主题时使用的 ROS 数据类型）、Topics（节点发布/订阅消息的主题）、Discovery（节点决定如何互相通信的自动过程）（F-325）
- 节点是 ROS graph 的参与者，使用 ROS 客户端库通信，节点之间的连接通过分布式发现过程建立（F-326）
- 官方维护的客户端库：rclcpp（C++）、rclpy（Python），核心 ROS 客户端库缩写为 RCL（F-327）
- 节点发现过程：节点启动后向相同 ROS domain（`ROS_DOMAIN_ID` 环境变量设置）网络上的其他节点通告存在状态；定期通告；下线时通告；仅兼容 QoS 设置的节点建立连接（F-328）
- ROS2 基于 DDS/RTPS 作为中间件，提供发现（discovery）、序列化（serialization）和传输（transportation）；RTPS（DDSI-RTPS）是 DDS 的网络有线协议（F-329）
- DDS 实现：RTI 的 Connext、ADLINK 的 OpenSplice、Eclipse 的 Cyclone DDS、eProsima 的 Fast RTPS；与 ROS2 结合需创建 "ROS Middleware interface"（rmw 接口）包（F-330）
- QoS History 策略：Keep last（最多存储 N 个样本，可配置"队列深度"）与 Keep all（根据基础中间件配置的资源限制存储所有样本）（F-331）
- Topic Statistics 度量：消息寿命（age）与消息周期（period），统计量含平均值/最大值/最小值/标准差/样本数，在移动窗口（moving window）中计算；ROS 2 Foxy 该功能仅限 C++（rclcpp）支持（F-332）

## 覆盖事实编号

F-324 ~ F-332
