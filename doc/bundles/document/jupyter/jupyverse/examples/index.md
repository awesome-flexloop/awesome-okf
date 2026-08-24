---
type: Index
title: "示例索引"
description: "Jupyverse 实践示例索引，包含启动、认证、协作、API调用和插件开发的实操指南。"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
---

# 示例索引

本目录包含 Jupyverse 的实践示例，提供可直接运行的操作指南。

| 序号 | 示例 | 难度 | 场景 |
|------|------|------|------|
| 01 | [基本服务器启动](01-basic-startup.md) | ⭐ | 本地快速启动，无认证模式访问 JupyterLab |
| 02 | [Token认证配置](02-token-auth.md) | ⭐⭐ | 配置Token认证，安全远程访问 |
| 03 | [实时协作编辑](03-collaboration.md) | ⭐⭐ | 启用Yjs多用户实时协作编辑Notebook |
| 04 | [REST API使用](04-rest-api-usage.md) | ⭐⭐ | 通过HTTP API进行文件操作、内核管理和代码执行 |
| 05 | [自定义插件开发](05-custom-plugin.md) | ⭐⭐⭐ | 从零开发FPS插件，添加自定义API端点 |

## 前置知识

- 示例01-02：需要基本的命令行和Python环境知识
- 示例03：需要理解示例01-02，建议阅读[协作编辑Yjs](../concepts/09-collaboration-yjs.md)
- 示例04：需要理解示例01，建议阅读[Contents文件服务](../concepts/06-contents-service.md)和[内核管理](../concepts/07-kernel-management.md)
- 示例05：需要理解FPS模块系统，建议阅读[FPS模块系统](../concepts/03-fps-module-system.md)和[插件开发指南](../concepts/12-plugin-development.md)

```{toctree}
:hidden:

01-basic-startup
02-token-auth
03-collaboration
04-rest-api-usage
05-custom-plugin
```
