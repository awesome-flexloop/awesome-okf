---
type: Example
title: 本地扫码连接快速上手
description: 从零跑通 DSH Mobile——启动 Relay、安装 dsh-scan-remote 插件、扫码配对四步流程、局域网排障三查；所有命令来自作者实测博文
tags: [DeepSeek Harness, DSH Mobile, 扫码连接, Relay, 快速上手, dsh-scan-remote, 排障]
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
    title: 博文信源事实清单（F-001~F-045）
---

# 本地扫码连接快速上手

> **操作基础**：以下命令与步骤来自博文作者一手实测（F-036~F-040）。**命令可能随版本演进**——DSH 处于 developer preview，接入时建议锁定博文对应版本（dsh-v0.1.1-rc.2，F-045）。完整事实清单见 [references/article-source.md](../references/article-source.md)。

## 1. 前置条件

本地扫码连接可按四步完成（F-036）：

1. 启动 Relay
2. 安装扫码插件并启动 DSH
3. 在手机上安装 DSH Mobile
4. 扫描 Settings 中的 Remote Access 二维码

先让手机和电脑连接**同一个可信 Wi-Fi 或热点**（F-036）。

## 2. 终端 1：启动本地 Relay

```bash
git clone https://github.com/yukiykchen/dsh-scan-remote.git
cd dsh-scan-remote/relay
cp .env.example .env
npm ci
npm run build
HOST=0.0.0.0 PORT=8787 npm start
```

> 局域网试用时，Relay 需要监听手机能够访问的网络接口。`HOST=0.0.0.0` 会开放 8787 端口到本机所有网络接口——**请只在可信网络中使用，并检查系统防火墙设置**（F-037）。

## 3. 终端 2：安装插件并启动 DSH

```bash
npx @deepseek-ai/dsh plugin --profile web add \
  "github:yukiykchen/dsh-scan-remote#v0.0.1"

export PUBLIC_RELAY_URL=http://192.168.1.10:8787
npx @deepseek-ai/dsh web
```

`PUBLIC_RELAY_URL` 要换成电脑当前的局域网地址——它会写进二维码，**必须能从手机访问**（F-038）。DSH 启动后，打开 Settings，进入 Remote Access 页面。

## 4. 手机安装 DSH Mobile

| 平台 | 安装方式 |
|------|---------|
| Android | 从 releases 页面下载 APK 后安装 |
| iOS | 用 Xcode 打开 `iosApp/iosApp.xcworkspace`，配置自己的开发者签名后装到真机 |
| HarmonyOS | 用 DevEco Studio 打开 `ohosApp` 自行构建 |

代码仓库：`deepseek-harness-mobile`（F-039）。

## 5. 扫码配对

手机扫描 Settings 中 Remote Access 页面显示的二维码即可完成配对（F-036/F-029）。

## 6. 排障三查

如果扫码后一直超时，先检查三件事（F-040）：

1. **手机能否访问** `http://电脑局域网地址:8787/health`
2. **PUBLIC_RELAY_URL** 是否仍是电脑当前地址
3. **Relay 是否真的监听**了手机可达的接口，防火墙是否允许 8787 端口

> 电脑更换 Wi-Fi 或热点后，局域网地址通常会变化——此时需要更新 `PUBLIC_RELAY_URL`，重启 DSH，再扫描新二维码（F-040）。

## 7. 云端运行变体

除个人电脑本地运行外，可将 DeepSeek Harness 部署在**腾讯云轻量应用服务器**上（F-041）：Agent 循环、工具执行、插件与工作区持续运行在云端，手机 App 仍只负责连接、交互与渲染——长任务不再依赖个人电脑一直开机（F-041）。

## 8. 协议与安全提示

- 扫码模式两端主动连接 Relay、sealed-tunnel-v1 转发，电脑不把 DSH 开放到局域网/公网（F-029/F-030）
- 也可改用 SSH 模式（已有主机+密钥时更直接，见 [03-connection-and-reconnect](../concepts/03-connection-and-reconnect.md)）
- 涉及 DSH 内部协议细节时，以官方仓库 rpc-map.ts 与 Releases 版本为准（verification B3 项）
