---
type: Concept
title: BlueChi 多节点管理
description: 了解 BlueChi 在 QM 中的集成：多节点服务管理、agent 配置、节点命名规则和跨节点服务控制
tags: [bluechi, multi-node, orchestration, systemd, service-management]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /bundles/containers/qm/references/readme-source.md
    title: "QM 项目 README 与 man 手册信源"
---

# BlueChi 多节点管理

BlueChi 是一个确定性的 systemd 服务控制器，专为高监管要求的多节点环境设计（如汽车 ECU 网络）。QM 内置了 BlueChi agent 支持，可以在多节点汽车场景中统一管理主机和 QM 内的服务。

## BlueChi 简介

BlueChi（原名为 hirte）是 Red Hat 开发的多节点服务管理工具，适用于传统编排工具（如 Kubernetes）因合规性、资源占用或确定性要求而不适用的场景。

### BlueChi 适用场景

- **功能安全行业**：汽车、航空航天、工业控制等需要确定性服务管理的领域
- **边缘设备**：跨多个边缘节点控制服务启停
- **预定义节点数量**：节点数量固定、不需要动态扩缩容的环境
- **监管合规**：需要审计追踪、确定性行为的高监管环境

### BlueChi 架构

BlueChi 采用 hub-and-spoke（中心-辐射）架构：

```
┌─────────────────────────────────────────────────────────────────┐
│                      BlueChi Controller                         │
│                   (运行在管理节点/主机上)                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  服务状态数据库、依赖解析、跨节点编排、API 接口            │  │
│  └──────────────┬──────────────────┬──────────────────┬───────┘  │
└─────────────────┼──────────────────┼──────────────────┼──────────┘
                  │                  │                  │
        ┌─────────▼────────┐ ┌──────▼─────────┐ ┌──────▼─────────┐
        │ bluechi-agent    │ │ bluechi-agent  │ │ bluechi-agent  │
        │ (主机节点)       │ │ (QM 容器)      │ │ (其他 ECU 节点)│
        │ node: hostname   │ │ node: qm.*     │ │ node: ecu-*    │
        └──────────────────┘ └────────────────┘ └────────────────┘
```

- **BlueChi Controller**：中心控制器，运行在管理节点上，维护全局服务状态
- **bluechi-agent**：每个被管理节点上运行的 agent，与本地 systemd 交互
- **节点命名**：每个节点有唯一名称，QM 节点名自动加 `qm.` 前缀

## QM 中的 BlueChi 集成

QM 安装时会自动在 QM 环境中安装并配置 bluechi-agent。

### 安装组件

`/usr/share/qm/setup` 脚本会自动安装以下包到 QM rootfs：

- `bluechi`：BlueChi 主程序
- `bluechi-agent`：BlueChi agent 服务

### 节点命名规则

QM 内的 bluechi-agent 有特殊的节点命名规则：

1. **基于主机配置**：读取主机的 `/etc/bluechi/agent.conf`
2. **自动添加前缀**：在主机节点名前添加 `qm.` 前缀
3. **默认名称**：如果主机没有配置 agent.conf，默认节点名为 `qm.$(hostname)`

**命名示例**：

| 主机节点名 | QM 节点名 |
|-----------|----------|
| `car-ecu-01` | `qm.car-ecu-01` |
| `ivI-system` | `qm.ivi-system` |
| (未配置) | `qm.$(hostname)`，如 `qm.autosd-host` |

### 配置同步机制

QM 启动时会自动将主机的 BlueChi 配置复制到 QM 内：

- **源配置**：主机 `/etc/bluechi/agent.conf`
- **目标位置**：QM 内 `/etc/bluechi/agent.conf`（每次 QM 启动时同步）
- **同步时机**：qm.service 启动时执行配置同步脚本

## 自定义 BlueChi 配置

有两种方式自定义 QM 内的 bluechi-agent 配置：

### 方式一：drop-in 配置目录（推荐）

在 QM rootfs 的 `agent.conf.d/` 目录添加配置，不会被启动同步覆盖：

```bash
# 在主机上操作（直接写入 QM rootfs）
mkdir -p /usr/lib/qm/rootfs/etc/bluechi/agent.conf.d/

cat > /usr/lib/qm/rootfs/etc/bluechi/agent.conf.d/99-custom.conf << EOF
[bluechi-agent]
# 自定义配置项
LogLevel=DEBUG
EOF
```

### 方式二：禁用自动配置同步

修改 QM Quadlet，移除 bluechi-agent 配置同步脚本，然后手动管理 QM 内的配置：

1. 创建 QM drop-in 配置
2. 覆盖启动命令，不执行 bluechi 配置脚本
3. 手动维护 `/usr/lib/qm/rootfs/etc/bluechi/agent.conf`

## BlueChi 基本操作

### 在主机上查看节点状态

```bash
# 列出所有已连接的 BlueChi 节点
bluechictl list-nodes

# 输出示例：
# NODE             STATUS     LAST SEEN
# car-ecu-01       online     2s ago
# qm.car-ecu-01    online     1s ago
# ecu-brake        online     5s ago
```

### 在节点上操作服务

