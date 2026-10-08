# Examples

本目录包含腾讯会议 CLI（tmeet）的 4 个实战示例，覆盖上手、知识沉淀、行政排期与实时自动化四类典型场景。

- [01 - 十分钟上手](01-quickstart.md) — 安装 CLI/Skill、设备码登录、创建并查询第一场会的最小闭环
- [02 - 会后取纪要工作流](02-minutes-workflow.md) — 双纪要权限分流、失败降级、跨会议双搜、录制权限两阶段申请
- [03 - 周期会议与参会明细导出](03-recurring-export.md) — 周期排期、受邀管理、异步导出 job 轮询、等候室记录
- [04 - 事件订阅自动化](04-event-automation.md) — event consume 批处理/常驻、NDJSON+jq、ready 同步、bus 自愈（v1.0.18+）

## 示例对应关系

| 示例 | 对应概念 | 涉及信源 |
|------|----------|----------|
| 十分钟上手 | [00 定位](../concepts/00-overview.md)、[01 安装授权](../concepts/01-install-auth.md)、[02 命令约定](../concepts/02-command-map.md)、[03 会议生命周期](../concepts/03-meeting-lifecycle.md) | [安装指南](../references/install-guide.md)、[命令参考](../references/command-reference.md)、[腾讯云文档](../references/cloud-doc.md) |
| 会后取纪要 | [04 双纪要体系](../concepts/04-record-minutes.md)、[06 安全契约](../concepts/06-agent-safety-contract.md) | [命令参考](../references/command-reference.md)、[Skill 清单](../references/skill-manifest.md) |
| 周期会议与导出 | [03 会议生命周期](../concepts/03-meeting-lifecycle.md)、[05 报告与控制](../concepts/05-report-control.md) | [命令参考](../references/command-reference.md)、[Skill 清单](../references/skill-manifest.md) |
| 事件订阅自动化 | [07 事件总线](../concepts/07-event-bus.md)、[02 命令约定](../concepts/02-command-map.md) | [命令参考](../references/command-reference.md)、[Skill 清单](../references/skill-manifest.md) |

```{toctree}
:hidden:
:maxdepth: 7

01-quickstart
02-minutes-workflow
03-recurring-export
04-event-automation
```
