---
type: Reference
title: "腾讯文档官方用户手册《腾讯会议 CLI使用说明》信源"
description: "腾讯文档平台托管的官方用户面手册（2026-06-25 最后保存）的事实登记：用户叙事定位、兼容工具名单、v1.0.0 时期 19 命令逐名表、企业灰度申请表、凭证 Keychain 表述、四个对话式场景、规则中心与反馈渠道。与腾讯云文档 133827 高度同源但早 13 天。"
tags: [tencent-meeting, tmeet, reference, tencent-docs, user-manual, oauth]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: user-manual-qqdoc
    resource: https://docs.qq.com/doc/DVUNDV0trdUdqeW5X
    title: 腾讯文档《腾讯会议 CLI使用说明》
---

# 腾讯文档官方用户手册《腾讯会议 CLI使用说明》信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | user-manual-qqdoc（facts 中编号 s-qqdoc） |
| URL | https://docs.qq.com/doc/DVUNDV0trdUdqeW5X |
| 类型 | 腾讯文档（docs.qq.com）在线协作文档，官方维护 |
| 页面最后保存 | 2026-06-25 16:00（页面元数据 lastSaveTimestamp） |
| 抓取日期 | 2026-10-03 |
| 访问性 | 公开可读，无需登录与口令 |
| 对应事实 | F-099 ~ F-112（其中 F-105、F-106 为与 s-command/s-skill 的跨版本比对事实） |

## 抓取方式（可复现）

腾讯文档正文不在服务端 HTML 中，页面加载后由 XHR 拉取。抓取路径：

1. 请求 `https://docs.qq.com/dop-api/opendoc?id=DVUNDV0trdUdqeW5X&normal=1&outformat=1&noEscape=1&commandsFormat=1&doc_chunk_version=3&preview_token=&doc_chunk_flag=1`（需带正常浏览器 UA 与 Referer）；
2. 响应 JSON 中 `clientVars.collab_client_vars.initialAttributedText.text[0]` 为 base64 文本，解码后是 protobuf 线格式；
3. 按 varint/length-delimited 递归遍历 wire format，收集可 UTF-8 解码的文本块，首个大字段即文档全文（含表格单元格，超链接以内联 HYPERLINK 属性形式给出）。

局限：文档中的安装截图、操作截图与内测群二维码以图片对象引用，文本接口未包含其 URL，本信源只登记文字内容（F-099、F-109）。

## 与既有信源的关系：用户面手册 vs 云文档

本手册与 [cloud-doc.md](cloud-doc.md)（腾讯云文档 133827，页面更新 2026-07-08）内容高度同源：调用链路、19 命令五类分组、四条常见报错、AES-256-GCM + Keychain 凭证表述、套餐矩阵、安全三条❌/一条✅几乎逐句一致；本手册保存时间（06-25）早于云文档页面时间（07-08）13 天，云文档页面可视为该手册内容的文档中心镜像。差异/增量：

- 本手册是「对最终用户说话」的教程叙事（你说/你拿到/AI 做），云文档是条目式说明；
- 本手册给出企业灰度申请表的精确 URL（F-103）、用户规则中心链接（F-108）与反馈三渠道（F-109），云文档条目未含这些 URL；
- 本手册点名 Workbuddy/Qclaw（F-101），并给出四个对话式场景样例（F-111）与「对 agent 说」安装 prompt（F-112）。

## 核心内容登记

### 定位与宿主

- 话术：「腾讯会议 CLI 就是给 AI Agent 的那双手」「你不需要自己敲命令」（F-100）；
- 点名兼容工具：Workbuddy、Qclaw、Cursor、Claude Code、Codex（F-101）；
- 本地依赖：Node.js ≥ 16 + 一个支持执行 Shell 命令的 AI Agent（F-102，与云文档共同构成 ≥16 口径的两个用户面信源）。

### v1.0.0 时期 19 命令逐名表

授权 3 / 会议 7 / 录制 6 / 参会报告 2 / 排查 1，逐条职责原文见 F-104。跨版本核对结论：19 个命令名在 v1.0.18 全部存活，44 = 19 + 25 纯增量，无重命名（F-105）；当时的二次确认范围仅 create/update/cancel，v1.0.18 扩至 9 命令（F-106）。

### 账号与凭证

- 个人版/专业版已开放；商业版/企业版走「腾讯会议Skills企业账号灰度申请」智能表格（F-103）；
- 同一句写「AES-256-GCM 加密，存入系统 Keychain，与设备绑定」，是 F-024/F-025 两口径互补的直接文本证据（F-107）。

### 场景、风险与支持

- 四个对话式场景（预约/取纪要/查参会/带确认改期，F-111）；
- 第三方 AI 客户端数据处理风险（点名 Cursor/Claude Code/ChatGPT，F-110）；
- 用户规则中心 rule.tencent.com/rule/202603130003（F-108）；
- 反馈三入口：GitHub Issues / SECURITY.md / 内测体验互助群二维码（F-109）；
- 最小命令序列（安装→login→create→list/list-ended→logout，F-112）。

> ⚠️ 时效性提示：该手册停留在 v1.0.0 时期命令面（19 命令），截至抓取日（2026-10-03）未跟进 contact/control/minutes/app/event 五个新域。参数级事实以 v1.0.18 `docs/command.md` 为准（见 [command-reference.md](command-reference.md)）；本信源价值在于用户面叙事、精确外链与跨日期版本比对。
