---
okf_version: "0.2"
type: Concept
title: "Octop 安装与快速上手"
description: "Octop 的安装命令、初始化、启动、登录与配置模型服务商（自托管部署操作层）"
tags: [octop, install, init, run, self-hosted, deployment]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T09:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
  - id: official-home
    url: "https://tencentcloud.github.io/Octop/"
---

# Octop 安装与快速上手

> 操作层（How to deploy）。以下命令来自博文并经官方安装文档口径核对（F-042、verification.md）。**实操前请以官方文档当前命令为准**（安装脚本托管渠道可能更新，F-043）。

## 前置要求

- Python 3.12+（自托管，官方口径 F-040）。
- 一台可长期运行的服务器/PC（本机即可）。

## 安装

macOS / Linux：

```bash
curl -fsSL https://finnie-1258344699.cos.ap-guangzhou.myqcloud.com/octop/install.sh | bash
```

Windows（PowerShell）：

```powershell
irm https://finnie-1258344699.cos.ap-guangzhou.myqcloud.com/octop/install.ps1 | iex
```

> 校验注：安装脚本 URL 为腾讯云对象存储 COS 域名（F-043）；以官方文档当前提供的安装方式为准。

## 初始化

```bash
octop init
```

## 启动

```bash
# 前台运行（API + Web 控制台）
octop run

# 自定义主机与端口
octop run --host 0.0.0.0 --port 8088

# 注册为系统服务（systemd / launchd / Windows 服务）
octop service start
```

## 登录与首用

1. 启动后在浏览器访问 **http://127.0.0.1:8088**（自定义端口则改端口）。
2. 使用初始化时设置的**管理员密码**登录。
3. 配置所需的**大模型服务商**和 **API Key**，即可开始使用。

## 建议的落地步骤（依据上文能力）

1. 安装并启动，确认 Web 控制台可登录（F-042）。
2. 创建多名用户的账户，设置角色与隔离边界（F-025/F-026）。
3. 按团队角色建立**专家**：写作 / 编程 / 资料整理（F-013）。
4. 导入团队文档建立**知识库 / RAG**（F-017/F-019）。
5. 按需开通工具能力（Browser / Terminal / 远程桌面）与消息渠道（F-020/F-027）。
6. 配置定时任务（F-028）与外部编码 Agent 委托（F-024）。

## 阅读下一篇

- [实操示例](../../examples/00-install-and-run.md)——带验证点的安装启动步骤清单
- [安装与使用注意事项（博文边界）](../references/verification.md)