---
type: toctree
title: CubeSandbox 实操示例
---

# 实操示例

四篇可照做的示例，从首次调用 SDK 到集群部署、模板制作与暂停恢复策略。

| 示例 | 内容 |
|---|---|
| [01 三端 SDK 完整工作流](01-sdk-workflow.md) | Python/Go/Node 创建沙箱、执行命令、文件读写与快照克隆 |
| [02 单机、多节点与离线部署实战](02-cluster-deploy.md) | 一键部署、节点扩容、Kubernetes 与离线环境校验 |
| [03 快照模板制作实战](03-template-build.md) | 从 OCI 镜像/运行中沙箱制作模板、探针与分发重做 |
| [04 超时策略与自动暂停恢复](04-pause-resume-policy.md) | 五状态、on_timeout 策略、CLM 选主与访问自动唤醒 |

```{toctree}
:caption: 实操示例
:maxdepth: 2

01-sdk-workflow
02-cluster-deploy
03-template-build
04-pause-resume-policy
```
