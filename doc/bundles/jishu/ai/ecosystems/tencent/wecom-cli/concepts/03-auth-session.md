---
type: concept
title: 认证与会话：授权来源、加密凭据与静默刷新
description: 说明 wecom-cli 的环境变量、加密文件、扫码授权与 853004 静默刷新链路。
tags: [wecom, wecom-cli, auth, session]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 认证与会话：授权来源、加密凭据与静默刷新

wecom-cli 同时支持持久凭据与无状态环境变量。凭据文件位于默认 home 下的 `credentials.enc`，写入权限为 `0600`，内容使用 AES-256-GCM；密钥文件为 `.encryption_key`，读取顺序是文件优先、keyring 兜底（F-077–F-085）。

## 授权来源

解析顺序是：非空 `WECOM_CLI_ACCESS_TOKEN` 优先，否则读取 `credentials.enc`；文件中只有 bot 而没有 token 时，解析结果没有 token（F-091）。配置目录可以由 `WECOM_CLI_CONFIG_DIR` 改道，空值视为未设置（F-094、F-095）。

## 首次授权

扫码流程每 3 秒轮询，最长 300 秒；引导签名采用 `sha256(secret + bot_id + time + nonce)`，换取 token 的端点使用 `SuppressAuth`，因此该请求不携带 Authorization（F-086–F-090）。`auth init --manual` 与 `--noninteractive` 互斥；非 TTY 下手动模式返回错误，手动模式会忽略 `--output-qrcode`（F-096–F-098）。

## 过期刷新

后端将 853004 视为 token 过期，调用会话刷新并重放原请求；刷新失败时返回原始错误（F-092、F-093）。`auth show --status` 只输出 authorized 或 unauthorized，不区分环境变量和文件来源（F-100）。

## 操作要点

- 自动化环境可使用环境变量来源，但排障时必须同时检查环境变量与凭据文件，因为状态命令不暴露来源（F-091、F-100）。
- 需要迁移旧凭据时，程序只在缺少 `credentials.enc` 且存在 `bot.enc` 的条件下尝试迁移（F-099）。
