---
type: Concept
title: "MAI-UI 项目概述：GUI Agent 基础模型家族仓库"
description: "MAI-UI 是通义 Tongyi-MAI 的 GUI Agent 基础模型家族仓库（2B/8B/32B/235B-A22B），src 为 OpenAI 兼容 API 客户端外壳，权重外置；并澄清与续作 Qwen-UI-Agent 的版本关系。"
tags: [MAI-UI, GUI智能体, 基础模型, Tongyi-MAI, 项目概述]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mai-ui-facts
    resource: /references/facts.md
    title: MAI-UI 源码事实台账
  - id: mai-ui-sources
    resource: /references/source-registry.md
    title: MAI-UI 信源登记
---

MAI-UI 是通义 Tongyi-MAI 团队发布的 GUI Agent（图形界面智能体）基础模型家族仓库：README 标题为 MAI-UI，声明提供 2B/8B/32B/235B-A22B 四个尺寸的 GUI agent 基础模型，其中 MAI-UI-2B 与 MAI-UI-8B 权重已在 HuggingFace（Tongyi-MAI 组织）发布，技术报告为 arXiv:2512.22047（F-001）。需要特别注意：仓库内 `src/` 并不包含模型权重或训练/推理框架，而是纯 OpenAI 兼容 API 客户端外壳——根 `requirements.txt` 仅有 Jinja2、numpy、openai、Pillow 四个包，无 torch/transformers（F-003），模型服务一律外置到 vLLM（F-004）。

本篇是整个束的入口：先厘清"仓库里有什么、没什么"，再给出目录地图与版本谱系，最后并入博客站（MAI-UI-blog）登记的模型家族声明与基准表概览。

## 仓库里有什么：目录地图

仓库根的目录结构如下（F-006）：

```
MAI-UI/
├── src/                    # 6 个 Python 文件：Agent 实现核心
│   ├── base.py             # BaseAgent 抽象基类（F-009~F-011）
│   ├── unified_memory.py   # TrajStep / TrajMemory 数据结构（F-007、F-008）
│   ├── mai_grounding_agent.py   # 无基类的定位代理（F-017~F-022）
│   ├── mai_naivigation_agent.py # 继承 BaseAgent 的导航代理（F-023~F-034）
│   ├── prompt.py           # 4 个 prompt 模板（F-013~F-016）
│   └── utils.py            # 5 个图像/坐标工具函数（F-012）
├── evaluation/grounding/   # 评估管线：模型封装、eval_local、eval_server、extract_metrics
├── cookbook/               # grounding.ipynb、run_agent.ipynb 两个可复现 notebook
├── tests/                  # test_mai_navigation_agent.py + output_messages/ 8 个 JSON 基线
├── resources/example_img/  # figure1~5.png 示例图
├── README.md / LICENSE / NOTICE / requirements.txt
└── .github/workflows/deploy-pages.yml   # GitHub Pages 部署 workflow（仅确认存在，F-054）
```

克隆后得到的是"Agent 使用侧"的全部代码：双 Agent（grounding 定位 + navigation 导航）、prompt 模板、评估脚本与两个 notebook。仓库里没有的是模型权重与训练代码——推理必须先起 vLLM 服务（见 [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)）。

## 许可证与依赖

- **许可证**：`LICENSE` 为 Apache License Version 2.0 全文；`NOTICE` 声明产品版权归 "Alibaba Cloud and its affiliates"，并列出第三方组件及其许可证：Jinja2（BSD-3-Clause）、NumPy（BSD-3-Clause）、OpenAI Python Client（Apache-2.0）、Pillow（HPND）（F-002）。
- **依赖**：根 `requirements.txt` 锁定 `Jinja2==3.1.6`、`numpy==2.3.5`、`openai==2.13.0`、`Pillow==12.0.0` 四包（F-003）。这份极简依赖正是"src 是 API 客户端而非模型运行时"的直接证据——模型的加载与推理在仓库外的 vLLM 服务中完成。

## 版本谱系：与 Qwen-UI-Agent 的关系

伞仓 README（`Tongyi-MAI/MAI-UI/README.md`）标题为 "MAI-UI × Qwen-UI-Agent"，其 Projects 章节列出两个子目录：`Qwen-UI-Agent/` 标注为 "continuation work of MAI-UI"（arXiv:2607.28227），`MAI-UI 1.0/` 标注为 "original MAI-UI repository content"（F-053）。也就是说，**MAI-UI 是前代项目，Qwen-UI-Agent 是其续作**——已发布的 MAI-UI-2B/8B 权重属于 MAI-UI 1.0 这一代（F-001）。

