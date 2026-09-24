---
okf_version: "0.2"
type: Reference
title: "ZDTaichu5.0-9B 核验报告"
description: "对模型架构、能力范围、训练方案、基准结果和具身部署边界进行信源距离与可复现性审查。"
tags: [核验, 勘误, 具身智能, 空间推理]
generated: { by: "process:blog-article-to-okf-wiki:R/V", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/YOW4mB8Dg6loiKDfzF_NHQ?from=industrynews&color_scheme=light#rd
  - id: official-blog
    url: https://taichu-ai.github.io/ZDTaichu5.0-9B/
  - id: github
    url: https://github.com/Taichu-AI/ZDTaichu5.0-9B
  - id: huggingface
    url: https://huggingface.co/TaichuAI/ZDTaichu5.0-9B
---

# 核验报告

> **状态：flagged。** 官方页面支持模型定位、架构和目录事实；基准排名、具体分数与真实机器人效果仍主要是发布方报告，未找到独立复现实验。

## 1. 信源距离

| 声明 | 处理 | 结论 |
|---|---|---|
| 标题、作者、日期 | 浏览器读取原文 | 可确认 |
| 9B、输入模态、模型定位 | 官方 Blog、GitHub、Hugging Face | 已核验 |
| Qwen3.5-9B + C-RADIOv4-H | 官方 Blog | 已核验 |
| `recurrent_reasoning/` | 官方 GitHub | 已核验 |
| 九项基准八项第一及具体分数 | 官方 Blog/文章转述 | 仅确认发布方报告，未独立复现 |
| 1.28T tokens、GRPO 奖励细节 | 文章与官方说明 | 单源或发布方自述 |
| 科研自动化、智能制造和机器人收纳演示 | 官方定性演示 | 不等于生产环境性能保证 |

## 2. 勘误四张清单

### 日期与版本

- 文章日期按微信公众号页面登记为 2026-09-22。
- 未在正文中补写未确认的模型版本号、推理框架版本或硬件要求。

### 成效数字

- 基准分数和“超过 Gemini 3 Pro、Grok 4、GPT-5.2”等比较，保留为“官方/文章报告值”。
- 未找到公开的独立复现实验、完整评测脚本和统一硬件环境，因此不写成普遍性能结论。

### 口径对照

- “九项基准”“八项第一”限定于官方定义的同参数模型比较组与报告设置。
- “真实场景验证”是定性演示，不能推导吞吐、成功率、延迟或安全等级。

### 引文与观点

- “小模型更有优势”属于作者判断，正文与 F-017 保持观点层级。
- 模型是高层规划器，不是端到端机器人控制系统；安全控制边界以 F-016 为准。

## 3. 可复现性判定

两问均为“否”：

1. 文章没有给出完整安装、配置、调用和部署流程。
2. 文章没有提供版本、输入输出样例、运行日志或可复验实验设计。

因此本 bundle 不创建 `examples/`，也不把演示截图改写成操作教程。

## 4. 对抗审查结论

- **事实视角**：模型架构和目录事实有官方来源；成绩数字均保留报告属性。
- **结构视角**：根索引、concepts、references 和 log 均接入 toctree。
- **读者视角**：明确区分官方事实、文章转述、作者观点和未独立验证结果。
- **时效视角**：模型代码、评测表和仓库状态会变化，`stale_after` 设为 2026-12-31。
