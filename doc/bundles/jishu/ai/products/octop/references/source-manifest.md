---
okf_version: "0.2"
type: Reference
title: "Octop 博文信源登记（source-manifest）"
description: "微信公众号《腾讯云开源的本地 AI 工作空间》博文的账号归属登记、采集通道、公开性预检与访问时点"
tags: [octop, source-manifest, public-gate, blog-article]
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-10-10T09:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
    title: "腾讯云开源的本地 AI 工作空间"
    account: 智能猩猩AI
---

# 博文信源登记（source-manifest）

> 公开性预检：本信源为公开微信公众号文章，无登录墙、无验证码、无邀请码，可通过公开 URL 直接访问，符合公有内容落地标准。未复制全文，仅在 facts.md 中登记结构事实、能力声明与命令。
> 采集通道：Defuddle CLI 解析公开 URL（2026-10-10）。

## 信源清单

| source_id | 类型 | 标题 / 标识 | URL | 账号 / 作者 | 访问时点 | 公开性 | 归属证据 | 状态 |
|-----------|------|------------|-----|------------|---------|--------|---------|------|
| blog | 微信公众号 | 腾讯云开源的本地 AI 工作空间 | https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg | 智能猩猩AI（编辑：没方） | 2026-10-10 | ✅ 公开 | 页面标注「智猩猩AI整理 / 编辑：没方」 | collected |
| github-repo | GitHub 官方仓库 | TencentCloud/Octop | https://github.com/TencentCloud/Octop | TencentCloud（腾讯云官方 org） | 2026-10-10 | ✅ 公开 | org 归属腾讯云；官方文档站 tencentcloud.github.io/Octop | verified |
| github-api | GitHub REST API | 仓库元数据 | https://api.github.com/repos/TencentCloud/Octop | GitHub API | 2026-10-10 | ✅ 公开 | 官方不可伪造元数据（Star/日期/许可/语言） | verified |
| official-home | 官方项目主页 | Octop 正式开源 | https://tencentcloud.github.io/Octop/ | 腾讯云 | 2026-10-10 | ✅ 公开 | 官方文档子域 | verified |
| pypi | PyPI | octop 包 | https://pypi.org/project/octop/ | octop maintainer | 2026-10-10 | ✅ 公开 | 官方包页 | verified |

## 访问时点与动态口径

- **当日**：2026-10-10。
- **动态数字**：Star/Fork/Issues 为 2026-10-10 GitHub API 快照（Star 8292、Fork 1006、Open Issues 697），引用须带时点。
- **版本口径**：博文成文于 Octop 1.0 GA（2026-09-14 发布 v1.0.0）之后；本项目功能口径对齐 main 分支及 v1.0.0 发布形态。

## 停止规则 / 失败记录

| source_id | 失败信号 | 重试边界 | 下次允许动作 |
|-----------|---------|---------|-------------|
| blog | 无（采集成功） | - | - |

## 未采集项

- 不保存文章全文、原始 HTML 转储；仅在本 bundle 内登记结构化事实与必要命令（符合版权最小引用原则）。
- 博文配图内嵌文字（若有）不经 OCR 采集；以正文文字事实为准。