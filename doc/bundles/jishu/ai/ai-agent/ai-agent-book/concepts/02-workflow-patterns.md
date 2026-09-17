---
okf_version: "0.2"
type: Concept
title: "工作流模式：链式、并行、Orchestrator 与 2.0 的二分叙述"
description: "博文展示的三种工作流模式原图核验——仓库实有5张fig1-wf模式图（含routing/evaluator），2.0第一章改为工作流（确定性编排）vs自主Agent（动态决策）二分，含停止条件与适配层内化观点"
tags: [AI Agent, 工作流, Chaining, Parallel, Orchestrator, 自主Agent, ReAct, 模式]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T21:00:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T21:00:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/XL9UWNcrC9BwQw8BbShHOA
    title: 杰克王聊AI博文（2026-08-01）
  - id: github-repo
    url: https://github.com/bojieli/ai-agent-book/tree/main/book/images
    title: 原书配图目录 book/images（fig1-wf-*.svg）
  - id: chapter1
    url: https://github.com/bojieli/ai-agent-book/blob/main/book/chapter1.md
    title: 原书第一章（main 分支 2.0）
---

# 工作流模式：从三种配图到 2.0 的二分叙述

> **口径提示（勘误 E3）**：博文称"第 1 章讲**四种**经典 Agent 工作流模式"，并展示链式、并行、Orchestrator 三种原书 SVG（F-018）。核验发现：博文时点仓库 `book/images/` 实有 **5 张**工作流模式图；2.0 版第一章正文已改用"工作流 vs 自主 Agent"二分叙述（F-033）。本文按核验后的完整口径呈现，博文 1.4 旧版口径显式标注。

## 一、博文展示的三种模式（F-018）

博文从第 1 章配图中选取三张（文件名已在仓库核验，F-033）：

| 模式 | 原书图文件 | 直观含义 |
|------|-----------|---------|
| 链式调用（Chaining） | fig1-wf-chaining.svg | 多个处理步骤按固定顺序串联，前一步输出是后一步输入 |
| 并行调用（Parallel） | fig1-wf-parallel.svg | 多个步骤同时执行后再汇总 |
| Orchestrator（编排者-执行者） | fig1-wf-orchestrator.svg | 一个编排者 Agent 动态分派子任务给执行者 Agent |

博文评价："书里类似的架构图贯穿每一章，不是摆设，是跟正文一一对应的。"

## 二、核验：仓库实有 5 张模式图（F-033）

博文时点 `book/images/` 目录中的完整 fig1-wf 系列为：

1. `fig1-wf-chaining.svg` — 链式
2. `fig1-wf-parallel.svg` — 并行
3. `fig1-wf-orchestrator.svg` — 编排者-执行者
4. **`fig1-wf-routing.svg`** — 路由（按输入类别分流到不同处理路径）
5. **`fig1-wf-evaluator.svg`** — 评估者-优化者（生成→评估→回环修正）

博文说"四种……下面是其中三种"，既未穷尽 5 张图，"四种"的数字也与仓库资产不符；其配图取自旧版 PDF（1.4 及更早版本曾以模式枚举组织第 1 章）。读者若按博文索骥在现行正文中查找"四种模式"文字，会找不到对应小节——这是本包标注 ⚠️ 的原因，但博文展示的 3 张图本身确为原书资产，内容不存在虚构。

## 三、2.0 版现行叙述：工作流 vs 自主 Agent（F-033）

2.0 第一章不再枚举模式清单，而是用一条轴组织两类系统：

### 工作流（Workflow）：确定性的编排

- 定义：通过**预定义的代码路径**编排 LLM 和工具；执行路径确定，每步做什么、下一步去哪里由代码写死，LLM 只在节点内部负责理解与生成。
- 原书示例（订机票）：核实身份 → 搜索航班 → 完成付款 → 确认预订，四个固定节点。
- 两个核心优势：
  1. **严格流程控制**——"付款前不能预订"类业务规则由代码强制执行，不依赖 LLM 判断；
  2. **安全性**——提示注入或模型犯错最多影响当前节点内部，无法跳到不该执行的分支，攻击面被限制在单节点。
- 主要局限：**缺乏变通性**，预设未覆盖的情况只能走异常分支或交还人类。
- 原书另举文生图两节点工作流（LLM 改写提示词 → 调用 Stable Diffusion），并把这类"给模型能力短板打补丁的 Harness 代码"称为**适配层**——一旦多模态模型具备原生图像生成能力，该适配层即被模型内化而消失。

### 自主 Agent（Autonomous Agent）：动态自主决策

- 定义：执行路径不预先定义，Agent 根据**环境反馈实时决定**下一步（如订票时发现要登录就先核实身份、发现要转机就主动询问用户）。
- 能力要求：自主规划、识别失败并调整策略，而不是出错即停。
- 必备约束：明确的**停止条件**（任务完成 / 达到最大迭代次数 / 不可恢复错误），防止死循环或过度执行。
- 实现本质：在一个循环中使用工具的 LLM，持续获取环境反馈推进任务——即 **ReAct 循环**；常见退出条件：调用最终输出工具、模型返回无工具调用的响应、出错或达到最大轮数。
- 典型适用：开放式、步骤数不可预测的问题——SWE-bench 类 Coding 任务、Computer Use、迭代式研究任务。
- 代价与治理：更高成本与复合错误风险；须在沙盒充分测试、设置护栏监控、关键决策点加入人机协作检查点。

## 四、阅读建议

- 想看 5 张模式图：克隆仓库后查阅 `book/images/fig1-wf-*.svg`（图片资产在 2.0 仍保留，F-033）。
- 想理解"什么时候用工作流、什么时候用自主 Agent"：2.0 第一章该小节末配有思考题（如订票客服系统能否混用两种模式）——实践中二者常混合：关键业务路径用工作流锁死，开放子任务交给自主 Agent。
- 与同组知识包的延伸：多 Agent 编排的框架级实现见 [orca](../../orca/index.md) 与 [veadk-python](../../veadk-python/index.md) 的 Sequential/Parallel/Loop/Supervisor 组合模式。
