---
type: Index
title: 信源索引
description: jupyterlab-webrtc-docprovider源码信源引用索引，所有概念文档的事实来源
tags: [references, source, index]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:07:00Z" }
status: stable
stale_after: 2027-08-22
---

## 信源文件索引

本目录包含所有源码信源引用文件，每个文件对应一个或一组源码文件，提供概念文档的事实溯源。

| 文件 | 对应源码 | 核心内容 |
|------|---------|---------|
| [plugin-source.md](plugin-source.md) | `src/plugin.ts` | 4个JupyterFrontEndPlugin定义、IDocumentProviderFactory实现、命令/设置面板注册、RetroLab适配 |
| [manager-source.md](manager-source.md) | `src/manager.ts` | WebRtcManager类、三级配置优先级、房间ID SHA256哈希、provider创建逻辑、信号机制 |
| [provider-source.md](provider-source.md) | `src/provider.ts` | WebRtcProvider继承关系、IDocumentProvider接口实现、awareness用户状态设置、yProviderOptions配置映射 |
| [tokens-source.md](tokens-source.md) | `src/tokens.ts` | 命名空间常量、4个插件ID、命令ID、PageConfig键名、IWebRtcManager接口与Token声明 |
| [status-source.md](status-source.md) | `src/status.tsx` | WebRtcStatus VDomRenderer组件、Model类、React渲染逻辑 |
| [icons-schema-source.md](icons-schema-source.md) | `src/icons.ts`, `schema/plugin.json` | 3个LabIcon定义、JSON Schema配置验证规则 |
| [vendor-source.md](vendor-source.md) | `vendor/SimplePeerExtended.js`, `vendor/int64-buffer.min.js` | simple-peer大消息分块补丁、Int64BE编码、webpack替换规则 |
| [python-source.md](python-source.md) | `pyproject.toml`, `setup.py`, `jupyterlab_webrtc_docprovider/__init__.py` | Python打包配置、jupyter_packaging构建系统、版本同步机制 |
| [readme-source.md](readme-source.md) | `README.md`, `CONTRIBUTING.md` | 用户文档、安装说明、配置指南、开发流程 |

```{toctree}
:hidden:
:maxdepth: 7

icons-schema-source
manager-source
plugin-source
provider-source
python-source
readme-source
status-source
tokens-source
vendor-source
```
