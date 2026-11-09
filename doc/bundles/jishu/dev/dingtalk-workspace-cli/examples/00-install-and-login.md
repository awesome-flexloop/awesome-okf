---
okf_version: "0.2"
type: Example
title: "演练：安装 dws 并完成首次登录"
description: "从选择安装渠道到确认身份的完整演练——四类安装法、三条登录路径、登录态只读检查、多组织切换与失败判读"
---

# 00 · 演练：安装 dws 并完成首次登录

> **性质**：以下命令逐字取自仓库 `README.md`（F-070 ~ F-078），**未在本机实跑**。安装器行为以实际版本为准；涉及企业权限的步骤需管理员配合。
> 相关概念：[00 定位与全景](../concepts/00-overview-and-positioning.md)、[04 认证、身份与多组织](../concepts/04-auth-identity-and-profiles.md)。

## 目标与完成标准

跑完本章应达到三个可观察结果：

1. `dws version` 能输出版本号（说明二进制已在 `PATH` 中）；
2. `dws auth status --readonly --format json` 中 `authenticated` 为 `true`；
3. `dws profile list` 能看到至少一个以 `corpId:userId` 标识的账号。

## 步骤 1：选择安装渠道

| 渠道 | 命令 | 适用场景 | 事实 |
|------|------|---------|------|
| 安装脚本（macOS/Linux） | `curl -fsSL https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.sh \| sh` | 个人开发机，最快 | F-070 |
| 安装脚本（Windows） | `irm https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.ps1 \| iex` | Windows 原生 PowerShell | F-070 |
| npm | `npm install -g dingtalk-workspace-cli` | 已有 Node.js 工具链 | F-070 |
| Homebrew | `brew tap DingTalk-Real-AI/dingtalk-workspace-cli https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli.git` 后 `brew install dingtalk-workspace-cli` | macOS/Linux，要求包管理器统一升级 | F-070 |
| 预编译二进制 | 从 GitHub Releases 下载当前平台归档 | 离线或受控分发 | F-070 |
| 源码构建 | `git clone` → `go build -o dws ./cmd` | 需要改代码或审计构建 | F-070、F-072 |

四条选择纪律：

- **Alpine 等 musl 发行版不要用脚本安装**：Linux 二进制链接 glibc（基线 2.17），安装器检测到 musl 会直接停止（F-071）。
- **源码构建默认需要 C 编译器**：默认 CGO 构建包含 SafeChat 后端（F-072）；只有明确要桩构建时才设 `CGO_ENABLED=0`。
- **中国大陆网络**：脚本可加 `DWS_GITEE_REPO=DingTalk-Real-AI/dingtalk-workspace-cli` 走 Gitee 镜像（F-070）。
- **只要 CLI、不要技能**：npm 安装前设 `DWS_NO_SKILLS=1`（F-074）。

> 安装器会顺带安装 Agent Skills，默认布局为 `multi`（按产品拆分）。非交互式一行命令安装默认 `multi`；想选 `mono` 可用 `DWS_SKILL_MODE=mono`，或安装后执行 `dws skill setup --mode mono`（F-073）。两种模式下 CLI 命令完全相同。

## 步骤 2：验证二进制

```bash
dws version
dws --help
```

`dws version` 输出版本号即说明安装成功。若提示找不到命令，检查安装目录是否在 `PATH` 中——脚本安装通常写入用户级可执行目录，需要重开终端。

## 步骤 3：登录（三选一）

### 路径 A：浏览器登录（默认）

```bash
dws auth login
```

