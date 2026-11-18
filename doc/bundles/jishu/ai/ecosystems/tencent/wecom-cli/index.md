---
type: bundle
title: 企业微信官方 CLI（wecom-cli）
okf_version: "0.2"
---

# 企业微信官方 CLI（wecom-cli）

wecom-cli 是企业微信官方 CLI，采用 Rust workspace 实现并通过 npm `@wecom/cli` 1.3.4 分发；固定基线为 `1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde`（F-001、F-003、F-009）。它以服务端 discovery/schema 动态装配命令树，覆盖消息、邮件、文档、表格、日程、会议、待办、微盘、通讯录等服务（F-037、F-047）。

本知识包按中文 OKF v0.2 组织，覆盖固定基线的 172 条事实，所有实现性论断均回指 F 编号；事实、洞察、概念和示例均已于 2026-11-09 通过 V 阶段独立复核并转为 stable，示例未在本机实跑。

## 概念篇

详见 [concepts/index.md](concepts/index.md)，共 8 篇：总览、命令模型、Crate 架构、认证与会话、传输与韧性、沙箱与安全、Skills 层、开发与发布。

## 实战示例

详见 [examples/index.md](examples/index.md)，共 3 篇：首次授权与只读调用、动态 schema 调用、文件输出与沙箱排查。示例只表达调用结构，不承诺实际输出（F-048–F-052、F-162）。

## 信源与生命周期

- [事实登记](references/facts.md)：F-001–F-172，连续无跳号、无重复。
- [洞察](references/insights.md)：6 条机制洞察，证据均回指 F 编号。
- [信源登记](references/sources.md)：记录上游、基线、许可证和复核边界。
- 当前状态为 stable，已于 2026-11-09 通过 V 阶段独立复核（Grep 级实体核验 + F 编号一致性 + 结构/链接检查）；`stale_after` 为 2027-11-09，升级上游后应重新固定 commit 并按事实条目复核。

## 相关企业微信知识包

- [企业微信套件 Skill（wecom-unified）](../wecom-unified/index.md)
- [企业微信智能机器人 Python SDK](../wecom-aibot-python-sdk/index.md)
- [企业微信 5.0.10 版本说明](../wecom-5-0-10-release/index.md)
- [企业微信 5.0.12 版本说明](../wecom-5-0-12-release/index.md)
- [企业微信专题场景](../wecom-topic-scenarios/index.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
