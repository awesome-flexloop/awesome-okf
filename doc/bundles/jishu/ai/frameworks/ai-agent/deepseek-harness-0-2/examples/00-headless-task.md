---
type: example
title: "一次性 Headless 任务"
description: "用 dsh --profile headless 在 CI 里跑一次性任务：三种输入方式、JSON 行式事件流、退出码语义与凭据来源。"
tags: [deepseek-harness, headless, ci, example]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 packages/bundle/headless 与 apps/cli/reference
---

# 一次性 Headless 任务

> 场景：CI 或脚本里跑一个 Agent 任务，打印结果即退出，不留 GUI、端口或后台进程。

## 1. 三种写法

```sh
# ① 位置参数
dsh --profile headless "run the tests"

# ② stdin 管道
{ echo "Summarize these changes:"; git diff --stat; } | dsh --profile headless

# ③ JSON 行式事件流（便于机器解析）
dsh --profile headless --json "job"
```

`dsh --profile headless` 也可简写为 `dsh headless`（前提是紧跟 `dsh` 且不是保留的 `plugin`）。

## 2. 行为要点

- **stdout 只打印最终答案**；非空的提供方推理以 `dsh: reasoning:` 标题流式写入 **stderr**；没有推理内容的成功响应保持 stderr 为空
- 退出码：`completed` → **0**，其余（中止/出错）→ **1**
- 无任务的调用是该应用的**用法错误**
- headless profile **不挂载**浏览器 Connection、HTTP 服务器、Web 运行时或浏览器客户端，**不打开监听端口**
- `--session-id` 可续接同一对话（持久会话按 `session.vN.jsonl` 落盘）

`--json` 的事件类型：`session` / `status` / `text` / `thinking` / `tool_call` / `tool_result` / `final` / `error`。

## 3. 凭据来源

headless **禁用托管凭据**——密钥按以下顺序查找：

```text
启动环境变量 → ./.env（调用目录） → $DSH_HOME/.env
```

`PATH` / `DSH_*` / `XDG_*` 等启动变量会被 `.env` 拒绝；四个代理类变量只接受来自 home `.env` 的值。

## 4. CI 里的最小配方

```sh
#!/usr/bin/env bash
set -euo pipefail

export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?missing key}"

out="$(dsh --profile headless --json \
  "Summarize the diff and list the files that need review")"

# 逐行 JSON 事件流，取 final 事件的文本
printf '%s\n' "$out" | grep '"type":"final"' | jq -r '.text'
```

配合 [安全模型](../concepts/09-security-model.md)：CI 里把审批策略设为 `never`（确定性拒绝而非挂起），沙箱保持 `workspace-write`。

## 5. 排查

- 想知道最终组合出的配置：`dsh --profile headless --dump-config`
- 启动失败时看 `$DSH_HOME/logs/startup-<timestamp>-<uuid>.log`
- 退出码 1 且无 stdout：多半是任务失败而非配置问题；`--json` 的 `error` 事件会带原因

## 相关

- [应用形态](../concepts/10-application-forms.md)
- [入门指引](../concepts/00-getting-started.md)
