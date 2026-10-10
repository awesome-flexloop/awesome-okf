---
type: Concept
title: Cua 项目概览：给 AI Agent 一台能用的电脑
description: Cua 项目身份（Cua AI, Inc./MIT/trycua/cua）、Computer-Use 2.0 理念、三大难题、三类目标人群、官方核验的仓库事实
tags: [Cua, Computer-Use, AI Agent, trycua, MIT, 开源]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T10:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-finops-cua
    resource: https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg
    title: 《开源精选 | Cua》（FinOps实战，2026-09-26）
  - id: github-api-cua
    resource: https://api.github.com/repos/trycua/cua
    title: GitHub API：trycua/cua 仓库元数据
---

# Cua 项目概览：给 AI Agent 一台能用的电脑

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

## 1. 项目身份

Cua（读作 /kjuːə/）是面向 Computer-Use（计算机使用）场景的开源基础设施项目，由 Cua AI, Inc. 开发，采用 **MIT 协议**，仓库位于 `github.com/trycua/cua`，官方口号是 **"Give AI agents computers they can use"**——给 AI Agent 提供可操作的电脑（F-004）。

> ⚠️ **主体口径说明（F-054）**：GitHub 仓库 owner 为 Organization `trycua`（id 191107687）；博文所称"Cua AI, Inc."为官网品牌运营主体，GitHub API 无法直接证实该法律实体注册名。

它不是一个模型，也不是一个聊天框架，而是一整套 Computer-Use 基础设施：开源桌面自动化驱动、隔离的云桌面集群、本地 macOS 虚拟机、专用决策小模型，以及评测基准（F-005）。

## 2. 官方核验的仓库事实

| 项目 | 值 | 来源 |
|------|-----|------|
| 仓库 | trycua/cua（id 925270205） | F-054 |
| 创建时间 | **2025-01-31T15:02:49Z** | F-054 |
| 默认分支 | main | F-054 |
| 官网 | https://cua.ai | F-054 |
| 许可证 | **MIT License** | F-056 |
| README 副标题 | "Scale computer-use 2.0 with open-source drivers, cross-OS fleets, and benchmarks for training, evaluation, and data generation." | F-056 |
| 时点快照（2026-10-10） | stars 29,189 / forks 2,061 / open_issues 1,149 | F-055 |

## 3. Computer-Use 2.0 理念

博文提出：现在的 AI Agent 想操作真实电脑（点按钮、填表单、开应用），面临三大难题（F-006）：

1. **没有安全隔离的执行环境**——Agent 误操作可能毁掉你的主机；
2. **缺少跨 macOS / Windows / Linux 的统一自动化接口**；
3. **没有标准化的评测手段**，无法量化 Agent 到底"会不会用电脑"。

Cua 官方提出的 **Computer-Use 2.0** 理念认为：Agent 应该能在同一个任务中自由穿梭于**代码、API 和图形界面**之间（F-007）。官方定义与之完全一致："an agent moving between code, APIs, and graphical interfaces within the same task"（F-062）。

这意味着 Cua 不是"只会点鼠标"的演示工具，而是规模化（Scale）的基础设施——README 副标题已经点明：用开源驱动、跨操作系统集群和基准测试，规模化支撑**训练、评估与数据生成**（F-008）。

## 4. 三类目标人群

一个项目覆盖三条工作流（F-009）：

| 人群 | 使用模块 | 目的 |
|------|---------|------|
| 做 Agent 产品的工程师 | Cua Driver | 接入桌面自动化能力 |
| 做模型训练的研究员 | Fleets + Bench | 批量生成轨迹数据 |
| 做安全隔离运维的团队 | Lume / Fleets | 提供沙箱环境 |

## 5. 为什么是"基础设施"而不是"玩具"

很多 computer-use 演示项目只解决"让 Agent 点一下鼠标"的问题，而 Cua 解决的是规模化问题（F-008、F-041）。它同时覆盖执行层（Driver / Fleets / Lume）、模型层（CUA-S1）与评测层（Bench），并且用 MIT 开源组合拳全部交付——这是它在同类项目中的核心壁垒（F-041）。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 五大核心模块：[01-five-core-modules.md](01-five-core-modules.md)
- Stars 趋势：[03-stars-and-momentum.md](03-stars-and-momentum.md)