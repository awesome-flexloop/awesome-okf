---
type: concept
title: 安装 Meoo CLI 与浏览器授权登录
description: 个人用户安装 meoo cli 的前置条件、自动安装话术与手动 npm 两种方式、版本验证、浏览器设备授权流程与 meoo login 兜底，以及 Windows/macOS 平台注意事项
tags: [meoo, miaowu, cli, install, login, nodejs]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
sources:
  - id: cli
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南
  - id: cli-aliyun
    resource: https://docs.meoo.com/features/cli-aliyun
    title: MEOO CLI 进阶：部署到你自己的阿里云账号
---

# 安装 Meoo CLI 与浏览器授权登录

> 本篇是**个人用户**路径。团队/CI 环境不用浏览器授权，而是安装接入版 tgz 并注入 `MEOO_TOKEN`，见 [06](06-team-skill-cli-integration.md)。

## 1. 前置条件

安装前先确认本机环境（F-005、F-006）：

| 平台 | 要求 |
|---|---|
| 通用 | 已安装 **Node.js 20 或更新版本**（源页链接 `https://nodejs.org/en/download/`） |
| macOS | 推荐通过 nvm 或 Homebrew 安装 Node.js |
| Windows | 除 Node 外还需安装 **Git for Windows** 和 **zip 工具** |

> ⚠️ 注意版本口径：这里的「Node.js 20+」是**本机运行 CLI 的前置要求**。另有两个数字别混淆——开放集成运行环境要求 Node.js 18+，全栈云端构建镜像固定 Node.js 24.15.0；三者语境不同，并列见 [verification.md](../references/verification.md) 核验项二。

## 2. 安装方式一：让 Agent 自动安装（推荐）

打开任意本地 agent（源页列举 codex / claude code / cursor / qoder / qoderwork 等），在对话框直接发送这句话（F-007，逐字）：

```text
读取 meoo.com/skill-setup.md 并按照说明安装秒悟技能
```

Agent 会自行读取该地址的说明并完成工具安装与登录引导。进阶部署（阿里云 BYOC）页给出的话术多了半句（F-062，逐字）：

```text
读取 meoo.com/skill-setup.md，并按照说明安装秒悟技能和最新版 meoo cli
```

两个话术分别出现在两个源页，措辞差异原样保留；要确保拿到含 `meoo aliyun` 能力的最新版时用第二个。

## 3. 安装方式二：手动 npm 安装

打开终端执行（F-008，逐字）：

```bash
npm install -g @aliyun-meoo/cli
```

随后验证安装（F-009，逐字）：

```bash
meoo --version
```

**显示版本号即安装成功。** 包名是带 scope 的 `@aliyun-meoo/cli`，少 scope 会装到无关包。

## 4. 浏览器设备授权（首次登录）

安装完成后的授权是**设备授权流**（F-010）：

1. CLI 自动打开浏览器，跳转到 `meoo.com` 的授权页面；
2. 首次授权需要登录秒悟账号；之后只需在网页上确认设备名称；
3. 点击「授权登录」；
4. 浏览器提示回到终端——CLI 自动获取凭证并保存，后续调用无需重复登录。

这意味着授权动作必须有人在浏览器前完成，**无人值守的服务器不适合走这条登录路径**——那种场景应使用团队接入版（[06](06-team-skill-cli-integration.md)）。

## 5. 兜底：手动触发登录

如果安装后没有自动打开浏览器，在终端执行（F-011，逐字）：

```bash
meoo login
```

该命令同样跳转到浏览器登录授权界面，后续确认设备、授权、凭证保存流程不变。

## 6. 安装后第一步：验证 Agent 能否驱动

CLI 本身装好不等于工作流就绪。源页给的最小验证是直接对 Agent 下一个完整意图（F-012，逐字）：

```text
帮我用meoo做一个好看的个人主页，数据接入云服务数据库，然后一键发布到线上
```

Agent 若能调用 CLI 完成云端建库、补后端代码、部署出链接（F-013），说明「Agent → CLI → 云」链路贯通。完整的本地预览到上线节奏见 [04](04-local-agent-workflow.md)。

## 7. 坑点与边界

| 现象 | 原因/处置 |
|---|---|
| `meoo` 命令找不到 | Node/npm 未装好或全局 bin 不在 PATH；先确认 `node --version` 满足 20+（F-005） |
| Windows 下打包/部署异常 | 缺 Git for Windows 或 zip 工具（F-006），补齐后重试 |
| 浏览器没弹出 | 手动执行 `meoo login`（F-011） |
| 想在 CI/服务器上用 | 浏览器授权流不适用；改装 tgz 接入版 + `MEOO_TOKEN`（F-050、F-053） |
| 想用 `meoo aliyun` 子命令却没有 | 可能不是最新版，用 F-062 话术让 Agent 升级，BYOC 详见 [05](05-aliyun-byoc-deploy.md) |

## 8. 延伸阅读

- [03 静态部署与全栈部署决策](03-deploy-static-vs-fullstack.md)
- [04 本地 Agent 协作工作流](04-local-agent-workflow.md)
- 安装命令逐字核验见 [verification.md](../references/verification.md) 核验项一
