---
type: Concept
title: "会议全生命周期管理"
description: "用 meeting 域完成预约（普通/周期会议）、查询（进行中/已结束/搜索）、修改、取消与受邀成员管理：参数规则、周期规则、冲突字段与 bool 语法。"
tags: [tencent-meeting, tmeet, meeting, recurring-meeting, invitees, lifecycle, booking]
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

# 会议全生命周期管理

## 预约会议：meeting create

必填三项（F-041）：

```bash
tmeet meeting create \
  --subject "Q4 产品评审" \
  --start "2026-10-15T14:00+08:00" \
  --end   "2026-10-15T15:30+08:00"
```

### 常用可选参数

| 参数 | 取值 | 说明 |
|------|------|------|
| `--password` | 4~6 位数字 | 入会密码 |
| `--timezone` | Oracle-TimeZone，如 `Asia/Shanghai` | 时区 |
| `--meeting-type` | `0` 普通（默认）/ `1` 周期性 | 会议类型 |
| `--join-type` | `1` 所有人 / `2` 仅受邀 / `3` 仅企业内部 | 加入权限（默认 0） |
| `--waiting-room` | bool（默认 false） | 是否开启等候室 |
| `--invitees` | openid 列表（逗号分隔或重复传参，≤100） | 受邀成员（F-043） |

### 高级参数与企业强制态

| 参数 | 默认 | 说明 |
|------|------|------|
| `--water-mark-type` | 个人账号 `2`（关闭） | 文字水印：`0` 单排 / `1` 双排 / `2` 关闭 |
| `--audio-watermark` | false | 音频水印 |
| `--auto-record-type` | `none` | `none` / `local` / `cloud` |
| `--auto-asr` | false | 是否自动开启 ASR |

注意：企业账号场景下，若企业管理后台强制开启水印/录制等策略，**入参不生效，以企业强制态为准**（F-044）。bool 显式 false 必须等号写法 `--audio-watermark=false`（F-045）。

## 周期会议

`--meeting-type 1` 时使用周期规则（F-042）：

| 参数 | 取值 |
|------|------|
| `--recurring-type` | `0` 每天 / `1` 周一至周五 / `2` 每周 / `3` 每两周 / `4` 每月 |
| `--until-type` | `0` 按日期结束 / `1` 按次数结束 |
| `--until-count` | 次数，默认 7；每天/工作日/每周最大 **500**，每两周/每月最大 **50** |
| `--until-date` | until-type=0 时的结束日期 |

示例（每周一次、共 10 次）：

```bash
tmeet meeting create --subject "周例会" \
  --start "2026-10-12T10:00+08:00" --end "2026-10-12T11:00+08:00" \
  --meeting-type 1 --recurring-type 2 --until-type 1 --until-count 10
```

## 查询会议

| 命令 | 用途 | 分页 |
|------|------|------|
| `meeting get` | 单个会议详情；`--meeting-id` 与 `--meeting-code` 二选一（id 优先，F-046） | — |
| `meeting list` | 进行中/即将开始的会议；`--start`/`--end` 作分页查询时间值；`--show-all-sub 1` 展示周期会全部子会议 | 20/20（F-050） |
| `meeting list-ended` | 按时间范围查已结束会议 | 30/30（F-051） |
| `meeting search` | 关键词/会议号/时间窗组合搜索 | 30/30（F-052） |

`meeting search` 的过滤维度（F-052）：

- `--query`：关键词；
- `--query-field`：`subject` / `creator` / `note` / `all`（默认 all）；
- `--meeting-code`：仅数字、无短横线的精确匹配；
- `--start` + `--end`：时间窗。

> 会后取纪要的检索路径建议：已知具体会议用 `meeting get`；按时间范围找会用 `meeting list-ended`；**按关键词找会（并可能需要纪要内容）应直接用 `minutes search` / `record search`**，不要先 list-ended 再逐场取纪要（N+1），详见 [04 - 双纪要体系](04-record-minutes.md)。

## 修改会议：meeting update

- 增量语义：只传需要修改的字段，未传字段保持不变（F-047）；
- 周期会议改单场：加 `--sub-meeting-id`，仅调整该子会议时间，**不可与** `--recurring-type`/`--until-type`/`--until-count`/`--until-date` 同用（F-047）；
- 变更邀请列表：`--invitees` 必须搭配 `--invitees-type`，取值 `replace` / `add` / `remove`（F-048）。

```bash
# 给某场会议加两个人
tmeet meeting update --meeting-id "xxx" \
  --invitees "openid1,openid2" --invitees-type add
```

`meeting update`、`meeting cancel`、三个 invitees-* 命令都在 **9 个必须二次确认**的清单内：Agent 必须先展示操作详情（用会议号标识）并结束本轮、等用户下一条真实确认后才执行（F-072、F-073），详见 [06 - Agent 安全契约](06-agent-safety-contract.md)。

## 取消会议：meeting cancel

| 场景 | 用法 |
|------|------|
| 普通会议 | `meeting cancel --meeting-id <id>` |
| 周期会议的某一子会议 | 加 `--sub-meeting-id <id>` |
| 整场周期会议 | `--meeting-id <id> --meeting-type 1` |

（F-049）

## 受邀成员独立管理

除 update 内嵌方式外，另有 4 个独立子命令（F-053）：

| 命令 | 作用 |
|------|------|
| `meeting invitees-list` | 查受邀成员（page-size 30/30） |
| `meeting invitees-add` | 追加受邀人 |
| `meeting invitees-remove` | 移除受邀人 |
| `meeting invitees-replace` | 全量替换受邀人 |

后三者的 `--invitees` 必填，最多 100 个 openid（F-053）。openid 的获取入口是 `contact search` / `lookup-by-*`，但通讯录命令有严格场景白名单——只能用于「邀请入会」或「会中呼叫」的前置解析，禁止单独查人（F-066），见 [06 - Agent 安全契约](06-agent-safety-contract.md)。

## 典型生命周期串联

```
create（预约，可带 invitees）
   │
   ├─ list / list-ended / search（找会）
   ├─ get（详情，含 permission_status 等）
   ├─ update（改时间/加人，需确认）
   ├─ control（会中呼叫/等候室/踢人）── report participants（取会中成员）
   ├─ report（参会明细/导出）
   ├─ record / minutes（会后录制与纪要）
   └─ cancel（取消，需确认）
```

## 延伸阅读

- [02 - 命令体系与全局约定](02-command-map.md)
- [04 - 录制、转写与双纪要体系](04-record-minutes.md)
- [05 - 参会报告与会中控制](05-report-control.md)
- [06 - Agent 安全契约](06-agent-safety-contract.md)
- 示例：[03 - 周期会议与参会明细导出](../examples/03-recurring-export.md)