这一谱系关系对使用既有 [Qwen-UI-Agent 知识束](../../qwen-ui-agent/index.md) 的读者尤为重要：该束记载的"MAI-UI 2B/8B 是 2025-12 前代权重、Qwen-UI-Agent 自身权重未发布"的勘误，可在本仓库的伞仓 README（F-053）与根 README（F-001）中找到仓库级权威出处。

## 博客站（MAI-UI-blog）登记概览

MAI-UI 项目主页（`site/index.html`）标题为 "MAI-UI: Real-World Centric Foundation GUI Agents"，Paper 按钮指向 arXiv:2512.22047（F-025）；作者列表含 Hanzhang Zhou*、Xu Zhang* 等共 11 人，机构署名 "Tongyi Lab, Alibaba Group"（F-026）；资源链接矩阵提供 Paper / Code（github.com/Tongyi-MAI/MAI-UI）/ HuggingFace / ModelScope / MobileWorld / Cite 六个按钮，并提供中英文切换页 `index_zh_cn.html`（F-027）。

- **模型家族声明**：站点 promotion 文案原文 "MAI-UI is a family of foundational GUI agent models from Tongyi-MAI Lab, ranging from 2B to 235B."，Technical Highlights 段声明首次将用户交互、MCP 工具调用、端云协同三项核心能力统一进一个架构（当前开源 2B 与 8B）（F-028）。
- **四大亮点卡**：MCP Tool Usage、User Interaction、Online Reinforcement Learning、Device-Cloud Collaboration（F-029）。
- **站点结构**：七个 section（overall_performance / highlights / demo / mobileworld / grounding / navigation / citation），hero 区嵌 Bilibili 视频（F-030）。
- **基准表（HTML 表可引用）**：AndroidWorld 成功率表中 MAI-UI-235B-A22B 以 76.7 为全表最高（MAI-UI-2B 49.1 / 8B 70.7 / 32B 73.3）（F-033）；MobileWorld 表按 GUI-Only (116) / User-Int. (45) / MCP (40) / Overall 分列，MAI-UI-235B-A22B overall 41.7（GUI-Only 39.7 / User-Int. 51.1 / MCP 37.5，均加粗为列最高）（F-034）；ScreenSpot-Pro 定位表已读部分含 MAI-UI-2B 57.4 及其 + Zoom-In 子行 62.8（F-035）。

⚠️ **博客边界**：站点下 `Grounding-Blog` 与 `MobileWorld-Blog-Post` 两页为 Notion 重定向 stub（F-036、F-037），仅存在重定向脚本，正文内容未采集——本束及全束文档一律不引用这两篇博客的正文，只登记其 URL 字面标题（"Why your AI Agent keeps misclicking: A Practical Grounding Guide for Frontier Models" / "MobileWorld Update: Can Frontier Models Really Control Your Phone? Evaluating End-to-End Mobile Use"）。上述基准分数均出自站点 HTML 表格页而非博客正文。

## 已知边界

- 32B 与 235B-A22B 两个尺寸的权重截至事实采集日未见 HuggingFace 发布记录（F-001 仅确认 2B/8B 已发布）。
- 仓库内 `.github/workflows/deploy-pages.yml` 仅确认存在、内容未展开（F-054），不据此推断 CI 行为。
- 博客站 HTML 表与 `leaderboard.json` 收录范围不一致（json 无 MAI-UI 条目），跨信源引用分数须注明出处文件（详见 [/concepts/06-evaluation-pipeline.md](/concepts/06-evaluation-pipeline.md) 与 [信源登记](/references/source-registry.md)）。

## 相关概念

- [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)：vLLM 服务部署与双 Agent 初始化
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：4 个 prompt 模板与 10/12 种动作空间
- [/references/source-registry.md](/references/source-registry.md)：本篇引用的全部信源文件清单
- [Qwen-UI-Agent 技术评测束](../../qwen-ui-agent/index.md)：MAI-UI 的续作项目，含博文实测与版本谱系勘误
- [MobileWorld 评测环境束](../../mobile-world/index.md)：MAI-UI 导航 Agent 以注册名 `mai_ui_agent` 接入的评测环境
