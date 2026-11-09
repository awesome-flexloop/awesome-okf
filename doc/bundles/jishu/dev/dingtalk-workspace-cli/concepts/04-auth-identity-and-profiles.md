---
okf_version: "0.2"
type: Concept
title: "身份与凭据：三条登录路径与本地凭据资产"
description: "OAuth 浏览器流、设备码、自有应用三种登录方式，多组织账号切换，令牌加密与钥匙串存储，以及跨机迁移的边界"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: readme
    resource: "README.md"
  - id: reference
    resource: "docs/reference.md"
facts: [F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040]
---

# 04 · 身份与凭据

> 核心判断：dws 把登录态当作**本地资产**而非服务端会话——令牌加密落盘、绑定设备、可迁移但有边界，这让它能在 CI、容器、多组织办公机之间安全复用。

## 1. 三条登录路径

| 路径 | 命令 | 适用 |
|------|------|------|
| 浏览器授权 | `dws auth login` | 有图形界面的办公机 |
| 设备码（无头） | `dws auth login --device` | SSH、容器、远程开发机 |
| 自有应用 | `dws auth login --client-id ... --client-secret ...` | 企业自建应用，需独立配额与权限 |

（F-033、F-034）

选择原则：

- 个人使用优先浏览器流，权限最小、体验最好；
- 自动化环境用设备码，避免把浏览器依赖带进流水线；
- 需要企业级配额与审计归属时用自有应用，但 `client-secret` 必须走环境变量（`DWS_CLIENT_SECRET`）而非命令行历史。

## 2. 登录态检查与并发

```bash
dws auth status --readonly --format json
```

（F-035）

- `--readonly` 保证检查动作本身不触发刷新或写盘，多个进程可并发轮询；
- `--format json` 便于脚本判断，配合退出码 3/4/5 区分「未登录」「待交互授权」「权限不足」（F-043）。

## 3. 多组织账号

```bash
dws profile list
dws profile switch <corpId:userId>
dws profile switch -
```

（F-036）

`-` 表示切回上一个账号，适合「主账号查资料、副账号做操作」的来回切换。

注意：`corpId:userId` 是**复合键**，不是邮箱或手机号。首次使用时应先跑 `auth status --format json` 读取当前身份，再决定切换到哪个档案（见 [examples/00](../examples/00-install-and-first-login.md)）。

## 4. 凭据在磁盘上长什么样

| 层 | 机制 | 说明 |
|----|------|------|
| 加密算法 | PBKDF2 派生 + AES-256-GCM | 认证加密，防篡改 |
| 密钥绑定 | 设备特征（如 MAC）参与派生 | 拷贝到另一台机器无法直接解密 |
| 存储后端 | 优先 OS 钥匙串：macOS Keychain / Windows DPAPI | 退化为文件存储时由 `DWS_DISABLE_KEYCHAIN` 控制 |

（F-038、F-040）

**推论**：凭据目录（`DWS_CONFIG_DIR` 指定）不能当普通配置文件随手打包；跨机复制会因设备绑定而失效。正确的迁移方式是导出/导入（第 5 节）。

## 5. 跨机迁移与 Windows 边界

```bash
dws auth export --format tar.gz   # 或 base64
dws auth import <file>
```

（F-037）

| 平台 | 支持情况 |
|------|---------|
| Linux / macOS | 支持导出与导入 |
| Windows | **不支持**导出与导入 |

这是本束记录的最明确的功能缺口。Windows 用户需要在新机器上重新登录，不能依赖迁移包。

钥匙串迁移（F-039）：

```bash
dws auth migrate-keychain --to file-dek
```

该命令可重复执行，用于把凭据从系统钥匙串迁到文件存储（或反向），适合容器化与无钥匙串环境。

## 6. 环境变量清单

| 变量 | 作用 |
|------|------|
| `DWS_CONFIG_DIR` | 覆盖配置与凭据目录 |
| `DWS_CLIENT_ID` / `DWS_CLIENT_SECRET` | 自有应用凭据 |
| `DWS_TRUSTED_DOMAINS` | 扩展出站域名白名单（默认 `*.dingtalk.com`） |
| `DWS_ALLOW_HTTP_ENDPOINTS` | 仅回环地址允许 HTTP，调试用 |
| `DWS_DISABLE_KEYCHAIN` | 禁用系统钥匙串，退化为文件存储 |

（F-040、F-050、F-051）

> **洞察**：把「设备绑定」写进密钥派生，是一次**安全与便利的显式交换**。它挡住了「拷走配置目录就能冒用身份」，代价是备份与迁移必须走官方通道——这也解释了为什么 Windows 的导出缺口值得单独提示。

## 7. 故障判读表

| 现象 | 退出码 | 可能原因 | 处置 |
|------|--------|---------|------|
| 命令直接失败 | 3 | 未登录或令牌失效 | `dws auth login` |
| 提示需要交互授权 | 4 | 设备码未完成确认 | 打开提示链接完成授权 |
| 接口返回无权限 | 5 | 应用缺少 scope | 到开放平台补权限或换账号 |
| 频繁失败 | 6 | 限流或服务端异常 | 退避重试，检查配额 |

（F-043）

## 延伸

- 输出与错误结构：[05-output-and-schema-discovery.md](05-output-and-schema-discovery.md)
- 安全默认：[06-safety-dry-run-and-audit.md](06-safety-dry-run-and-audit.md)
- 实践：[examples/00-install-and-first-login.md](../examples/00-install-and-first-login.md)