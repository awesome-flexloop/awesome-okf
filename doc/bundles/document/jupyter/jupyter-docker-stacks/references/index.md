---
type: Reference
title: "信源索引"
description: "Jupyter Docker Stacks 源码信源登记索引，为 concepts 和 examples 提供引用目标"
tags: [reference, index, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
---

# 信源索引

本目录登记 Jupyter Docker Stacks 所有源码信源的索引，为 concepts/ 和 examples/ 文档中的 `sources` 字段提供引用目标。

## 信源文件清单

| 文件 | 内容 | 覆盖范围 |
|------|------|---------|
| [dockerfiles.md](dockerfiles.md) | 12+1个镜像Dockerfile源码路径、构建参数、CUDA变体 | 镜像层定义 |
| [startup-scripts.md](startup-scripts.md) | 启动链路脚本、Hook目录、环境变量、执行流程 | 容器启动机制 |
| [tagging-source.md](tagging-source.md) | tagging/ Python工具架构、Tagger/Manifest清单 | 标签自动化系统 |
| [tests-source.md](tests-source.md) | pytest框架、TrackedContainer、测试目录组织 | 测试框架 |
| [makefile-ci-source.md](makefile-ci-source.md) | Makefile目标、变量、GitHub Actions工作流 | 构建与CI/CD |

```{toctree}
:hidden:

dockerfiles
makefile-ci-source
startup-scripts
tagging-source
tests-source
```
