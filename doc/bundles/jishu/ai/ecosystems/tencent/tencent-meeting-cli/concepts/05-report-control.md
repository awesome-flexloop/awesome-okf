---
type: Concept
title: "参会报告、会中控制与通讯录边界"
description: "report 域参会人/等候室查询与异步导出轮询、control 域呼叫/踢人/等候室操作的参数规则，以及 contact 通讯录命令「仅限邀请/呼叫前置解析」的场景白名单。"
tags: [tencent-meeting, tmeet, report, participants, export, control, contact, waiting-room]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: command-reference
    resource: /references/command-reference.md
    title: 官方完整命令参考 docs/command.md
  - id: cloud-doc
    resource: /references/cloud-doc.md
    title: 腾讯云文档《腾讯会议 CLI 说明》
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单
---

# 参会报告、会中控制与通讯录边界

## report 域：谁参加了会（4 个命令）

### 实时参会人 / 历史参会明细

```bash
tmeet report participants --meeting-id "xxx" --compact
```

返回参会人列表，含入会时间、离会时间等（F-067）。`--page-size` 默认/上限均为 **100**，配合 `--page-token` 翻页。

```bash
tmeet report waiting-room-log --meeting-id "xxx"   # 等候室成员记录，page-size 100/100
```

`report participants` 不只是报表工具——它是会中控制（尤其踢人）唯一合法的成员来源，见下文。

### 异步导出：participants-export + job-result 轮询

参会明细数据量大时走异步任务（F-068）：

```bash
# 1) 发起导出，立即返回 job_id（格式 xlsx 默认，也可 json）
tmeet report participants-export --meeting-id "xxx"

# 2) 每 5 秒轮询一次
tmeet report job-result --job-id "<job_id>"
```

job-result 的 status 三态：

| status | 处置 |
|--------|------|
| 处理中 | 等待约 5 秒后再次轮询 |
| 成功 | 取下载链接（**有效期 2 小时**，及时下载） |
| 失败 | 读取 `error_msg`，停止轮询并告知用户 |

这是 tmeet 中唯一的异步任务模式（发起→轮询→取产物），适合 Agent 用 `--timeout` 或定时器封装。

## control 域：会中操作（3 个命令）

三个命令都是会中实时操作，且全部在**二次确认清单**内（F-072）。

### 呼叫成员入会

```bash
tmeet control call --meeting-id "xxx" --users "openid1,openid2"
```

`--users` 最多 20 个 openid（F-069）。openid 由 `contact search` 解析而来——「呼叫入会」正是通讯录白名单允许的两个下游场景之一。

### 踢人

```bash
tmeet control kick --meeting-id "xxx" --users "openid1" --allow-rejoin=false
```

- 三类成员参数 `--users` / `--sip-users` / `--pstn-users`，合计最多 20 个；
- `--allow-rejoin` 默认 true（踢出后可重新入会）；
- **成员来源硬约束**：必须取自 `report participants` 返回的当前会中参会人，**严禁使用 `contact search` 的结果**（F-071）。

这条约束的工程理由：通讯录里的同名/近似成员不一定在会中，拿通讯录结果踢人极易误伤；report participants 是「此刻在会议里的人」的唯一权威视图。

### 等候室操作

```bash
tmeet control waiting-room --meeting-id "xxx" \
  --operate-type enter-meeting --users "openid1"
```

| `--operate-type` | 含义 |
|------------------|------|
| `enter-meeting` | 从等候室移入会议（放行） |
| `back-to-waiting` | 从会中移回等候室 |
| `expel` | 移出（拒绝） |

成员参数 `--users` / `--sip-users` / `--pstn-users` **三选一至少给一种**，合计最多 20 个；`expel` 时可用 `--allow-rejoin` 控制是否允许重新加入（F-070）。

## contact 域：通讯录只做前置解析（3 个命令）

```bash
# 按姓名搜索（可加职位/部门过滤）
tmeet contact search --username "张三" --department-name "研发部"

# 邮箱批量反查（≤50）
tmeet contact lookup-by-email --emails "a@x.com,b@x.com"

# 手机号批量反查（≤50）
tmeet contact lookup-by-phone --phones "13800000000"
```

### 场景白名单（SKILL.md 硬约束，F-066）

通讯录命令**只允许**服务于以下两类下游会议动作：

1. **会议邀请**：解析出 openid 后立即用于 `meeting invitees-add` / `invitees-replace` / `create --invitees`；
2. **会中呼叫**：解析后用于 `control call`。

以下请求应直接拒绝：「查一下张三的电话」「张三在哪个部门」「这个人是不是我们公司的」「列出研发部所有人」。无下游会议动作的查人请求一律不执行。

多候选时必须让用户选定，禁止按匹配度自行代选（F-076）；回显成员用 `姓名（部门/职位/open_id 取其一）` 格式（F-075），详见 [06 - Agent 安全契约](06-agent-safety-contract.md)。

## 典型串联：会中点名与处置

```
report participants          ← 取得当前会中成员（含 openid）
        │
        ├─ 用户确认目标成员（多候选必须用户选）
        ▼
control waiting-room / kick  ← 二次确认（展示会议号+成员姓名）后执行
```

## 典型串联：会后导出签到表

```
report participants-export  →  job_id
        │
        └─ 每 5s report job-result ──成功──► 下载链接（2 小时内下载）
                                  └─失败──► error_msg 告知用户
```

## 延伸阅读

- [03 - 会议全生命周期管理](03-meeting-lifecycle.md)
- [06 - Agent 安全契约](06-agent-safety-contract.md)
- 示例：[03 - 周期会议与参会明细导出](../examples/03-recurring-export.md)
