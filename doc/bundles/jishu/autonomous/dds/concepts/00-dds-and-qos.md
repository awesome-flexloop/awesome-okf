---
type: Concept
title: DDS 与 QoS
description: DDS 数据分发服务核心概念——OMG 中间件标准、QoS 控制的数据共享、域隔离、全局数据空间、动态发现、安全机制、DomainParticipant（2020 年前后）
tags: [DDS, OMG, QoS, 中间件, 发布订阅, 动态发现, 自动驾驶, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-46945ab25c01
    resource: /references/source-01.md
    title: 《数据分发服务：DDS》
---
# DDS 与 QoS

本文基于 2020 年前后教程（译自 dds-foundation.org 的 "What is DDS"），介绍数据分发服务（DDS）的核心概念：中间件标准定位、QoS 控制的数据共享、域隔离、全局数据空间、动态发现、安全机制与 DomainParticipant（F-312~F-318）。ROS 2 的通信底座建立在 DDS/RTPS 之上（[ROS 2 概念总览](../ros2/index.md)）。

## DDS 是什么

DDS（数据分发服务，Data Distribution Service™）是来自 Object Management Group®（OMG®）的中间件协议和 API 标准，提供以数据为中心的连接（F-312）。

## QoS 控制的数据共享

DDS 提供 **QoS 控制**的数据共享，应用程序通过发布和订阅由其主题名称标识的主题进行通信；订阅可以指定时间和内容过滤器，仅获取在主题上发布的数据的子集（F-313）。

## 域隔离

不同的 DDS 域（domain）彼此完全独立，DDS 域之间没有数据共享（F-314）。

## 全局数据空间

DDS 概念上的"全局数据空间"（global data space），对应用程序来说看起来像是通过 API 访问的本地内存；文章陈述 DDS 进行**对等通信**（F-315）。

## 动态发现

DDS 提供发布者和订阅者的**动态发现**（Dynamic Discovery），该机制使 DDS 应用程序可扩展，应用程序不必知道或配置通信端点（endpoint）（F-316）。

## 安全机制

DDS 包括为信息分发提供**身份验证、访问控制、机密性和完整性**的安全机制；DDS Security 使用**分散的点对点体系结构**（F-317）。

## DomainParticipant

DDS DomainParticipant 代表域中应用程序的本地成员身份，并充当 DDS 发布者、订阅者、主题、MultiTopics 和 ContentFilteredTopics 的工厂（F-318）。

## 现状

本文基于 2020 年前后教程（译自 dds-foundation.org），DDS 标准规范自发布以来持续演进，QoS 策略集与安全规范（DDS Security）也在扩展。上述核心概念（以数据为中心、QoS 数据共享、域隔离、动态发现）作为心智模型仍然有效，具体规范细节请以 OMG 与 DDS Foundation 的当前文档为准。

## 事实溯源

- F-312~F-318（[source-01.md](../references/source-01.md)）
