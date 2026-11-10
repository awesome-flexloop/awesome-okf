---
okf_version: "0.2"
type: index
title: concepts 索引
description: Claude Agent SDK 生产级智能体构建指南概念文档——发布与能力、安装与配置、权限与 hooks、生产加固、选型与采用
tags: []
---

# concepts/ 概念文档

| 文档 | 说明 |
|------|------|
| [00-release-and-capabilities.md](00-release-and-capabilities.md) | 发布日、Claude Code SDK 更名、六项能力、四种接入方式、agent loop 与适用边界 |
| [01-quickstart-and-configuration.md](01-quickstart-and-configuration.md) | TypeScript/Python 安装、API key、最小 agent、7 项配置、工具三档、版本与打包边界 |
| [02-permissions-and-hooks.md](02-permissions-and-hooks.md) | `allowed_tools` 真实语义、六步权限评估、六种模式、PreToolUse 写法、两个审计盲区 |
| [03-production-hardening.md](03-production-hardening.md) | 威胁模型、沙箱、审计字段、最小权限四级阶梯、8 项边界测试、上线清单 |
| [04-sdk-vs-raw-api-and-adoption.md](04-sdk-vs-raw-api-and-adoption.md) | SDK/CLI/Client SDK/Managed Agents 四选一、SDK vs raw API、分阶段采用、六类反模式 |

```{toctree}
:hidden:
:maxdepth: 2

00-release-and-capabilities
01-quickstart-and-configuration
02-permissions-and-hooks
03-production-hardening
04-sdk-vs-raw-api-and-adoption
```
