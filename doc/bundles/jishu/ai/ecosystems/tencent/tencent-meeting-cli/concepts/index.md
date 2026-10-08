# Concepts

本目录包含腾讯会议 CLI（tmeet）的 14 个概念文档，按「入门 → 核心域 → Agent 契约 → 高级能力 → 源码内部机制」组织。00~08 基于官方文档信源（用户面），09~13 基于 v1.0.18 固定 tag 源码（实现面，第三轮增量）。

## 入门与全局约定

- [00 - 产品定位与双件架构](00-overview.md) — CLI + Skill 双件模型、调用链路、账号条件与命令域全景
- [01 - 安装与 OAuth2 授权](01-install-auth.md) — npm/源码安装、Skill 安装、设备码登录、Keychain 凭证
- [02 - 命令体系与全局约定](02-command-map.md) — 44 命令地图、v1.0.0 十九命令存活对照、JSON 信封、compact、ISO 8601、游标分页、bool 语法

## 核心业务域

- [03 - 会议全生命周期管理](03-meeting-lifecycle.md) — 创建（普通/周期）、查询、修改、取消、受邀成员
- [04 - 录制、转写与双纪要体系](04-record-minutes.md) — record/minutes 双链路、权限两阶段申请、纪要分流路由
- [05 - 参会报告与会中控制](05-report-control.md) — 参会明细、异步导出、呼叫/踢人/等候室、通讯录白名单

## Agent 契约与高级能力

- [06 - Agent 安全契约](06-agent-safety-contract.md) — 9 个二次确认命令、跨轮确认、meeting_id 禁令、脱敏纪律
- [07 - 实时事件总线](07-event-bus.md) — event 命令组、per-host bus、NDJSON、ready 标记与退出码（v1.0.18+）
- [08 - 应用配置与运维反馈](08-app-tshoot.md) — app 会中展示配置、tshoot 日志导出与结构化反馈

## 源码内部机制（v1.0.18 固定 tag，第三轮增量）

- [09 - 源码工程总览](09-codebase-architecture.md) — module/依赖、cmd-internal 分层、Tmeet 容器与四主机、5 目标静态构建、Node 包装器分发
- [10 - 命令装配与中间件](10-command-assembly.md) — 手写 cobra 壳、38 个 ApiCmd 常量真相、compact 远程字段表、分页兼容、隐藏命令
- [11 - 凭证安全内部机制](11-credential-security-internals.md) — OAuth 设备码时序、三平台密钥托管、AES-256-GCM/AAD、原子写与资源释放钩子
- [12 - 事件总线内核](12-event-bus-internals.md) — 七组件微内核、alive-lock 选举、wsspb、8 个硬编码 EventKey、owner 哈希与清理闭环
- [13 - 传输、输出与跨平台工程](13-cross-platform-engineering.md) — 双代理/诊断头/重试、16 枚举文件、输出中间件、自研日志、崩溃上报与版本沿革

## 阅读建议

1. **新用户**：00 → 01 → 02，再配合 [十分钟上手示例](../examples/01-quickstart.md)
2. **会议管理员/助理**：03 → 05 → 06
3. **知识管理/纪要场景**：04 必读，配合[会后取纪要示例](../examples/02-minutes-workflow.md)
4. **自动化/集成开发者**：02 → 07 → 08，配合[事件订阅示例](../examples/04-event-automation.md)；需要理解 bus 内部/排障时续读 12
5. **所有 Agent 集成者**：06 为必读红线
6. **源码学习者/二开者**：09 → 10 → 11 → 12 → 13，配合 [源码信源登记](../references/source-code.md) 与 F-113~F-199 事实

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
09-codebase-architecture
10-command-assembly
11-credential-security-internals
12-event-bus-internals
13-cross-platform-engineering
```
