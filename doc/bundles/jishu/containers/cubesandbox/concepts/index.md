---
type: toctree
title: CubeSandbox 核心概念
---

# 核心概念

本束概念文档按「全景 → 控制面 → 数据面 → 生态运维」四层组织，共 13 篇，全部事实锚定 F-001 ~ F-244。

## 全景与部署

| 文档 | 内容 |
|---|---|
| [01 总览](01-overview.md) | 产品定位、E2B 兼容、60ms 冷启动与开源历程（F-001 ~ F-009） |
| [02 总体架构](02-architecture.md) | 控制面/数据面/Guest 三层全景与端口地图（F-010 ~ F-013） |
| [03 部署形态](03-deployment.md) | 一键部署、多节点、K8s、离线环境（F-014 ~ F-036） |

## 控制面

| 文档 | 内容 |
|---|---|
| [04 CubeAPI](04-cubeapi.md) | axum REST 网关、E2B 兼容路由、鉴权与下游调用（F-037 ~ F-059） |
| [05 CubeMaster](05-cubemaster.md) | gin/gRPC 调度核心、模板内嵌与配置体系（F-060 ~ F-068） |

## 数据面

| 文档 | 内容 |
|---|---|
| [06 Cubelet](06-cubelet.md) | 节点守护进程、沙箱管理与 gRPC 接口（F-069 ~ F-093） |
| [07 cube-hypervisor](07-hypervisor.md) | cloud-hypervisor fork、VM 生命周期与设备模型（F-094 ~ F-140） |
| [08 cube-agent 与 CubeShim](08-agent-shim.md) | guest 内 ttrpc AgentService 与 containerd Shim v2 两层容器（F-141 ~ F-165） |
| [09 CubeNet](09-network.md) | eBPF TC 数据面、BPF map、SNAT 与固定拓扑（F-166 ~ F-184） |
| [10 CubeEgress 与 CubeProxy](10-gateways.md) | OpenResty 出向 L7 策略网关与入站路由、自动唤醒（F-185 ~ F-196） |
| [11 CubeCoW 与 CubeS3lvol](11-storage.md) | reflink 免账本 CoW 与 SPDK NVMe/TCP 对象存储后端（F-197 ~ F-214） |

## 运维与生态

| 文档 | 内容 |
|---|---|
| [12 CubeOps 与生命周期管理](12-ops-lifecycle.md) | 运维面分离、CLM 选主、五状态与超时语义、版本演进（F-215 ~ F-225、F-234 ~ F-244） |
| [13 三端 SDK 与模板生态](13-sdk-ecosystem.md) | Python/Go/Node SDK、envd 模板与日志体系（F-226 ~ F-233、F-239 ~ F-240） |

```{toctree}
:caption: 核心概念
:maxdepth: 2

01-overview
02-architecture
03-deployment
04-cubeapi
05-cubemaster
06-cubelet
07-hypervisor
08-agent-shim
09-network
10-gateways
11-storage
12-ops-lifecycle
13-sdk-ecosystem
```
