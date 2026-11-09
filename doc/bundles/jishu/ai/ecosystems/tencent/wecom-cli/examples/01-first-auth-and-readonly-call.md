---
type: example
title: 首次授权与只读调用
description: 以版本检查、授权状态、扫码初始化和通讯录只读调用串起首次接入流程。
tags: [wecom, wecom-cli, example, auth]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 首次授权与只读调用

> 本示例未在本机实跑。输出为格式示意，实际行为以固定基线对应的 CLI 为准。

## 流程

```bash
npm install -g @wecom/cli
wecom-cli --version
wecom-cli auth show --status
wecom-cli auth init --noninteractive
wecom-cli auth show --status
wecom-cli contact users search --json '{"keywords":["张三"]}'
```

安装要求 Node.js >=18，npm 包版本基线为 1.3.4；`auth show --status` 用 authorized/unauthorized 表示状态，`auth init` 支持非交互扫码模式（F-009、F-014、F-048、F-049、F-162）。通讯录是文档列出的服务之一，完整方法和参数由运行时 schema 提供（F-047、F-072）。

## 判断点

- 版本不满足预期时先停止业务调用，以 `--version` 复核二进制来源（F-041、F-042）。
- 状态为 unauthorized 时执行初始化；扫码轮询间隔为 3 秒，超时为 300 秒（F-086）。
- 业务命令的完整参数由目标服务 schema 动态装配，不能仅凭根帮助推断（F-037、F-044）。
