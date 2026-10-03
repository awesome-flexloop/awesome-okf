---
type: Example
title: "会后取纪要工作流：双链路路由与权限申请"
description: "按官方 Skill 路由，用 meeting get 的 permission_status 在录制纪要与元宝纪要间分流，录制侧失败降级元宝，跨会议双搜去重，并走通录制权限两阶段申请。"
tags: [tencent-meeting, tmeet, example, minutes, smart-minutes, transcript, permission, workflow]
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

# 会后取纪要工作流

> 场景：会议结束，用户对 AI 说「把昨天产品评审的纪要给我，顺便查下张三说的那个预算数字」。本示例演示为什么要按权限分流、具体怎么走、没权限怎么办。

## 背景：两类纪要别搞混

| | 元宝纪要 minutes | 录制纪要 record smart-minutes |
|---|---|---|
| 基础 | 会中 ASR，AI 加工 | 云录制文件 |
| 权限 | 参会者人人可直接取 | 录制所有者持有，需申请 |
| 原话 | 无 | 有（transcript-*） |

（F-062）

## 路线 A：已知会议，按权限分流

### 第 1 步：meeting get 拿权限状态

```bash
tmeet meeting get --meeting-code "412-345-678"
```

在响应 `data` 中找到 `permission_status`（F-063）。对用户只说会议号 `412-345-678`，不回显 meeting_id（F-074）。

### 第 2 步：按状态路由

```bash
# 情况 1：can_view —— 有录制权限，走录制纪要（信息最全，含逐字稿）
tmeet record list --meeting-code "412-345-678"
# 从 list 结果拿到 record_file_id 后：
tmeet record smart-minutes --record-file-id "<rfid>" --lang zh

# 情况 2：can_apply / closed / 无录制 —— 直接走元宝纪要
tmeet minutes get --meeting-id "<meeting_id>"
```

### 第 3 步：失败降级

录制侧命令报错或返回空时，**不要直接回答「没有纪要」**，降级到元宝纪要并向用户说明（F-063）：

```
录制纪要暂时取不到（<原因>），已为你改用元宝智能纪要。
```

### 第 4 步：要「原话/具体数字」→ 查逐字稿

元宝纪要是 AI 概括，具体数字与某成员原话可能被概括掉；用录制逐字稿精确检索（F-058、F-064）：

```bash
tmeet record transcript-search --record-file-id "<rfid>" --text "预算"
tmeet record transcript-get --record-file-id "<rfid>" --pid 0 --limit 50
```

## 路线 B：没有权限，两阶段申请录制

当 `permission_status = can_apply`（F-059）：

```bash
# 阶段 1：预览申请（不落任何提交）
tmeet record permission-apply-prepare --record-file-id "<rfid>"
```

返回审批文案、会议主题、录制所有者、申请人与 **`expires_in`（预览有效秒数）**。Agent 应把这些信息展示给用户（会议用会议号标识），等用户明确说「申请」：

```bash
# 阶段 2：用户确认后才提交（该命令在二次确认清单内，F-072）
tmeet record permission-apply-commit --record-file-id "<rfid>"
```

返回 `unique_id` / `status` / `approval_url`。审批通过后回到路线 A 的情况 1。

## 路线 C：跨会议关键词检索（「最近哪些会提过预算」）

两条链路**都要跑**，按会议去重并标注来源（F-064）：

```bash
# 链路 1：元宝纪要（AI 内容）
tmeet minutes search --query "Q4 预算" \
  --start "2026-09-01T00:00+08:00" --end "2026-10-01T00:00+08:00"

# 链路 2：录制原始转写（原话）
tmeet record search --query "Q4 预算" --query-field transcript_content \
  --start "2026-09-01T00:00+08:00" --end "2026-10-01T00:00+08:00"
```

合并呈现格式建议：

```
找到 3 场相关会议：
1. 9/28 Q4 产品评审（来源：元宝纪要 + 录制转写）—— 提及 3 次
2. 9/25 财务对齐会（来源：录制转写）—— 张三原话：「…预算 120 万…」
3. 9/20 周会（来源：元宝纪要）
```

注意按时间找纪要直接用 `minutes search --start/--end`，不要 `meeting list-ended` 后逐场 `minutes get`（避免 N+1）。

## Agent 执行检查单

- [ ] 面向用户只用会议号，不输出 meeting_id/open_id（F-074）
- [ ] 先 `meeting get` 看 `permission_status` 再选链路
- [ ] 录制取不到时降级元宝并说明
- [ ] 「原话」诉求走 transcript，不拿 AI 纪要硬答
- [ ] 跨会议检索双链路并标注来源
- [ ] permission-apply-commit 前跨轮确认，且注意 prepare 的 expires_in
- [ ] 查询默认带 `--compact`，翻页先征询（F-077、F-078）

## 相关概念

- [04 - 录制、转写与双纪要体系](../concepts/04-record-minutes.md)
- [06 - Agent 安全契约](../concepts/06-agent-safety-contract.md)
