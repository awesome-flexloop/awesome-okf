---
type: example
title: 博客生成三步法调用时序
description: "基于 blog_submit.sh / blog_status.sh / blog_result.sh 与 blog.sh 同步封装，演练「提交→轮询→取结果」的完整调用时序及契约层与实现层的节奏差异。"
tags: [scholarclaw, example, blog-generation, async, polling]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# 博客生成三步法调用时序

本演练基于 `examples/blog-generation.md` 示例（F-sc-056）与真实脚本（F-sc-035~F-sc-037），场景为：为 ArXiv 论文 `2303.14535` 生成一篇博客。

博客生成是 ScholarClaw 中**唯一的异步长任务**：SKILL.md 约定按「提交 → 轮询任务状态 → 获取结果」三步执行（F-sc-047）。分步调用与同步封装两种方式各有适用场景，下文逐一演练。

## 方式一：分步调用（三步法）

### 第 1 步：提交任务

`blog_submit.sh` 以 multipart 表单（curl `-F` 参数）向 `/api/blog/submit` 提交（F-sc-035）：

```bash
./scripts/blog_submit.sh -i 2303.14535
```

参数说明：`-i/--arxiv-ids` 接受 ArXiv ID 或 URL，逗号分隔可合并多篇（如 `"2303.14535,1706.03762"`）；`-f/--file PATH` 上传本地 PDF（可多次指定）；`-v/--views TEXT` 附加个人观点以引导博客侧重点。

响应（输出任务 ID 等字段，F-sc-035）：

```json
{
  "task_id": "blog_abc123def456",
  "status": "pending",
  "message": "任务已提交，正在后台处理中"
}
```

提交后注意保存 `task_id`。注意编码差异：TS 侧 `submitBlog()` 走 `URLSearchParams` 表单编码（F-sc-015），shell 侧走 multipart，两者不同但服务端均接受。

### 第 2 步：轮询任务状态

`blog_status.sh` 查询 `/api/blog/task/{id}`（F-sc-036）：

```bash
./scripts/blog_status.sh -i blog_abc123def456
```

响应：

```json
{
  "task_id": "blog_abc123def456",
  "status": "running",
  "progress": {
    "step": "generate",
    "stage": "processing",
    "message": "正在生成报告..."
  },
  "created_at": "2024-01-15T10:30:00"
}
```

轮询节奏要遵守**契约层**约定：SKILL.md 要求间隔 10–15 秒、最多 40 次（最坏约 10 分钟）（F-sc-047）。注意状态取值的防御性判断：类型层枚举为 `pending/running/completed/failed` 四值（F-sc-007），但服务端实际可能返回 `processing`、`queued`、`success` 等超集取值（F-sc-063）——`blog.sh` 即以三组并集分支匹配（`completed|success`、`failed|error`、`pending|running|processing|queued`，F-sc-037），自研轮询应沿用分组匹配而非精确等值比较（详见 [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)）。

### 第 3 步：获取结果

`blog_result.sh` 查询 `/api/blog/result/{id}`（F-sc-036）：

```bash
./scripts/blog_result.sh -i blog_abc123def456
```

响应含 `title` 与 `blog_content`（Markdown 正文，对应 `BlogResult` 在 `BlogTask` 基础上增加的 `markdown_content`/`blog_content` 字段，F-sc-026）：

```json
{
  "task_id": "blog_abc123def456",
  "status": "completed",
  "title": "Understanding the Paper Title",
  "blog_content": "# Paper Title\n\n## Introduction\n...",
  "created_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:35:00"
}
```

常用输出控制：`--content-only` 只输出博客正文；`-o blog.md` 保存到文件。

## 方式二：同步封装（一行命令）

`blog.sh` 把三步串行为一个命令：提交 → 按 `POLL_INTERVAL=5` 秒轮询 → 直到完成或超出 `DEFAULT_TIMEOUT=600` 秒 → 取结果（F-sc-037）：

```bash
# 同步等待，完成后直接输出结果
./scripts/blog.sh -i 2303.14535

# 只提交不等待（等价于 blog_submit.sh）
./scripts/blog.sh -i 2303.14535 --no-wait

# 自定义等待上限并保存正文
./scripts/blog.sh -i 2303.14535 -t 900 -o blog.md
```

注意：`blog.sh` 不在 `package.json` 的 14 个 supportedCommands 中，但 `install.sh` 生成的 `sc-blog` 别名指向它（F-sc-064）——功能真实可用。

## 契约层与实现层的节奏差异

两套轮询参数**不一致**（F-sc-047 vs F-sc-037）：

| 来源 | 轮询间隔 | 最大轮询 | 定位 |
|------|---------|---------|------|
| SKILL.md（LLM 契约） | 10–15 秒 | 40 次（约 10 分钟） | 面向 LLM 客户端的长期稳定面 |
| `blog.sh`（shell 实现） | 5 秒 | 总超时 600 秒 | 面向人类/CI 的实现层 |

自研 LLM 客户端以 SKILL.md 的 10–15s×40 轮为准；在 CI 中用 `blog.sh` 时按 600 秒常量显式放宽步骤超时（详见 [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)）。

## 完整 shell 工作流参考

忠实于 `examples/blog-generation.md` 的命令序列（F-sc-056）：

```bash
# 1. 提交任务并提取 task_id
TASK_ID=$(./scripts/blog_submit.sh -i 2303.14535 | jq -r '.task_id')
echo "Task ID: $TASK_ID"

# 2. 轮询至完成
while true; do
  STATUS=$(./scripts/blog_status.sh -i "$TASK_ID" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  sleep 10
done

# 3. 取结果并保存
if [ "$STATUS" = "completed" ]; then
  ./scripts/blog_result.sh -i "$TASK_ID" -o blog.md
  echo "Blog saved to blog.md"
fi
```

博客生成通常耗时 2–5 分钟，取决于论文长度、图表数量与服务端负载；超时与重试遵循 SKILL.md 契约（503/504 按 2s/4s/8s 退避最多 3 次，400/404 不重试，F-sc-048）。

## 相关概念

- [/concepts/01-server-client.md](/concepts/01-server-client.md)
- [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)
- [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)
- [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)
