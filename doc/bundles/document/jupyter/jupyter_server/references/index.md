---
type: Index
title: "源码信源索引"
description: "Jupyter Server v2.21.0.dev0 源码分析信源文档索引，覆盖 ServerApp、Handler 体系、认证授权、核心服务等模块"
tags: [references, source, index]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:10:00Z" }
status: stable
stale_after: 2027-02-22
sources: []
---

# 源码信源索引

本目录包含 Jupyter Server 各核心模块的源码分析信源文档，所有概念文档和示例均基于这些信源生成。

## 核心模块

- [serverapp.py 源码信源](serverapp-source.md) — ServerApp 主应用类、ServerWebApplication、密码/停止/列表子应用
- [base/handlers.py 源码信源](handlers-source.md) — AuthenticatedHandler、JupyterHandler、APIHandler、FileFindHandler 继承体系
- [base/websocket.py 源码信源](websocket-base-source.md) — WebSocketHandler 基类、ZMQ 频道桥接、消息序列化

## 认证与安全

- [auth/ 源码信源](auth-source.md) — IdentityProvider、Authorizer、PasswordIdentityProvider、User 模型、LoginHandler、登录/登出流程

## 核心服务

- [services/contents/ 源码信源](contents-source.md) — ContentsManager、FileContentsManager、Checkpoints、文件 CRUD API
- [services/kernels/ 源码信源](kernels-source.md) — MappingKernelManager、KernelWebsocketHandler、空闲内核回收、KernelSpec
- [services/ 其他模块源码信源](services-source.md) — SessionManager、TerminalManager、ConfigManager、NbconvertHandler、APIHandler 等

## 扩展与网关

- [extension/ 源码信源](extension-source.md) — ExtensionApp、ExtensionManager、扩展发现机制、entry points、静态资源注册
- [gateway/ 源码信源](gateway-source.md) — GatewayClient、GatewayKernelManager、GatewayWebSocketHandler、远程内核代理

## 配置

- [config 管理源码信源](config-source.md) — traitlets 配置、BaseJSONConfigManager、递归合并机制、配置文件搜索路径

## 版本信息

| 属性 | 值 |
|------|-----|
| 源码版本 | v2.21.0.dev0 |
| Python 要求 | ≥ 3.10 |
| 源码路径 | `external/libs/jupyter/jupyter_server/` |

```{toctree}
:hidden:

auth-source
config-source
contents-source
extension-source
gateway-source
handlers-source
kernels-source
serverapp-source
services-source
websocket-base-source
```
