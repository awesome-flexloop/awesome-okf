---
type: Reference
title: "凭据安全设计"
description: "cnblogs-publish 的凭据资产、四种系统凭据后端、配置文件边界、原生对话框输入路径、统一脱敏与平台差异的完整登记。"
tags: ["cnblogs", "security", "credential", "keychain", "dpapi", "secret-service"]
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

# 凭据安全设计

本文件整理 `references/security.md` 与 `scripts/secretstore.py`、`scripts/dialogs.py`、`scripts/cnblogs.py` 的实现事实。目标是把用户名、博客名、访问令牌排除在明文文件、对话、命令行参数、stdin、环境变量和日志之外。

## 凭据资产与存储位置

| 项 | 值 |
|---|---|
| Service | `cnblogs-publish` |
| Account | `credentials` |
| 值 | 一条 JSON：`{"username","blog","token","endpoint"}` |
| 旧 service | `cnblogs-metaweblog`（仅 macOS 读取迁移，迁移后删除） |
| 读写入口 | `cnblogs.py` → `secretstore.py` |

## 四种后端

| 平台 | 后端名 | 实现 | 关键细节 |
|---|---|---|---|
| macOS | `macos-keychain` | `Security.framework` ctypes | `SecKeychainAddGenericPassword` / `FindGenericPassword` / `ItemDelete`；100001 表示沙箱拒绝写入 |
| Windows | `windows-credential-manager` | `advapi32` ctypes | `CredReadW` / `CredWriteW` / `CredDeleteW`；target 为 `cnblogs-publish:credentials`；DPAPI 加密 |
| Linux | `linux-secret-service` | `secret-tool` 子进程 | secret 通过 **stdin** 传入，不进入 argv；`store` / `lookup` / `clear` |
| Linux | `linux-keyring` | Python `keyring` | 检测到 plaintext 后端时拒绝使用 |

Linux 没有 Secret Service/keyring 时返回退出码 5 与安装提示，绝不退化为明文文件。

## 配置文件边界

`config.json` 只保存 7 个偏好键，权限尝试设为 `0600`，写入采用「临时文件 + `os.replace`」：

| 键 | 默认值 |
|---|---|
| `blogid` | `cnblogs` |
| `markdown_category` | `[Markdown]` |
| `format` | `markdown` |
| `upload_images` | `true` |
| `validate_categories` | `true` |
| `ai_generated` | `true` |
| `timeout` | `30` |

配置中不存在 `username`、`blog`、`token`、`password`、`endpoint`。

## 输入路径

`setup` 在非交互环境依次弹出 3 个原生输入框：登录用户名（可见）、博客名（可见）、访问令牌（隐藏）。脚本拒绝从命令行、stdin 或环境变量接收凭据值。

| 平台 | 对话框实现 |
|---|---|
| macOS | `osascript` + `display dialog ... with hidden answer` |
| Windows | PowerShell WinForms；令牌框 `UseSystemPasswordChar`；提示文本经环境变量传递，不进命令行 |
| Linux | `zenity` / `kdialog` / Tk；无图形会话时退化为终端 `input` / `getpass` |
| 任意 TTY | 直接 `input` / `getpass`，不回显 |

`ask_secret` 还拒绝空值和含空白字符的令牌（常见于复制不完整）。

## 输出脱敏

- 令牌读入后注册进进程内 `_SECRETS`；`redact()` 把令牌替换为 `***`。
- `Reporter.emit` 对 JSON/human payload 递归执行 `redact_obj`。
- `_fail` 用 `_scrub_identity` 再屏蔽用户名、博客名、邮箱和 `.../metaweblog/...` URL。
- `status` 报告「已保存/未保存」与后端名称；`check` 只报告 `ok` 与 `blog_count`。
- XML-RPC 请求体从不打印，也没有 `--debug`/`--verbose` dump 开关。
- 唯一包含博客名的输出是发布结果的公开文章 URL。

## 威胁对照

| 通道 | 风险 | 该实现 |
|---|---|---|
| 明文 `config.json` / `.env` | 任意读取 | 不存凭据 |
| 环境变量 | `env`、崩溃日志、子进程继承 | 不接受凭据 |
| 命令行参数 / `curl` | shell 历史、`ps` | 只走脚本内部 XML-RPC |
| 聊天输入 | 进入模型上下文，不可撤回 | 原生对话框 |
| 错误信息 | 回显令牌/邮箱/URL | 双层脱敏 |

## 平台注意事项

- macOS：`workspace-write` 沙箱通常允许读钥匙串但拒绝写（OSStatus 100001）；`setup`/`forget`/`--new-token` 可能需要完整访问权限，日常 `publish` 只读。
- Windows：Credential Manager 在普通用户会话可用；远程/服务会话可能不可用，应在桌面会话运行 setup。
- Linux：依赖运行中的 D-Bus session 与已解锁 keyring；headless 环境需先启动/解锁。

## 泄露处置

1. 立即在博客园后台重置/删除旧令牌。
2. 运行 `setup --new-token`，在系统对话框中录入新令牌。
3. 若用户名/博客名曾出现在聊天或截图，检查博客是否有异常变更，必要时 `setup --reconfigure`。

## 相关文档

- [安全模型](/concepts/02-security-model.md)
- [首次配置](/concepts/03-credentials-setup.md)
- [源码登记](/references/source-code.md)
