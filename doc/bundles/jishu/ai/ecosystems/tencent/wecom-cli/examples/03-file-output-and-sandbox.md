---
type: example
title: 文件输出与沙箱排查
description: 展示下载输出目录选择、配置目录隔离和 deny 规则排查路径。
tags: [wecom, wecom-cli, example, sandbox]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 文件输出与沙箱排查

> 本示例未在本机实跑。路径和结果均为示意。

```bash
wecom-cli disk files download --output-dir ./downloads
```

产生文件的分支默认写入当前工作目录，`--output-dir` 可重定向目录；文件写入前会经过工作域沙箱，成功后 stdout 返回下载结果 JSON（F-051、F-116、F-118、F-119）。

## 排查顺序

1. 确认目标路径位于工作域允许的 cwd 或固定临时目录内（F-118、F-131）。
2. 排除配置目录、`.env`、`.ssh`、密钥证书扩展名等 deny 形状（F-120–F-124）。
3. 若使用 Windows，额外检查系统目录和 DPAPI 凭据目录规则（F-126、F-127）。
4. 注意 deny 恒优先于 allow；即使取消 roots 限制，已安装的 deny 仍然拒绝匹配路径（F-128）。

下载中断、路径越界或文件名不合法时，应保留 stderr 与退出码，不要把业务 stdout 当作诊断日志；入口层约定退出码 1 为运行时错误、2 为用法错误（F-059、F-172）。
