---
okf_version: "0.2"
type: examples
title: "示例代码"
description: "jupyter_server_fileid 的可运行代码示例，涵盖编程接口、REST API 和自定义管理器。"
tags: [jupyter, fileid, examples, index]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 示例代码

本章节提供 jupyter_server_fileid 的可运行代码示例。

## 💻 示例列表

| 示例 | 简介 |
|------|------|
| [01 - 编程接口基础使用](01-basic-usage.md) | 直接使用 ArbitraryFileIdManager 和 LocalFileIdManager 的 Python API 进行索引、查询、移动、复制、删除和带外检测。 |
| [02 - REST API 使用示例](02-rest-api-usage.md) | 通过 curl、Python requests、前端 fetch/JupyterLab 插件调用 HTTP API 进行路径与 ID 的双向查询。 |
| [03 - 自定义 File ID 管理器](03-custom-manager.md) | 继承 BaseFileIdManager 实现支持 S3 对象存储的自定义管理器，包含完整代码和配置方法。 |

---

**导航：**
- [核心概念](../concepts/index.md) — 概念文档
- [源码信源](../references/index.md) — 源码信源文档
- [返回首页](../index.md)

```{toctree}
:hidden:

01-basic-usage
02-rest-api-usage
03-custom-manager
```
