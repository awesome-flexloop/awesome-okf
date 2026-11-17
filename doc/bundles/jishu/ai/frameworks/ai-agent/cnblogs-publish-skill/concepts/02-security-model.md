---
type: Concept
title: "安全模型：把凭据排除在 Agent 通道之外"
description: "cnblogs-publish 的凭据资产、威胁模型、存储/输入/输出三层控制、HTTPS 与博客名校验，以及五条对 Agent 的硬性禁止事项。"
tags: ["cnblogs", "security", "credentials", "redaction", "threat-model"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/security-design.md"
    type: "repository-docs"
    trust: high
---

# 安全模型：把凭据排除在 Agent 通道之外

该 skill 把**用户名、博客名、访问令牌**统一视为私密凭据。安全目标不是"提醒模型小心"，而是让这些值在结构上不进入对话、命令行、stdin、环境变量、配置文件和日志。

## 2.1 资产与信任边界

| 资产 | 敏感度 | 存放位置 |
|---|---|---|
| 登录用户名 | 高 | 系统凭据库 |
| 博客名 | 中（会出现在公开文章 URL） | 系统凭据库 |
| 访问令牌 | 最高 | 系统凭据库 |
| 偏好配置 | 低 | `config.json`（7 键，无身份信息） |
| 文章正文 | 由用户决定 | 本地 Markdown → 博客园 |

信任边界在**脚本进程**：凭据只在进程内存中展开，磁盘上是操作系统加密存储，进程外只能看到脱敏输出。

## 2.2 三层控制

### 存储层

- 单一加密记录：service `cnblogs-publish`，account `credentials`。
- macOS Keychain / Windows Credential Manager（DPAPI）/ Linux Secret Service 或 keyring。
- Linux 无安全后端时返回退出码 5，不回退明文。
- `config.json` 只有 7 个偏好键；权限尝试 `0600`；写入用临时文件 + `os.replace`。

### 输入层

- `setup` 只通过原生对话框收集，令牌使用隐藏输入。
- 脚本**拒绝**从命令行参数、stdin、环境变量接收凭据值。
- `--new-token` / `--reconfigure` 只是触发重新弹框，不接受值本身。
- `ask_secret` 拒绝空值与含空白字符的令牌（常见于复制不完整）。

### 输出层

- 令牌注册进进程内 `_SECRETS`，所有文本替换为 `***`。
- `Reporter.emit` 对 JSON/human payload 递归脱敏。
- `_scrub_identity` 额外屏蔽用户名、博客名、邮箱、`.../metaweblog/...` URL。
- `status` 只报告是否已保存与后端名称；`check` 只报告 `ok` 与 `blog_count`。
- 不提供 `--debug`/`--verbose` dump 请求体。

## 2.3 网络与输入校验

- `validate_endpoint` 只允许 `https://`；`http://` 仅放行 `127.0.0.1`、`localhost`、`::1`。
- `validate_blog_name` 拒绝含 `@`、`/`、`:`、空白或以 `.` 开头的值，避免把邮箱/昵称/完整网址误当博客名。
- 令牌加载时校验不含空白字符；凭据 JSON 缺字段或损坏时要求重新 `setup --new-token`。

## 2.4 凭据泄露后的行为

| 场景 | 正确处置 |
|---|---|
| 用户已在聊天中贴出令牌 | 提醒立即到博客园后台重置，并运行 `setup --new-token` |
| 怀疑博客名/用户名泄露 | 检查博客是否有异常文章或设置变更，必要时 `setup --reconfigure` |
| 换机器/换解释器 | 重新 `setup`；系统可能弹出一次"允许访问凭据"确认，但不显示内容 |
| 需要清除 | `forget`（可加 `--all` 同时删除配置文件） |

## 2.5 对 Agent 的五条硬性禁止事项

1. 绝不要让用户在聊天里提供用户名、博客名或令牌。
2. 绝不运行 `security find-generic-password ... -w`、`secret-tool lookup ...`、`echo $CNBLOGS_TOKEN` 等会打印凭据的命令。
3. 绝不用 `curl`/`wget` 直接调用 MetaWeblog（凭据会进入命令行与历史）。
4. 不要把凭据写进 Markdown、配置、环境变量或临时文件。
5. 用户若已泄露令牌，提醒重置并运行 `setup --new-token`。

## 2.6 按设计会出现的"泄露"

发布结果中的文章 URL 含**公开博客名**：`https://www.cnblogs.com/<博客名>/p/<id>`。这是交付给用户的公开链接本身，不包含用户名或令牌。除该 URL 外，成功/失败输出都不应出现身份字段。

## 2.7 可验证的安全不变量

- `publish --json` 输出中不含令牌（测试 `test_publish_json_never_contains_token`）。
- 错误输出中的令牌被替换（`test_error_output_redacts_token`）。
- `config.json` 不含凭据（`test_default_config_has_no_credentials`）。
- Linux `secret-tool` 的 secret 走 stdin 而非 argv（`test_linux_secret_tool_roundtrip_uses_stdin`）。
- `status` 输出不含身份（`test_status_never_reads_credentials`）。

这些不变量比功能覆盖更能代表该 skill 的安全质量，详见[跨平台与测试](/concepts/07-cross-platform-and-tests.md)。

## 相关概念

- [首次配置](/concepts/03-credentials-setup.md)
- [凭据安全设计](/references/security-design.md)
- [可见性与审核](/concepts/05-visibility-and-review.md)
