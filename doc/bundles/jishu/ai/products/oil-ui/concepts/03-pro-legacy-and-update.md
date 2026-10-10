---
okf_version: "0.2"
type: concept
title: "Oil UI Pro、老项目改造与版本检查"
description: "免费/Pro 功能图谱、老项目'先分清再体检'、版本检查机制与相邻工具"
sources:
  - id: github-repo
    resource: https://github.com/oil-oil/oil-ui
  - id: pro
    resource: https://ui.oiloil.org/pro
  - id: blog
    resource: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
status: stable
stale_after: 2027-03-31
---

# Oil UI Pro、老项目改造与版本检查

## 开源版 vs 完整版（Oil UI Pro）功能图谱（F-023 / F-028✅）

| 能力 | 开源版 | Pro（69 元买断） |
|------|:---:|:---:|
| 八步设计法 | ✅ | ✅（含更深挖掘） |
| 自带风格对比页 | ✅ | ✅（审计版更细） |
| 视觉层级 | ✅ | ✅ |
| 截图还原 | ✅ | ✅ |
| 老项目基础体检 | ✅ | ✅ |
| 交互 / 状态设计 | ❌ | ✅ |
| 页面布局适配 | ❌ | ✅ |
| 组件极致打磨 | ❌ | ✅ |
| SVG / 着色器特效 | ❌ | ✅ |
| 按三种立场（PM/开发/用户）出方案 | ❌ | ✅ |

> **合规边界**：Pro 是**闭源付费产品**（[ui.oiloil.org/pro](https://ui.oiloil.org/pro)，69 元买断、永久更新）。本知识包只描述其**能力分界**，不提供购买建议之外的承诺；实际能力以官方当期条款为准（F-028）。

## 老项目改造："先分清，再体检"

面对已有的老界面，oil-ui 主张（F-017 / F-009✅）：

1. **先分清**：判断这是"内容页"还是"说服页"，决定首屏策略。
2. **再体检**：用八步法逐项检查当前实现的品类、调性、差异化、记忆点是否到位。
3. **只推进一处**：一次只改一处"最该改"的地方，避免大改伤及可用性。

> 开源版"老项目"能力是**基础体检**；完整版提供更深的问题定位与改造建议（F-028）。

## 版本检查机制细节（F-020）

- **频率**：约每 10 分钟检查一次是否有更新。
- **超时**：网络请求超时 2 秒即跳过，不阻塞工作。
- **隐私**：**只读版本列表，不上传对话内容**。
- **静默**：本机无 Python（`python3`/`python`/Windows `py -3`）时只提醒一次。
- **关闭**：设置环境变量 `OIL_NO_UPDATE_CHECK=1` 可关闭检查。

## 相邻工具

官方推荐的搭配（F-029）：

- [draw-ui](https://github.com/oil-oil/draw-ui)：生图产出设计稿。
- [oil-motion](https://github.com/oil-oil/oil-motion)：滚动 / 拖动类网页动画。

两者与 oil-ui 各司其职：oil-ui 定方向，draw-ui 出图，oil-motion 做动效。

---
**本概念支撑事实**：F-009、F-017、F-020、F-023、F-028、F-029。