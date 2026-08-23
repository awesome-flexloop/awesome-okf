---
type: reference_index
title: "anywidget 信源登记簿索引"
description: "anywidget API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2027-08-23
---

# anywidget 信源文档

本目录包含 anywidget 框架的源码级参考文档，所有 API 均经源码验证。

| 文档 | 覆盖模块 | 信源 |
|------|---------|------|
| [widget-base](widget-base.md) | AnyWidget基类与生命周期 | widget.py, __init__.py |
| [traits](traits.md) | Trait同步与数据绑定 | _traits.py, _protocols.py |
| [esm-protocol](esm-protocol.md) | ESM前端协议与通信 | _file_contents.py, JS runtime |
| [descriptor](descriptor.md) | 描述符协议与文件内容管理 | _descriptor.py, _file_contents.py |
| [hmr](hmr.md) | HMR热更新与开发工作流 | JS runtime, packages/vite/ |
| [framework-bridges](framework-bridges.md) | 多前端框架桥接 | packages/types, packages/react, packages/svelte, packages/vue |
