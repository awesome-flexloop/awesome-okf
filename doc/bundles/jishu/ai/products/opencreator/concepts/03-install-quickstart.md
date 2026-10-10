---
okf_version: "0.2"
type: Concept
title: "安装与快速上手：桌面版与网页版"
description: "OpenCreator 的两种上手路径——桌面版（自带 Codex，免装 Node）与网页版（Node+pnpm 源码启动）"
tags: [opencreator, install, quickstart, desktop, web]
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator README"
---

# 安装与快速上手

> ⚠️ 本概念仅整理官方与博文的**安装/启动路径**，**未在本机实测**。具体命令、版本与端口以官方开发文档为准。

## 路径一：桌面版（最省事）

- 从官方 **Releases** 页面下载安装包，提供 **macOS（Apple 芯片与 Intel）和 Windows 64 位** [F-035](references/facts.md)。
- 桌面版**自带 Codex CLI**，无需另装 Node [F-036](references/facts.md)。
- **首次启动**：扫描本机是否有可用的 Codex 配置——有则询问是否复用（复用一个已登录的 ChatGPT 或 API Key 配置）；没有则走引导表单配置其他模型服务商（国内厂商按 OpenAI 兼容格式填写）[F-037](references/facts.md)。
- 本地 Runtime 按需启动，并自动准备一个默认项目。

## 路径二：网页版（源码跑）

按官方/博文整理的需求：

1. **Node 22 以上**。
2. **pnpm 锁定 9.15.0**（可用 `corepack enable` 自动对齐版本）。
3. 额外准备一个 **Codex CLI**。
4. 克隆仓库后 `pnpm install`、`pnpm web:dev`。
5. 浏览器访问 `http://127.0.0.1:19861/`。

> 端口 `19861`、`Node 22`、`pnpm 9.15.0` 为博文声明（[F-038/F-039](references/facts.md)），官方确认使用 pnpm workspace（monorepo），但具体版本与端口以官方开发文档为准。

## 模型额度提醒

OpenCreator 的模型任务走**你自己配置的服务，额度是你自己的**。有社区测试估算单 Agent 任务约消耗 10~20 万 token（非官方数字，[F-040](references/facts.md)），建议先拿小任务试水、确认额度与成本。

## 相关概念

- [项目身份与定位](00-what-is-opencreator.md)
- [Agent 与 Codex 原生架构](02-agent-and-codex-native.md)
- [实操示例：安装与界面](../examples/index.md)