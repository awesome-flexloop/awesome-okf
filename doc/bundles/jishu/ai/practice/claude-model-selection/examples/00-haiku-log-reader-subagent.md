---
type: Example
title: "用 Haiku 子代理读日志"
description: "照博文示例创建一个只读日志的 Haiku 子代理，把失败定位交给便宜模型，把修复判断留给主模型。"
tags: [claude-code, subagents, haiku, practice]
generated: { by: "lobsterai/main", at: "2026-11-10T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T13:30:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: cc-model-config
    resource: https://code.claude.com/docs/en/model-config
---

# 用 Haiku 子代理读日志

## 目标

让一个 Haiku 子代理读完测试日志，只回报“文件、测试名、第一行错误”，不修改任何文件；主模型拿着这份清单做修复判断。对应博文的 `log-reader` 示例（F-055）。

**预期产出**：一个可复用的 `.claude/agents/log-reader.md`，以及一次可验证的调用。

## 前置条件

1. Claude Code 已安装并登录。
2. 版本满足 `haiku` 别名解析到 Haiku 5.5 的要求：v2.1.293 或更高（F-058）。用 `claude --version` 确认；低了就 `claude update`。
3. 有一份测试输出或日志文件可读。

## 步骤

**1. 建目录与文件。** 在项目根目录创建 `.claude/agents/log-reader.md`。

```bash
mkdir -p .claude/agents
```

**2. 写入子代理定义。** 内容与博文示例一致：

```markdown
---
name: log-reader
description: Reads test output and logs, and reports each failing case. Use after a test run.
tools: Read, Grep, Glob, Bash
model: haiku
---

Read the logs you're given. For each failure, report the file, the test name and the first error line. Don't edit any files.
```

三个字段的作用：`tools` 限定它只能读与查，不能写；`model: haiku` 把费用压到家族最低档（F-054）；正文用一句“不要改文件”再加一道行为约束。

**3. 触发一次。** 先跑测试并留下输出，然后对主模型说：

```text
Use the log-reader subagent on test-output.log. Report each failing case.
```

**4. 检查结果。** 合格的回传应满足：

1. 每条失败都有文件路径、测试名、第一行错误。
2. 没有任何 Edit/Write 动作。
3. 没有对根因下结论——那是主模型的工作。

## 为什么这样分工

博文的原则是：小模型只做错误容易发现的工作，改代码与判断留给主模型（F-056）。日志读取正好符合——读错了很容易被发现，代价也低；而“这个失败说明哪个设计有问题”需要判断，放给 Haiku 会引入难以察觉的偏差。

另一个收益是上下文：子代理在自己的窗口里读完整日志，只回传摘要，主模型不必把几万行日志装进上下文（F-054）。主模型越大，这个收益越明显（F-047）。

## 常见问题

**子代理没有按预期用 Haiku。** 先确认版本（F-058）；再确认 `model:` 字段拼写；如果项目固定了 `CLAUDE_CODE_SUBAGENT_MODEL`，它会覆盖未指定模型的子代理。

**在内置 Explore 上省钱失败。** Claude Code 的内置 Explore 子代理跑会话模型，不总是 Haiku；要省成本得自建同名 `Explore` 并设 `model: haiku`（F-057）。

**子代理开始改文件。** `tools` 里去掉 `Edit`/`Write`，并在正文重复“不要编辑”。工具白名单比提示词更可靠。

**日志太长导致截断。** 让子代理先用 `Grep` 定位 `FAIL`/`ERROR` 再读上下文，而不是整文件通读。

## 验收清单

1. 文件位于 `.claude/agents/log-reader.md`，frontmatter 可解析。
2. 一次调用能返回结构化失败清单。
3. 调用期间没有文件被修改。
4. `/usage` 中该子代理的 token 计入 Haiku 档位。
