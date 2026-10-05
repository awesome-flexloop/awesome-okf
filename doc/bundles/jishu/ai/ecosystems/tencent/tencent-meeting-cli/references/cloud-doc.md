---
type: Reference
title: "腾讯云文档《腾讯会议 CLI 说明》信源"
description: "腾讯云开发者文档 product/1095/133827 的事实登记：产品定义、Agent 调用链路、Keychain 凭证、19 命令旧清单（2026-07-08 页面口径）、常见报错、套餐条件与安全建议。"
tags: [tencent-meeting, tmeet, reference, tencent-cloud, docs, oauth]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: cloud-doc
    resource: https://cloud.tencent.com/document/product/1095/133827
    title: 腾讯云文档中心《腾讯会议 CLI 说明》
---

# 腾讯云文档《腾讯会议 CLI 说明》信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | cloud-doc |
| URL | https://cloud.tencent.com/document/product/1095/133827 |
| 类型 | 腾讯云开发者文档（官方） |
| 页面更新时间 | 2026-07-08 |
| 抓取日期 | 2026-10-03 |
| 对应事实 | F-004、F-015、F-021、F-025、F-029、F-030、F-034、F-040、F-067、F-093、F-094、F-096 |

> ⚠️ 时效性提示：该页面反映的是 v1.0.18 之前的版本形态（命令清单停留在 19 个、Node ≥16 口径）。凡与仓库 `docs/command.md`（v1.0.18）冲突处，以 command.md 为准，本束已并列登记。

## 产品定义与调用链路

文档将 tmeet 定义为腾讯会议官方命令行工具，核心作用是充当 AI Agent 的执行抓手：Agent 依托配套 CLI-Skill 完成命令调用，用户输入自然语言、AI 代为操作（F-004）。

调用链路（F-096）：

```
Agent 加载 CLI-Skill（触发词+范例+安全约束）
  → 拼 tmeet 命令并终端执行
  → CLI 自动注入 OAuth Token
  → 调腾讯会议开放平台 REST API
  → JSON 响应返回 Agent
```

## 环境与凭证（页面口径）

- 本地依赖：Node.js ≥ 16（F-015，与安装指南 >=14、package.json >=14 并列）；
- 授权同样为设备码 OAuth2，CLI 自动打开浏览器并轮询（F-021）；
- 凭证存入系统 Keychain，与设备绑定，无法在另一台机器解密（F-025）；
- 未登录提示 `user config is empty`（F-029）。

安全建议（F-030）：不传递/归档/上传 `~/.tmeet/` 与 Keychain 数据；不硬编码账号；不把凭证文件贴给 AI。

## 工具清单（旧口径，19 命令）

页面按五类列示 19 个命令：授权管理 3、会议管理 7、录制管理 6、参会报告 2、问题排查 1（F-034）。该清单不含 contact/control/minutes/app/event 等后续新增域；v1.0.18 的 command.md 已登记 44 个子命令（F-033）。

## 常见报错（页面登记）

| 报错 | 含义 |
|------|------|
| user config is empty | 未登录 |
| --start format error | 时间格式不合法 |
| --meeting-id is required | 缺必填参数 |
| user has been initialized | 重复登录 |

（F-040）

## 参会报告

页面介绍了参会人列表（含入会/离会时间）与等候室记录能力（F-067）。

## 使用条件

- 个人版、专业版已开放；商业版/企业版需灰度申请表（F-093）；
- 以 OAuth 账号身份操作，仅能访问该账号数据；当前只支持单账号登录，切换先 logout（F-094）。
