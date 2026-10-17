---
type: Example
title: 命令流一：从安装到静态/全栈部署上线
description: 个人用户在本机完成 meoo cli 安装、浏览器授权、本地预览（localhost:3015）、静态部署与首次全栈 --runtime image 部署的端到端命令与话术序列（文档级复现）
tags: [meoo, miaowu, cli, deploy, example]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: cli
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南
---

# 命令流一：从安装到静态/全栈部署上线

> **复现性质声明**：本示例为**文档级复现，未做运行验证（2026-10-18）**——命令与话术全部逐字摘自 [Meoo CLI 使用指南](https://docs.meoo.com/features/cli)，未在真实环境执行。命令原理与坑点见 [03 静态部署与全栈部署](../concepts/03-deploy-static-vs-fullstack.md)、[04 本地 Agent 协作工作流](../concepts/04-local-agent-workflow.md)。

## 阶段 0：前置环境

- 本机已装 **Node.js 20 或更新版本**（F-005）；
- Windows 额外装好 Git for Windows 与 zip 工具（F-006）。

## 阶段 1：安装（二选一）

方式 A——对本地 Agent 发送自动安装话术（F-007）：

```text
读取 meoo.com/skill-setup.md 并按照说明安装秒悟技能
```

方式 B——终端手动安装并验证（F-008、F-009）：

```bash
npm install -g @aliyun-meoo/cli
meoo --version
```

显示版本号即成功。

## 阶段 2：浏览器授权

安装后 CLI 自动打开浏览器跳转 `meoo.com` 授权页：首次登录秒悟账号 → 确认设备名称 → 点「授权登录」→ 回终端，凭证自动保存（F-010）。

未自动弹出时手动触发（F-011）：

```bash
meoo login
```

## 阶段 3：创建项目（对 Agent 下意图）

```text
帮我用meoo做一个好看的个人主页，数据接入云服务数据库，然后一键发布到线上
```

（F-012）Agent 自动写页面、云端建库、补后端、部署出链接（F-013）。

若项目有服务端进程，补一句（F-017）：

```text
这个项目需要服务端进程，请使用全栈应用部署。
```

## 阶段 4：本地预览自测

```text
起个本地预览看看效果
```

浏览器自动打开 `localhost:3015`（静态应用）；全栈应用按项目自己的方式启动（F-014、F-018）。可注册账号、提交表单、查数据库。

## 阶段 5a：静态部署

```text
部署上线
```

Agent 执行 `meoo deploy`，构建前端产物发布到 CDN，终端输出分享链接（F-015、F-022）。纯静态页无需开通云服务、不占云服务额度（F-023）。

## 阶段 5b：全栈部署（首次）

首次全栈部署必须带 runtime 参数（F-022）：

```bash
meoo deploy --runtime image
```

云端在 Linux `/code` 环境构建（Node.js 24.15.0 等固定矩阵，F-024），应用必须监听 `0.0.0.0:${PORT:-9000}`，并提供 `scripts/setup.sh`（构建期）与 `scripts/start.sh`（启动期）（F-025）。无需自写 Dockerfile（F-026）。**首跑之后**的后续部署可直接 `meoo deploy`（F-022）。

## 阶段 6（按需）：同步回云端做二次开发

```text
帮我把代码同步到meoo云端
```

同步后可在 meoo 官网看到应用并在秒悟中二次修改；扩容量、大模型服务、自定义域名、发布范围控制建议在同步后使用（F-016）。

## 异常分支速查

| 现象 | 处置（来源） |
|---|---|
| 开通云服务后立刻连库报「未开通」 | 等 2-3 分钟让 Agent 重试，命令成功只代表申请已发出（F-020） |
| 网页后台也在改，担心覆盖 | 本地开发期不在网页发布；先同步再网页协作（F-019） |
| 余额不足 | 查 `https://docs.meoo.com/pricing`，或到 `https://meoo.com` 删闲置项目/实例（F-027） |
| 全栈项目数受限 | 限时免费口径 Free 1 / Pro 4 / MAX 8（F-027 ⚠️ dated） |

## 下一步

- 要部署到**自己的阿里云账号**：见 [02 阿里云 BYOC 命令流](02-aliyun-byoc.md)；
- 要在**团队 Agent/CI** 中跑：见 [03 团队 token 与 CI 发布](03-team-token-ci-publish.md)。
