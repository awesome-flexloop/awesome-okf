---
okf_version: "0.2"
type: examples
title: "示例代码"
description: "jupyter_core v5.9.1 可运行代码示例索引，覆盖基础使用、自定义应用和路径定制。"
tags: [jupyter, core, examples, index]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: version-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/version.py"
    title: "jupyter_core/version.py"
---

# 示例代码

本章节提供 jupyter_core 核心 API 的可运行代码示例。

## 示例列表

| 示例 | 简介 |
|------|------|
| [01 - 基础使用示例](01-basic-usage.md) | 查询 Jupyter 路径、使用 secure_write 安全写入文件、收集环境诊断信息、发现可用子命令。 |
| [02 - 自定义 JupyterApp 应用](02-custom-app.md) | 继承 JupyterApp 创建完整应用，添加自定义配置项、使用 @run_sync 装饰异步方法、扩展命令行选项。 |
| [03 - 路径定制与环境变量](03-path-customization.md) | 通过环境变量自定义目录位置、附加搜索路径、虚拟环境路径行为、运行时安全权限、多环境隔离。 |

---

**导航：**
- [核心概念](../concepts/index.md) — 系统学习 jupyter_core 架构与 API
- [源码信源](../references/index.md) — 源码信源文档
- [返回首页](../index.md)

```{toctree}
:hidden:

01-basic-usage
02-custom-app
03-path-customization
```
