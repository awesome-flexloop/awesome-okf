---
okf_version: "0.2"
type: Example
title: "skylinevpn-proxylist 演练层索引"
description: "三篇可操作演练：本地复现构建与验证幂等、消费方接入与更新策略、维护者发布 Runbook"
---

# 演练层索引

| 演练 | 你要完成的事 | 前置条件 | 预计产出 |
|------|------------|---------|---------|
| [00 本地复现构建](00-local-rebuild-and-idempotency.md) | 在本地跑一次 `build.sh`，并证明第二次运行不再产生差异 | bash、curl、python3、可访问上游 | 一份更新后的 `proxy.list` + 一份空 diff |
| [01 消费方接入](01-consumer-integration.md) | 用固定 URL 拉取清单，并按三节语义做一次匹配 | 可访问 GitHub | 一个能判断「某主机是否命中」的小脚本 |
| [02 维护者 Runbook](02-maintainer-runbook.md) | 手动触发发布、换上游源、处理发版异常 | 仓库写权限 | 一次可核对的手动发布 |

> **统一边界**：三篇演练的命令均**未在本次研读中执行**。命令依据来自 `scripts/build.sh`、`scripts/merge.py`、`.github/workflows/release.yml` 与 `README.md` 的源码与文档，实际执行结果可能因上游变化、Python 版本、网络环境而不同。

```{toctree}
:maxdepth: 1
:caption: 演练

00-local-rebuild-and-idempotency
01-consumer-integration
02-maintainer-runbook
```
