---
type: Concept
title: "凭证安全内部机制：OAuth 设备码流与三平台密钥托管"
description: "源码视角的认证与存储：cli-oauth-init/poll/refresh 设备码时序、UserConfig/AppMeta/AgentConfig 三文件、macOS Keychain/Linux 0600 文件/Windows DPAPI 三平台密钥托管、AES-256-GCM 与 AAD 绑定、原子写/filelock/filecheck、资源释放钩子。"
tags: [tencent-meeting, tmeet, source-code, oauth, keychain, aes-gcm, dpapi, security, credentials]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: source-code
    resource: /references/source-code.md
    title: tencentmeeting-cli 源码主体（tag v1.0.18 @ e631b35）
  - id: github-readme
    resource: /references/github-readme.md
    title: GitHub README（main 分支）
  - id: cloud-doc
    resource: /references/cloud-doc.md
    title: 腾讯云文档《腾讯会议 CLI 说明》
---

# 凭证安全内部机制

> 用户面知识（怎么登录、凭证加密、登出）见 [01 - 安装与 OAuth2 授权](01-install-auth.md)。本文讲源码侧的 How/Why，并对官方文档「存入系统 Keychain」的说法给出**按平台区分的准确口径**。

## OAuth 设备码流：三个 endpoint 的时序

授权全程走 CGI 主机 `work.medialab.qq.com`（F-138、F-139）：

```
tmeet auth login
  ① POST /v2/oauth2/oauth/cli-oauth-init
       body: { device_id: <MachineID> }
     ← AuthCodeData.auth_code
  ② 浏览器打开（或 --no-browser 仅打印）：
       https://meeting.tencent.com/marketplace/tencentmeeting-cli-auth.html?code=<auth_code>
       （三平台 open / rundll32 / xdg-open，F-146）
  ③ 每 5s 轮询 POST /v2/oauth2/oauth/cli-oauth-poll
       总超时 5 分钟（authorizationTimeout）
     ← AuthTokenData（6 字段，F-140）
  ④ 后续过期前自动刷新：
       POST /v2/oauth2/oauth/cli-refresh-token
       过期判断预留 60s leeway
```

- AuthTokenData 6 字段：access_token、refresh_token、access_token_expire_time、refresh_token_expire_time、open_id、sdk_id（F-140）。
- 5s × 300s 正好对应用户面的「阻塞最多 300s、必须前台运行」（F-023）。
- 整个登录写盘过程包在 `filelock.WithLock(token.lock)` 中；已登录再登录返回 UserHasBeenInitializedError（用户面文案 `user has been initialized`）（F-141）。

设备指纹来自配置目录的 `.machine_id`：48 字符随机串，O_EXCL 首写者胜；设备唯一 ID 为 `<openId>*<machineId>`（F-147），即请求头 Tmeet-Unique-ID。

## 磁盘上到底有什么：三份配置，而非「一个 Config」

源码中不存在统一 Config 类型（F-142）：

| 文件/载体 | 内容 | 是否敏感 |
|------|------|----------|
| `<config>/config.json` | AppMeta：仅 `active_open_id`，用于定位当前账号的密文（macOS/Linux 为 `.enc` 文件，Windows 为注册表值） | 否（明文） |
| `<config>/agent.json` | AgentConfig：TMEET_AGENT/TMEET_MODEL 标识 | 否（明文） |
| `<dataDir>/<open_id>.enc`（macOS/Linux）；注册表值 `HKCU\Software\TmeetCli\keychain\<open_id>`（Windows） | UserConfig 加密体：sdk_id/open_id/access_token/refresh_token + 过期时间 | **是** |

目录解析（F-143）：`TMEET_CLI_CONFIG_DIR` 默认 `~/.tmeet`；`TMEET_CLI_DATA_DIR` 默认值按平台为 macOS `~/Library/Application Support/tmeet`、Windows `%LOCALAPPDATA%\tmeet`、Linux `~/.local/share/tmeet`。配置注释明确「plaintext is never persisted to disk」（F-155）。

写入全部走原子写：同目录临时文件 → Sync → Rename；目录权限 0700（F-144）。

## 三平台密钥托管：「系统 Keychain」只在 macOS 字面上成立

这是对用户面 F-025/F-107（「凭证存入系统 Keychain，与设备绑定」）最重要的口径深化（F-149）。常量 ServiceName=`"tmeet"`、MasterKeyAccount=`"master.key"`。

```
                    ┌─ macOS：主密钥 → 系统 Keychain（go-keyring）
随机 32B 主密钥 ───┼─ Linux：主密钥 → ~/.local/share/tmeet/master.key（权限 0600，umask 0077）
                    └─ Windows：主密钥 → 注册表 HKCU\Software\TmeetCli\keychain（DPAPI 保护）

业务数据（加密原语三平台一致，存储载体分叉）：
  UserConfig JSON → AES-256-GCM（AAD=open_id）
    ├─ macOS/Linux：写 <dataDir>/<open_id>.enc 文件
    └─ Windows：base64 后写注册表值 HKCU\Software\TmeetCli\keychain\<open_id>（不落 .enc 文件）
```

> DPAPI（Windows Data Protection API，Windows 数据保护 API）是操作系统提供的按用户/机器绑定的加密接口。注意源码包注释存在历史泛化措辞（keychain.go 头注释/config.go 注释统称 `.enc`），平台注释与各平台 `Get/Set` 实现才是权威：Windows 业务数据全程无文件操作（F-149）。

