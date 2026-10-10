---
okf_version: "0.2"
type: Reference
title: "OpenCreator 博文信源登记（source-manifest）"
description: "微信公众号《1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器》的账号归属登记、采集通道、公开性预检与访问时点"
tags: [opencreator, krillinai, source-manifest, public-gate, blog-article]
generated: { by: "wechat-public-okf:R", at: "2026-10-10T12:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
---

# 博文信源登记（source-manifest）

> 公开性预检：本信源为公开微信公众号文章，无登录墙、无验证码、无邀请码，可通过公开 URL 直接访问，符合公有内容落地标准。未复制全文，仅在 facts.md 中登记结构事实、能力声明与命令。
> 采集通道：WebFetch 解析公开 URL（2026-10-10）。

## 信源清单

| source_id | 类型 | 标题 / 标识 | URL | 账号 / 作者 | 访问时点 | 公开性 | 归属证据 | 状态 |
|-----------|------|------------|-----|------------|---------|--------|---------|------|
| blog | 微信公众号 | 1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器 | https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA | AI开源无界 | 2026-10-10 | ✅ 公开 | 页面标注原创「小知小知」，公众号「AI开源无界」（409 篇原创内容） | collected |
| github-repo | GitHub 官方仓库 | krillinai/OpenCreator | https://github.com/krillinai/OpenCreator | krillinai | 2026-10-10 | ✅ 公开 | 官方仓库，README「OpenCreator was formerly known as KrillinAI」 | verified |
| github-api | GitHub REST API | 仓库元数据 | https://api.github.com/repos/krillinai/OpenCreator | GitHub API | 2026-10-10 | ✅ 公开 | 官方不可伪造元数据（Star/日期/许可/语言） | verified |
| official-home | 官方项目主页 | Open Creator | https://www.open-creator.ai/en/ | OpenCreator | 2026-10-10 | ✅ 公开 | README `homepage` 字段 | verified |

## 访问时点与动态口径

- **当日**：2026-10-10。
- **动态数字**：Star 12,671 / Fork 1,306 / Open Issues 29（2026-10-10 GitHub API 快照），引用须带时点。
- **许可**：官方为 **Apache-2.0**，博文未提及许可信息，本 bundle 以官方口径补充。
- **版本口径**：功能口径对齐 master 分支（README.md，最后推送 2026-10-10T03:05:51Z）。

## 停止规则 / 失败记录

| source_id | 失败信号 | 重试边界 | 下次允许动作 |
|-----------|---------|---------|-------------|
| blog | 无（采集成功） | - | - |

## 未采集项

- 不保存文章全文、原始 HTML 转储；仅在本 bundle 内登记结构化事实与必要命令（符合版权最小引用原则）。
- 博文配图内嵌文字（字幕对齐示例、AI 服务配置页、模板库截图）不经 OCR 采集；以正文文字事实为准。
- 火柴人动画合作的艺术家 Harbor Hsia 姓名为第三方作者声明，未在本 bundle 独立核验，标记为 author_claim。