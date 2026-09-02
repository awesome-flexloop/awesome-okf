---
okf_version: "0.2"
type: bundle
title: "DDS 与 QoS"
description: "2020 年前后 DDS 数据分发服务核心概念——OMG 中间件标准、QoS 数据共享、域隔离、全局数据空间、动态发现、安全机制、DomainParticipant（历史教程知识包）"
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

> **⚠️ 性质声明**：本知识包为**历史教程类知识包**，内容基于 2020 年前后简书连载《☠️无人驾驶(停止维护)》的《数据分发服务：DDS》一文（作者"水之心"，译自 dds-foundation.org 的 "What is DDS"），非当前官方技术文档。DDS 标准规范持续演进，部分细节可能过时。读者应将本包作为**历史方法与概念参考**，具体规范行为请以 OMG 与 DDS Foundation 的当前文档为准。

本知识包梳理 2020 年前后 DDS（数据分发服务）的核心概念。DDS 是来自 OMG 的中间件协议和 API 标准，提供以数据为中心的连接（F-312），是 ROS 2 通信底座 DDS/RTPS 的标准基础。本包以概念综述为主线，介绍 QoS 控制的数据共享、域隔离、全局数据空间、动态发现、安全机制与 DomainParticipant。

通信底座上层应用：[ROS 2 概念总览](../ros2/index.md)；自动驾驶整车栈：[Autoware / Autoware.Auto](../autoware/index.md)。

---

## 信源说明

本知识包采用**单信源**结构：

| 信源ID | 文档 | 覆盖范围 |
|--------|------|---------|
| jianshu-46945ab25c01 | [source-01.md](references/source-01.md) | F-312 ~ F-318（DDS 与 QoS 核心概念） |

文章为 dds-foundation.org 官方文档译作，内容时点为 2020 年前后（详见 [references/index.md](references/index.md) 可信度说明）。

---

## 📚 知识结构总览

```
dds/
├── concepts/              # 核心概念文档（1篇）
│   └── 00-dds-and-qos.md          # DDS 与 QoS（标准定位/数据共享/域/发现/安全/参与体）
├── references/            # 信源登记簿（1篇）
│   └── source-01.md       # 数据分发服务：DDS（F-312~F-318）
├── index.md               # 本文件
└── log.md                 # 生成日志
```

> 本 bundle **不设 examples/ 目录**——内容为概念综述，无可运行示例。

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [DDS 与 QoS](concepts/00-dds-and-qos.md) | DDS 标准定位、QoS 数据共享、域隔离、全局数据空间、动态发现、安全机制、DomainParticipant |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [信源登记簿](references/index.md) | 单信源清单、F 编号段索引、可信度说明 |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2020 年前后发布的《数据分发服务：DDS》一文生成，内容为**历史登记**，非当前事实
- **覆盖事实**：共 7 条事实（F-312~F-318）
- **核验情况**：文章为官方文档译作，无 P0 成效数字类声明，按"仅博文单源"处理
- **status**：stable — 核心概念（以数据为中心/QoS/域/发现）作为心智模型长期有效
- **stale_after**：2026-12-31 — 历史参考类内容，按 OKF 规范设保守复核节点

### 已知边界（过时内容处理清单）

1. **DDS 标准演进**：文中 QoS 策略与安全机制（F-313、F-317）为 2020 年前后状态，OMG 规范持续更新；
2. **实现生态扩展**：文中以标准概念为主，未覆盖后续实现与 DDS Security 规范的细化演进。

---

**本知识包共收录 2 个内容文档（1 个概念 + 1 个信源），外加 2 个子目录索引、根索引与生成日志，合计 6 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
