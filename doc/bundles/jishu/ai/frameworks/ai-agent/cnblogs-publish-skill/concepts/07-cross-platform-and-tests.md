---
type: Concept
title: "跨平台与测试：三平台后端与 50 项不变量"
description: "cnblogs-publish 在 macOS/Windows/Linux 的凭据后端与对话框差异，以及 15 个测试类、50 个测试方法覆盖的安全与流程不变量。"
tags: ["cnblogs", "cross-platform", "testing", "keychain", "credential-manager", "secret-service"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
---

# 跨平台与测试：三平台后端与 50 项不变量

该 skill 用同一套命令覆盖 macOS、Windows、Linux；差异被压缩到 `secretstore.py`（凭据后端）与 `dialogs.py`（输入对话框）两个模块。

## 7.1 平台能力矩阵

| 能力 | macOS | Windows | Linux |
|---|---|---|---|
| 凭据后端 | 登录钥匙串 | Credential Manager（DPAPI） | `secret-tool` 或 `keyring` |
| 后端名 | `macos-keychain` | `windows-credential-manager` | `linux-secret-service` / `linux-keyring` |
| 对话框 | `osascript` | PowerShell WinForms | `zenity` / `kdialog` / Tk |
| 隐藏令牌 | `hidden answer` | `UseSystemPasswordChar` | `--password` / `show="*"` |
| 额外依赖 | 无 | Python 3 + PowerShell | `libsecret-tools` 或 `keyring`；图形对话框建议 `zenity` |
| 已知限制 | 沙箱写钥匙串可能被拒（100001） | 远程/服务会话可能无 Credential Manager | 需要 D-Bus session 与已解锁 keyring |

## 7.2 四个后端

| 后端 | 实现要点 |
|---|---|
| `_MacKeychain` | ctypes 直调 `Security.framework`；错误码 100001/-25308/-25299 有专门提示 |
| `_WindowsCredentialManager` | ctypes 定义 `CREDENTIALW`；target `cnblogs-publish:credentials`；`CredReadW/WriteW/DeleteW` |
| `_LinuxSecretTool` | 子进程调用 `secret-tool store/lookup/clear`；secret 走 **stdin** |
| `_LinuxKeyring` | Python `keyring`；检测到 plaintext 后端时拒绝 |

Linux 选择顺序：优先 `secret-tool`；否则 `keyring`；都不可用则报错退出 5。

## 7.3 测试规模与分布

| 指标 | 值 |
|---|---|
| 测试文件 | `tests/test_local.py`（798 行） |
| 测试类 | 15 |
| 测试方法 | 50 |
| 本机实测 | `Ran 50 tests ... OK (skipped=1)` |
| 跳过项 | `test_linux_secret_tool_real_subprocess`（Windows 无 POSIX shell helper） |

测试类覆盖：

| 测试类 | 关注点 |
|---|---|
| `MarkdownTests` | 基础转换、HTML 转义、链接与图片 |
| `FrontmatterTests` | frontmatter 解析、H1 标题提取 |
| `DraftTests` | `--draft`/`--private` 与非公开语义 |
| `PrepareTests` | `[Markdown]` 增删、图片替换、AI 声明、分类 warning |
| `CredentialStorageTests` | 凭据往返、config 无凭据、旧 service 迁移、后端缺失 |
| `PostUrlTests` | 无后缀 URL 回退、服务端 link 保留 |
| `PublishFlowTests` | JSON 无令牌、默认非公开、错误脱敏 |
| `UpdateFlowTests` | 默认非公开、元数据保留与 `[Markdown]` |
| `RpcIntegrationTests` | XML-RPC 往返、非回环 HTTP 拒绝 |
| `SecurityScrubTests` | 凭据/邮箱/URL 脱敏、博客名校验 |
| `CheckOutputTests` | `check` 输出不含身份 |
| `SecretStoreTests` | 四后端选择、Windows target、secret 走 stdin |
| `WindowsCredentialManagerTests` | 写入/删除/读取不存在项 |
| `DialogTests` | 三平台对话框命令构造、空白令牌拒绝、平台路由 |
| `StatusTests` | `status` 输出不含身份 |

## 7.4 测试能证明什么、不能证明什么

能证明：

- 业务流程与安全不变量（默认非公开、输出脱敏、凭据不落 config）。
- 平台路由逻辑与命令构造（通过 mock `sys.platform`、mock `ctypes.WinDLL`、临时假 `secret-tool`）。

不能证明：

- 真实 Windows DPAPI / Credential Manager 的行为。
- 真实 Linux Secret Service / keyring 的可用性。
- 真实博客园账号的发布与审核结果。

因此 `tests/README.md` 要求在真实 macOS/Windows/Linux 上各跑一遍冒烟：`setup` → `status` → `check` → `publish --draft`。

## 7.5 运行方式

```bash
python -m unittest discover -s tests -v
```

在 Windows 上会跳过 POSIX 专用用例；这是环境限制，不是失败。

## 7.6 对新平台移植的启示

新增平台只需实现 `secretstore` 的 get/set/delete 与 `dialogs` 的输入函数，并补平台路由测试；业务流程、frontmatter、图片与 RPC 不需要改动。这种"薄平台层"是该项目可移植性的来源。

## 相关概念

- [架构设计](/concepts/01-architecture.md)
- [安全模型](/concepts/02-security-model.md)
- [源码登记](/references/source-code.md)
