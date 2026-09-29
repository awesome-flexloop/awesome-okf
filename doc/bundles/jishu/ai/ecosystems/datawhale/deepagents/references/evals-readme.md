---
title: libs/evals/README.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/evals/README.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/evals/README.md
---

# libs/evals/README.md 引用

Deep Agents Evals 评估套件概览。

## 核心内容

- **定位**：Deep Agents SDK 的端到端行为评估套件，每个评估针对真实 LLM 运行 Agent，捕获完整轨迹（工具调用、文件变更、最终响应），从正确性和效率评分
- **参考文档**：EVAL_CATALOG.md（完整评估和类别列表）、MODEL_GROUPS.md（评估工作流使用的模型目录）
- **Harbor 集成**：包含 Harbor 集成，用于运行沙箱基准测试如 Terminal Bench 2.0
- **结果链接**：
  - Evals CI：evals.yml 工作流，LangSmith 项目 deepagents-evals
  - Harbor CI：harbor.yml 工作流，LangSmith 项目 deepagents-harbor
- **贡献**：架构、编写新评估、类别系统、Harbor 设置、LangSmith 集成均记录在 CONTRIBUTING.md

## 相关概念

- Evals评估套件