| 平台 | 主密钥托管 | 业务数据载体 | 拷贝到别的机器能否解密 |
|------|-----------|----------|------------------------|
| macOS | 系统 Keychain（绑定登录态） | `<open_id>.enc` 文件 | 不能（官方口径在此成立） |
| Linux | **0600 文件，无系统 keyring** | `<open_id>.enc` 文件 | 拿到 `.enc` + `master.key` 即可 |
| Windows | 注册表 + DPAPI（仅主密钥，绑定用户/机器） | **同一注册表键下以 open_id 命名的值**（AES-GCM base64，非 DPAPI、非文件） | 不能 |

含义有两面：①Linux 上安全强度等价于「0600 + 用户隔离」，root/同权限进程可读，运维侧应自行补偿（全盘加密、限制主目录、避免多用户同机）；②三平台**加密原语统一**（同一套 AES-256-GCM + AAD 代码），但**存储后端分叉**（macOS/Linux 文件后端 vs Windows 注册表后端，各有平台专属 Get/Set/Remove 实现）。

## 加密原语与防搬运设计

- **算法**：AES-256-GCM（KDF 即密钥派生函数）；主密钥为 32 字节随机数，**无 KDF、无口令派生**；nonce 12 字节；字节布局 `nonce || ciphertext || tag`——macOS/Linux 即 `.enc` 文件布局，Windows 为注册表值解码后的字节布局（F-150）。
- **AAD 绑定**：GCM 附加认证数据使用 account（open_id 字节），把密文绑定到账号——把甲的 `.enc` 改名替换乙的文件（Windows 下为改写他人的注册表值）会在认证阶段失败（代码注释 SEC-009）（F-151）。
- **迁移降级**：`decryptWithAADFallback` 先以 account 作 AAD 解密，失败再以 nil AAD 解密一次，用于自动迁移 AAD 机制上线前的历史密文（F-151）。这是一条有意保留的兼容降级路径，安全评估时应知晓。
- **Windows DPAPI 细节**：entropy 为 `service + "\x00" + account`；仅当主密钥解密命中 NTE_BAD_KEY_STATE(0x8009000B)/ERROR_INVALID_DATA(0xD)/NTE_BAD_DATA(0x80090005) 三个错误码、且新旧 entropy 两次尝试均失败时，才 purge 整个注册表键并重新生成（F-152）——不是任何读取失败都自愈。

## 文件安全原语三件套

| 原语 | unix | windows | 事实 |
|------|------|---------|------|
| filelock | flock(LOCK_EX\|LOCK_NB) | LockFileEx；50ms 轮询、5s 超时 | F-153 |
| filecheck | 读敏感文件前拒绝符号链接、非常规文件、非属主文件 | no-op（走注册表，注释 SEC-010） | F-154 |
| 原子写 | tmp + Sync + Rename；目录 0700 | 同 | F-144 |

## 登出：先释放资源，后删凭证

v1.0.18 的两阶段清理（用户面 F-032）实现为 ResourceReleaseHook 链（F-145）：

1. 按注册顺序执行、fail-fast；单个 hook 的 panic 被 recover 转成 error；
2. 任一 hook 失败 → **保留 keychain 条目与 active_open_id**，允许重试；
3. 全部成功 → 才删业务密文（macOS/Linux 的 `.enc` 文件；Windows 的注册表值）/Keychain 主密钥项与 active_open_id。

首个注册的 hook 是事件总线 `cleanup.OnUserCleared`：owner hash 匹配才动作，先发 Shutdown 等 3s，进程仍活则 SIGKILL/TerminateProcess，再清理 sock/meta/pid（F-183）。总线在鉴权失败场景另有 `ClearUserConfigUnResource` 旁路，不跑 hook（F-145）。

此外 panic 恢复后走 `/v1/cli/crash` 上报且**不产生 coredump 文件**（F-192），避免栈/内存映像在磁盘上泄露敏感片段。

## 排障与运维清单

| 现象/需求 | 按源码的正确动作 |
|-----------|------------------|
| 怀疑凭证损坏 | 核对 config.json 的 active_open_id → 业务密文（macOS/Linux：对应 `<open_id>.enc`；Windows：注册表 `HKCU\Software\TmeetCli\keychain` 下同名值）→ 主密钥（Keychain/master.key/注册表 DPAPI 项）三处是否齐备 |
| 重复登录报错 | 先 `auth logout`（会跑资源释放 hook）；`user has been initialized` 不是网络错误 |
| Linux 备份/迁移机器 | 须知 `.enc` + `master.key` 同时可迁移即可读；不要把这两个文件打入镜像/归档；Windows 注册表项因 DPAPI 绑定不可随机器迁移 |
| 多用户共用主机 | Linux/Windows 均非强 OS 隔离设计，建议每用户独立系统账户运行 CLI |
| 疑似泄露 | `auth logout` + 腾讯会议账号安全中心吊销授权（F-031） |

## 相关概念

- [01 - 安装与 OAuth2 授权](01-install-auth.md)（登录操作与用户面安全建议）
- [06 - Agent 安全契约](06-agent-safety-contract.md)（Skill 层的行为红线）
- [12 - 事件总线内核](12-event-bus-internals.md)（logout hook 如何停 bus）｜[09 - 源码工程总览](09-codebase-architecture.md)

## 延伸阅读

- 信源登记：[references/source-code.md](../references/source-code.md)（含与 F-025/F-107 的口径差异表）
- 核心洞察：[洞察七 · 主密钥分层托管的平台自适应体系](../spec/insights.md)
