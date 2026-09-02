---
type: Concept
title: ROS 2 概念总览
description: ROS 2 核心概念——发布订阅中间件与 ROS graph、节点/话题/消息、分布式发现、DDS/RTPS 中间件与 QoS 策略、Topic Statistics（2020 年前后）
tags: [ros2, ROS graph, 节点, 话题, 消息, DDS, RTPS, QoS, 客户端库]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-86377a66ecef
    resource: /references/source-01.md
    title: 《ROS2 概念》
---
# ROS 2 概念总览

本文基于 2020 年前后教程，介绍 ROS 2 的核心概念体系：发布订阅中间件、节点/话题/消息/发现四要素、基于 DDS/RTPS 的通信底座，以及 QoS 与 Topic Statistics 等行为控制机制（F-324~F-332）。ROS 2 的通信底座 [DDS 与 QoS](../dds/index.md) 由独立知识包详解。

## 发布订阅中间件与 ROS graph

ROS 2 是基于**匿名发布/订阅（publish/subscribe）**机制的中间件，该机制允许消息（message）在不同的 ROS 进程之间传递；ROS graph 是所有 ROS 2 系统的核心（F-324）。

## 基本概念

文章列出的四个基本概念（F-325）：

- **Nodes**：使用 ROS 与其他节点通信的实体；
- **Messages**：订阅或发布主题时使用的 ROS 数据类型；
- **Topics**：节点将消息发布到主题或订阅主题以接收消息；
- **Discovery**：节点决定如何互相通信的自动过程。

## 节点与客户端库

节点是 ROS graph 的参与者，ROS 节点使用 ROS 客户端库（client library）与其他节点通信，节点之间的连接通过分布式发现过程建立（F-326）。ROS 2 团队维护的客户端库（F-327）：

- **rclcpp**：C++ client library；
- **rclpy**：Python client library；
- 核心 ROS 客户端库缩写为 **RCL**。

## 节点发现过程

节点发现过程描述（F-328）：

1. 节点启动后向具有相同 ROS domain（通过 `ROS_DOMAIN_ID` 环境变量设置）的网络上的其他节点通告其存在状态；
2. 节点定期通告其存在；
3. 节点下线时向其他节点通告；
4. 仅具有兼容 QoS 设置的节点建立连接。

## DDS/RTPS 中间件

ROS2 基于 DDS/RTPS 作为中间件，该中间件提供发现（discovery）、序列化（serialization）和传输（transportation）；RTPS（DDSI-RTPS）是 DDS 通过网络进行通信的有线协议（F-329）。

## DDS 实现与 rmw

文章列举的 DDS 实现（F-330）：

- RTI 的 Connext；
- ADLINK 的 OpenSplice；
- Eclipse 的 Cyclone DDS；
- eProsima 的 Fast RTPS。

将 DDS/RTPS 实现与 ROS2 结合需创建 "ROS Middleware interface"（rmw 接口）包（F-330）。

## QoS History 策略

QoS 策略中 History 包括两种（F-331）：

- **Keep last**：最多存储 N 个样本，可通过"队列深度"选项配置；
- **Keep all**：根据基础中间件的配置资源限制存储所有样本。

## Topic Statistics

Topic Statistics 提供的度量是接收到的消息寿命（age）与消息周期（period），统计量包括平均值、最大值、最小值、标准差和样本数，在移动窗口（moving window）中计算；文章说明 ROS 2 Foxy 的该功能仅限 C++（rclcpp）支持（F-332）。

## 现状

本文基于 2020 年前后教程，涉及的 **ROS 2 Dashing/Foxy 早期版本** 已过时（ROS 2 有新的发行版与更多客户端库能力），Topic Statistics 等功能的实现范围与默认 QoS 策略也可能演进。上述核心概念（发布订阅/节点/发现/DDS 底座）作为心智模型仍然有效，具体版本行为请以 ROS 2 官方当前文档为准。

## 事实溯源

- F-324~F-332（[source-01.md](../references/source-01.md)）
