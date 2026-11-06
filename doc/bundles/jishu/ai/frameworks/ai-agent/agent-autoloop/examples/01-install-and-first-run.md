---
type: Example
title: "安装与首次试跑：从一条命令到读懂 status"
description: "官方 INSTALL/README 的安装命令、目录布局、验证命令组、try→answer→status 首次试跑序列，以及 Windows/WSL2 与用量合规前置提示"
tags: ["安装", "试跑", "Node.js 24", "WSL2", "doctor", "用量合规"]
status: stable
sources:
  - id: official-install
    resource: https://github.com/KKKKhazix/agent-autoloop/blob/main/INSTALL.md
    title: "Agent Autoloop 官方 INSTALL（标题即「安装说明（写给 Agent）」）"
  - id: official-readme
    resource: https://github.com/KKKKhazix/agent-autoloop/blob/main/README.md
    title: "Agent Autoloop 官方 README"
---

# 安装与首次试跑

> **⚠️ 可复现性声明（务必先读）**：本篇的命令、目录与输出序列**全部整理自官方 `INSTALL.md` / `README.md`（2026-11-06 `main` 分支快照）**，可照做，但**本知识包生成过程中未在本机安装或运行该项目**。本机为 Windows，而官方 Windows 版待定（F-045）。官方另标注多项「未测 / 未逐个跑过」，请按 [P0 核验报告](../references/verification.md) 的分档判断。
>
> 博文没有逐步教安装，而是给出一段把仓库地址交给 Agent、让它自己读 README 与 INSTALL.md 装好并试跑的提示词（F-038）；作者称 INSTALL.md 本来就是写给 Agent 看的。本篇把同一份官方文档拆成人类可读的步骤。

## 0. 前置条件

| 条件 | 官方要求 | 检查命令 | 事实 |
|------|---------|---------|------|
| 操作系统 | **macOS / Linux**；Windows 版待定 | `uname -a` | F-044、F-045 |
| Node.js | **24 或更新** | `node --version` | F-044 |
| Git | 需要 | `git --version` | F-044 |
| curl | 需要 | `curl --version` | F-044 |
| 命令行 Agent | 一个**已安装并登录**的 CLI Agent（如 Claude Code / Codex） | 手动确认 `claude` 或 `codex` 可用 | F-044 |
| GitHub 账号 | **不需要** | — | F-044 |

> ⚠️ 博文「电脑上装个 Node 就能跑」（F-013）省略了 Node 24+ 版本下限、Git、curl 与平台限制，这是最常见的踩坑点。「零第三方依赖」指**运行时依赖为 0**（F-058、F-061），不等于零前置。

### 动手前的合规前置（官方 F-064，博文未提）

中台调用的是本机已登录的 CLI，**不读取或转存账号凭据**；模型调用消耗算在你自己的账号上，额度与使用范围遵循各厂商服务条款。官方明确：**高频自动化场景下厂商通常更建议使用 API Key**（个人订阅额度主要为日常人工交互设计）；**对外提供服务请使用 API Key**。

→ 如果你打算按 [规则配置](02-rules-and-receipts.md) 设置「每 5 分钟巡检」「每晚批量跑」这类 cron，先按厂商条款确认账号用法，再往下走。

## 1. 安装

```bash
curl -fsSL https://raw.githubusercontent.com/KKKKhazix/agent-autoloop/main/install.sh | sh
```

安装后的目录布局（F-046）：

| 路径 | 内容 |
|------|------|
| `~/.agent-autoloop/app` | 程序本体 |
| `~/.agent-autoloop` | 配置与记录（含后面的 `rules.json`） |

安装器与 `agent-autoloop update` 都取**最新 Release（通过全部检查的版本）**；`main` 上未发布的改动等下一个 Release（F-046）。安装器与中台启动时把数据目录权限设为 `0700`（F-066）。

> 安全提示：上面是 `curl | sh` 的远程脚本安装。执行前建议先把脚本下载下来看一遍（`curl -fsSL .../install.sh -o install.sh` 再 `less install.sh`），这是通用卫生习惯，非官方原文要求。

## 2. 验证安装

