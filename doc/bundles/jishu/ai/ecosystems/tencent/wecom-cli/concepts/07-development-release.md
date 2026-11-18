---
type: concept
title: 开发与发布：门禁、文档和 e2e
description: 说明 wecom-cli 从 Cargo 与 pnpm 脚本到 changeset、多平台发布及 e2e 组织的工程链路。
tags: [wecom, wecom-cli, development, release, testing]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 开发与发布：门禁、文档和 e2e

仓库同时使用 Cargo workspace 与 pnpm workspace。脚本提供 check、fmt、lint、test、skip-auth-check 测试和 doctest 等入口，Node 要求为 >=18，包管理器固定为 pnpm 12.3.4（F-012–F-014）。

## 代码门禁

release profile 开启 strip、LTO 与单 codegen unit；rustfmt 固定 edition 2024、宽度 100 和 4 空格；commitlint 允许 12 类 type，并限制 subject 100 字符、header 120 字符（F-023–F-026）。pre-commit 串行执行 rustfmt、clippy 和暂存 JavaScript/TypeScript 的 eslint；commit-msg 执行 commitlint；pre-push 并行执行 test 与 check（F-027–F-030）。

## 发布结构

changeset 将 CLI 与 5 个平台包固定为同版本发布，发布访问级别为 public，基线分支为 main（F-018–F-021）。平台包覆盖 macOS、Linux 和 Windows 的五种架构组合，入口脚本根据平台选择二进制名称并透传退出码（F-015–F-017、F-019）。

## 文档与测试

仓库 docs 现有 9 个 Markdown 文件，包含 CLI、Skills、数据采集、开发和 e2e 规范入口（F-155–F-161）。e2e 用例采用 `cases/<group>/<NNN>-<slug>/{desc.md,test.rs}`，wecom 层有 9 组 56 个用例目录，wecom-cli 层有 6 组 19 个用例目录（F-166–F-169）。根目录无 tests 目录，单元测试以内嵌 `#[cfg(test)]` 组织（F-170）。
