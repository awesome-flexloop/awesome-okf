---
okf_version: "0.2"
type: Example
title: "Octop 安装、初始化、启动与首用配置"
description: "从空环境安装 Octop 到可登录控制台、配置模型服务商的步骤清单（macOS/Linux 与 Windows 两种渠道）"
tags: [octop, example, install, run, deploy]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T09:55:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
  - id: official-home
    url: "https://tencentcloud.github.io/Octop/"
---

# 示例：安装、初始化、启动与首用配置

> ⚠️ 前置说明：本示例命令经官方口径核对（verification.md F-042），**未在本机实际执行**。执行前以官方安装文档当前命令为准（F-043）。

## 目标

在一台空环境中完成 Octop 自托管部署，直到能登录 Web 控制台并可使用模型。

## 输入

- 一台满足 Python 3.12+ 的机器（macOS / Linux / Windows）。
- 大模型服务商 API Key。

## 步骤

### 1. 安装

macOS / Linux：

```bash
curl -fsSL https://finnie-1258344699.cos.ap-guangzhou.myqcloud.com/octop/install.sh | bash
```

Windows（PowerShell）：

```powershell
irm https://finnie-1258344699.cos.ap-guangzhou.myqcloud.com/octop/install.ps1 | iex
```

**预期可观察输出**：命令执行完成且无错误，`octop` 命令可识别（后续 `octop --help` 不再报 command not found）。

### 2. 初始化

```bash
octop init
```

**预期**：按提示设置管理员账户/密码，完成初始配置。

### 3. 启动

```bash
# 前台运行（API + Web 控制台）
octop run

# 或：自定义主机与端口
octop run --host 0.0.0.0 --port 8088

# 或：注册为系统服务
octop service start
```

**预期**：进程启动且打印监听地址（默认 `http://127.0.0.1:8088`）。

### 4. 登录

浏览器访问 **http://127.0.0.1:8088**，用初始化时设置的管理员密码登录。

**预期**：可进入 Web 控制台（Web Dashboard）。

### 5. 配置模型服务商

在控制台配置大模型服务商与 API Key。

**预期**：保存后可在对话/专家中使用模型。

## 输出 / 验收

- [ ] `octop` 命令可用（安装成功）
- [ ] `octop init` 完成管理员初始化
- [ ] `octop run` 启动且监听 127.0.0.1:8088
- [ ] 浏览器可登录 Web 控制台
- [ ] 配置模型服务商后可发起对话

## 反模式提醒

- 不要跳过 `octop init` 直接 `run`：管理员初始化是登录的前置（F-042）。
- 不要把安装脚本 URL 当作唯一长期事实源：以官方文档当前命令为准（F-043）。
- 不要在未配置模型服务商时误以为「无法使用」：控制台可先登录，模型再配置（F-042）。

## 阅读下一步

- 建用户与角色隔离：[多 Agent 专家与长期记忆](../concepts/02-multi-agent-and-memory.md)
- 开通工具与渠道：[工具调用与多渠道接入](../concepts/03-tools-and-channels.md)