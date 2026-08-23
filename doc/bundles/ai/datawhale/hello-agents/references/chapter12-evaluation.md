---
title: 第十二章 智能体性能评估
type: reference
bundle: /datawhale/hello-agents
chapter: 12
part: 第三部分：高级知识扩展
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/第十二章%20智能体性能评估.md
---

# 第十二章 智能体性能评估

## 章节概要

本章构建HelloAgents评估体系，覆盖工具调用评估（BFCL）、通用能力评估（GAIA）和数据生成质量评估三大场景。

## 核心知识点

### 评估的独特挑战
1. **输出不确定性**：同一问题多个正确答案
2. **标准多样性**：工具调用检查签名，问答评估语义
3. **成本高昂**：大量API调用
4. **多步轨迹**：需评估中间步骤合理性

### 工具调用评估基准

**BFCL（Berkeley Function Calling Leaderboard）**：
- UC Berkeley推出
- 1120+测试样本
- 四个类别：simple、multiple、parallel、irrelevance
- AST（抽象语法树）匹配算法
- 数据集规模适中，社区活跃

**ToolBench**：清华，16000+真实API场景
**API-Bank**：Microsoft，53个常用API

### 通用能力评估基准

**GAIA（General AI Assistants）**：
- Meta AI + HuggingFace联合推出
- 466个真实世界问题
- Level 1/2/3三级难度
- 评估多步推理、工具使用、文件处理、网页浏览
- 准精确匹配（Quasi Exact Match）算法
- 任务真实、综合性强

**AgentBench**：清华，8个领域任务
**WebArena**：CMU，真实网页环境交互

### 多Agent协作评估
- ChatEval：多Agent对话质量
- SOTOPIA：社交场景互动

### 评估指标体系

**准确性**：Accuracy、Exact Match、F1、Quasi Exact Match
**效率**：Response Time、Token Usage、工具调用次数
**鲁棒性**：Error Rate、Failure Recovery
**协作**：Communication Efficiency、Task Completion

### 评估方法

1. **自动化匹配**：
   - AST匹配：函数调用结构比较
   - 准精确匹配：标准化后比较（去空白、统一大小写）

2. **LLM Judge**：
   - 强大AI模型作为评判者
   - 质量评分、优劣比较
   - 注意评判偏差和位置偏好

3. **Win Rate**：
   - 两两比较统计胜率
   - 用于模型对比和数据生成质量

4. **人工验证**：最终质量把关

### HelloAgents评估体系

```
evaluation/benchmarks/
├── bfcl/              # BFCL工具调用评估
│   ├── dataset.py
│   ├── evaluator.py   # AST匹配
│   ├── metrics.py
│   └── ast_matcher.py
├── gaia/              # GAIA通用能力评估
│   ├── dataset.py
│   ├── evaluator.py   # 准精确匹配
│   ├── metrics.py
│   └── quasi_exact_match.py
└── data_generation/   # 数据生成质量评估
    ├── dataset.py     # AIME数据集
    ├── llm_judge.py
    └── win_rate.py
```

评估工具也遵循"万物皆工具"理念，封装为bfcl_evaluation_tool、gaia_evaluation_tool、llm_judge_tool、win_rate_tool。

### 评估-训练闭环
SFT基线评估 → GRPO奖励信号 → 迭代数据增强 → 持续监控回归

## 配套代码（code/chapter12/）
8个脚本：BFCL快速开始/自定义评估/完整运行、GAIA快速开始/最佳实践、数据生成完整流程/LLM评判

## 相关概念
- [评估方法](/ai/datawhale/hello-agents/concepts/evaluation-methods)
- [Agentic-RL](/ai/datawhale/hello-agents/concepts/agentic-rl)
