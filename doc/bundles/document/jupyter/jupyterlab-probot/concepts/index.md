---
okf_version: "0.2"
type: "concept-index"
bundle: jupyterlab-probot
title: 概念文档索引
description: jupyterlab-probot 核心概念文档导航
---

# 概念文档索引

本目录包含 jupyterlab-probot 的核心概念文档，从入门到深入：

| 序号 | 文档 | 主题 |
|------|------|------|
| 00 | [简介](00-introduction) | 项目定位、四大功能特性、项目结构 |
| 01 | [快速上手](01-getting-started) | 环境要求、安装配置、运行测试、部署到 Glitch |
| 02 | [Probot 架构](02-probot-architecture) | Probot 框架原理、事件驱动模型、Context 对象、App 生命周期 |
| 03 | [配置系统](03-config-system) | YAML 配置文件、JSON Schema 验证、默认值机制、配置缓存 |
| 04 | [事件处理器](04-event-handlers) | 六大事件处理器详解、条件匹配逻辑、API 调用模式 |
| 05 | [测试与部署](05-testing-deployment) | nock 录制测试、smee.io 本地调试、GitHub App 注册、Glitch 部署 |

## 阅读路径推荐

- **新手上路**：00 → 01 → 02
- **自定义配置**：00 → 01 → 03 → [examples/02-custom-config](../examples/02-custom-config)
- **扩展功能**：02 → 04 → 05
- **部署上线**：01 → 05


```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-probot-architecture
03-config-system
04-event-handlers
05-testing-deployment
```
