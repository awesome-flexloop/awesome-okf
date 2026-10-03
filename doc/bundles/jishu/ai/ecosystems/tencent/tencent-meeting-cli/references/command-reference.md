---
type: Reference
title: "官方完整命令参考 docs/command.md 信源"
description: "仓库 main 分支 docs/command.md（1594 行，对应 v1.0.18）的事实登记：auth/meeting/contact/record/report/control/minutes/tshoot/app/event 全部 44 子命令的参数、分页与输出约定。"
tags: [tencent-meeting, tmeet, reference, command-reference, parameters, api]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: command-reference
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/docs/command.md
    title: 官方完整命令参考 docs/command.md
---

# 官方完整命令参考 docs/command.md 信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | command-reference |
| URL | https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/docs/command.md |
| 类型 | 仓库内官方命令参考（完整抓取 1594 行） |
| 版本对应 | v1.0.18（main 分支，抓取于 2026-10-03） |
| 对应事实 | F-026、F-027、F-033（命令清点）、F-041 ~ F-061、F-065、F-067 ~ F-071、F-080 ~ F-091 |

## 覆盖的命令域（44 子命令）

| 域 | 子命令 | 事实段 |
|----|--------|--------|
| auth（3） | login / logout / status | F-026、F-027 |
| meeting（11） | create、update、cancel、get、list、list-ended、search、invitees-list/add/remove/replace | F-041 ~ F-053 |
| contact（3） | search、lookup-by-email、lookup-by-phone | F-065 |
| record（9） | list、address、search、smart-minutes、transcript-get/paragraphs/search、permission-apply-prepare/commit | F-054 ~ F-059 |
| report（4） | participants、waiting-room-log、participants-export、job-result | F-067、F-068 |
| control（3） | call、kick、waiting-room | F-069 ~ F-071 |
| minutes（2） | search、get | F-060、F-061 |
| tshoot（2） | log、feedback | F-090、F-091 |
| app（2，v1.0.17+） | get、set | F-087 ~ F-089 |
| event（5，v1.0.18+） | list、schema、consume、status、stop | F-080 ~ F-086 |

## 关键参数约定（摘自命令参考）

- meeting create 必填 subject/start/end；password 4~6 位数字；周期会 recurring-type/until-* 规则；invitees ≤ 100；bool 显式 false 用等号（F-041~F-045）；
- meeting get 的 meeting-id/meeting-code 二选一且 id 优先（F-046）；
- record list 过滤三选一（时间范围 / meeting-id / meeting-code）（F-054）；
- transcript-* 用 `--pid`+`--limit` 独立定位，非通用分页（F-058）；
- minutes search/get 的标识互斥与内容开关默认值（F-060、F-061）；
- report participants/waiting-room-log page-size 100/100；异步导出 job 轮询三态、链接 2 小时有效（F-067、F-068）；
- control 成员参数合计 ≤20；waiting-room 三种 operate-type；kick 的 allow-rejoin 默认 true（F-069~F-071）；
- event consume 的 max-events/timeout/param/jq/output-dir/quiet 选项、ready/exit 标记、退出码 0/1/2（F-080、F-081）；
- app set 三参数的长度与枚举约束、客户端 3.45.10 的 http/https 分界（F-087、F-088）；
- tshoot log 的 start/end 同传同不传、feedback 的字段长度限制（F-090、F-091）。

## 分页参数（命令级值表）

| 命令 | 默认 page-size | 上限 |
|------|---------------:|-----:|
| meeting list | 20 | 20 |
| meeting list-ended / search / invitees-list | 30 | 30 |
| record list / address / search | 30 | 30 |
| report participants / waiting-room-log | 100 | 100 |
| minutes search | 20 | 50 |
| minutes get | 10 | 30 |

## 引用方式

本束概念篇 03/04/05/07/08 的全部参数级陈述均回引本信源；命令输出的字段级细节（各命令 data 结构）应以在线原文为准，本束不逐字段转抄以避免版本漂移。
