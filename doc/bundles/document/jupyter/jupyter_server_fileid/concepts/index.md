---
okf_version: "0.2"
type: concepts
title: "核心概念"
description: "jupyter_server_fileid 核心概念文档索引，涵盖从入门到进阶的完整知识体系。"
tags: [jupyter, fileid, concepts, index]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: manager-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py"
    title: "manager.py"
---

# 核心概念

本章节系统讲解 jupyter_server_fileid 的核心概念，分为入门、核心、进阶三个层次。

## 📘 入门

| 文档 | 简介 |
|------|------|
| [00 - jupyter_server_fileid 简介](00-introduction.md) | 了解 jupyter_server_fileid 解决的问题（文件路径不稳定）、核心能力、项目信息与架构概览。 |
| [01 - 5分钟快速上手](01-getting-started.md) | 安装扩展、配置管理器、使用 REST API 查询文件 ID 的快速入门。 |

## 📗 核心

| 文档 | 简介 |
|------|------|
| [02 - 架构总览](02-architecture-overview.md) | 理解四层架构（Extension→Handler→Manager→SQLite）、事件驱动数据流与设计哲学。 |
| [03 - 抽象基类与核心 API](03-file-id-manager.md) | 详解 BaseFileIdManager 的接口契约、traitlets 配置、路径归一化和 CRUD 抽象方法。 |
| [04 - 双管理器对比：Arbitrary vs Local](04-arbitrary-vs-local.md) | 深入对比两种管理器的设计差异、Schema 区别、适用场景和同步机制。 |
| [05 - 事件驱动同步与带外检测](05-event-sync-mechanism.md) | jupyter_events 事件监听、contents service 事件格式、LocalFileIdManager 的 inode 跟踪和带外移动检测算法。 |
| [06 - REST API 端点](06-http-api.md) | 两个 HTTP 端点的请求参数、响应格式、错误处理和在前端扩展中的使用方式。 |

## 📙 进阶

| 文档 | 简介 |
|------|------|
| [07 - 扩展配置与自定义管理器](07-extension-configuration.md) | 配置 FileIdExtension 选项、创建自定义 File ID 管理器、db_path 和 journal_mode 配置。 |
| [08 - CLI 工具与数据库管理](08-cli-and-database.md) | CLI drop 命令、SQLite 数据库位置和 Schema、pytest 测试插件与 fs_helpers 工具。 |

---

**导航：**
- [示例代码](../examples/index.md) — 可运行的代码示例
- [源码信源](../references/index.md) — 源码信源文档
- [返回首页](../index.md)
