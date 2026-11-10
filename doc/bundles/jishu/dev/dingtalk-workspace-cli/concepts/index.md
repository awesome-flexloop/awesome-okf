---
okf_version: "0.2"
type: Concept
title: "dws 概念地图"
description: "dingtalk-workspace-cli 知识包概念层导航——定位与全景、命令契约、静态管线、产品组织、认证身份、输出契约、安全审计、Agent 集成、工程边界"
---

# 概念地图

| # | 篇目 | 层 | 回答的问题 |
|---|------|----|-----------|
| [00](00-overview-and-positioning.md) | 定位与全景 | 定位层 | dws 是什么、给谁用、由哪些面组成、什么场景不适用 |
| [01](01-command-contract-model.md) | 命令契约模型 | 结构层 | 一条命令由哪些声明组成、flag 如何回退、约束如何表达、执行体有几类 |
| [02](02-static-endpoint-pipeline.md) | 静态端点管线 | 架构层 | 命令表从哪来、为什么不跑运行时 `tools/list`、生成物如何守护 |
| [03](03-command-surface-and-products.md) | 命令面与产品组织 | 结构层 | 20 个服务域怎么切、产品如何归并、命令发现走哪三条路径 |
| [04](04-auth-identity-and-profiles.md) | 认证、身份与多组织 | 机制层 | 三条登录路径、凭据如何落盘、多组织如何切换、跨机如何迁移 |
| [05](05-output-and-schema-discovery.md) | 输出与 Schema 发现 | 接口层 | 四种格式怎么选、jq/fields 怎么投影、退出码与错误结构、Schema 如何分级读 |
| [06](06-safety-dry-run-and-audit.md) | 安全、预览与审计 | 治理层 | dry-run 看什么、确认门何时拦、审计能回答什么、出站边界在哪 |
| [07](07-agent-skills-and-events.md) | Agent 技能与事件 | 集成层 | multi/mono 怎么选、事件怎么订阅、raw api 何时用、Agent 标识怎么设 |
| [08](08-engineering-and-boundaries.md) | 工程与边界 | 边界层 | 仓库多大、九道门禁是什么、测试怎么分层、什么缺口必须承认 |

## 学习路径

- **只想判断值不值得用**：00 → 03 → 08
- **要写脚本或接入 Agent**：00 → 01 → 05 → 07 → [examples/02](../examples/02-agent-workflow.md)
- **要管权限与合规**：00 → 04 → 06 → 08
- **要改源码或做二次开发**：00 → 01 → 02 → 08
- **任何数字要引用前**：先读 [references/facts.md](../references/facts.md) 与 [references/verification.md](../references/verification.md)

## 一条主线

九个概念围绕一个判断展开：**dws 把「命令契约」当成唯一事实源，用静态生成替代运行时发现，从而同时服务人与 Agent 两个表面**（F-026 ~ F-032）。

由此派生三条阅读线索：

1. **契约线**：01（声明什么）→ 02（怎么生成）→ 05（怎么消费）；
2. **安全线**：04（谁在调用）→ 06（调用前看什么、调用后留什么）→ 07（Agent 侧如何被约束）；
3. **边界线**：03（产品怎么切）→ 08（工程怎么守、哪里不能承诺）。

```{toctree}
:hidden:
:maxdepth: 2

00-overview-and-positioning
01-command-contract-model
02-static-endpoint-pipeline
03-command-surface-and-products
04-auth-identity-and-profiles
05-output-and-schema-discovery
06-safety-dry-run-and-audit
07-agent-skills-and-events
08-engineering-and-boundaries
```