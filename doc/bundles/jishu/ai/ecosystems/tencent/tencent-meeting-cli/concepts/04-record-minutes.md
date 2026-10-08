---
type: Concept
title: "录制、转写与双纪要体系"
description: "record 域（录制文件/下载/内容搜索/转写/权限两阶段申请）与 minutes 元宝纪要域的完整地图，以及一套按 permission_status 分流、失败降级、双向兜底的纪要检索路由。"
tags: [tencent-meeting, tmeet, recording, transcript, minutes, smart-minutes, permission]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: command-reference
    resource: /references/command-reference.md
    title: 官方完整命令参考 docs/command.md
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单
---

# 录制、转写与双纪要体系

## 核心概念：一场会议，两类纪要

tmeet 里「纪要」不是单一产物，而是两套权限模型独立的东西（F-062）：

| 维度 | 元宝纪要（minutes） | 录制纪要（record smart-minutes） |
|------|--------------------|---------------------------------|
| 数据基础 | 会中实时 ASR | 录制文件（云录制） |
| 取数权限 | 参会者人人可取，无需单独授权 | 录制创建者所有，其他人需申请权限 |
| 逐字稿 | 无 | 有（transcript-* 命令族） |
| 获取命令 | `minutes get` / `minutes search` | `record smart-minutes` + `record transcript-*` |
| 内容特征 | AI 加工（概览/要点/待办/滚动短总结） | 智能纪要 + 可检索的原始转写 |

这一分流设计是 tmeet 最容易被误解、也最体现 Agent 工程化的地方（见[洞察二](../spec/insights.md)）。

## record 域：录制文件与转写（9 个命令）

### 查录制列表：record list

过滤参数**三选一**，均不传会报错（F-054）：

```bash
# 按时间范围
tmeet record list --start "2026-10-01T00:00+08:00" --end "2026-10-08T00:00+08:00" --compact
# 按会议
tmeet record list --meeting-id "xxx"
tmeet record list --meeting-code "123456789"
```

page-size 默认/上限均为 30（游标分页）。

### 取下载地址：record address

```bash
tmeet record address --meeting-record-id "xxx"
```

返回录制文件下载地址与 `record_file_id`（F-055），后续取纪要/转写都依赖该 ID。

### 全文检索：record search

`--query-field` 可搜的内容维度（F-056）：

- `subject` 会议主题、`creator` 创建者；
- `transcript_content` **原始转写内容**；
- `smart_minutes` 智能纪要内容；
- `timeline` 时间轴；
- `all`（默认）。

文件类型过滤 `--file-type`：`video` / `audio` / `transcript` / `upload` / `external` / `all`。

### 智能纪要与逐字稿

```bash
# 智能纪要（--lang：default 原文 / zh / en / ja；--pwd：录制文件密码）
tmeet record smart-minutes --record-file-id "xxx" --lang zh

# 逐字稿：段落定位用 --pid + --limit（非通用分页）
tmeet record transcript-get        --record-file-id "xxx" --pid 0 --limit 50
tmeet record transcript-paragraphs --record-file-id "xxx"
tmeet record transcript-search     --record-file-id "xxx" --text "预算"
```

（F-057、F-058）

### 权限申请：prepare → 人确认 → commit 两阶段

当用户不是录制所有者时，不能直接取录制内容，需走两阶段申请（F-059）：

```bash
# 1) 预览：审批文案、会议主题、录制所有者、申请人，响应含 expires_in（过期秒数）
tmeet record permission-apply-prepare --record-file-id "xxx"

# 2) 用户确认后再提交，返回 unique_id/status/approval_url 等
tmeet record permission-apply-commit  --record-file-id "xxx"
```

`permission-apply-commit` 在 9 个必须二次确认的命令清单内（F-072）。prepare 响应带 `expires_in`，意味着预览后不能无限期搁置，确认动作要在有效期内完成。

## minutes 域：元宝纪要（2 个命令）

```bash
# 跨会议搜索：关键词 ≤ 50 字，可带时间范围；page-size 默认 20 / 上限 50
tmeet minutes search --query "Q4 预算" --start "…" --end "…"

# 单场取纪要：--minute-id 与 --meeting-id 二选一；周期会议加 --sub-meeting-id
tmeet minutes get --meeting-id "xxx"
```

`minutes get` 的内容开关（F-061）：

| 开关 | 默认 | 内容 |
|------|------|------|
| `--overview` | true | 会议概览 |
| `--summary-points` | true | 要点 |
| `--todos` | true | 待办事项 |
| `--short-summary` | false | 滚动短总结历史序列（page-size 默认 10/上限 30） |

## 官方 Skill 的纪要检索路由（建议照搬）

### 已知某场会议，要纪要

```
meeting get（顺带取 permission_status）
        │
        ├─ can_view ────────► record smart-minutes（+需要原话时 transcript-*）
        ├─ can_apply ─┐
        ├─ closed ─────┤
        └─ 无录制 ─────┴──► minutes get（元宝纪要）

record 侧取不到 / 报错 ──降级──► minutes get，并向用户说明降级原因
```

（F-063）要点：先看权限再选链路，而不是凭命令名瞎试；录制链路失败时降级元宝纪要并告知，而不是直接回答「没有纪要」。

### 跨会议找内容（「最近哪些会提到了预算」）

**两条链路都执行**（F-064）：

```bash
tmeet minutes search --query "预算"                              # 元宝纪要
tmeet record search --query-field transcript_content --query "预算"  # 录制逐字稿
```

然后：按会议去重 → 每条结果标注来源（元宝/录制）→ 一并呈现。

为什么必须双搜：元宝纪要是 AI 加工，可能概括掉具体数字与某人原话；逐字稿保留原始发言，但只有有权限的录制才搜得到。单链路必然漏。

### 按时间找「上周的会和纪要」

用 `minutes search --start/--end` 直接按时间检索，不要 `meeting list-ended` 后对每场循环 `minutes get`（N+1 次调用，慢且浪费 token）。

## 选择速查

| 用户诉求 | 首选命令 |
|----------|----------|
| 「这场会的纪要」 | `meeting get` 看权限 → `record smart-minutes` 或 `minutes get` |
| 「谁在会上说了 X / 原话」 | `record transcript-search --text` |
| 「把录制文件给我」 | `record list` → `record address` |
| 「最近提到 X 的会议」 | `minutes search` + `record search` 双跑 |
| 「我没有这个录制的权限」 | `permission-apply-prepare` → 确认 → `commit` |
| 「待办事项」 | `minutes get --todos`（默认即带） |

## 延伸阅读

- [03 - 会议全生命周期管理](03-meeting-lifecycle.md)
- [06 - Agent 安全契约](06-agent-safety-contract.md)
- 示例：[02 - 会后取纪要工作流](../examples/02-minutes-workflow.md)
