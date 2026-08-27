---
title: 智能体评估方法
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/agentic-rl
  - /datawhale/hello-agents/concepts/agent-paradigms-react
  - /datawhale/hello-agents/references/chapter12-evaluation
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/第十二章%20智能体性能评估.md
---

# 智能体评估方法

智能体评估回答三个核心问题：Agent是否具备预期能力？在不同任务上表现如何？与其他Agent相比处于什么水平？评估是构建可靠、可改进的Agent系统的闭环关键。

## 评估的独特挑战

与传统软件测试不同，智能体评估面临：

1. **输出不确定性**：同一问题可能有多个正确答案，难以简单判断对错
2. **评估标准多样性**：工具调用需检查函数签名，问答需评估语义相似度
3. **评估成本高昂**：每次评估需要大量API调用，成本可达数百元
4. **多步轨迹评估**：不仅看最终结果，还需评估中间步骤的合理性

## 主流评估基准

### 工具调用能力评估

| 基准 | 推出方 | 规模 | 评估方法 | 特点 |
|------|--------|------|---------|------|
| **BFCL** | UC Berkeley | 1120+样本 | AST匹配 | simple/multiple/parallel/irrelevance四类，社区活跃 |
| **ToolBench** | 清华大学 | 16000+场景 | - | 真实世界复杂工具使用 |
| **API-Bank** | Microsoft | 53个API | - | API文档理解与调用 |

**BFCL**是教程重点实现的基准，使用AST（抽象语法树）匹配算法评估函数调用的准确性，不依赖字符串精确匹配，能容忍参数顺序等表面差异。

### 通用能力评估

| 基准 | 推出方 | 规模 | 评估方法 | 特点 |
|------|--------|------|---------|------|
| **GAIA** | Meta + HuggingFace | 466题 | 准精确匹配 | Level 1/2/3三级难度，真实世界任务 |
| **AgentBench** | 清华大学 | 8个领域 | - | 全面评估通用能力 |
| **WebArena** | CMU | - | - | 真实网页环境交互 |

**GAIA**是教程重点实现的基准，任务包含多步推理、工具使用、文件处理、网页浏览等，使用**准精确匹配（Quasi Exact Match）**算法——在精确匹配基础上容忍格式差异、大小写等。

### 多智能体协作评估
- **ChatEval**：多Agent对话系统质量评估
- **SOTOPIA**：社交场景互动能力评估

## 评估指标体系

### 准确性指标
- **Accuracy（准确率）**：正确回答占比
- **Exact Match（精确匹配）**：答案与标准答案完全一致
- **F1 Score**：精确率和召回率的调和平均
- **Quasi Exact Match（准精确匹配）**：容忍格式差异的匹配

### 效率指标
- **Response Time（响应时间）**：端到端延迟
- **Token Usage（Token使用量）**：输入+输出token总数
- **工具调用次数**：完成任务所需的工具调用轮数

### 鲁棒性指标
- **Error Rate（错误率）**：失败任务占比
- **Failure Recovery（故障恢复）**：从错误中恢复的能力

### 协作指标
- **Communication Efficiency（通信效率）**：Agent间消息数量与质量
- **Task Completion（任务完成度）**：子任务完成比例

## 评估方法

### 1. 自动化匹配
- **AST匹配**：解析函数调用为语法树进行结构比较
- **准精确匹配**：标准化答案后比较（去除空白、统一大小写等）

### 2. LLM Judge（LLM评判）
用强大的AI模型（如GPT-4）作为评判者：
- 对回答进行质量评分
- 比较两个回答的优劣（Win Rate）
- 优势：能评估开放性、主观性任务
- 注意：需要防止评判偏差和位置偏好

### 3. Win Rate（胜率评估）
- 对同一问题生成多个候选回答
- LLM Judge两两比较，统计胜率
- 常用于数据生成质量评估和模型对比

### 4. 人工验证
- 最终质量把关
- 适用于自动化方法难以判断的场景
- 成本最高但最可靠

## HelloAgents评估体系

```
hello_agents/evaluation/
└── benchmarks/
    ├── bfcl/                    # BFCL工具调用评估
    │   ├── dataset.py           # 数据集加载
    │   ├── evaluator.py         # AST匹配评估器
    │   ├── metrics.py           # 专用指标
    │   └── ast_matcher.py       # AST匹配算法
    ├── gaia/                    # GAIA通用能力评估
    │   ├── dataset.py
    │   ├── evaluator.py         # 准精确匹配
    │   ├── metrics.py
    │   └── quasi_exact_match.py
    └── data_generation/         # 数据生成质量评估
        ├── dataset.py           # AIME数据集
        ├── llm_judge.py         # LLM评判器
        └── win_rate.py          # 胜率评估
```

评估工具也遵循"万物皆工具"理念，封装为：
- `bfcl_evaluation_tool.py`
- `gaia_evaluation_tool.py`
- `llm_judge_tool.py`
- `win_rate_tool.py`

## 评估与训练的闭环

评估是Agent持续改进的基础：
1. **SFT阶段**：评估确定模型基线能力
2. **GRPO阶段**：奖励函数本质是可微分的评估信号
3. **迭代优化**：评估发现弱点 → 针对性数据增强 → 重新训练
4. **生产监控**：部署后持续评估，发现回归问题

## 相关阅读

- 第十二章 智能体性能评估
- Agentic-RL
- 智能体范式与ReAct
