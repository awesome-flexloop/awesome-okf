---
type: example
title: 动态 schema 调用
description: 展示目标服务 schema 装配、JSON 请求体、深层覆盖和分页输出的组合用法。
tags: [wecom, wecom-cli, example, schema]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 动态 schema 调用

> 本示例未在本机实跑。命令与输出只用于说明调用结构。

先查看服务目录和目标 schema：

```bash
wecom-cli schema list
wecom-cli schema get contact.users.search
```

再使用 schema 生成的方法调用：

```bash
wecom-cli contact users search \
  --json '{"keywords":["张三"]}' \
  --set limit=10 \
  --page-count 2 \
  --page-delay 100
```

`schema list` 与 `schema get` 是内建命令；请求体可以通过完整 `--json` 或可重复的 `--set path=value` 提供，分页通过 `--page-count` 进入 NDJSON 输出（F-050–F-052）。运行时只针对目标服务拉取 schema，再完成第二阶段命令树装配（F-037、F-043、F-044）。

如果 schema 装配失败，后台错误码 10021 按用法错误处理并返回退出码 2；普通成功、运行时错误和用法错误分别对应退出码 0、1、2（F-045、F-172）。
