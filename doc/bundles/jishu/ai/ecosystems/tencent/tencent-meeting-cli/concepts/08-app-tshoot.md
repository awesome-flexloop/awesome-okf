---
type: Concept
title: "应用展示配置与运维反馈（app / tshoot）"
description: "v1.0.17 的 app get/set 管理 CLI 应用在会中的展示形态（主页/三档布局/名称），以及 tshoot log 日志导出与 tshoot feedback 结构化问题反馈回流机制。"
tags: [tencent-meeting, tmeet, app, layout, tshoot, logs, feedback, telemetry]
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
    title: CLI-SKILL 清单与 CHANGELOG（v1.0.17 / v1.0.18）
---

# 应用展示配置与运维反馈

## app：CLI 应用的会中展示（v1.0.17+）

`app get` / `app set` 管理**当前登录用户自己的 CLI 应用**在腾讯会议客户端会中的展示配置（F-087）。

```bash
tmeet app get

tmeet app set \
  --homepage "https://example.com/meeting" \
  --layout-style sidebar \
  --sdk-name "示例助手"
```

| 参数 | 取值/约束 |
|------|-----------|
| `--homepage` | http/https URL，≤ 200 字符；传空字符串表示不下发（不在会中展示） |
| `--layout-style` | `sidebar`（375px 侧边栏）/ `wide_sidebar`（735px 宽侧边栏）/ `popout`（960×540 弹窗） |
| `--sdk-name` | 显示名称；显示宽度 ≤ 20，ASCII 字符计 1、中文字符计 2 |

（F-087）

### 两条版本/生效规则

- **协议支持**：腾讯会议客户端 3.45.10 之前版本不支持会中打开 `http://` 页面，仅支持 `https://`；3.45.10 及以后两者都支持（F-088）。面向不确定客户端版本的用户时，优先用 https 主页。
- **生效时机**：`app set` 的变更不影响当前已在进行中的会议，需要重新入会才能看到变化（F-089）。配置后应提示用户「下一场会议生效」。

## tshoot：日志与问题反馈（2 个命令）

### 导出日志：tshoot log

```bash
tmeet tshoot log                          # 全量本地日志
tmeet tshoot log --start "2026-10-01T00:00+08:00" --end "2026-10-03T00:00+08:00"
tmeet tshoot log --upload                 # 打包并上传服务器（需登录）
```

- 输出 zip 包，路径形如 `~/tmeet_ts_{datetime}.zip`；
- `--start` 与 `--end` **必须同时传或同时不传**（F-090）。

排障协作时，Agent 可引导用户导出日志并在获得同意后 `--upload`，再把回执提供给支持渠道。

### 结构化反馈：tshoot feedback

```bash
tmeet tshoot feedback \
  --category tool_inadequate \
  --intent "想批量导出整个部门上周的参会记录，但 CLI 只能按会议导出" \
  --actions-tried "尝试用 participants-export 循环 12 场会议" \
  --result "调用次数过多，希望支持按时间范围批量导出" \
  --tool-name "report participants-export"
```

字段（F-091）：

| 字段 | 必填 | 约束 |
|------|------|------|
| `--category` | 是 | `tool_not_found` / `tool_error` / `tool_inadequate` / `unexpected_result` / `suggestion` 五选一 |
| `--intent` | 是 | 用户原始意图，≤ 200 字符 |
| `--actions-tried` | 否 | 已尝试动作，≤ 500 字符 |
| `--result` | 否 | 实际结果/阻塞点，≤ 500 字符 |
| `--tool-name` | 否 | 相关命令名 |
| `--error-code` | 否 | 相关错误码 |

### 反馈的 Agent 行为规则

这是 tmeet「能力缺口回流」设计的入口，但 SKILL.md 对它有三条纪律（F-092）：

1. **上报前二次确认**（向用户展示将提交的内容）；
2. **强制脱敏**：不得包含姓名、电话、会议号、会议链接、会议主题、参会人；姓名写成「张*」、手机号写成「138****8000」；
3. **同一会话同一问题只报一次**，失败去重，不重复打点。

`category` 的选用语义：

| category | 适用 |
|----------|------|
| `tool_not_found` | 想做的事没有对应命令（能力缺口） |
| `tool_error` | 命令报错/崩溃 |
| `tool_inadequate` | 有命令但能力不足（如只能单会议、字段不够） |
| `unexpected_result` | 能跑通但结果与预期不符 |
| `suggestion` | 一般性产品建议 |

## 运维操作速查

| 场景 | 命令 |
|------|------|
| 排查「某命令行为异常」 | `tshoot log --start/--end` → 用户确认 → `--upload` |
| Agent 发现没有对应工具 | 经用户确认后 `tshoot feedback --category tool_not_found` |
| 设置会中应用主页 | `app set --homepage <https-url> --layout-style <样式>` |
| 查看当前应用配置 | `app get` |
| 停用会中应用展示 | `app set --homepage ""` |
| 事件总线异常 | `event status --fail-on-orphan` → `event stop --force`（见 [07](07-event-bus.md)） |

## 延伸阅读

- [07 - 实时事件总线](07-event-bus.md)
- 核心洞察：[洞察四 · 能力缺口与实时事件的产品化](../spec/insights.md)
