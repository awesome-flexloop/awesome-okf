---
type: Concept
title: 车载术语：ECU 与 CAN
description: 2020 年前后车载系统常见术语——ECU 电子控制单元定义与 CAN 控制器局域网总线标准（2020 年前后）
tags: [ECU, CAN, 车载总线, 嵌入式系统, 自动驾驶, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-e99b8cbb1825
    resource: /references/source-02.md
    title: 《汽车系统开发常见名称》
---
# 车载术语：ECU 与 CAN

本文基于 2020 年前后教程，介绍汽车系统开发中的两个常见术语：ECU 与 CAN（F-362~F-363）。理解这两个术语是进入车载系统与自动驾驶工程的基础。

## ECU：电子控制单元

**ECU**（电子控制器，又称电子控制单元或电控单元，英文 Electronic Control Unit，缩写 ECU）是汽车电子系统中控制电气系统、电子系统及汽车子系统的嵌入式系统（F-362）。

## CAN：控制器局域网

**CAN / CAN bus**（控制器局域网，Controller Area Network）是一种车用总线标准。该标准允许网络上的单片机和仪器在不需要主机（Host）的情况下相互通信、基于消息传递协议，并在车辆上采用复用通信线缆以降低铜线使用量（F-363）。

## 现状

本文基于 2020 年前后教程，ECU 与 CAN 是车载系统长期稳定的基础概念，定义本身依然有效。现代车辆电子电气架构（如域控制器、车载以太网）在此基础上持续演进，具体架构请以当前车厂与标准组织资料为准。

## 事实溯源

- F-362~F-363（[source-02.md](../references/source-02.md)）
