---
okf_version: "0.2"
type: bundle
title: "ROS 2 概念总览"
description: "2020 年前后 ROS 2 应用框架层核心概念——发布订阅中间件、节点/话题/消息/发现、DDS/RTPS 底座、QoS 与 Topic Statistics（历史教程知识包）"
tags: [ros2, ROS graph, 节点, 话题, 消息, DDS, RTPS, QoS, 自动驾驶, 无人驾驶]
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

> **⚠️ 性质声明**：本知识包为**历史教程类知识包**，内容基于 2020 年前后简书连载《☠️无人驾驶(停止维护)》的《ROS2 概念》一文（作者"水之心"），非当前官方技术文档。涉及的 ROS 2 Dashing/Foxy 早期版本已过时，部分功能细节（如 Topic Statistics 的实现范围）可能演进。读者应将本包作为**历史方法与概念参考**，具体版本行为请以 ROS 2 官方当前文档为准。

本知识包梳理 2020 年前后 ROS 2 应用框架层的核心概念。ROS 2 是基于匿名发布/订阅机制的中间件，ROS graph 是其系统核心（F-324）；节点通过客户端库（rclcpp/rclpy）通信，经分布式发现过程建立连接（F-326、F-327）。其通信底座建立在 DDS/RTPS 之上（F-329），由 DDS 独立知识包详解。

通信底座：[DDS 与 QoS](../dds/index.md)；自动驾驶整车栈：[Autoware / Autoware.Auto](../autoware/index.md)。

---

## 信源说明

本知识包采用**单信源**结构：

| 信源ID | 文档 | 覆盖范围 |
|--------|------|---------|
| jianshu-86377a66ecef | [source-01.md](references/source-01.md) | F-324 ~ F-332（ROS 2 核心概念） |

文章内容为 ROS 2 官方概念的转述整理，属概念综述，内容时点为 2020 年前后（详见 [references/index.md](references/index.md) 可信度说明）。

---

## 📚 知识结构总览

```
ros2/
├── concepts/              # 核心概念文档（1篇）
│   └── 00-ros2-overview.md        # ROS 2 概念总览（中间件/节点/发现/DDS/QoS）
├── references/            # 信源登记簿（1篇）
│   └── source-01.md       # ROS2 概念（F-324~F-332）
├── index.md               # 本文件
└── log.md                 # 生成日志
```

> 本 bundle **不设 examples/ 目录**——内容为概念综述，无可运行示例。

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [ROS 2 概念总览](concepts/00-ros2-overview.md) | 发布订阅中间件与 ROS graph、节点/话题/消息/发现、客户端库、节点发现过程、DDS/RTPS 底座、DDS 实现与 rmw、QoS History、Topic Statistics |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [信源登记簿](references/index.md) | 单信源清单、F 编号段索引、可信度说明 |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2020 年前后发布的《ROS2 概念》一文生成，内容为**历史登记**，非当前事实
- **覆盖事实**：共 9 条事实（F-324~F-332）
- **核验情况**：文章为官方概念转述整理，无 P0 成效数字类声明，按"仅博文单源"处理
- **status**：stable — 核心概念（发布订阅/节点/发现/DDS 底座）作为心智模型长期有效
- **stale_after**：2026-12-31 — 历史参考类内容，按 OKF 规范设保守复核节点

### 已知边界（过时内容处理清单）

1. **ROS 2 Dashing/Foxy 早期版本**：文中版本行为（F-332 等）为 2020 年状态，ROS 2 已有新的发行版与更多客户端库能力；
2. **Topic Statistics 实现范围**：Foxy 中仅 C++（rclcpp）支持（F-332），后续版本实现可能扩展。

---

**本知识包共收录 2 个内容文档（1 个概念 + 1 个信源），外加 2 个子目录索引、根索引与生成日志，合计 6 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
