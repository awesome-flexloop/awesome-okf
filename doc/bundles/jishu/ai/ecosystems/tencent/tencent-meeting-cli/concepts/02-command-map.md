---
type: Concept
title: "命令体系与全局约定"
description: "tmeet 10 个命令域地图、JSON 信封结构、--format/--compact 全局标志、ISO 8601 时间、游标分页、布尔参数等号语法等 Agent 调用必须遵守的全局契约。"
tags: [tencent-meeting, tmeet, commands, json, pagination, iso8601, compact, cli-contract]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: github-readme
    resource: /references/github-readme.md
    title: tencentmeeting-cli GitHub README
  - id: command-reference
    resource: /references/command-reference.md
    title: 官方完整命令参考 docs/command.md
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单
---

# 命令体系与全局约定

## 命令地图（v1.0.18，44 个子命令）

```
tmeet
├── auth        login | logout | status
├── meeting     create | update | cancel | get | list | list-ended | search
│               | invitees-list | invitees-add | invitees-remove | invitees-replace
├── contact     search | lookup-by-email | lookup-by-phone
├── record      list | address | search | smart-minutes
│               | transcript-get | transcript-paragraphs | transcript-search
│               | permission-apply-prepare | permission-apply-commit
├── report      participants | waiting-room-log | participants-export | job-result
├── control     call | kick | waiting-room
├── minutes     search | get
├── tshoot      log | feedback
├── app         get | set                 (v1.0.17+)
└── event       list | schema | consume | status | stop   (v1.0.18+)
```

依据 README 命令树与 command.md 逐命令清点（F-033）。腾讯云文档的「19 命令」旧清单见 F-034。

## 三个全局标志

| 标志 | 取值/默认 | 说明 |
|------|-----------|------|
| `--format` | `json`（默认紧凑）/ `json-pretty` | 输出格式（F-035） |
| `--compact` | bool，默认 false | 精简输出：仅保留各命令的关键字段，降低 Agent 上下文 token（F-035、F-077） |
| `--version` / `-V` | — | 查看版本号 |

SKILL.md 要求**查询类命令默认追加 `--compact`**。其精简字段白名单由服务端按命令下发，某命令未声明白名单或拉取失败时透明放行（返回全量字段），不会因此报错（F-077）。event 族例外：不经过 compact 中间件，`--compact` 对其无效（F-037）。

## JSON 响应信封

除 event 族外，所有响应统一结构（F-036）：

```json
{
  "trace_id": "…",
  "message": "…",
  "data": { }
}
```

- `data` 为业务载荷；分页命令的 `data` 中带游标字段（见下）。
- event 族输出 **bare JSON**（NDJSON 事件流），不带信封（F-037）。

人类阅读时加 `--format json-pretty`；Agent/管道消费保持默认紧凑 JSON。

## 时间：强制 ISO 8601 带时区

所有时间入参必须是 ISO 8601 且**带时区偏移**，例如：

```bash
--start "2026-04-10T14:00+08:00"
--end   "2026-04-10T15:00+08:00"
```

不支持仅日期（`2026-04-10`）写法，否则报 `--start format error`（F-038、F-040）。响应中的时间戳也自动转为 ISO 8601 展示。

## 分页：游标方案（v1.0.5 起统一）

支持分页的命令统一使用（F-039）：

| 参数 | 含义 |
|------|------|
| `--page-size` | 每页条数 |
| `--page-token` | 上一页响应中返回的游标；首页不传 |

旧参数 `--page`、`--pos`、`--size` 已标记 deprecated（仍可使用，应尽快迁移）。

各命令 page-size 默认/上限（来自 command.md，F-050、F-051、F-054、F-060、F-067）：

| 命令 | 默认 page-size | 上限 |
|------|---------------:|-----:|
| `meeting list` | 20 | 20 |
| `meeting list-ended` / `search` / `invitees-list` | 30 | 30 |
| `record list` / `address` / `search` | 30 | 30 |
| `report participants` / `waiting-room-log` | 100 | 100 |
| `minutes search` | 20 | 50 |
| `minutes get`（短总结分页） | 10 | 30 |

例外：`record transcript-*` 三个命令不使用通用分页，采用独立的 `--pid`（起始段落 ID）+ `--limit`（段落数）定位，未弃用（F-058）。

**翻页纪律（SKILL.md，F-078）**：

- 不得自行拼接或递增 page-token，只能原样回传响应中的游标；
- 非穷尽式诉求（「最近的会议」），取完首页后先询问用户是否继续；
- 连续翻页超过 5 页或累计超过 200 条，必须主动征询。

## 布尔参数：显式 false 必须用等号

bool 型开关（如 `--waiting-room`、`--audio-watermark`）显式传 **false 时必须写等号形式**（F-045）：

```bash
# 正确
tmeet meeting create --subject "评审" --start "…" --end "…" --audio-watermark=false

# 错误（空格形式无法表达 false）
tmeet meeting create … --audio-watermark false
```

不写该标志时使用服务端默认值。

## 会议标识：meeting_id 与 meeting_code

- `meeting_id`：API/CLI 内部标识，作为命令参数传递；
- `meeting_code`：人类使用的会议号，面向用户展示。

多数查询命令支持二选一（meeting-id 优先级更高，F-046）。SKILL.md 明令**禁止向用户回显 meeting_id**，所有展示统一用 meeting_code（F-074）。

## 常见报错速查

| 报错 | 含义与处置 | 信源 |
|------|-----------|------|
| `user config is empty` | 未登录，先 `tmeet auth login` | F-040 |
| `--start format error` | 时间格式不合法，补全 ISO 8601 时区 | F-040 |
| `--meeting-id is required` | 缺少必填标识参数 | F-040 |
| `user has been initialized` | 已登录，勿重复 login；换账号先 logout | F-040 |
| 500284（该功能暂不可使用） | 套餐/灰度不可用，**严禁重试**，如实告知 | F-095 |
| 500294 | 套餐不足，响应中的升级链接须原样渲染为 Markdown 链接 | F-095 |

## 调用风格建议（Agent 视角）

1. 查询默认 `--compact`，写操作或需要原始字段时取全量；
2. 脚本中用 `--format json`（默认），解析 `data` 字段；
3. 时间一律由 Agent 换算为带时区 ISO 8601；
4. 分页先问再翻，游标原样透传；
5. 输出给用户前剥离 meeting_id、open_id 等内部标识（见 [06 - Agent 安全契约](06-agent-safety-contract.md)）。

## 延伸阅读

- [03 - 会议全生命周期管理](03-meeting-lifecycle.md)
- [04 - 录制、转写与双纪要体系](04-record-minutes.md)
- 示例：[01 - 十分钟上手](../examples/01-quickstart.md)
