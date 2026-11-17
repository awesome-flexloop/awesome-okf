# 变更日志 / Changelog

## 2026-11-18 — ReAct 教程深度补充

### 更新
- 重写 `concepts/agent-paradigms-react.md`：补充论文出处与作者、轨迹形式化、少样本提示格式、最小实现骨架、四类基准结果、消融、HotpotQA 失败模式归因、上下文与动作空间限制、从文本协议到函数调用的工程化对照，以及与小满手机 Agent 的 ReAct 对照。
- 新增信源：arXiv:2210.03629（ICLR 2023）、react-lm.github.io 项目页。
- 保留原有 Plan-and-Solve 与 Reflection 小节，三者对比表不变。

### 结论
- ReAct 的机制是「推理与行动交错、观察回填」；论文数字为 PaLM-540B 少样本结果，不构成对其他模型的效果承诺。
- 失败模式以推理/循环（47%）与检索质量（23%）为主；工程实现必须补步数上限、重复检测与安全闸门。

## 2026-08-23 — OKF v0.2 知识包初始化

### 新增
- 基于 Hello-Agents 项目 main 分支生成 OKF v0.2 知识包
- 完成 R→I→E→V 全流程

#### R 阶段（阅读）
- 阅读 README.md、docs/README.md、docs/_sidebar.md、docs/Preface.md、docs/前言.md
- 通读 docs/ 全部16章文档，提取核心知识点
- 扫描 Extra-Chapter/ 13篇社区精选文章
- 扫描 code/ 目录配套代码结构
- 在 spec/facts.md 记录完整章节结构与技术标签

#### I 阶段（洞察）
- 在 spec/insights.md 提炼5条核心洞察：
  1. Agent范式演进：从规则反射到推理-行动协同
  2. 从单Agent到多Agent通信：协议标准化是生态爆发前提
  3. 记忆与上下文工程是Agent从演示到生产的核心瓶颈
  4. Agentic-RL标志着从prompt工程到策略训练的范式转移
  5. "用轮子"与"造轮子"的辩证：HelloAgents教学法创新

#### E 阶段（工程化）
- 创建 index.md 主入口（含完整frontmatter与知识地图）
- 创建 concepts/ 8个概念文档：
  - agent-paradigms-react.md（智能体范式与ReAct）
  - agent-framework-development.md（Agent框架开发）
  - memory-systems.md（记忆系统）
  - context-engineering.md（上下文工程）
  - communication-protocols.md（通信协议MCP/A2A/ANP）
  - multi-agent-collaboration.md（多Agent协作）
  - agentic-rl.md（Agentic-RL）
  - evaluation-methods.md（评估方法）
- 创建 examples/ 4个实战示例文档
- 创建 references/ 17个章节参考文档（16章+社区精选）

### 来源
- 仓库: https://github.com/datawhalechina/hello-agents
- 本地路径: d:\spaces\SpecWeave\external\libs\ai\datawhalechina\hello-agents
