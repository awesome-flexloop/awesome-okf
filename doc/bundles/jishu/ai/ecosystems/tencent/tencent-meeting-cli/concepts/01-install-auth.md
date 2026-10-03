---
type: Concept
title: "安装与 OAuth2 授权"
description: "tmeet 的两种安装方式（npm 全局安装与 Go 源码构建）、CLI-Skill 安装、Node 版本口径差异、设备码 OAuth2 登录流程、凭证加密存储与目录配置。"
tags: [tencent-meeting, tmeet, installation, npm, oauth2, device-code, keychain, credential]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: install-guide
    resource: /references/install-guide.md
    title: 腾讯会议 CLI 安装指南
  - id: github-readme
    resource: /references/github-readme.md
    title: tencentmeeting-cli GitHub README
  - id: cloud-doc
    resource: /references/cloud-doc.md
    title: 腾讯云文档《腾讯会议 CLI 说明》
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单与 package.json
---

# 安装与 OAuth2 授权

## 环境要求

| 项 | 要求 | 信源 |
|----|------|------|
| Node.js | `>=14`（安装指南与 package.json engines） | F-013、F-014 |
| Node.js（腾讯云文档口径） | `≥ 16` | F-015 |
| 操作系统 | macOS / Linux / Windows | F-018 |
| Go（仅源码构建） | 1.22+ | F-003 |

> ⚠️ Node 版本口径差异：安装指南页与 package.json 均为 `>=14`，腾讯云文档正文写「Node.js ≥ 16」（F-015）。实践建议：以 package.json 的 `>=14` 为最低门槛，但优先使用 Node LTS 版本（首页 FAQ 对 npm 缺失的处理建议同样是安装 LTS，F-016）。若遇安装或运行异常，先升级到 LTS 再排查。

## 第一步：安装 CLI

推荐 npm 全局安装（F-011）：

```bash
npm install -g @tencentcloud/tmeet
```

验证：

```bash
tmeet --version    # 或 tmeet -V
```

npm 包特征（F-008）：包名 `@tencentcloud/tmeet`，`bin` 注册 `tmeet` 命令，含 `postinstall` 清理钩子，发布产物仅 `scripts/` 与 `dist/`。

### 从 Go 源码构建

需要 Go 1.22+（F-017）：

```bash
git clone https://github.com/TencentCloud/tencentmeeting-cli.git
cd tencentmeeting-cli

# 方式一：直接 go build
go build -ldflags "-X tmeet/cmd.Version=v1.0.0" -o tmeet .

# 方式二：make
make build VERSION=v1.0.0
```

### npm 常见问题（首页 FAQ，F-016）

- `npm: command not found`：安装 Node.js LTS（自带 npm）。
- 装完找不到 `tmeet`：检查 npm 全局 bin 目录是否在 `PATH` 中，安装后重启终端。

## 第二步：安装 CLI-Skill（必需）

```bash
npx skills add TencentCloud/tencentmeeting-cli -y -g
```

- `npx skills` 是 Skills 生态的 Skill 分发命令（随 Node.js/npm 提供的 `npx` 按需拉取运行，无需预装），`add` 后接 `组织/仓库` 形式的 Skill 源；
- `-g` 为全局安装；
- 安装后**必须重启 AI 工具**（Claude Code / Cursor / Codex 等），确保 SKILL 完整加载（F-019）。

安装指南还提供了可直接发给 AI 助手的一句话提示词（F-020）：

> 帮我安装腾讯会议CLI，链接地址：https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web

## 第三步：设备码授权登录

```bash
tmeet auth login
```

流程特征（F-021、F-022）：

1. CLI 自动打开系统默认浏览器，跳转到腾讯会议授权页；
2. 用户在浏览器中确认授权（设备码 OAuth2 流程，全程不输入密码）；
3. CLI 在终端轮询授权结果，**超时时间 5 分钟（300 秒）**；
4. 无图形界面环境加 `--no-browser`，CLI 只打印授权 URL，由用户自行在有浏览器的设备打开。

```bash
tmeet auth login --no-browser
```

### Agent 执行 login 的硬约束

SKILL.md 规定 `auth login` 是阻塞命令，最长阻塞 300 秒，**必须前台运行，禁止用 `&` 等后台方式**，否则凭证可能写入失败（F-023）。

### 登录态查询与登出

```bash
tmeet auth status    # 输出 OpenId、Access/Refresh Token 过期状态与剩余秒数；未登录提示 Not logged in
tmeet auth logout    # 清除本地认证凭证，无参数
```

除 `auth login/status` 与 `event list/schema/status/stop` 外，所有命令都要求先登录；未登录执行业务命令会得到 `user config is empty`（F-029）。重复登录会提示 `user has been initialized`（F-040）。

## 凭证如何存储

- Access/Refresh Token 使用 **AES-256-GCM 加密**保存，明文不落盘（README/首页口径，F-024）；
- 腾讯云文档进一步描述为「存入系统 Keychain，与设备绑定，无法在另一台机器上解密」（F-025）。

> 两个口径互补：加密凭证通过系统 Keychain 机制保管（macOS Keychain / Windows 凭据管理器等），因此同时具备「AES-256-GCM 加密」与「设备绑定」两个属性。

配置目录默认 `~/.tmeet/`，可用环境变量覆盖（F-028）：

| 环境变量 | 作用 | 默认值 |
|----------|------|--------|
| `TMEET_CLI_CONFIG_DIR` | 配置目录 | `~/.tmeet/` |
| `TMEET_CLI_DATA_DIR` | 加密数据目录 | 平台相关默认路径 |

## 凭证安全纪律（腾讯云文档建议，F-030、F-031）

- 不要把 `~/.tmeet/` 目录或 Keychain 数据作为构建产物传递/归档/上传到代码仓库；
- 不要在命令行参数或脚本注释中硬编码账号信息；
- 不要把凭证文件截图或复制到 AI 对话框；
- 怀疑泄露：立即 `tmeet auth logout`，并到腾讯会议账号安全中心吊销授权。

v1.0.18 起登出改为两阶段：先执行全部资源释放 hook（如停止事件总线），全部成功后才删除 Keychain 与本地配置；任一 hook 失败则保留凭证供重试（F-032）。这意味着如果 event bus 残留导致登出失败，按报错处理 bus 后重新 logout 即可，凭证不会处于半清除状态。

## 延伸阅读

- [00 - 产品定位与架构](00-overview.md)
- [02 - 命令体系与全局约定](02-command-map.md)
- 示例：[01 - 十分钟上手](../examples/01-quickstart.md)
