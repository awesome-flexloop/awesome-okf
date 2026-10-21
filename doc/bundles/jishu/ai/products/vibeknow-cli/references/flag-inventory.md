---
type: Reference
title: "VibeKnow CLI 旗标清单与统计口径"
description: "cmd/ 目录 104 处旗标注册调用的逐文件分布、72 个全局去重旗标名、vk create 的 23 个自有旗标与 cmd/video 的 44 个旗标对"
tags: [vibeknow, cli, 旗标, cli-reference, 统计口径]
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
---

# VibeKnow CLI 旗标清单与统计口径

本文登记 VibeKnow CLI 的旗标分布。信源为 tag `v0.9.2` @ `93a26eca`。

## 统计口径

| 指标 | 数值 | 口径 |
|---|---|---|
| 旗标注册调用总数 | 104 | `cmd/` 目录下全部 `Flags()` / `PersistentFlags()` 注册调用，去重前 |
| （文件, 旗标名）去重对数 | 103 | 同一文件内同名旗标只计一次 |
| 旗标名全局去重数 | 72 | 跨文件按旗标名去重 |

计数方法为括号配对抓取注册调用的完整实参列表，再取第一个字符串字面量，因此同时覆盖 `String` / `StringVar` / `BoolVar` / `IntVar` / `Float64Var` 等全部注册形式。

> **口径备注**：104 与 103 的差值来自同一文件内重复注册同名旗标的情况；72 与 103 的差值来自跨文件复用旗标名（如 `session-id` 出现在 10 余个 `cmd/video/` 文件中）。三个数字各有用途，不可互相替代。

## 逐文件分布

| 文件 | 旗标数 | 旗标名 |
|---|---|---|
| `cmd/create.go` | 22 | aspect, async, avatar, avatar-position, avatar-size, bgm, confirm, engine, export, from, images, kb-id, language, mode, pages, preview-dir, prompt, script-lock, text, theme, voice, yes |
| `cmd/video/set.go` | 15 | bgm, bgm-volume, session-id, subtitle, subtitle-animation, subtitle-bg-color, subtitle-bottom, subtitle-color, subtitle-font, subtitle-font-weight, subtitle-preset, subtitle-size, subtitle-stroke-color, subtitle-stroke-width, title |
| `cmd/profile/add.go` | 8 | credential-ref, default-project, endpoint-account, endpoint-figlens, endpoint-vectoria, endpoint-vibeknow, is-production, trust |
| `cmd/video/edit.go` | 7 | confirm, preview-dir, scene, script, script-only, session-id, yes |
| `cmd/video/export.go` | 7 | async, confirm, poll-interval, preview-dir, session-id, timeout, yes |
| `cmd/api/call.go` | 4 | body, method, path, service |
| `cmd/auth/login.go` | 4 | device-code, headless, no-wait, with-token |
| `cmd/kb/list.go` | 4 | older-than, page, pattern, size |
| `cmd/jobs/prune.go` | 3 | all, older-than, terminal |
| `cmd/kb/prune.go` | 3 | older-than, pattern, yes |
| `cmd/root.go` | 3 | output, profile, verbose |
| `cmd/video/download.go` | 3 | dest, overwrite, session-id |
| `cmd/video/wait.go` | 3 | for, preview-dir, session-id |
| `cmd/jobs/list.go` | 2 | active, limit |
| `cmd/video/avatar_retry.go` | 2 | scene, session-id |
| `cmd/video/list.go` | 2 | page, size |
| `cmd/video/pause.go` | 2 | session-id |
| `cmd/video/status.go` | 2 | preview-dir, session-id |
| `cmd/create_preset.go` | 1 | preset |
| `cmd/doc/get.go` | 1 | kb-id |
| `cmd/doc/images.go` | 1 | kb-id |
| `cmd/kb/delete.go` | 1 | yes |
| `cmd/theme/list.go` | 1 | mode |
| `cmd/video/export_status.go` | 1 | session-id |
| `cmd/video/script.go` | 1 | session-id |
| `cmd/voice/list.go` | 1 | language |

## 根命令持久旗标

| 旗标 | 作用 |
|---|---|
| `--profile` | 选择配置档案 |
| `--output` | 指定输出格式（`text` / `json` / `ndjson`） |
| `--verbose` | 打开详细输出 |

## `vk create` 的 23 个自有旗标

`cmd/create.go` 的 22 个加 `cmd/create_preset.go` 的 `preset` 1 个：

```
aspect          async           avatar          avatar-position
avatar-size     bgm             confirm         engine
export          from            images          kb-id
language        mode            pages           preset
preview-dir     prompt          script-lock     text
theme           voice           yes
```

### 按语义分组

| 组 | 旗标 | 备注 |
|---|---|---|
| 输入源 | `from`、`text`、`kb-id` | `from` 与 `text` 互斥；`kb-id` 必配 `doc_id` 形态的 `from` |
| 授权 | `export`、`yes`、`confirm` | 三者均在 preset 拒绝表内 |
| 执行方式 | `async`、`preview-dir` | `async` 与 `export` 互斥 |
| 风格 | `mode`、`script-lock`、`aspect`、`bgm`、`theme`、`language`、`voice`、`prompt`、`avatar`、`avatar-position`、`avatar-size`、`images`、`pages` | preset 允许表覆盖其中 14 项 |
| 引擎 | `engine` | `pipeline` / `agent` 两档 |
| 其它 | `preset` | preset 文件名或路径 |

## `cmd/video/` 的 44 个旗标对

`cmd/video/` 目录内（文件, 旗标名）去重对共 44 个。其中 `session-id` 出现在 10 余个文件，`yes` / `confirm` / `preview-dir` 跨 `edit`、`export`、`wait`、`status` 等文件复用。

| 旗标 | 出现文件 | 作用 |
|---|---|---|
| `session-id` | status / wait / download / url / export / export-status / script / edit / set / pause / resume / avatar-retry | 显式指定运行标识 |
| `preview-dir` | status / wait / export / edit | 预览产物落盘目录 |
| `confirm` | export / edit | 回传 `action_id` |
| `yes` | export / edit | 跳过交互确认 |
| `async` | export | 不等待导出完成 |
| `timeout` / `poll-interval` | export | 同步导出的轮询预算与间隔 |
| `dest` / `overwrite` | download | 下载目标路径与覆盖策略 |
| `for` | wait | 等待预算 |
| `page` / `size` | list | 分页参数 |
| `scene` / `script` / `script-only` | edit / avatar-retry | 场景定位与改写内容 |
| `bgm` / `bgm-volume` / `subtitle` + 10 个字幕样式旗标 | set | 作品级修改 |

`vk video export` 另有别名 `no-wait` 指向 `async`（`cmd/video/export.go:247` 的 `cmdutil.AliasFlags`）。

## 字幕样式旗标（10 个）

集中在 `cmd/video/set.go:43-47` 的 `subtitleStyleFlags` 变量：

```
subtitle-preset       subtitle-size        subtitle-color
subtitle-font         subtitle-font-weight subtitle-bg-color
subtitle-bottom       subtitle-stroke-color subtitle-stroke-width
subtitle-animation
```

## 相关概念

- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— create 参数域与正交组合
- [/concepts/06-preset-contract.md](/concepts/06-preset-contract.md) —— preset 的允许/拒绝清单
- [/concepts/07-subtitle-style-and-work-edit.md](/concepts/07-subtitle-style-and-work-edit.md) —— 字幕样式与作品修改
