---
okf_version: "0.2"
type: Example
title: 实操 1——安装 LoopX 与 doctor 自检
description: 按博文作者实测路径安装 loopx、安装工作流技能、doctor 自检；标注 1.0 的 Node.js 22.18+ 前置要求与 Windows PowerShell 7 分支
tags: [loopx, 安装, pip, doctor, powershell]
generated:
  by: trae-solo-agent
  at: "2026-09-16T20:40:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
  - id: github-loopx
    url: https://github.com/huangruiteng/loopx
  - id: pypi-loopx
    url: https://pypi.org/project/loopx/
---

# 实操 1：安装 LoopX 与 doctor 自检

> 本篇复现博文「快速开始」的作者实测路径（F-021~F-023、F-026），并补充核验时（1.0.5 时代）官方文档的新增前置条件。**本文步骤以官方 README 逐字比对，但未在本知识包制作中真机执行**，执行时如遇差异以官方 Getting Started 为准。

## 0. 前置环境

| 组件 | 博文口径（0.4/0.5 时点） | 当前要求（1.0.x，核验时最新 1.0.5） |
|---|---|---|
| Python | 3.11 以上（F-021） | **>=3.11**（PyPI `requires_python` 实测，F-038） |
| Node.js | 博文未提 | **22.18.0+**，推荐 24 LTS——运行托管的 TypeScript Effect 内核，LoopX 自动启停（F-040） |
| 平台 shell | macOS/Linux 直接用；Windows 用 PowerShell 7（F-021） | 不变：POSIX shell / 原生 Windows PowerShell 7，无需 POSIX 兼容层 |
| Git | 未提 | 仅贡献者 clone/canary 工作流需要 |

> ⚠️ **版本提示**：博文发文时（2026-09-03）PyPI 最新为 0.5.4，1.0 线始于 09-06。下列 pip 命令在两个时代完全一致；若你安装到的是 1.0+，务必先满足 Node 条件。用 `pip index versions loopx` 或 PyPI 页面确认当前版本。

## 1. 安装（三条命令）

macOS / Linux：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
```

Windows 原生 PowerShell 7（官方给出的等价形式）：

```powershell
py -3.11 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
```

三条命令的职责（F-022，与官方 Getting Started 逐字一致）：

1. `pip install --upgrade loopx`——从 PyPI 安装/升级，无需 clone 仓库；
2. `loopx workflow-skills --install`——向 AI 编程宿主安装"工作流技能"（让 Codex/Claude Code 等能识别 LoopX 工作流）；
3. `loopx doctor`——环境与安装自检。

博文称"pip 一把装完"，并形容整个过程"没什么要配置的"（F-026，作者体验）。0.4/0.5 时代 PyPI 包零强制运行时依赖；1.0 起 Node 是外部前置（见上表）。

## 2. 重启宿主

安装完成后**重启你的 AI 编程工具**，使其重新加载工作流技能（F-023，官方原文 "Restart your agent host after first install so it reloads the workflow skills."）。漏掉这一步会导致宿主内看不到 loopx 技能/斜杠命令。

## 3. doctor 通过的判据

官方给出的"连接成功"检查清单（首次安装时先看 doctor 项）：

- `loopx doctor` 输出通过；
- 后续连接项目后会生成 `.loopx/registry.json`（F-046）；
- `loopx status` 能显示当前目标、具体的用户门禁与下一条 Agent 待办；
- 能看到可见的 loop 驱动方式或一条明确的激活指令；
- 本地运行态被 ignore 而非提交。

## 4. 升级与卸载（官方补充，博文未覆盖）

- 已安装版本可用 `loopx update plan` 查看计划、`loopx update apply` 执行；LoopX 会保持探测到的 pip/pipx/archive 安装归属，不擅自切换渠道；
- 贡献者才需要 clone 安装：`git clone https://github.com/huangruiteng/loopx ~/loopx && ~/loopx/scripts/install-local.sh && loopx doctor`；
- 完整 pipx、宿主命令面、回滚与卸载见官方 Installing LoopX 指南。

## 5. 常见报错对照（依据官方文档推断，非真机实测）

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 宿主内找不到 loopx 技能 | 未重启宿主 | 退出并重新打开 Codex/Claude Code/Cursor（F-023） |
| 1.0+ 下 doctor 提示 Node 相关失败 | 未装 Node.js 22.18+ | 安装 Node 24 LTS 后重跑 doctor（F-040） |
| Windows 下命令异常 | 使用了 Windows PowerShell 5.1 或 cmd | 改用 PowerShell 7（F-021） |
| `loopx` 命令不在 PATH | Python 环境的 console scripts 不在 PATH | 激活对应 Python 环境或用 `py -3.11 -m` 等价形式 |

下一篇：[连接项目与首个长期目标](01-connect-goal-dashboard.md)。
