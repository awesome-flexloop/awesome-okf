---
type: Reference
title: "OpenCode 2.0.32 同快照深化信源"
description: "固定配置、codemode、插件、状态、回放及云端更新的实现链与阅读边界"
source: "https://github.com/anomalyco/opencode/tree/6ec56821d63100fe5bda45b759364f561c56b359"
tags: [opencode, source-map, deepening]
status: draft
sources:
  - id: opencode-fixed
    resource: https://github.com/anomalyco/opencode/tree/6ec56821d63100fe5bda45b759364f561c56b359
    title: "anomalyco/opencode@6ec56821"
---

# OpenCode 2.0.32 同快照深化信源

本轮于 2026-10-21 在既有束内深化，根 manifest 为 `2.0.32`，源码坐标仍为 `6ec56821d63100fe5bda45b759364f561c56b359`。本机 checkout 只是读取通道；活动信源采用不可变 commit URL，不要求读者具有同样的本机路径。

## 增量证据

本轮事实续接 F-115～F-151，共 37 条；不重排历史 F-001～F-114。逐声明路径、行范围与固定链接见[新增事实](../spec/facts-deepening-2.0.32.md)。这里的“正文已读”指列出的代表性文件，不表示整个包已穷尽审计。

| 主题 | 正文已读的代表入口 | 对照及片段读取 | 未读边界 |
|---|---|---|---|
| 配置与上下文 | Core config/discovery；config plugin instruction/skill/skill-scan/skill-file/compaction；session instructions/skill/compaction | config compaction 测试正文；config skill 测试1-120 | normalize/variable、全部指令测试、Provider压缩内部 |
| Codemode | codemode、interpreter execute/limits；Core codemode/tool与tool snapshot | tool-runtime381-450、tool-schema289-308；codemode测试566-618；Core codemode测试正文 | 其他语法/stdlib/web extension；无进程级隔离验证 |
| Schema/Plugin | schema plugin/event；Effect/Promise plugin；Core module/hooks、activate90-180 | Event测试正文；adapter613-628；module/plugin测试由只读代理片段核验 | 其他领域与完整插件生态 |
| 产品状态 | TUI storage/persistence；App persist/namespace；Desktop renderer storage、RPC handler/state/write-behind | App settings303-352、storage586-768；persist测试39-90、Desktop state测试27-108 | session/global-sync、draft、全部migration、Electron E2E |
| 回放与模拟 | simulation backend/provider/Timeline；HTTP recorder/replay/store；HTTP测试/support/JSON夹具 | simulation provider测试与WebSocket fixture由只读代理核验 | redaction/matching全部内部、其他transport、Drive controller/UI |
| 云端与更新 | Console proxy/responses；Stats daemon；files Worker；GUI updater main/machine/platform；TUI notification | GUI updater machine测试1-200；其他proxy调用方仅检索 | inference鉴权计费、Stats core、其他services、底层TUI安装 |

代理研究已由主代理关键正文回读整合。未读内容不作为行为断言来源。六主题矩阵补充[前轮地图](source-code-map-2.0.32.md)，不改变前轮“深读6、入口4、清单29”的历史统计。

## 定位方法

1. 从[学习地图](../spec/insights-deepening-2.0.32.md)选读者路径。
2. 在教程中找到 F 编号，回到新增事实表。
3. 点击固定 blob 链接及行号，核验函数与调用方。
4. 测试文件只说明有哪些断言定义；本轮未运行 OpenCode 源码测试。

## 验证等级

- **静态源码证据**：实现、调用方、测试定义与固定夹具阅读。
- **本轮文档验证**：OKF、链接、导航、Sphinx质量门与构建，结果由增量日志记录。
- **不在本轮验证内**：真实模型调用、云部署、计费结算、Electron运行、自动更新与全平台发布。

## 相关概念

- [前轮源码地图](source-code-map-2.0.32.md)
- [增量学习地图](../spec/insights-deepening-2.0.32.md)
