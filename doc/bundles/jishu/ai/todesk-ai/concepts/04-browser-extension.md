---
okf_version: "0.2"
type: concept
title: 浏览器插件
description: ToDesk AI 浏览器插件——免安装客户端、浏览器内即用的 Chrome 扩展，四大能力：智能导航、自动操作、内容采集、智能检查（F-059 至 F-065）
tags: [todesk-ai, browser-extension, chrome, web-automation]
generated:
  by: codearts/glm-5.2-sft-harmony
  at: "2026-09-12T12:30:00+08:00"
sources:
  - id: todesk-ai-site
    url: https://www.todeskai.com
  - id: chrome-store
    url: https://chromewebstore.google.com/detail/todesk-ai/lffkckjdanbbljnldjikonmjhnnjbccg
---

# 浏览器插件

## 定位

ToDesk AI 浏览器插件是产品在 3.1.x 版本阶段推出的 Chrome 扩展（F-059），核心卖点是**免安装客户端、浏览器内即用**（F-060）——用户无需下载 ToDesk AI 桌面应用，在浏览器中安装插件后即可一键唤起 AI，自动完成网页任务。

这与桌面端的 Computer Use 形成互补：Computer Use 通过远程连接操控目标电脑上的软件界面，而浏览器插件直接在本地浏览器中操作网页，无需远程连接链路。

## 四大能力（F-061）

| 能力 | 说明 | F |
|------|------|---|
| 智能导航 | 自动打开网页、搜索、前进后退，精准直达目标页面 | F-062 |
| 自动操作 | 点击、输入、滚动、拖拽、下拉选择，模拟真人交互 | F-063 |
| 内容采集 | 截图、PDF、GIF 录制、页面内容提取，一键留存资料 | F-064 |
| 智能检查 | 元素查找、属性读取、样式检测，洞察页面结构 | F-065 |

## 与桌面端的关系

浏览器插件不是桌面端的替代，而是**轻量级入口**：

- **桌面端**（Computer Use）：跨设备远程操控，能操作任何桌面软件，需要远程连接
- **浏览器插件**：本地浏览器内操作，仅限网页任务，无需远程连接，安装门槛更低

对于纯网页任务（数据采集、表单填写、页面信息提取），浏览器插件是更轻便的选择；对于需要操作桌面软件的任务（IM 发消息、OA 系统操作），仍需桌面端 Computer Use。

## 安装方式

通过 Chrome 网上应用店安装（F-059）。插件页面链接见 [references/article-source.md](../references/article-source.md)。

## 主题关联

- [Computer Use 运行机制与能力边界](02-computer-use.md)：桌面端 GUI 操控的机制与边界，与浏览器插件形成互补
- [BrowserAct 浏览器自动化 Agent](../../browseract/index.md)：同为浏览器自动化方案的开源框架对照