---
type: Example
title: "实操二：不会重复计费的 Agent 自动化脚本"
description: "用 --async + video wait --for 分步等待、分离 stdout/stderr、读取 resource_ready 事件拿本地产物、exit 8 转人工、exit 6 三态判定的完整脚本范式"
tags: [vibeknow, cli, 自动化, agent, 脚本, 计费安全]
generated:
  by: trae-seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: "2027-04-21"
sources:
  - id: vksrc
    resource: https://github.com/vibeknow/cli
    title: "VibeKnow CLI 源码仓库 v0.9.2 @ 93a26eca"
  - id: skill
    resource: /concepts/10-ai-skill-contract.md
    title: "AI Skill 运行契约"
---

# 实操二：不会重复计费的 Agent 自动化脚本

> 本文脚本基于 v0.9.2 源码（commit `93a26eca`）与仓库自带 Skill 契约写成。**本文作者未实机执行**；接入前请在测试账号上验证计费相关分支。

Agent 驱动这个 CLI 最大的风险是**重复计费**与**重复展示**。这份脚本范式把六个风险点各自钉死。

## 铁律速查

| 风险 | 纪律 |
|---|---|
| 重复渲染 | 同一请求只跑一次 `create`；丢了 id 先 `jobs list` |
| 重复导出 | 导出对 (user, session) 幂等，但 `create` 不是 |
| 流被合并 | **不要 `2>&1`**，stdout 与 stderr 分开 |
| 事件被跳过 | 不要用 `tail -n 20` 当游标 |
| 静默被误判 | 安静时不要重发，等终态事件 |
| 授权被代行 | 不要自己编 `--confirm`，不要主动加 `--yes` |

## 脚本骨架

```bash
#!/usr/bin/env bash
set -uo pipefail

OUT_DIR="${OUT_DIR:-./vk-out}"
STDOUT_LOG="$OUT_DIR/create.stdout.json"
STDERR_LOG="$OUT_DIR/create.stderr.log"
mkdir -p "$OUT_DIR"

# 1) 先查本地账本：这一请求是否已经跑过
if existing=$(vibeknow jobs list --output json 2>/dev/null \
             | jq -r '.[0].session_id // empty'); then
  echo "已有运行 $existing，复用而非重跑" >&2
  SESSION_ID="$existing"
else
  # 2) 只跑一次 create。stdout 与 stderr 分开落盘。
  vibeknow create \
    --from "$INPUT" \
    --mode image --aspect vertical --language zh-CN \
    --preview-dir "$OUT_DIR" \
    --async \
    --output json \
    >"$STDOUT_LOG" 2>"$STDERR_LOG"
  rc=$?

  if [ $rc -eq 8 ]; then
    # 3) 出口码 8 = 需要用户决策的计费动作，转人工
    echo "需要用户确认计费动作：" >&2
    jq -r '.error.detail // .' "$STDOUT_LOG" >&2
    exit 8
  fi
  if [ $rc -ne 0 ]; then
    echo "create 失败，退出码 $rc" >&2
    exit $rc
  fi

  SESSION_ID=$(jq -r '.session_id' "$STDOUT_LOG")
  TASK_ID=$(jq -r '.task_id' "$STDOUT_LOG")
fi

# 4) 分步等待。每轮 --for 90s，退出码 6 = 等待预算用尽，继续下一轮。
while true; do
  vibeknow video wait "$TASK_ID" --session-id "$SESSION_ID" --for 90s \
    >"$OUT_DIR/wait.stdout" 2>>"$OUT_DIR/wait.stderr"
  rc=$?
  if [ $rc -eq 0 ]; then break; fi
  if [ $rc -eq 6 ]; then
    # 6 也可能是投递状态未知，查 error.detail.delivery 再决定
    detail=$(jq -r '.error.detail.delivery // "unknown"' "$OUT_DIR/wait.stdout" 2>/dev/null)
    if [ "$detail" = "not_submitted" ]; then
      echo "确认未提交，可以重试" >&2
    elif [ "$detail" = "indeterminate" ]; then
      echo "状态不明，先查状态再决定，勿重跑" >&2
      vibeknow video status "$TASK_ID" --session-id "$SESSION_ID" >&2
      exit 6
    else
      echo "仍在等待，继续" >&2
    fi
    continue
  fi
  echo "wait 失败，退出码 $rc" >&2
  exit $rc
done
```

