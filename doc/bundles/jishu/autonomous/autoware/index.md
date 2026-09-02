---
okf_version: "0.2"
type: bundle
title: "Autoware / Autoware.Auto 自动驾驶开源栈"
description: "2020 年前后 Autoware 自动驾驶开源软件栈——三系（AI/IO/Auto）分工、ADE 开发环境、WSL2 与 Ubuntu 搭建、目标检测演示（历史教程知识包）"
tags: [autoware, Autoware.Auto, ADE, WSL2, ROS2, Ubuntu, 自动驾驶, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-7218542ae424
    resource: /references/source-01.md
    title: 《Ubuntu 搭建 AutowareAuto》
  - id: jianshu-8f97786e1631
    resource: /references/source-02.md
    title: 《AutowareAuto 基础》
  - id: jianshu-a95f95276fec
    resource: /references/source-03.md
    title: 《WSL2 之 autoware.auto》
  - id: jianshu-dfc1df4eb6ee
    resource: /references/source-04.md
    title: 《WSL2 安装和配置无人驾驶系统 autoware.auto》
---
# Autoware / Autoware.Auto 自动驾驶开源栈

> **⚠️ 性质声明**：本知识包为**历史教程类知识包**，内容基于 2020 年前后简书连载《☠️无人驾驶(停止维护)》的 4 篇实测教程（作者"水之心"），非当前官方技术文档。涉及的 Autoware.Auto 早期版本、ROS2 Dashing、WSL2 早期版本、ADE 早期命令行工具均已演进，命令细节可能过时。读者应将本包作为**历史方法与概念参考**，而非当前安装依据；具体操作请以 Autoware 官方当前文档为准。

本知识包梳理 2020 年前后 Autoware 自动驾驶开源软件栈的搭建与基础。Autoware 由 The Autoware Foundation 维护，2020 年已有 Autoware.AI、Autoware.IO、Autoware.Auto 三系（F-333）；其中 Autoware.Auto 基于 ROS 2，具备定位、感知与运动计划能力（F-334、F-335）。本包以 **开发环境（ADE）** 与 **搭建路径（WSL2/Ubuntu）** 为主线，帮助读者理解 2020 年代自动驾驶开源栈的安装痛点与基本命令链。

与通信底座、应用框架相关的知识包：[DDS 与 QoS](../dds/index.md)、[ROS 2 概念总览](../ros2/index.md)。

---

## 信源说明

本知识包采用**四信源**结构，全部来自同一连载的 4 篇实测教程：

| 信源ID | 文档 | 覆盖范围 |
|--------|------|---------|
| jianshu-7218542ae424 | [source-01.md](references/source-01.md) | F-319 ~ F-323（Ubuntu/ADE 开发环境） |
| jianshu-8f97786e1631 | [source-02.md](references/source-02.md) | F-333 ~ F-340（Autoware 三系与演示） |
| jianshu-a95f95276fec | [source-03.md](references/source-03.md) | F-349 ~ F-353（WSL2 路径一） |
| jianshu-dfc1df4eb6ee | [source-04.md](references/source-04.md) | F-357 ~ F-361（WSL2 路径二） |

四篇均为作者一手实测教程，无厂商自宣数据；内容时点均为 2020 年前后，未做第三方交叉核验，按"仅博文单源"处理（详见 [references/index.md](references/index.md) 可信度说明）。

---

## 📚 知识结构总览

```
autoware/
├── concepts/              # 核心概念文档（3篇）
│   ├── 00-wsl2-environment.md      # WSL2 环境搭建（两条路径 + VcXsrv 显示转发）
│   ├── 01-ubuntu-ade-environment.md # Ubuntu 与 ADE 开发环境（adehome/构建测试）
│   └── 02-autoware-auto-basics.md   # Autoware.Auto 基础（三系/能力/演示命令链）
├── references/            # 信源登记簿（4篇）
│   ├── source-01.md       # Ubuntu 搭建 AutowareAuto（F-319~F-323）
│   ├── source-02.md       # AutowareAuto 基础（F-333~F-340）
│   ├── source-03.md       # WSL2 之 autoware.auto（F-349~F-353）
│   ├── source-04.md       # WSL2 安装配置 autoware.auto（F-357~F-361）
├── index.md               # 本文件
└── log.md                 # 生成日志
```

> 本 bundle **不设 examples/ 目录**——教程命令已在 concepts 内联呈现，历史环境不可复现，无可独立运行示例。

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [WSL2 环境搭建 Autoware.Auto](concepts/00-wsl2-environment.md) | 路径一（X 桌面 + docker + conda autoware + 免 sudo + 构建测试）；路径二（Ubuntu20.04 子系统 + 远程桌面 + VcXsrv 显示转发） |
| [Ubuntu 与 ADE 开发环境](concepts/01-ubuntu-ade-environment.md) | ADE 定位、adehome 主目录约定、.adehome/.aderc 机制、克隆与 colcon 构建测试 |
| [Autoware.Auto 基础](concepts/02-autoware-auto-basics.md) | Autoware 三系分工、2020 年 5 月能力范围、ADE/NVIDIA Docker 安装、目标检测演示命令链 |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [信源登记簿](references/index.md) | 四信源清单、F 编号段索引、可信度说明 |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2020 年前后发布的 4 篇实测教程生成，全部内容为**历史登记**，非当前事实
- **覆盖事实**：共 23 条事实（F-319~F-323、F-333~F-340、F-349~F-353、F-357~F-361）
- **核验情况**：四篇为作者一手实操记录，无 P0 成效数字类声明，按"仅博文单源"处理
- **status**：stable — 历史方法记录，不随当前生态变化而失效
- **stale_after**：2026-12-31 — 历史参考类内容，按 OKF 规范设保守复核节点

### 已知边界（过时内容处理清单）

1. **Autoware.Auto 早期版本**：文中能力清单（F-335）与命令链为 2020 年 5 月状态，当前 Autoware 生态已有大幅演进；
2. **ROS2 Dashing**：文中 Autoware.Auto 基于 ROS2 Dashing（F-339），为 2020 年版本，当前 ROS 2 发行版不同；
3. **WSL2 早期版本**：文中显示转发（VcXsrv/xrdp，F-349/F-361）在 WSL2 早期阶段必要，当前 WSLg 已原生支持图形界面；
4. **旧式安装方式**：apt-key、老式 docker 安装、`ade+x86_64` 下载链接（F-337）等可能已失效或改变。

---

**本知识包共收录 7 个内容文档（3 个概念 + 4 个信源），外加 2 个子目录索引、根索引与生成日志，合计 11 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
