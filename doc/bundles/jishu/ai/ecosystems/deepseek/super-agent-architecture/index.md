---
okf_version: "0.2"
type: bundle
title: Super-agent 双层协作架构概念教程
description: 小枫coding 公开导读与媒体报道的分层学习教程，涵盖 Router/Worker、事件、恢复、评估与安全；非部署或源码教程，上游与实验待核验。
tags: [DeepSeek, Harness, Super-agent, Router, Worker, 事件驱动, 人机协作]
sources:
  - id: guide
    resource: https://mp.weixin.qq.com/s/gYZGu2qndS6dgCYqQHi03Q
  - id: news-pd
    resource: https://peoplesdaily.pdnews.cn/china/er/30053466920
  - id: news-pandaily
    resource: https://pandaily.com/deepseek-harness-super-agent-prototype-router-worker-event-driven-watchdog-open-source-mit
status: flagged
stale_after: 2026-12-04
generated: { by: "agent/okf-wiki", at: "2026-11-04" }
---

# Super-agent 双层协作架构概念教程

**核验边界：上游文章遇验证码，研究仓库未直接核读。** 本包整理用户指定导读与公开二手报道，不能声称全面读完上游研究、复现实验或确认生产功能。状态保持 `flagged`；[核验页](references/verification.md)列明缺口。

读者可沿“协调负担、职责分配、事件与恢复、评估与安全”学习架构问题。适合已接触 AI 会话与任务委派的读者；术语在正文解释。没有安装或运行前置条件，不需提交凭证。

## 文档导航

| 入口 | 内容 |
|---|---|
| [概念学习路径](concepts/index.md) | 四篇递进教程及知识地图 |
| [信源与核验](references/index.md) | 来源登记、30项事实、逐项核验 |
| [更新记录](log.md) | 方法论链路、验证与待办 |

## 使用范围

本包为概念解读，非操作教程，不建 `examples/`。初步实验、许可和团队归属仅按媒体转述登记；性能数字不进入正文结论。对权限、恢复、订阅寿命和评估的展开是执行者分析，不能当作源码描述。

截至 2026-11-04，本次读到指定导读正文和两篇公开报道，未读到导读配图细节、上游正文及原型代码。复核日期为 2026-12-04，更新前不解除证据限定。

## 主题关联

- [DeepSeek Agent 生态资源](../awesome-deepseek-agent/index.md)：资源与工具集成入口，本包聚焦双层架构的概念学习。
- [AI 工程方法论](../../../practice/ai-engineering-methodology/index.md)：工程方法论扩展阅读，不用于替代本包的事实来源。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