## 导出：交给人决定

```bash
vibeknow video export "$TASK_ID" --session-id "$SESSION_ID" \
  >"$OUT_DIR/export.stdout.json" 2>"$OUT_DIR/export.stderr.log"
rc=$?

case $rc in
  0) echo "已导出" >&2 ;;
  6) echo "导出状态未知：先查状态，不要重跑" >&2; exit 6 ;;
  7) echo "预览已在、MP4 未就绪（部分成功）" >&2
     jq -r '.error.detail.next_actions[0].command' "$OUT_DIR/export.stdout.json" >&2
     exit 7 ;;
  8) echo "需要用户批准计费：" >&2
     jq -r '.resume_command // .error.detail.resume_command' "$OUT_DIR/export.stdout.json" >&2
     exit 8 ;;
  *) echo "导出失败，退出码 $rc" >&2; exit $rc ;;
esac
```

## 消费 resource_ready 事件

事件走 stderr，每行以 `vk_event=` 开头：

```bash
# 从 stderr 日志里取出本地产物路径
grep -o '^{"type":"resource_ready".*$' "$OUT_DIR/wait.stderr" \
  | sed 's/^vk_event=//' \
  | jq -r 'select(.type == "resource_ready") | "\(.asset_kind)\t\(.local_path)"'
```

要点：

- **只认 `local_path`**，别去猜文件名，也别去用 `share_url`（签名会过期）
- **内容未变化不会重复宣告**，所以同一个目录可以被多次调用安全地写入
- **每个新路径交给用户一次**，重复展示同一张图是噪音

## 事件游标：记 offset，不要 tail

```bash
# 第一次：记下当前 stderr 偏移
OFFSET=$(wc -c < "$STDERR_LOG")

# 之后：只读新增部分
tail -c +$((OFFSET + 1)) "$STDERR_LOG" | grep '^vk_event='
OFFSET=$(wc -c < "$STDERR_LOG")
```

用 `tail -n 20` 会跳过整段——事件是成批到达的。

## 只读命令是安全的

以下命令不计费、不改状态，可以随便重跑：

```bash
vibeknow jobs list
vibeknow video list
vibeknow video status "$TASK_ID" --session-id "$SESSION_ID"
vibeknow kb list
vibeknow voice list
vibeknow theme list --mode image
```

`vk jobs prune` 只动本地账本、不碰后端，但**裸调用会被拒**：

```bash
vibeknow jobs prune --terminal          # 只丢已结束的运行
vibeknow jobs prune --older-than 30d
```

`vk kb prune` 删的是远端知识库，**默认 dry-run**：

```bash
vibeknow kb prune --pattern "tmp-*" --output json   # 先看
vibeknow kb prune --pattern "tmp-*" --yes            # 再删
```

## 排查清单

| 症状 | 检查 |
|---|---|
| 同一请求跑了两次 | 是否在 `create` 失败后无条件重试？先查 `jobs list` |
| stdout 里是散文 | 是否忘了 `--output json`？ |
| 看不到进度 | 事件在 stderr，且默认只有 json 模式开启；`VIBEKNOW_EVENTS=1` 可在文本模式开启 |
| 退出码 8 | 正常——把 `resume_command` 转达给人 |
| 退出码 6 | 查 `error.detail.delivery` 三态，别盲目重跑 |

## 延伸

- [/concepts/10-ai-skill-contract.md](/concepts/10-ai-skill-contract.md) —— 这份脚本的规范来源
- [/concepts/04-run-ledger-and-async.md](/concepts/04-run-ledger-and-async.md) —— 账本与异步语义
- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码完整语义
- [/examples/02-style-reuse-and-maintenance.md](/examples/02-style-reuse-and-maintenance.md) —— 把风格固定下来，减少参数出错
