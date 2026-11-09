---
type: sources
title: "WeChatBridge iOS 版与定验收 · 信源地图"
description: "区分产品方博文、官方仓库设计文档、验收记录与权威第三方转述，说明四项核心口径冲突的证据来源。"
---

# 信源地图

本文件提供信源层级和使用边界；具体事实以 [article-source.md](article-source.md) 的 F-001~F-084 登记为准，逐项判定以 [verification.md](verification.md) 为准。

## 信源分层

| 层级 | 信源 | 支持范围 | 使用边界 |
|---|---|---|---|
| L1 产品方博文 | 微信公众号「苍何」《开源微信流 APP，手机微信聊天记录，可以直接给 WorkBuddy 和 Obsidian 了》 | 产品方自述、iOS 功能叙述、两段提示词、五步流程和作者数字（F-001~F-061） | 属厂商/作者自述与实测混合材料；成效数字、完成态和模型评价须单独核验（F-008、F-037~F-061） |
| L2 官方仓库 | `freestylefly/WeChatBridge` GitHub API、README、目录树 | 项目身份、许可、平台状态、隐私边界与文件结构（F-062~F-070） | tree API 曾截断，`ios/` 只能写“约百余条/可见条目”，不能补精确数量（F-071） |
| L3 官方设计与计划 | `ios-dev-spec.zh-CN.md`、`ios-schedule.zh-CN.md` | S/R/T 编号、交付定义、档期和“不在 v1”清单（F-071、F-072、F-077、F-078） | 计划与规格不等于已交付；仍需结合验收记录和实际可用状态 |
| L4 官方验收记录 | `ios-验收记录.zh-CN.md` | 测试数量、复跑结果、R1~R7 状态、自修问题（F-073、F-079、F-080） | R3~R6 标为待真机，R7 为模拟器通过、待真机，不得改写成全面通过 |
| L5 权威第三方 | 关于模型发布、权重、评分和补偿的媒体转述（F-081~F-084） | 只能支持相应的媒体转述层级 | 不得写成已经取得官方原文；模型能力评价不由本束下结论 |

## 四项核心口径冲突

| 博文口径 | 官方/核验口径 | 结论 | 事实依据 |
|---|---|---|---|
| iOS 已开发完成、正在提审 | README 写正在开发中；路线图未勾选；多项验收待真机 | ❌ V-21 | F-009、F-010、F-065、F-066、F-077、F-080 |
| 灵动岛小入口与复制提示词 | dev-spec 将灵动岛列为不在 v1；通知快速投递仍待真机 | ❌ V-22 | F-019、F-077、F-080 |
| 一次发完、哪家都能吃 | 部分目标只发 TXT，视频和压缩包仍发不了 | ❌ V-23 | F-022、F-080 |
| 10-27 的国产开源模型表述 | 完整权重 11-04 才公开 | ❌ V-24 | F-037、F-040、F-081 |

## 双份登记与引用规则

- `article-source.md` 与主仓库 spec 的 `facts.md` 是 F 编号双份登记，集合应为连续的 F-001~F-084。
- `insights.md` 的行动项是编者建议；引用产品状态时必须同时给出时间点和证据状态。
- examples 全部标为非官方模板、未实机验证；可复现的是提示词与验收设计流程，不是 iOS 安装（F-046、F-047、F-065、F-071、F-072、F-080）。

## 原文与官方入口

- [微信公众号原文](https://mp.weixin.qq.com/s/94FP4Cl7JIQbxU5-i3B6og)：产品方博文与方法论线。
- [WeChatBridge 官方仓库](https://github.com/freestylefly/WeChatBridge)：README、代码与设计文档入口。
- [iOS 开发规格](https://github.com/freestylefly/WeChatBridge/blob/main/docs/design/ios-dev-spec.zh-CN.md)：S/R/T 及“不在 v1”清单。
- [iOS 验收记录](https://github.com/freestylefly/WeChatBridge/blob/main/docs/design/ios-验收记录.zh-CN.md)：验收状态与复跑记录。

