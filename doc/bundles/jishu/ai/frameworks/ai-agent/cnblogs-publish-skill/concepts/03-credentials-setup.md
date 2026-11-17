---
type: Concept
title: "首次配置：setup 状态机与跨平台对话框"
description: "cnblogs-publish 的 setup 分支（首次、复用、--new-token、--reconfigure、--skip-check）、三平台对话框、鉴权检查与常见失败处置。"
tags: ["cnblogs", "setup", "credentials", "keychain", "troubleshooting"]
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

# 首次配置：setup 状态机与跨平台对话框

`setup` 是唯一写入凭据的命令。它的输入只来自系统对话框或 TTY，不接受命令行值。理解它的分支可以避免"配置成功了但 Agent 还是读不到"的困惑。

## 3.1 先看状态

```bash
python3 scripts/cnblogs.py status --json
```

关注两个字段：

- `credentials_present`：`false` 表示尚未保存凭据。
- `credential_backend`：当前平台选中的后端名（`macos-keychain` / `windows-credential-manager` / `linux-secret-service` / `linux-keyring` / `unavailable`）。

`status` 不输出用户名、博客名、令牌或端点。

## 3.2 setup 的四个分支

| 条件 | 行为 |
|---|---|
| 无凭据 | 依次询问用户名、博客名、令牌，写入系统凭据库 |
| 已有凭据，无额外参数 | 复用现有三项，不重复询问（可做鉴权检查） |
| `--new-token` | 只重新询问令牌，保留用户名与博客名 |
| `--reconfigure` | 重新询问用户名与博客名，并询问令牌 |
| `--skip-check` | 只保存，不调用 `getUsersBlogs` 做鉴权 |

用户名提示明确要求"登录名，不是昵称"；博客名默认取用户名（除非用户名含 `@`），并经过 `validate_blog_name` 校验。令牌输入是隐藏字段，含空白字符会被拒绝。

执行成功后，`setup` 会：

1. 若配置文件不存在，写入 7 键默认配置（不覆盖已有文件）。
2. 若检测到旧 service `cnblogs-metaweblog`（仅 macOS），迁移到 `cnblogs-publish` 并删除旧记录。
3. 除非 `--skip-check`，调用 `blogger.getUsersBlogs`，返回 `auth_ok` 与 `blog_count`。

## 3.3 对话框实现

| 平台 | 实现 | 隐藏令牌 |
|---|---|---|
| macOS | `osascript` + `display dialog` | `with hidden answer` |
| Windows | PowerShell WinForms 窗口 | `UseSystemPasswordChar = true`；提示文本经环境变量传递 |
| Linux | `zenity` → `kdialog` → Tk | `--password` 或 `show="*"` |
| 任意 TTY | `input` / `getpass` | `getpass` 不回显 |

Linux 无图形会话（`DISPLAY`/`WAYLAND_DISPLAY` 为空）时会提示在可交互终端运行同一条命令。Windows 找不到 PowerShell 时直接报错，不会退化为明文输入。

## 3.4 配置文件位置

默认写在 skill 根目录的 `config.json`（与 `SKILL.md` 同级）。若安装目录只读：

```bash
python3 scripts/cnblogs.py --config ~/.config/cnblogs-publish.json setup
```

凭据仍然只进系统凭据库；`--config` 只改变偏好文件位置。该路径也适用于所有后续命令。

## 3.5 鉴权失败怎么排查

| 现象 | 原因 | 处置 |
|---|---|---|
| `code: 3` + "请配置正确的用户名与访问令牌" | 令牌未启用/错误，或用户名写成昵称 | 检查开放 API 设置；`setup --new-token` 或 `--reconfigure` |
| `code: 5` + macOS `100001` | 命令运行在受限沙箱，钥匙串写入被拒 | 用完整访问权限重试，或让用户在终端运行 setup |
| `code: 5` + Linux "未找到可用的安全凭据存储" | 无 `secret-tool` 且无可用 keyring | 安装 `libsecret-tools` 并启动 GNOME Keyring/KWallet，或 `pip install keyring` |
| `code: 5` + Windows 凭据管理器错误 | 远程/服务会话无交互桌面 | 在用户自己的桌面会话运行 setup |
| `status` 显示已保存但 `check` 失败 | 令牌/用户名不匹配 | 返回已脱敏的完整错误，不要改用 curl |

不要向用户索要凭据内容；让他在对话框中重新输入。

## 3.6 撤销与轮换

```bash
# 只删凭据
python3 scripts/cnblogs.py forget

# 凭据 + 配置文件一起删
python3 scripts/cnblogs.py forget --all
```

轮换令牌的标准流程是：后台重置旧令牌 → `setup --new-token` → `check --json`。这样旧令牌立即失效，新令牌不经过对话。

## 相关概念

- [安全模型](/concepts/02-security-model.md)
- [凭据安全设计](/references/security-design.md)
- [CLI 参考](/concepts/06-cli-reference.md)
