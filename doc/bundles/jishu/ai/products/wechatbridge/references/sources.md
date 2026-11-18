---
type: sources
title: "WeChatBridge（微信流）· 信源地图"
description: "登记第三方博文、官方仓库文档和核验补充的职责范围，保留九个与十二个入口、平台状态等时点差异。"
---

# 信源地图

本文件说明不同材料支持什么结论；具体事实仍以 [article-source.md](article-source.md) 的 F-001~F-107 登记为准，逐项结论以 [verification.md](verification.md) 为准。

## 信源分层

| 层级 | 信源 | 支持范围 | 使用边界 |
|---|---|---|---|
| L1 二手推介 | 微信公众号「虾说AI实验室 / 虾哥」《微信聊天记录只能烂在手机里？开源 WeChatBridge 一键转给 AI 和 Obsidian》 | 源文的产品定位、九个入口、场景叙述和作者判断（F-001~F-063） | 作者不是项目方；图片演示只作缺口登记，价值判断不升级为官方结论（F-009、F-038） |
| L2 官方一手 | GitHub `freestylefly/WeChatBridge` 默认分支 README | 项目身份、MIT 许可、当前十二个入口、平台状态、隐私边界、安装与构建流程（F-064~F-100） | 默认分支渲染页未返回 commit SHA 与最后更新日期，不能完整回溯源文时点（F-102、F-105） |
| L3 官方引用 | `USAGE.zh-CN.md`、`PRODUCT_CAPABILITIES.zh-CN.md` | README 中引用的使用与能力文档关系（F-101） | 本次只登记引用关系；未将未抓取正文扩写成新的事实 |
| L4 核验补充 | README、官方脚本、GitHub 页面和相关权威材料 | 入口组装、隐私/权限、分批上限、项目署名等补充（F-081~F-107） | 四项 ⚠️ 是时点或措辞差异，不应改写为源文完全失实 |

## 关键时点对照

| 主题 | 源文口径 | 官方当前口径 | 事实依据 |
|---|---|---|---|
| 内置入口 | 九个原生入口 | 十二个内置入口 | F-018、F-041、F-067、F-068 |
| 平台范围 | macOS 工具 | macOS 与 Windows 已提供下载，iOS 开发中 | F-011、F-078、F-079、F-095 |
| 签名公证 | 源文写完成态 | 官方未逐字确认完成态 | F-015、F-100、F-103 |
| 微信接口边界 | 源文概括为不调接口 | 官方逐字说明不读库、不解密、不注入、不改进程 | F-026、F-082 |

## 双份登记与引用规则

- `article-source.md` 与主仓库 spec 的 `facts.md` 是 F 编号双份登记，集合应为连续的 F-001~F-107。
- `insights.md` 中的行动项是编者建议；任何入口数量、版本、平台和命令仍需回指 F 编号。
- examples 的流程来自官方 README 文档化材料，必须标注“非源文作者实测、未在本知识包 macOS 实机验证”（F-039、F-077、F-088~F-094）。

## 原文与官方入口

- [微信公众号原文](https://mp.weixin.qq.com/s/QdCiRiwjjc5uOvBW0nBZxw)：第三方产品推介。
- [WeChatBridge 官方仓库](https://github.com/freestylefly/WeChatBridge)：官方 README 与项目入口。
- [官方使用指南](https://github.com/freestylefly/WeChatBridge/blob/main/USAGE.zh-CN.md)：README 引用的使用材料。
- [官方能力说明](https://github.com/freestylefly/WeChatBridge/blob/main/PRODUCT_CAPABILITIES.zh-CN.md)：README 引用的能力材料。

