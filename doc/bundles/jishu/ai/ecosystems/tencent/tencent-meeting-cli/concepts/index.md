# Concepts

本目录包含腾讯会议 CLI（tmeet）的 9 个概念文档，按「入门 → 核心域 → Agent 契约 → 高级能力」组织。

## 入门与全局约定

- [00 - 产品定位与双件架构](00-overview.md) — CLI + Skill 双件模型、调用链路、账号条件与命令域全景
- [01 - 安装与 OAuth2 授权](01-install-auth.md) — npm/源码安装、Skill 安装、设备码登录、Keychain 凭证
- [02 - 命令体系与全局约定](02-command-map.md) — 44 命令地图、JSON 信封、compact、ISO 8601、游标分页、bool 语法

## 核心业务域

- [03 - 会议全生命周期管理](03-meeting-lifecycle.md) — 创建（普通/周期）、查询、修改、取消、受邀成员
- [04 - 录制、转写与双纪要体系](04-record-minutes.md) — record/minutes 双链路、权限两阶段申请、纪要分流路由
- [05 - 参会报告与会中控制](05-report-control.md) — 参会明细、异步导出、呼叫/踢人/等候室、通讯录白名单

## Agent 契约与高级能力

- [06 - Agent 安全契约](06-agent-safety-contract.md) — 9 个二次确认命令、跨轮确认、meeting_id 禁令、脱敏纪律
- [07 - 实时事件总线](07-event-bus.md) — event 命令组、per-host bus、NDJSON、ready 标记与退出码（v1.0.18+）
- [08 - 应用配置与运维反馈](08-app-tshoot.md) — app 会中展示配置、tshoot 日志导出与结构化反馈

## 阅读建议

1. **新用户**：00 → 01 → 02，再配合 [十分钟上手示例](../examples/01-quickstart.md)
2. **会议管理员/助理**：03 → 05 → 06
3. **知识管理/纪要场景**：04 必读，配合[会后取纪要示例](../examples/02-minutes-workflow.md)
4. **自动化/集成开发者**：02 → 07 → 08，配合[事件订阅示例](../examples/04-event-automation.md)
5. **所有 Agent 集成者**：06 为必读红线

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-install-auth
02-command-map
03-meeting-lifecycle
04-record-minutes
05-report-control
06-agent-safety-contract
07-event-bus
08-app-tshoot
```
