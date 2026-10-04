---
okf_version: "0.2"
type: bundle-index
title: "CubeSandbox — 腾讯 AI Agent 安全微沙箱"
description: "CubeSandbox 知识包：腾讯开源的 AI Agent 代码执行安全沙箱——基于 RustVMM + KVM 轻量 MicroVM，冷启动 <60ms、额外内存 <5MB、单机数千实例；控制面 CubeAPI（E2B SDK 兼容）/CubeMaster，数据面 Cubelet/CubeShim/cube-hypervisor/cube-agent，eBPF 网络数据面、OpenResty L7 出向网关、CubeCoW reflink/S3 双存储后端、CLM 自动暂停恢复；基于 v0.7.2 官方源码（commit f1aaa737）的全景教程"
tags:
  - cubesandbox
  - microvm
  - kvm
  - rustvmm
  - cloud-hypervisor
  - containerd
  - ebpf
  - openresty
  - sandbox
  - ai-agent
  - e2b
  - code-interpreter
generated:
  at: "2026-10-04"
verified:
  at: "2026-10-04"
  by: process:seven-concepts-v
  status: stable
  noted: "信源固定于 v0.7.2 tag blob（post-release 文件一律以 git show v0.7.2:<path> 为准）；openapi.yml info.version 仍为 0.1.0、changelog 日期与 tag 日期相差一天等信源瑕疵已在 references/01-source-map.md 登记"
stale_after: "2027-10-04"
sources:
  - url: "https://github.com/TencentCloud/CubeSandbox"
    type: official
    title: "TencentCloud/CubeSandbox — GitHub 官方仓库"
    distance: 1
  - url: "https://github.com/TencentCloud/CubeSandbox/releases/tag/v0.7.2"
    type: official
    title: "CubeSandbox v0.7.2 Release（2026-09-24，commit f1aaa737fb3862202b1731e0e0d844c28779f930）"
    distance: 1
  - url: "https://github.com/TencentCloud/CubeSandbox"
    type: source-code
    title: "CubeSandbox 主仓源码（本地克隆 external/dao/runtime/tencent/CubeSandbox；CubeAPI/cube-hypervisor/CubeShim/cube-agent/CubeCoW/CubeNet/CubeEgress/CubeProxy/CubeOps/CLM 等全组件）"
    distance: 1
status: stable
---

# CubeSandbox — 腾讯 AI Agent 安全微沙箱

本知识包基于腾讯官方开源仓库 **TencentCloud/CubeSandbox** 源码生成，信源固定于 release tag **v0.7.2**（2026-09-24，commit `f1aaa737`）。CubeSandbox 是面向 AI Agent 的代码执行安全沙箱：以 RustVMM + KVM 轻量 MicroVM 为隔离边界，冷启动 <60ms、沙箱额外内存 <5MB、单机可运行数千实例，并通过 CubeAPI 兼容 E2B SDK 生态。

全部内容溯源至 [F-001 ~ F-244](references/02-anchor-index.md)（14 主题面），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

> **⚠️ 信源瑕疵提示**：v0.7.2 的 `openapi.yml` 中 `info.version` 仍标注为 "0.1.0"（实际 26 个 paths、前缀 `/cubeapi/v1`）；changelog 记载日期为 09-23 而 tag 实际发布于 09-24；cube-hypervisor 的 workspace 成员数以 v0.7.2 tag Cargo.toml 登记的 29 个为准。完整瑕疵清单与版本 pin 规则见 [信源地图](references/01-source-map.md)。

## 五个核心架构洞察

| # | 洞察 | 详见 |
|---|---|---|
| I-1 | **池化 + 快照克隆**：预启动 pauseVM 池 + 内存快照恢复，把冷启动压到 60ms 级 | [cube-hypervisor](concepts/07-hypervisor.md) |
| I-2 | **Shim v2 嵌入 containerd 生态**：`io.containerd.cube.v2` 让 MicroVM 以标准 containerd 任务形态被编排 | [cube-agent 与 CubeShim](concepts/08-agent-shim.md) |
| I-3 | **独立内核 + eBPF + OpenResty 三层安全**：VM 隔离边界、内核态强制接管、L7 策略裁决 | [CubeNet](concepts/09-network.md)、[网关](concepts/10-gateways.md) |
| I-4 | **控制/运维分离与 CLM 自动暂停恢复**：CubeOps 独立运维面，Redis Stream 选主驱动空闲回收与访问唤醒 | [生命周期管理](concepts/12-ops-lifecycle.md) |
| I-5 | **CubeCoW reflink 免账本/双后端**：FICLONE 即时 CoW，索引扫描重建；S3 后端经 SPDK NVMe/TCP 接对象存储 | [存储体系](concepts/11-storage.md) |

## 导航

### 核心概念（concepts/，13 篇）

