---
type: Reference
title: 信源：《数据分发服务：DDS》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《数据分发服务：DDS》信源登记——DDS 中间件标准、QoS 数据共享、域隔离、全局数据空间、动态发现、安全机制、DomainParticipant（2020 年前后，译自 dds-foundation.org）
tags: [DDS, OMG, QoS, 中间件, 信源登记, 简书, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-46945ab25c01
    url: https://www.jianshu.com/p/46945ab25c01
    title: 《数据分发服务：DDS》
---
# 信源：《数据分发服务：DDS》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中介绍 DDS 的文章，作者为"水之心"，内容时点为 2020 年前后。文章译自 dds-foundation.org 的 "What is DDS" 一文。本 dds 束的 DDS 与 QoS 内容以其为事实依据（F-312~F-318）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | 数据分发服务：DDS |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/46945ab25c01 |
| 原始出处 | dds-foundation.org 的 "What is DDS"（文章译作） |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- DDS（数据分发服务，Data Distribution Service）是来自 Object Management Group®（OMG®）的中间件协议和 API 标准，提供以数据为中心的连接（F-312）
- DDS 提供 QoS 控制的数据共享，应用程序通过发布和订阅由其主题名称标识的主题进行通信；订阅可以指定时间和内容过滤器，仅获取在主题上发布的数据的子集（F-313）
- 不同的 DDS 域（domain）彼此完全独立，DDS 域之间没有数据共享（F-314）
- DDS 概念上的"全局数据空间"（global data space），对应用程序来说看起来像是通过 API 访问的本地内存；文章陈述 DDS 进行对等通信（F-315）
- DDS 提供发布者和订阅者的动态发现（Dynamic Discovery），该机制使 DDS 应用程序可扩展，应用程序不必知道或配置通信端点（endpoint）（F-316）
- DDS 包括为信息分发提供身份验证、访问控制、机密性和完整性的安全机制，DDS Security 使用分散的点对点体系结构（F-317）
- DDS DomainParticipant 代表域中应用程序的本地成员身份，并充当 DDS 发布者、订阅者、主题、MultiTopics 和 ContentFilteredTopics 的工厂（F-318）

## 覆盖事实编号

F-312 ~ F-318
