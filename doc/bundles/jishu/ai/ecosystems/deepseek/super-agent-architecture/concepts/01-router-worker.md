---
type: Concept
title: Router 与 Worker 的职责分配
description: 解释统一交互、独立上下文和订阅直达的区别，分析双层架构的边界。
sources:
  - id: facts
    resource: ../references/facts.md
  - id: guide
    resource: https://mp.weixin.qq.com/s/gYZGu2qndS6dgCYqQHi03Q
  - id: news-pandaily
    resource: https://pandaily.com/deepseek-harness-super-agent-prototype-router-worker-event-driven-watchdog-open-source-mit
status: flagged
stale_after: 2026-12-04
generated: { by: "agent/okf-wiki", at: "2026-11-04" }
---

# Router 与 Worker 的职责分配

Router 可以理解为接待与派工会话；Worker 则是处理具体任务的执行会话。导读用这两层说明 Super-agent：用户面对统一协作者，任务在多个独立上下文中推进。[F-007 至 F-010](../references/facts.md)

## 两类上下文

| 组件 | 来源描述的职责 | 教学上需要区分的信息 |
|---|---|---|
| Router | 统一交互、派工、维持共享背景 | 用户目标、任务关联、进度摘要 |
| Worker | 在独立上下文执行任务 | 当前任务的材料、过程与结果 |
| 订阅机制 | 相关消息送到对应 Worker | 哪条讨论属于哪个仍在处理的任务 |

独立上下文并不等于安全隔离。来源描述的是会话结构；文件、凭证、工具进程和网络是否隔离，需另看实现。多个 Worker 修改同一文件仍可能冲突，这是设计推论，不是本次发现的原型缺陷。

## 消息流不必都经过 Router

依据导读与 Pandaily 的二手描述，可以用下列文字路径理解：[F-008 至 F-010、F-026](../references/facts.md)

1. 新请求到达统一交互入口。
2. Router 判断任务归属并分派。
3. Worker 在任务上下文中处理。
4. 已归属线程的新消息，经订阅送到相关 Worker。
5. Worker 报告进度或结果，由统一入口衔接用户。

这是教学用概念路径，不是官方 API、严格时序协议或源码复现。Pandaily 还称 Router 可不具备 Bash 工具，而 Worker 向 Router 汇报；仓库未核读，不能把该说法升级为实现契约。[F-026](../references/facts.md)

## 为什么订阅需要生命周期

以下为执行者分析：订阅减少重新判断消息归属的需求，同时增加了状态管理责任。任务完成后仍接收旧线程消息，可能出现重复动作；同一事件被多个 Worker 当作新请求，可能重复派工；线程关联错误则可能把材料送到无关任务。

一个设计评审应能回答：谁建立订阅、谁撤销、线程是否能重开、事件是否去重、失败后是否重放。来源未给出这些问题的可核验实现，因此教程保留为提问，不补造数据库表或接口。

## 与临时子代理的区别

临时子代理通常围绕一次委派处理子任务；本包讨论的双层方案还涉及持续交互、外部事件和任务订阅。不能只看到“多个 Worker”就认定所有多智能体框架都等价。也不能仅凭组件名称认定新架构优于旧架构：需要同任务、同资源和同验收口径的比较。

继续阅读[事件与恢复](02-events-and-recovery.md)，理解会话之外的运行机制。