**全景与部署**

* [CubeSandbox 总览](concepts/01-overview.md) — 产品定位、核心指标、E2B 兼容与开源历程
* [总体架构](concepts/02-architecture.md) — 控制面/数据面/Guest 三层全景与端口地图
* [部署形态](concepts/03-deployment.md) — 一键部署、多节点、K8s 与离线环境

**控制面**

* [CubeAPI](concepts/04-cubeapi.md) — axum REST 网关、E2B 兼容路由、鉴权
* [CubeMaster](concepts/05-cubemaster.md) — gin/gRPC 调度核心与模板内嵌

**数据面**

* [Cubelet](concepts/06-cubelet.md) — 节点守护进程与沙箱 gRPC 接口
* [cube-hypervisor](concepts/07-hypervisor.md) — cloud-hypervisor fork、VM 生命周期、pauseVM 池
* [cube-agent 与 CubeShim](concepts/08-agent-shim.md) — guest ttrpc AgentService 与 containerd Shim v2
* [CubeNet](concepts/09-network.md) — eBPF TC 数据面、BPF map、SNAT
* [CubeEgress 与 CubeProxy](concepts/10-gateways.md) — OpenResty 出向 L7 策略与入站路由
* [CubeCoW 与 CubeS3lvol](concepts/11-storage.md) — reflink CoW 与 SPDK NVMe/TCP 对象后端

**运维与生态**

* [CubeOps 与生命周期管理](concepts/12-ops-lifecycle.md) — 运维面、CLM 选主、五状态、版本演进
* [三端 SDK 与模板生态](concepts/13-sdk-ecosystem.md) — Python/Go/Node SDK、envd 模板、日志

### 实操示例（examples/，4 篇）

* [三端 SDK 完整工作流](examples/01-sdk-workflow.md) — 创建沙箱、执行命令、文件读写、快照克隆
* [单机、多节点与离线部署实战](examples/02-cluster-deploy.md) — 一键部署、扩容、K8s、离线
* [快照模板制作实战](examples/03-template-build.md) — OCI 镜像/运行沙箱 → 探针 → 模板
* [超时策略与自动暂停恢复](examples/04-pause-resume-policy.md) — on_timeout、CLM、自动唤醒

### 信源与参考（references/）

* [信源地图](references/01-source-map.md) — 版本 pin、组件地图、信源瑕疵
* [事实锚点索引](references/02-anchor-index.md) — F-001 ~ F-244 逐条锚点
* [术语表](references/03-glossary.md) — 虚拟化、容器、eBPF、存储、网关五类术语

## 学习路径建议

1. **入门**：[总览](concepts/01-overview.md) → [总体架构](concepts/02-architecture.md) → [部署形态](concepts/03-deployment.md)
2. **控制面**：[CubeAPI](concepts/04-cubeapi.md) → [CubeMaster](concepts/05-cubemaster.md)
3. **数据面深入**：[Cubelet](concepts/06-cubelet.md) → [cube-hypervisor](concepts/07-hypervisor.md) → [cube-agent 与 CubeShim](concepts/08-agent-shim.md) → [CubeNet](concepts/09-network.md) → [网关](concepts/10-gateways.md) → [存储](concepts/11-storage.md)
4. **运维与生态**：[CubeOps 与生命周期](concepts/12-ops-lifecycle.md) → [SDK 与模板](concepts/13-sdk-ecosystem.md)
5. **实操**：按 [examples/](examples/) 四篇照做
6. **溯源**：通过 [锚点索引](references/02-anchor-index.md) 回到 v0.7.2 源码核对

## 骨架判定说明

* **一问**（有读者可照做的安装/配置/代码/调用流程？）：✅ 满足——examples/ 四篇覆盖 SDK 调用、集群部署、模板制作与暂停恢复策略。
* **二问**（经实测、有版本/输入输出/步骤顺序？）：事实与命令均锚定 v0.7.2 源码与官方文档；示例未在本环境实跑（Windows 无 KVM），不确定的方法签名均已显式注释。
* **结论**：bundle 含 concepts/ 13 篇 + examples/ 4 篇 + references/ 3 篇，定位"源码级分层全景教程"。

## 信任与生命周期说明

* **status 判定依据**：`stable`。244 条事实全部取自 v0.7.2 tag blob（信源距离 ①），关键 API/常量/计数经 Grep 与源码逐一对拍。
* **stale_after 解释**：设为 `2027-10-04`。CubeSandbox 处于快速迭代期（v0.1.0 至 v0.7.2 历时五个月），接口与默认值可能随版本变化，满一年后重新评估。
* **核验链路**：`generated.at` 2026-10-04（process:source-code-to-okf-wiki）；`verified.at` 2026-10-04（process:seven-concepts-v，V 阶段详见 [log.md](log.md)）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
examples/index
log
```
