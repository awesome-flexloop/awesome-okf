---
type: Concept
title: 五大核心模块：Driver、Fleets、Lume、CUA-S1、Bench
description: Cua 五大核心模块架构详解——Cua Driver 后台桌面自动化、Cua Fleets 隔离云桌面、Lume 本地 macOS 虚拟机、CUA-S1 决策模型、Cua Bench 评测基准
tags: [Cua, Cua Driver, Cua Fleets, Lume, CUA-S1, Cua Bench, 架构]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T10:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-finops-cua
    resource: https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg
    title: 《开源精选 | Cua》（FinOps实战，2026-09-26）
  - id: cua-driver-pypi
    resource: https://libraries.io/pypi/cua-driver
    title: Libraries.io：cua-driver PyPI 页（含官方 README 摘要）
---

# 五大核心模块：Driver、Fleets、Lume、CUA-S1、Bench

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

Cua 由五个紧密集成的模块构成，覆盖"执行环境 → 操作驱动 → 决策模型 → 评测闭环"的完整链条（F-010~F-014）：

```
┌────────────────────────────────────────────────────────────┐
│                    AI Agents & Models                      │
│        (Claude Code / Codex / Cursor / CUA-S1 ...)         │
└──────────────────────────┬─────────────────────────────────┘
                           │ CLI / MCP / 类型化 SDK
┌──────────────────────────▼─────────────────────────────────┐
│                       Cua Driver                            │
│        （macOS / Windows / Linux 后台桌面自动化驱动）          │
└──────────┬────────────────────────────┬─────────────────────┘
           ▼                            ▼
   [ Cua Fleets ]                [ Lume VMs ]
   (隔离云桌面集群)            (Apple Silicon 本地虚拟机)
           └──────────┬─────────────────────┘
                      ▼
            [ Cua Bench 评测闭环 ]
            （数据生成 → 训练 → 评估）
```

## 1. Cua Driver：后台桌面自动化驱动

Cua Driver 让 Agent 检查并操作 macOS、Windows、Linux 上的**原生应用和浏览器**，支持 **CLI、MCP 和类型化 SDK** 三种接入方式（F-010）。

其标志性能力是**「后台投递」**：在应用和平台支持的前提下，Agent 干活时不会抢占你的鼠标指针和窗口焦点（F-010）。官方文档将其概括为 "no-foreground contract"——Agent 可以在后台驱动应用，你继续用你的电脑。

官方入门任务（F-029）：连接你的 Agent，让它打开计算器算 **6 × 7**，并验证应用界面上确实显示 **42**（F-061）。这个任务完整走通"Agent 决策 → 驱动执行 → 结果验证"的闭环。

## 2. Cua Fleets：隔离云桌面集群

Fleet 维护一池沙箱容量，你的代码从池中**认领一台桌面**，用 Sandbox SDK 在里面跑命令、截屏、操作应用，**用完即弃**，安全隔离（F-011）。

- 云端入口：run.cua.ai（F-036）
- 适用：批量并行任务、不可信 Agent 执行、可扩展的评测运行
- 注意：Fleet 池在认领结束后可能保留**付费容量**，官方教程有完整清理步骤（F-038）

## 3. Lume：本地 macOS 虚拟机

Lume 基于 **Apple Virtualization.Framework**，在 Apple Silicon 上创建和管理 macOS / Linux 虚拟机，适合本地开发和数据生成（F-012）。

- 从 Apple 恢复镜像直接创建原生 **macOS Tahoe** 虚拟机（F-031）
- 启动后通过 SSH 连接，**全程无人值守**（F-031）
- 需要 Apple Silicon 芯片的 Mac（F-031）

## 4. CUA-S1：System 1 决策模型家族

CUA-S1 是官方自研的**小型专用「System 1」决策模型家族**，主打表单场景：对结构化界面元素和文档取值做**快速打分决策**，而不是逐 token 生成回复（F-013）。

- 定位：执行层的高频快决策模型，复杂规划交给上层大模型
- 授权：**源码 MIT 开源**，模型权重托管在 Hugging Face（F-013）
- 状态：早期研究性发布（**source-only**），生产环境慎用（F-049）

> ✅ **核验（F-063）**：CUA-S1 于 2026-09-19 前后被第三方报道确认开源，报道描述其解决"高频桌面操作"的执行层瓶颈；权重在 Hugging Face 按各自卡片条款授权，与博文 source-only 口径一致。

## 5. Cua Bench：评测基准

Cua Bench 用于构建 computer-use 任务、评估 Agent 表现、导出训练轨迹，形成 **「数据生成 → 训练 → 评估」的闭环**（F-014）。

- 第一个评测任务**不需要虚拟机、Docker 或模型 API Key**（F-035）
- 创建小任务 → 运行参考解法 → 验证评估器给出 reward = 1.0 → 自己完成任务（F-035）
- 导出的轨迹可用于强化学习训练（F-044）

## 模块协同：一套 SDK 贯穿本地与云端

本地沙箱与云端 Fleet 共享**同一套 Sandbox SDK**，代码可以无缝迁移（F-037）。这意味着你可以在本地开发、验证，再平滑地把同一套流程放到云端大规模执行。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 项目概览：[00-project-overview.md](00-project-overview.md)
- 快速上手：[04-getting-started.md](04-getting-started.md)