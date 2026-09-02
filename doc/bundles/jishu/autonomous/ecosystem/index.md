---
okf_version: "0.2"
type: bundle
title: "无人驾驶生态：数据集、车载术语与开发资源"
description: "2020 年前后无人驾驶生态外围知识——常用数据集盘点、ECU/CAN 车载术语、学习资源导航、WSL2 GPU 深度学习环境搭建（历史教程知识包）"
tags: [无人驾驶, 数据集, ECU, CAN, WSL2, CUDA, 深度学习, 学习资源]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-0066c78a2f43
    resource: /references/source-01.md
    title: 《无人驾驶数据集》
  - id: jianshu-e99b8cbb1825
    resource: /references/source-02.md
    title: 《汽车系统开发常见名称》
  - id: jianshu-ca403b26e91b
    resource: /references/source-03.md
    title: 《Autonomous 资源》
  - id: jianshu-98c8af1d2d33
    resource: /references/source-04.md
    title: 《wsl2 配置多环境的深度学习 GPU 环境》
---
# 无人驾驶生态：数据集、车载术语与开发资源

> **⚠️ 性质声明**：本知识包为**历史教程类知识包**，内容基于 2020 年前后简书连载《☠️无人驾驶(停止维护)》的 4 篇文章（作者"水之心"），非当前官方技术文档。涉及的数据集规模、工具版本、资源链接与 WSL2/CUDA 早期安装方式均已演进。读者应将本包作为**历史方法与概念参考**，而非当前依据；具体请以各数据集、NVIDIA、Anaconda 与各框架的官方当前文档为准。

本知识包梳理 2020 年前后无人驾驶生态的外围知识，覆盖四类内容：常用数据集盘点（F-301~F-311）、车载术语 ECU/CAN（F-362~F-363）、学习资源导航（F-354~F-356）与 WSL2 GPU 深度学习环境搭建（F-341~F-348）。

生态核心栈知识包：[DDS 与 QoS](../dds/index.md)、[ROS 2 概念总览](../ros2/index.md)、[Autoware / Autoware.Auto](../autoware/index.md)。

---

## 信源说明

本知识包采用**四信源**结构，全部来自同一连载的 4 篇文章：

| 信源ID | 文档 | 覆盖范围 |
|--------|------|---------|
| jianshu-0066c78a2f43 | [source-01.md](references/source-01.md) | F-301 ~ F-311（无人驾驶数据集） |
| jianshu-e99b8cbb1825 | [source-02.md](references/source-02.md) | F-362 ~ F-363（车载术语 ECU/CAN） |
| jianshu-ca403b26e91b | [source-03.md](references/source-03.md) | F-354 ~ F-356（学习资源） |
| jianshu-98c8af1d2d33 | [source-04.md](references/source-04.md) | F-341 ~ F-348（WSL2 GPU 环境） |

四篇均为作者一手实测/盘点记录，无厂商自宣数据；内容时点均为 2020 年前后，未做第三方交叉核验，按"仅博文单源"处理（详见 [references/index.md](references/index.md) 可信度说明）。

---

## 📚 知识结构总览

```
ecosystem/
├── concepts/              # 核心概念文档（4篇）
│   ├── 00-datasets.md                 # 无人驾驶常用数据集盘点（10 数据集）
│   ├── 01-vehicle-terms.md            # 车载术语：ECU 与 CAN
│   ├── 02-resources.md                # 无人驾驶学习资源导航
│   └── 03-wsl2-gpu-deep-learning.md   # WSL2 GPU 深度学习环境搭建
├── references/            # 信源登记簿（4篇）
│   ├── source-01.md       # 无人驾驶数据集（F-301~F-311）
│   ├── source-02.md       # 汽车系统开发常见名称（F-362~F-363）
│   ├── source-03.md       # Autonomous 资源（F-354~F-356）
│   ├── source-04.md       # wsl2 配置多环境的深度学习 GPU 环境（F-341~F-348）
├── index.md               # 本文件
└── log.md                 # 生成日志
```

> 本 bundle **不设 examples/ 目录**——内容为资源盘点与历史环境记录，无可独立运行示例；WSL2 GPU 环境命令已在 concepts/03 内联呈现。

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [无人驾驶常用数据集盘点](concepts/00-datasets.md) | KITTI/Cityscapes/Mapillary/comma.ai/Udacity/ApolloCar3D/BDDV/nuScenes/H3D/CamVid 规模与用途 |
| [车载术语：ECU 与 CAN](concepts/01-vehicle-terms.md) | ECU 电子控制单元、CAN 控制器局域网定义 |
| [无人驾驶学习资源导航](concepts/02-resources.md) | paperswithcode 任务页、GitHub 资源、Kaggle Lyft 竞赛代码 |
| [WSL2 GPU 深度学习环境搭建](concepts/03-wsl2-gpu-deep-learning.md) | CUDA 11.1 安装与离线回退、Anaconda、MXNet/TF/PyTorch conda 环境 |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [信源登记簿](references/index.md) | 四信源清单、F 编号段索引、可信度说明 |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2020 年前后发布的 4 篇文章生成，全部内容为**历史登记**，非当前事实
- **覆盖事实**：共 24 条事实（F-301~F-311、F-341~F-348、F-354~F-356、F-362~F-363）
- **核验情况**：四篇为作者一手实测/盘点记录，无 P0 成效数字类声明，按"仅博文单源"处理
- **status**：stable — 历史方法记录，不随当前生态变化而失效
- **stale_after**：2026-12-31 — 历史参考类内容，按 OKF 规范设保守复核节点

### 已知边界（过时内容处理清单）

1. **数据集规模为 2020 年前后状态**：文中各数据集规模（F-301~F-311）为当时快照，现已扩充；
2. **CUDA 11.1 与老式安装**：文中 WSL2 CUDA 11.1、apt-key、离线 run 安装（F-342、F-343）为 2020 年方式，已过时；
3. **conda 通道与框架版本**：文中 mxnet-cu110、cudatoolkit=11 等（F-346~F-348）为 2020 年版本，当前安装方式不同；
4. **资源链接状态**：文中学习资源链接（F-354~F-356）可能已变更或失效。

---

**本知识包共收录 8 个内容文档（4 个概念 + 4 个信源），外加 2 个子目录索引、根索引与生成日志，合计 12 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
