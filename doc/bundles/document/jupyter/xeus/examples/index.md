---
type: Index
title: Xeus 示例索引
description: jupyterlite-xeus 实战示例列表，从基础部署到生产环境配置
tags: [examples, index, xeus, jupyterlite]
status: stable
---

# Xeus 示例索引

本目录包含 jupyterlite-xeus 的实战示例，从基础部署到生产环境配置。

## 示例列表

| 示例 | 难度 | 场景 |
|------|------|------|
| [basic-deploy.md](basic-deploy.md) | ⭐ 入门 | 从零创建最小可用的JupyterLite+xeus站点 |
| [custom-env.md](custom-env.md) | ⭐⭐ 中级 | 配置包含数据科学包的自定义conda环境 |
| [advanced-deploy.md](advanced-deploy.md) | ⭐⭐⭐ 高级 | 生产级Nginx/CDN部署、COOP/COEP配置、性能优化 |

## 前置知识

- 阅读 [快速开始](../concepts/01-getting-started.md) 了解基本安装
- 阅读 [构建系统详解](../concepts/05-build-system.md) 理解构建流程
- 阅读 [双Worker通信模式](../concepts/03-dual-worker-modes.md) 理解部署时的跨域隔离配置

```{toctree}
:maxdepth: 7

advanced-deploy
basic-deploy
custom-env
```
