---
type: Index
title: 概念文档索引
description: jupyterlab-webrtc-docprovider概念文档，按学习路径组织
tags: [concepts, index, learning-path]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:07:00Z" }
status: stable
stale_after: 2027-08-22
---

## 概念文档索引

### 入门（00-01）

| 文件 | 主题 | 前置知识 |
|------|------|---------|
| [00-introduction.md](00-introduction.md) | 项目介绍与工作原理 | 无 |
| [01-getting-started.md](01-getting-started.md) | 安装、环境要求、依赖版本 | 00 |

### 架构与核心（02-06）

| 文件 | 主题 | 前置知识 |
|------|------|---------|
| [02-architecture-overview.md](02-architecture-overview.md) | 整体架构、模块关系、数据流 | 00-01 |
| [03-webrtc-manager.md](03-webrtc-manager.md) | WebRtcManager配置与生命周期 | 02 |
| [04-document-provider.md](04-document-provider.md) | WebRtcProvider文档同步 | 02-03 |
| [05-room-and-signaling.md](05-room-and-signaling.md) | 房间ID哈希、信令、P2P发现 | 03-04 |
| [06-plugin-system.md](06-plugin-system.md) | 4个JupyterLab插件详解 | 02 |

### UI与适配（07）

| 文件 | 主题 | 前置知识 |
|------|------|---------|
| [07-status-bar.md](07-status-bar.md) | 状态栏VDom组件、RetroLab适配 | 02, 06 |

### 高级主题（08-10）

| 文件 | 主题 | 前置知识 |
|------|------|---------|
| [08-vendor-patches.md](08-vendor-patches.md) | SimplePeer分块补丁、webpack集成 | 05 |
| [09-configuration.md](09-configuration.md) | 三级配置优先级、5种配置方式 | 03 |
| [10-build-and-packaging.md](10-build-and-packaging.md) | TypeScript/webpack/Python构建 | 06, 08 |

### 推荐学习路径

```
00 → 01 → 02 → 03 → 04 → 05 → 06
                          ↓
                          07 → 09
                    08 → 10
```
