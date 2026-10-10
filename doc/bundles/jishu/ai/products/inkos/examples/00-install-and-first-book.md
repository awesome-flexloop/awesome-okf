---
okf_version: "0.2"
type: Example
title: 实操 1——从零跑通 InkOS：安装、配置与写出第一本书
description: npm 全局安装 @actalk/inkos、三模型配置入口、建书链路（--brief 建书→世界观→角色→大纲→细纲→确认→开写）、守护进程 inkos up 挂机写章与回调通知；附可用性检查表与常见坑
tags: [inkos, 安装, npm, 模型配置, 建书, 守护进程, first-book]
generated:
  by: reference_agent/trae-solo
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: draft
stale_after: "2026-12-10"
sources:
  - id: github
    resource: https://github.com/Narcooo/inkos
    title: "Narcooo/inkos README"
  - id: blog
    resource: https://mp.weixin.qq.com/s/wJr32O2L82eq5k_7wJHiJQ
    title: "枫音AI 推广文 2026-10-08"
---

# 实操 1：从零跑通 InkOS——安装、配置与写出第一本书

> **实操来源说明（必读）**：本篇命令均来自**官方 README 的逐字核验**（核验日 2026-10-10，对应 README 当前主线，F-029~F-045）；**本知识包制作过程中未在任何环境真机执行**。博文作者仅以营销软文口径描述界面与流程（F-011~F-028），**未给出任何命令、未给版本号、未展示输出**。因此本篇是"官方口径重组的实操指引"而非"作者实测记录"——命令可能随版本变化，执行前请以官方最新文档为准。

## 0. 前置认知（装之前必须清楚）

- **InkOS 不内置模型**：必须配置自己的大模型 API（F-028、F-039）。它在工程侧是"自带模型才跑得动"的创作管线，而非开箱即用的聊天框。
- **开源协议为 AGPL-3.0**（F-032）：想商用/闭源二次开发/线上托管，先读 [00 概览的开源协议补充](../concepts/00-inkos-overview.md) 的 AGPL 传染性说明。
- **需要能长跑的守护环境**：挂机写书依赖 `inkos up` 后台进程（F-042），进程必须保持存活。

## 1. 安装（npm 全局包）

官方安装命令（F-039）：

```bash
npm i -g @actalk/inkos
```

完成后应出现 `inkos` 命令。**注意**：InkOS 也发布为 **OpenClaw Skill**（`clawhub install inkos`，F-034）——若你用 OpenClaw/兼容 Agent，可走 Skill 路径而不装 CLI；否则 npm 全局安装即可。

## 2. 配置模型（硬前提）

官方配置命令（F-039）：

```bash
inkos config set-global \
  --provider <openai|anthropic|custom> \
  --base-url <url> \
  --api-key <key> \
  --model <model>
```

配置持久化在 `~/.inkos/.env`（F-039）。要点：

- **provider 三选一**：`openai` / `anthropic` / `custom`（自定义走 `--base-url`）。
- **多模型路由（可选）**：想按 Agent 分工换模型用 `inkos config set-model <agent> <model> --provider <p>`，未配的 Agent 自动回退全局（F-045）。
- **博文建议参考（作者观点，非官方承诺）**：建议用官方平台，第三方中转站需能自动读模型列表（F-028）——若你的中转不支持，配置可能不稳定。

## 3. 建书（对话式 / 简报式）

两种建书入口（F-036）：

**① 对话式建书**：自然语言逐步构思世界观、角色……草稿就绪后一键创建，对应博文"先搭框架由你确认再继续"（F-011、F-012）。

**② 简报式建书**：

```bash
inkos book create --brief my-ideas.md
```

把脑洞/世界观/人设写进 `my-ideas.md`，一次传入（F-036）。建好后 Agent 流水线会逐步搭建**世界观 → 角色卡 → 大纲 → 细纲**，每一步给你确认再推进（F-011、F-012）——这是它区别于"直接生成整本"的人审门控设计。

## 4. 开写与守护进程

1. **指定章节开写**（继承 7 真相文件设定，F-016、F-035）：

   ```bash
   inkos write
   ```

   （README 提供 `--words` 目标字数治理，见 [01 记忆与流水线](../concepts/01-memory-and-agent-pipeline.md)）

2. **挂机写书**：`inkos up` 启动后台循环自动写章（F-042），对应博文"加通讯软件挂机写、写完叫醒"（F-026）。通知推送支持 Telegram / 飞书 / 企业微信 / Webhook（HMAC-SHA256 签名 + 事件过滤，F-042）。

3. **持续提升风格**：若想让后续章节贴近某文风，先 `inkos style analyze` 提取指纹，再 `inkos style import` 注入这本书（F-043）。

## 5. 装完如何确认可用（检查表）

> ⚠️ **官方未登记等价于 doctor 的独立自检命令**：不要按其他 CLI 工具的习惯去找 `inkos doctor`。以下判据均来自 README 登记的功能入口。

| 检查项 | 判据 | 出处 |
|---|---|---|
| 命令存在 | 终端 `inkos --help` 有输出 | F-039/F-034 |
| 模型已配 | `~/.inkos/.env` 存在且含 provider/base-url/api-key/model | F-039 |
| 能建书 | `inkos book create` 能完成建书并产出 7 真相文件 | F-035、F-036 |
| 能开写 | `inkos write` 能产出章节并写状态 | F-016 |
| 能守护 | `inkos up` 能启动后台循环 | F-042 |
| 能仿写（可选） | `inkos style analyze` 能对输入文本出指纹 | F-043 |

## 6. 常见坑

| 坑 | 说明 | 出处 |
|---|---|---|
| 以为自带模型 | InkOS 不含模型，必须自带 API；这是最大心智落差 | F-039、[00 概览](../concepts/00-inkos-overview.md) |
| 忽略 AGPL 传染性 | AGPL-3.0 下做商用/闭源二次开发需评估；博文只说"开源"未提 License | F-032 |
| 中转站不稳 | 第三方中转需能自动读模型列表，否则配置不稳定（作者建议，非官方承诺） | F-028 |
| 守护进程被杀 | `inkos up` 依赖后台进程存活，宿主休眠/占用关闭会打断 | F-042 |
| 把"去 AI 味"当绝对保证 | 是工程化降低而非绝对抗检测，效果因模型而异 | F-041、[02 内容能力](../concepts/02-content-capabilities-and-fit.md) |

## 7. 延伸

- 机制层：为什么这样设计 → [01 记忆与 Agent 流水线](../concepts/01-memory-and-agent-pipeline.md)
- 能力与适用判断 → [02 内容能力与适用判断](../concepts/02-content-capabilities-and-fit.md)
- 信源与勘误 → [references](../references/index.md)