---
type: Example
title: "十分钟上手：从安装到约出第一场会"
description: "完整走通 tmeet 安装、CLI-Skill 安装、设备码登录、登录态校验、创建会议、查询会议列表的最小闭环，含常见报错处置。"
tags: [tencent-meeting, tmeet, example, quickstart, installation, auth, meeting-create]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: install-guide
    resource: /references/install-guide.md
    title: 腾讯会议 CLI 安装指南
  - id: command-reference
    resource: /references/command-reference.md
    title: 官方完整命令参考 docs/command.md
  - id: cloud-doc
    resource: /references/cloud-doc.md
    title: 腾讯云文档《腾讯会议 CLI 说明》
---

# 十分钟上手：从安装到约出第一场会

> 本示例基于 v1.0.18 文档整理，命令均可直接在终端执行；在 Agent 中使用时，把自然语言交给已加载 tmeet-skill 的 AI 即可，命令仅用于理解背后发生了什么。

## 0. 前置条件

- Node.js（package.json 要求 `>=14`，建议直接装 LTS；腾讯云文档另有 ≥16 的口径，F-013~F-015）
- 腾讯会议账号：个人版/专业版直接可用；商业版/企业版需灰度申请（F-093）
- macOS / Linux / Windows（F-018）

## 1. 安装 CLI（2 分钟）

```bash
npm install -g @tencentcloud/tmeet
tmeet --version
```

预期输出版本号（如 `v1.0.18`）。若提示 `npm: command not found`，先安装 Node.js LTS 并确认 npm 全局 bin 在 PATH 中、重启终端（F-016）。

## 2. 安装 CLI-Skill 并重启 AI 工具（1 分钟）

```bash
npx skills add TencentCloud/tencentmeeting-cli -y -g
```

安装后**完全退出并重启** Claude Code / Cursor / Codex 等 AI 工具（F-019）。这一步不做，Agent 不会获得二次确认、隐私字段等安全规则。

## 3. 登录（2 分钟）

```bash
tmeet auth login
```

- 终端会自动打开浏览器，在浏览器中确认授权；
- 终端轮询最多 5 分钟（F-021）；
- 远程/无桌面环境：`tmeet auth login --no-browser`，复制终端打印的 URL 到本地浏览器（F-022）；
- ⚠ 不要用 `tmeet auth login &` 后台执行（凭证可能写入失败，F-023）。

验证：

```bash
tmeet auth status
```

能看到 OpenId 与 Token 过期状态即成功。未登录时业务命令会报 `user config is empty`，重新 login 即可（F-040）。

## 4. 约出第一场会（2 分钟）

```bash
tmeet meeting create \
  --subject "CLI 上手测试会" \
  --start "2026-10-20T14:00+08:00" \
  --end   "2026-10-20T14:30+08:00" \
  --join-type 1
```

要点：

- `--subject`/`--start`/`--end` 三项必填（F-041）；
- 时间必须带时区，写成 `2026-10-20T14:00+08:00`，只写日期会报 `--start format error`（F-038、F-040）；
- `--join-type 1` 表示所有人可加入；
- 返回的 JSON 在 `data` 中包含会议信息。**会议号（meeting_code）用来分享和记忆；meeting_id 只在后续命令参数里用，不要转发给别人**（F-074）。

加密码与等候室：

```bash
tmeet meeting create --subject "带管控的会" \
  --start "2026-10-21T10:00+08:00" --end "2026-10-21T11:00+08:00" \
  --password "1234" --waiting-room
```

## 5. 查看自己的会议（1 分钟）

```bash
# 进行中/即将开始（精简输出，适合看摘要）
tmeet meeting list --compact

# 本周已结束的会
tmeet meeting list-ended \
  --start "2026-10-19T00:00+08:00" --end "2026-10-26T00:00+08:00" \
  --compact

# 按会议号精确查（只写数字）
tmeet meeting get --meeting-code "123456789" --compact
```

page-size 20~30，想看更多时把响应中的游标原样传给 `--page-token`（F-039、F-050、F-051）。

## 6. 改期与取消（会触发确认）

```bash
tmeet meeting update --meeting-id "<id>" \
  --start "2026-10-22T15:00+08:00" --end "2026-10-22T16:00+08:00"

tmeet meeting cancel --meeting-id "<id>"
```

在 Agent 中，这两条命令执行前 AI 会先用**会议号**展示变更内容并停下等你确认，你回复「确认」后才真正执行（F-072、F-073）。直接在终端敲则不经过该流程——这正说明安全规则在 Skill 层而非 CLI 层。

## 7. 完成后的清理（可选）

```bash
tmeet auth logout
```

共享设备或演示结束建议登出。v1.0.18 会先停掉事件总线等资源再清 Keychain 凭证（F-032）。

## 最小闭环回顾

```
npm install -g @tencentcloud/tmeet
npx skills add TencentCloud/tencentmeeting-cli -y -g   # 重启 AI
tmeet auth login
tmeet meeting create --subject … --start … --end …
tmeet meeting list --compact
```

## 下一步

- 会后自动取纪要 → [示例 02 · 会后取纪要工作流](02-minutes-workflow.md)
- 周期会议 + 参会明细导出 → [示例 03](03-recurring-export.md)
- 实时事件驱动自动化 → [示例 04](04-event-automation.md)
