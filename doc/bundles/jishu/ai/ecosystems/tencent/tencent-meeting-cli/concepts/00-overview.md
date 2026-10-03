---
type: Concept
title: "腾讯会议 CLI 是什么：CLI + Skill 双件架构与调用链路"
description: "腾讯会议官方 CLI（tmeet）的产品定位、双件分发模型（Go 二进制 + CLI-Skill 提示词契约）、从自然语言到 REST API 的调用链路，以及账号与能力边界。"
tags: [tencent-meeting, tmeet, cli, agent, skill, oauth, architecture]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: product-page
    resource: /references/product-page.md
    title: 腾讯会议 CLI 产品首页
  - id: github-readme
    resource: /references/github-readme.md
    title: tencentmeeting-cli GitHub README
  - id: cloud-doc
    resource: /references/cloud-doc.md
    title: 腾讯云文档《腾讯会议 CLI 说明》
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单与变更日志
---

# 腾讯会议 CLI 是什么

腾讯会议 CLI 是腾讯会议官方推出的命令行工具，命令入口为 `tmeet`，npm 包名为 `@tencentcloud/tmeet`，仓库 [TencentCloud/tencentmeeting-cli](https://github.com/TencentCloud/tencentmeeting-cli) 以 MIT License 开源，Go 1.22+ 编写（F-001、F-003）。产品首页标语是「一行指令，让 AI 为你管理腾讯会议」（F-002）。

## 双件架构：CLI 是手，Skill 是脑

理解 tmeet 的第一要点是：它不是一个单独的可执行文件，而是**两个必须分别安装的组件**：

| 组件 | 载体 | 职责 |
|------|------|------|
| CLI 本体 | npm 包 `@tencentcloud/tmeet`（Go 二进制 + npm 包装脚本） | 接收命令参数、自动注入 OAuth Token、调用腾讯会议开放平台 REST API、返回 JSON（F-096） |
| CLI-Skill | `npx skills add TencentCloud/tencentmeeting-cli` 安装的 Skill 包（仓库 `skills/tmeet-skill/SKILL.md`，v1.0.18） | 给 AI Agent 阅读的触发词、调用范例、参数规则与安全约束（F-012） |

安装指南把 Skill 明确标注为「必需」，并要求安装后重启 AI 工具才能完整加载（F-012、F-019）。只装 CLI 不装 Skill，人类可以直接敲命令，但 AI Agent 不知道何时调用、如何确认、哪些字段不能展示——安全行为契约全部写在 SKILL.md 的自然语言里，而非编译进二进制。

## 一次自然语言指令的完整链路

腾讯云文档给出的调用链路为（F-096）：

```
用户自然语言
   │  「帮我把明天下午的周会改到三点」
   ▼
AI Agent（已加载 tmeet-skill）
   │  ① 按 Skill 的触发词/范例理解意图
   │  ② 按安全约束决定是否二次确认
   │  ③ 拼出 tmeet 命令
   ▼
tmeet CLI（终端执行）
   │  ④ 自动注入本地 OAuth Token
   ▼
腾讯会议开放平台 REST API
   │  ⑤ 返回 JSON
   ▼
AI Agent 解析 JSON → 用自然语言回复用户
```

CLI 本身不包含大模型，也不做意图识别；Agent 宿主（Claude Code、Cursor、Codex 等）才是「脑」。

## 兼容的 Agent 宿主

产品首页列出的兼容工具包括 WorkBuddy、DeepSeek Harness、Claude Code、Codex、Cursor、GitHub Copilot，FAQ 另提到 Qclaw/OpenClaw（F-005、F-006）。CLI 本体是标准命令行程序，任何能执行 shell 命令并读取其 stdout 的 Agent 框架都可集成。

## 能做什么：覆盖会议核心业务域

截至 v1.0.18，命令树包含 10 个一级命令域、44 个子命令（F-033）：

| 域 | 能力概览 |
|----|----------|
| `auth` | 登录、登出、登录状态（3） |
| `meeting` | 会议创建/修改/取消/查询/搜索/受邀成员管理（11） |
| `contact` | 企业通讯录搜索与邮箱/手机号反查（3） |
| `record` | 录制列表/下载地址/内容搜索/智能纪要/转写/权限申请（9） |
| `report` | 参会人明细、等候室记录、异步导出任务（4） |
| `control` | 会中呼叫、踢人、等候室操作（3） |
| `minutes` | 元宝纪要搜索与获取（2） |
| `tshoot` | 日志导出、问题反馈（2） |
| `app` | 自己的 CLI 应用在会中的展示配置（2，v1.0.17+） |
| `event` | 实时会议事件订阅与总线管理（5，v1.0.18+） |

> ⚠️ 口径提示：腾讯云文档（页面更新时间 2026-07-08）写的是「19 个命令」，且不含 contact/control/minutes/app/event 域（F-034）。该文档反映的是较早版本；最新权威清单以仓库 `docs/command.md`（对应 v1.0.18，2026-09-11）为准。约两个月内子命令数从 19 增长到 44，本产品处于月级甚至周级迭代节奏，引用时务必标注版本与日期。

## 账号条件与能力边界

- **套餐**：个人版、专业版已开放；商业版/企业版需填写灰度申请表，专人联系开通（F-093）。
- **单账号**：CLI 以 OAuth 授权账号身份操作，只能访问该账号下数据，不能跨账号或访问企业级数据；同一时刻只支持单账号登录，切换需先 `tmeet auth logout`（F-094）。
- **平台**：macOS、Linux、Windows（F-018）。

## 官方明示的风险

README 的「安全与风险提示」明确指出：AI 可能因模型幻觉、提示词注入、投毒攻击、执行偏差等导致数据泄露、越权操作；安装使用 CLI 即视为自愿承担相关责任（F-097）。这也是官方为什么要把细粒度安全约束（二次确认、隐私字段、通讯录场景白名单）写进 Skill 的原因——详见 [06 - Agent 安全契约](05-agent-safety-contract.md)。

## 延伸阅读

- [01 - 安装与授权](01-install-auth.md)
- [02 - 命令体系与全局约定](02-command-map.md)
- [06 - Agent 安全契约](06-agent-safety-contract.md)
- 核心洞察：[安全边界在 Skill 提示词层](../spec/insights.md)