浏览器自动打开，选择组织并授权。若组织尚未启用 CLI 访问，会提示向管理员发起申请；管理员在 [开放平台](https://open-dev.dingtalk.com) 的「CLI Access Management」启用后重新登录即可（F-078）。

### 路径 B：设备码登录（无浏览器环境）

```bash
dws auth login --device
```

适用于 Docker、SSH 远程机、CI 等无图形界面的环境。按终端提示在另一台设备上完成授权。

### 路径 C：自有应用登录（CI/CD、ISV）

先在开放平台创建应用，并在安全设置中加入重定向 URL：

```text
http://127.0.0.1,https://login.dingtalk.com
```

发布应用后登录（F-078）：

```bash
dws auth login --client-id <your-app-key> --client-secret <your-app-secret>
```

凭据首次登录后持久化到系统钥匙串，后续自动刷新。

## 步骤 4：确认身份（只读检查）

自动化场景不要用会刷新令牌的 `auth status`，改用只读快照（F-033 ~ F-040）：

```bash
dws auth status --readonly --format json
dws profile list
```

判读要点：

| 字段/现象 | 含义 | 下一步 |
|-----------|------|--------|
| `authenticated: true` | 访问令牌或刷新令牌至少一项有效 | 可以执行业务命令 |
| `token_valid: false` 但 `authenticated: true` | 访问令牌过期，刷新令牌仍有效 | 正常运行即可，业务命令会自动刷新 |
| `reason` 非空且为 `local_state_requires_repair` | 本地凭据需要迁移或修复 | 用同一 profile 执行非只读的 `dws auth status` |
| `reason` 为 `local_state_unreadable` | 本地状态读取失败 | 不要当作「已登出」，先修复本地状态 |
| 只读模式报令牌过期 | 只读模式从不刷新 | 以正常模式的结论为准 |

> **纪律**：只读结果带非空 `reason` 时属于「不确定」，**不得**据此判定用户已登出。

## 步骤 5：多组织切换

一个 `dws` 可同时保持多个组织、多个账号的登录态，profile 以 `corpId:userId` 唯一标识（F-076、F-077）。

```bash
dws profile list                            # 列出全部已登录账号
dws profile switch <corpId:userId>          # 持久切换；用 - 切回上一个
dws profile switch "<corpName>:<userName>"  # 友好名输入，要求名称唯一
dws --profile <corpId> contact user search --query "engineering"
dws --profile <corpId:userId> contact user search --query "engineering"
```

三条边界：

- `--profile <corpId>` 使用该组织**已显式记录**的当前账号；若该组织有多个账号却没有记录，命令失败而不是替你挑一个（F-076）。
- 友好名只是输入别名；自动化脚本应使用 `profile list` 返回的稳定 `profile` 值。
- 跨组织读取没有 `--all-orgs` 开关，需由 Agent 编排：列 profile → 按 `corpId` 分组 → 取每组唯一 `isOrgCurrent=true` 的账号（F-077）。

退出登录时注意粒度：

```bash
dws auth logout --profile <corpId:userId>   # 只删一个账号
dws auth logout --profile <corpId>          # 删除该组织全部本地账号
```

## 步骤 6：安装 Agent Skills（可选）

```bash
npx skills add DingTalk-Real-AI/dingtalk-workspace-cli -g
```

或使用带归属管理与 Gitee 回退的官方路径：

```bash
dws skill setup                                   # 交互式选择模式与目标，先预览计划再确认
dws skill setup --mode multi --target cursor
dws skill setup --mode mono --target all
```

`--target` 支持 `all`、`claude`、`cursor`、`codex`、`zcode`、`opencode`、`qoder`；移除前会备份到 `~/.dws/skill-backups/`（F-081）。

## 失败判读

| 退出码 | 含义 | 常见原因 | 处置 |
|--------|------|---------|------|
| 2 | 参数错误 | 命令拼错、flag 不存在 | `dws <path> --help` 对照 |
| 3 | 认证/授权错误 | 未登录、令牌失效且无法刷新 | 重新 `dws auth login` |
| 4 | 待交互授权 | 组织未启用 CLI 访问、需管理员审批 | 发起申请，审批后重试 |
| 5 | 权限不足 | 账号无该接口权限或数据范围 | 换账号或申请权限 |
| 6 | 限流/服务端错误 | 调用过频、服务端异常 | 退避重试；持续失败查服务状态 |

退出码语义见 F-043，完整错误结构见 [05 输出与 Schema 发现](../concepts/05-output-and-schema-discovery.md)。

## 跨机迁移（Linux 沙箱之间）

只复制 `~/.dws/app.json` **不会**带走刷新令牌，访问令牌过期后就需要重新登录。应使用官方导出/导入（F-033 ~ F-040）：

```bash
# 源机器
dws auth export -o /tmp/dws-auth.tar.gz
# 目标机器
dws auth import -i /tmp/dws-auth.tar.gz
dws auth status
```

Windows 上的 export/import 会被主动拒绝（凭据存于 DPAPI 保护的注册表，无法安全转换为可移植包）。

下一篇 → [01 日常办公操作](01-daily-workspace-operations.md)