---
type: Example
title: "周期会议排期与参会明细异步导出"
description: "创建每周周期会议、查询子会议、管理受邀人，会后用 participants-export 发起异步导出并按 job-result 三态轮询下载签到表。"
tags: [tencent-meeting, tmeet, example, recurring-meeting, invitees, export, job-result]
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

# 周期会议排期与参会明细异步导出

> 场景：团队要安排「每周一 10:00–11:00、共 8 期」的迭代回顾会，邀请 6 名成员；每期结束后导出参会明细做考勤。

## 1. 创建周期会议

```bash
tmeet meeting create --subject "迭代回顾会" \
  --start "2026-10-12T10:00+08:00" \
  --end   "2026-10-12T11:00+08:00" \
  --meeting-type 1 \
  --recurring-type 2 \
  --until-type 1 --until-count 8 \
  --join-type 2 \
  --waiting-room
```

参数对应（F-042）：

- `--meeting-type 1`：周期性会议；
- `--recurring-type 2`：每周（0 每天 / 1 工作日 / 2 每周 / 3 每两周 / 4 每月）；
- `--until-type 1 --until-count 8`：按次数结束，共 8 期；
- 次数上限：每天/工作日/每周 ≤ 500，每两周/每月 ≤ 50；
- `--join-type 2`：仅受邀人可加入。

## 2. 邀请成员：先解析 openid，再加会

通讯录只能作为邀请/呼叫的前置步骤使用（F-066）：

```bash
# 2.1 解析成员（多候选时必须让用户选定，F-076）
tmeet contact search --username "张三" --department-name "研发部" --compact
tmeet contact lookup-by-email --emails "li4@x.com,wang5@x.com"

# 2.2 加入会议（≤100 人）
tmeet meeting invitees-add --meeting-id "<id>" \
  --invitees "openid_a,openid_b,openid_c"
```

`invitees-add/remove/replace` 都是二次确认命令：Agent 先用会议号 + 成员姓名列表展示，等用户确认后执行（F-072、F-073、F-075）。

## 3. 查看各期子会议

```bash
# 展示周期会全部子会议
tmeet meeting list --show-all-sub 1 --compact

# 单场详情（会议号精确查）
tmeet meeting get --meeting-code "412-345-678"
```

## 4. 只改某一期时间

```bash
tmeet meeting update --meeting-id "<周期会 id>" \
  --sub-meeting-id "<第3期 id>" \
  --start "2026-10-26T14:00+08:00" --end "2026-10-26T15:00+08:00"
```

`--sub-meeting-id` 不能与 `--recurring-type`/`--until-*` 同用（F-047）。

## 5. 取消某一期 / 取消整个系列

```bash
# 仅取消第 3 期
tmeet meeting cancel --meeting-id "<id>" --sub-meeting-id "<第3期 id>"

# 取消整个周期系列
tmeet meeting cancel --meeting-id "<id>" --meeting-type 1
```

（F-049，均需二次确认）

## 6. 会后导出参会明细（异步任务轮询）

### 6.1 先看实时明细（可选）

```bash
tmeet report participants --meeting-id "<某期 id>" --compact
# page-size 默认/上限 100，人多时用 --page-token 翻页（F-067）
```

### 6.2 发起异步导出

```bash
tmeet report participants-export --meeting-id "<某期 id>"
# 返回 data.job_id
```

### 6.3 每 5 秒轮询

```bash
tmeet report job-result --job-id "<job_id>"
```

| status | 处理 |
|--------|------|
| 处理中 | 等 5 秒再查 |
| 成功 | 取下载 URL，**2 小时内**下载（F-068） |
| 失败 | 读 error_msg，停止轮询并告知用户 |

Shell 轮询骨架（人类/脚本使用）：

```bash
while true; do
  out=$(tmeet report job-result --job-id "<job_id>")
  status=$(echo "$out" | jq -r '.data.status')
  case "$status" in
    成功) echo "$out" | jq -r '.data.url'; break ;;
    失败) echo "$out" | jq -r '.data.error_msg'; exit 1 ;;
    *) sleep 5 ;;
  esac
done
```

> 注：状态中文字面量以实际返回为准（文档登记为「成功」「失败」「处理中」，F-068）；写脚本时建议对中英文枚举做兼容。

## 7. 等候室记录（会后核对准入）

```bash
tmeet report waiting-room-log --meeting-id "<某期 id>" --compact
```

返回被放入/拒入等候室的成员记录，page-size 100/100（F-067）。

## 常见坑位

| 现象 | 原因/处置 |
|------|-----------|
| 周期次数报错 | 每周最大 500、每两周/每月最大 50（F-042） |
| update 改单场失败 | `--sub-meeting-id` 与 recurring/until 参数互斥（F-047） |
| 导出链接打开 404 | 下载链接 2 小时过期，重新发起导出（F-068） |
| Agent 没确认就改会 | 确认 Skill 已安装并重启过 AI 工具（F-019） |

## 相关概念

- [03 - 会议全生命周期管理](../concepts/03-meeting-lifecycle.md)
- [05 - 参会报告与会中控制](../concepts/05-report-control.md)
