---
okf_version: "0.2"
type: Example
title: "skylinevpn-cli 演练层索引"
description: "安装校验卸载、日常使用排障、维护者发布 Runbook 三篇演练的入口与性质说明"
---

# 演练层索引

> 三篇演练均**未在实机执行**，命令来自仓库文档与脚本；「文档口径」与「可自行验证」在正文中逐步标注。

| 演练 | 参与者 | 内容 | 预计产出 |
|------|--------|------|---------|
| [00 安装、校验与卸载](00-install-verify-uninstall.md) | 使用者 / 运维 | 一键与离线安装、`--check`、`SHA256SUMS` 校验、两档卸载 | 一台可运行 `skyline version` 的机器 |
| [01 日常使用与排障](01-daily-usage-and-troubleshooting.md) | 使用者 | 登录、节点、连接、模式与语言；按症状分流的排障决策树 | 能判断问题落在订阅、TUN、服务还是 PATH |
| [02 维护者发布 Runbook](02-maintainer-release-runbook.md) | 维护者 | 六步主流程 + 仅换安装器 + 预发布晋升 + 容器测试 | 一个通过核验的 Release |

```{toctree}
:maxdepth: 1
:caption: 演练

00-install-verify-uninstall
01-daily-usage-and-troubleshooting
02-maintainer-release-runbook
```
