---
okf_version: "0.2"
type: example
title: 浏览器插件安装与使用
description: Chrome 商店安装 ToDesk AI 浏览器插件、一键唤起与四类网页任务的实操流程（F-059 至 F-065）
tags: [todesk-ai, browser-extension, chrome, install]
generated:
  by: codearts/glm-5.2-sft-harmony
  at: "2026-09-12T12:30:00+08:00"
sources:
  - id: todesk-ai-site
    url: https://www.todeskai.com
  - id: chrome-store
    url: https://chromewebstore.google.com/detail/todesk-ai/lffkckjdanbbljnldjikonmjhnnjbccg
---

# 浏览器插件安装与使用

> 本篇为可照做的实操流程，整合自 todeskai.com 官网浏览器插件介绍。

## 1. 安装

1. 访问 Chrome 网上应用店 ToDesk AI 插件页面（F-059）；
2. 点击"添加至 Chrome"，确认安装；
3. 安装完成后浏览器工具栏出现 ToDesk AI 图标。

> 当前仅支持 Chrome 浏览器。桌面端 Computer Use 的网页操作支持 Chrome 和 Edge（F-055），但浏览器插件目前仅提供 Chrome 版本。

## 2. 唤起

点击工具栏中的 ToDesk AI 图标，即可在浏览器内唤起 AI 助手——无需打开桌面客户端（F-060）。

## 3. 四类网页任务

### 智能导航（F-062）

让 AI 自动打开目标网页、执行搜索、前进后退。适用于：
- "帮我打开 XX 后台搜索今天的订单"
- "导航到某个网站的特定页面"

### 自动操作（F-063）

模拟真人交互：点击按钮、输入文本、滚动页面、拖拽元素、下拉选择。适用于：
- "在这个表单里填写以下信息并提交"
- "点击页面上的下载按钮"

### 内容采集（F-064）

截图、导出 PDF、录制 GIF、提取页面内容。适用于：
- "把这个网页截图保存"
- "提取这个页面的所有产品名称和价格"
- "录制一段操作过程的 GIF"

### 智能检查（F-065）

元素查找、属性读取、样式检测——洞察页面结构。适用于：
- "检查这个页面有没有某个特定的按钮"
- "读取这个元素的属性值"

## 4. 适用与不适用

| 场景 | 浏览器插件 | 桌面端 Computer Use |
|------|:---:|:---:|
| 纯网页任务（采集/表单/导航） | ✅ 推荐（更轻便） | ✅ 可用（需远程连接） |
| 桌面软件操作（IM/OA/ERP） | ❌ 不支持 | ✅ 必须 |
| 跨设备远程操控 | ❌ 不支持 | ✅ 必须 |
| 快速网页任务（免安装客户端） | ✅ 推荐 | ❌ 需安装桌面端 |

## 本篇检查清单

- [ ] Chrome 浏览器已安装
- [ ] 从 Chrome 商店安装 ToDesk AI 插件（非第三方来源）
- [ ] 工具栏可见 ToDesk AI 图标
- [ ] 测试一次智能导航任务验证插件可用