```bash
# 查看指定节点上的服务状态
bluechictl list-units qm.car-ecu-01

# 在 QM 节点上启动服务
bluechictl start qm.car-ecu-01 myapp.service

# 在 QM 节点上停止服务
bluechictl stop qm.car-ecu-01 myapp.service

# 启用/禁用服务
bluechictl enable qm.car-ecu-01 myapp.service
bluechictl disable qm.car-ecu-01 myapp.service
```

### 在 QM 内操作 BlueChi

进入 QM 后可以直接使用 bluechictl 操作本地服务：

```bash
# 进入 QM
podman exec -ti qm sh

# 在 QM 内查看本地 bluechi-agent 状态
systemctl status bluechi-agent

# 在 QM 内使用 bluechictl（查看本地节点）
bluechictl list-units
bluechictl status bluechi-agent
```

### 跨节点服务依赖

BlueChi 支持跨节点的服务依赖配置，这在汽车场景中非常有用：

```ini
# /etc/containers/systemd/qm.container.d/dependencies.conf (示例)
# 配置 QM 内服务依赖主机或其他 ECU 上的服务
[Unit]
# 示例：依赖主机上的 some-host.service
# Requires=bluechi-proxy@car-ecu-01.some-host.service
# After=bluechi-proxy@car-ecu-01.some-host.service
```

## 典型汽车多节点场景

在汽车域控制器架构中，BlueChi 可以管理以下节点：

```
┌─────────────────────────────────────────────────────────────────┐
│                     中央计算单元 (CCU)                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ BlueChi Controller                                        │  │
│  └──────────────┬────────────────────────────────────────────┘  │
│                 │                                                │
│  ┌──────────────▼──────────────┐  ┌──────────────────────────┐  │
│  │ bluechi-agent (主机)        │  │ bluechi-agent (QM)       │  │
│  │ node: ccu-main              │  │ node: qm.ccu-main        │  │
│  │ - ASIL 相关服务             │  │ - 信息娱乐应用           │  │
│  │ - 车辆总线通信              │  │ - 导航、媒体             │  │
│  │ - 系统管理服务              │  │ - 第三方应用             │  │
│  └─────────────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                           │
    ┌──────┴──────┐             ┌──────┴──────┐
    │  CAN/LIN    │             │  以太网     │
    └──────┬──────┘             └──────┬──────┘
           │                           │
┌──────────▼─────────┐     ┌──────────▼─────────┐
│  制动 ECU           │     │  仪表 ECU          │
│  bluechi-agent     │     │  bluechi-agent     │
│  node: ecu-brake   │     │  node: ecu-ic      │
│  ASIL D            │     │  ASIL B            │
└────────────────────┘     └────────────────────┘
```

### 场景示例：信息娱乐启动依赖

```
1. 车辆上电 → CCU 主机启动
2. BlueChi Controller 启动，等待各节点 agent 连接
3. qm.ccu-main 节点连接成功
4. BlueChi 启动 QM 内的信息娱乐服务
5. 导航应用依赖定位服务（主机或其他 ECU）
6. 媒体应用依赖音频服务（QM 内或独立节点）
```

## 监控与日志

### 查看 BlueChi 日志

```bash
# 主机上查看 BlueChi 日志
journalctl -u bluechi-controller -f
journalctl -u bluechi-agent -f

# QM 内查看 bluechi-agent 日志
podman exec qm journalctl -u bluechi-agent -f
```

### 健康检查

QM 测试套件中包含 BlueChi 健康检查：

```bash
# 查看测试脚本（参考）
cat tests/qm-sanity-test/check_bluechi_is_ok.sh
```

健康检查通常验证：
1. bluechi-agent 服务在 QM 内运行
2. QM 节点已连接到 BlueChi Controller
3. 节点名正确（包含 `qm.` 前缀）

## 与其他容器编排工具对比

| 特性 | BlueChi | Kubernetes | systemd（单机） |
|------|---------|------------|----------------|
| 适用场景 | 固定节点数、边缘、功能安全 | 云原生、动态扩缩容 | 单节点 |
| 资源占用 | 极低（适合嵌入式） | 高 | 极低 |
| 确定性 | 高（同步操作） | 低（最终一致） | 高 |
| 容器管理 | 通过 systemd + Podman | 原生支持 | Podman Quadlet |
| 安全合规 | 面向功能安全设计 | 通用 | 通用 |
| 多节点 | ✅ | ✅ | ❌ |

在汽车功能安全场景中选择 BlueChi 的原因：
- 资源占用适合嵌入式 ECU
- 确定性行为满足安全认证要求
- 与 systemd/Podman 深度集成
- QM 开箱即用支持

## 相关概念

- [嵌套隔离架构](/bundles/containers/qm/concepts/01-nested-architecture.md)：了解 QM 内独立 systemd 和 BlueChi agent 的运行环境
- [QM 定位与 ASIL 汽车功能安全场景](/bundles/containers/qm/concepts/00-introduction.md)：了解 BlueChi 适用的汽车安全场景
- [创建 QM 虚拟机环境](/bundles/containers/qm/examples/01-vm-setup.md)：在虚拟机中测试 BlueChi 多节点配置