```bash
agent-autoloop --version
agent-autoloop doctor
agent-autoloop check
```

三条来自官方安装验证与运维命令组（F-048、INSTALL 验证段）。`doctor` 用于自检环境，`check` 用于检查配置状态；具体输出以本机版本为准，**本知识包未记录实测输出**。

## 3. 首次试跑：try → answer → status

官方给出的三段序列（F-047）：

```bash
agent-autoloop try          # 启动演示试跑
agent-autoloop answer 1 2   # 非交互终端下选择第 2 项
agent-autoloop status       # 查看会话续接与今天 / 最近 7 天轮数、Token 与费用
```

| 步 | 命令 | 预期发生什么 | 事实 |
|----|------|-------------|------|
| 1 | `agent-autoloop try` | 启动演示任务，中途转给用户一个问题让其**选颜色** | F-039、F-047 |
| 2 | `agent-autoloop answer 1 2` | 在第 1 轮问题上选择第 2 项；官方示例里该选项为绿色 | F-047 |
| 3 | 观察 | 选完后 Agent 接着把活干完并告知通过（博文描述） | F-039 |
| 4 | `agent-autoloop status` | 查看会话是否续接上，以及轮数 / Token / 费用统计 | F-047 |

> 这一串恰好把 [挂起零消耗](../concepts/02-four-mechanisms.md) 走了一遍：提问后 Agent 退出，人工点选后从存档接回原会话，而不是重跑任务。

## 4. 日常运维命令组（官方 F-048）

| 命令 | 用途 |
|------|------|
| `agent-autoloop --version` | 查看版本 |
| `agent-autoloop doctor` | 环境自检 |
| `agent-autoloop check` | 配置检查 |
| `agent-autoloop rules explain` | 解释当前规则会怎么派活 |
| `agent-autoloop emit <类型> --dry-run` | 预演一条事件派给谁，**不连接中台、不写日志** |
| `agent-autoloop why 1` | 查第 1 轮的完整事件链（官方自测命令，F-060） |
| `agent-autoloop status` | 会话续接与用量统计 |

`rules explain` 与 `emit --dry-run` 在 [规则与回执](02-rules-and-receipts.md) 里会再用到——**先预演再接真实事件**，是这套系统里成本最低的验证方式。

## 5. Windows 用户：当前没有官方支持路径

官方口径（F-045）：**Windows 版待定**，作者称 11 月 7、8 日回家后开发并做兼容性测试，进度见 issue #17。WSL2 按 Linux 安装可跑，但有五项注意：

| # | WSL2 限制 |
|---|----------|
| 1 | 需要 systemd；否则用 `--no-service` / `loginctl enable-linger` |
| 2 | 桌面通知到不了 Windows 桌面 |
| 3 | `command` 方式接入的 Agent 不上报用量 |
| 4 | WSL2 自身约占 1GB 内存 |
| 5 | 整体仍按 Linux 方式安装，不视为原生 Windows 支持 |

> 时效性：这是 2026-11-06 的官方快照。Windows 版进度请以仓库 issue #17 与最新 Release 为准，本包的复核项已登记在 [P0 核验报告](../references/verification.md)。

## 6. 卸载

```bash
agent-autoloop uninstall           # 默认保留规则、密钥与记录
agent-autoloop uninstall --yes     # 非交互确认
```

⚠️ **卸载不等于清除数据**：默认保留 `~/.agent-autoloop` 下的规则、密钥与记录（F-066）。迁移或报废机器前请单独处理该目录。

## 7. 边界与未验证项清单

1. 本篇所有命令**未在本机实测**；官方给出的是命令与输入输出序列，不是本包的实测记录。
2. 官方注明场景模板样例数据均为虚构，脚本与回执只用本地 HTTP 与假飞书 CLI 验证、未在真实账号跑完整业务（F-067）。
3. 试跑之外的 Agent / 通道 / Webhook 支持程度分三档，见 [03 插件生态](../concepts/03-plugin-ecosystem.md) 第五节与 [插件接入演练](03-plugins-and-delivery.md)。
4. 性能数字为作者单环境自测（Apple M5 Pro / 24GB / Node 24.21.0），无第三方独立复现（F-061）。
