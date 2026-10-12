---
okf_version: "0.2"
type: Reference
title: "REA 信源登记（source-manifest）"
description: "REA（Reverse Engineer Anything）五个信源的 URL、归属、公开性预检、访问时点、版本固定与关系核实结论"
tags: [rea, source-manifest, public-gate, mcp, reverse-engineering]
generated:
  by: source-code-to-okf-wiki:R
  at: "2026-10-12T09:00:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: rea-run
    url: "https://rea.run/zh/"
  - id: zhihu-article
    url: "https://zhuanlan.zhihu.com/p/2091916182064456398"
  - id: rea-research-repo
    url: "https://github.com/ringozzt/rea-research"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
  - id: local-source
    url: "file" # 本地 vendor 镜像：external/dao/rea（主仓库 morluto/rea 的本地副本）
---

# REA 信源登记（source-manifest）

> 公开性预检：本 bundle 的四个网络信源均为公开内容（公开展示页 / 公开文章 / 公开仓库 / 公开文档站），无登录墙、无验证码、无邀请码，可通过公开 URL 直接访问，符合公有内容落地标准。本地源码信源为 `external/dao/rea`（MIT 许可），可追溯、可复现。未复制任何页面全文，仅在 facts.md 中登记可验证的结构事实、命令与能力声明。
> 采集通道：WebFetch 解析公开 URL + 本地源码读取（2026-10-12）。

## 关系核实结论（spec 中 Open Questions）

| 问题 | 结论 | 证据 |
|------|------|------|
| Q-A：`rea.run/zh/` 与 `rea.tools/zh-CN/` 是否为同一站点的不同域名/版本？ | **否。二者为不同站点。** `rea.run/zh/` 是**非官方**中英双语教学/整理站；`rea.tools/zh-CN/` 是 REA **官方**文档站。 | rea.run 首页原文明示「rea.run 是非官方中英双语站点，整理 REA（Reverse Engineer Anything）的 MCP／CLI 工作流、安装说明与原创教学示例。行为以 [GitHub 上游](https://github.com/morluto/rea)为准」；rea.tools 首页无此声明且为官方文档引导。 |
| Q-B：`github.com/ringozzt/rea-research` 与 `github.com/morluto/rea` 的关系？ | **独立第三方调研仓库，非主仓库。** `ringozzt/rea-research` 是用户 `ringozzt` 于 2026-10-11 发布的**独立技术调研仓库**（研究笔记，3 stars / 4 commits / 0 forks，含 README + report.html + mindmap.html）；主仓库为 `morluto/rea`。 | rea-research README 明示「**本报告为独立第三方调研，与原项目无关**」并「原项目：[morluto/rea](https://github.com/morluto/rea)（MIT）· 官网 [rea.tools](https://rea.tools/)」。 |

> **口径取舍**：由于 Q-A/Q-B 结论，本 bundle 的「产品事实」以**官方信源（rea.tools 文档站 + 本地源码 main@eaf88aca）**为一手权威；`rea.run/zh/` 与 `ringozzt/rea-research` 作为**教学/调研补充信源**，标注为二手/衍生，仅在 facts 中登记可复核的结构性声明，不作前瞻性（timeline/预估）依据。

## 信源清单

| source_id | 类型 | 标题 / 标识 | URL | 归属 / 作者 | 访问时点 | 公开性 | 归属证据 | 一/二手 | 状态 |
|-----------|------|------------|-----|------------|---------|--------|---------|---------|------|
| rea-tools-doc | 官方文档站 | REA · Reverse Engineer Anything（中文） | https://rea.tools/zh-CN/ | morluto（REA 官方） | 2026-10-12 | ✅ 公开 | 官方域名 rea.tools；站内导航 guides/showcase 与 npm 安装指引 | 一手 | collected |
| local-source | 本地源码 | REA 源码仓库（`rea-agents` v6.4.0） | external/dao/rea（镜像自 https://github.com/morluto/rea @ eaf88aca） | morluto（MIT） | 2026-10-12 | ✅ 公开 | package.json 版本 6.4.0、MIT、homepage morluto/rea；commit eaf88aca | 一手 | verified |
| rea-run | 教学/整理站 | rea.run 社区指南（中文） | https://rea.run/zh/ | ylwl1997（第三方，非 REA 官方） | 2026-10-12 | ✅ 公开 | 站点首页自述「非官方中英双语站点」，操作为自有教学实验（GitHub Actions 演示 / Codespaces） | 二手 | collected |
| rea-research-repo | GitHub 调研仓库 | REA 深度技术调研 | https://github.com/ringozzt/rea-research | ringozzt（第三方研究者） | 2026-10-12 | ✅ 公开 | README 自述「本报告为独立第三方调研，与原项目无关」；2026-10-11 调研 | 二手 | collected |
| zhihu-article | 知乎专栏文章 | 前端 Hardy ·《GitHub 31.2K Star！AI开始搞逆向工程了？》 | https://zhuanlan.zhihu.com/p/2091916182064456398 | 前端Hardy（知乎用户 wang-yan-hui-35-43） | 2026-10-12 | ✅ 公开 | 文章正文署名与作者主页；文章发布于 2026-10-09 | 二手 | collected |

## 本地源码版本固定（G0 信源稳定性门）

- **本地源码路径**：`external/dao/rea`
- **上游仓库**：https://github.com/morluto/rea
- **npm 包名 / 版本**：`rea-agents` / **6.4.0**（package.json）
- **许可证**：MIT
- **当前分支**：`main`（浮动）
- **固定提交**：**`eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a`**（2026-10-12 捕获）
- **不锚定浮动 `main` 名**：本 bundle 所有对本地源码的引用以 commit hash `eaf88aca` 为追溯固定点；若上游 main 前进，本 bundle 的 facts 仍指向该固定提交可复现。
- **G0 判定**：本地源码位于 `external/`（非 git submodule、非临时目录），为**可追溯副本**；以 commit hash 登记即可满足信源稳定性门。

## 访问时点与动态口径

- **当日**：2026-10-12。
- **动态数字口径**：GitHub Star/Forks、npm 周下载量等为**快速变化**的动态指标，各信源之间数值不一致（rea.tools 首页显示 105,209；知乎文写 31.2K；rea-research 调研写 79K）。本 bundle **不把任何动态数字作为规范事实**，仅在 facts.md 中记录「快照时点 + 来源」的原始数字，不进行跨源裁决。
- **版本口径**：产品功能以本地源码 `main@eaf88aca`（package.json version 6.4.0）为准。
- **信源时间线**：README/文档为 2026-10 期间；知乎文发布于 2026-10-09；rea-research 调研于 2026-10-11。

## 停止规则 / 失败记录

| source_id | 失败信号 | 重试边界 | 下次允许动作 |
|-----------|---------|---------|-------------|
| rea-tools-doc | 无（采集成功） | - | - |
| local-source | 无（0 失败） | - | - |
| rea-run | 无（采集成功） | - | - |
| rea-research-repo | 无（采集成功，但属第三方衍生，多数字段与一手源冲突，仅作补充视角） | - | - |
| zhihu-article | 无（采集成功，但含大量反爬 token，正文核心段仍可读） | - | - |

## 未采集项

- 不保存任何页面全文、HTML 转储；仅在本 bundle 内登记结构化事实与必要命令（符合版权最小引用原则）。
- 网络页面内嵌图片文字不经 OCR 采集；以正文文字事实为准。
- rea-research 调研中的「未验证 / 待核实项」（如约 97 CLI commands、150MB→577MB JSON、ghidra-mcp tool 数）**不采用**，需以本地源码或官方文档一手核验为准。