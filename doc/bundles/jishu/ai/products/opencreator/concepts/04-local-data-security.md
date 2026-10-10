---
okf_version: "0.2"
type: Concept
title: "数据与安全：本地优先工程纪律"
description: "OpenCreator 的本地数据存放、网络只监听本地、密钥凭据存储与组件更新治理"
tags: [opencreator, local-data, security, privacy, sqlite, yt-dlp]
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator README Local Security"
---

# 数据与安全

OpenCreator 强调**本地优先的安全与隐私纪律**，官方归为「Local Security」：默认数据、附件、日志都留在本机 [F-006](references/facts.md)[F-041](references/facts.md)。

## 本地数据

- 博文声称数据、附件、日志默认全在本机 **`.runtime/`** 目录，用 **SQLite** 存项目、会话与记忆 [F-041](references/facts.md)。
  > ⚠️ `.runtime/` 目录与 SQLite 为博文细节，官方只确认「数据本地」，本包未实测确认（single-source）。
- 模型任务走用户自己配置的服务，额度属用户自己。

## 网络与鉴权

- 本地服务**只监听 127.0.0.1**，不暴露到局域网；除健康检查外每个接口都要 **token** 鉴权 [F-042](references/facts.md)。
  > 与官方 Local Security 叙事一致；「逐接口 token」为博文细节（single-source）。

## 密钥与日志

- 模型密钥走**系统凭据存储**，日志输出前会**脱敏**（redacted diagnostics）[F-043](references/facts.md)。

## 组件更新治理

- `yt-dlp` 等组件会周期性检查更新，但**要你手动确认**才安装；更新失败仍保留当前可用版本供回退 [F-044](references/facts.md)。
- 博文称更新检查周期为 7 天（官方仅言「periodically」，周期为博文细节）。

## 工程纪律可借鉴点

本地优先 + 系统凭据存密钥 + 日志脱敏 + 手动确认更新 + 失败可回退，是一套面向隐私敏感用户的可迁移工程纪律，适用于任何本地优先工具。

## 相关概念

- [项目身份与定位](00-what-is-opencreator.md)
- [安装与快速上手](03-install-quickstart.md)