---
okf_version: "0.2"
type: Example
title: "安装与快速上手：桌面版与网页版"
description: "OpenCreator 桌面版与网页版的安装/启动例程（未在本机实测）"
tags: [opencreator, install, desktop, web, quickstart]
stale_after: 2026-12-31
source: "wechat-public-okf:E"
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator README"
---

# 安装与快速上手（未实测引导）

> ⚠️ 本页为**引导性例程**，未在本机实际运行。请以官方文档与 Releases 为准。

## 目标

在本机启动 OpenCreator，开始第一个创作任务。

## 前置准备

- **需要自备**：模型提供商的凭据（OpenAI、DeepSeek、通义千问、Kimi、智谱 GLM、豆包、文心、混元、MiniMax、Grok 等任一，或走 OpenAI 兼容接口的国内服务商）。
- 若用**桌面版**：无需另装 Node，安装包自带 Codex CLI。
- 若用**网页版**：需 Node 22+、pnpm 9.15.0、一个 Codex CLI。

## 例程 A：桌面版（推荐）

1. 打开官方 Releases 页面，下载对应平台安装包（macOS Apple 芯片 / macOS Intel / Windows 64 位）。
2. 安装并启动应用。
3. 首次启动会扫描本机 Codex 配置：有则选择复用；无则走引导表单配其他服务商。
4. 进入 Dashboard，选择创作工具或从模板开始，填参数点生成。

## 例程 B：网页版（源码）

```bash
# 1. 环境准备（Node 22+，pnpm 9.15.0）
node -v          # 期望 >= 22
corepack enable  # 让 pnpm 自动对齐版本
pnpm -v          # 期望 9.15.0

# 2. 克隆并安装
git clone https://github.com/krillinai/OpenCreator.git
cd OpenCreator
pnpm install

# 3. 启动网页版
pnpm web:dev

# 4. 浏览器打开
#    访问 http://127.0.0.1:19861/
```

> 端口 `19861`、`Node 22`、`pnpm 9.15.0` 为博文声明（[F-038/F-039](../references/facts.md)），以官方开发文档为准。

## 第一个任务建议

- 模型任务走你自己的额度，单 Agent 任务可能消耗较大 token（社区估算 10~20 万，非官方）。**建议先拿一个小任务试水**（如一条短视频的翻译或一次图片生成），确认额度与成本后再放大任务。

## 验证

- 桌面版：应用启动后能看到 Dashboard 与工具面板即视为成功。
- 网页版：浏览器访问 `127.0.0.1:19861/` 能加载界面即视为成功。

## 相关概念

- [安装与快速上手（概念）](../concepts/03-install-quickstart.md)
- [数据与安全](../concepts/04-local-data-security.md)