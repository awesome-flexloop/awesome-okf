---
type: Source Manifest
title: "信源登记表：Tauri 2.0 与 Electron 对比文章"
description: "本次知识包转化的单一信源登记——公众号「前端之神」公开技术评论文章的可访问性、归属证据与采集元数据"
sources:
  - id: wechat-frontend-god-tauri-electron
    resource: "https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg"
    title: "取代 Electron？Tauri 2.0 做到全平台适配、轻量化！"
    author: "林三心不学挖掘机 / 前端之神"
status: verified
generated: { by: process:wechat-public-okf, at: 2026-10-10 }
---

# 信源登记表（Source Manifest）

## 1. 来源基本信息

| 维度 | 内容 |
|---|---|
| source_id | `wechat-frontend-god-tauri-electron` |
| 文章标题 | 《取代 Electron？Tauri 2.0 做到全平台适配、轻量化！》 |
| 公众号账号 | 前端之神 |
| 作者署名 | 林三心不学挖掘机 |
| 文章 URL | https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg |
| 发布时间 | 2026-10-08（页面显示 2026年10月8日 01:46） |
| 访问时间 | 2026-10-10 |
| 发现渠道 | 用户直接提供 URL（`from=industrynews` 行业资讯入口） |
| 文章类型 | 桌面跨平台开发框架对比评论（技术评测 + 选型建议） |
| 内容敏感度 | 公开（Public）——公众号公开文章，无登录/验证码/邀请码访问控制 |

## 2. 归属核验（Ownership Evidence）

- **账号信号**：文章头部署名「林三心不学挖掘机」，底部版权与公众号标识「前端之神」，位于 `mp.weixin.qq.com` 官方域名。
- **可访问性**：URL 可直接访问，未出现登录墙（login wall）、验证码（CAPTCHA）或访问频率限制。
- **无访问控制参数**：URL 中 `from=industrynews` 与 `color_scheme=light` 仅为来源渠道与主题色样式参数，非 `share?code=`/`token=` 等授权码，不构成私域访问控制。
- **停止规则**：若后续访问出现登录墙/验证码/限流循环/重复失败，则停止采集并登记为 `not-collected`。

## 3. 采集元数据

| 项 | 值 |
|---|---|
| 采集方式 | 浏览器解析器（WebFetch 稳定公开页抓取正文） |
| 正文完整性 | 获取到完整正文（约 44 段结构 + 5 大章节），未保存原文 HTML 全文镜像 |
| 图片 | 未采集（正文为纯文字对比，无必须保留的示意图） |

## 4. 范围说明

- 本次仅针对**单篇文章**（source_id 唯一）进行 OKF 转化。
- 公众号「前端之神」的其他历史内容不在本次范围。
- 判定依据：用户指定的单一 URL；不推断公众号其他未披露文章。

## 5. 已知限制与失败清单

| 类别 | 说明 |
|---|---|
| 未采集项 | 无（正文成功获取） |
| 单源局限 | 所有内容仅来自本篇单一公众号文章，未做跨平台多源全文对照；文章具体数值（内存/体积/耗时）属作者陈述，未在本流程独立复测 |
| 时效性 | 文章发布于 2026-10-08，Tauri/Electron 生态快速演进，技术数据存在过期风险，见 [verification.md](verification.md) 的 `stale_after` 建议 |